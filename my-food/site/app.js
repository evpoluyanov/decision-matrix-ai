'use strict';
// Demonstration per-100-g food estimates. Real labelled products can be added from Open Food Facts.
const FOOD=[
['ÑÐ¾ÑÑ ÑÑÑÐ½ÑÐ¹',280,4,25,9,15,['ÑÐ¾ÑÑ ÑÑÑÐ½ÑÐ¹','ÑÑÑÐ½ÑÐ¹ ÑÐ¾ÑÑ']],
['Ð³ÑÐµÑÐºÐ° Ð²Ð°ÑÐµÐ½Ð°Ñ',110,3.6,1.1,20,180,['Ð³ÑÐµÑÐº','Ð³ÑÐµÑÐ½ÐµÐ²']],
['Ð±ÑÐ»Ð¾ÑÐºÐ° Ð´Ð»Ñ Ð±ÑÑÐ³ÐµÑÐ°',280,9,5,49,70,['Ð±ÑÐ»Ð¾ÑÐº','Ð±ÑÐ»ÐºÐ° Ñ ÐºÑÐ½Ð¶ÑÑÐ¾Ð¼']],
['Ð³Ð¾Ð²ÑÐ¶ÑÑ ÐºÐ¾ÑÐ»ÐµÑÐ°',250,26,15,0,105,['ÐºÐ¾ÑÐ»ÐµÑ','Ð¿Ð°ÑÑÐ¸']],
['ÑÐ°Ð»Ð°Ñ Ð°Ð¹ÑÐ±ÐµÑÐ³',14,0.9,0.1,3,15,['Ð°Ð¹ÑÐ±ÐµÑÐ³','Ð»Ð¸ÑÑÑÑ ÑÐ°Ð»Ð°ÑÐ°','Ð»Ð¸ÑÑ ÑÐ°Ð»Ð°ÑÐ°']],
['ÑÐ°Ð»Ð°Ñ Ð»Ð°ÑÑÐº',15,1.4,0.2,2.9,15,['ÑÐ°Ð»Ð°Ñ Ð»Ð°ÑÑÐº','Ð»Ð°ÑÑÐº','Ð»Ð¸ÑÑÑÑ Ð»Ð°ÑÑÐºÐ°','Ð»Ð¸ÑÑÑÐµÐ² Ð»Ð°ÑÑÐºÐ°','Ð»Ð¸ÑÑ Ð»Ð°ÑÑÐºÐ°']],
['Ð¼Ð°ÑÐ¸Ð½Ð¾Ð²Ð°Ð½Ð½ÑÐ¹ Ð¾Ð³ÑÑÐµÑ',16,0.5,0.2,2.8,25,['Ð¼Ð°ÑÐ¸Ð½Ð¾Ð²Ð°Ð½Ð½ Ð¾Ð³ÑÑ','Ð¼Ð°ÑÐ¸Ð½Ð¾Ð²Ð°Ð½Ð½ÑÐµ Ð¾Ð³ÑÑ','Ð¿Ð¸ÐºÐ»']],
['ÐºÑÐ°ÑÐ½ÑÐ¹ Ð»ÑÐº',40,1.1,0.1,9.3,20,['ÐºÑÐ°ÑÐ½ÑÐ¹ Ð»ÑÐº','Ð»ÑÐº ÐºÑÐ°ÑÐ½ÑÐ¹','Ð»ÑÐºÐ¾Ð²ÑÐµ ÐºÐ¾Ð»ÑÑÐ°','Ð»ÑÐº']],

// Approximate comparable Napoleon pastry from Norwegian food composition table (per 100 g).
['ÑÐ¾ÑÑ Ð½Ð°Ð¿Ð¾Ð»ÐµÐ¾Ð½',297,5.3,14.4,35.9,120,['Ð½Ð°Ð¿Ð¾Ð»ÐµÐ¾Ð½']],
// Illustrative honey cake recipe: 338.2 kcal, P 6.4, F 11.7, C 51.7 per 100g. Actual recipes vary.
['ÑÐ¾ÑÑ Ð¼ÐµÐ´Ð¾Ð²Ð¸Ðº',338.2,6.4,11.7,51.7,110,['Ð¼ÐµÐ´Ð¾Ð²Ð¸Ðº','Ð¼ÐµÐ´Ð¾Ð²ÑÐ¸ ÑÐ¾ÑÑ','Ð¼ÐµÐ´Ð¾Ð²ÑÐ¹ ÑÐ¾ÑÑ','ÑÐ¾ÑÑ Ð¼ÐµÐ´Ð¾Ð²ÑÐ¹']],
// Conservative editable fallbacks only when all external food databases fail.
// Example recipe estimate (not an official USDA record): ~390 kcal/100g, P5 F20 C48.
['ÑÐ¾ÑÑ Ñ ÐºÑÐµÐ¼Ð¾Ð¼',390,5,20,48,110,['ÑÐ¾ÑÑ Ñ ÐºÑÐµÐ¼Ð¾Ð¼','ÑÐ¾ÑÑ ÑÐ¾ Ð²Ð·Ð±Ð¸ÑÑÐ¼Ð¸ ÑÐ»Ð¸Ð²ÐºÐ°Ð¼Ð¸','Ð±Ð¸ÑÐºÐ²Ð¸ÑÐ½ÑÐ¹ ÑÐ¾ÑÑ Ñ ÐºÑÐµÐ¼Ð¾Ð¼','Ð±Ð¸ÑÐºÐ²Ð¸ÑÐ½ÑÐ¹ ÑÐ¾ÑÑ ÑÐ¾ ÑÐ»Ð¸Ð²ÐºÐ°Ð¼Ð¸']],
// USDA SR Legacy FDC 172706 sponge cake (without frosting), per 100g.
['Ð±Ð¸ÑÐºÐ²Ð¸Ñ',290,5.4,2.7,61,100,['Ð±Ð¸ÑÐºÐ²Ð¸Ñ','Ð±Ð¸ÑÐºÐ²Ð¸ÑÐ½ÑÐ¹ ÐºÐ¾ÑÐ¶']],
['Ð²Ð·Ð±Ð¸ÑÑÐµ ÑÐ»Ð¸Ð²ÐºÐ¸',257,3,25,8,25,['Ð²Ð·Ð±Ð¸ÑÑÐµ ÑÐ»Ð¸Ð²ÐºÐ¸','Ð²Ð·Ð±Ð¸ÑÑÑ ÑÐ»Ð¸Ð²Ð¾Ðº']],
['ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÑÐ¾ÑÑ',320,2,9,58,15,['ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÑÐ¾ÑÑ']],
['ÑÐ¸Ñ Ð²Ð°ÑÐµÐ½ÑÐ¹',130,2.5,0.3,28.2,180,['ÑÐ¸Ñ']],
['ÐºÑÑÐ¸Ð½Ð°Ñ Ð³ÑÑÐ´ÐºÐ°',165,31,3.6,0,150,['ÐºÑÑÐ¸Ñ','ÐºÑÑÐ¸Ð½','Ð³ÑÑÐ´Ðº']],
['ÑÐ¹ÑÐ¾',143,12.6,9.5,0.7,55,['ÑÐ¹Ñ','ÑÐ¹ÑÐ°','ÑÐ¸Ñ','ÑÐ¹ÑÐ¾']],
// USDA SR Legacy FDC 173423: egg, whole, cooked, fried (per 100 g, incl. typical cooking fat).
['ÑÐ¹ÑÐ¾ Ð¶Ð°ÑÐµÐ½Ð¾Ðµ',196,13.61,14.84,0.83,55,['ÑÐ¸ÑÐ½Ð¸ÑÐ°','Ð³Ð»Ð°Ð·ÑÐ½ÑÑ','Ð¶Ð°ÑÐµÐ½ÑÐµ ÑÐ¹ÑÐ°','Ð¶Ð°ÑÐµÐ½Ð¾Ðµ ÑÐ¹ÑÐ¾','ÑÐ¹ÑÐ¾ Ð¶Ð°ÑÐµÐ½Ð¾Ðµ']],
['ÑÐ±Ð»Ð¾ÐºÐ¾',52,0.3,0.2,14,160,['ÑÐ±Ð»Ð¾Ðº']],
['Ð±Ð°Ð½Ð°Ð½',89,1.1,0.3,23,120,['Ð±Ð°Ð½Ð°Ð½']],
['Ð¾Ð²ÑÑÐ½ÐºÐ° Ð²Ð°ÑÐµÐ½Ð°Ñ',71,2.5,1.5,12,200,['Ð¾Ð²ÑÑÐ½']],
['ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð²Ð°ÑÐµÐ½ÑÐ¹',87,1.9,0.1,20.1,180,['ÐºÐ°ÑÑÐ¾Ñ','ÐºÐ°ÑÑÐ¾Ñ']],
['Ð¾Ð³ÑÑÐµÑ',15,0.7,0.1,3.6,120,['Ð¾Ð³ÑÑ']],
['Ð¿Ð¾Ð¼Ð¸Ð´Ð¾Ñ',18,0.9,0.2,3.9,120,['Ð¿Ð¾Ð¼Ð¸Ð´','ÑÐ¾Ð¼Ð°Ñ']],
['ÑÐ»ÐµÐ±',250,8,3,49,35,['ÑÐ»ÐµÐ±','Ð±Ð°ÑÐ¾Ð½','ÑÐ¾ÑÑ']],
['ÑÑÑ',350,25,27,2,30,['ÑÑÑ']],
['Ð¼Ð¾Ð»Ð¾ÐºÐ¾',60,3.2,3.2,4.8,200,['Ð¼Ð¾Ð»Ð¾Ðº']],
['ÐºÐµÑÐ¸Ñ',53,3,2.5,4,200,['ÐºÐµÑÐ¸Ñ']],
['ÑÐ²Ð¾ÑÐ¾Ð³',121,17,5,1.8,180,['ÑÐ²Ð¾ÑÐ¾Ð³']],
['Ð¹Ð¾Ð³ÑÑÑ Ð½Ð°ÑÑÑÐ°Ð»ÑÐ½ÑÐ¹',65,4,3,5,150,['Ð¹Ð¾Ð³ÑÑÑ']],
['Ð¾ÑÐµÑÐ¸',607,20,54,16,30,['Ð¾ÑÐµÑ']],
['ÑÐ»Ð¸Ð²Ð¾ÑÐ½Ð¾Ðµ Ð¼Ð°ÑÐ»Ð¾',748,0.5,82.5,0.8,10,['ÑÐ»Ð¸Ð²Ð¾ÑÐ½','Ð¼Ð°ÑÐ»Ð¾ ÑÐ»Ð¸Ð²']],
['ÑÐ°ÑÑÐ¸ÑÐµÐ»ÑÐ½Ð¾Ðµ Ð¼Ð°ÑÐ»Ð¾',900,0,100,0,10,['Ð¼Ð°ÑÐ»','Ð¾Ð»Ð¸Ð²ÐºÐ¾Ð²']],
['ÑÐ°ÑÐ°Ñ',400,0,0,100,5,['ÑÐ°ÑÐ°Ñ']],
['Ð³Ð¾Ð²ÑÐ´Ð¸Ð½Ð° Ð¿ÑÐ¸Ð³Ð¾ÑÐ¾Ð²Ð»ÐµÐ½Ð½Ð°Ñ',250,26,15,0,150,['Ð³Ð¾Ð²ÑÐ´Ð¸Ð½']],
['ÑÐ²Ð¸Ð½Ð¸Ð½Ð° Ð¿ÑÐ¸Ð³Ð¾ÑÐ¾Ð²Ð»ÐµÐ½Ð½Ð°Ñ',290,25,21,0,150,['ÑÐ²Ð¸Ð½Ð¸Ð½']],
['ÑÑÐ±Ð° Ð¿ÑÐ¸Ð³Ð¾ÑÐ¾Ð²Ð»ÐµÐ½Ð½Ð°Ñ',130,23,4,0,150,['ÑÑÐ±','ÑÑÐµÑÐº','ÑÐµÐº']],
['Ð³ÑÐµÑÐµÑÐºÐ¸Ð¹ ÑÐ°Ð»Ð°Ñ',120,3.8,9.4,4.5,180,['Ð³ÑÐµÑÐµÑÐº ÑÐ°Ð»Ð°Ñ']],
['Ð¾Ð²Ð¾ÑÐ½Ð¾Ð¹ ÑÐ°Ð»Ð°Ñ Ð±ÐµÐ· Ð·Ð°Ð¿ÑÐ°Ð²ÐºÐ¸',25,1,0.3,4.5,150,['ÑÐ°Ð»Ð°Ñ']],
['Ð¼Ð°ÐºÐ°ÑÐ¾Ð½Ñ Ð²Ð°ÑÐµÐ½ÑÐµ',157,5.8,0.9,30.9,180,['Ð¼Ð°ÐºÐ°ÑÐ¾Ð½','Ð¿Ð°ÑÑ']],
['Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½',47,0.9,0.1,11.8,150,['Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½']],
['ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ ÑÑÐ¸',312,3.4,15,41,100,['ÑÑÐ¸']],
['ÐºÑÑÐ¸Ð½ÑÐµ Ð½Ð°Ð³Ð³ÐµÑÑÑ',295,15,20,13,120,['Ð½Ð°Ð³Ð³ÐµÑ']],
['ÐºÐ¾ÑÐµ ÑÐµÑÐ½ÑÐ¹',2,0.1,0,0,200,['ÐºÐ¾ÑÐµ']],
['Ð¿Ð¸ÑÑÐ°',260,11,10,34,180,['Ð¿Ð¸ÑÑ']],
['Ð±ÑÑÐ³ÐµÑ',260,14,12,26,180,['Ð±ÑÑÐ³ÐµÑ','Ð³Ð°Ð¼Ð±ÑÑÐ³ÐµÑ']],
['ÑÑÑÐ½Ð¸ÐºÐ¸',230,13,12,20,150,['ÑÑÑÐ½Ð¸Ðº']],
['ÑÑÐ¿',70,3,4,5,250,['ÑÑÐ¿']],
['Ð¿ÐµÐ»ÑÐ¼ÐµÐ½Ð¸',270,11,13,27,180,['Ð¿ÐµÐ»ÑÐ¼ÐµÐ½']],
['ÑÑÑÐ¸',145,6,3,23,150,['ÑÑÑÐ¸','ÑÐ¾Ð»Ð»']],
['ÑÑÐµÐ¹Ðº',250,26,16,0,180,['ÑÑÐµÐ¹Ðº']],
['Ð»Ð¾ÑÐ¾ÑÑ',208,20,13,0,150,['Ð»Ð¾ÑÐ¾Ñ','ÑÐµÐ¼Ð³Ð°']],
['ÑÐµÐ·Ð°ÑÑ ÑÐ°Ð»Ð°Ñ',180,11,12,6,180,['ÑÐµÐ·Ð°ÑÑ']],
['Ð¿Ð°ÑÑÐ° ÐºÐ°ÑÐ±Ð¾Ð½Ð°ÑÐ°',260,12,13,24,180,['ÐºÐ°ÑÐ±Ð¾Ð½Ð°Ñ']],
['ÑÐ°Ð¹ Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°',1,0,0,0,200,['ÑÐ°Ð¹']]
].map(([name,k,p,f,c,portion,aliases])=>({name,k,p,f,c,portion,aliases}));

