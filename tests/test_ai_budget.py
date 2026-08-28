import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from threading import Barrier
from unittest.mock import Mock

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session

from app import models
from app.database import Base
from app.llm.providers.mws import MWSProvider
from app.services import ai_budget_service as budget
from app.services import admin_service, auth_rate_limit_service, ai_usage_service
from conftest import TEST_PASSWORD
from test_ai_usage_routes import llm_response


def reported(incoming=100, outgoing=50):
    return {"model": "gpt-oss-120b", "usage": {
        "prompt_tokens": incoming, "completion_tokens": outgoing,
        "total_tokens": incoming + outgoing,
        "completion_tokens_details": {"reasoning_tokens": 10},
    }}


def test_budget_defaults_to_100_rubles(monkeypatch):
    monkeypatch.delenv("AI_DAILY_BUDGET_RUB", raising=False)
    assert budget.daily_limit_microrub() == 100_000_000


@pytest.mark.parametrize("value", ["0", "-1", "abc", "NaN", "Infinity", "0.0000001"])
def test_invalid_budget_fails_closed(monkeypatch, value):
    monkeypatch.setenv("AI_DAILY_BUDGET_RUB", value)
    with pytest.raises(budget.AIBudgetConfigurationError):
        budget.get_pricing()


@pytest.mark.parametrize("setting,value", [
    ("AI_PRICING_CONFIRMED", "false"), ("AI_ENABLED", "false"),
    ("LLM_MODEL", "unknown-expensive-model"), ("LLM_PROVIDER", "other"),
    ("AI_INPUT_RUB_PER_MILLION", "-1"), ("AI_OUTPUT_RUB_PER_MILLION", "NaN"),
])
def test_unknown_model_or_unconfirmed_pricing_fails_closed(monkeypatch, setting, value):
    monkeypatch.setenv(setting, value)
    with pytest.raises(budget.AIBudgetConfigurationError):
        budget.get_pricing()


