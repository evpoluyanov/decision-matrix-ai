
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.schemas import AlternativeResult, CalculateRequest
from fastapi import Depends, FastAPI, Form, Request
from sqlalchemy import select
from sqlalchemy.orm import Session
from app import models
from app.database import Base, engine, get_db

app = FastAPI(title="Decision Matrix AI")

templates = Jinja2Templates(directory="app/templates")

Base.metadata.create_all(bind=engine)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={},
    )

@app.post("/projects", response_class=HTMLResponse)
def create_project(
    request: Request,
    project_name: str = Form(...),
    db: Session = Depends(get_db),
):
    project = models.Project(name=project_name)

    db.add(project)
    db.commit()
    db.refresh(project)

    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={"project": project},
    )

@app.get("/projects", response_class=HTMLResponse)
def list_projects(
    request: Request,
    db: Session = Depends(get_db),
):
    projects = db.scalars(
        select(models.Project).order_by(models.Project.id)
    ).all()

    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={"projects": projects},
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/about")
def about():
    return {"description": "Decision Matrix AI is a tool for helping managers make decisions."}


@app.post("/calculate")
def calculate(request: CalculateRequest) -> list[AlternativeResult]:
    results = []

    for alternative in request.alternatives:
        alternative_scores = request.scores.get(alternative, {})
        total_score = sum(
            alternative_scores.get(criterion.name, 0) * criterion.weight
            for criterion in request.criteria
        )
        results.append(
            AlternativeResult(alternative=alternative, total_score=total_score)
        )

    results.sort(key=lambda item: item.total_score, reverse=True)
    return results
