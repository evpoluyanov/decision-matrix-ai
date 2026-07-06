from pydantic import BaseModel


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
