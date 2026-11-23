'use strict';
// Demonstration per-100-g food estimates. Real labelled products can be added from Open Food Facts.
// Published food-composition references for use ONLY when the live lookup is
// unavailable or yields a different product. No portion weights live here;
// the neural network determines grams. All values below are per 100 g.
// The generic cod-liver entry is an approximate canned-product analogue
// (JUOR, 525 kcal, P6, F55.46, carbs <0.5). The exact brand is unknown.
const VERIFIED_LOCAL_NUTRIENTS=[
 {name:'печень трески сырая',k:553,p:5.5,f:59,c:0,portion:null,
  aliases:['печень трески сырая','сырая печень трески','печени трески сырой'],
  source:'Matvaretabellen (Норвегия) · печень трески сырая',reference_url:'https://matvaretabellen.mattilsynet.io/en/cod-liver-raw/',approximate:true},
 {name:'печень трески',k:525,p:6,f:55.46,c:0,portion:null,
  aliases:['печень трески','печени трески','тресковая печень','тресковой печени','печень трески консервированная'],
  source:'Опубликованная этикетка JUOR · аналог консервированной печени трески',reference_url:'https://en.juor.pl/the-offering/cod-liver-in-natural-fat-2/',approximate:true}
];
const FOOD=[
['соус сырный',280,4,25,9,15,['соус сырный','сырный соус']],
['гречка вареная',110,3.6,1.1,20,180,['гречк','гречнев']],
['булочка для бургера',280,9,5,49,70,['булочк','булка с кунжутом']],
['говяжья котлета',250,26,15,0,105,['котлет','патти']],
['салат айсберг',14,0.9,0.1,3,15,['айсберг','листья салата','лист салата']],
['салат латук',15,1.4,0.2,2.9,15,['салат латук','латук','листья латука','листьев латука','лист латука']],
['маринованный огурец',16,0.5,0.2,2.8,25,['маринованн огур','маринованные огур','пикл']],
['красный лук',40,1.1,0.1,9.3,20,['красный лук','лук красный','луковые кольца','лук']],

// Approximate comparable Napoleon pastry from Norwegian food composition table (per 100 g).
['торт наполеон',297,5.3,14.4,35.9,120,['наполеон']],
// Illustrative honey cake recipe: 338.2 kcal, P 6.4, F 11.7, C 51.7 per 100g. Actual recipes vary.
['торт медовик',338.2,6.4,11.7,51.7,110,['медовик','медовыи торт','медовый торт','торт медовый']],
// Conservative editable fallbacks only when all external food databases fail.
// Example recipe estimate (not an official USDA record): ~390 kcal/100g, P5 F20 C48.
['торт с кремом',390,5,20,48,110,['торт с кремом','торт со взбитыми сливками','бисквитный торт с кремом','бисквитный торт со сливками']],
// USDA SR Legacy FDC 172706 sponge cake (without frosting), per 100g.
['бисквит',290,5.4,2.7,61,100,['бисквит','бисквитный корж']],
['взбитые сливки',257,3,25,8,25,['взбитые сливки','взбитых сливок']],
['шоколадный соус',320,2,9,58,15,['шоколадный соус']],
['рис вареный',130,2.5,0.3,28.2,180,['рис']],
['куриная грудка',165,31,3.6,0,150,['куриц','курин','грудк']],
['яйцо',143,12.6,9.5,0.7,55,['яйц','яйца','яиц','яйцо']],
// USDA SR Legacy FDC 173423: egg, whole, cooked, fried (per 100 g, incl. typical cooking fat).
['яйцо жареное',196,13.61,14.84,0.83,55,['яичница','глазунья','жареные яйца','жареное яйцо','яйцо жареное']],
['яблоко',52,0.3,0.2,14,160,['яблок']],
['банан',89,1.1,0.3,23,120,['банан']],
['овсянка вареная',71,2.5,1.5,12,200,['овсян']],
['картофель вареный',87,1.9,0.1,20.1,180,['картош','картоф']],
['огурец',15,0.7,0.1,3.6,120,['огур']],
['помидор',18,0.9,0.2,3.9,120,['помид','томат']],
['хлеб',250,8,3,49,35,['хлеб','батон','тост']],
['сыр',350,25,27,2,30,['сыр']],
['молоко',60,3.2,3.2,4.8,200,['молок']],
['кефир',53,3,2.5,4,200,['кефир']],
['творог',121,17,5,1.8,180,['творог']],
['йогурт натуральный',65,4,3,5,150,['йогурт']],
['орехи',607,20,54,16,30,['орех']],
['сливочное масло',748,0.5,82.5,0.8,10,['сливочн','масло слив']],
['растительное масло',900,0,100,0,10,['масл','оливков']],
['сахар',400,0,0,100,5,['сахар']],
['говядина приготовленная',250,26,15,0,150,['говядин']],
['свинина приготовленная',290,25,21,0,150,['свинин']],
['рыба приготовленная',130,23,4,0,150,['рыб','треск','хек']],
['греческий салат',120,3.8,9.4,4.5,180,['греческ салат']],
['овощной салат без заправки',25,1,0.3,4.5,150,['салат']],
['макароны вареные',157,5.8,0.9,30.9,180,['макарон','паст']],
['апельсин',47,0.9,0.1,11.8,150,['апельсин']],
['картофель фри',312,3.4,15,41,100,['фри']],
['куриные наггетсы',295,15,20,13,120,['наггет']],
['кофе черный',2,0.1,0,0,200,['кофе']],
['пицца',260,11,10,34,180,['пицц']],
['бургер',260,14,12,26,180,['бургер','гамбургер']],
['сырники',230,13,12,20,150,['сырник']],
['суп',70,3,4,5,250,['суп']],
['пельмени',270,11,13,27,180,['пельмен']],
['суши',145,6,3,23,150,['суши','ролл']],
['стейк',250,26,16,0,180,['стейк']],
['лосось',208,20,13,0,150,['лосос','семга']],
['цезарь салат',180,11,12,6,180,['цезарь']],
['паста карбонара',260,12,13,24,180,['карбонар']],
['чай без сахара',1,0,0,0,200,['чай']]
].map(([name,k,p,f,c,portion,aliases])=>({name,k,p,f,c,portion,aliases}));
FOOD.unshift(...VERIFIED_LOCAL_NUTRIENTS); // These are nutritional data, never serving-size defaults.

