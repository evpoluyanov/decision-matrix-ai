"""Synthetic, in-memory SQLite benchmark. Never reads .env or calls an LLM."""
import json
import statistics
import time
import sys
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from app.database import Base
from app import models
from app.services import score_service


def run(read=False):
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine, autoflush=False) as db:
        user = models.User(email="benchmark@example.invalid", password_hash="unused")
        db.add(user)
        db.flush()
        project = models.Project(name="Synthetic", owner_id=user.id)
        db.add(project)
        db.flush()
        alternatives = [models.Alternative(name=str(i), project_id=project.id) for i in range(10)]
        criteria = [models.Criterion(name=str(i), project_id=project.id, weight=.1) for i in range(10)]
        db.add_all(alternatives + criteria)
        db.flush()
        pairs = [(a.id, c.id) for a in alternatives for c in criteria]
        project_id = project.id
        db.add_all([models.Score(alternative_id=a, criterion_id=c, value=1) for a,c in pairs])
        db.commit()
        counts = {"sql": 0, "commits": 0}
        event.listen(engine, "before_cursor_execute", lambda *args: counts.__setitem__("sql", counts["sql"] + 1))
        event.listen(db, "after_commit", lambda *args: counts.__setitem__("commits", counts["commits"] + 1))
        runs = []
        for index in range(6):
            data = {f"score_{a}_{c}": str(index+2) for a,c in pairs}
            counts.update(sql=0, commits=0)
            started = time.perf_counter()
            if read:
                from app.services.calculation_service import calculate_results
                db.expunge_all()
                calculate_results(db, project_id)
            elif hasattr(score_service, "save_matrix"):
                version = score_service.matrix_version(db, project_id)
                score_service.save_matrix(db, project_id, data, version)
            else:
                for a,c in pairs:
                    score_service.set_score(db, a, c, index+2)
            elapsed = (time.perf_counter()-started)*1000
            if index:
                runs.append({"ms": round(elapsed,3), **counts})
        print(json.dumps({"stage": "rating_read" if read else "matrix_save", "engine": "SQLite memory", "cells":100, "runs":runs,
            "median_ms":round(statistics.median(r["ms"] for r in runs),3)},ensure_ascii=False))
        if read:
            from starlette.requests import Request
            from app.routers import alternatives as routes
            request = Request({"type":"http", "method":"GET", "path":f"/projects/{project_id}",
                "scheme":"http", "server":("localhost",8000), "headers":[], "query_string":b"", "session":{}})
            original = routes.templates.TemplateResponse
            render_times = []
            def timed(*args, **kwargs):
                stamp = time.perf_counter()
                result = original(*args, **kwargs)
                render_times.append((time.perf_counter()-stamp)*1000)
                return result
            routes.templates.TemplateResponse = timed
            page_times = []
            try:
                for _ in range(6):
                    db.expunge_all()
                    stamp = time.perf_counter()
                    routes.project_detail(project_id, request, db, db.get(models.Project,project_id))
                    page_times.append((time.perf_counter()-stamp)*1000)
            finally:
                routes.templates.TemplateResponse = original
            print(json.dumps({"stage":"page_server_prepare_and_render", "median_ms":round(statistics.median(page_times[1:]),3),
                "template_render_median_ms":round(statistics.median(render_times[1:]),3), "browser_render":"not measured"}))
    engine.dispose()


if __name__ == "__main__":
    run(read="--read" in sys.argv)
