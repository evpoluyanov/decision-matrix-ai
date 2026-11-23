import assert from 'node:assert/strict';
import worker from '../worker/worker.js';
const endpoint='https://food-ai-inference.evpoluyanov.workers.dev/analyze';
const whole=(name,grams,per100)=>({name,mode:'whole',weight_g:grams,per100,items:[]});
const per=(k,p,f,c)=>({k,p,f,c});
const wrap=(body)=>({choices:[{message:{content:JSON.stringify(body)}}],usage:{neurons:1}});
const complex='Блинчики с творогом (2шт), 20 г сметаны, 4 гренки, 100 г мортаделлы, 30 г сыра, 15 г масла 85% жирности, 10г меда, 20 г грецких орехов';
async function call(AI,text=complex){const form=new FormData();form.set('text',text);const r=await worker.fetch(new Request(endpoint,{method:'POST',body:form}),{AI});return {status:r.status,body:await r.json()};}
const partial={status:'partial',input_mode:'text',dishes:[whole('Блинчики с творогом',140,per(215,8,10,25)),whole('Сметана',20,per(205,3,20,3)),whole('Мёд',10,{k:320,p:null,f:0,c:80})],warnings:['Не удалось оценить орехи']};
let times=0;
let r=await call({run:async()=>{times++;return wrap(partial)}});
assert.equal(r.status,200,JSON.stringify(r.body));
assert.equal(r.body.ok,true);assert.equal(r.body.food.dishes.length,3);assert.equal(r.body.status,'partial');
assert.equal(r.body.food.dishes[2].per100.p,null);assert.equal(times,1);
console.log('PASS: partial list and missing per100 accepted, not HTTP 422, no recheck');
let toolArgs=[];
const toolAI={run:async(_model,options)=>{
 toolArgs.push(options);
 if(toolArgs.length===1)return {tool_calls:[{name:'search_official_menu',arguments:{queries:['Чизбургер']}}]};
 return wrap({status:'complete',input_mode:'text',dishes:[whole('Чизбургер',109,per(270,13,10,30))]});
 }};
r=await call(toolAI,'В маке чизбургер');
assert.equal(r.status,200,JSON.stringify(r.body));
assert.equal(r.body.food.dishes[0].name,'Чизбургер');
assert.equal(r.body.tool_trace[0].name,'search_official_menu');
assert.equal(toolArgs.length,2);
assert.ok(toolArgs[1].messages.find(m=>m.role==='tool'&&m.name==='search_official_menu'));
console.log('PASS: AI calls actual official menu lookup and uses resulting tool context');
// Valid ingredient recipe must be shown even with one missing component's nutrition.
const recipe={status:'partial',input_mode:'text',dishes:[{name:'Блины с рыбой',mode:'ingredients',weight_g:150,items:[{name:'Блины',weight_g:100,per100:per(210,7,8,26)},{name:'Сёмга',weight_g:50,per100:{k:null,p:null,f:null,c:null}}]}]};
r=await call({run:async()=>wrap(recipe)},'Блины с сёмгой');assert.equal(r.status,200);
assert.equal(r.body.food.dishes[0].items.length,2);
console.log('PASS: partial ingredient data retained');
// One-step multimodal model analysis passes photo as image; model owns OCR and mode selection.
const AI={run:async(_model,opts)=>{assert.ok(Array.isArray(opts.messages.find(x=>x.role==='user').content));return wrap({status:'complete',input_mode:'photo_text',recognized_text:'Творог 150 г',dishes:[whole('Творог',150,per(120,17,5,2))]})}};
const form=new FormData();form.set('photo',new File([Uint8Array.from([255,216,255,217])],'test.jpg',{type:'image/jpeg'}));const res=await worker.fetch(new Request(endpoint,{method:'POST',body:form}),{AI});const data=await res.json();assert.equal(res.status,200,JSON.stringify(data));assert.equal(data.food.input_mode,'photo_text');console.log('PASS: photo text processed by model in same logic');
