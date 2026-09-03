import json

from sqlalchemy import update
from sqlalchemy.orm import Session

from app import models


def get_analysis(
    db: Session,
    project_id: int,
) -> models.ProjectAIAnalysis | None:
    return (
        db.query(
            models.ProjectAIAnalysis
        )
        .filter_by(
            project_id=project_id
        )
        .first()
    )

def invalidate_analysis(
    db: Session,
    project_id: int,
) -> bool:
    """
    Удаляет сохранённую AI-аналитику проекта.

    Используется, когда исходные данные
    матрицы изменились и старый анализ
    больше нельзя считать актуальным.
    """
    # Also serializes writers and invalidates snapshots held by in-flight AI.
    db.execute(update(models.Project).where(models.Project.id == project_id).values(
        matrix_revision=models.Project.matrix_revision + 1,
    ))
    analysis = get_analysis(
        db=db,
        project_id=project_id,
    )

    if analysis is None:
        return False

    db.delete(analysis)
    db.flush()

    return True

def get_or_create_analysis(
    db: Session,
    project_id: int,
) -> models.ProjectAIAnalysis:
    analysis = get_analysis(
        db=db,
        project_id=project_id,
    )

    if analysis is not None:
        return analysis

    analysis = models.ProjectAIAnalysis(
        project_id=project_id,
    )

    db.add(analysis)
    db.flush()

    return analysis


def save_result_explanation(
    *,
    db: Session,
    project_id: int,
    result: dict,
) -> models.ProjectAIAnalysis:
    analysis = get_or_create_analysis(
        db=db,
        project_id=project_id,
    )

    analysis.result_summary = (
        result.get("summary")
    )

    analysis.result_factors_json = (
        json.dumps(
            result.get(
                "factors",
                [],
            ),
            ensure_ascii=False,
        )
    )

    analysis.result_strengths_json = (
        json.dumps(
            result.get(
                "strengths",
                [],
            ),
            ensure_ascii=False,
        )
    )

    analysis.result_weaknesses_json = (
        json.dumps(
            result.get(
                "weaknesses",
                [],
            ),
            ensure_ascii=False,
        )
    )

    analysis.result_competitor = (
        result.get("competitor")
    )

    analysis.result_caveat = (
        result.get("caveat")
    )

    analysis.result_preliminary = bool(
        result.get(
            "preliminary",
            False,
        )
    )

    db.commit()
    db.refresh(analysis)

    return analysis


def save_decision_risks(
    *,
    db: Session,
    project_id: int,
    result: dict,
) -> models.ProjectAIAnalysis:
    analysis = get_or_create_analysis(
        db=db,
        project_id=project_id,
    )

    analysis.decision_risks_json = (
        json.dumps(
            result.get(
                "items",
                [],
            ),
            ensure_ascii=False,
        )
    )

    analysis.decision_risks_preliminary = (
        bool(
            result.get(
                "preliminary",
                False,
            )
        )
    )

    db.commit()
    db.refresh(analysis)

    return analysis


def decode_list(
    value: str | None,
) -> list:
    if not value:
        return []

    try:
        data = json.loads(value)
    except json.JSONDecodeError:
        return []

    if not isinstance(
        data,
        list,
    ):
        return []

    return data


def to_report_data(
    analysis: models.ProjectAIAnalysis | None,
) -> dict:
    if analysis is None:
        return {
            "result": None,
            "decision_risks": [],
        }

    result = None

    if analysis.result_summary:
        result = {
            "summary":
                analysis.result_summary,
            "factors":
                decode_list(
                    analysis.result_factors_json
                ),
            "strengths":
                decode_list(
                    analysis.result_strengths_json
                ),
            "weaknesses":
                decode_list(
                    analysis.result_weaknesses_json
                ),
            "competitor":
                analysis.result_competitor,
            "caveat":
                analysis.result_caveat,
            "preliminary":
                analysis.result_preliminary,
        }

    return {
        "result": result,
        "decision_risks":
            decode_list(
                analysis.decision_risks_json
            ),
        "decision_risks_preliminary":
            analysis.decision_risks_preliminary,
    }

