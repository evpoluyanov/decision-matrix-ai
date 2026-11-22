import assert from 'node:assert/strict';
import worker from '../worker/worker.js';
const endpoint='https://food-ai-inference.evpoluyanov.workers.dev/analyze';
const text='2 блина, каждый с начинкой из чайной ложки творожного сыра и кусочком слабосоленой семги';
function ingredient(name,portion,weight){return {name,portion,weight_g:weight,weight_estimated:true,weight_basis:'оценка ИИ',confidence:'high'};}
const blini=ingredient('Блины','2 штуки',110),cheese=ingredient('Сыр творожный','2 чайные ложки, по одной в каждом блине',20),salmon=ingredient('Сёмга слабосолёная','2 кусочка, по одному в каждом блине',35);
const composite=(items=[blini,cheese,salmon],kind='recipe')=>({name:'Блины с творожным сыром и слабосолёной сёмгой',kind,main:'Блины',main_portion:'2 штуки',main_weight_g:110,main_weight_basis:'оценка ИИ',items,additions:[]});
const wrap=(dishes)=>({choices:[{message:{content:JSON.stringify({dishes,uncertain:[]})}}],usage:{neurons:1,prompt_tokens:90,completion_tokens:200}});
async function run(responses){let count=0,prompts=[];const AI={run:async(_model,req)=>{prompts.push(req.messages?.[0]?.content||'');let next=responses[count++];assert(next,'No more AI responses for invocation '+count);return wrap(next)}};const form=new FormData();form.set('text',text);const r=await worker.fetch(new Request(endpoint,{method:'POST',body:form}),{AI});return {status:r.status,data:await r.json(),count,prompts};}
// A compound with repeated fillings must be ONE recipe, not three independent portions.
let v=await run([[composite([blini,cheese,salmon],'prepared')]]);
assert.equal(v.status,200,JSON.stringify(v.data));
assert.equal(v.data.food.dishes.length,1);
assert.equal(v.data.food.dishes[0].kind,'recipe');
assert.deepEqual(v.data.food.dishes[0].items.map(i=>i.weight_g),[110,20,35]);
assert.equal(v.data.coverage.final_missing.length,0);
assert.equal(v.count,1);
console.log('PASS: full pancake recipe accepted in one AI request; no false HTTP 422');
// If salmon was silently omitted, repair must replace, not append, the incomplete dish.
v=await run([[composite([blini,cheese])],[composite()]]);
assert.equal(v.status,200,JSON.stringify(v.data));
assert.equal(v.data.food.dishes.length,1);
assert.deepEqual(v.data.food.dishes[0].items.map(i=>i.name),[blini.name,cheese.name,salmon.name]);
assert.equal(v.data.coverage.composed,true);
assert.equal(v.data.coverage.restored.length,1);
assert.equal(v.count,2);
console.log('PASS: missing filling recovered by one AI correction; no double-counting');
// Distinct portions are still distinct: safeguards for 2 eggs, liver, tartar.
const originalText='2 яйца, 20 г печени трески и соус тартар 10г';
function simple(name,portion,mass){return {name,kind:'prepared',main:name,main_portion:portion,main_weight_g:mass,items:[ingredient(name,portion,mass)],additions:[]}};
let independentCalls=0;
const AI={run:async()=>{independentCalls++;return wrap([simple('Яйца','2 шт',100),simple('Печень трески','20 г',20),simple('Соус тартар','10 г',10)])}};
const form=new FormData();form.set('text',originalText);
const result=await worker.fetch(new Request(endpoint,{method:'POST',body:form}),{AI});
const data=await result.json();assert.equal(result.status,200,JSON.stringify(data));assert.equal(data.food.dishes.length,3);assert.equal(independentCalls,1);
console.log('PASS: independent servings remain three separate dishes');
