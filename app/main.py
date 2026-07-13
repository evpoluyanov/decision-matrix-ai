from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas import AlternativeResult, CalculateRequest

app = FastAPI(title="Decision Matrix AI")

templates = Jinja2Templates(directory="app/templates")

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
):
    return templates.TemplateResponse(
        request=request,
        name="project.html",
        context={"project_name": project_name},
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
