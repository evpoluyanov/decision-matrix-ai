(() => {
 'use strict';
 const start = document.getElementById('decision-start');
 const workspace = document.getElementById('decision-workspace');
 const message = document.getElementById('decision-message');
 const bid = workspace?.dataset.brief;
 const seen = new Set();
 function track(name) {
   if (!window.decisionAnalytics || seen.has(name)) return;
   seen.add(name);
   fetch('/decisions/events',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({event:name,brief:bid})}).catch(()=>{});
   if(window.dmatrixReachGoal)window.dmatrixReachGoal(name);
 }
 async function request(url, options={}) {
   const response = await fetch(url, options);
   const data = await response.json();
   if(!response.ok){const error=new Error(typeof data.detail==='string'?data.detail:'Не удалось выполнить действие. Введённые данные сохранены.');error.status=response.status;throw error;}
   return data;
 }
 function node(tag, text, classes='') { const el=document.createElement(tag); if(text!==undefined)el.textContent=text; if(classes)el.className=classes; return el; }
 if(start) {
   track('landing_viewed');
   start.addEventListener('input',()=>track('input_started'),{once:true});
   const examples={
     software:['Какую программу выбрать для учёта клиентов?','Нужна простая настройка, бюджет до 3 000 ₽ в месяц.'],
     equipment:['Какой ноутбук выбрать для работы?','Работаю с документами и видеозвонками. Важно удобно брать его с собой.'],
     career:['Что выбрать: онлайн-курс или занятия с преподавателем?','Хочу освоить разговорный английский. Могу заниматься два вечера в неделю.'],
     contractor:['Какого подрядчика выбрать для разработки сайта?','Обязательно запустить сайт до конца месяца. Важно понятное сопровождение после запуска.']};
   let dirty=false;start.addEventListener('input',()=>dirty=true);
   start.querySelectorAll('[data-example]').forEach(button=>button.addEventListener('click',()=>{
     if(dirty&&!confirm('Заменить введённый текст выбранным примером?'))return;
     const [q,d]=examples[button.dataset.example]; start.elements.decision_question.value=q; start.elements.decision_details.value=d; dirty=true;track('input_started');track('example_selected');
   }));
   start.addEventListener('submit',async e=>{
     e.preventDefault();const button=start.querySelector('[type=submit]');if(button.disabled)return;
     button.disabled=true;button.textContent='Разбираемся в задаче…';message.textContent='';
     try {const data=await request('/start',{method:'POST',body:new FormData(start)});location.assign(data.url);}
     catch(error){
       if(!error.status){
         message.textContent='Проверяем, успел ли сохраниться разбор…';
         try{const active=await request('/decisions/active');
           if(active.url&&active.question===start.elements.decision_question.value.trim()&&active.details===start.elements.decision_details.value.trim()&&active.allow_suggestions===start.elements.allow_suggestions.checked){location.assign(active.url);return;}
         }catch(checkError){message.textContent='Не удалось проверить состояние. Введённый текст сохранён в форме. Обновите связь перед новой попыткой.';return;}
       }
       message.textContent=error.message;button.disabled=false;button.textContent='Разобраться с выбором';
     }
   });
 }
 if(!workspace)return;
 let current=null, busy=false, editing=false, pollTimer=null;
 const form=document.getElementById('comparison-form'), understanding=document.getElementById('understanding'), result=document.getElementById('decision-result'), loading=document.getElementById('decision-loading');
 function optionRow(value='') {
   const row=node('div',undefined,'decision-row');const input=node('input');input.className='form-control';input.value=value;input.placeholder='Например: онлайн-курс';input.required=true;input.setAttribute('aria-label','Вариант');
   const remove=node('button','×','remove-row');remove.type='button';remove.setAttribute('aria-label','Удалить вариант');remove.addEventListener('click',()=>row.remove());row.append(input,remove);document.getElementById('options-list').append(row);
 }
 function conditionRow(c={name:'',required:false}) {
   const row=node('div',undefined,'decision-row');const input=node('input');input.className='form-control';input.value=c.name;input.required=true;input.placeholder='Например: без поездок';input.setAttribute('aria-label','Условие');
   const select=node('select');select.className='form-select condition-kind';select.setAttribute('aria-label','Обязательность условия');
   [['no','Предпочтение'],['yes','Обязательно']].forEach(([v,t])=>{const o=node('option',t);o.value=v;select.append(o);});select.value=c.required?'yes':'no';
   const remove=node('button','×','remove-row');remove.type='button';remove.setAttribute('aria-label','Удалить условие');remove.addEventListener('click',()=>row.remove());row.append(input,select,remove);document.getElementById('conditions-list').append(row);
 }
 function renderUnderstanding(data) {
   document.getElementById('options-list').replaceChildren();document.getElementById('conditions-list').replaceChildren();document.getElementById('questions-list').replaceChildren();
   data.options.forEach(optionRow);data.conditions.forEach(conditionRow);
   document.getElementById('edit-question').value=current.question;document.getElementById('edit-details').value=current.details;document.getElementById('edit-suggestions').checked=current.allow_suggestions;
   for(const [id,items,add] of [['additional-options',data.additional_options||[],optionRow],['additional-conditions',data.additional_conditions||[],conditionRow]]) {
     const area=document.getElementById(id);area.replaceChildren();
     if(items.length&&current.allow_suggestions){const details=node('details');details.append(node('summary','Дополнительные предложения ИИ'));
       items.forEach(item=>{const b=node('button','+ '+(typeof item==='string'?item:item.name),'btn btn-link btn-sm');b.type='button';b.addEventListener('click',()=>{add(item);b.remove();});details.append(b);});area.append(details);}
   }
   (data.questions||[]).forEach((q,i)=>{const label=node('label',q,'d-block');label.htmlFor='answer-'+i;const input=node('input');input.id=label.htmlFor;input.className='form-control mb-3';input.placeholder='Например: пока не знаю';input.value=data.answers?.[i]||'';document.getElementById('questions-list').append(label,input);});
 }
 const statuses={yes:'Соответствует',no:'Не соответствует',unknown:'Нет данных'};
 const origins={user:'По вашим сведениям',model:'Предположение ИИ',unknown:'Нужно уточнить'};
 function renderResult(data) {
   document.getElementById('result-summary').textContent=data.summary;
   const observations=document.getElementById('result-observations');observations.replaceChildren();
   if(data.observations.length){observations.append(node('h2','Различия и компромиссы','h4'));const list=node('ul');data.observations.forEach(t=>list.append(node('li',t)));observations.append(list);}
   const rows=document.getElementById('result-rows');rows.replaceChildren();
   const table=node('table',undefined,'table table-sm');const head=node('tr');['Вариант','Условие','Статус','Основание'].forEach(t=>head.append(node('th',t)));table.append(head);
   data.rows.forEach(row=>{const card=node('article',undefined,'comparison-card');card.append(node('h3',row.option),node('p',{eligible:'Соответствует обязательным условиям',conditional:'Обязательные условия требуют уточнения',excluded:'Не подходит под обязательные условия'}[row.status],'small'));
     const ul=node('ul'); row.cells.slice(0,3).forEach(c=>ul.append(node('li',c.condition+': '+c.detail+' ('+origins[c.basis]+')')));card.append(ul);rows.append(card);
     row.cells.forEach(c=>{const tr=node('tr');[row.option,c.condition,statuses[c.status],c.detail+' · '+origins[c.basis]].forEach(t=>tr.append(node('td',t)));table.append(tr);});
   });document.getElementById('result-table').replaceChildren(table);
   const missing=document.getElementById('result-missing');missing.replaceChildren();if(data.missing.length){missing.append(node('h2','Что стоит уточнить','h4'));const ul=node('ul');data.missing.forEach(t=>ul.append(node('li',t)));missing.append(ul);}
   document.getElementById('save-result').textContent=current.saved?'Сохранено в аккаунте':'Сохранить результат';
 }
 function setBusy(value,label='Готовим сравнение…') {busy=value;loading.hidden=!value;document.getElementById('loading-label').textContent=label;form.querySelectorAll('button,input,textarea,select').forEach(e=>e.disabled=value);}
 function schedule(){clearTimeout(pollTimer);pollTimer=setTimeout(load,2000);}
 async function load(){
   try{
     const state=await request('/decisions/'+bid+'/status');const changed=!current||current.revision!==state.revision||current.state!==state.state;current=state;
     const pending=['preparing','comparing'].includes(state.state);setBusy(pending,state.state==='preparing'?'Разбираемся в задаче…':'Готовим сравнение…');
     if(pending){schedule();return;}
     document.getElementById('retry-area').hidden=true;
     if(state.state==='unknown'){message.textContent='Не удалось подтвердить завершение предыдущей операции. Новый запрос не отправлен. Разбор сохранён. Попробуйте проверить состояние позже.';document.getElementById('workspace-title').textContent='Разбор сохранён';return;}
     if(state.result&&!editing){if(changed)renderResult(state.result);result.hidden=false;understanding.hidden=true;document.getElementById('workspace-title').textContent='Что подходит под ваши условия';track('result_viewed');}
     else if(state.understanding){if(changed)renderUnderstanding(state.understanding);understanding.hidden=false;result.hidden=true;document.getElementById('workspace-title').textContent='Правильно ли мы вас поняли?';track('understanding_viewed');}
     if(state.state==='error'){message.textContent='Не удалось завершить разбор. Данные и предыдущий результат сохранены. Можно повторить после проверки введённых условий.';if(!state.understanding){document.getElementById('retry-area').hidden=false;document.getElementById('workspace-title').textContent='Не удалось разобрать задачу';}}
     else message.textContent='';
   }catch(e){setBusy(true,'Проверяем состояние…');message.textContent='Связь прервалась. Проверяем состояние; повторный ИИ-запрос не отправлен.';schedule();}
 }
 document.getElementById('add-option').addEventListener('click',()=>optionRow());document.getElementById('add-condition').addEventListener('click',()=>conditionRow());
 document.getElementById('edit-result').addEventListener('click',()=>{editing=true;renderUnderstanding(current.understanding);understanding.hidden=false;result.hidden=true;document.getElementById('workspace-title').textContent='Уточните условия';track('conditions_changed');document.getElementById('edit-question').focus({preventScroll:true});});
 document.getElementById('comparison-details').addEventListener('toggle',e=>{if(e.target.open)track('details_opened');});
 function payload(){return {
   question:document.getElementById('edit-question').value,details:document.getElementById('edit-details').value,
   allow_suggestions:document.getElementById('edit-suggestions').checked,revision:current.revision,
   options:[...document.querySelectorAll('#options-list input')].map(e=>e.value),
   conditions:[...document.querySelectorAll('#conditions-list .decision-row')].map(e=>({name:e.querySelector('input').value,required:e.querySelector('select').value==='yes'})),
   questions:current.understanding?.questions||[],answers:[...document.querySelectorAll('#questions-list input')].map(e=>e.value),additional_options:[],additional_conditions:[]};}
 form.addEventListener('submit',async e=>{e.preventDefault();if(busy)return;const data=payload();setBusy(true);message.textContent='';
   try{await request('/decisions/'+bid+'/compare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});editing=false;await load();}catch(e){message.textContent=e.message;if(e.status){setBusy(false);}else{setBusy(true,'Проверяем состояние…');schedule();}}});
 async function prepare(){if(busy)return;const data=current?.understanding?payload():{};setBusy(true,'Разбираемся в задаче…');
   try{await request('/decisions/'+bid+'/prepare',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});editing=true;await load();}catch(e){message.textContent=e.message;if(e.status){setBusy(false);}else{setBusy(true,'Проверяем состояние…');schedule();}}}
 document.getElementById('retry-prepare').addEventListener('click',prepare);document.getElementById('reprepare').addEventListener('click',prepare);
 load();
})();
