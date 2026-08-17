from app import models
from app.services import (
    alternative_service,
    criterion_service,
    project_ai_analysis_service,
    project_service,
    score_service,
)


def _create_saved_analysis(
    db,
    project_id: int,
):
    analysis = models.ProjectAIAnalysis(
        project_id=project_id,
        result_summary="Сохранённый анализ",
        decision_risks_json="[]",
    )

    db.add(analysis)
    db.commit()

    return analysis


def test_project_change_invalidates_ai_analysis(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    db = TestingSessionLocal()

    project = db.get(
        models.Project,
        project_id,
    )

    _create_saved_analysis(
        db,
        project_id,
    )

    project_service.update_project(
        db=db,
        project=project,
        project_name=project.name,
        project_description=(
            "Новое описание проекта"
        ),
    )

    analysis = (
        project_ai_analysis_service
        .get_analysis(
            db=db,
            project_id=project_id,
        )
    )

    assert analysis is None

    db.close()


def test_new_alternative_invalidates_ai_analysis(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    db = TestingSessionLocal()

    _create_saved_analysis(
        db,
        project_id,
    )

    alternative_service.create_alternative(
        db=db,
        project_id=project_id,
        name="Новая альтернатива",
    )

    analysis = (
        project_ai_analysis_service
        .get_analysis(
            db=db,
            project_id=project_id,
        )
    )

    assert analysis is None

    db.close()


def test_criterion_change_invalidates_ai_analysis(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    criterion_id = (
        test_environment["criterion_1_id"]
    )

    db = TestingSessionLocal()

    criterion = db.get(
        models.Criterion,
        criterion_id,
    )

    _create_saved_analysis(
        db,
        project_id,
    )

    criterion_service.update_criterion(
        db=db,
        criterion_id=criterion_id,
        name=criterion.name,
        weight_percent=50,
    )

    analysis = (
        project_ai_analysis_service
        .get_analysis(
            db=db,
            project_id=project_id,
        )
    )

    assert analysis is None

    db.close()


def test_score_change_invalidates_ai_analysis(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    alternative_id = (
        test_environment[
            "alternative_1_id"
        ]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    score_service.set_score(
        db=db,
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=5.0,
    )

    _create_saved_analysis(
        db,
        project_id,
    )

    score_service.set_score(
        db=db,
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=8.0,
    )

    analysis = (
        project_ai_analysis_service
        .get_analysis(
            db=db,
            project_id=project_id,
        )
    )

    assert analysis is None

    db.close()


def test_same_score_keeps_ai_analysis(
    test_environment,
):
    TestingSessionLocal = (
        test_environment[
            "TestingSessionLocal"
        ]
    )

    project_id = (
        test_environment["project_1_id"]
    )

    alternative_id = (
        test_environment[
            "alternative_1_id"
        ]
    )

    criterion_id = (
        test_environment[
            "criterion_1_id"
        ]
    )

    db = TestingSessionLocal()

    score_service.set_score(
        db=db,
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=7.0,
    )

    _create_saved_analysis(
        db,
        project_id,
    )

    score_service.set_score(
        db=db,
        alternative_id=alternative_id,
        criterion_id=criterion_id,
        value=7.0,
    )

    analysis = (
        project_ai_analysis_service
        .get_analysis(
            db=db,
            project_id=project_id,
        )
    )

    assert analysis is not None
    assert (
        analysis.result_summary
        == "Сохранённый анализ"
    )

    db.close()