import os

from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from app.routers import (
    alternatives,
    auth,
    criteria,
    projects,
    scores,
)
from app.schemas import AlternativeResult, CalculateRequest


load_dotenv(dotenv_path=".env")

session_secret = os.getenv("SESSION_SECRET")

if not session_secret:
    raise RuntimeError(
        "Не задана переменная SESSION_SECRET"
    )

session_https_only = (
    os.getenv(
        "SESSION_HTTPS_ONLY",
        "false",
    ).lower()
    == "true"
)


app = FastAPI(title="Decision Matrix AI")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="decision_matrix_session",
    max_age=60 * 60 * 24 * 14,
    same_site="lax",
    https_only=session_https_only,
)

app.include_router(projects.router)
app.include_router(alternatives.router)
app.include_router(criteria.router)
app.include_router(scores.router)
app.include_router(auth.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/about")
def about():
    return {
        "description": (
            "Decision Matrix AI is a tool for helping managers make decisions."
        )
    }


@app.post("/calculate")
def calculate(
    request: CalculateRequest,
) -> list[AlternativeResult]:
    results = []

    for alternative in request.alternatives:
        alternative_scores = request.scores.get(
            alternative,
            {},
        )

        total_score = sum(
            alternative_scores.get(
                criterion.name,
                0,
            )
            * criterion.weight
            for criterion in request.criteria
        )

        results.append(
            AlternativeResult(
                alternative=alternative,
                total_score=total_score,
            )
        )

    results.sort(
        key=lambda item: item.total_score,
        reverse=True,
    )

    return results