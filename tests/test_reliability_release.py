import io
import json
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
import httpx
import pytest
from PIL import Image
from sqlalchemy import event
from sqlalchemy.exc import OperationalError
from app import models
from app.llm.errors import ProviderError
from app.services import (score_service, admin_service, growth_service, operation_service,
                          ai_score_generation_service, project_ai_analysis_service)
from conftest import TEST_PASSWORD
from test_ai_budget import prepared, reported, mock_http
from test_ai_usage_routes import llm_response


@pytest.fixture
def matrix100(test_environment):
    env = test_environment
    with env["TestingSessionLocal"]() as db:
        project_id = env["project_1_id"]
        existing_a = db.get(models.Alternative, env["alternative_1_id"])
        existing_c = db.get(models.Criterion, env["criterion_1_id"])
        existing_c.weight = .1
        alternatives = [existing_a] + [models.Alternative(project_id=project_id, name=f"A{i}") for i in range(9)]
        criteria = [existing_c] + [models.Criterion(project_id=project_id, name=f"C{i}", weight=.1) for i in range(9)]
        db.add_all(alternatives + criteria)
        db.flush()
        env["pairs"] = [(a.id,c.id) for a in alternatives for c in criteria]
        db.commit()
    return env


def form100(env, value="7"):
    return {f"score_{a}_{c}": value for a,c in env["pairs"]}


def test_atomic_100_scores_and_one_commit(matrix100):
    with matrix100["TestingSessionLocal"]() as db:
        commits=[]
        event.listen(db,"after_commit",lambda *_: commits.append(1))
        revision=score_service.save_matrix(db,matrix100["project_1_id"],form100(matrix100),0,"save-test-0000000001")
        assert revision == 1
        assert len(commits) == 1
        assert len(score_service.get_scores(db,matrix100["project_1_id"])) == 100
        assert all(s.value == 7 for s in score_service.get_scores(db,matrix100["project_1_id"]).values())
        assert db.query(models.AIRequestLog).count() == 0
        assert db.query(models.ProductEvent).count() == 0


@pytest.mark.parametrize("bad",["NaN","inf","-1","10.1","hello"])
def test_invalid_cell_rejects_entire_matrix(matrix100,bad):
    data=form100(matrix100)
    data[next(reversed(data))]=bad
    with matrix100["TestingSessionLocal"]() as db:
        with pytest.raises(score_service.MatrixSaveError):
            score_service.save_matrix(db,matrix100["project_1_id"],data,0)
        db.rollback()
        assert db.query(models.Score).count() == 0
        assert score_service.matrix_version(db,matrix100["project_1_id"]) == 0


def test_stale_and_repeated_save_cannot_overwrite_newer_data(matrix100):
    with matrix100["TestingSessionLocal"]() as db:
        score_service.save_matrix(db,matrix100["project_1_id"],form100(matrix100),0,"save-test-0000000001")
        assert score_service.save_matrix(db,matrix100["project_1_id"],form100(matrix100),0,"save-test-0000000001") == 1
        with pytest.raises(score_service.MatrixSaveError) as error:
            score_service.save_matrix(db,matrix100["project_1_id"],form100(matrix100,"9"),0,"save-test-0000000002")
        assert error.value.status == 409
        db.rollback()
        assert all(s.value == 7 for s in score_service.get_scores(db,matrix100["project_1_id"]).values())


def test_failed_transaction_rolls_back_all_100_scores(matrix100,monkeypatch):
    with matrix100["TestingSessionLocal"]() as db:
        def fail():
            db.flush()
            raise OperationalError("synthetic",{},Exception("test"))
        monkeypatch.setattr(db,"commit",fail)
        with pytest.raises(OperationalError):
            score_service.save_matrix(db,matrix100["project_1_id"],form100(matrix100),0)
        db.rollback()
        assert db.query(models.Score).count() == 0


