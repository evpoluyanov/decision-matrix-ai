"""Explicit local-only UI demo: fresh synthetic SQLite DB, mocked HTTP, no paid APIs.

Run from the repository: python -m scripts.preview_mock_server
Never used or imported by app.main/Vercel. Never opens an existing database.
"""
import argparse
import json
import os
import secrets
import tempfile
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--delay", type=float, default=2)
    parser.add_argument("--risk-mode", choices=["ok", "fail-second", "truncated", "timeout"], default="fail-second")
    parser.add_argument("--check", action="store_true", help="Run in-process HTTP smoke checks, without a browser or listening port")
    args = parser.parse_args()
    if os.getenv("VERCEL") == "1":
        raise SystemExit("Local demo only. Do not run in Vercel.")
    if not 1024 <= args.port <= 65535 or not 0 <= args.delay <= 30:
        raise SystemExit("Invalid port or delay (allowed: 0–30 seconds).")
    directory = Path(tempfile.mkdtemp(prefix="dmatrix-synthetic-preview-"))
    db_url = f"sqlite:///{directory / 'preview.db'}"
    base = (f'https://{os.environ["CODESPACE_NAME"]}-{args.port}.app.github.dev'
            if os.getenv("CODESPACE_NAME") else f"http://127.0.0.1:{args.port}")
    # Set these BEFORE importing any app modules: dotenv will not overwrite them.
    os.environ.update({"DATABASE_URL":db_url, "MIGRATION_DATABASE_URL":db_url,
        "SESSION_SECRET":secrets.token_urlsafe(40), "SESSION_HTTPS_ONLY":"false",
        "APP_BASE_URL":base, "PUBLIC_SITE_URL":"", "YANDEX_METRIKA_ID":"",
        "ADMIN_USER_IDS":"1", "MARKETING_EXCLUDED_USER_IDS":"", "MARKETING_TEST_EMAILS":"", "AI_ENABLED":"true", "AI_PRICING_CONFIRMED":"true",
        "AI_DAILY_BUDGET_RUB":"100", "AI_REQUESTS_PER_MINUTE":"3", "AI_REQUESTS_PER_24_HOURS":"30",
        "AI_INPUT_RUB_PER_MILLION":"13.42", "AI_OUTPUT_RUB_PER_MILLION":"54.90",
        "LLM_PROVIDER":"mws", "LLM_MODEL":"gpt-oss-120b",
        "LLM_API_KEY":"synthetic-preview-not-a-secret", "LLM_BASE_URL":"https://llm.invalid",
        "BREVO_API_KEY":"", "BREVO_SENDER_EMAIL":""})
    import httpx
    counters = {"risk":0}

    def transport(_transport, request):
        if request.url.host != "llm.invalid" or request.url.path != "/chat/completions":
            raise httpx.ConnectError("Outbound HTTP is disabled in synthetic Preview",request=request)
        time.sleep(args.delay)
        payload = json.loads(request.content)
        system = payload["messages"][0]["content"]
        data = json.loads(payload["messages"][1]["content"])
        finish = "stop"
        if "existing_alternatives" in data:
            offset=len(data["existing_alternatives"])
            result={"s":"ok","i":[{"n":f"Демо-вариант {offset+i+1}","r":"Искусственное предложение для проверки интерфейса."} for i in range(5)]}
        elif "existing_criteria" in data:
            offset=len(data["existing_criteria"])
            weight=min(10,data["remaining_weight_percent"]/5)
            result={"s":"ok","i":[{"n":f"Демо-критерий {offset+i+1}","w":weight,"cr":"Тест критерия.","wr":"Тест распределения веса."} for i in range(5)]}
        elif "summary" in system:
            result={"summary":"Демонстрационное объяснение: рейтинг рассчитан по заданным весам.",
                "factors":["Демо-фактор"],"strengths":["Демо-преимущество"],"weaknesses":[],"competitor":"Демо-сравнение","caveat":"Это имитация модели, не рекомендация."}
        elif "hypothesis" in system:
            counters["risk"]+=1
            if args.risk_mode=="timeout":
                raise httpx.ReadTimeout("Synthetic timeout",request=request)
            result={"s":"ok","i":[{"t":"hypothesis","n":"Демо-риск","r":"Следует проверить предположения.","c":"Сравните с исходными данными."}]}
            if args.risk_mode=="truncated":finish="length"
            if args.risk_mode=="fail-second" and counters["risk"]==2:result=None
        else:
            result={"s":"ok","i":[{"a":a["id"],"c":c["id"],"v":7,"r":"Искусственная оценка для теста."} for a in data["alternatives"] for c in data["criteria"]]}
        return httpx.Response(200,request=request,json={"id":"synthetic-"+secrets.token_hex(8),"model":"gpt-oss-120b",
            "choices":[{"message":{"content":json.dumps(result,ensure_ascii=False) if result is not None else "invalid json"},"finish_reason":finish}],
            "usage":{"prompt_tokens":120,"completion_tokens":80,"total_tokens":200,"completion_tokens_details":{"reasoning_tokens":20}}})

    httpx.HTTPTransport.handle_request=transport
    class SyntheticClient(httpx.Client):
        def __init__(self, *args, **kwargs):
            # No sockets or environment proxies: the response is generated in process.
            kwargs.update(transport=httpx.MockTransport(lambda request: transport(None,request)), trust_env=False)
            super().__init__(*args, **kwargs)
    httpx.Client=SyntheticClient
    from alembic import command
    from alembic.config import Config
    command.upgrade(Config("alembic.ini"),"head")
    from app import models
    from app.database import SessionLocal
    from app.security import hash_password
    from app.main import app
    import uvicorn
    password="preview-only-123"
    with SessionLocal() as db:
        users=[models.User(email=email,password_hash=hash_password(password),email_verified=True)
               for email in ["admin@example.com","tester@example.com"]]
        db.add_all(users);db.flush()
        project=models.Project(owner_id=users[1].id,name="Демо 10 × 10",description="Выбираем поставщика для демонстрационной проверки. Все данные искусственные.")
        db.add(project);db.flush()
        alternatives=[models.Alternative(project_id=project.id,name=f"Демо-поставщик {i+1}") for i in range(10)]
        criteria=[models.Criterion(project_id=project.id,name=f"Демо-критерий {i+1}",weight=.1) for i in range(10)]
        db.add_all(alternatives+criteria);db.flush()
        db.add_all([models.Score(alternative_id=a.id,criterion_id=c.id,value=5) for a in alternatives for c in criteria]);db.commit()
    print(f"SYNTHETIC PREVIEW ONLY: {base}\nDB: {directory / 'preview.db'}\nAccounts: admin@example.com / tester@example.com\nTest password: {password}\nNo real AI, email or analytics calls. Keep the Codespaces port PRIVATE. Stop with Ctrl+C.",flush=True)
    if args.check:
        from fastapi.testclient import TestClient
        with TestClient(app,base_url=base,headers={"Origin":base}) as client:
            assert client.get('/health').status_code==200
            assert client.post('/login',data={"email":"tester@example.com","password":password}).status_code==200
            for path in ['/projects/1','/pricing','/favicon.svg','/favicon-120.png','/favicon.ico','/apple-touch-icon.png']:
                assert client.get(path).status_code==200, path
            first=client.post('/projects/1/ai/decision-risks',headers={"X-Operation-Key":"preview-smoke-00000001"})
            assert first.status_code==(503 if args.risk_mode in {'timeout','truncated'} else 200), first.text
            if args.risk_mode=='fail-second':
                assert client.post('/projects/1/ai/decision-risks',headers={"X-Operation-Key":"preview-smoke-00000002"}).status_code==503
                assert 'Демо-риск' in client.get('/projects/1/report').text
        print('Synthetic HTTP smoke passed. Browser rendering NOT checked.')
        return
    uvicorn.run(app,host="127.0.0.1",port=args.port,proxy_headers=False)


if __name__=="__main__":
    main()