const $=id=>document.getElementById(id);
const clean=s=>String(s||'').toLowerCase().replaceAll('Ñ','Ðµ').replace(/[.!?]/g,'').trim();
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
const macroLabels={k:'Ð',p:'Ð',f:'Ð',c:'Ð£'};
const macroNames={k:'ÐÐ°Ð»Ð¾ÑÐ¸Ð¸',p:'ÐÐµÐ»ÐºÐ¸',f:'ÐÐ¸ÑÑ',c:'Ð£Ð³Ð»ÐµÐ²Ð¾Ð´Ñ'};
function nutritionField(label,value,step,klass='',idTag=''){
 const wrap=el('label','editField '+klass);wrap.append(el('span','',label));
 const input=el('input');input.type='text';input.inputMode='decimal';input.autocomplete='off';input.setAttribute('enterkeyhint','done');input.dataset.numeric='true';input.dataset.max=label==='ÐÐµÑ, Ð³'?'10000':'100000';input.value=value==null?'':toDisplay(value);if(idTag)input.id=idTag;wrap.append(input);return {wrap,input};
}
function newDish(name='ÐÐ»ÑÐ´Ð¾',items=[],unresolved=[],manual=null){return {id:id(),name:capital(name),items:cloneItems(items),manual:manual?{...emptyTotals(),...manual}:emptyTotals(),per100:null,unresolved:unresolved.map(x=>({...x,id:id()}))}}
function dishById(key){return dishes.find(d=>d.id===key)}
function itemKey(name){return clean(name).replace(/[^\p{L}\p{N}]+/gu,' ').trim()}
function fallbackDishName(items,label=''){
 if(label)return capital(label);
 if(items.length===1)return capital(items[0].name);
 const names=items.map(x=>clean(x.name));
 if(names.some(n=>/Ð±ÑÐ»Ð¾Ñ|ÐºÐ¾ÑÐ»ÐµÑ|Ð±ÑÑÐ³ÐµÑ/.test(n)))return 'ÐÑÑÐ³ÐµÑ';
 return items.length?'ÐÐ»ÑÐ´Ð¾':'ÐÐ¾Ð²Ð¾Ðµ Ð±Ð»ÑÐ´Ð¾';
}
// Return an estimate *and* a warning when a photo implies an implausible mass.
function parseOffline(text){
 const chunks=String(text).replace(/(\d),(\d)/g,'$1.$2').split(/[,;\n]+|\s+Ð¸\s+/i).map(x=>x.trim()).filter(Boolean);
 const out=[];
 for(const chunk of chunks){const food=findFood(chunk);if(food){const grams=0; const item={name:capital(food.name),grams,k:food.k,p:food.p,f:food.f,c:food.c,weightReview:grams?'':'ÐÐµÑ Ð¾ÑÐµÐ½ÐºÐ¸ Ð¼Ð°ÑÑÑ: Ð½ÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½ÐµÐ´Ð¾ÑÑÑÐ¿Ð½Ð°.'};out.push(newDish(capital(chunk.replace(/^\d+\s*/,'')||food.name),[item]))}
  else out.push(newDish(capital(chunk),[{name:capital(chunk),grams:0,k:null,p:null,f:null,c:null,source:'unknown'}]));}
 return out;
}
function openDB(){return new Promise((resolve,reject)=>{const req=indexedDB.open('my-food-diary-v1',2);req.onupgradeneeded=()=>{const db=req.result;if(!db.objectStoreNames.contains('entries'))db.createObjectStore('entries',{keyPath:'id'});if(!db.objectStoreNames.contains('favorites'))db.createObjectStore('favorites',{keyPath:'id'})};req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
function all(store){return new Promise((resolve,reject)=>{const q=db.transaction(store,'readonly').objectStore(store).getAll();q.onsuccess=()=>resolve(q.result);q.onerror=()=>reject(q.error)})}
function put(store,data){return new Promise((resolve,reject)=>{const tx=db.transaction(store,'readwrite');tx.objectStore(store).put(data);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)})}
function erase(store,key){return new Promise((resolve,reject)=>{const tx=db.transaction(store,'readwrite');tx.objectStore(store).delete(key);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error)})}
function summaryLabel(items){return (items||[]).slice(0,3).map(x=>capital(x.name)).join(' + ')||'ÐÐ»ÑÐ´Ð¾'}
function favoriteKey(d){return JSON.stringify([itemKey(d.name||''),(d.items||[]).map(x=>[itemKey(x.name),Number(x.grams)||0,...MACRO_KEYS.map(k=>numInput(x[k]))]),d.items?.length?null:totalsFor(d)])}
function favoriteFor(d){return favoritesCache.find(f=>favoriteKey(f)===favoriteKey(d))}
async function toggleFavorite(d){
 if(!d.items.length && !(d.manual?.grams>0))return;
 const old=favoriteFor(d);
 try{if(old)await erase('favorites',old.id);else await put('favorites',{id:id(),name:d.name,items:cloneItems(d.items),manual:d.items.length?null:{...d.manual},created:new Date().toISOString()});await refresh();refreshFavoriteStars()}catch(e){setStatus('ÐÑÐ¸Ð±ÐºÐ° Ð¸Ð·Ð±ÑÐ°Ð½Ð½Ð¾Ð³Ð¾: '+e.message)}
}
function refreshFavoriteStars(){for(const d of dishes){const b=document.querySelector(`[data-dish-star="${d.id}"]`);if(!b)continue;const fav=!!favoriteFor(d);b.textContent=fav?'â':'â';b.setAttribute('aria-pressed',String(fav));b.title=fav?'Ð£Ð±ÑÐ°ÑÑ Ð¸Ð· Ð¸Ð·Ð±ÑÐ°Ð½Ð½Ð¾Ð³Ð¾':'Ð Ð¸Ð·Ð±ÑÐ°Ð½Ð½Ð¾Ðµ';b.setAttribute('aria-label',b.title);b.classList.toggle('favoriteActive',fav)}
 $('tabFaves').classList.toggle('favoriteActive',dishes.some(d=>!!favoriteFor(d)))}
function setStatus(txt=''){$('operationStatus').textContent=txt}
function hasMissingNutrition(i){return MACRO_KEYS.some(k=>i[k]===null || i[k]===undefined)}
function canSaveDish(d){return !!d.name.trim() && (d.items.length?d.items.every(i=>Number(i.grams)>0&&Number.isFinite(+i.grams)&&!hasMissingNutrition(i)):Number(d.manual?.grams)>0)}
function updateDishSummary(d){const elTotal=document.querySelector(`[data-dish-total="${d.id}"]`);if(!elTotal)return;const t=totalsFor(d);
 elTotal.textContent=`ÐÑÐ¾Ð³Ð¾ Â· ÐÐµÑ: ${one(t.grams)} Ð³ Â· Ð: ${num(t.k)} Â· Ð: ${one(t.p)} Â· Ð: ${one(t.f)} Â· Ð£: ${one(t.c)}`;
 const summary=document.querySelector(`[data-dish-warning="${d.id}"]`);
 if(summary){const noWeight=d.items.some(i=>!(Number(i.grams)>0));const unknown=d.items.some(hasMissingNutrition);
  summary.textContent=noWeight?'ÐÐ°Ð¿Ð¾Ð»Ð½Ð¸ÑÐµ Ð²ÐµÑ ÐºÐ°Ð¶Ð´Ð¾Ð³Ð¾ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½ÑÐ°.':unknown?'Ð§Ð°ÑÑÑ ÐÐÐÐ£ Ð½Ðµ Ð¾Ð¿ÑÐµÐ´ÐµÐ»ÐµÐ½Ð° â Ð¸ÑÐ¾Ð³ Ð¼Ð¾Ð¶ÐµÑ Ð±ÑÑÑ Ð½ÐµÐ¿Ð¾Ð»Ð½ÑÐ¼. ÐÑÐ¾Ð²ÐµÑÑÑÐµ ÐºÑÐ°ÑÐ½ÑÐµ Ð¿Ð¾Ð»Ñ.':'';
 }
 const btnSave=document.querySelector(`[data-dish-save="${d.id}"]`);if(btnSave)btnSave.disabled=!canSaveDish(d);
}
function removeUnknown(d,u){d.unresolved=d.unresolved.filter(x=>x.id!==u.id);renderDishes()}
function editFieldGroup(item,d){
 const block=el('div','ingredientRow');const headline=el('div','ingredientHeading');
 const name=el('input','ingredientNameInput');name.type='text';name.value=capital(item.name);name.setAttribute('aria-label','ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½ÑÐ°');
 name.addEventListener('input',()=>{item.name=name.value;item.userEdited=true;refreshFavoriteStars()});
 const del=button('Ã','iconAction red',()=>{d.items=d.items.filter(x=>x.id!==item.id);if(!d.items.length)d.manual=emptyTotals();renderDishes()});del.setAttribute('aria-label','Ð£Ð´Ð°Ð»Ð¸ÑÑ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½Ñ');headline.append(name,del);block.append(headline);
 const fields=el('div','nutriEditRow'),weight=nutritionField('ÐÐµÑ, Ð³',item.grams>0?item.grams:null,10,'weightEdit'),macroRow=el('div','macroFields');fields.append(weight.wrap);const m={};
 const refreshMissing=()=>{weight.input.classList.toggle('missingData',!(Number(item.grams)>0));
  for(const k of MACRO_KEYS)m[k].classList.toggle('missingData',item[k]===null||item[k]===undefined);
 };
 for(const k of MACRO_KEYS){const f=nutritionField(macroLabels[k],Number(item.grams)>0&&item[k]!=null?portionVal(item,k):null,5);f.input.setAttribute('aria-label',`${macroNames[k]} Ð´Ð»Ñ ${item.name}`);
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
 const panel=el('div','wholeDishEditor'),line=el('div','nutriEditRow'),weight=nutritionField('ÐÐµÑ, Ð³',d.manual.grams>0?d.manual.grams:null,10,'weightEdit'),group=el('div','macroFields'),fields={};
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
 draft.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,Math.max(0,Number(candidate[k])||0)]));draft.ready=true;draft.source=candidate.source||'';draft.status='ÐÐ°Ð¹Ð´ÐµÐ½Ð¾: '+(candidate.source||'ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº')+'. ÐÑÐ¾Ð²ÐµÑÑÑÐµ Ð·Ð½Ð°ÑÐµÐ½Ð¸Ñ.';
 renderDishes();
}
async function lookupDraft(d){const draft=getDraft(d);const name=draft.name.trim();if(name.length<2){draft.status='ÐÐ²ÐµÐ´Ð¸ÑÐµ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½ÑÐ°';renderDishes();return}
 const local=findFood(name);draft.ready=true;if(local){draft.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,local[k]]));draft.source='ÐÐ¾ÐºÐ°Ð»ÑÐ½ÑÐ¹ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº';draft.status='ÐÑÐµÐ´Ð²Ð°ÑÐ¸ÑÐµÐ»ÑÐ½Ð°Ñ Ð¾ÑÐµÐ½ÐºÐ°. ÐÑÐ¾Ð²ÐµÑÑÐµÐ¼ Ð²Ð½ÐµÑÐ½ÑÑ Ð±Ð°Ð·Ñâ¦'}
 else{draft.per100={k:null,p:null,f:null,c:null};draft.status='ÐÑÐµÐ¼ Ð¿Ð¸ÑÐµÐ²ÑÑ ÑÐµÐ½Ð½Ð¾ÑÑÑâ¦'}
 draft.options=[];draft.busy=true;renderDishes();
 try{const data=await fetchFoodCandidates(name);if(draft.name.trim()!==name)return;draft.options=(data.items||[]).slice(0,6);draft.status=(draft.options.length?'ÐÐ°Ð¹Ð´ÐµÐ½Ñ Ð²Ð°ÑÐ¸Ð°Ð½ÑÑ; Ð²ÑÐ±ÐµÑÐ¸ÑÐµ Ð¿Ð¾Ð´ÑÐ¾Ð´ÑÑÐ¸Ð¹ Ð¸Ð»Ð¸ Ð¸Ð·Ð¼ÐµÐ½Ð¸ÑÐµ Ð·Ð½Ð°ÑÐµÐ½Ð¸Ñ.':'ÐÐ½ÐµÑÐ½ÑÑ Ð±Ð°Ð·Ð° Ð½Ðµ Ð½Ð°ÑÐ»Ð° ÑÐ¾Ð²Ð¿Ð°Ð´ÐµÐ½Ð¸Ðµ.')+(data.sources?.usda?' USDA Ð´Ð¾ÑÑÑÐ¿Ð½Ð°.':'');
  if(!local&&draft.options.length) {const top=draft.options[0];draft.per100=Object.fromEntries(MACRO_KEYS.map(k=>[k,Math.max(0,Number(top[k])||0)]));draft.source=top.source;}
 }catch(e){draft.status='ÐÐ¾Ð¸ÑÐº Ð½ÐµÐ´Ð¾ÑÑÑÐ¿ÐµÐ½: '+String(e.message||e)+(local?' Â· ÐÑÑÐ°Ð²Ð»ÐµÐ½Ð° Ð»Ð¾ÐºÐ°Ð»ÑÐ½Ð°Ñ Ð¾ÑÐµÐ½ÐºÐ°.':'')}
 finally{draft.busy=false;renderDishes()}
}
function addDraftPanel(d){const draft=getDraft(d),panel=el('div','addIngredientPanel');panel.append(el('h4','','ÐÐ¾Ð±Ð°Ð²Ð¸ÑÑ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½Ñ'));
 const nameLabel=el('label','inlineLabel','ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½ÑÐ°'),name=el('input','addIngredientName');name.type='text';name.value=draft.name;name.placeholder='ÐÐ°Ð¿ÑÐ¸Ð¼ÐµÑ, ÑÐ¾ÑÑ ÑÑÑÐ½ÑÐ¹';name.autocomplete='off';
 name.addEventListener('input',()=>{if(draft.name!==name.value){draft.name=name.value;draft.per100={k:null,p:null,f:null,c:null};draft.options=[];draft.status='';draft.source='';draft.ready=false;
  const region=panel.querySelector('.draftResults');if(region)region.hidden=true;
 }});nameLabel.append(name);panel.append(nameLabel);
 const draftActions=el('div','draftActionRow');const find=button(draft.busy?'ÐÐ¾Ð¸ÑÐºâ¦':'ÐÐ°Ð¹ÑÐ¸','secondary addSearchButton',()=>lookupDraft(d));find.disabled=draft.busy;draftActions.append(find);
 if(draft.ready||draft.name){const clear=button('Ã','iconAction red draftClear',()=>{draftsByDish.delete(d.id);renderDishes();});clear.setAttribute('aria-label','ÐÑÐ¸ÑÑÐ¸ÑÑ Ð½Ð°Ð¹Ð´ÐµÐ½Ð½ÑÐ¹ Ð¸Ð½Ð³ÑÐµÐ´Ð¸ÐµÐ½Ñ');draftActions.append(clear);}
 panel.append(draftActions);
 const region=el('div','draftResults');region.hidden=!draft.ready;
 if(draft.status)region.append(el('div','addIngredientStatus',draft.status));
 if(draft.options.length){const suggestions=el('div','addSuggestions');for(const candidate of draft.options){const ru=capital(candidate.name_ru||candidate.name);const wrap=el('div','addOptionText');wrap.append(el('strong','',ru));if(candidate.source==='USDA FoodData Central')wrap.append(el('small','resultEnglish',candidate.name));wrap.append(el('small','',`${candidate.source} Â· ${num(candidate.k)} ÐºÐºÐ°Ð» / 100 Ð³`));suggestions.append(button('', 'addSuggestion',()=>applyCandidateToDraft(d,candidate)));suggestions.lastChild.append(wrap)}region.append(suggestions)}
 const fields=el('div','addItemNutrition'),w=nutritionField('ÐÐµÑ, Ð³',draft.grams,10,'weightEdit'),macros=el('div','macroFields');w.input.dataset.addWeight='1';fields.append(w.wrap);
 w.input.addEventListener('input',()=>{const val=w.input.value===''?0:Number(w.input.value.replace(',','.'));if(!Number.isFinite(val)||val<0||val>10000)return;draft.grams=val;
  for(const k of MACRO_KEYS){const input=region.querySelector(`[data-add-macro="${k}"]`);if(input)input.value=draft.per100[k]===null?'0':toDisplay(val*draft.per100[k]/100)}
  refreshDraftMissing();});
 for(const k of MACRO_KEYS){const v=draft.per100[k]===null?0:draft.grams*draft.per100[k]/100;const f=nutritionField(macroLabels[k],v,5);f.input.dataset.addMacro=k;
  f.input.addEventListener('input',()=>{const val=f.input.value===''?0:Number(f.input.value.replace(',','.'));if(!Number.isFinite(val)||val<0)return;
   if(draft.grams>0)draft.per100[k]=val*100/draft.grams;else f.input.value='0';refreshDraftMissing()});macros.append(f.wrap)}
 fields.append(macros);region.append(fields);
 const add=button('ÐÐ¾Ð±Ð°Ð²Ð¸ÑÑ','primary addIngredientSubmit',()=>{
  if(!draft.name.trim()||!(draft.grams>0)||draft.grams>10000){draft.status='Ð£ÐºÐ°Ð¶Ð¸ÑÐµ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¸ Ð²ÐµÑ Ð±Ð¾Ð»ÑÑÐµ Ð½ÑÐ»Ñ.';const msg=region.querySelector('.addIngredientStatus');if(msg)msg.textContent=draft.status;else region.prepend(el('div','addIngredientStatus',draft.status));return}
  const ingredient={id:id(),name:capital(draft.name),grams:draft.grams,...Object.fromEntries(MACRO_KEYS.map(k=>[k,draft.per100[k]])),source:draft.source||'unknown'};
  if(!d.items.length)d.manual=emptyTotals();d.items.push(ingredient);draftsByDish.delete(d.id);renderDishes();
 });region.append(add);panel.append(region);
 function refreshDraftMissing(){w.input.classList.toggle('missingData',!(draft.grams>0));for(const k of MACRO_KEYS){const field=region.querySelector(`[data-add-macro="${k}"]`);if(field)field.classList.toggle('missingData',draft.per100[k]===null)}}refreshDraftMissing();
 return panel;
}
function renderDishes(focusDishId=null){const holder=$('dishesList');holder.replaceChildren();$('preview').hidden=!dishes.length;
 for(const d of dishes){const card=el('article','dishCard');card.dataset.dish=d.id;
  const nameHeading=el('div','dishHeading'),label=el('label','dishLabel','ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð±Ð»ÑÐ´Ð°');const dishName=el('input','dishNameInput');dishName.type='text';dishName.value=d.name;dishName.placeholder='ÐÐ²ÐµÐ´Ð¸ÑÐµ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð±Ð»ÑÐ´Ð°';dishName.maxLength=100;
  dishName.addEventListener('input',()=>{d.name=dishName.value;updateDishSummary(d);refreshFavoriteStars()});label.append(dishName);
  const remove=button('Ã','iconAction red',()=>{dishes=dishes.filter(x=>x.id!==d.id);draftsByDish.delete(d.id);renderDishes()});remove.setAttribute('aria-label','Ð£Ð±ÑÐ°ÑÑ Ð±Ð»ÑÐ´Ð¾');nameHeading.append(label,remove);card.append(nameHeading);
  const totals=el('div','dishTotals');totals.dataset.dishTotal=d.id;card.append(totals);
  const warning=el('small','dishWarning');warning.dataset.dishWarning=d.id;card.append(warning);
  if(d.items.length){const itemsHolder=el('div','dishIngredients');for(const item of d.items)itemsHolder.append(editFieldGroup(item,d));card.append(itemsHolder)}
  else card.append(editWholeDish(d));
  if(d.uncertain?.length){const p=el('p','hint','Ð¢ÑÐµÐ±ÑÐµÑ ÑÑÐ¾ÑÐ½ÐµÐ½Ð¸Ñ: '+d.uncertain.join('; '));card.append(p)}
  card.append(addDraftPanel(d));
  const actions=el('div','dishActions'),star=button('â','iconFavorite',()=>toggleFavorite(d)),save=button('Ð¡Ð¾ÑÑÐ°Ð½Ð¸ÑÑ','primary',()=>saveDish(d));star.dataset.dishStar=d.id;save.dataset.dishSave=d.id;actions.append(star,save);card.append(actions);holder.append(card);updateDishSummary(d);
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
 catch(e){setStatus('ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ ÑÐ¾ÑÑÐ°Ð½Ð¸ÑÑ: '+e.message)}
}
function renderDateStrip(){const strip=$('dateStrip');strip.replaceChildren();const more=button('Â·Â·Â·','dateMore',()=>{const wrap=$('calendarWrap');wrap.hidden=!wrap.hidden;calendarBase=dateFromKey(selectedDay);renderCalendar()});strip.append(more);
 for(let ago=6;ago>=0;ago--){const d=new Date();d.setHours(12,0,0,0);d.setDate(d.getDate()-ago);const key=dayKey(d);
  const tag=d.toLocaleDateString('ru-RU',{weekday:'short'}).replace('.','').slice(0,2).replace(/^./,x=>x.toUpperCase());const b=el('button','dateChip'+(key===selectedDay?' chosen':''));b.type='button';b.append(el('small','',tag),el('strong','',String(d.getDate())));b.addEventListener('click',()=>{selectedDay=key;$('calendarWrap').hidden=true;refresh()});strip.append(b)}}
function renderCalendar(){const grid=$('calendarGrid');grid.replaceChildren();const base=new Date(calendarBase.getFullYear(),calendarBase.getMonth(),1);$('calendarMonth').textContent=base.toLocaleDateString('ru-RU',{month:'long',year:'numeric'});
 for(const day of ['ÐÐ½','ÐÑ','Ð¡Ñ','Ð§Ñ','ÐÑ','Ð¡Ð±','ÐÑ'])grid.append(el('span','calendarWeek',day));const start=(base.getDay()+6)%7;for(let i=0;i<start;i++)grid.append(el('span','calendarBlank',''));
 const end=new Date(base.getFullYear(),base.getMonth()+1,0).getDate();for(let i=1;i<=end;i++){const key=dayKey(new Date(base.getFullYear(),base.getMonth(),i));const b=button(String(i),'calendarDay'+(key===selectedDay?' chosen':''),()=>{selectedDay=key;$('calendarWrap').hidden=true;refresh()});b.disabled=key>today();grid.append(b)}}
$('calendarPrev').addEventListener('click',()=>{calendarBase.setMonth(calendarBase.getMonth()-1);renderCalendar()});$('calendarNext').addEventListener('click',()=>{calendarBase.setMonth(calendarBase.getMonth()+1);renderCalendar()});
function renderDailyTotals(entries){const tday=entries.filter(e=>(e.date||String(e.created||'').slice(0,10))===today());const t=sumEntries(tday);
 $('todayLabel').textContent=dayText(today());$('mealsCount').textContent='ÐÐ°Ð¿Ð¸ÑÐµÐ¹: '+tday.length;$('kcal').textContent=num(t.k);$('prot').textContent=one(t.p)+' Ð³';$('fat').textContent=one(t.f)+' Ð³';$('carb').textContent=one(t.c)+' Ð³';
 const ratio=t.k/NORMS.k;$('calPercent').textContent=Math.round(ratio*100)+'%';$('calRing').style.setProperty('--progress',Math.min(100,ratio*100)+'%');$('calRing').style.setProperty('--ringColor',ratio>=.95?'#e64737':ratio>=.75?'#ef9c28':'#298c20');$('calRing').setAttribute('aria-valuenow',String(num(t.k)));
 for(const [key,id] of [['p','protMeter'],['f','fatMeter'],['c','carbMeter']]){const r=t[key]/NORMS[key],bar=$(id);bar.style.width=Math.min(100,r*100)+'%';bar.style.background=r>=.95?'#e54d43':r>=.75?'#f7a22c':'#328c22'}
}
function renderHistorySummary(entries){const box=$('historySummary');box.replaceChildren();const t=sumEntries(entries);
 const head=el('div','historySummaryTitle');head.append(el('span','','ÐÑÐ¾Ð³Ð¸: '+dayText(selectedDay)),el('span','',`ÐÐ°Ð¿Ð¸ÑÐµÐ¹: ${entries.length}`));box.append(head,el('div','historySummaryFacts',`ÐÐ±ÑÐ¸Ð¹ Ð²ÐµÑ: ${num(t.grams)} Ð³`));
 // Keep the four nutrition progress lines at the same baseline on every phone width.
 const grid=el('div','historyKpis');
 for(const [label,key,unit] of [['ÐÐºÐ°Ð»','k','ÐºÐºÐ°Ð»'],['ÐÐµÐ»ÐºÐ¸','p','Ð³'],['ÐÐ¸ÑÑ','f','Ð³'],['Ð£Ð³Ð»ÐµÐ²Ð¾Ð´Ñ','c','Ð³']]){
  const ratio=t[key]/NORMS[key],p=Math.round(ratio*100),card=el('div','historyKpi');
  // "ÐÐºÐ°Ð»" is already the heading; do not repeat it in the current value or goal.
  const value=key==='k'?num(t[key]):`${one(t[key])} ${unit}`;
  const goal=key==='k'?`${NORMS[key]}`:`${NORMS[key]} ${unit}`;
  card.append(el('small','',label),el('strong','',value),el('em','',`${p}% / ${goal}`));
  const m=el('div','historyMeter'),inner=el('i');inner.style.width=Math.min(100,ratio*100)+'%';inner.style.background=ratio>=.95?'#de483f':ratio>=.75?'#ed9f29':'#3b992a';m.append(inner);card.append(m);grid.append(card);
 }
 box.append(grid)
}
async function refresh(){if(!db)return;const [entries,faves]=await Promise.all([all('entries'),all('favorites')]);favoritesCache=faves||[];entries.sort((a,b)=>String(b.created||'').localeCompare(String(a.created||'')));
 renderDailyTotals(entries);$('historyDayText').textContent=selectedDay===today()?'Ð¡ÐµÐ³Ð¾Ð´Ð½Ñ':dateFromKey(selectedDay).toLocaleDateString('ru-RU',{day:'numeric',month:'short'});renderDateStrip();
 const selected=entries.filter(x=>(x.date||String(x.created||'').slice(0,10))===selectedDay);renderHistorySummary(selected);
 const hist=$('historyItems');hist.replaceChildren();if(!selected.length)hist.append(el('p','empty','ÐÐ° Ð²ÑÐ±ÑÐ°Ð½Ð½ÑÐ¹ Ð´ÐµÐ½Ñ Ð¿Ð¾ÐºÐ° Ð½ÐµÑ Ð·Ð°Ð¿Ð¸ÑÐµÐ¹.'));
 for(const entry of selected){const t=totalsFor(entry),card=el('article','entry');card.append(el('b','historyDishName',capital(entry.name||summaryLabel(entry.items))));
  card.append(el('div','entryDetail',`ÐÐµÑ: ${num(t.grams)} Ð³ Â· Ð: ${num(t.k)} Â· Ð: ${one(t.p)} Â· Ð: ${one(t.f)} Â· Ð£: ${one(t.c)}`));
  if((entry.items||[]).length){const details=el('details','entryIngredients');details.append(el('summary','','Ð¡Ð¾ÑÑÐ°Ð² Â· '+entry.items.length));for(const i of entry.items)details.append(el('div','entryIngredient',`${capital(i.name)} Â· ${num(i.grams)} Ð³ Â· Ð: ${num(portionVal(i,'k'))} Â· Ð: ${one(portionVal(i,'p'))} Â· Ð: ${one(portionVal(i,'f'))} Â· Ð£: ${one(portionVal(i,'c'))}`));card.append(details)}
  const foot=el('div','entryFooter'),time=el('span','entryDate');const date=new Date(entry.created);time.textContent=Number.isNaN(date.valueOf())?'':date.toLocaleTimeString('ru-RU',{hour:'2-digit',minute:'2-digit'});foot.append(time);
  const actions=el('div','miniActions'),fbutton=button('â','iconAction',()=>toggleFavorite({...entry,name:entry.name||summaryLabel(entry.items)}));if(favoriteFor({...entry,name:entry.name||summaryLabel(entry.items)})){fbutton.textContent='â';fbutton.classList.add('on')}
  const remove=button('Ã','iconAction red',async()=>{await erase('entries',entry.id);await refresh()});remove.setAttribute('aria-label','Ð£Ð´Ð°Ð»Ð¸ÑÑ Ð·Ð°Ð¿Ð¸ÑÑ');actions.append(fbutton,remove);foot.append(actions);card.append(foot);hist.append(card)}
 const favorite=$('favoritesList');favorite.replaceChildren();if(!faves.length)favorite.append(el('p','empty','ÐÐ·Ð±ÑÐ°Ð½Ð½ÑÑ Ð±Ð»ÑÐ´ Ð¿Ð¾ÐºÐ° Ð½ÐµÑ.'));
 for(const f of faves){const t=totalsFor(f),card=el('article','entry');card.append(el('b','historyDishName',capital(f.name||summaryLabel(f.items))),el('div','entryDetail',`ÐÐµÑ: ${num(t.grams)} Ð³ Â· Ð: ${num(t.k)} Â· Ð: ${one(t.p)} Â· Ð: ${one(t.f)} Â· Ð£: ${one(t.c)}`));
  const foot=el('div','entryFooter'),actions=el('div','miniActions');actions.append(button('ï¼ ÐÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÑ','textBtn',()=>{dishes.push(newDish(f.name,f.items,[],f.manual));renderDishes();setTab('Text');$('preview').scrollIntoView({behavior:'smooth',block:'nearest'})}));actions.append(button('â','iconAction on',async()=>{await erase('favorites',f.id);await refresh();refreshFavoriteStars()}));foot.append(actions);card.append(foot);favorite.append(card)}
 refreshFavoriteStars();
}
function setTab(value){for(const x of ['Text','Photo','Faves']){const active=x===value;$('pane'+x).hidden=!active;$('tab'+x).classList.toggle('active',active);$('tab'+x).setAttribute('aria-selected',String(active))}}
$('tabText').addEventListener('click',()=>setTab('Text'));$('tabFaves').addEventListener('click',()=>setTab('Faves'));
$('tabPhoto').addEventListener('click',()=>{setTab('Photo');const input=$('photoInput');input.value='';input.click()});
$('photoInput').addEventListener('change',async e=>{const file=e.target.files?.[0];e.target.value='';if(!file)return;
 if(!file.type.startsWith('image/')){$('photoAIStatus').textContent='ÐÑÐ±ÐµÑÐ¸ÑÐµ Ð¸Ð·Ð¾Ð±ÑÐ°Ð¶ÐµÐ½Ð¸Ðµ';return}
 $('photoAIStatus').textContent='';const processed=await preparePhotoBlob(file);if(processed.size>2e6){$('photoAIStatus').textContent='ÐÐ·Ð¾Ð±ÑÐ°Ð¶ÐµÐ½Ð¸Ðµ ÑÐ»Ð¸ÑÐºÐ¾Ð¼ Ð±Ð¾Ð»ÑÑÐ¾Ðµ';return}
 if(photoUrl)URL.revokeObjectURL(photoUrl);photoFile=processed;photoUrl=URL.createObjectURL(processed);$('photoPreview').src=photoUrl;$('photoPreview').hidden=false;recognizePhoto()});
async function preparePhotoBlob(file){const src=URL.createObjectURL(file);try{const image=new Image();image.src=src;await image.decode();const ratio=Math.min(1,900/Math.max(image.naturalWidth,image.naturalHeight));
 const c=document.createElement('canvas');c.width=Math.round(image.naturalWidth*ratio);c.height=Math.round(image.naturalHeight*ratio);c.getContext('2d').drawImage(image,0,0,c.width,c.height);const blob=await new Promise(ok=>c.toBlob(ok,'image/jpeg',.75));c.width=0;c.height=0;return blob||file;
 }catch(e){console.warn(e);return file}finally{URL.revokeObjectURL(src)}}
async function requestCloudFood({text='',file=null,signal}){const body=new FormData();body.set('text',text.slice(0,500));if(file)body.set('photo',file,'meal.jpg');const response=await fetch(CLOUD_AI_ENDPOINT,{method:'POST',body,mode:'cors',cache:'no-store',signal});let data;const raw=await response.text();try{data=JSON.parse(raw)}catch(_){throw Error('Worker Ð²ÐµÑÐ½ÑÐ» Ð½Ðµ JSON, HTTP '+response.status)}
 if(!response.ok||data.ok!==true)throw Error('HTTP '+response.status+': '+String(data.message||data.error||'Cloudflare AI'));return data;}

// Cloud nutrition lookup: apply only well-matching documented records, never invent missing K/B/F/C.
const isChainText=(text)=>/(?:^|\s)(?:Ð¸Ð·\s+)?Ð¼Ð°Ðº(?:Ð°|Ðµ|Ð¾Ð¼)?(?=[\s:;,]|$)|Ð²ÐºÑÑÐ½Ð¾\s*[-ââ]?\s*Ð¸\s*ÑÐ¾ÑÐºÐ°|Ð¼Ð°ÐºÐ´Ð¾Ð½Ð°Ð»Ð´Ñ/i.test(String(text||''));
function toOfficialDish(row,quantity=1){
 const w=row.w*quantity;
 const per={k:row.k/row.w*100,p:row.p/row.w*100,f:row.f/row.w*100,c:row.c/row.w*100};
 return newDish(row.base_name,[{name:row.name,grams:w,...per,source:'ÐÐºÑÑÐ½Ð¾ â Ð¸ ÑÐ¾ÑÐºÐ°',verified_brand:true}]);
}
// Prefer independent menu items as named by the user, never a vague summary from the LLM.
async function applyRestaurantNutrition(input,parsed,signal){
 const response=await fetch(CHAIN_ORDER_API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:input}),mode:'cors',cache:'no-store',signal});
 const raw=await response.text();let data;
 try{data=JSON.parse(raw)}catch(e){throw Error('Ð Ð°Ð·Ð±Ð¾Ñ ÑÐµÑÑÐ¾ÑÐ°Ð½Ð½Ð¾Ð³Ð¾ Ð·Ð°ÐºÐ°Ð·Ð°: Ð½Ðµ JSON, HTTP '+response.status)}
 if(!response.ok||data.ok!==true)throw Error('Ð Ð°Ð·Ð±Ð¾Ñ Ð·Ð°ÐºÐ°Ð·Ð°: HTTP '+response.status+': '+(data.error||'ÐÐµÐ¸Ð·Ð²ÐµÑÑÐ½Ð°Ñ Ð¾ÑÐ¸Ð±ÐºÐ°'));
 devRecord('Ð Ð°Ð·Ð´ÐµÐ»ÐµÐ½Ð¸Ðµ Ð·Ð°ÐºÐ°Ð·Ð° Ð¸ Ð¿ÑÐ¾Ð²ÐµÑÐºÐ° Ð¼ÐµÐ½Ñ',{input,diagnostics:data.diagnostics,restaurant:data.restaurant});
 const official=[];
 for(const item of data.dishes||[]){
  if(item.found&&item.row&&Number(item.row.w)>0){
   const dish=toOfficialDish(item.row,Number(item.quantity)||1);
   if(item.row.estimated_portion)dish.weightReview='ÐÐµÐ»Ð¸ÑÐ¸Ð½Ð° Ð¿Ð¾ÑÑÐ¸Ð¸ Ð¿Ð¾Ð»ÑÑÐµÐ½Ð° Ð¼Ð°ÑÑÑÐ°Ð±Ð¸ÑÐ¾Ð²Ð°Ð½Ð¸ÐµÐ¼ Ð¸Ð¼ÐµÑÑÐµÐ³Ð¾ÑÑ Ð·Ð½Ð°ÑÐµÐ½Ð¸Ñ';
   official.push(dish);
  }else{
   const name=capital(item.canonical||item.input||'ÐÐµÐ¸Ð·Ð²ÐµÑÑÐ½Ð°Ñ Ð¿Ð¾Ð·Ð¸ÑÐ¸Ñ');
   official.push(newDish(name,[{name,grams:0,k:null,p:null,f:null,c:null,source:'unknown',portion:'',lookup_error:item.reason||'ÐÐµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð¾ Ð² Ð¼ÐµÐ½Ñ'}]));
  }
 }
 if(!official.length)throw Error('ÐÐ±Ð»Ð°ÑÐ½ÑÐ¹ ÑÐ°Ð·Ð±Ð¾Ñ Ð½Ðµ Ð²ÐµÑÐ½ÑÐ» Ð½Ð¸ Ð¾Ð´Ð½Ð¾Ð¹ Ð¿Ð¾Ð·Ð¸ÑÐ¸Ð¸');
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
  if(!response.ok)throw Error('ÐÐ¾Ð¸ÑÐº ÐÐÐÐ£: HTTP '+response.status);
  const result=await response.json();
  const lookup=new Map((result.results||[]).map(r=>[r.query,r]));
  devRecord('ÐÐ¾Ð¸ÑÐº ÐÐÐÐ£: ÐºÐ°Ð½Ð´Ð¸Ð´Ð°ÑÑ',{requests:names,results:(result.results||[]).map(x=>({query:x.query,diagnostics:x.diagnostics,items:(x.items||[]).slice(0,8)}))});
  for(const {dish,item,query} of tasks){
   if(item.userEdited || !(dish.items||[]).includes(item))continue;
   const options=lookup.get(query)?.items||[];
   // Require a strong name match and plausible nutrient composition.
   // Low score contains bad matches such as DRIED EGG/CANDY in egg search.
   const best=options.find(o=>Number(o.match_score)>=70 &&
    ['k','p','f','c'].every(k=>Number.isFinite(Number(o[k])) && Number(o[k])>=0) &&
    Number(o.k)<=900 &&
    !(/\b(?:powder|dried|substitute|pretzel|flavored|candy|mix)\b/i.test(o.name||'') && !/Ð¿Ð¾ÑÐ¾Ñ|ÑÑÑ|ÑÐ¼ÐµÑ/i.test(query)));
   if(!best)continue;
   // Nutrient lookup never substitutes a default portion. Missing weight must remain editable (0).
   for(const k of MACRO_KEYS)item[k]=Number(best[k]);
   item.source=best.source||'ÐÑÐºÑÑÑÐ°Ñ Ð±Ð°Ð·Ð°';item.source_name=best.name;updates++;
  }
 }catch(e){console.warn('ÐÐ²ÑÐ¾Ð¼Ð°ÑÐ¸ÑÐµÑÐºÐ¸Ð¹ Ð¿Ð¾Ð¸ÑÐº ÐÐÐÐ£:',e.message||e)}
 return {queried:names.length,filled:updates};
}


