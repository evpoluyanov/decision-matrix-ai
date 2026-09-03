from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.llm.safety import (
    MAX_ENTITY_NAME_LENGTH,
    MAX_PROJECT_DESCRIPTION_LENGTH,
    MAX_PROJECT_NAME_LENGTH,
)

from app import models
from app.auth_dependencies import (
    require_alternative_owner,
    require_project_owner,
)
from app.database import get_db
from app.services import (
    alternative_service,
    calculation_service,
    criterion_service,
    project_service,
    score_service,
    risk_service,
    project_ai_analysis_service,
    growth_service,
    feedback_service,
    public_site_service,
)


router = APIRouter()

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/projects/{project_id}",
    response_class=HTMLResponse,
)
def project_detail(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
    weight_error: int | None = None,
):
    alternatives = alternative_service.get_alternatives(
        db,
        project.id,
    )

    criteria = criterion_service.get_criteria(
        db,
        project.id,
    )

    scores = score_service.get_scores(
        db,
        project.id,
    )

    score_summary = (
        score_service.get_score_summary(
            scores=scores,
            alternatives_count=len(
                alternatives
            ),
            criteria_count=len(
                criteria
            ),
        )
    )

    results = calculation_service.calculate_results(
        db=db,
        project_id=project.id,
    )
    user = db.get(models.User, project.owner_id)
    growth_service.record_project_value(
        db, user=user, project_id=project.id, results=results,
    )

    risk_analysis = (
        risk_service.analyze_decision_risks(
            criteria=criteria,
            results=results,
            score_summary=score_summary,
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "project": project,
            "alternatives": alternatives,
            "criteria": criteria,
            "scores": scores,
            "score_summary": score_summary,
            "results": results,
            "risk_analysis": risk_analysis,
            "weight_error": weight_error,
            "saved_ai_analysis": project_ai_analysis_service.to_report_data(
                project_ai_analysis_service.get_analysis(db, project.id)),
            "show_second_project_offer": growth_service.should_offer_for_second_project(
                db, user_id=user.id, project_id=project.id,
            ),
            **public_site_service.product_analytics_context(request),
        },
    )


@router.get(
    "/projects/{project_id}/report",
    response_class=HTMLResponse,
)
def project_report(
    project_id: int,
    request: Request,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    alternatives = (
        alternative_service
        .get_alternatives(
            db,
            project.id,
        )
    )

    criteria = (
        criterion_service
        .get_criteria(
            db,
            project.id,
        )
    )

    scores = (
        score_service
        .get_scores(
            db,
            project.id,
        )
    )

    score_summary = (
        score_service
        .get_score_summary(
            scores=scores,
            alternatives_count=len(
                alternatives
            ),
            criteria_count=len(
                criteria
            ),
        )
    )

    results = (
        calculation_service
        .calculate_results(
            db=db,
            project_id=project.id,
        )
    )
    user = db.get(models.User, project.owner_id)
    growth_service.record_project_value(
        db, user=user, project_id=project.id, results=results,
    )
    report_was_recorded = growth_service.has_event(
        db, "report_generated", user_id=user.id, project_id=project.id,
    )
    growth_service.record_project_value(
        db, user=user, project_id=project.id, results=results, report=True,
    )
    is_trial_report = (
        bool(results)
        and growth_service.first_trial_project_id(db, user.id) == project.id
    )
    report_question_answered = feedback_service.has_report_answer(db, user.id)
    show_monetization_offer = (
        is_trial_report and growth_service.preference_for(db, user.id) is None
    )
    offer_was_recorded = growth_service.has_event(
        db, "paid_offer_viewed", user_id=user.id, project_id=project.id,
    )
    if show_monetization_offer:
        growth_service.record_event(
            db, "paid_offer_viewed", user=user, project_id=project.id,
            metadata={"source": "report"},
            dedupe_key=f"paid_offer_viewed:user:{user.id}:source:report:project:{project.id}",
        )

    risk_analysis = (
        risk_service
        .analyze_decision_risks(
            criteria=criteria,
            results=results,
            score_summary=score_summary,
        )
    )

    saved_ai_analysis = (
        project_ai_analysis_service
        .get_analysis(
            db=db,
            project_id=project.id,
        )
    )

    ai_report = (
        project_ai_analysis_service
        .to_report_data(
            saved_ai_analysis
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="project_report.html",
        context={
            "project": project,
            "alternatives": alternatives,
            "criteria": criteria,
            "scores": scores,
            "score_summary": score_summary,
            "results": results,
            "risk_analysis": risk_analysis,
            "ai_report": ai_report,
            "show_monetization_offer": show_monetization_offer,
            "offer_source": "report",
            "offer_event_recorded": show_monetization_offer and not offer_was_recorded,
            "show_report_feedback": is_trial_report and not report_question_answered,
            "report_question_answered": report_question_answered,
            "report_event_recorded": is_trial_report and not report_was_recorded,
            **public_site_service.product_analytics_context(request),
        },
    )

@router.post(
    "/projects/{project_id}/edit",
)
def edit_project(
    project_id: int,
    project_name: str = Form(
        ...,
        min_length=1,
        max_length=MAX_PROJECT_NAME_LENGTH,
    ),
    project_description: str | None = Form(
        None,
        max_length=MAX_PROJECT_DESCRIPTION_LENGTH,
    ),
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    project_service.update_project(
        db=db,
        project=project,
        project_name=project_name,
        project_description=project_description,
    )

    return RedirectResponse(
        url=f"/projects/{project.id}",
        status_code=303,
    )


@router.post(
    "/projects/{project_id}/delete",
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    project_service.delete_project(
        db=db,
        project=project,
    )

    return RedirectResponse(
        url="/projects",
        status_code=303,
    )


@router.post(
    "/projects/{project_id}/copy",
)
def copy_project(
    project_id: int,
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    project_service.copy_project(
        db=db,
        source_project=project,
    )

    return RedirectResponse(
        url="/projects",
        status_code=303,
    )


@router.post(
    "/projects/{project_id}/alternatives",
)
def create_alternative(
    project_id: int,
    name: str = Form(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
    ),
    db: Session = Depends(get_db),
    project: models.Project = Depends(
        require_project_owner
    ),
):
    alternative_service.create_alternative(
        db=db,
        project_id=project.id,
        name=name,
    )

    return RedirectResponse(
        url=f"/projects/{project.id}",
        status_code=303,
    )


@router.post(
    "/alternatives/{alternative_id}/delete",
)
def delete_alternative(
    db: Session = Depends(get_db),
    alternative: models.Alternative = Depends(
        require_alternative_owner
    ),
):
    project_id = alternative.project_id

    alternative_service.delete_alternative(
        db=db,
        alternative_id=alternative.id,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )


@router.post(
    "/alternatives/{alternative_id}/edit",
)
def edit_alternative(
    name: str = Form(
        ...,
        min_length=1,
        max_length=MAX_ENTITY_NAME_LENGTH,
    ),
    db: Session = Depends(get_db),
    alternative: models.Alternative = Depends(
        require_alternative_owner
    ),
):
    project_id = alternative.project_id

    alternative_service.update_alternative(
        db=db,
        alternative_id=alternative.id,
        name=name,
    )

    return RedirectResponse(
        url=f"/projects/{project_id}",
        status_code=303,
    )