def test_failed_form_preserves_escaped_input_and_json_error(client,matrix100):
    client.post("/login",data={"email":"user1@test.com","password":TEST_PASSWORD})
    data={**form100(matrix100),"matrix_revision":"0"}
    first=next(iter(form100(matrix100)))
    data[first]='<script>alert(1)</script>'
    response=client.post(f'/projects/{matrix100["project_1_id"]}/scores',data=data)
    assert response.status_code == 422
    assert "&lt;script&gt;" in response.text and "<script>alert(1)" not in response.text
    response=client.post(f'/projects/{matrix100["project_1_id"]}/scores',data=data,headers={"X-Requested-With":"fetch"})
    assert response.json()["field"] == first


def test_successful_save_has_state_endpoint_and_timing(client,matrix100):
    client.post("/login",data={"email":"user1@test.com","password":TEST_PASSWORD})
    key="save-test-0000000001"
    path=f'/projects/{matrix100["project_1_id"]}/scores'
    response=client.post(path,data={**form100(matrix100),"matrix_revision":"0","request_key":key},headers={"X-Requested-With":"fetch"})
    assert response.status_code == 200
    assert response.json()["matrix_revision"] == 1
    assert "matrix_save;dur=" in response.headers["Server-Timing"]
    assert client.get(path+"/state?request_key="+key).json()["status"] == "saved"


def test_current_preference_counts_one_user_not_events(client,prepared):
    client.get("/pricing")
    for plan in ("project_99","pro_299","free_beta","free_beta"):
        response=client.post("/monetization/preference",data={"selected_plan":plan,"source":"pricing","return_to":"/pricing"})
        assert response.status_code == 200
    assert "Вы продолжаете бесплатное бета-тестирование" in response.text
    assert "Спасибо! Мы проинформируем" not in response.text
    with prepared["TestingSessionLocal"]() as db:
        stats=admin_service.statistics(db,"all")["funnel"]
        assert (stats["project_99"],stats["pro_299"],stats["free_beta"]) == (0,0,1)
        assert stats["free_beta_conversion"] == 100
        assert db.query(models.MonetizationPreference).count() == 1
        assert not db.query(models.MonetizationPreference).one().notify_on_launch
        assert db.query(models.ProductEvent).filter(models.ProductEvent.event_name.in_("project_99_selected pro_299_selected free_beta_selected".split())).count() == 3


def test_cohort_period_exclusion_and_zero_denominator(test_environment,monkeypatch):
    with test_environment["TestingSessionLocal"]() as db:
        user=db.get(models.User,test_environment["user_1_id"])
        growth_service.save_preference(db,user=user,selected_plan="pro_299",source="pricing")
        assert admin_service.statistics(db,1)["funnel"]["pro_299_conversion"] == 0
        growth_service.record_event(db,"paid_offer_viewed",user=user,metadata={"source":"pricing"})
        event_row=db.query(models.ProductEvent).filter_by(event_name="paid_offer_viewed").one()
        event_row.created_at=datetime.now(timezone.utc)-timedelta(days=10)
        db.commit()
        assert admin_service.statistics(db,7)["funnel"]["pro_299"] == 0
        assert admin_service.statistics(db,30)["funnel"]["pro_299"] == 1
        monkeypatch.setenv("MARKETING_EXCLUDED_USER_IDS",str(user.id))
        assert admin_service.statistics(db,"all")["funnel"]["pro_299"] == 0


def test_operation_identity_prevents_second_paid_call(client,prepared,monkeypatch):
    payload=reported(120,40)
    payload["choices"]=[{"message":{"content":llm_response("alternatives",prepared).content},"finish_reason":"stop"}]
    transport=mock_http(monkeypatch,payload=payload)
    path=f'/projects/{prepared["project_1_id"]}/ai/alternatives'
    key="operation-test-00000001"
    assert client.post(path,headers={"X-Operation-Key":key}).status_code == 200
    duplicate=client.post(path,headers={"X-Operation-Key":key})
    assert duplicate.status_code == 409 and duplicate.json()["status"] == "completed"
    assert transport.call_count == 1
    assert client.get(f'/projects/{prepared["project_1_id"]}/ai/operations/{key}').json()["status"] == "completed"
    # A distinct, deliberate generation is still permitted.
    assert client.post(path,headers={"X-Operation-Key":"operation-test-00000002"}).status_code == 200
    assert transport.call_count == 2


