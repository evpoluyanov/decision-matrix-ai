"""HTTP checks for usage accounting across the four remaining AI features."""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest

pytestmark = pytest.mark.usefixtures("verified_users")

from app import models
from app.llm import service as llm_service
from app.llm.safety import MAX_PROJECT_DESCRIPTION_LENGTH
from app.llm.schemas import LLMResponse, LLMUsage
from app.services import ai_usage_service
from conftest import TEST_PASSWORD


FEATURES = (
    "criteria",
    "scores",
    "result_explanation",
    "decision_risks",
)
USAGE = {
    "input_tokens": 120,
    "output_tokens": 40,
    "reasoning_tokens": 10,
    "total_tokens": 160,
}


def endpoint(project_id, feature):
    return f"/projects/{project_id}/ai/{feature.replace('_', '-')}"


@pytest.fixture(autouse=True)
def isolate_ai_requests(monkeypatch):
    monkeypatch.setenv("AI_REQUESTS_PER_MINUTE", "100")
    monkeypatch.setenv("AI_REQUESTS_PER_24_HOURS", "100")
    # No test in this module may accidentally contact a real provider.
    monkeypatch.setattr(
        llm_service,
        "generate",
        Mock(side_effect=AssertionError("Unexpected LLM call")),
    )


@pytest.fixture()
def ai_context(client, test_environment):
    response = client.post(
        "/login",
        data={"email": "user1@test.com", "password": TEST_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with test_environment["TestingSessionLocal"]() as db:
        project = db.get(models.Project, test_environment["project_1_id"])
        project.description = "Выбор семейного автомобиля до 4 млн рублей."
        criterion = db.get(models.Criterion, test_environment["criterion_1_id"])
        # Leave room for suggested criteria and fill the matrix for analysis.
        criterion.weight = 0.5
        db.add(models.Score(
            alternative_id=test_environment["alternative_1_id"],
            criterion_id=criterion.id,
            value=7.0,
        ))
        db.commit()

    return test_environment


def llm_response(feature, context):
    payloads = {
        "alternatives": {
            "s": "ok", "i": [{"n": "Toyota Camry", "r": "Семейный автомобиль."}],
        },
        "criteria": {
            "s": "ok",
            "i": [{"n": "Надёжность", "w": 25, "cr": "Важна для семьи.",
                   "wr": "Снижает риск ремонта."}],
        },
        "scores": {
            "s": "ok",
            "i": [{"a": context["alternative_1_id"], "c": context["criterion_1_id"],
                   "v": 8.5, "r": "Соответствует критерию."}],
        },
        "result_explanation": {
            "summary": "Результат следует из оценок матрицы.",
            "factors": ["Основной критерий"],
            "strengths": ["Высокая оценка"], "weaknesses": [],
            "competitor": "", "caveat": "",
        },
        "decision_risks": {
            "s": "ok",
            "i": [{"t": "hypothesis", "n": "Стоимость ремонта",
                   "r": "Возможны дополнительные расходы.",
                   "c": "Проверить стоимость обслуживания."}],
        },
    }
    return LLMResponse(
        content=json.dumps(payloads[feature], ensure_ascii=False),
        provider="test-provider", model="test-model", usage=LLMUsage(**USAGE),
    )


@pytest.mark.parametrize("feature", FEATURES)
def test_request_is_reserved_before_llm_and_completed(
    client, ai_context, monkeypatch, feature,
):
    def generate(**kwargs):
        with ai_context["TestingSessionLocal"]() as db:
            request_log = db.query(models.AIRequestLog).one()
            assert request_log.status == "started"
            assert request_log.feature == feature
            assert request_log.user_id == ai_context["user_1_id"]
            assert request_log.project_id == ai_context["project_1_id"]
            assert request_log.completed_at is None
            assert request_log.total_tokens == 0
        return llm_response(feature, ai_context)

    provider = Mock(side_effect=generate)
    monkeypatch.setattr(llm_service, "generate", provider)
    response = client.post(endpoint(ai_context["project_1_id"], feature))

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert provider.call_count == 1

    with ai_context["TestingSessionLocal"]() as db:
        request_log = db.query(models.AIRequestLog).one()
        assert request_log.status == "completed"
        assert request_log.completed_at is not None
        for name, value in USAGE.items():
            assert getattr(request_log, name) == value
            assert data["usage"][name] == value

        # Tracking must not replace or break the route's existing writes.
        if feature == "scores":
            score = db.query(models.Score).one()
            assert data["updated"] == 1
            assert score.ai_value == 8.5
            assert score.value == 7.0
        elif feature == "result_explanation":
            analysis = db.query(models.ProjectAIAnalysis).one()
            assert analysis.result_summary == data["summary"]
        elif feature == "decision_risks":
            analysis = db.query(models.ProjectAIAnalysis).one()
            assert json.loads(analysis.decision_risks_json) == data["items"]
        else:
            assert len(data["items"]) == 1
            assert db.query(models.Criterion).filter_by(
                project_id=ai_context["project_1_id"],
            ).count() == 1  # Suggestions are still accepted separately.


@pytest.mark.parametrize("feature", FEATURES)
def test_provider_failure_is_logged_and_consumes_quota(
    client, ai_context, monkeypatch, feature,
):
    monkeypatch.setenv("AI_REQUESTS_PER_MINUTE", "1")
    provider = Mock(side_effect=RuntimeError("Provider unavailable"))
    monkeypatch.setattr(llm_service, "generate", provider)

    url = endpoint(ai_context["project_1_id"], feature)
    response = client.post(url)
    assert response.status_code == 503
    assert response.json()["status"] == "error"

    with ai_context["TestingSessionLocal"]() as db:
        request_log = db.query(models.AIRequestLog).one()
        assert request_log.feature == feature
        assert request_log.status == "failed"
        assert request_log.completed_at is not None
        assert request_log.total_tokens == 0

    assert client.post(url).status_code == 429
    assert provider.call_count == 1
    with ai_context["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 1


@pytest.mark.parametrize("feature", FEATURES)
@pytest.mark.parametrize("scope", ("minute", "day"))
def test_limit_rejects_request_without_llm_or_extra_log(
    client, ai_context, monkeypatch, feature, scope,
):
    setting, age, message = {
        "minute": ("AI_REQUESTS_PER_MINUTE", timedelta(seconds=10),
                   ai_usage_service.RATE_LIMIT_MESSAGE),
        "day": ("AI_REQUESTS_PER_24_HOURS", timedelta(hours=2),
                ai_usage_service.DAILY_LIMIT_MESSAGE),
    }[scope]
    monkeypatch.setenv(setting, "1")
    with ai_context["TestingSessionLocal"]() as db:
        db.add(models.AIRequestLog(
            user_id=ai_context["user_1_id"],
            project_id=ai_context["project_1_id"],
            feature="alternatives", status="completed",
            created_at=datetime.now(timezone.utc) - age,
            input_tokens=0, output_tokens=0, reasoning_tokens=0, total_tokens=0,
        ))
        db.commit()

    response = client.post(endpoint(ai_context["project_1_id"], feature))
    assert response.status_code == 429
    assert response.json() == {
        "status": "rate_limited", "scope": scope, "message": message,
    }
    llm_service.generate.assert_not_called()
    with ai_context["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 1


@pytest.mark.parametrize("feature", FEATURES)
@pytest.mark.parametrize("missing", (False, True), ids=("foreign", "missing"))
def test_project_access_is_checked_before_reservation(
    client, ai_context, feature, missing,
):
    project_id = 999999 if missing else ai_context["project_2_id"]
    response = client.post(endpoint(project_id, feature))
    assert response.status_code == 404
    llm_service.generate.assert_not_called()
    with ai_context["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 0


@pytest.mark.parametrize("feature", FEATURES)
def test_anonymous_request_does_not_reserve(client, test_environment, feature):
    response = client.post(
        endpoint(test_environment["project_1_id"], feature),
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    llm_service.generate.assert_not_called()
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 0


@pytest.mark.parametrize("feature", FEATURES)
def test_oversized_input_does_not_reserve(client, ai_context, feature):
    with ai_context["TestingSessionLocal"]() as db:
        project = db.get(models.Project, ai_context["project_1_id"])
        project.description = "x" * (MAX_PROJECT_DESCRIPTION_LENGTH + 1)
        db.commit()

    response = client.post(endpoint(ai_context["project_1_id"], feature))
    assert response.status_code == 400
    assert response.json()["status"] == "input_limit_exceeded"
    llm_service.generate.assert_not_called()
    with ai_context["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 0


@pytest.mark.parametrize("feature", FEATURES)
def test_result_without_usage_does_not_leave_started_log(
    client, ai_context, feature,
):
    with ai_context["TestingSessionLocal"]() as db:
        project = db.get(models.Project, ai_context["project_1_id"])
        project.description = ""
        db.commit()

    response = client.post(endpoint(ai_context["project_1_id"], feature))
    assert response.status_code == 200
    assert response.json()["status"] == "insufficient_context"
    llm_service.generate.assert_not_called()
    with ai_context["TestingSessionLocal"]() as db:
        request_log = db.query(models.AIRequestLog).one()
        assert request_log.feature == feature
        assert request_log.status == "completed"
        assert request_log.completed_at is not None
        assert request_log.total_tokens == 0


@pytest.mark.parametrize("feature", FEATURES)
def test_unsafe_response_keeps_http_400_and_finalizes_log(
    client, ai_context, monkeypatch, feature,
):
    monkeypatch.setattr(llm_service, "generate", Mock(return_value=LLMResponse(
        content='{"s":"unsafe"}', provider="test", model="test",
        usage=LLMUsage(**USAGE),
    )))
    response = client.post(endpoint(ai_context["project_1_id"], feature))
    assert response.status_code == 400
    assert response.json()["status"] == "unsafe_content"
    with ai_context["TestingSessionLocal"]() as db:
        request_log = db.query(models.AIRequestLog).one()
        assert request_log.feature == feature
        assert request_log.status == "completed"
        assert request_log.completed_at is not None


@pytest.mark.parametrize("feature", FEATURES)
def test_alternatives_and_other_features_share_one_user_limit(
    client, ai_context, monkeypatch, feature,
):
    monkeypatch.setenv("AI_REQUESTS_PER_MINUTE", "1")
    provider = Mock(return_value=llm_response("alternatives", ai_context))
    monkeypatch.setattr(llm_service, "generate", provider)

    first = client.post(endpoint(ai_context["project_1_id"], "alternatives"))
    assert first.status_code == 200
    assert first.json()["status"] == "ok"
    second = client.post(endpoint(ai_context["project_1_id"], feature))
    assert second.status_code == 429
    assert second.json()["scope"] == "minute"
    assert provider.call_count == 1
    with ai_context["TestingSessionLocal"]() as db:
        assert db.query(models.AIRequestLog).count() == 1
