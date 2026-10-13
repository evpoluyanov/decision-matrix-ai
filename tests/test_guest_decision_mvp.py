import json
from datetime import timedelta

import pytest
from app import models
from app.llm.schemas import LLMResponse, LLMUsage
from app.services import decision_service as service, cookie_consent_service
from tests.conftest import TEST_PASSWORD


@pytest.fixture
def decision_mock(monkeypatch):
    calls = []
    def generate(**kwargs):
        data = json.loads(kwargs["user_prompt"])
        calls.append(data)
        if "allow_suggestions" in data:
            result = {"options": ["А", "Б"], "conditions": [{"name": "Без поездок", "required": True}],
                      "questions": ["Что важнее?"], "additional_options": ["В"],
                      "additional_conditions": [{"name": "Стоимость", "required": False}]}
        else:
            result = {"cells": [{"option": o, "condition": c["name"],
                "status": "no" if o == "А" else "yes", "detail": "По вашим условиям", "basis": "user",
                "evidence": "А требует поездок" if o == "А" else "Б без поездок"}
                for o in data["options"] for c in data["conditions"]], "observations": ["Сравните расписание."]}
        return LLMResponse(content=json.dumps(result), provider="mock", model="mock", usage=LLMUsage(1,1,0,2))
    monkeypatch.setattr(service.llm, "generate", generate)
    return calls


def start(client, allow="yes"):
    r = client.post("/start", data={"decision_question": "Как учиться?", "decision_details": "А требует поездок, Б без поездок",
                                    "allow_suggestions": allow})
    assert r.status_code == 200, r.text
    return r.json()["url"]


def compare(client, url):
    data = client.get(url+"/status").json()
    payload = {**data["understanding"], "revision": data["revision"]}
    r = client.post(url+"/compare", json=payload)
    assert r.status_code == 200, r.text
    return client.get(url+"/status").json()


def test_guest_full_journey_no_registration(client, decision_mock, test_environment):
    assert "Без регистрации" in client.get("/").text
    url = start(client)
    result = compare(client, url)
    assert result["state"] == "result"
    assert result["result"]["rows"][0]["status"] == "excluded"
    assert result["result"]["rows"][1]["status"] == "eligible"
    assert "Б" in result["result"]["summary"]
    before = len(decision_mock)
    assert client.get(url).status_code == 200
    assert client.get(url+"/status").json()["result"] == result["result"]
    assert len(decision_mock) == before
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.ProductEvent).count() == 0
        assert db.query(models.AIRequestLog).filter_by(user_id=None).count() == 2


def test_guest_privacy_and_expiry(client, decision_mock, test_environment):
    url = start(client)
    from fastapi.testclient import TestClient
    from app.main import app
    with TestClient(app) as other:
        assert other.get(url).status_code == 404
        assert other.get(url+"/status").status_code == 404
    with test_environment["TestingSessionLocal"]() as db:
        b = db.get(models.DecisionBrief, url.rsplit('/',1)[1]); b.expires_at = service.now()-timedelta(days=1);db.commit()
    assert client.get(url).status_code == 410
    client.get("/")
    with test_environment["TestingSessionLocal"]() as db:
        assert db.query(models.DecisionBrief).count() == 0


def test_suggestions_off_stale_revision_and_existing_login_save(client, decision_mock, test_environment, verified_users):
    url = start(client, "no")
    state = client.get(url+"/status").json()
    assert state["understanding"]["additional_options"] == []
    assert state["understanding"]["additional_conditions"] == []
    assert client.post(url+"/compare", json={**state["understanding"], "revision": 99}).status_code == 409
    compare(client, url)
    r = client.post(url+"/save", follow_redirects=False)
    assert r.headers["location"] == "/login?from=save"
    before = len(decision_mock)
    r = client.post('/login',data={'email':'user1@test.com','password':TEST_PASSWORD},follow_redirects=False)
    assert r.headers['location'] == url
    assert client.get(url+'/status').json()['saved'] is True
    assert len(decision_mock) == before
    assert url in client.get('/decisions/mine').text


def test_unknown_mandatory_no_artificial_winner(client, decision_mock, monkeypatch):
    url=start(client)
    original=service.llm.generate
    def incomplete_evidence(**kwargs):
        r=original(**kwargs);data=json.loads(r.content)
        for c in data['cells']:c['evidence']='invented fact'
        r.content=json.dumps(data);return r
    monkeypatch.setattr(service.llm,'generate',incomplete_evidence)
    result=compare(client,url)['result']
    assert all(r['status']=='conditional' for r in result['rows'])
    assert 'нельзя подтвердить' in result['summary']


def test_new_registration_confirmation_claims_result(client, decision_mock, monkeypatch, test_environment):
    from app.services import email_verification_service
    sent=[]
    monkeypatch.setattr(email_verification_service,'send_email_verification_message',lambda **kw:sent.append(kw))
    url=start(client);compare(client,url);client.post(url+'/save')
    response=client.post('/register',data={'email':'new@test.com','password':TEST_PASSWORD,
        'password_confirmation':TEST_PASSWORD,'terms_accepted':'yes','personal_data_consent':'yes'},follow_redirects=False)
    assert response.status_code==303
    with test_environment['TestingSessionLocal']() as db:
        user=db.query(models.User).filter_by(email='new@test.com').one()
        uid=user.id
        b=db.get(models.DecisionBrief,url.rsplit('/',1)[1]);assert b.owner_id is None and b.pending_user_id==uid
    token=email_verification_service.create_email_verification_token(user_id=uid)
    r=client.post('/verify-email',data={'token':token},follow_redirects=False)
    assert r.headers['location']==url
    assert client.get(url+'/status').json()['saved']
    client.post('/verify-email',data={'token':token})
    with test_environment['TestingSessionLocal']() as db:
        assert db.query(models.DecisionBrief).filter_by(owner_id=uid).count()==1