// v0.9.6 â find complete prepared dishes first. Decompose only if an exact
// finished-dish match is unavailable. Never count included sauce twice.
const MEAL_PLATTER_RE=/ÑÑÑÐµÑÐº.{0,20}Ð·Ð°Ð²ÑÑÐ°Ðº|Ð·Ð°Ð²ÑÑÐ°Ðº.{0,20}ÑÑÑÐµÑÐº|ÑÐ²ÐµÐ´ÑÐº.{0,12}ÑÑÐ¾Ð»|Ð°ÑÑÐ¾ÑÑÐ¸|Ð½Ð°Ð±Ð¾Ñ.{0,12}(?:Ð±Ð»ÑÐ´|Ð·Ð°ÐºÑÑ)|Ð·Ð°Ð²ÑÑÐ°Ðº.{0,12}(?:Ð½Ð°Ð±Ð¾Ñ|Ð¸Ð·)|ÑÐ¼ÐµÑÐ°Ð½Ð½.{0,12}ÑÐ°ÑÐµÐ»Ðº/i;
const READY_MAIN_RE=/Ð¿ÐµÐ»ÑÐ¼ÐµÐ½|Ð²Ð°ÑÐµÐ½Ð¸Ðº|Ð¼Ð°Ð½ÑÑ|Ð±Ð¾ÑÑ|ÑÑÐ¿|ÑÐ¾Ð»ÑÐ½Ðº|ÑÑÐ°|Ð±ÑÑÐ³ÐµÑ|Ð³Ð°Ð¼Ð±ÑÑÐ³ÐµÑ|Ð¿Ð¸ÑÑ|Ð¿Ð»Ð¾Ð²|ÑÑÑÐ½Ð¸Ðº|ÑÑÐµÐ¹Ðº|ÐºÐ¾ÑÐ»ÐµÑ|ÑÐ¸ÑÐ½Ð¸Ñ|Ð¾Ð¼Ð»ÐµÑ|ÑÑÑÐ¸|ÑÐ¾Ð»Ð»|Ð¿Ð°ÑÑ|Ð¼Ð°ÐºÐ°ÑÐ¾Ð½|Ð±Ð»Ð¸Ð½|ÑÐ°ÑÑÐ¼/i;
const BAD_CANDIDATE_RE=/powder|dried|substitute|pretzel|candy|flavored|infant|baby food|dry mix|Ð¿Ð¾ÑÐ¾Ñ|ÑÑÑÐ¾Ð¹ ÑÐ¼ÐµÑÐ¸/i;
function comparableWords(value){
 return itemKey(value).replace(/\b(?:ÑÐ¾|Ñ|Ð¸Ð·|Ð²|Ð½Ð°|Ð´Ð»Ñ|Ð±ÐµÐ·|Ð¿Ð¾ÑÑÐ¸Ñ|Ð¿Ð¾ÑÑÐ¸Ð¸|ÑÑÑÐº|ÑÑÑÐºÐ¸|ÑÑ|Ð³|Ð³ÑÐ°Ð¼Ð¼|Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ|ÑÑÐµÐ´Ð½ÑÑ|Ð±Ð¾Ð»ÑÑÐ°Ñ|Ð±Ð»ÑÐ´Ð¾|Ð³Ð¾ÑÐ¾Ð²Ð¾Ðµ)\b/gu,' ')
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
  if(/ÑÐ¾ÑÑ|ÑÐ¼ÐµÑÐ°Ð½/.test(query)&&!/(ÑÐ¾ÑÑ|ÑÐ¼ÐµÑÐ°Ð½|sauce|sour cream)/i.test(translated+' '+original))return -1;
  if(/Ð¶Ð°ÑÐµÐ½|Ð³Ð»Ð°Ð·ÑÐ½/.test(query)&&!/(Ð¶Ð°ÑÐµÐ½|Ð³Ð»Ð°Ð·ÑÐ½|fried)/i.test(translated+' '+original))return -1;
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
 devRecord('ÐÑÐ±Ð¾Ñ ÐÐÐÐ£',{query,full,considered:ranked.slice(0,7).map(x=>({name:x.row.name,ru:x.row.name_ru,source:x.row.source,score:x.score,k:x.row.k,p:x.row.p,f:x.row.f,c:x.row.c})),selected:selected.map(x=>({source:x.row.source,name:x.row.name,score:x.score})),final_per100:per});
 return {...per,source:selected.map(x=>x.row.source).join(' + ')||'ÐÐ°Ð·Ð° ÐÐÐÐ£',name:strongest.row.name_ru||strongest.row.name,allBranded:selected.every(x=>!!x.row.brand),approximate:false};
}
// Broad-match fallback ONLY if no comparable whole dish was found. A generic
// "cake" food record is useful as an editable estimate for a cream/sponge cake;
// it must not be asserted as the exact commercial product or exact recipe.
function approximateCategoryNutrition(query,candidates){
 const key=clean(query),qCake=/ÑÐ¾ÑÑ|cake|Ð¿Ð¸ÑÐ¾Ð¶Ð½/.test(key);
 if(!qCake || /Ð¼ÐµÐ´Ð¾Ð²Ð¸Ðº|Ð½Ð°Ð¿Ð¾Ð»ÐµÐ¾Ð½|ÑÐ¸Ð·ÐºÐµÐ¹Ðº|cheesecake/.test(key))return null;
 const valid=(candidates||[]).filter(c=>candidateMatch(query,c,false)>=-1 &&
   ['k','p','f','c'].every(k=>Number.isFinite(Number(c[k]))&&Number(c[k])>=0) &&
   Number(c.k)>100 && Number(c.k)<700 &&
   /\bcake\b|ÑÐ¾ÑÑ|Ð±Ð¸ÑÐºÐ²Ð¸Ñ/i.test((c.name||'')+' '+(c.name_ru||'')) &&
   !/mix|batter|dry|powder|pancake|rice cake|cake flour|pancake|waffle|cheesecake|gingerbread|ÑÐ¾ÑÑÐ¾Ð²Ð°Ñ ÑÐ¼ÐµÑÑ|ÑÐ¼ÐµÑÑ Ð´Ð»Ñ Ð²ÑÐ¿ÐµÑÐºÐ¸/i.test(c.name||''));
 if(!valid.length)return null;
 const withCream=/ÐºÑÐµÐ¼|ÑÐ»Ð¸Ð²Ðº|ÑÐ¾ÑÑ|Ð³Ð»Ð°Ð·ÑÑ/.test(key);
 const rated=valid.map(c=>{
   const n=String(c.name||'').toLowerCase();let s=Number(c.match_score||0)*.1;
   if(/\bcake\b/.test(n))s+=15;
   if(/frost|icing|cream|filled|layer/.test(n))s+=withCream?26:3;
   if(/sponge/.test(n))s+=withCream?-5:15;
   if(/chocolate/.test(n)&&!/(ÑÐ¾ÐºÐ¾Ð»Ð°Ð´|chocolate)/.test(key))s-=8;
   if(/fruitcake|cupcake|mug cake|snack cake/.test(n))s-=12;
   if(c.brand)s-=5;
   if(/FNDDS|SR Legacy|Foundation/i.test(c.dataType||''))s+=6;
   return {c,s};
 }).sort((a,b)=>b.s-a.s);
 const c=rated[0].c;
 const approximate={k:Number(c.k),p:Number(c.p),f:Number(c.f),c:Number(c.c),name:c.name_ru||c.name,source:'ÐÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐ¹ Ð°Ð½Ð°Ð»Ð¾Ð³: '+(c.source||'ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº'),approximate:true,includesToppings:true};
 devRecord('ÐÐ¾Ð´Ð±Ð¾Ñ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð¶ÑÐ½Ð½Ð¾Ð³Ð¾ Ð³Ð¾ÑÐ¾Ð²Ð¾Ð³Ð¾ Ð±Ð»ÑÐ´Ð°',{query,category:'Ð¢Ð¾ÑÑ / cake',candidates:rated.slice(0,7).map(x=>({name:x.c.name,k:x.c.k,p:x.c.p,f:x.c.f,c:x.c.c,source:x.c.source,score:x.s})),selected:c.name,note:'ÐÐµ ÑÐ¾ÑÐ½Ð°Ñ ÑÐµÑÐµÐ¿ÑÑÑÐ°. ÐÐÐÐ£ Ð²ÑÐ±ÑÐ°Ð½Ñ Ð¿Ð¾ ÑÐ¾Ð¿Ð¾ÑÑÐ°Ð²Ð¸Ð¼Ð¾Ð¼Ñ Ð³Ð¾ÑÐ¾Ð²Ð¾Ð¼Ñ Ð¸Ð·Ð´ÐµÐ»Ð¸Ñ.'});
 return approximate;
}
function inferGroupPlan(group){
 const name=String(group.name||'ÐÐ»ÑÐ´Ð¾').trim()||'ÐÐ»ÑÐ´Ð¾';
 const items=Array.isArray(group.items)?group.items.filter(x=>x&&x.name):[];
 let main=String(group.main||'').trim(),mainPortion=String(group.main_portion||'').trim();
 let additions=Array.isArray(group.additions)?group.additions.filter(x=>x?.name).map(x=>({...x,name:String(x.name),portion:String(x.portion||'1 Ð¿Ð¾ÑÑÐ¸Ñ')})):[];
 let kind=['prepared','platter','recipe'].includes(group.kind)?group.kind:'prepared';
 if(MEAL_PLATTER_RE.test(name))kind='platter';
 const suffix=name.match(/^(.+?)\s+(?:ÑÐ¾?|Ð²)\s+(ÑÐ¼ÐµÑÐ°Ð½(?:Ð¾Ð¹|Ð°|Ñ)|ÑÐ¾ÑÑ(?:Ðµ|Ð¾Ð¼)?\s+[^,]+)$/i);
 if(suffix){
   if(!main||itemKey(main)===itemKey(name))main=suffix[1].trim();
   if(!additions.some(a=>/ÑÐ¼ÐµÑÐ°Ð½|ÑÐ¾ÑÑ/.test(clean(a.name))))additions.push({name:capital(suffix[2].replace(/^ÑÐ¾ÑÑÐµ?Ð¼?\s+/i,'Ð¡Ð¾ÑÑ ')),portion:'1 Ð¿Ð¾ÑÑÐ¸Ñ'});
   if(/ÐºÑÐµÐ²ÐµÑ|ÑÑÐ±|ÐºÑÑÐ¸Ñ|Ð¼ÑÑ|Ð¾Ð²Ð¾Ñ/.test(clean(main))&&/ÑÐ¾ÑÑ/.test(clean(suffix[2])))kind='recipe';
 }
 if(!main && kind!=='platter'){
  const possible=items.find(x=>exactEnough(x.name,name));
  const edible=items.find(x=>!/(ÑÐ¾ÑÑ|ÑÐ¼ÐµÑÐ°Ð½|Ð¼Ð°Ð¹Ð¾Ð½ÐµÐ·|Ð¿ÑÐ¸Ð¿ÑÐ°Ð²|ÑÐ¿ÐµÑÐ¸)/.test(clean(x.name)));
  main=possible?.name||(/^(?:Ð±Ð»ÑÐ´Ð¾|ÐµÐ´Ð°|ÑÐ°ÑÐµÐ»ÐºÐ°)$/i.test(name)?(edible?.name||name):name);
 }
 const mainIncluded=items.find(x=>exactEnough(x.name,main));
 if(!mainPortion)mainPortion=String(mainIncluded?.portion||'1 Ð¿Ð¾ÑÑÐ¸Ñ');
 const mainMeta={...mainIncluded,weight_g:group.main_weight_g??mainIncluded?.weight_g??null,volume_ml:group.main_volume_ml??mainIncluded?.volume_ml??null,weight_basis:group.main_weight_basis||mainIncluded?.weight_basis||'',weight_estimated:mainIncluded?.weight_estimated!==false};
 // Older AI versions may return ONLY the topping of a recognized main dish.
 if(!additions.length){
  // Only infer a side when ALL model items are toppings: e.g. 'ÐÐµÐ»ÑÐ¼ÐµÐ½Ð¸' but only 'Ð¡Ð¼ÐµÑÐ°Ð½Ð°'.
  // Sauces already INSIDE a burger are not separate servings.
  const core=items.filter(x=>!/ÑÐ¼ÐµÑÐ°Ð½|ÑÐ¾ÑÑ|ÐºÐµÑÑÑÐ¿|Ð¼Ð°Ð¹Ð¾Ð½ÐµÐ·|Ð¼ÐµÐ´/.test(clean(x.name)));
  if(!core.length) additions=items.filter(x=>!exactEnough(x.name,main)&&/ÑÐ¼ÐµÑÐ°Ð½|ÑÐ¾ÑÑ|ÐºÐµÑÑÑÐ¿|Ð¼Ð°Ð¹Ð¾Ð½ÐµÐ·|Ð¼ÐµÐ´/.test(clean(x.name)));
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
   devRecord('ÐÐ¾Ð¸ÑÐº ÐÐÐÐ£: Ð¾ÑÐ´ÐµÐ»ÑÐ½ÑÐ¹ Ð¾ÑÐ²ÐµÑ',{query:q,diagnostics:data.diagnostics,options:(data.items||[]).slice(0,7)});
  }catch(e){devRecord('ÐÑÐ¸Ð±ÐºÐ° Ð¾ÑÐ´ÐµÐ»ÑÐ½Ð¾Ð³Ð¾ Ð¿Ð¾Ð¸ÑÐºÐ° ÐÐÐÐ£',{query:q,error:String(e.message||e)});}
  finally{clearTimeout(timer)}
 }
 // A small group is fast on Worker v1.11; on failure try every query separately
 // so a single delayed API request cannot erase results already received.
 for(let i=0;i<queries.length;i+=6){
  const slice=queries.slice(i,i+6),controller=new AbortController(),timer=setTimeout(()=>controller.abort(),23000);
  try{
   const r=await fetch(FOOD_BATCH_API,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({queries:slice}),mode:'cors',cache:'no-store',signal:controller.signal});
   if(!r.ok)throw Error('HTTP '+r.status);
   const json=await r.json();if(!json.ok)throw Error(json.error||'ÐÐµÐºÐ¾ÑÑÐµÐºÑÐ½ÑÐ¹ Ð¾ÑÐ²ÐµÑ');
   for(const x of json.results||[])result.set(x.query,x);
   devRecord('ÐÑÐµ Ð½Ð°Ð¹Ð´ÐµÐ½Ð½ÑÐµ ÐÐÐÐ£',{queries:slice,results:(json.results||[]).map(x=>({query:x.query,diagnostics:x.diagnostics,sources:x.sources,options:(x.items||[]).slice(0,10)}))});
   const missing=slice.filter(q=>!result.has(q));if(missing.length)await Promise.all(missing.map(fetchOne));
  }catch(error){
   devRecord('ÐÑÐ¸Ð±ÐºÐ° Ð³ÑÑÐ¿Ð¿Ñ ÐÐÐÐ£',{queries:slice,error:String(error.message||error),action:'ÐÐ¾Ð²ÑÐ¾ÑÐ¸ÑÑ Ð·Ð°Ð¿ÑÐ¾ÑÑ Ð¿Ð¾ Ð¾Ð´Ð½Ð¾Ð¼Ñ'});
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
   devRecord('ÐÑÐºÐ°Ð· Ð¾Ñ Ð½ÐµÑÐµÐ¿ÑÐµÐ·ÐµÐ½ÑÐ°ÑÐ¸Ð²Ð½Ð¾Ð³Ð¾ Ð±ÑÐµÐ½Ð´Ð°',{query,remote:remote.name,k:remote.k,local:local.name,local_k:local.k});
   return {...local,approximate:true,source:'ÐÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐ¹ Ð²ÑÑÑÐ¾ÐµÐ½Ð½ÑÐ¹ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº'};
 }
 if(remote)return remote;
 if(full){const approximate=approximateCategoryNutrition(query,candidates);if(approximate)return approximate;}
 if(local){devRecord('Ð ÐµÐ·ÐµÑÐ²Ð½ÑÐ¹ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº',{query,nutrition:local,whole:full});return {...local,approximate:true,source:'ÐÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐ¹ Ð²ÑÑÑÐ¾ÐµÐ½Ð½ÑÐ¹ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº',includesToppings:/ÑÐ¾ÑÑ Ñ ÐºÑÐµÐ¼Ð¾Ð¼/.test(local.name)};}
 // Last resort per user request: when strict multilingual matching rejected all
 // nutritional records, use the most plausible available original candidate
 // instead of leaving K/B/F/C blank. Clearly mark this as approximate.
 const plausible=candidates.filter(x=>['k','p','f','c'].every(k=>x[k]!==null&&x[k]!==undefined&&Number.isFinite(Number(x[k]))&&Number(x[k])>=0)&&Number(x.k)<=900);
 const acceptable=plausible.filter(x=>!BAD_CANDIDATE_RE.test(String(x.name||'')));
 const pool=acceptable.length?acceptable:plausible;
 if(pool.length){
  const ranked=pool.map(x=>{
   const label=String(x.name||'')+' '+String(x.name_ru||'');
   const n=String(x.name||'').toLowerCase();
   let score=Number(x.match_score)||0;
   if(exactEnough(query,label)||englishQuery&&exactEnough(englishQuery,label))score+=65;
   if(x.brand)score-=25;
   if(/CoFID|Matvaretabellen|Livsmedelsverket|Canadian Nutrient|Foundation|SR Legacy|FNDDS/i.test(String(x.source||'')+' '+String(x.dataType||'')))score+=20;
   if(/\b(?:oil|pate|powder|candy|nog|fu yung|mix)\b/i.test(n)&&!/(Ð¼Ð°ÑÐ»Ð¾|Ð¿Ð°ÑÑÐµÑ|Ð¿Ð¾ÑÐ¾Ñ|ÐºÐ¾Ð½ÑÐµÑ|\boil\b|\bpate\b|\bmix\b)/i.test(query+' '+englishQuery))score-=180;
   return {x,score};
  }).sort((a,b)=>b.score-a.score);
  if(ranked[0].score>=-40){
   const x=ranked[0].x;
   devRecord('Ð ÐµÐ·ÐµÑÐ² Ð¸Ð· Ð¾ÑÐºÐ»Ð¾Ð½ÑÐ½Ð½ÑÑ ÑÐµÐ·ÑÐ»ÑÑÐ°ÑÐ¾Ð²',{query,english_query:englishQuery,candidate:x.name,source:x.source,score:ranked[0].score,note:'ÐÐÐÐ£ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐµ; ÑÐ¾Ð²Ð¿Ð°Ð´ÐµÐ½Ð¸Ðµ Ð½Ðµ Ð¿ÑÐ¾ÑÐ»Ð¾ ÑÑÑÐ¾Ð³Ð¸Ð¹ Ð¾ÑÐ±Ð¾Ñ'});
   return {...Object.fromEntries(MACRO_KEYS.map(k=>[k,Number(x[k])])),source:'ÐÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐ¹ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½ÑÐ¹ Ð°Ð½Ð°Ð»Ð¾Ð³: '+(x.source||'Ð¸ÑÑÐ¾ÑÐ½Ð¸Ðº'),name:x.name_ru||x.name,approximate:true,matched_by:'relaxed_fallback'};
  }
 }
 // Existing recipe-only approximation for whipped-cream cakes.
 if(full && /ÑÐ¾ÑÑ|Ð¿Ð¸ÑÐ¾Ð¶Ð½/.test(clean(query)) && !/Ð¼ÐµÐ´Ð¾Ð²Ð¸Ðº|Ð½Ð°Ð¿Ð¾Ð»ÐµÐ¾Ð½|ÑÐ¸Ð·ÐºÐµÐ¹Ðº/.test(clean(query))){
  const category=FOOD.find(f=>f.name==='ÑÐ¾ÑÑ Ñ ÐºÑÐµÐ¼Ð¾Ð¼');
  devRecord('Ð ÐµÐ·ÐµÑÐ²Ð½Ð°Ñ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½Ð°Ñ ÐºÐ°ÑÐµÐ³Ð¾ÑÐ¸Ñ',{query,category:'ÑÐ¾ÑÑ Ñ ÐºÑÐµÐ¼Ð¾Ð¼',nutrition:category});
  return {...category,approximate:true,includesToppings:true,source:'ÐÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½Ð°Ñ Ð¾ÑÐµÐ½ÐºÐ° ÑÐµÑÐµÐ¿ÑÑÑÑ'};
 }
 return null;
}
function safeWeight(food,portion,source,meta={}){
 // No local cup/bowl/"usual=100g" mapping may override a model's context-dependent mass.
 const grams=Number(meta?.weight_g);
 const valid=Number.isFinite(grams)&&grams>0&&grams<=10000;
 const result={grams:valid?Math.round(grams*10)/10:0,
  weightReview:valid?'':'ÐÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½Ðµ Ð¾Ð¿ÑÐµÐ´ÐµÐ»Ð¸Ð»Ð° Ð²ÐµÑ. Ð£ÐºÐ°Ð¶Ð¸ÑÐµ ÐµÐ³Ð¾ Ð²ÑÑÑÐ½ÑÑ.',
  volume_ml:Number(meta?.volume_ml)||null,weight_basis:String(meta?.weight_basis||''),
  weight_estimated:meta?.weight_estimated!==false,portion:String(portion||'1 Ð¿Ð¾ÑÑÐ¸Ñ')};
 devRecord('ÐÑÐµÐ½ÐºÐ° Ð²ÐµÑÐ° Ð½ÐµÐ¹ÑÐ¾ÑÐµÑÑÑ',{food,portion:result.portion,weight_g:valid?result.grams:null,volume_ml:result.volume_ml,weight_basis:result.weight_basis,estimated:result.weight_estimated,source});
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
 if(food.matched_by==='relaxed_fallback')dish.uncertain=['ÐÐÐÐ£ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐµ: Ð¸ÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°Ð½ Ð½Ð°Ð¸Ð±Ð¾Ð»ÐµÐµ Ð±Ð»Ð¸Ð·ÐºÐ¸Ð¹ ÑÐµÐ·ÑÐ»ÑÑÐ°Ñ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸ÐºÐ°. ÐÑÐ¾Ð²ÐµÑÑÑÐµ Ð·Ð½Ð°ÑÐµÐ½Ð¸Ñ.'];
 if(!grams)dish.uncertain=[...(dish.uncertain||[]),'ÐÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½Ðµ Ð¾Ð¿ÑÐµÐ´ÐµÐ»Ð¸Ð»Ð° Ð²ÐµÑ Ð¿Ð¾ÑÑÐ¸Ð¸. Ð£ÐºÐ°Ð¶Ð¸ÑÐµ Ð²ÐµÑ Ð¿ÐµÑÐµÐ´ ÑÐ¾ÑÑÐ°Ð½ÐµÐ½Ð¸ÐµÐ¼.'];
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
  const core=plan.items.filter(x=>x.name&&!(/ÑÐ¼ÐµÑÐ°Ð½|ÑÐ¾ÑÑ|Ð¼Ð°Ð¹Ð¾Ð½ÐµÐ·/.test(clean(x.name))));
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
async function resolveCloudDishes(response,source='text'){
 const raw=response?.food||response||{};
 const groups=Array.isArray(raw.dishes)&&raw.dishes.length?raw.dishes:
   (Array.isArray(raw.items)&&raw.items.length?[{name:raw.name||'ÐÐ»ÑÐ´Ð¾',items:raw.items}]:[]);
 if(!groups.length)throw Error('ÐÐµ Ð½Ð°Ð¹Ð´ÐµÐ½Ñ Ð±Ð»ÑÐ´Ð° Ð² Ð¾ÑÐ²ÐµÑÐµ Ð½ÐµÐ¹ÑÐ¾ÑÐµÑÐ¸');
 const plans=groups.slice(0,8).map(inferGroupPlan);
 devRecord('ÐÐ»Ð°Ð½ ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð½Ð½ÑÑ Ð±Ð»ÑÐ´',{source,plans});
 // First ask ONLY for complete ready dishes (and platter components); do not
 // make 5 separate requests for the cake ingredients unless the complete
 // cake lookup genuinely failed. This also saves DEMO_KEY requests.
 const firstQueries=plans.flatMap(p=>p.kind==='platter'?p.items.map(x=>x.name):[p.name]);
 const matches=await batchNutritionQueries(firstQueries);
 const extraQueries=[];
 for(const p of plans){
  if(p.kind==='platter'){
   extraQueries.push(p.main,...p.additions.map(a=>a.name));
   continue;
  }
  const whole=nutritionFor(p.name,matches,true);
  if(!whole)extraQueries.push(p.main,...p.additions.map(a=>a.name),...p.items.map(x=>x.name));
  else if(!whole.includesToppings)extraQueries.push(...p.additions.filter(a=>!exactEnough(p.name,p.main+' '+a.name)).map(a=>a.name));
 }
 if(extraQueries.length){const more=await batchNutritionQueries(extraQueries.filter(q=>!matches.has(q)));for(const [q,x] of more)matches.set(q,x);}
 const output=[];
 for(const plan of plans){
  // Different foods served together: do not use a generic "Turkish breakfast" listing.
  if(plan.kind==='platter'){
   const items=detailItemsForPlan(plan,matches,source);output.push(newDish(plan.name,items));
   devRecord('Ð ÐµÑÐµÐ½Ð¸Ðµ Ð¿Ð¾ Ð±Ð»ÑÐ´Ñ',{dish:plan.name,decision:'platter_components',components:items.map(x=>x.name)});continue;
  }
  // First: exact whole prepared dish. Never accept just "pelmeni" as "pelmeni with sour cream".
  const complete=nutritionFor(plan.name,matches,true);
  if(complete){
   output.push(dishFromWhole(plan.name,plan.mainPortion,complete,source,plan.mainMeta));
   const extrasOutside=complete.includesToppings?[]:plan.additions.filter(x=>!exactEnough(plan.name,plan.main+' '+x.name));
   if(complete.includesToppings&&plan.additions.length)devRecord('ÐÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½Ð¾Ðµ ÑÐµÐ»Ð¾Ðµ Ð±Ð»ÑÐ´Ð¾',{dish:plan.name,note:'ÐÐ¸Ð´Ð¸Ð¼ÑÐµ ÑÐºÑÐ°ÑÐµÐ½Ð¸Ñ/ÐºÑÐµÐ¼ ÑÐ¾ÑÑÐ° ÑÑÐ¸ÑÐ°ÑÑÑÑ ÑÐ°ÑÑÑÑ Ð¾ÑÐµÐ½ÑÐ½Ð½Ð¾Ð³Ð¾ Ð³Ð¾ÑÐ¾Ð²Ð¾Ð³Ð¾ Ð¸Ð·Ð´ÐµÐ»Ð¸Ñ, ÑÑÐ¾Ð±Ñ Ð¸Ð·Ð±ÐµÐ¶Ð°ÑÑ Ð´Ð²Ð¾Ð¹Ð½Ð¾Ð³Ð¾ ÑÑÑÑÐ°',additions:plan.additions.map(x=>x.name)});
   // A record for "ÐÐµÐ»ÑÐ¼ÐµÐ½Ð¸" does not include a separate spoon of smetana.
   for(const addon of extrasOutside){
    const nutrition=nutritionFor(addon.name,matches,false);
    if(nutrition)output.push(dishFromWhole(addon.name,addon.portion,nutrition,source,addon));
    else output.push(newDish(capital(addon.name),[makeKnownItem(addon.name,addon.portion,null,source,addon)]));
   }
   devRecord('Ð ÐµÑÐµÐ½Ð¸Ðµ Ð¿Ð¾ Ð±Ð»ÑÐ´Ñ',{dish:plan.name,decision:'whole_prepared_dish',source:complete.source,additional_standalone:extrasOutside.map(x=>x.name),extras_inside:plan.additions.filter(x=>!extrasOutside.includes(x)).map(x=>x.name)});
   continue;
  }
  const standalone=nutritionFor(plan.main,matches,false);
  // A prepared main food with an external topping is saved as separate dishes.
  if(plan.kind==='prepared'&&standalone&&plan.additions.length){
   output.push(dishFromWhole(plan.main,plan.mainPortion,standalone,source,plan.mainMeta));
   for(const addon of plan.additions){
    const nutrition=nutritionFor(addon.name,matches,false);
    if(nutrition)output.push(dishFromWhole(addon.name,addon.portion,nutrition,source,addon));
    else output.push(newDish(capital(addon.name),[makeKnownItem(addon.name,addon.portion,null,source,addon)]));
   }
   devRecord('Ð ÐµÑÐµÐ½Ð¸Ðµ Ð¿Ð¾ Ð±Ð»ÑÐ´Ñ',{dish:plan.name,decision:'prepared_main_plus_separate_topping',main:plan.main,extras:plan.additions});continue;
  }
  if(plan.kind==='prepared'&&standalone&&(!plan.additions.length)){
   output.push(dishFromWhole(plan.name,plan.mainPortion,standalone,source,plan.mainMeta));
   devRecord('Ð ÐµÑÐµÐ½Ð¸Ðµ Ð¿Ð¾ Ð±Ð»ÑÐ´Ñ',{dish:plan.name,decision:'main_prepared_whole',main:plan.main});continue;
  }
  // No complete dish: decompose only now, preserving main when AI omitted it.
  const parts=detailItemsForPlan(plan,matches,source);
  const built=newDish(plan.name,parts);if(parts.some(x=>x.nutritionFallback))built.uncertain=['ÐÐµÐºÐ¾ÑÐ¾ÑÑÐµ ÐÐÐÐ£ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐµ: Ð¸ÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°Ð½ Ð±Ð»Ð¸Ð¶Ð°Ð¹ÑÐ¸Ð¹ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½ÑÐ¹ Ð²Ð°ÑÐ¸Ð°Ð½Ñ.'];output.push(built);
  devRecord('Ð ÐµÑÐµÐ½Ð¸Ðµ Ð¿Ð¾ Ð±Ð»ÑÐ´Ñ',{dish:plan.name,decision:'decompose_no_whole_match',main:plan.main,ingredients:parts.map(x=>({name:x.name,has_nutrition:!hasMissingNutrition(x)}))});
 }
 if(!output.length)throw Error('ÐÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½Ðµ Ð²ÑÐ´ÐµÐ»Ð¸Ð»Ð° ÑÑÐµÐ´Ð¾Ð±Ð½ÑÐµ Ð¿ÑÐ¾Ð´ÑÐºÑÑ');
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
 showPhotoProgress('ÐÐ½Ð°Ð»Ð¸Ð· ÑÐ¾ÑÐ¾Ð³ÑÐ°ÑÐ¸Ð¸â¦');$('photoDebug').hidden=true;
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),65000);
 try{
  const response=await requestCloudFood({file:photoFile,signal:controller.signal});if(run!==activePhotoRun)return;devRecord('Ð¤Ð¾ÑÐ¾: Ð½ÐµÐ¹ÑÐ¾ÑÐµÑÑ',{food:response.food,usage:response.usage,portion_retry:response.portion_retry,json_recovery:response.json_recovery});
  showPhotoProgress('ÐÐ¾Ð¸ÑÐº ÐÐÐÐ£ Ð³Ð¾ÑÐ¾Ð²ÑÑ Ð±Ð»ÑÐ´â¦');
  const result=await resolveCloudDishes(response,'photo');if(!result.length)throw Error('ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ Ð¾Ð¿ÑÐµÐ´ÐµÐ»Ð¸ÑÑ Ð±Ð»ÑÐ´Ð°');
  // Do not show intermediate empty ingredients while nutrition calls are still running.
  if(run!==activePhotoRun)return;
  dishes=result;pendingSource='photo';renderDishes();status.textContent='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ Ð·Ð°Ð²ÐµÑÑÐµÐ½Ð¾';
  if(response.food?.uncertain?.length)$('photoCandidates').textContent='Ð£ÑÐ¾ÑÐ½Ð¸ÑÐµ: '+response.food.uncertain.join('; ');
  else $('photoCandidates').replaceChildren();
  scrollToDish();
 }catch(e){if(run!==activePhotoRun)return;status.textContent='ÐÑÐ¸Ð±ÐºÐ° ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ñ';$('photoDebug').hidden=false;$('photoDebugLog').textContent=String(e.message||e)+'\n'+CLOUD_AI_ENDPOINT;
 }finally{clearTimeout(timeout);if(run===activePhotoRun)bar.hidden=true}
}
$('parseBtn').addEventListener('click',async()=>{
 const text=$('foodText').value.trim();if(!text)return;
 const run=++activeTextRun,btn=$('parseBtn');btn.disabled=true;$('parseBtnLabel').hidden=true;$('parseSpinner').hidden=false;
 pendingSource=null;dishes=[];draftsByDish.clear();renderDishes();
 $('textDebug').hidden=true;$('textAIStatus').textContent='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ â Ð°Ð½Ð°Ð»Ð¸Ð· ÑÐµÐºÑÑÐ°â¦';
 $('textProgressWrap').hidden=false;$('textProgressBar').removeAttribute('value');
 const controller=new AbortController();const timeout=setTimeout(()=>controller.abort(),65000);
 try{
  let found;
  if(isChainText(text)){
   // The user explicitly names a restaurant: get exact menu entries first.
   $('textAIStatus').textContent='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ â ÑÐ¸ÑÐ¼ÐµÐ½Ð½Ð¾Ðµ Ð¼ÐµÐ½Ñâ¦';
   found=await applyRestaurantNutrition(text,[],controller.signal);
  }else{
   const response=await requestCloudFood({text,signal:controller.signal});if(run!==activeTextRun)return;devRecord('Ð¢ÐµÐºÑÑ: Ð½ÐµÐ¹ÑÐ¾ÑÐµÑÑ',{input:text,food:response.food,usage:response.usage,portion_retry:response.portion_retry,json_recovery:response.json_recovery});
   $('textAIStatus').textContent='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ â Ð¿Ð¾Ð¸ÑÐº Ð³Ð¾ÑÐ¾Ð²ÑÑ Ð±Ð»ÑÐ´ Ð¸ ÐÐÐÐ£â¦';
   found=await resolveCloudDishes(response,'text');if(!found.length)throw Error('ÐÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½Ðµ Ð²ÑÐ´ÐµÐ»Ð¸Ð»Ð° Ð±Ð»ÑÐ´Ð°');
  }
  if(run!==activeTextRun)return;
  $('textAIStatus').textContent='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ â Ð¿Ð¾Ð´Ð±Ð¾Ñ ÐÐÐÐ£â¦';
  if(run!==activeTextRun)return;
  dishes=found;pendingSource='text';renderDishes();$('textAIStatus').textContent='';scrollToDish();
 }catch(e){if(run!==activeTextRun)return;
  $('textDebug').hidden=false;$('textDebugLog').textContent=String(e.message||e);
  devRecord('ÐÑÐ¸Ð±ÐºÐ° ÑÐ°Ð·Ð±Ð¾ÑÐ° ÑÐµÐºÑÑÐ°',{input:text,error:String(e.message||e)});
  if(isChainText(text)){
   $('textAIStatus').textContent='ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ Ð¿Ð¾Ð»ÑÑÐ¸ÑÑ Ð¼ÐµÐ½Ñ. ÐÐ¾Ð²ÑÐ¾ÑÐ¸ÑÐµ Ð·Ð°Ð¿ÑÐ¾Ñ.';
   dishes=[];renderDishes();
  }else{
   // No guessed dishes when AI is unavailable: the offline text splitter
   // cannot infer portion weights and may corrupt product names ("Ð³ Ð¿ÐµÑÐµÐ½Ð¸").
   // Preserve the original input for an immediate retry instead.
   $('textAIStatus').textContent='ÐÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½Ðµ ÑÐ¼Ð¾Ð³Ð»Ð° Ð¾Ð±ÑÐ°Ð±Ð¾ÑÐ°ÑÑ Ð·Ð°Ð¿ÑÐ¾Ñ. Ð¢ÐµÐºÑÑ ÑÐ¾ÑÑÐ°Ð½ÑÐ½ â Ð½Ð°Ð¶Ð¼Ð¸ÑÐµ Â«Ð Ð°ÑÑÑÐ¸ÑÐ°ÑÑÂ» ÐµÑÑ ÑÐ°Ð·.';
   dishes=[];pendingSource=null;renderDishes();
  }
 }finally{clearTimeout(timeout);if(run===activeTextRun){btn.disabled=false;$('parseBtnLabel').hidden=false;$('parseSpinner').hidden=true;$('textProgressWrap').hidden=true}}
});
$('clearPreview').addEventListener('click',()=>{
 activeTextRun++;pendingSource=null;releasePhotoPreview();$('photoInput').value='';
 dishes=[];draftsByDish.clear();renderDishes();$('textAIStatus').textContent='';
 $('foodText').value='';setStatus('');
 devRecord('ÐÑÐ¸ÑÑÐºÐ° ÑÐµÐºÑÑÐµÐ³Ð¾ Ð²Ð²Ð¾Ð´Ð°',{photo:true,text:true,dishes:true,historyUntouched:true});
});
$('addDishBtn').addEventListener('click',()=>{const d=newDish('');dishes.push(d);renderDishes(d.id);document.querySelector(`[data-dish="${d.id}"]`)?.scrollIntoView({behavior:'smooth',block:'nearest'})});
async function fetchFoodCandidates(q){const controller=new AbortController();const timer=setTimeout(()=>controller.abort(),18000);try{const r=await fetch(FOOD_SEARCH_API+'?q='+encodeURIComponent(q),{mode:'cors',cache:'no-store',signal:controller.signal});const raw=await r.text();let data;try{data=JSON.parse(raw)}catch(_){throw Error('ÐÑÐ²ÐµÑ Ð½Ðµ JSON (HTTP '+r.status+')')}if(!r.ok||data.ok!==true)throw Error(`HTTP ${r.status}: ${data.error||'ÐÐ¾Ð¸ÑÐº Ð½ÐµÐ´Ð¾ÑÑÑÐ¿ÐµÐ½'}`);return data}finally{clearTimeout(timer)}}

$('copyDiagnostic').addEventListener('click',async()=>{
 const out=$('technicalDebugLog').textContent;
 try{await navigator.clipboard.writeText(out);$('technicalCopyStatus').textContent='Ð¡ÐºÐ¾Ð¿Ð¸ÑÐ¾Ð²Ð°Ð½Ð¾';}
 catch(e){$('technicalCopyStatus').textContent='ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ ÑÐºÐ¾Ð¿Ð¸ÑÐ¾Ð²Ð°ÑÑ: '+e.message;}
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
(async()=>{try{db=await openDB();await refresh();renderDishes()}catch(e){console.error(e);$('textAIStatus').textContent='ÐÑÐ¸Ð±ÐºÐ° Ð»Ð¾ÐºÐ°Ð»ÑÐ½Ð¾Ð³Ð¾ ÑÑÐ°Ð½Ð¸Ð»Ð¸ÑÐ°: '+e.message}})();
if('serviceWorker'in navigator)window.addEventListener('load',()=>navigator.serviceWorker.register('./sw.js').catch(console.warn));