def test_active_operation_blocks_new_request_across_tabs(client,prepared,monkeypatch):
    with prepared["TestingSessionLocal"]() as db:
        db.add(models.AIRequestLog(user_id=prepared["user_1_id"],project_id=prepared["project_1_id"],feature="decision_risks",status="started",client_request_key="operation-test-00000001"))
        db.commit()
    transport=mock_http(monkeypatch,payload={})
    response=client.post(f'/projects/{prepared["project_1_id"]}/ai/decision-risks',headers={"X-Operation-Key":"operation-test-00000002"})
    assert response.status_code == 409
    assert response.json()["status"] == "in_progress"
    transport.assert_not_called()


@pytest.mark.parametrize("feature",["decision_risks","result_explanation"])
def test_truncated_reply_preserves_money_and_safe_error(client,prepared,monkeypatch,feature,caplog):
    # Alembic's preceding migration test disables existing loggers globally.
    monkeypatch.setattr(operation_service.logger, "disabled", False)
    payload=reported(120,40)
    payload["choices"]=[{"message":{"content":"PRIVATE TEXT secret@example.com"},"finish_reason":"length"}]
    mock_http(monkeypatch,payload=payload)
    with caplog.at_level("INFO",logger="dmatrix.operations"):
        response=client.post(f'/projects/{prepared["project_1_id"]}/ai/{feature.replace("_","-")}')
    assert response.status_code == 503
    assert response.json()["error_code"] == "truncated_response"
    assert "AI_DIAG" in caplog.text and '"finish_reason": "length"' in caplog.text
    assert "PRIVATE TEXT" not in caplog.text and "secret@example.com" not in caplog.text
    with prepared["TestingSessionLocal"]() as db:
        call=db.query(models.AIProviderCall).one()
        assert call.status == "reported" and call.estimated_microrub > 0
        assert db.query(models.AIRequestLog).one().error_code == "truncated_response"
        assert not growth_service.first_trial_project_id(db,prepared["user_1_id"])


def test_risks_10_by_10_and_failed_reanalysis_preserves_saved(client,prepared,matrix100,monkeypatch):
    with prepared["TestingSessionLocal"]() as db:
        score_service.save_matrix(db,prepared["project_1_id"],form100(matrix100),0)
    payload=reported(400,300)
    payload["choices"]=[{"message":{"content":json.dumps({"s":"ok","i":[{"t":"hypothesis","n":"Risk","r":"Check assumptions","c":"Validate inputs"}]})},"finish_reason":"stop"}]
    transport=mock_http(monkeypatch,payload=payload)
    path=f'/projects/{prepared["project_1_id"]}/ai/decision-risks'
    assert client.post(path).status_code == 200
    assert transport.call_count == 1
    payload["choices"][0]["message"]["content"]="not json"
    assert client.post(path).status_code == 503
    report=client.get(f'/projects/{prepared["project_1_id"]}/report')
    assert report.status_code == 200 and "Check assumptions" in report.text
    page=client.get(f'/projects/{prepared["project_1_id"]}')
    assert page.text.index('id="report-link"') > page.text.index("Риски выбранной альтернативы")
    assert "saved-ai-analysis" in page.text


def test_timeout_keeps_uncertain_reserve_and_status(client,prepared,monkeypatch):
    transport=mock_http(monkeypatch,error=httpx.ReadTimeout("do not log me"))
    key="operation-test-00000001"
    path=f'/projects/{prepared["project_1_id"]}/ai/decision-risks'
    assert client.post(path,headers={"X-Operation-Key":key}).status_code == 503
    state=client.get(f'/projects/{prepared["project_1_id"]}/ai/operations/{key}').json()
    assert state["status"] == "uncertain"
    assert client.post(path,headers={"X-Operation-Key":key}).status_code == 409
    assert transport.call_count == 1
    with prepared["TestingSessionLocal"]() as db:
        call=db.query(models.AIProviderCall).one()
        assert call.charged_microrub == call.reserved_microrub


