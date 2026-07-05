from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Decision Matrix AI")


class Criterion(BaseModel):
    name: str
    weight: float


class CalculateRequest(BaseModel):
    alternatives: list[str]
    criteria: list[Criterion]
    scores: dict[str, dict[str, float]]


class AlternativeResult(BaseModel):
    alternative: str
    total_score: float


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