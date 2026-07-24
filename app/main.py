from fastapi import FastAPI

from app import models
from app.database import Base, engine
from app.routers import alternatives, criteria, projects, scores
from app.schemas import AlternativeResult, CalculateRequest
from app.routers import alternatives

app = FastAPI(title="Decision Matrix AI")

Base.metadata.create_all(bind=engine)

app.include_router(projects.router)
app.include_router(alternatives.router)
app.include_router(criteria.router)
app.include_router(scores.router)

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