def test_stale_analysis_not_saved(client,prepared,monkeypatch):
    from app.services import ai_decision_risk_service
    def changed(**kwargs):
        with prepared["TestingSessionLocal"]() as db:
            project_ai_analysis_service.invalidate_analysis(db,prepared["project_1_id"])
            db.commit()
        return {"status":"ok","items":[{"type":"hypothesis","title":"Old","risk":"Old","check":"Old"}]}
    monkeypatch.setattr(ai_decision_risk_service,"generate_decision_risks",changed)
    response=client.post(f'/projects/{prepared["project_1_id"]}/ai/decision-risks')
    assert response.status_code == 503 and response.json()["error_code"] == "matrix_changed"
    with prepared["TestingSessionLocal"]() as db:
        assert project_ai_analysis_service.get_analysis(db,prepared["project_1_id"]) is None


def test_stale_score_batch_cannot_overwrite_manual_edit(matrix100):
    from app.services import ai_usage_service
    with matrix100["TestingSessionLocal"]() as db:
        project=db.get(models.Project,matrix100["project_1_id"])
        alternatives=db.query(models.Alternative).filter_by(project_id=project.id).all()
        criteria=db.query(models.Criterion).filter_by(project_id=project.id).all()
        log=ai_usage_service.reserve_ai_request(db=db,user_id=project.owner_id,project_id=project.id,feature="scores")
        job=ai_score_generation_service.create_job(db,project,log,alternatives,criteria)
        batch=ai_score_generation_service.claim_batch(db,job,alternatives,criteria)
        score_service.save_matrix(db,project.id,form100(matrix100,"9"),0)
        with pytest.raises(ai_score_generation_service.MatrixChangedError):
            ai_score_generation_service.finish_batch(db,job,criteria,batch,{"items":[]})
        assert all(s.value == 9 for s in score_service.get_scores(db,project.id).values())


@pytest.mark.parametrize("name,mime,size",[("favicon.svg","image/svg+xml",None),("favicon-120.png","image/png",120),("apple-touch-icon.png","image/png",180),("favicon.ico","image/vnd.microsoft.icon",48)])
def test_public_favicon_files(client,monkeypatch,name,mime,size):
    monkeypatch.setenv("PUBLIC_SITE_URL","https://dmatrix.tech")
    response=client.get("/"+name,follow_redirects=False)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith(mime)
    assert "noindex" not in response.headers.get("x-robots-tag","")
    assert client.head("/"+name).status_code == 200
    if size:
        image=Image.open(io.BytesIO(response.content))
        assert image.size==(size,size)
        if name.endswith(".ico"): assert image.ico.sizes()=={(16,16),(32,32),(48,48)}
    else: assert b"<svg" in response.content
    assert "Allow: /"+name+"$" in client.get("/robots.txt").text
    assert name not in client.get("/sitemap.xml").text
    assert client.get("/").text.count('href="/'+name+'"') == 1


def test_internal_proxy_referrer_and_invalid_port_are_not_sources(monkeypatch):
    from starlette.requests import Request
    from app.services.attribution_service import capture_first_touch,SESSION_KEY
    monkeypatch.setenv("CODESPACE_NAME","test-preview")
    for ref in ["https://test-preview-8000.app.github.dev/admin","https://invalid.test:bad/path"]:
        request=Request({"type":"http","method":"GET","scheme":"http","path":"/register","query_string":b"","server":("localhost",8000),"headers":[(b"referer",ref.encode())],"session":{}})
        capture_first_touch(request)
        assert request.session[SESSION_KEY]["referrer"] is None
