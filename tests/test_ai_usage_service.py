from datetime import (
    datetime,
    timedelta,
    timezone,
)

import pytest

from app import models
from app.services import (
    ai_usage_service,
)


def reserve_request(
    *,
    db,
    test_environment,
    now,
):
    return (
        ai_usage_service
        .reserve_ai_request(
            db=db,
            user_id=(
                test_environment[
                    "user_1_id"
                ]
            ),
            project_id=(
                test_environment[
                    "project_1_id"
                ]
            ),
            feature="alternatives",
            now=now,
        )
    )


def test_ai_request_is_reserved(
    test_environment,
    monkeypatch,
):
    monkeypatch.delenv(
        "AI_REQUESTS_PER_MINUTE",
        raising=False,
    )

    monkeypatch.delenv(
        "AI_REQUESTS_PER_24_HOURS",
        raising=False,
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    now = datetime(
        2026,
        8,
        27,
        12,
        0,
        tzinfo=timezone.utc,
    )

    db = TestingSessionLocal()

    request_log = reserve_request(
        db=db,
        test_environment=test_environment,
        now=now,
    )

    assert request_log.id is not None
    assert request_log.status == "started"
    assert (
        request_log.feature
        == "alternatives"
    )
    assert request_log.total_tokens == 0

    saved_log = db.get(
        models.AIRequestLog,
        request_log.id,
    )

    assert saved_log is not None
    assert (
        saved_log.user_id
        == test_environment["user_1_id"]
    )

    db.close()


def test_ai_minute_limit_is_enforced(
    test_environment,
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_REQUESTS_PER_MINUTE",
        "2",
    )

    monkeypatch.setenv(
        "AI_REQUESTS_PER_24_HOURS",
        "100",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    now = datetime(
        2026,
        8,
        27,
        12,
        0,
        tzinfo=timezone.utc,
    )

    db = TestingSessionLocal()

    reserve_request(
        db=db,
        test_environment=test_environment,
        now=now - timedelta(
            seconds=20
        ),
    )

    reserve_request(
        db=db,
        test_environment=test_environment,
        now=now - timedelta(
            seconds=10
        ),
    )

    with pytest.raises(
        ai_usage_service
        .AIRequestLimitError
    ) as error:
        reserve_request(
            db=db,
            test_environment=test_environment,
            now=now,
        )

    assert error.value.scope == "minute"

    assert str(error.value) == (
        ai_usage_service
        .RATE_LIMIT_MESSAGE
    )

    db.close()


def test_ai_daily_limit_is_enforced(
    test_environment,
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_REQUESTS_PER_MINUTE",
        "100",
    )

    monkeypatch.setenv(
        "AI_REQUESTS_PER_24_HOURS",
        "2",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    now = datetime(
        2026,
        8,
        27,
        12,
        0,
        tzinfo=timezone.utc,
    )

    db = TestingSessionLocal()

    reserve_request(
        db=db,
        test_environment=test_environment,
        now=now - timedelta(
            hours=23
        ),
    )

    reserve_request(
        db=db,
        test_environment=test_environment,
        now=now - timedelta(
            hours=2
        ),
    )

    with pytest.raises(
        ai_usage_service
        .AIRequestLimitError
    ) as error:
        reserve_request(
            db=db,
            test_environment=test_environment,
            now=now,
        )

    assert error.value.scope == "day"

    assert str(error.value) == (
        ai_usage_service
        .DAILY_LIMIT_MESSAGE
    )

    db.close()


def test_ai_daily_limit_ignores_old_requests(
    test_environment,
    monkeypatch,
):
    monkeypatch.setenv(
        "AI_REQUESTS_PER_MINUTE",
        "100",
    )

    monkeypatch.setenv(
        "AI_REQUESTS_PER_24_HOURS",
        "1",
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    now = datetime(
        2026,
        8,
        27,
        12,
        0,
        tzinfo=timezone.utc,
    )

    db = TestingSessionLocal()

    reserve_request(
        db=db,
        test_environment=test_environment,
        now=now - timedelta(
            hours=25
        ),
    )

    request_log = reserve_request(
        db=db,
        test_environment=test_environment,
        now=now,
    )

    assert request_log.id is not None

    db.close()


def test_ai_request_rejects_unknown_feature(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    with pytest.raises(
        ValueError,
        match="Неизвестная",
    ):
        (
            ai_usage_service
            .reserve_ai_request(
                db=db,
                user_id=(
                    test_environment[
                        "user_1_id"
                    ]
                ),
                project_id=(
                    test_environment[
                        "project_1_id"
                    ]
                ),
                feature="unknown",
            )
        )

    db.close()


def test_ai_request_rejects_naive_time(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    with pytest.raises(
        ValueError,
        match="часовой пояс",
    ):
        reserve_request(
            db=db,
            test_environment=test_environment,
            now=datetime(
                2026,
                8,
                27,
                12,
                0,
            ),
        )

    db.close()


@pytest.mark.parametrize(
    (
        "setting_name",
        "setting_value",
    ),
    [
        (
            "AI_REQUESTS_PER_MINUTE",
            "abc",
        ),
        (
            "AI_REQUESTS_PER_24_HOURS",
            "0",
        ),
    ],
)
def test_ai_request_rejects_invalid_setting(
    test_environment,
    monkeypatch,
    setting_name,
    setting_value,
):
    monkeypatch.setenv(
        setting_name,
        setting_value,
    )

    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    db = TestingSessionLocal()

    with pytest.raises(
        RuntimeError,
        match=setting_name,
    ):
        reserve_request(
            db=db,
            test_environment=test_environment,
            now=datetime(
                2026,
                8,
                27,
                12,
                0,
                tzinfo=timezone.utc,
            ),
        )

    db.close()