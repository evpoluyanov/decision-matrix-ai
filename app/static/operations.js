/* Local operation state. No analytics, user content storage or automatic paid retry. */
(() => {
    "use strict";
    const nativeFetch = window.fetch.bind(window);
    const operations = new Map();
    const projectMatch = location.pathname.match(/^\/projects\/(\d+)$/);
    const positionKey = "dmatrix-position:" + location.pathname;
    const config = {
        alternatives: ["ai-alternatives-button", "Генерируем альтернативы…"],
        criteria: ["ai-criteria-button", "Генерируем критерии…"],
        scores: ["ai-scores-button", "ИИ заполняет матрицу…"],
        "result-explanation": ["ai-result-button", "ИИ готовит объяснение результата…"],
        "decision-risks": ["ai-decision-risks-button", "ИИ анализирует риски решения…"]
    };
    const get = id => document.getElementById(id);
    const store = (key, value) => { try { sessionStorage.setItem(key, JSON.stringify(value)); } catch (_) {} };
    const load = key => { try { return JSON.parse(sessionStorage.getItem(key)); } catch (_) { return null; } };
    const drop = key => { try { sessionStorage.removeItem(key); } catch (_) {} };
    const uuid = () => crypto.randomUUID();
    let workPosition = null;
    let dialogOperation = null;
    let dialog = null;

    function snapshotPosition() {
        if (!projectMatch) return null;
        return {path: location.pathname, x: scrollX, y: scrollY, at: Date.now(),
            focus: document.activeElement?.id || null,
            horizontal: [...document.querySelectorAll(".table-responsive")].map((e,i) => [e.id || String(i), e.scrollLeft]),
            tab: document.querySelector('[role="tab"][aria-selected="true"]')?.id || null};
    }
    function remember() { workPosition = snapshotPosition(); }
    function preserve() { if (workPosition) store(positionKey, workPosition); }
    window.dmatrixReload = () => { preserve(); location.reload(); };
    function restore() {
        const saved = load(positionKey);
        drop(positionKey);
        if (performance.getEntriesByType("navigation")[0]?.type === "back_forward") return;
        if (!saved || saved.path !== location.pathname || Date.now()-saved.at > 600000) return;
        requestAnimationFrame(() => requestAnimationFrame(() => {
            if (saved.tab && get(saved.tab) && window.bootstrap?.Tab) bootstrap.Tab.getOrCreateInstance(get(saved.tab)).show();
            document.querySelectorAll(".table-responsive").forEach((e,i) => {
                const value = saved.horizontal.find(([id]) => id === (e.id || String(i)));
                if (value) e.scrollLeft = value[1];
            });
            get(saved.focus)?.focus({preventScroll:true});
            window.scrollTo(saved.x, saved.y);
        }));
    }
    function spinner() {
        const span = document.createElement("span");
        span.className = "operation-spinner";
        span.setAttribute("aria-hidden", "true");
        return span;
    }
    function setButton(button, busy, label) {
        if (!button) return;
        if (busy) {
            if (!button.dataset.idleHtml) button.dataset.idleHtml = button.innerHTML;
            button.replaceChildren(spinner(), document.createTextNode(label));
        } else if (button.dataset.idleHtml) {
            button.innerHTML = button.dataset.idleHtml;
        }
        button.disabled = busy;
        button.setAttribute("aria-busy", String(busy));
    }
    async function boundedFetch(url, options = {}) {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), 60000);
        try {
            const response = await nativeFetch(url, {...options, signal:controller.signal});
            // Keep the deadline while receiving the body, not just the headers.
            await response.clone().text();
            return response;
        } finally { clearTimeout(timer); }
    }
    const asResponse = (data, status = 503) => new Response(JSON.stringify(data), {status, headers:{"Content-Type":"application/json"}});
    function makeOperation(path, feature) {
        let op = operations.get(path);
        if (op) return op;
        const notice = document.createElement("div");
        notice.className = "operation-notice";
        notice.setAttribute("role", "status");
        notice.setAttribute("aria-live", "polite");
        get(config[feature][0])?.closest(".card")?.prepend(notice);
        op = {path, feature, notice, state:"idle", key:load("dmatrix-operation:" + path)?.key || null};
        operations.set(path, op);
        return op;
    }
    function showDialog(op) {
        if (!dialog) return;
        dialogOperation = op;
        get("analysis-wait-title").textContent = op.feature === "decision-risks" ? "Анализ рисков" : "Объяснение результата";
        updateDialog(op);
        if (!dialog.open) dialog.showModal();
    }
    function updateDialog(op) {
        if (dialogOperation !== op) return;
        const body = get("analysis-wait-message");
        body.replaceChildren();
        if (op.state === "running") body.append(spinner());
        body.append(document.createTextNode(op.message || config[op.feature][1]));
        get("analysis-check").hidden = !["uncertain", "in_progress"].includes(op.state);
    }
    function setState(op, state, message) {
        op.state = state; op.message = message;
        op.notice.dataset.state = state;
        op.notice.replaceChildren();
        if (state === "running") op.notice.append(spinner());
        const text = document.createElement("span"); text.textContent = message; op.notice.append(text);
        if (["result-explanation", "decision-risks"].includes(op.feature)) {
            const reopen = document.createElement("button");
            reopen.type="button"; reopen.className="btn btn-outline-primary btn-sm";
            reopen.textContent="Показать состояние";
            reopen.addEventListener("click", () => showDialog(op)); op.notice.append(reopen);
        }
        if (["uncertain", "in_progress"].includes(state)) {
            const check = document.createElement("button"); check.type="button";
            check.className="btn btn-outline-secondary btn-sm"; check.textContent="Проверить состояние";
            check.addEventListener("click", () => checkOnly(op)); op.notice.append(check);
        }
        updateDialog(op);
    }
    function forget(op) { op.key=null; drop("dmatrix-operation:" + op.path); }
    async function statusOf(op) {
        const base = op.path.slice(0,op.path.lastIndexOf("/ai/"));
        const url = op.feature === "scores" ? base+"/ai/scores/state" : base+"/ai/operations/"+op.key;
        const response = await boundedFetch(url);
        return response.json();
    }
    async function checkOnly(op) {
        try {
            const state = await statusOf(op);
            if (op.feature === "scores" && state.job_status === "ready") {
                op.unknownScore = false;
                forget(op);
                setState(op,"failed","Предыдущая часть завершена. Можно продолжить заполнение матрицы; новый запрос пока не отправлен.");
                return;
            }
            if (["completed", "failed"].includes(state.status)) {
                forget(op);
                setState(op, state.status, state.message + (state.status === "completed" ? " Сохранённые результаты доступны в проекте и отчёте." : " Можно запустить новую операцию."));
                if (state.result) renderAnalysis(op.feature, state.result);
            } else {
                setState(op, "uncertain", state.message || "Результат пока не подтверждён. Новый запрос не отправлен.");
            }
        } catch (_) { setState(op, "uncertain", "Пока нет связи для проверки. Новый запрос не отправлен."); }
    }

    window.fetch = async (input, options = {}) => {
        const url = new URL(typeof input === "string" ? input : input.url, location.href);
        const match = url.pathname.match(/^\/projects\/\d+\/ai\/(alternatives|criteria|scores|result-explanation|decision-risks)$/);
        if (url.origin !== location.origin || !match || (options.method || "GET").toUpperCase() !== "POST") return nativeFetch(input, options);
        const feature = match[1], op = makeOperation(url.pathname, feature);
        if (op.inFlight) return asResponse({status:"in_progress", message:"Операция уже выполняется."}, 409);
        op.inFlight = true;
        if (!workPosition) remember();
        const button = get(config[feature][0]);
        let keepBusy = false;
        setButton(button, true, config[feature][1]);
        setState(op, "running", config[feature][1]);
        if (["result-explanation", "decision-risks"].includes(feature)) showDialog(op);
        try {
            if (op.key) {
                const state = await statusOf(op);
                if (state.status === "completed" || state.status === "failed") {
                    forget(op);
                    if (state.result) { setState(op,"completed","Результат получен."); return asResponse(state.result,200); }
                    setState(op,state.status,"Предыдущий запрос завершён. Новый запрос не отправлен. Для новой генерации нажмите кнопку ещё раз.");
                    return asResponse({status:"error",message:op.message},409);
                }
                if (feature !== "scores" || state.job_status !== "ready") {
                    setState(op,"uncertain",state.message || "Результат предыдущего запроса ещё не подтверждён. Новый запрос не отправлен.");
                    return asResponse({status:"error", message:op.message},409);
                }
                // Scores can advance only a confirmed ready batch; no unknown-result retry.
            }
            if (feature === "scores" && op.unknownScore) {
                const state = await statusOf(op);
                if (state.job_status !== "ready") {
                    setState(op,"uncertain",state.message || "Предыдущая часть ещё обрабатывается. Новый вызов не отправлен.");
                    return asResponse({status:"error",message:op.message},409);
                }
                op.unknownScore = false;
            }
            if (feature !== "scores") {
                op.key = uuid(); store("dmatrix-operation:" + op.path,{key:op.key});
            }
            const headers = new Headers(options.headers);
            if (op.key) headers.set("X-Operation-Key",op.key);
            const response = await boundedFetch(input,{...options,headers});
            const data = await response.clone().json();
            if (response.status === 409 && data.request_key) {
                op.key=data.request_key; store("dmatrix-operation:"+op.path,{key:op.key});
            }
            if (response.ok && data.status === "in_progress") {
                keepBusy = feature === "scores";
                setState(op,"running",data.message);
                return response;
            }
            if (!response.ok && response.status >= 500 || data.status === "in_progress" || data.status === "uncertain") {
                if (feature === "scores") op.unknownScore = true;
                const state = await statusOf(op);
                if (feature === "scores" && state.job_status === "ready") {
                    op.unknownScore = false;
                    setState(op,"failed",data.message || "Часть завершилась ошибкой. Можно продолжить после проверки.");
                    return response;
                }
                if (["in_progress","uncertain"].includes(state.status)) {
                    setState(op,"uncertain",state.message);
                    return asResponse({status:"error",message:state.message,error_code:data.error_code},response.status >= 400 ? response.status : 503);
                }
            }
            forget(op);
            const success = response.ok && data.status === "ok";
            setState(op,success?"completed":"failed",success?"Операция завершена.":(data.message||"Операция завершилась ошибкой."));
            if (success && dialogOperation === op && dialog?.open) dialog.close();
            return response;
        } catch (_) {
            if (feature === "scores") op.unknownScore = true;
            setState(op,"uncertain","Связь прервалась. Сначала проверьте состояние; повторный запрос автоматически не отправляется.");
            return asResponse({status:"error",message:op.message});
        } finally { op.inFlight=false; setButton(button,keepBusy,config[feature][1]); }
    };

    function renderList(blockId,listId,values) {
        const list=get(listId), block=get(blockId);
        if (!list || !block) return;
        list.replaceChildren();
        (values||[]).forEach(value=>{const li=document.createElement("li");li.textContent=value;list.append(li);});
        block.classList.toggle("d-none",!(values||[]).length);
    }
    function renderAnalysis(feature, data) {
        if (feature === "result-explanation") {
            if (!get("ai-result-summary")) return;
            get("ai-result-summary").textContent=data.summary||"";
            for (const part of ["factors","strengths","weaknesses"]) renderList("ai-result-"+part+"-block","ai-result-"+part,data[part]);
            get("ai-result-competitor").textContent=data.competitor||"";
            get("ai-result-competitor-block").classList.toggle("d-none",!data.competitor);
            get("ai-result-caveat").textContent=data.caveat||"";
            get("ai-result-caveat").classList.toggle("d-none",!data.caveat);
            get("ai-result-preliminary").classList.toggle("d-none",!data.preliminary);
            get("ai-result-explanation").classList.remove("d-none");
        } else {
            const list=get("ai-decision-risks-list"); if(!list)return;
            list.replaceChildren();
            (data.items||[]).forEach(item=>{
                const card=document.createElement("div");card.className="border rounded p-3";
                const title=document.createElement("h3"); title.className="h6"; title.textContent=item.title;
                const type=document.createElement("small");type.className="text-secondary";type.textContent=item.type==="matrix"?"Следует из матрицы":"Гипотеза ИИ";
                const risk=document.createElement("p");risk.textContent=item.risk;
                const check=document.createElement("p");check.className="small mb-0";check.textContent="Что проверить: "+item.check;
                card.append(title,type,risk,check);list.append(card);
            });
            get("ai-decision-risks-intro").classList.add("d-none");
            get("ai-decision-risks-preliminary").classList.toggle("d-none",!data.preliminary);
            get("ai-decision-risks-result").classList.remove("d-none");
        }
    }
    function setupAnalysis() {
        if (!projectMatch) return;
        dialog=document.createElement("dialog");dialog.className="analysis-dialog";
        dialog.setAttribute("aria-labelledby","analysis-wait-title");
        dialog.innerHTML='<header><h2 id="analysis-wait-title"></h2><button type="button" class="btn btn-outline-secondary" id="analysis-hide" aria-label="Скрыть окно ожидания">Закрыть</button></header><div class="operation-message" id="analysis-wait-message" role="status" aria-live="polite"></div><p class="small text-secondary">Закрытие только скрывает окно и не отменяет обращение к модели. Состояние останется на странице.</p><button type="button" class="btn btn-outline-primary" id="analysis-check" hidden>Проверить состояние</button>';
        document.body.append(dialog);
        get("analysis-hide").addEventListener("click",()=>dialog.close());
        get("analysis-check").addEventListener("click",()=>dialogOperation&&checkOnly(dialogOperation));
        for (const feature of ["result-explanation","decision-risks"]) {
            const button=get(config[feature][0]); if(!button)continue;
            button.addEventListener("click",async()=>{
                remember();
                const response=await window.fetch(location.pathname+"/ai/"+feature,{method:"POST"});
                const data=await response.json();
                if(response.ok&&data.status==="ok")renderAnalysis(feature,data);
            });
        }
        try {
            const saved=JSON.parse(get("saved-ai-analysis")?.textContent||"{}");
            if(saved.result)renderAnalysis("result-explanation",saved.result);
            if(saved.decision_risks?.length)renderAnalysis("decision-risks",{items:saved.decision_risks,preliminary:saved.decision_risks_preliminary});
        } catch (_) {}
    }
    function setupMatrix() {
        const form=get("matrix-form");if(!form)return;
        let busy=false, unknown=null, changedAfterUnknown=false;
        const notice=get("matrix-save-status"), button=form.querySelector('button[type="submit"]');
        const fields=[...form.querySelectorAll("input.score-input")];
        function reviewLink() {
            const link=document.createElement("a");link.href=location.pathname+"#matrix";
            link.target="_blank";link.rel="noopener";link.textContent=" Открыть актуальную матрицу в новой вкладке";
            notice.append(link);
        }
        form.addEventListener("submit",async event=>{
            event.preventDefault();if(busy)return;
            if(!form.reportValidity())return;
            busy=true;remember();setButton(button,true,"Сохраняем матрицу…");
            fields.forEach(e=>e.readOnly=true);notice.replaceChildren(spinner(),document.createTextNode("Сохраняем матрицу… Это сохранение данных, не запрос к ИИ."));
            try {
                if(unknown) {
                    const state=await (await boundedFetch(form.action+"/state?request_key="+encodeURIComponent(unknown))).json();
                    if(changedAfterUnknown){
                        notice.textContent=(state.status==="saved"?"Предыдущее сохранение подтверждено. ":"Предыдущее сохранение пока не подтверждено. ")+"После него вы изменили ввод. Он остаётся здесь: сверьте его с серверной версией перед переносом изменений.";
                        reviewLink();return;
                    }
                    if(state.status==="saved"){unknown=null;window.dmatrixReload();return;}
                    if(state.matrix_revision !== Number(form.elements.matrix_revision.value)) {
                        notice.textContent="На сервере уже другая версия. Ввод остался на экране. Откройте актуальную матрицу в новой вкладке и сверьте изменения.";
                        reviewLink();
                        return;
                    }
                    // Same operation key and original values: safely replay an unconfirmed save.
                }
                const key=unknown||uuid();form.elements.request_key.value=key;
                const response=await boundedFetch(form.action,{method:"POST",body:new FormData(form),headers:{"X-Requested-With":"fetch"}});
                const data=await response.json();
                if(!response.ok){
                    notice.textContent=data.message;
                    if(response.status===409)reviewLink();
                    if(response.status>=500)unknown=key;
                    if(data.field&&form.elements.namedItem(data.field))form.elements.namedItem(data.field).focus();
                    else notice.focus({preventScroll:true});
                    return;
                }
                unknown=null;notice.textContent="Матрица сохранена полностью.";
                window.dmatrixReload();
            } catch (_) {
                unknown=form.elements.request_key.value||unknown;
                notice.textContent="Связь прервалась. Ввод остался на экране. Кнопка проверит состояние перед повторным сохранением.";
            } finally {
                busy=false;fields.forEach(e=>e.readOnly=false);setButton(button,false);
                if(unknown)button.textContent="Проверить сохранение";
            }
        });
        fields.forEach(e=>e.addEventListener("input",()=>{
            // Do not reuse an ambiguous operation ID for changed input.
            if(unknown){changedAfterUnknown=true;notice.textContent="Есть неподтверждённое сохранение. Сверьте текущую серверную версию перед отправкой изменённого ввода.";reviewLink();}
        }));
    }
    document.addEventListener("DOMContentLoaded",()=>{
        setupAnalysis();setupMatrix();restore();
        for(const [feature,[id]] of Object.entries(config)){
            const button=get(id);if(!button)continue;
            button.addEventListener("click",event=>{
                const op=operations.get(location.pathname+"/ai/"+feature);
                if(op?.inFlight){event.preventDefault();event.stopImmediatePropagation();return;}
                if(op&&["uncertain","in_progress"].includes(op.state)){
                    event.preventDefault();event.stopImmediatePropagation();checkOnly(op);
                    if(["result-explanation","decision-risks"].includes(feature))showDialog(op);
                }else remember();
            },true);
            const pending=load("dmatrix-operation:"+location.pathname+"/ai/"+feature);
            if(pending?.key){const op=makeOperation(location.pathname+"/ai/"+feature,feature);setState(op,"uncertain","Сохранился незавершённый запрос. Проверьте его состояние.");}
        }
        document.querySelectorAll('form[method="post"]').forEach(form=>{
            if(form.id==="matrix-form")return;
            form.addEventListener("submit",event=>{
                if(event.defaultPrevented)return;
                if(form.dataset.submitting){event.preventDefault();return;}
                form.dataset.submitting="1";remember();preserve();
                const button=event.submitter||form.querySelector('button[type="submit"],button:not([type])');
                // Defer disabling until the browser has included submitter fields.
                setTimeout(()=>setButton(button,true,"Сохраняем…"),0);
            });
        });
        get("report-link")?.addEventListener("click",event=>{
            if(event.ctrlKey||event.metaKey||event.shiftKey)return;
            const link=get("report-link");link.setAttribute("aria-busy","true");link.replaceChildren(spinner(),document.createTextNode("Формируем отчёт…"));
        });
        window.addEventListener("pageshow",event=>{
            if(event.persisted){document.querySelectorAll('[data-submitting]').forEach(f=>delete f.dataset.submitting);document.querySelectorAll('[data-idle-html]').forEach(b=>setButton(b,false));}
            const report=get("report-link");if(report){report.removeAttribute("aria-busy");report.textContent="Отчёт";}
        });
    });
})();
