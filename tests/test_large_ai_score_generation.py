import json
from unittest.mock import Mock

from app import models
from app.llm.schemas import LLMResponse, LLMUsage
from app.services import ai_score_service
from conftest import TEST_PASSWORD


def login(client):
    response = client.post(
        "/login",
        data={"email": "user1@test.com", "password": TEST_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code == 303


def prepare_matrix(test_environment, alternatives=13, criteria=10):
    Session = test_environment["TestingSessionLocal"]
    project_id = test_environment["project_1_id"]
    with Session() as db:
        project = db.get(models.Project, project_id)
        project.description = "Выбор рабочего решения с учётом всех условий."
        existing_alternatives = db.query(models.Alternative).filter_by(
            project_id=project_id,
        ).count()
        existing_criteria = db.query(models.Criterion).filter_by(
            project_id=project_id,
        ).count()
        db.add_all([
            models.Alternative(name=f"Альтернатива {number}", project_id=project_id)
            for number in range(existing_alternatives + 1, alternatives + 1)
        ])
        db.add_all([
            models.Criterion(
                name=f"Критерий {number}", weight=1 / criteria, project_id=project_id,
            )
            for number in range(existing_criteria + 1, criteria + 1)
        ])
        db.commit()
    return project_id


def complete_response(kwargs):
    user_data = json.loads(kwargs["user_prompt"])
    items = [
        {"a": alternative["id"], "c": criterion["id"], "v": 7.5,
         "r": "Соответствует критерию."}
        for alternative in user_data["alternatives"]
        for criterion in user_data["criteria"]
    ]
    return LLMResponse(
        content=json.dumps({"s": "ok", "i": items}, ensure_ascii=False),
        provider="test", model="test-model",
        usage=LLMUsage(
            input_tokens=100, output_tokens=200,
            reasoning_tokens=50, total_tokens=300,
        ),
    )


def test_13_by_10_matrix_is_generated_in_resumable_batches(
    client, test_environment, verified_users, monkeypatch,
):
    login(client)
    project_id = prepare_matrix(test_environment)
    batches = []

    def generate(**kwargs):
        data = json.loads(kwargs["user_prompt"])
        pairs = len(data["alternatives"]) * len(data["criteria"])
        batches.append((pairs, kwargs["max_output_tokens"]))
        return complete_response(kwargs)

    monkeypatch.setattr(ai_score_service.llm_service, "generate", generate)
    statuses = []
    for _ in range(10):
        response = client.post(f"/projects/{project_id}/ai/scores")
        assert response.status_code == 200
        statuses.append(response.json()["status"])
        if statuses[-1] == "ok":
            break

    assert statuses == ["in_progress"] * 6 + ["ok"]
    assert batches == [(20, 1800)] * 6 + [(10, 900)]
    Session = test_environment["TestingSessionLocal"]
    with Session() as db:
        assert db.query(models.Score).count() == 130
        logs = db.query(models.AIRequestLog).filter_by(feature="scores").all()
        assert len(logs) == 1
        assert logs[0].status == "completed"
        assert logs[0].input_tokens == 700
        assert logs[0].output_tokens == 1400
        assert logs[0].reasoning_tokens == 350
        assert logs[0].total_tokens == 2100
        job = db.get(models.AIScoreGenerationJob, project_id)
        assert job.status == "completed"
        assert job.next_alternative_index == 13


def test_20_by_10_matrix_is_generated_in_ten_batches(
    client, test_environment, verified_users, monkeypatch,
):
    login(client)
    project_id = prepare_matrix(test_environment, alternatives=20, criteria=10)
    batch_sizes = []

    def generate(**kwargs):
        data = json.loads(kwargs["user_prompt"])
        batch_sizes.append(len(data["alternatives"]) * len(data["criteria"]))
        return complete_response(kwargs)

    monkeypatch.setattr(ai_score_service.llm_service, "generate", generate)
    for _ in range(10):
        response = client.post(f"/projects/{project_id}/ai/scores")
        assert response.status_code == 200

    assert response.json()["status"] == "ok"
    assert response.json()["completed"] == 200
    assert response.json()["total"] == 200
    assert batch_sizes == [20] * 10
    Session = test_environment["TestingSessionLocal"]
    with Session() as db:
        assert db.query(models.Score).count() == 200
        assert db.query(models.AIRequestLog).filter_by(feature="scores").count() == 1


def test_failed_batch_can_resume_without_spending_another_user_request(
    client, test_environment, verified_users, monkeypatch,
):
    login(client)
    project_id = prepare_matrix(test_environment, alternatives=3, criteria=2)
    provider = Mock(side_effect=[RuntimeError("LLM не ответила вовремя."), None])

    def generate(**kwargs):
        result = provider()
        return result if result is not None else complete_response(kwargs)

    monkeypatch.setattr(ai_score_service.llm_service, "generate", generate)
    first = client.post(f"/projects/{project_id}/ai/scores")
    assert first.status_code == 503
    assert first.json()["error_code"] == "provider_timeout"
    second = client.post(f"/projects/{project_id}/ai/scores")
    assert second.status_code == 200
    assert second.json()["status"] == "ok"
    Session = test_environment["TestingSessionLocal"]
    with Session() as db:
        assert db.query(models.AIRequestLog).filter_by(feature="scores").count() == 1
        job = db.get(models.AIScoreGenerationJob, project_id)
        assert job.status == "completed"
        assert job.last_error_code is None


def test_incomplete_batch_is_not_saved_or_advanced(
    client, test_environment, verified_users, monkeypatch,
):
    login(client)
    project_id = prepare_matrix(test_environment, alternatives=3, criteria=2)

    def generate(**kwargs):
        response = complete_response(kwargs)
        data = json.loads(response.content)
        data["i"] = data["i"][:1]
        response.content = json.dumps(data)
        return response

    monkeypatch.setattr(ai_score_service.llm_service, "generate", generate)
    response = client.post(f"/projects/{project_id}/ai/scores")
    assert response.status_code == 503
    Session = test_environment["TestingSessionLocal"]
    with Session() as db:
        assert db.query(models.Score).count() == 0
        job = db.get(models.AIScoreGenerationJob, project_id)
        assert job.status == "ready"
        assert job.next_alternative_index == 0
        assert job.last_error_code == "incomplete_batch"


def test_retry_limit_stops_repeated_provider_failures(
    client, test_environment, verified_users, monkeypatch,
):
    login(client)
    project_id = prepare_matrix(test_environment, alternatives=3, criteria=2)
    provider = Mock(side_effect=RuntimeError("LLM не ответила вовремя."))
    monkeypatch.setattr(ai_score_service.llm_service, "generate", provider)

    for _ in range(4):
        response = client.post(f"/projects/{project_id}/ai/scores")
        assert response.status_code == 503

    stopped = client.post(f"/projects/{project_id}/ai/scores")
    assert stopped.status_code == 429
    assert stopped.json()["status"] == "retry_limit"
    assert provider.call_count == 4
    Session = test_environment["TestingSessionLocal"]
    with Session() as db:
        job = db.get(models.AIScoreGenerationJob, project_id)
        request_log = db.get(models.AIRequestLog, job.request_log_id)
        assert job.status == "cancelled"
        assert job.last_error_code == "retry_limit"
        assert request_log.status == "failed"


def test_score_generation_uses_visible_progress_modal(
    client, test_environment, verified_users,
):
    login(client)
    response = client.get(f'/projects/{test_environment["project_1_id"]}')
    assert response.status_code == 200
    assert 'id="aiScoresModal"' in response.text
    assert 'id="ai-scores-progress"' in response.text
    assert "Матрица обрабатывается небольшими частями" in response.text
    assert "spinner-border text-primary flex-shrink-0" in response.text
    assert "Продолжить" in response.text
    assert 'id="ai-scores-status"' not in response.text