def test_consent_funnel_dedupe_and_no_texts(client, decision_mock, test_environment):
    client.cookies.set(cookie_consent_service.COOKIE_NAME,cookie_consent_service.encode_choice('yes'))
    client.get('/');client.post('/decisions/events',json={'event':'input_started','email':'private@test.com'})
    url=start(client)
    for _ in range(2):client.post('/decisions/events',json={'event':'understanding_viewed','brief':url.rsplit('/',1)[1]})
    compare(client,url)
    client.post('/decisions/events',json={'event':'result_viewed','brief':url.rsplit('/',1)[1]})
    with test_environment['TestingSessionLocal']() as db:
        ev=db.query(models.ProductEvent).all()
        assert sum(e.event_name=='understanding_viewed' for e in ev)==1
        assert all('private' not in e.metadata_json and 'поездок' not in e.metadata_json for e in ev)
        funnel=service.funnel(db,'all')
        assert next(r['count'] for r in funnel['rows'] if r['name']=='result_viewed')==1
    client.cookies.set(cookie_consent_service.COOKIE_NAME,cookie_consent_service.encode_choice('no'))
    assert client.post('/decisions/events',json={'event':'example_selected'}).json()=={'recorded':False}


def test_all_pairs_batched_without_count_cap(client, decision_mock):
    url=start(client)
    state=client.get(url+'/status').json()
    options=['А']*0+[f'Вариант {i}' for i in range(25)]
    conditions=[{'name':f'Условие {i}','required':False} for i in range(23)]
    r=client.post(url+'/compare',json={'options':options,'conditions':conditions,'revision':state['revision']})
    assert r.status_code==200
    result=client.get(url+'/status').json()['result']
    assert len(result['rows'])==25
    assert all(len(row['cells'])==23 for row in result['rows'])
    assert len(decision_mock)==1+9*6


def test_disabled_ai_preserves_input(client, monkeypatch, test_environment):
    monkeypatch.setenv('AI_ENABLED','false')
    r=client.post('/start',data={'decision_question':'Сохранённый вопрос'})
    assert r.status_code==503
    with test_environment['TestingSessionLocal']() as db:
        assert db.query(models.DecisionBrief).one().question=='Сохранённый вопрос'


def test_placeholder_and_menu(client):
    page=client.get('/').text
    assert 'allow_suggestions' in page and 'checked' in page
    assert '/pricing' not in page
    assert 'decision-menu' in page
    css=client.get('/static/decision-mvp.css').text
    assert 'color:#000!important' in css and 'color:#a1a7ad!important' in css


def test_revoked_consent_stops_background_events(client, decision_mock, test_environment):
    client.cookies.set(cookie_consent_service.COOKIE_NAME, cookie_consent_service.encode_choice('yes'))
    client.get('/')
    url = start(client)
    with test_environment['TestingSessionLocal']() as db:
        jid = db.get(models.DecisionBrief, url.rsplit('/',1)[1]).journey_id
        before = db.query(models.ProductEvent).count()
    client.post('/cookie-consent', data={'analytics':'no','next_path':'/'})
    with test_environment['TestingSessionLocal']() as db:
        service.event(db, jid, 'operation_failed')
        assert db.query(models.ProductEvent).count() == before
        assert not db.get(models.DecisionJourney, jid).analytics_enabled


def test_lost_start_response_can_be_recovered_without_ai(client, decision_mock):
    url = start(client)
    count = len(decision_mock)
    active = client.get('/decisions/active').json()
    assert active['url'] == url and active['question'] == 'Как учиться?'
    assert len(decision_mock) == count


def test_invalid_provider_result_preserves_previous_result(client, decision_mock, monkeypatch):
    url = start(client)
    before = compare(client, url)
    from app.llm.schemas import LLMResponse, LLMUsage
    monkeypatch.setattr(service.llm, 'generate', lambda **kw: LLMResponse(
        content='{"cells":', provider='mock', model='mock', usage=LLMUsage(1,1,0,2)))
    client.post(url+'/compare', json={**before['understanding'], 'revision':before['revision']})
    after = client.get(url+'/status').json()
    assert after['state'] == 'error' and after['error_code'] == 'invalid_response'
    assert after['result'] == before['result']


def test_guest_real_provider_boundary_reserves_and_reports_cost(client, monkeypatch, test_environment):
    import httpx
    original_client = httpx.Client
    sent = []
    def response(request):
        payload = json.loads(request.content)
        sent.append(payload)
        data = {"options":["А", "Б"], "conditions":[{"name":"Без поездок", "required":True}]}
        return httpx.Response(200, request=request, json={"model":"gpt-oss-120b",
            "choices":[{"message":{"content":json.dumps(data)}, "finish_reason":"stop"}],
            "usage":{"prompt_tokens":120,"completion_tokens":40,"total_tokens":160}})
    monkeypatch.setattr(httpx, 'Client', lambda **kw: original_client(transport=httpx.MockTransport(response), **kw))
    url = start(client)
    assert client.get(url+'/status').json()['state'] == 'understanding'
    assert len(sent) == 1
    with test_environment['TestingSessionLocal']() as db:
        log = db.query(models.AIRequestLog).filter_by(feature='decision_preparing').one()
        call = db.query(models.AIProviderCall).filter_by(request_log_id=log.id).one()
        assert log.status == 'completed' and log.user_id is None
        assert call.status == 'reported' and call.input_tokens == 120 and call.output_tokens == 40
        assert call.estimated_microrub > 0 and call.charged_microrub > 0