def test_preview_never_uses_paid_ai(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    monkeypatch.setenv("VERCEL_ENV", "preview")
    with pytest.raises(budget.AIBudgetConfigurationError, match="preview"):
        budget.get_pricing()


def test_reservation_is_persisted_before_work_and_uncertain_call_keeps_money(provider_budget_context):
    db, log = provider_budget_context
    with pytest.raises(RuntimeError):
        with budget.metered_call(model="gpt-oss-120b", max_output_tokens=700) as call:
            assert call.id is not None
            assert db.get(models.AIDailyBudget, call.budget_day).allocated_microrub == call.reserved_microrub
            raise RuntimeError("timeout")
    db.expire_all()
    saved = db.query(models.AIProviderCall).one()
    assert saved.status == "uncertain"
    assert saved.charged_microrub == saved.reserved_microrub
    assert saved.estimated_microrub is None


def test_known_usage_settles_once_and_preserves_price_snapshot(provider_budget_context, monkeypatch):
    db, log = provider_budget_context
    with budget.metered_call(model="gpt-oss-120b", max_output_tokens=700) as call:
        old_reserve = call.reserved_microrub
        monkeypatch.setenv("AI_INPUT_RUB_PER_MILLION", "900")
        budget.record_usage(call, reported())
        first = db.get(models.AIDailyBudget, call.budget_day).allocated_microrub
        budget.record_usage(call, reported())
        assert db.get(models.AIDailyBudget, call.budget_day).allocated_microrub == first
    db.expire_all()
    saved = db.query(models.AIProviderCall).one()
    assert saved.input_rub_per_million == Decimal("13.42")
    assert saved.estimated_microrub == 4087  # 100*13.42 + 50*54.90, no double-counted reasoning
    assert saved.charged_microrub == 6832  # upward-rounded 100-token units
    assert saved.charged_microrub < old_reserve
    assert log.total_tokens == 150
    # A business refusal with no usage field must not erase known provider usage.
    ai_usage_service.complete_ai_request(db=db, request_log=log, usage={})
    assert log.total_tokens == 150


@pytest.mark.parametrize("bad", [
    {}, {"usage": None}, {"usage": {}},
    {"usage": {"prompt_tokens": True, "completion_tokens": 1, "total_tokens": 2}},
    {"usage": {"prompt_tokens": -1, "completion_tokens": 1, "total_tokens": 0}},
    {"usage": {"prompt_tokens": 100, "completion_tokens": 1, "total_tokens": 999}},
    {"usage": {"prompt_tokens": 100, "completion_tokens": 9000, "total_tokens": 9100}},
])
def test_missing_or_invalid_usage_never_refunds(provider_budget_context, bad):
    db, _ = provider_budget_context
    with budget.metered_call(model="gpt-oss-120b", max_output_tokens=700) as call:
        budget.record_usage(call, bad)
    saved = db.query(models.AIProviderCall).one()
    assert saved.status == "uncertain"
    assert saved.charged_microrub == saved.reserved_microrub


def test_budget_boundary_and_moscow_midnight(provider_budget_context, monkeypatch):
    db, log = provider_budget_context
    pricing = budget.get_pricing()
    maximum = budget.cost_microrub(budget.INPUT_TOKEN_BOUND, 700, pricing.input_rate, pricing.output_rate, upper=True)
    monkeypatch.setenv("AI_DAILY_BUDGET_RUB", str(Decimal(maximum) / 1_000_000))
    now = datetime(2026, 8, 28, 20, 59, 59, tzinfo=timezone.utc)
    first = budget.reserve_call(db=db, request_log=log, pricing=pricing, max_output_tokens=700, now=now)
    assert first.budget_day.isoformat() == "2026-08-28"
    with pytest.raises(budget.AIBudgetExceeded):
        budget.reserve_call(db=db, request_log=log, pricing=pricing, max_output_tokens=700, now=now)
    second = budget.reserve_call(db=db, request_log=log, pricing=pricing,
                                 max_output_tokens=700, now=now + timedelta(seconds=1))
    assert second.budget_day.isoformat() == "2026-08-29"
    assert db.query(models.AIProviderCall).count() == 2


def test_settlement_uses_original_day_not_completion_day(provider_budget_context):
    db, log = provider_budget_context
    old = datetime.now(timezone.utc) - timedelta(days=1)
    call = budget.reserve_call(db=db, request_log=log, pricing=budget.get_pricing(), max_output_tokens=700, now=old)
    day = call.budget_day
    budget.record_usage(call, reported())
    assert db.query(models.AIDailyBudget).count() == 1
    assert db.get(models.AIDailyBudget, day).allocated_microrub == 6832


def test_deleting_request_log_does_not_restore_budget(provider_budget_context):
    db, log = provider_budget_context
    # Enable FK actions on SQLite too (PostgreSQL always enforces these).
    db.rollback()
    db.connection().exec_driver_sql("PRAGMA foreign_keys=ON")
    db.commit()
    with budget.metered_call(model="gpt-oss-120b", max_output_tokens=700) as call:
        pass
    call_id, day, charged = call.id, call.budget_day, call.charged_microrub
    db.execute(delete(models.AIRequestLog).where(models.AIRequestLog.id == log.id))
    db.commit()
    db.expire_all()
    assert db.get(models.AIProviderCall, call_id).request_log_id is None
    assert db.get(models.AIDailyBudget, day).allocated_microrub == charged


def test_paid_provider_without_context_cannot_send_http(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.test")
    client = Mock(side_effect=AssertionError("HTTP must not run"))
    monkeypatch.setattr(httpx, "Client", client)
    with pytest.raises(budget.AIBudgetConfigurationError):
        MWSProvider().generate(system_prompt="test", user_prompt="test", max_output_tokens=100, temperature=0)
    client.assert_not_called()


@pytest.fixture()
def prepared(client, test_environment, verified_users, monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "test")
    monkeypatch.setenv("LLM_BASE_URL", "https://example.test")
    client.post("/login", data={"email": "user1@test.com", "password": TEST_PASSWORD})
    with test_environment["TestingSessionLocal"]() as db:
        db.get(models.Project, test_environment["project_1_id"]).description = "Выбор автомобиля для семьи."
        db.get(models.Criterion, test_environment["criterion_1_id"]).weight = 0.5
        db.add(models.Score(alternative_id=test_environment["alternative_1_id"],
                            criterion_id=test_environment["criterion_1_id"], value=7.0))
        db.commit()
    return test_environment


def mock_http(monkeypatch, payload=None, error=None):
    original = httpx.Client
    def respond(request):
        if error:
            raise error
        return httpx.Response(200, json=payload, request=request)
    transport = Mock(side_effect=respond)
    monkeypatch.setattr(httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(transport), **kw))
    return transport


@pytest.mark.parametrize("feature", ["alternatives", "criteria", "scores", "result_explanation", "decision_risks"])
def test_real_provider_boundary_is_guarded_for_all_routes(client, prepared, monkeypatch, feature):
    response = llm_response(feature, prepared)
    payload = reported(120, 40)
    payload["choices"] = [{"message": {"content": response.content}}]
    transport = mock_http(monkeypatch, payload=payload)
    path = f'/projects/{prepared["project_1_id"]}/ai/{feature.replace("_", "-")}'
    result = client.post(path)
    assert result.status_code == 200
    assert transport.call_count == 1
    with prepared["TestingSessionLocal"]() as db:
        assert db.query(models.AIProviderCall).one().status == "reported"
        assert db.query(models.AIRequestLog).one().total_tokens == 160
        stats = admin_service.statistics(db, 1)
        assert stats["input_tokens"] == 120
        assert stats["output_tokens"] == 40
        assert stats["estimated"] > 0
    monkeypatch.setenv("AI_DAILY_BUDGET_RUB", "0.01")
    result = client.post(path)
    assert result.status_code == 429
    assert result.json()["status"] == "budget_exhausted"
    assert transport.call_count == 1


@pytest.mark.parametrize("content,status", [("not json", 503), ('{"s":"unsafe"}', 400)])
def test_paid_invalid_or_unsafe_reply_keeps_actual_usage(client, prepared, monkeypatch, content, status):
    payload = reported()
    payload["choices"] = [{"message": {"content": content}}]
    mock_http(monkeypatch, payload=payload)
    response = client.post(f'/projects/{prepared["project_1_id"]}/ai/alternatives')
    assert response.status_code == status
    with prepared["TestingSessionLocal"]() as db:
        assert db.query(models.AIProviderCall).one().status == "reported"
        assert db.query(models.AIRequestLog).one().total_tokens == 150


def test_timeout_retains_money_and_returns_normal_503(client, prepared, monkeypatch):
    mock_http(monkeypatch, error=httpx.ReadTimeout("timeout"))
    response = client.post(f'/projects/{prepared["project_1_id"]}/ai/alternatives')
    assert response.status_code == 503
    with prepared["TestingSessionLocal"]() as db:
        call = db.query(models.AIProviderCall).one()
        assert call.status == "uncertain"
        assert call.estimated_microrub is None
        assert call.charged_microrub > 0
        assert db.query(models.AIRequestLog).one().status == "failed"


def test_concurrent_reservations_and_auth_attempts_use_shared_atomic_counters(tmp_path, monkeypatch):
    # Independent connections, not an in-memory lock or one shared test session.
    engine = create_engine(f'sqlite:///{tmp_path / "concurrency.db"}', connect_args={"timeout": 30})
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        user = models.User(email="test@example.com", password_hash="not-used")
        db.add(user)
        db.flush()
        logs = [models.AIRequestLog(user_id=user.id, project_id=1, feature="alternatives") for _ in range(8)]
        db.add_all(logs)
        db.commit()
        ids = [log.id for log in logs]
    monkeypatch.setenv("AI_DAILY_BUDGET_RUB", "2")
    barrier = Barrier(8)
    pricing = budget.get_pricing()
    def reserve(log_id):
        with Session(engine) as db:
            log = db.get(models.AIRequestLog, log_id)
            barrier.wait(timeout=10)
            try:
                budget.reserve_call(db=db, request_log=log, pricing=pricing, max_output_tokens=700)
                return True
            except budget.AIBudgetExceeded:
                return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(reserve, ids)) == 1
    with Session(engine) as db:
        assert db.query(models.AIProviderCall).count() == 1
        assert db.query(models.AIDailyBudget).one().allocated_microrub <= 2_000_000
    barrier = Barrier(8)
    def attempt(_):
        with Session(engine) as db:
            barrier.wait(timeout=10)
            try:
                auth_rate_limit_service.consume(db, scope="parallel", identity="same", limit=3, seconds=60)
                return True
            except HTTPException as error:
                assert error.status_code == 429
                return False
    with ThreadPoolExecutor(max_workers=8) as pool:
        assert sum(pool.map(attempt, range(8))) == 3
    engine.dispose()