const $=id=>document.getElementById(id);
const clean=s=>String(s||'').toLowerCase().replaceAll('ё','е').replace(/[.!?]/g,'').trim();
const num=n=>Math.round(Number(n)||0);
const newId=()=>typeof crypto!=='undefined'&&typeof crypto.randomUUID==='function'?crypto.randomUUID():String(Date.now())+'-'+Math.random().toString(36).slice(2);
const one=n=>(Math.round((Number(n)||0)*10)/10).toLocaleString('ru-RU');
const today=()=>{const d=new Date();return [d.getFullYear(),String(d.getMonth()+1).padStart(2,'0'),String(d.getDate()).padStart(2,'0')].join('-')};
let db, photoUrl=null, photoFile=null, dishes=[], favoritesCache=[], activePhotoRun=0, activeTextRun=0;
let pendingSource=null; // text/photo: keep original input until ALL recognised dishes are saved or cleared
let selectedDay=today(), calendarBase=new Date(), addDrafts=new Map();
const NORMS={k:2100,p:160,f:70,c:200};
const known=FOOD.flatMap(f=>f.aliases.map(a=>({a:clean(a),f}))).sort((a,b)=>b.a.length-a.a.length);
function findFood(t){let s=clean(t);return known.find(o=>s.includes(o.a))?.f||null}
// Convert everyday portion descriptions into APPROXIMATE weights, without asking an LLM
// to invent calories. UI always allows correcting these numbers manually.
// Portion sizes are estimates, not gram measurements inferred directly from pixels.
const MACRO_KEYS=['k','p','f','c'];
const CLOUD_AI_ENDPOINT='https://food-ai-inference.evpoluyanov.workers.dev/analyze';
const FOOD_SEARCH_API='https://food-ai-inference.evpoluyanov.workers.dev/nutrition-search';
const FOOD_BATCH_API='https://food-ai-inference.evpoluyanov.workers.dev/nutrition-batch';
const CHAIN_ORDER_API='https://food-ai-inference.evpoluyanov.workers.dev/order-analyze';
// All scoring, source matching and transport diagnostics stay in this removable dev panel.
const technicalEvents=[];
function devRecord(stage,details){
 const event={time:new Date().toISOString(),stage,details};technicalEvents.push(event);
 if(technicalEvents.length>35)technicalEvents.shift();
 const pre=document.getElementById('technicalDebugLog');if(pre)pre.textContent=JSON.stringify(technicalEvents,null,2);
}
const draftsByDish=new Map();
let searchTargetDish=null, remoteResultCache=new Map();
const numInput=v=>Math.round((Number(v)||0)*10)/10;
const toDisplay=v=>String(numInput(v));
const capital=s=>{s=String(s||'').trim();return s?s[0].toLocaleUpperCase('ru-RU')+s.slice(1):''};
const id=()=>typeof crypto!=='undefined'&&typeof crypto.randomUUID==='function'?crypto.randomUUID():Date.now()+'-'+Math.random().toString(36).slice(2);
const gramsOf=x=>Number(x?.grams)||0;
const emptyTotals=()=>({k:0,p:0,f:0,c:0,grams:0});
const sumItems=a=>(a||[]).reduce((out,x)=>{const scale=gramsOf(x)/100;for(const k of MACRO_KEYS)out[k]+=(Number(x[k])||0)*scale;out.grams+=gramsOf(x);return out},emptyTotals());
const totalsFor=d=>d.items?.length?sumItems(d.items):({...emptyTotals(),...(d.manual||{})});
const sumEntries=entries=>(entries||[]).reduce((out,entry)=>{const t=totalsFor(entry);for(const k of ['grams',...MACRO_KEYS])out[k]+=Number(t[k])||0;return out},emptyTotals());
const portionVal=(i,key)=>(Number(i.grams)||0)*(Number(i[key])||0)/100;
const setPortionVal=(i,key,v)=>{if(Number(i.grams)>0)i[key]=Number(v)*100/Number(i.grams)};
const cloneItems=a=>(a||[]).map(x=>({...x,id:id()}));
const dayKey=d=>`${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
const dateFromKey=k=>{const [y,m,d]=k.split('-').map(Number);return new Date(y,m-1,d)};
const dayText=k=>dateFromKey(k).toLocaleDateString('ru-RU',{weekday:'long',day:'numeric',month:'long'});
const el=(tag,cls,text)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=text;return x};
const button=(label,cls,run)=>{const x=el('button',cls,label);x.type='button';x.addEventListener('click',run);return x};
const macroLabels={k:'К',p:'Б',f:'Ж',c:'У'};
const macroNames={k:'Калории',p:'Белки',f:'Жиры',c:'Углеводы'};
function nutritionField(label,value,step,klass='',idTag=''){
 const wrap=el('label','editField '+klass);wrap.append(el('span','',label));
 const input=el('input');input.type='text';input.inputMode='decimal';input.autocomplete='off';input.setAttribute('enterkeyhint','done');input.dataset.numeric='true';input.dataset.max=label==='Вес, г'?'10000':'100000';input.value=value==null?'':toDisplay(value);if(idTag)input.id=idTag;wrap.append(input);return {wrap,input};
}
function newDish(name='Блюдо',items=[],unresolved=[],manual=null){return {id:id(),name:capital(name),items:cloneItems(items),manual:manual?{...emptyTotals(),...manual}:emptyTotals(),per100:null,unresolved:unresolved.map(x=>({...x,id:id()}))}}
function dishById(key){return dishes.find(d=>d.id===key)}
function itemKey(name){return clean(name).replace(/[^\p{L}\p{N}]+/gu,' ').trim()}
function fallbackDishName(items,label=''){
 if(label)return capital(label);
 if(items.length===1)return capital(items[0].name);
 const names=items.map(x=>clean(x.name));
 if(names.some(n=>/булоч|котлет|бургер/.test(n)))return 'Бургер';
 return items.length?'Блюдо':'Новое блюдо';
}
// Return an estimate *and* a warning when a photo implies an implausible mass.
function parseOffline(text){
 const chunks=String(text).replace(/(\d),(\d)/g,'$1.$2').split(/[,;\n]+|\s+и\s+/i).map(x=>x.trim()).filter(Boolean);
 const out=[];
 for(const chunk of chunks){const food=findFood(chunk);if(food){const grams=0; const item={name:capital(food.name),grams,k:food.k,p:food.p,f:food.f,c:food.c,weightReview:grams?'':'Нет оценки массы: нейросеть недоступна.'};out.push(newDish(capital(chunk.replace(/^\d+\s*/,'')||food.name),[item]))}
  else out.push(newDish(capital(chunk),[{name:capital(chunk),grams:0,k:null,p:null,f:null,c:null,source:'unknown'}]));}
 return out;
}
function openDB(){return new Promise((resolve,reject)=>{const req=indexedDB.open('my-food-diary-v1',2);req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains('entries'))db.createObjectStore('entries',{keyPath:'id'});if(!db.objectStoreNames.contains('favorites'))db.createObjectStore('favorites',{keyPath:'id'})};req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
function all(store){return new Promise((resolve,reject)=>{const q=db.transaction(store,'readonly').objectStore(store).getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)})}
function put(store,data){return new Promise((resolve,reject)=>{const tx=db.transaction(store,'readwrite');tx.objectStore(store).put(data);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)})}
function erase(store,key){return new Promise((resolve,reject)=>{const tx=db.transaction(store,'readwrite');tx.objectStore(store).delete(key);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)})}
function summaryLabel(items){return (items||[]).slice(0,3).map(x=>capital(x.name)).join(' + ')||'Блюдо'}
function favoriteKey(d){return JSON.stringify([itemKey(d.name||''),(d.items||[]).map(x=>[itemKey(x.name),Number(x.grams)||0,...MACRO_KEYS.map(k=>numInput(x[k]))]),d.items?.length?null:totalsFor(d)])}
function favoriteFor(d){return favoritesCache.find(f=>favoriteKey(f)===favoriteKey(d))}
async function toggleFavorite(d){
 if(!d.items.length && !(d.manual?.grams>0))return;
 const old=favoriteFor(d);
 try{if(old)await erase('favorites',old.id);else await put('favorites',{id:id(),name:d.name,items:cloneItems(d.items),manual:d.items.length?null:{...d.manual},created:new Date().toISOString()});await refresh();refreshFavoriteStars()}catch(e){setStatus('Ошибка избранного: '+e.message)}
}
function refreshFavoriteStars(){for(const d of dishes){const b=document.querySelector(`[data-dish-star="${d.id}"]`);if(!b)continue;const fav=!!favoriteFor(d);b.textContent=fav?'★':'☆';b.setAttribute('aria-pressed',String(fav));b.title=fav?'Убрать из избранного':'В избранное';b.setAttribute('aria-label',b.title);b.classList.toggle('favoriteActive',fav)}
 $('tabFaves').classList.toggle('favoriteActive',dishes.some(d=>!!favoriteFor(d)))}
function setStatus(txt=''){$('operationStatus').textContent=txt}
function hasMissingNutrition(i){return MACRO_KEYS.some(k=>i[k]===null || i[k]===undefined)}
function canSaveDish(d){return !!d.name.trim() && (d.items.length?d.items.every(i=>Number(i.grams)>0&&Number.isFinite(+i.grams)&&!hasMissingNutrition(i)):Number(d.manual?.grams)>0)}
function updateDishSummary(d){const elTotal=document.querySelector(`[data-dish-total="${d.id}"]`);if(!elTotal)return;const t=totalsFor(d);
 elTotal.textContent=`Итого · Вес: ${one(t.grams)} г · К: ${num(t.k)} · Б: ${one(t.p)} · Ж: ${one(t.f)} · У: ${one(t.c)}`;
 const summary=document.querySelector(`[data-dish-warning="${d.id}"]`);
 if(summary){const noWeight=d.items.some(i=>!(Number(i.grams)>0));const unknown=d.items.some(hasMissingNutrition);
  summary.textContent=noWeight?'Заполните вес каждого ингредиента.':unknown?'Часть КБЖУ не определена — итог может быть неполным. Проверьте красные поля.':'';
 }
 const btnSave=document.querySelector(`[data-dish-save="${d.id}"]`);if(btnSave)btnSave.disabled=!canSaveDish(d);
}
function removeUnknown(d,u){d.unresolved=d.unresolved.filter(x=>x.id!==u.id);renderDishes()}
function editFieldGroup(item,d){
 const block=el('div','ingredientRow');const headline=el('div','ingredientHeading');
 const name=el('input','ingredientNameInput');name.type='text';name.value=capital(item.name);name.setAttribute('aria-label','Название ингредиента');
 name.addEventListener('input',()=>{item.name=name.value;item.userEdited=true;refreshFavoriteStars()});
 const del=button('×','iconAction red',()=>{d.items=d.items.filter(x=>x.id!==item.id);if(!d.items.length)d.manual=emptyTotals();renderDishes()});del.setAttribute('aria-label','Удалить ингредиент');headline.append(name,del);block.append(headline);
 const fields=el('div','nutriEditRow'),weight=nutritionField('Вес, г',item.grams>0?item.grams:null,10,'weightEdit'),macroRow=el('div','macroFields');fields.append(weight.wrap);const m={};
 const refreshMissing=()=>{weight.input.classList.toggle('missingData',!(Number(item.grams)>0));
  for(const k of MACRO_KEYS)m[k].classList.toggle('missingData',item[k]===null||item[k]===undefined);
 };
 for(const k of MACRO_KEYS){const f=nutritionField(macroLabels[k],Number(item.grams)>0&&item[k]!=null?portionVal(item,k):null,5);f.input.setAttribute('aria-label',`${macroNames[k]} для ${item.name}`);
  f.input.addEventListener('input',()=>{
   const val=Number(f.input.value.replace(',','.'));if(!Number.isFinite(val)||val<0)return;
   if(Number(item.grams)>0){item.userEdited=true;setPortionVal(item,k,val);refreshMissing();updateDishSummary(d);refreshFavoriteStars()}
   else{f.input.value='';}
  });m[k]=f.input;macroRow.append(f.wrap)}
 weight.input.addEventListener('input',()=>{const val=weight.input.value;const w=val===''?0:Number(val);if(!Number.isFinite(w)||w<0||w>10000)return;
  item.userEdited=true;item.grams=w;item.weightReview='';block.querySelector('.portionEstimateWarning')?.remove();for(const k of MACRO_KEYS)m[k].value=w>0&&item[k]!=null?toDisplay(portionVal(item,k)):'';refreshMissing();updateDishSummary(d);refreshFavoriteStars()});
 fields.append(macroRow);block.append(fields);if(item.weightReview)block.append(el('small','portionEstimateWarning',item.weightReview));refreshMissing();
 return block;
}
function editWholeDish(d){
 const panel=el('div','wholeDishEditor'),line=el('div','nutriEditRow'),weight=nutritionField('Вес, г',d.manual.grams>0?d.manual.grams:null,10,'weightEdit'),group=el('div','macroFields'),fields={};
 line.append(weight.wrap);for(const k of MACRO_KEYS){const field=nutritionField(macroLabels[k],d.manual.grams>0?d.manual[k]:null,5);fields[k]=field.input;
  field.input.addEventListener('input',()=>{const val=field.input.value===''?0:Number(field.input.value.replace(',','.'));if(!Number.isFinite(val)||val<0)return;d.manual[k]=val;if(d.manual.grams>0&&d.per100)d.per100[k]=val*100/d.manual.grams;updateDishSummary(d);refreshFavoriteStars()});group.append(field.wrap)}
 weight.input.addEventListener('input',()=>{const w=weight.input.value===''?0:Number(weight.input.value.replace(',','.'));if(!Number.isFinite(w)||w<0||w>10000)return;
  const old=d.manual.grams;const scale=old>0?w/old:0;for(const k of MACRO_KEYS){d.manual[k]=d.per100&&Number.isFinite(d.per100[k])?d.per100[k]*w/100:(old>0?d.manual[k]*scale:0);fields[k].value=w>0?toDisplay(d.manual[k]):''}d.manual.grams=w;updateDishSummary(d);refreshFavoriteStars();});
 line.append(group);panel.append(line);return panel;
}
function getDraft(d){if(!draftsByDish.has(d.id))draftsByDish.set(d.id,{name:'',grams:100,per100:{k:null,p:null,f:null,c:null},options:[],status:'',busy:false,ready:false,source:''});return draftsByDish.get(d.id)}
function updateDraftInputs(d,container){const draft=getDraft(d);container.querySelectorAll('[data-add-macro]').forEach(input=>{const key=input.dataset.addMacro;input.value=draft.per100[key]===null?'':toDisplay(draft.grams*draft.per100[key]/100)});
 const weight=container.querySelector('[data-add-weight]');if(weight)weight.value=toDisplay(draft.grams)}
function applyCandidateToDraft(d,candidate){const draft=getDraft(d);
 draft.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,Math.max(0,Number(candidate[k])||0)]));draft.ready=true;draft.source=candidate.source||'';draft.status='Найдено: '+(candidate.source||'справочник')+'. Проверьте значения.';
 renderDishes();
}
async function lookupDraft(d){const draft=getDraft(d);const name=draft.name.trim();if(name.length<2){draft.status='Введите название ингредиента';renderDishes();return}
 const local=findFood(name);draft.ready=true;if(local){draft.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,local[k]]));draft.source='Локальный справочник';draft.status='Предварительная оценка. Проверяем внешнюю базу…'}
 else{draft.per100={k:null,p:null,f:null,c:null};draft.status='Ищем пищевую ценность…'}
 draft.options=[];draft.busy=true;renderDishes();
 try{const data=await fetchFoodCandidates(name);if(draft.name.trim()!==name)return;draft.options=(data.items||[]).slice(0,6);draft.status=(draft.options.length?'Найдены варианты; выберите подходящий или измените значения.':'Внешняя база не нашла совпадение.')+(data.sources?.usda?' USDA доступна.':'');
  if(!local&&draft.options.length) {const top=draft.options[0];draft.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,Math.max(0,Number(top[k])||0)]));draft.source=top.source;}
 }catch(e){draft.status='Поиск недоступен: '+String(e.message||e)+(local?' · Оставлена локальная оценка.':'')}
 finally{draft.busy=false;renderDishes()}
}
function addDraftPanel(d){const draft=getDraft(d),panel=el('div','addIngredientPanel');panel.append(el('h4','','Добавить ингредиент'));
 const nameLabel=el('label','inlineLabel','Название ингредиента'),name=el('input','addIngredientName');name.type='text';name.value=draft.name;name.placeholder='Например, соус сырный';name.autocomplete='off';
 name.addEventListener('input',()=>{if(draft.name!==name.value){draft.name=name.value;draft.per100={k:null,p:null,f:null,c:null};draft.options=[];draft.status='';draft.source='';draft.ready=false;
  const region=panel.querySelector('.draftResults');if(region)region.hidden=true;
 }});nameLabel.append(name);panel.append(nameLabel);
 const draftActions=el('div','draftActionRow');const find=button(draft.busy?'Поиск…':'Найти','secondary addSearchButton',()=>lookupDraft(d));find.disabled=draft.busy;draftActions.append(find);
 if(draft.ready||draft.name){const clear=button('×','iconAction red draftClear',()=>{draftsByDish.delete(d.id);renderDishes();});clear.setAttribute('aria-label','Очистить найденный ингредиент');draftActions.append(clear);}
 panel.append(draftActions);
 const region=el('div','draftResults');region.hidden=!draft.ready;
 if(draft.status)region.append(el('div','addIngredientStatus',draft.status));
 if(draft.options.length){const suggestions=el('div','addSuggestions');for(const candidate of draft.options){const ru=capital(candidate.name_ru||candidate.name);const wrap=el('div','addOptionText');wrap.append(el('strong','',ru));if(candidate.source==='USDA FoodData Central')wrap.append(el('small','resultEnglish',candidate.name));wrap.append(el('small','',`${candidate.source} · ${num(candidate.k)} ккал / 100 г`));suggestions.append(button('', 'addSuggestion',()=>applyCandidateToDraft(d,candidate)));suggestions.lastChild.append(wrap)}region.append(suggestions)}
 const fields=el('div','addItemNutrition'),w=nutritionField('Вес, г',draft.grams,10,'weightEdit'),macros=el('div','macroFields');w.input.dataset.addWeight='1';fields.append(w.wrap);
 w.input.addEventListener('input',()=>{const val=w.input.value===''?0:Number(w.input.value.replace(',','.'));if(!Number.isFinite(val)||val<0||val>10000)return;draft.grams=val;
  for(const k of MACRO_KEYS){const input=region.querySelector(`[data-add-macro="${k}"]`);if(input)input.value=draft.per100[k]===null?'0':toDisplay(val*draft.per100[k]/100)}
  refreshDraftMissing();});
 for(const k of MACRO_KEYS){const v=draft.per100[k]===null?0:draft.grams*draft.per100[k]/100;const f=nutritionField(macroLabels[k],v,5);f.input.dataset.addMacro=k;
  f.input.addEventListener('input',()=>{const val=f.input.value===''?0:Number(f.input.value.replace(',','.'));if(!Number.isFinite(val)||val<0)return;
   if(draft.grams>0)draft.per100[k]=val*100/draft.grams;else f.input.value='0';refreshDraftMissing()});macros.append(f.wrap)}
 fields.append(macros);region.append(fields);
 const add=button('Добавить','primary addIngredientSubmit',()=>{
  if(!draft.name.trim()||!(draft.grams>0)||draft.grams>10000){draft.status='Укажите название и вес больше нуля.';const msg=region.querySelector('.addIngredientStatus');if(msg)msg.textContent=draft.status;else region.prepend(el('div','addIngredientStatus',draft.status));return}
  const ingredient={id:id(),name:capital(draft.name),grams:draft.grams,...Object.fromEntries(MACRO_KEYS.map(k=>[k,draft.per100[k]])),source:draft.source||'unknown'};
  if(!d.items.length)d.manual=emptyTotals();d.items.push(ingredient);draftsByDish.delete(d.id);renderDishes();
 });region.append(add);panel.append(region);
 function refreshDraftMissing(){w.input.classList.toggle('missingData',!(draft.grams>0));for(const k of MACRO_KEYS){const field=region.querySelector(`[data-add-macro="${k}"]`);if(field)field.classList.toggle('missingData',draft.per100[k]===null)}}refreshDraftMissing();
 return panel;
}
function renderDishes(focusDishId=null){const holder=$('dishesList');holder.replaceChildren();$('preview').hidden=!dishes.length;
 for(const d of dishes){const card=el('article','dishCard');card.dataset.dish=d.id;
  const nameHeading=el('div','dishHeading'),label=el('label','dishLabel','Название блюда');const dishName=el('input','dishNameInput');dishName.type='text';dishName.value=d.name;dishName.placeholder='Введите название блюда';dishName.maxLength=100;
  dishName.addEventListener('input',()=>{d.name=dishName.value;updateDishSummary(d);refreshFavoriteStars()});label.append(dishName);
  const remove=button('×','iconAction red',()=>{dishes=dishes.filter(x=>x.id!==d.id);draftsByDish.delete(d.id);renderDishes()});remove.setAttribute('aria-label','Убрать блюдо');nameHeading.append(label,remove);card.append(nameHeading);
  const totals=el('div','dishTotals');totals.dataset.dishTotal=d.id;card.append(totals);
  const warning=el('small','dishWarning');warning.dataset.dishWarning=d.id;card.append(warning);
  if(d.items.length){const itemsHolder=el('div','dishIngredients');for(const item of d.items)itemsHolder.append(editFieldGroup(item,d));card.append(itemsHolder)}
  else card.append(editWholeDish(d));
  if(d.uncertain?.length){const p=el('p','hint','Требует уточнения: '+d.uncertain.join('; '));card.append(p)}
  card.append(addDraftPanel(d));
  const actions=el('div','dishActions'),star=button('☆','iconFavorite',()=>toggleFavorite(d)),save=button('Сохранить','primary',()=>saveDish(d));star.dataset.dishStar=d.id;save.dataset.dishSave=d.id;actions.append(star,save);card.append(actions);holder.append(card);updateDishSummary(d);
  if(focusDishId===d.id){dishName.focus();selectAllEditor(dishName)}
 }
 refreshFavoriteStars();
}
function releasePhotoPreview(){activePhotoRun++;if(photoUrl){URL.revokeObjectURL(photoUrl);photoUrl=null;} photoFile=null;const image=$('photoPreview');image.hidden=true;image.removeAttribute('src');$('photoAIStatus').textContent='';$('photoCandidates').replaceChildren();$('photoProgressWrap').hidden=true;}
async function saveDish(d){if(!canSaveDish(d))return;
 const idx=dishes.findIndex(x=>x.id===d.id);const nextId=dishes[idx+1]?.id||dishes[idx-1]?.id||null;
 try{await put('entries',{id:id(),name:capital(d.name),items:cloneItems(d.items),manual:d.items.length?null:{...d.manual},date:today(),created:new Date().toISOString()});
  dishes=dishes.filter(x=>x.id!==d.id);draftsByDish.delete(d.id);
  // Never discard an input source while there are unsaved dishes from this batch.
  if(!dishes.length){if(pendingSource==='text')$('foodText').value='';if(pendingSource==='photo')releasePhotoPreview();pendingSource=null;}
  renderDishes();selectedDay=today();await refresh();setStatus('');if(dishes.length)scrollToDish(nextId);}
 catch(e){setStatus('Не удалось сохранить: '+e.message)}
}
function renderDateStrip(){const strip=$('dateStrip');strip.replaceChildren();const more=button('···','dateMore',()=>{const wrap=$('calendarWrap');wrap.hidden=!wrap.hidden;calendarBase=dateFromKey(selectedDay);renderCalendar()});strip.append(more);
 for(let ago=6;ago>=0;ago--){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()-ago);const key=dayKey(d);
  const tag=d.toLocaleDateString('ru-RU',{weekday:'short'}).replace('.','').slice(0,2).replace(/^./,x=>x.toUpperCase());const b=el('button','dateChip'+(key===selectedDay?' chosen':''));b.type='button';b.append(el('small','',tag),el('strong','',String(d.getDate())));b.addEventListener('click',()=>{selectedDay=key;$('calendarWrap').hidden=true;refresh()});strip.append(b)}}
function renderCalendar(){const grid=$('calendarGrid');grid.replaceChildren();const base=new Date(calendarBase.getFullYear(),calendarBase.getMonth(),1);$('calendarMonth').textContent=base.toLocaleDateString('ru-RU',{month:'long',year:'numeric'});
 for(const day of ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'])grid.append(el('span','calendarWeek',day));const start=(base.getDay()+6)%7;for(let i=0;i<start;i++)grid.append(el('span','calendarBlank',''));
 const end=new Date(base.getFullYear(),base.getMonth()+1,0).getDate();for(let i=1;i<=end;i++){const key=dayKey(new Date(base.getFullYear(),base.getMonth(),i));const b=button(String(i),'calendarDay'+(key===selectedDay?' chosen':''),()=>{selectedDay=key;$('calendarWrap').hidden=true;refresh()});b.disabled=key>today();grid.append(b)}}
$('calendarPrev').addEventListener('click',()=>{calendarBase.setMonth(calendarBase.getMonth()-1);renderCalendar()});$('calendarNext').addEventListener('click',()=>{calendarBase.setMonth(calendarBase.getMonth()+1);renderCalendar()});
function renderDailyTotals(entries){const tday=entries.filter(e=>(e.date||String(e.created||'').slice(0,10))===today());const t=sumEntries(tday);
 $('todayLabel').textContent=dayText(today());$('mealsCount').textContent='Записей: '+tday.length;$('kcal').textContent=num(t.k);$('prot').textContent=one(t.p)+' г';$('fat').textContent=one(t.f)+' г';$('carb').textContent=one(t.c)+' г';
 const ratio=t.k/NORMS.k;$('calPercent').textContent=Math.round(ratio*100)+'%';$('calRing').style.setProperty('--progress',Math.min(100,ratio*100)+'%');$('calRing').style.setProperty('--ringColor',ratio>=.95?'#e64737':ratio>=.75?'#ef9c28':'#298c20');$('calRing').setAttribute('aria-valuenow',String(num(t.k)));
 for(const [key,id] of [['p','protMeter'],['f','fatMeter'],['c','carbMeter']]){const r=t[key]/NORMS[key],bar=$(id);bar.style.width=Math.min(100,r*100)+'%';bar.style.background=r>=.95?'#e54d43':r>=.75?'#f7a22c':'#328c22'}
}
function renderHistorySummary(entries){const box=$('historySummary');box.replaceChildren();const t=sumEntries(entries);
 const head=el('div','historySummaryTitle');head.append(el('span','','Итоги: '+dayText(selectedDay)),el('span','',`Записей: ${entries.length}`));box.append(head,el('div','historySummaryFacts',`Общий вес: ${num(t.grams)} г`));
 // Keep the four nutrition progress lines at the same baseline on every phone width.
 const grid=el('div','historyKpis');
 for(const [label,key,unit] of [['Ккал','k','ккал'],['Белки','p','г'],['Жиры','f','г'],['Углеводы','c','г']]){
  const ratio=t[key]/NORMS[key],p=Math.round(ratio*100),card=el('div','historyKpi');
  // "Ккал" is already the heading; do not repeat it in the current value or goal.
  const value=key==='k'?num(t[key]):`${one(t[key])} ${unit}`;
  const goal=key==='k'?`${NORMS[key]}`:`${NORMS[key]} ${unit}`;
  card.append(el('small','',label),el('strong','',value),el('em','',`${p}% / ${goal}`));
  const m=el('div','historyMeter'),inner=el('i');inner.style.width=Math.min(100,ratio*100)+'%';inner.style.background=ratio>=.95?'#de483f':ratio>=.75?'#ed9f29':'#3b992a';m.append(inner);card.append(m);grid.append(card);
 }
 box.append(grid)
}
async function refresh(){if(!db)return;const [entries,faves]=await Promise.all([all('entries'),all('favorites')]);favoritesCache=faves||[];entries.sort((a,b)=>String(b.created||'').localeCompare(String(a.created||'')));
 renderDailyTotals(entries);$('historyDayText').textContent=selectedDay===today()?'Сегодня':dateFromKey(selectedDay).toLocaleDateString('ru-RU',{day:'numeric',month:'short'});renderDateStrip();
 const selected=entries.filter(x=>(x.date||String(x.created||'').slice(0,10))===selectedDay);renderHistorySummary(selected);
 const hist=$('historyItems');hist.replaceChildren();if(!selected.length)hist.append(el('p','empty','За выбранный день пока нет записей.'));
 for(const entry of selected){const t=totalsFor(entry),card=el('article','entry');card.append(el('b','historyDishName',capital(entry.name||summaryLabel(entry.items))));
  card.append(el('div','entryDetail',`Вес: ${num(t.grams)} г · К: ${num(t.k)} · Б: ${one(t.p)} · Ж: ${one(t.f)} · У: ${one(t.c)}`));
  if((entry.items||[]).length){const details=el('details','entryIngredients');details.append(el('summary','','Состав · '+entry.items.length));for(const i of entry.items)details.append(el('div','entryIngredient',`${capital(i.name)} · ${num(i.grams)} г · К: ${num(portionVal(i,'k'))} · Б: ${one(portionVal(i,'p'))} · Ж: ${one(portionVal(i,'f'))} · У: ${one(portionVal(i,'c'))}`));card.append(details)}
  const foot=el('div','entryFooter'),time=el('span','entryDate');const date=new Date(entry.created);time.textContent=Number.isNaN(date.valueOf())?'':date.toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'});foot.append(time);
  const actions=el('div','miniActions'),fbutton=button('☆','iconAction',()=>toggleFavorite({...entry,name:entry.name||summaryLabel(entry.items)}));if(favoriteFor({...entry,name:entry.name||summaryLabel(entry.items)})){fbutton.textContent='★';fbutton.classList.add('on')}
  const remove=button('×','iconAction red',async()=>{await erase('entries',entry.id);await refresh()});remove.setAttribute('aria-label','Удалить запись');actions.append(fbutton,remove);foot.append(actions);card.append(foot);hist.append(card)}
 const favorite=$('favoritesList');favorite.replaceChildren();if(!faves.length)favorite.append(el('p','empty','Избранных блюд пока нет.'));
 for(const f of faves){const t=totalsFor(f),card=el('article','entry');card.append(el('b','historyDishName',capital(f.name||summaryLabel(f.items))),el('div','entryDetail',`Вес: ${num(t.grams)} г · К: ${num(t.k)} · Б: ${one(t.p)} · Ж: ${one(t.f)} · У: ${one(t.c)}`));
  const foot=el('div','entryFooter'),actions=el('div','miniActions');actions.append(button('＋ Использовать','textBtn',()=>{dishes.push(newDish(f.name,f.items,[],f.manual));renderDishes();setTab('Text');$('preview').scrollIntoView({behavior:'smooth',block:'nearest'})}));actions.append(button('★','iconAction on',async()=>{await erase('favorites',f.id);await refresh();refreshFavoriteStars()}));foot.append(actions);card.append(foot);favorite.append(card)}
 refreshFavoriteStars();
}
function setTab(value){for(const x of ['Text','Photo','Faves']){const active=x===value;$('pane'+x).hidden=!active;$('tab'+x).classList.toggle('active',active);$('tab'+x).setAttribute('aria-selected',String(active))}}
$('tabText').addEventListener('click',()=>setTab('Text'));$('tabFaves').addEventListener('click',()=>setTab('Faves'));
$('tabPhoto').addEventListener('click',()=>{setTab('Photo');const input=$('photoInput');input.value='';input.click()});
$('photoInput').addEventListener('change',async e=>{const file=e.target.files?.[0];e.target.value='';if(!file)return;
 if(!file.type.startsWith('image/')){$('photoAIStatus').textContent='Выберите изображение';return}
 $('photoAIStatus').textContent='';const processed=await preparePhotoBlob(file);if(processed.size>2e6){$('photoAIStatus').textContent='Изображение слишком большое';return}
 if(photoUrl)URL.revokeObjectURL(photoUrl);photoFile=processed;photoUrl=URL.createObjectURL(processed);$('photoPreview').src=photoUrl;$('photoPreview').hidden=false;recognizePhoto()});
async function preparePhotoBlob(file){const src=URL.createObjectURL(file);try{const image=new Image();image.src=src;await image.decode();const ratio=Math.min(1,900/Math.max(image.naturalWidth,image.naturalHeight));
 const c=document.createElement('canvas');c.width=Math.round(image.naturalWidth*ratio);c.height=Math.round(image.naturalHeight*ratio);c.getContext('2d').drawImage(image,0,0,c.width,c.height);const blob=await new Promise(ok=>c.toBlob(ok,'image/jpeg',.75));c.width=0;c.height=0;return blob||file;
 }catch(e){console.warn(e);return file}finally{URL.revokeObjectURL(src)}}
async function requestCloudFood({text='',file=null,signal}){const body=new FormData();body.set('text',text.slice(0,500));if(file)body.set('photo',file,'meal.jpg');const response=await fetch(CLOUD_AI_ENDPOINT,{method:'POST',body,mode:'cors',cache:'no-store',signal});let data;const raw=await response.text();try{data=JSON.parse(raw)}catch(_){throw Error('Worker вернул не JSON, HTTP '+response.status)}
 if(!response.ok||data.ok!==true)throw Error('HTTP '+response.status+': '+String(data.message||data.error||'Cloudflare AI'));return data;}

// Cloud nutrition lookup: apply only well-matching documented records, never invent missing K/B/F/C.
const isChainText=(text)=>/(?:^|\s)(?:из\s+)?мак(?:а|е|ом)?(?=[\s:;,]|$)|вкусно\s*[-—–]?\s*и\s*точка|макдоналдс/i.test(String(text||''));
function toOfficialDish(row,quantity=1){
 const w=row.w*quantity;
 const per={k:row.k/row.w*100,p:row.p/row.w*100,f:row.f/row.w*100,c:row.c/row.w*100};
 return newDish(row.base_name,[{name:row.name,grams:w,...per,source:'Вкусно — и точка',verified_brand:true}]);
}
// Prefer independent menu items as named by the user, never a vague summary from the LLM.
async function applyRestaurantNutrition(input,parsed,signal){
 const response=await fetch(CHAIN_ORDER_API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:input}),mode:'cors',cache:'no-store',signal});
 const raw=await response.text();let data;
 try{data=JSON.parse(raw)}catch(e){throw Error('Разбор ресторанного заказа: не JSON, HTTP '+response.status)}
 if(!response.ok||data.ok!==true)throw Error('Разбор заказа: HTTP '+response.status+': '+(data.error||'Неизвестная ошибка'));
 devRecord('Разделение заказа и проверка меню',{input,diagnostics:data.diagnostics,restaurant:data.restaurant});
 const official=[];
 for(const item of data.dishes||[]){
  if(item.found&&item.row&&Number(item.row.w)>0){
   const dish=toOfficialDish(item.row,Number(item.quantity)||1);
   if(item.row.estimated_portion)dish.weightReview='Величина порции получена масштабированием имеющегося значения';
   official.push(dish);
  }else{
   const name=capital(item.canonical||item.input||'Неизвестная позиция');
   official.push(newDish(name,[{name,grams:0,k:null,p:null,f:null,c:null,source:'unknown',portion:'',lookup_error:item.reason||'Не найдено в меню'}]));
  }
 }
 if(!official.length)throw Error('Облачный разбор не вернул ни одной позиции');
 return official;
}
async function autoCompleteNutrition(current,source,runId){
 const tasks=[];
 for(const dish of current)for(const item of dish.items||[]){
  if(item.verified_brand||item.userEdited||(!item.name||item.name.length<2))continue;
  // Verified or internally curated food data is a valid result, not something to overwrite
  // with the first remotely similar result (e.g. dried egg powder instead of fried eggs).
  if(!hasMissingNutrition(item))continue;
  tasks.push({dish,item,query:item.name});
 }
 if(!tasks.length)return {queried:0,filled:0};
 const names=[...new Set(tasks.map(t=>t.query))].slice(0,12);
 let updates=0;
 try{
  const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),30000);
  let response;
  try{response=await fetch(FOOD_BATCH_API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({queries:names}),mode:'cors',cache:'no-store',signal:controller.signal});}
  finally{clearTimeout(timeout)}
  if(!response.ok)throw Error('Поиск КБЖУ: HTTP '+response.status);
  const result=await response.json();
  const lookup=new Map((result.results||[]).map(r=>[r.query,r]));
  devRecord('Поиск КБЖУ: кандидаты',{requests:names,results:(result.results||[]).map(x=>({query:x.query,diagnostics:x.diagnostics,items:(x.items||[]).slice(0,8)}))});
  for(const {dish,item,query} of tasks){
   if(item.userEdited || !(dish.items||[]).includes(item))continue;
   const options=lookup.get(query)?.items||[];
   // Require a strong name match and plausible nutrient composition.
   // Low score contains bad matches such as DRIED EGG/CANDY in egg search.
   const best=options.find(o=>Number(o.match_score)>=70 &&
    ['k','p','f','c'].every(k=>Number.isFinite(Number(o[k])) && Number(o[k])>=0) &&
    Number(o.k)<=900 &&
    !(/\b(?:powder|dried|substitute|pretzel|flavored|candy|mix)\b/i.test(o.name||'') && !/порош|сух|смес/i.test(query)));
   if(!best)continue;
   // Nutrient lookup never substitutes a default portion. Missing weight must remain editable (0).
   for(const k of MACRO_KEYS)item[k]=Number(best[k]);
   item.source=best.source||'Открытая база';item.source_name=best.name;updates++;
  }
 }catch(e){console.warn('Автоматический поиск КБЖУ:',e.message||e)}
 return {queried:names.length,filled:updates};
}


// v0.9.6 — find complete prepared dishes first. Decompose only if an exact
// finished-dish match is unavailable. Never count included sauce twice.
const MEAL_PLATTER_RE=/турецк.{0,20}завтрак|завтрак.{0,20}турецк|шведск.{0,12}стол|ассорти|набор.{0,12}(?:блюд|закус)|завтрак.{0,12}(?:набор|из)|смешанн.{0,12}тарелк/i;
const READY_MAIN_RE=/пельмен|вареник|манты|борщ|суп|солянк|уха|бургер|гамбургер|пицц|плов|сырник|стейк|котлет|яичниц|омлет|суши|ролл|паст|макарон|блин|шаурм/i;
const BAD_CANDIDATE_RE=/powder|dried|substitute|pretzel|candy|flavored|infant|baby food|dry mix|порош|сухой смеси/i;
function comparableWords(value){
 return itemKey(value).replace(/\b(?:со|с|из|в|на|для|без|порция|порции|штук|штуки|шт|г|грамм|маленькая|средняя|большая|блюдо|готовое)\b/gu,' ')
 .split(/\s+/).filter(x=>x.length>2&&!/^\d+$/.test(x)).map(x=>x.slice(0,x.length>6?5:4)).filter(Boolean);
}
function exactEnough(needle,hay){
 const q=comparableWords(needle),h=comparableWords(hay);
 if(!q.length||!h.length)return false;
 const hit=q.filter(w=>h.some(t=>t.startsWith(w)||w.startsWith(t))).length;
 return hit===q.length && Math.min(q.length,h.length)/Math.max(q.length,h.length)>=.55;
}
function localWholeMatch(query){
 const key=itemKey(query);
 return FOOD.find(f=>itemKey(f.name)===key || f.aliases.some(a=>itemKey(a)===key && key.length>=4))||null;
}
function candidateMatch(query,candidate,full=false,englishQuery=''){
 if(!candidate||!['k','p','f','c'].every(k=>Number.isFinite(Number(candidate[k]))&&Number(candidate[k])>=0))return -1;
 if(Number(candidate.k)>900||Number(candidate.p)>100||Number(candidate.f)>100||Number(candidate.c)>100)return -1;
 const original=String(candidate.name||''),translated=String(candidate.name_ru||'');
 if(BAD_CANDIDATE_RE.test(original)&&!BAD_CANDIDATE_RE.test(query))return -1;
 const exactRu=exactEnough(query,translated),exactOrig=exactEnough(query,original),exactEnglish=!!englishQuery&&exactEnough(englishQuery,original),provider=Number(candidate.match_score)||0;
 // Reject forms that clearly differ from the requested food, even when the core word matches.
 const requested=clean(query+' '+englishQuery),label=clean(original+' '+translated);
 if(/\b(?:oil|pate|powder|mix|candy|nog|fu yung|chocolate|creme egg)\b/i.test(label) && !/\b(?:oil|pate|powder|mix|candy|nog|fu yung|chocolate|creme egg)\b/i.test(requested))return -1;
 if(full){
  // Server score alone is not enough to call a DIFFERENT recipe the same finished dish.
  if(!exactRu&&!exactOrig&&!exactEnglish && provider<115)return -1;
  if(/соус|сметан/.test(query)&&!/(соус|сметан|sauce|sour cream)/i.test(translated+' '+original))return -1;
  if(/жарен|глазун/.test(query)&&!/(жарен|глазун|fried)/i.test(translated+' '+original))return -1;
 }else if(!exactRu&&!exactOrig&&!exactEnglish&&provider<68)return -1;
 let score=provider*.45+(exactRu?90:0)+(exactOrig?92:0)+(exactEnglish?95:0);
 if(candidate.brand)score-=comparableWords(query).length<=2?50:18;
 if(!candidate.brand && /CoFID|Matvaretabellen|Livsmedelsverket|Canadian Nutrient|Foundation|SR Legacy|FNDDS/i.test((candidate.source||'')+' '+(candidate.dataType||'')))score+=14;
 if(candidate.source)score+=2;
 return score;
}
function median(vals){const a=[...vals].sort((x,y)=>x-y);return a.length?a[Math.floor((a.length-1)/2)] : 0}
function resolveNutrition(query,candidates,full=false,englishQuery=''){
 const ranked=(candidates||[]).map(v=>({row:v,score:candidateMatch(query,v,full,englishQuery)})).filter(x=>x.score>=0).sort((a,b)=>b.score-a.score);
 if(!ranked.length)return null;
 // For a generic food query, prefer independent reference foods to branded
 // products with identical short labels (e.g. a commercial product named BEER).
 if(ranked.some(x=>!x.row.brand) && comparableWords(query).length<=2)
  ranked.sort((a,b)=>(b.score-(b.row.brand?40:0))-(a.score-(a.row.brand?40:0)));
 const strongest=ranked[0];
 // Do not treat ten listings from one provider as ten independent confirmations.
 const representatives=[],seenSource=new Set();
 for(const x of ranked){
  if(x.score<strongest.score-30)continue;
  const src=String(x.row.source||'unattributed');if(seenSource.has(src))continue;
  seenSource.add(src);representatives.push(x);
 }
 const comparable=(left,right)=>{
  const a=Number(left.row.k),b=Number(right.row.k);
  if(Math.abs(a-b)>Math.max(25,Math.min(a,b)*.15))return false;
  return ['p','f','c'].every(k=>{const v=Number(left.row[k]),w=Number(right.row[k]);return Math.abs(v-w)<=Math.max(4,Math.max(v,w)*.35)});
 };
 // Choose the largest internally coherent cluster. A high-scoring outlier must
 // not override two independent databases that agree on the same prepared food.
 let selected=[strongest];
 for(const pivot of representatives){
  const group=[pivot];
  for(const x of representatives.filter(x=>x!==pivot).sort((a,b)=>Math.abs(a.row.k-pivot.row.k)-Math.abs(b.row.k-pivot.row.k))){
   if(group.every(y=>comparable(x,y)))group.push(x);
  }
  const groupQuality=group.reduce((sum,x)=>sum+x.score,0);
  const bestQuality=selected.reduce((sum,x)=>sum+x.score,0);
  if(group.length>selected.length||(group.length===selected.length&&groupQuality>bestQuality))selected=group;
 }
 const weights=selected.map(x=>Math.max(1,x.score));const total=weights.reduce((a,b)=>a+b,0);
 const per=Object.fromEntries(MACRO_KEYS.map(k=>[k,selected.reduce((v,x,i)=>v+Number(x.row[k])*weights[i],0)/total]));
 devRecord('Выбор КБЖУ',{query,full,considered:ranked.slice(0,7).map(x=>({name:x.row.name,ru:x.row.name_ru,source:x.row.source,score:x.score,k:x.row.k,p:x.row.p,f:x.row.f,c:x.row.c})),selected:selected.map(x=>({source:x.row.source,name:x.row.name,score:x.score})),final_per100:per});
 return {...per,source:selected.map(x=>x.row.source).join(' + ')||'База КБЖУ',name:strongest.row.name_ru||strongest.row.name,allBranded:selected.every(x=>!!x.row.brand),approximate:selected.some(x=>!!(x.row.reference_fallback||x.row.approximate))};
}
// Broad-match fallback ONLY if no comparable whole dish was found. A generic
// "cake" food record is useful as an editable estimate for a cream/sponge cake;
// it must not be asserted as the exact commercial product or exact recipe.
function approximateCategoryNutrition(query,candidates){
 const key=clean(query),qCake=/торт|cake|пирожн/.test(key);
 if(!qCake || /медовик|наполеон|чизкейк|cheesecake/.test(key))return null;
 const valid=(candidates||[]).filter(c=>candidateMatch(query,c,false)>=-1 &&
   ['k','p','f','c'].every(k=>Number.isFinite(Number(c[k]))&&Number(c[k])>=0) &&
   Number(c.k)>100 && Number(c.k)<700 &&
   /\bcake\b|торт|бисквит/i.test((c.name||'')+' '+(c.name_ru||'')) &&
   !/mix|batter|dry|powder|pancake|rice cake|cake flour|pancake|waffle|cheesecake|gingerbread|тортовая смесь|смесь для выпечки/i.test(c.name||''));
 if(!valid.length)return null;
 const withCream=/крем|сливк|соус|глазур/.test(key);
 const rated=valid.map(c=>{
   const n=String(c.name||'').toLowerCase();let s=Number(c.match_score||0)*.1;
   if(/\bcake\b/.test(n))s+=15;
   if(/frost|icing|cream|filled|layer/.test(n))s+=withCream?26:3;
   if(/sponge/.test(n))s+=withCream?-5:15;
   if(/chocolate/.test(n)&&!/(шоколад|chocolate)/.test(key))s-=8;
   if(/fruitcake|cupcake|mug cake|snack cake/.test(n))s-=12;
   if(c.brand)s-=5;
   if(/FNDDS|SR Legacy|Foundation/i.test(c.dataType||''))s+=6;
   return {c,s};
 }).sort((a,b)=>b.s-a.s);
 const c=rated[0].c;
 const approximate={k:Number(c.k),p:Number(c.p),f:Number(c.f),c:Number(c.c),name:c.name_ru||c.name,source:'Приблизительный аналог: '+(c.source||'справочник'),approximate:true,includesToppings:true};
 devRecord('Подбор приближённого готового блюда',{query,category:'Торт / cake',candidates:rated.slice(0,7).map(x=>({name:x.c.name,k:x.c.k,p:x.c.p,f:x.c.f,c:x.c.c,source:x.c.source,score:x.s})),selected:c.name,note:'Не точная рецептура. КБЖУ выбраны по сопоставимому готовому изделию.'});
 return approximate;
}
function inferGroupPlan(group){
 const name=String(group.name||'Блюдо').trim()||'Блюдо';
 const items=Array.isArray(group.items)?group.items.filter(x=>x&&x.name):[];
 let main=String(group.main||'').trim(),mainPortion=String(group.main_portion||'').trim();
 let additions=Array.isArray(group.additions)?group.additions.filter(x=>x?.name).map(x=>({...x,name:String(x.name),portion:String(x.portion||'1 порция')})):[];
 let kind=['prepared','platter','recipe'].includes(group.kind)?group.kind:'prepared';
 if(MEAL_PLATTER_RE.test(name))kind='platter';
 const suffix=name.match(/^(.+?)\s+(?:со?|в)\s+(сметан(?:ой|а|у)|соус(?:е|ом)?\s+[^,]+)$/i);
 if(suffix){
   if(!main||itemKey(main)===itemKey(name))main=suffix[1].trim();
   if(!additions.some(a=>/сметан|соус/.test(clean(a.name))))additions.push({name:capital(suffix[2].replace(/^соусе?м?\s+/i,'Соус ')),portion:'1 порция'});
   if(/кревет|рыб|куриц|мяс|овощ/.test(clean(main))&&/соус/.test(clean(suffix[2])))kind='recipe';
 }
 if(!main && kind!=='platter'){
  const possible=items.find(x=>exactEnough(x.name,name));
  const edible=items.find(x=>!/(соус|сметан|майонез|приправ|специ)/.test(clean(x.name)));
  main=possible?.name||(/^(?:блюдо|еда|тарелка)$/i.test(name)?(edible?.name||name):name);
 }
 const mainIncluded=items.find(x=>exactEnough(x.name,main));
 if(!mainPortion)mainPortion=String(mainIncluded?.portion||'1 порция');
 const mainMeta={...mainIncluded,weight_g:kind==='recipe'?(mainIncluded?.weight_g??group.main_weight_g??null):(group.main_weight_g??mainIncluded?.weight_g??null),volume_ml:kind==='recipe'?(mainIncluded?.volume_ml??group.main_volume_ml??null):(group.main_volume_ml??mainIncluded?.volume_ml??null),weight_basis:(kind==='recipe'&&mainIncluded?.weight_g?mainIncluded?.weight_basis:'')||group.main_weight_basis||mainIncluded?.weight_basis||'',weight_estimated:mainIncluded?.weight_estimated!==false};
 // Older AI versions may return ONLY the topping of a recognized main dish.
 if(!additions.length){
  // Only infer a side when ALL model items are toppings: e.g. 'Пельмени' but only 'Сметана'.
  // Sauces already INSIDE a burger are not separate servings.
  const core=items.filter(x=>!/сметан|соус|кетчуп|майонез|мед/.test(clean(x.name)));
  if(!core.length) additions=items.filter(x=>!exactEnough(x.name,main)&&/сметан|соус|кетчуп|майонез|мед/.test(clean(x.name)));
 }
 const seen=new Set();additions=additions.filter(x=>{const key=itemKey(x.name);if(seen.has(key))return false;seen.add(key);return !exactEnough(x.name,main)});
 return {name,kind,main,mainPortion,mainMeta,additions,items};
}
async function batchNutritionQueries(inputQueries){
 const queries=[...new Set(inputQueries.map(x=>String(x||'').trim()).filter(x=>x.length>=2))].slice(0,24);
 const result=new Map();
 async function fetchOne(q){
  const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),18000);
  try{
   const r=await fetch(FOOD_SEARCH_API+'?q='+encodeURIComponent(q),{mode:'cors',cache:'no-store',signal:ctrl.signal});
   const data=await r.json();if(!r.ok)throw Error('HTTP '+r.status+': '+(data.error||''));
   result.set(q,{query:q,...data});
   devRecord('Поиск КБЖУ: отдельный ответ',{query:q,diagnostics:data.diagnostics,options:(data.items||[]).slice(0,7)});
  }catch(e){devRecord('Ошибка отдельного поиска КБЖУ',{query:q,error:String(e.message||e)});}
  finally{clearTimeout(timer)}
 }
 // A small group is fast on Worker v1.11; on failure try every query separately
 // so a single delayed API request cannot erase results already received.
 for(let i=0;i<queries.length;i+=6){
  const slice=queries.slice(i,i+6),controller=new AbortController(),timer=setTimeout(()=>controller.abort(),23000);
  try{
   const r=await fetch(FOOD_BATCH_API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({queries:slice}),mode:'cors',cache:'no-store',signal:controller.signal});
   if(!r.ok)throw Error('HTTP '+r.status);
   const json=await r.json();if(!json.ok)throw Error(json.error||'Некорректный ответ');
   for(const x of json.results||[])result.set(x.query,x);
   devRecord('Все найденные КБЖУ',{queries:slice,results:(json.results||[]).map(x=>({query:x.query,diagnostics:x.diagnostics,sources:x.sources,options:(x.items||[]).slice(0,10)}))});
   const missing=slice.filter(q=>!result.has(q));if(missing.length)await Promise.all(missing.map(fetchOne));
  }catch(error){
   devRecord('Ошибка группы КБЖУ',{queries:slice,error:String(error.message||error),action:'Повторить запросы по одному'});
   await Promise.all(slice.map(fetchOne));
  }finally{clearTimeout(timer)}
 }
 return result;
}

function nutritionFor(query,found,full=false){
 const result=found.get(query)||{}, candidates=result.items||[];
 const englishQuery=String(result.english_query||'');
 const remote=resolveNutrition(query,candidates,full,englishQuery);
 const local=localWholeMatch(query);
 // A single branded hit called "EGG" is not necessarily an ordinary egg.
 // Prefer a curated generic value when the branded entry is implausibly different.
 if(local && remote?.allBranded && (remote.k<local.k*.55||remote.k>local.k*1.65)){
   devRecord('Отказ от нерепрезентативного бренда',{query,remote:remote.name,k:remote.k,local:local.name,local_k:local.k});
   return {...local,approximate:true,source:local.source||'Приблизительный встроенный справочник'};
 }
 if(remote)return remote;
 if(full){const approximate=approximateCategoryNutrition(query,candidates);if(approximate)return approximate;}
 if(local){devRecord('Резервный справочник',{query,nutrition:local,whole:full});return {...local,approximate:true,source:local.source||'Приблизительный встроенный справочник',includesToppings:/торт с кремом/.test(local.name)};}
 // Last resort per user request: when strict multilingual matching rejected all
 // nutritional records, use the most plausible available original candidate
 // instead of leaving K/B/F/C blank. Clearly mark this as approximate.
 const plausible=candidates.filter(x=>['k','p','f','c'].every(k=>x[k]!==null&&x[k]!==undefined&&Number.isFinite(Number(x[k]))&&Number(x[k])>=0)&&Number(x.k)<=900);
 const acceptable=plausible.filter(x=>!BAD_CANDIDATE_RE.test(String(x.name||'')) &&
  !(/печен[ьи]\s+треск|тресков[а-я]*\s+печен/i.test(query) && /\boil\b|рыбий жир|масло печени/i.test(String(x.name||'')+' '+String(x.name_ru||''))));
 const pool=acceptable.length?acceptable:plausible.filter(x=>
   !(/печен[ьи]\s+треск|тресков[а-я]*\s+печен/i.test(query) && /\boil\b|рыбий жир|масло печени/i.test(String(x.name||'')+' '+String(x.name_ru||''))));
 if(pool.length){
  const ranked=pool.map(x=>{
   const label=String(x.name||'')+' '+String(x.name_ru||'');
   const n=String(x.name||'').toLowerCase();
   let score=Number(x.match_score)||0;
   if(exactEnough(query,label)||englishQuery&&exactEnough(englishQuery,label))score+=65;
   if(x.brand)score-=25;
   if(/CoFID|Matvaretabellen|Livsmedelsverket|Canadian Nutrient|Foundation|SR Legacy|FNDDS/i.test(String(x.source||'')+' '+String(x.dataType||'')))score+=20;
   if(/\b(?:oil|pate|powder|candy|nog|fu yung|mix)\b/i.test(n)&&!/(масло|паштет|порош|конфет|\boil\b|\bpate\b|\bmix\b)/i.test(query+' '+englishQuery))score-=180;
   return {x,score};
  }).sort((a,b)=>b.score-a.score);
  if(ranked[0].score>=-40){
   const x=ranked[0].x;
   devRecord('Резерв из отклонённых результатов',{query,english_query:englishQuery,candidate:x.name,source:x.source,score:ranked[0].score,note:'КБЖУ приблизительные; совпадение не прошло строгий отбор'});
   return {...Object.fromEntries(MACRO_KEYS.map(k=>[k,Number(x[k])])),source:'Приблизительный справочный аналог: '+(x.source||'источник'),name:x.name_ru||x.name,approximate:true,matched_by:'relaxed_fallback'};
  }
 }
 // Existing recipe-only approximation for whipped-cream cakes.
 if(full && /торт|пирожн/.test(clean(query)) && !/медовик|наполеон|чизкейк/.test(clean(query))){
  const category=FOOD.find(f=>f.name==='торт с кремом');
  devRecord('Резервная приблизительная категория',{query,category:'торт с кремом',nutrition:category});
  return {...category,approximate:true,includesToppings:true,source:'Приблизительная оценка рецептуры'};
 }
 return null;
}
function safeWeight(food,portion,source,meta={}){
 // No local cup/bowl/"usual=100g" mapping may override a model's context-dependent mass.
 const grams=Number(meta?.weight_g);
 const valid=Number.isFinite(grams)&&grams>0&&grams<=10000;
 const result={grams:valid?Math.round(grams*10)/10:0,
  weightReview:valid?'':'Нейросеть не определила вес. Укажите его вручную.',
  volume_ml:Number(meta?.volume_ml)||null,weight_basis:String(meta?.weight_basis||''),
  weight_estimated:meta?.weight_estimated!==false,portion:String(portion||'1 порция')};
 devRecord('Оценка веса нейросетью',{food,portion:result.portion,weight_g:valid?result.grams:null,volume_ml:result.volume_ml,weight_basis:result.weight_basis,estimated:result.weight_estimated,source});
 return result;
}
function makeKnownItem(name,portion,food,source,meta={}){
 const estimate=safeWeight(name,portion,source,meta);
 return {name:capital(name),...estimate,...Object.fromEntries(MACRO_KEYS.map(k=>[k,food?Number(food[k]):null])),source:food?.source||'unknown',nutritionApproximate:!!food?.approximate,nutritionFallback:food?.matched_by==='relaxed_fallback'};
}
function dishFromWhole(name,portion,food,source,meta={}){
 const estimate=safeWeight(name,portion,source,meta),grams=estimate.grams;
 const dish=newDish(capital(name),[],[],{grams,...Object.fromEntries(MACRO_KEYS.map(k=>[k,food[k]*grams/100]))});
 dish.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,Number(food[k])]));dish.nutritionSource=food.source;dish.nutritionApproximate=!!food.approximate;
 if(food.matched_by==='relaxed_fallback')dish.uncertain=['КБЖУ приблизительные: использован наиболее близкий результат справочника. Проверьте значения.'];
 if(food.approximate && !food.matched_by && /JUOR|печен[ьи]\s+треск/i.test(String(food.source||'')))dish.uncertain=['КБЖУ приблизительные: использован справочный аналог консервированной печени трески.'];
 if(!grams)dish.uncertain=[...(dish.uncertain||[]),'Нейросеть не определила вес порции. Укажите вес перед сохранением.'];
 return dish;
}
function detailItemsForPlan(plan,found,source){
 const incoming=[];
 if(plan.kind==='platter'){
  incoming.push(...plan.items);
  if(plan.main && !MEAL_PLATTER_RE.test(plan.main) && !incoming.some(x=>exactEnough(x.name,plan.main)))incoming.unshift({name:plan.main,portion:plan.mainPortion,...plan.mainMeta});
 }
 else if(plan.kind==='recipe'){
  incoming.push({name:plan.main,portion:plan.mainPortion,...plan.mainMeta},...plan.additions);
  for(const x of plan.items)if(!incoming.some(y=>exactEnough(y.name,x.name)))incoming.push(x);
 }else{
  const core=plan.items.filter(x=>x.name&&!(/сметан|соус|майонез/.test(clean(x.name))));
  if(core.length>=2)incoming.push(...core);else incoming.push({name:plan.main,portion:plan.mainPortion,...plan.mainMeta});
  incoming.push(...plan.additions);
 }
 const seen=new Set();const items=[];
 for(const x of incoming){const name=String(x.name||'').trim(),key=itemKey(name);if(!name||seen.has(key))continue;seen.add(key);
  items.push(makeKnownItem(name,x.portion,nutritionFor(name,found,false),source,x));
 }
 if(!items.length)items.push(makeKnownItem(plan.main,plan.mainPortion,nutritionFor(plan.main,found,false),source,plan.mainMeta));
 return items;
}
// New AI-first architecture: the model supplies ALL portion weights and per-100g
// macros. Local code only multiplies per100 * weight/100; directories are for
// an independent comparison AFTER the result has been rendered.
function validAIMacros(per100){
 return !!per100 && MACRO_KEYS.every(k=>
  per100[k]!==undefined&&per100[k]!==null&&Number.isFinite(Number(per100[k]))&&Number(per100[k])>=0);
}
function aiMacroRecord(per100){return Object.fromEntries(MACRO_KEYS.map(k=>[k,Number(per100[k])]))}
function aiComponentDeduplicate(group){
 const seen=new Map(),output=[];
 for(const raw of [...(group.items||[]),...(group.additions||[])]){
  const name=String(raw?.name||'').trim(), key=itemKey(name);
  if(!name||!key)continue;
  const previous=seen.get(key);
  if(previous){
   // Duplicated same component across items/additions represents one portion;
   // prefer the model record with more complete macros and/or weight.
   const value=(x)=>Number(x?.weight_g>0)+Number(validAIMacros(x?.per100));
   if(value(raw)>value(previous)){output[output.indexOf(previous)]=raw;seen.set(key,raw)}
   continue;
  }
  seen.set(key,raw);output.push(raw);
 }
 return output;
}
function aiDishFromResponse(group,source){
 const name=capital(group.name||group.main||'Блюдо');
 const mode=group.mode==='ingredients'?'ingredients':'whole';
 if(mode==='whole'){
  if(!validAIMacros(group.per100))throw Error('ИИ не вернул КБЖУ на 100 г для '+name);
  const grams=Number(group.weight_g??group.main_weight_g);
  if(!(grams>0))throw Error('ИИ не определил массу блюда '+name);
  const p100=aiMacroRecord(group.per100);
  // A whole dish has one single model-per100 estimate; additions are INCLUDED,
  // never appended to the manual record and counted a second time.
  const dish=newDish(name,[],[],{grams,...Object.fromEntries(MACRO_KEYS.map(k=>[k,grams*p100[k]/100]))});
  dish.per100={...p100};dish.nutritionSource='ИИ · оценка блюда на 100 г';
  dish.aiMode='whole';dish.aiWeightEstimated=group.weight_estimated!==false;
  dish.aiSourceType=source;
  devRecord('ИИ: блюдо целиком',{name,source,mode,weight_g:grams,per100:p100,
   portion_kbju:Object.fromEntries(MACRO_KEYS.map(k=>[k,Math.round((grams*p100[k]/100)*100)/100]))});
  return dish;
 }
 const components=aiComponentDeduplicate(group);
 if(!components.length)throw Error('ИИ не вернул состав блюда '+name);
 const items=components.map(c=>{
  if(!validAIMacros(c.per100))throw Error('ИИ не вернул КБЖУ на 100 г для '+c.name);
  if(!(Number(c.weight_g)>0))throw Error('ИИ не определил массу ингредиента '+c.name);
  return makeKnownItem(c.name,c.portion,{...aiMacroRecord(c.per100),source:'ИИ · оценка на 100 г'},source,c);
 });
 const dish=newDish(name,items);dish.aiMode='ingredients';dish.aiSourceType=source;
 const modelWeight=Number(group.weight_g);
 const calculatedWeight=items.reduce((s,x)=>s+Number(x.grams),0);
 if(modelWeight>0 && Math.abs(modelWeight-calculatedWeight)>.5){
   devRecord('ИИ: различие суммарного веса',{name,model_weight_g:modelWeight,components_weight_g:calculatedWeight,
    resolution:'Для суммарного веса и КБЖУ используем сумму весов каждого компонента, указанных ИИ'});
 }
 devRecord('ИИ: состав блюда',{name,source,mode,weight_g:calculatedWeight,
   components:items.map(x=>({name:x.name,weight_g:x.grams,per100:Object.fromEntries(MACRO_KEYS.map(k=>[k,x[k]]))}))});
 return dish;
}
function ratioDifference(ai,reference,k){
 const a=Number(ai),b=Number(reference);
 if(!Number.isFinite(a)||!Number.isFinite(b)||a<0||b<0)return null;
 if(a===0&&b===0)return null;
 if(a===0||b===0){
  // A zero/reference-positive pair cannot be measured by a ratio.
  // Report explicitly rather than claiming an invented multiplier.
  if(Math.max(a,b)<(k==='k'?1:0.5))return null;
  return {factor:null,zero_conflict:true};
 }
 const factor=Math.max(a/b,b/a);
 return factor>1.5?{factor:Math.round(factor*100)/100,zero_conflict:false}:null;
}
async function auditAIPer100(response,source,stillCurrent){
 const dishes=response?.food?.dishes||[];
 const units=[];
 for(const d of dishes){
  if(d.mode==='whole')units.push({name:d.name,level:'готовое блюдо',ai:d.per100});
  else for(const x of aiComponentDeduplicate(d))units.push({name:x.name,level:'ингредиент',ai:x.per100});
 }
 const queries=[...new Set(units.map(x=>x.name))].slice(0,12);
 if(!queries.length)return;
 try{
  const lookup=await batchNutritionQueries(queries);
  if(!stillCurrent())return;
  const mismatches=[],checks=[],missing=[];
  for(const unit of units){
   // ONLY reference check. No assignment to dish/manual/item macros here.
   const candidate=nutritionFor(unit.name,lookup,unit.level==='готовое блюдо');
   if(!candidate||!validAIMacros(candidate.per100||candidate)){
    missing.push({food:unit.name,level:unit.level,reason:'Нет сопоставимого результата справочника'});continue;
   }
   const reference=candidate.per100||candidate;
   const diffs=[];
   for(const k of MACRO_KEYS){
    const delta=ratioDifference(unit.ai?.[k],reference[k],k);
    if(delta)diffs.push({field:macroNames[k],ai_per100:unit.ai[k],reference_per100:reference[k],...delta});
   }
   const record={food:unit.name,level:unit.level,ai_per100:unit.ai,
    reference_per100:aiMacroRecord(reference),source:candidate.source||'Открытый справочник',
    reference_name:candidate.name||'',reference_approximate:!!candidate.approximate,differences:diffs};
   checks.push(record);
   if(diffs.length)mismatches.push(record);
  }
  devRecord('Проверка КБЖУ по справочникам (только диагностика)',{
   source,threshold:'строго больше 1,5 раза по каждому показателю, на 100 г',checked:checks.length,
   differences:mismatches,unverified:missing,
   notice:'Значения ИИ не изменялись. Для нуля и положительного значения отношение не определяется — конфликт указан отдельно.'});
 }catch(e){if(stillCurrent())devRecord('Не удалось проверить КБЖУ по справочникам',{
  source,error:String(e?.message||e),note:'Значения ИИ оставлены без изменений'});}
}
async function resolveCloudDishes(response,source='text'){
 const groups=response?.food?.dishes;
 if(!Array.isArray(groups)||!groups.length)throw Error('ИИ не выделил блюда');
 if(response?.food?.input_mode==='photo_text')devRecord('Фото: распознанный текст',{text:response.food.recognized_text});
 const output=groups.slice(0,8).map(g=>aiDishFromResponse(g,source));
 if(!output.length)throw Error('Нет пригодных данных распознавания');
 return output;
}

function scrollToDish(target){
 requestAnimationFrame(()=>requestAnimationFrame(()=>{
  const elem=target?document.querySelector(`[data-dish="${target}"]`):document.querySelector('.dishCard');
  (elem||document.querySelector('.history'))?.scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
 }));
}

function showPhotoProgress(phase){
 const wrap=$('photoProgressWrap');wrap.hidden=false;
 $('photoAIStatus').textContent='';
 $('photoProgressBar').removeAttribute('value');
 $('photoProgressText').textContent=phase;
}
async function recognizePhoto(){
 const run=++activePhotoRun,bar=$('photoProgressWrap'),status=$('photoAIStatus');
 pendingSource=null;dishes=[];draftsByDish.clear();renderDishes();
 showPhotoProgress('Анализ фотографии…');$('photoDebug').hidden=true;
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),65000);
 try{
  const response=await requestCloudFood({file:photoFile,signal:controller.signal});if(run!==activePhotoRun)return;devRecord('Фото: нейросеть',{food:response.food,usage:response.usage,portion_retry:response.portion_retry,nutrition_retry:response.nutrition_retry,json_recovery:response.json_recovery});
  showPhotoProgress('Расчёт КБЖУ по ответу ИИ…');
  const result=await resolveCloudDishes(response,'photo');if(!result.length)throw Error('Не удалось определить блюда');
  // Do not show intermediate empty ingredients while nutrition calls are still running.
  if(run!==activePhotoRun)return;
  dishes=result;pendingSource='photo';renderDishes();status.textContent='Распознавание завершено';
  void auditAIPer100(response,'photo',()=>run===activePhotoRun);
  if(response.food?.uncertain?.length)$('photoCandidates').textContent='Уточните: '+response.food.uncertain.join('; ');
  else $('photoCandidates').replaceChildren();
  scrollToDish();
 }catch(e){if(run!==activePhotoRun)return;status.textContent='Ошибка распознавания';$('photoDebug').hidden=false;$('photoDebugLog').textContent=String(e.message||e)+'\n'+CLOUD_AI_ENDPOINT;
 }finally{clearTimeout(timeout);if(run===activePhotoRun)bar.hidden=true}
}
$('parseBtn').addEventListener('click',async()=>{
 const text=$('foodText').value.trim();if(!text)return;
 const run=++activeTextRun,btn=$('parseBtn');btn.disabled=true;$('parseBtnLabel').hidden=true;$('parseSpinner').hidden=false;
 pendingSource=null;dishes=[];draftsByDish.clear();renderDishes();
 $('textDebug').hidden=true;$('textAIStatus').textContent='Распознавание — анализ текста…';
 $('textProgressWrap').hidden=false;$('textProgressBar').removeAttribute('value');
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),65000);
 try{
  const response=await requestCloudFood({text,signal:controller.signal});
  if(run!==activeTextRun)return;
  devRecord('Текст: нейросеть',{input:text,food:response.food,coverage:response.coverage,usage:response.usage,nutrition_retry:response.nutrition_retry});
  $('textAIStatus').textContent='Расчёт порций по данным ИИ…';
  const found=await resolveCloudDishes(response,'text');
  if(!found.length)throw Error('ИИ не выделил блюда');
  if(run!==activeTextRun)return;
  $('textAIStatus').textContent='Распознавание — подбор КБЖУ…';
  if(run!==activeTextRun)return;
  dishes=found;pendingSource='text';renderDishes();$('textAIStatus').textContent='';scrollToDish();
  void auditAIPer100(response,'text',()=>run===activeTextRun);
 }catch(e){if(run!==activeTextRun)return;
  $('textDebug').hidden=false;$('textDebugLog').textContent=String(e.message||e);
  devRecord('Ошибка разбора текста',{input:text,error:String(e.message||e)});
  const networkFailed=/^(?:Load failed|Failed to fetch|NetworkError|The network connection was lost)$/i.test(String(e?.message||''));
  if(isChainText(text)){
   $('textAIStatus').textContent='Не удалось получить меню. Повторите запрос.';
   dishes=[];renderDishes();
  }else{
   // No guessed dishes when AI is unavailable: the offline text splitter
   // cannot infer portion weights and may corrupt product names ("г печени").
   // Preserve the original input for an immediate retry instead.
   $('textAIStatus').textContent=networkFailed?'Не удалось соединиться с ИИ. Текст сохранён — проверьте сеть и повторите расчёт.':'Не удалось полностью распознать продукты. Текст сохранён — повторите расчёт.';
   dishes=[];pendingSource=null;renderDishes();
  }
 }finally{clearTimeout(timeout);if(run===activeTextRun){btn.disabled=false;$('parseBtnLabel').hidden=false;$('parseSpinner').hidden=true;$('textProgressWrap').hidden=true}}
});
$('clearPreview').addEventListener('click',()=>{
 activeTextRun++;pendingSource=null;releasePhotoPreview();$('photoInput').value='';
 dishes=[];draftsByDish.clear();renderDishes();$('textAIStatus').textContent='';
 $('foodText').value='';setStatus('');
 devRecord('Очистка текущего ввода',{photo:true,text:true,dishes:true,historyUntouched:true});
});
$('addDishBtn').addEventListener('click',()=>{const d=newDish('');dishes.push(d);renderDishes(d.id);document.querySelector(`[data-dish="${d.id}"]`)?.scrollIntoView({behavior:'smooth',block:'nearest'})});
async function fetchFoodCandidates(q){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),18000);try{const r=await fetch(FOOD_SEARCH_API+'?q='+encodeURIComponent(q),{mode:'cors',cache:'no-store',signal:controller.signal});const raw=await r.text();let data;try{data=JSON.parse(raw)}catch(_){throw Error('Ответ не JSON (HTTP '+r.status+')')}if(!r.ok||data.ok!==true)throw Error(`HTTP ${r.status}: ${data.error||'Поиск недоступен'}`);return data}finally{clearTimeout(timer)}}

$('copyDiagnostic').addEventListener('click',async()=>{
 const out=$('technicalDebugLog').textContent;
 try{await navigator.clipboard.writeText(out);$('technicalCopyStatus').textContent='Скопировано';}
 catch(e){$('technicalCopyStatus').textContent='Не удалось скопировать: '+e.message;}
});
// Select the entire value whenever an editable text/number field is tapped.
// iOS Safari does not support setSelectionRange for input[type=number],
// so numeric macro fields use type=text + inputmode=decimal.
function selectAllEditor(target){
 if(!(target instanceof HTMLInputElement||target instanceof HTMLTextAreaElement))return;
 if(target.type==='file'||target.type==='hidden'||target.readOnly||target.disabled)return;
 const apply=()=>{
  if(document.activeElement!==target)return;
  try{target.select();target.setSelectionRange(0,target.value.length,'none')}catch(_){/* unsupported input */}
 };
 // iOS WebKit may restore the caret *after* pointerup or the synthetic click.
 apply();requestAnimationFrame(()=>{apply();requestAnimationFrame(apply)});setTimeout(apply,50);
}
function selectAllOnTap(e){
 const target=e.target instanceof Element?e.target.closest('input:not([type=file]):not([type=hidden]),textarea'):null;
 if(target)selectAllEditor(target);
}
// iOS Safari/WebKit: keep the currently edited field inside the *visual*
// viewport, not only inside the layout viewport behind the software keyboard.
let activeEditField=null,editScrollScheduled=false;
function isEditableField(el){return el instanceof HTMLInputElement&&el.type!=='file'&&el.type!=='hidden'||el instanceof HTMLTextAreaElement;}
function keepEditorVisible(){
 editScrollScheduled=false;
 const target=activeEditField;
 if(!target||document.activeElement!==target||!target.isConnected)return;
 const vv=window.visualViewport;
 const top=(vv?.offsetTop||0)+12,bottom=(vv?(vv.offsetTop+vv.height):window.innerHeight)-22;
 const rect=target.getBoundingClientRect();
 let delta=0;
 if(rect.bottom>bottom)delta=rect.bottom-bottom;
 else if(rect.top<top)delta=rect.top-top;
 if(Math.abs(delta)>2)window.scrollBy({top:delta,behavior:'instant'});
}
function scheduleEditorVisibility(){if(editScrollScheduled)return;editScrollScheduled=true;requestAnimationFrame(keepEditorVisible);}
document.addEventListener('focusin',e=>{
 selectAllEditor(e.target);
 if(isEditableField(e.target)){
   activeEditField=e.target;scheduleEditorVisibility();
   setTimeout(scheduleEditorVisibility,110);setTimeout(scheduleEditorVisibility,320);
 }
},true);
document.addEventListener('focusout',e=>{if(e.target===activeEditField)activeEditField=null},true);
if(window.visualViewport){
 window.visualViewport.addEventListener('resize',scheduleEditorVisibility,{passive:true});
 window.visualViewport.addEventListener('scroll',scheduleEditorVisibility,{passive:true});
}

document.addEventListener('pointerup',selectAllOnTap,true);
document.addEventListener('touchend',selectAllOnTap,{capture:true,passive:true});
document.addEventListener('click',selectAllOnTap,true);
document.addEventListener('pointerdown',(event)=>{
 const focused=document.activeElement;
 const isTyping=focused&&(focused.tagName==='INPUT'||focused.tagName==='TEXTAREA'||focused.isContentEditable);
 if(isTyping && !event.target.closest('input,textarea,select,[contenteditable="true"]'))focused.blur();
},true);
(async()=>{try{db=await openDB();await refresh();renderDishes()}catch(e){console.error(e);$('textAIStatus').textContent='Ошибка локального хранилища: '+e.message}})();
if('serviceWorker'in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(console.warn));
