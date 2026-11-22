import assert from 'node:assert/strict';
import worker from '../worker/worker.js';
const u='https://food-ai-inference.evpoluyanov.workers.dev/analyze';
const mk=(name,portion,grams)=>({name,kind:'prepared',main:name,main_portion:portion,main_weight_g:grams,main_weight_basis:'ИИ',items:[{name,portion,weight_g:grams,weight_estimated:false,weight_basis:'ИИ',confidence:'high'}],additions:[]});
const wrap=(ds)=>({choices:[{message:{content:JSON.stringify({dishes:ds,uncertain:[]})}}],usage:{neurons:1,prompt_tokens:80,completion_tokens:90}});
const tartar=mk('Соус тартар','10 г',10),egg=mk('Яйца','2 шт',110),cod=mk('Печень трески','20 г',20);
const query='2 яйца, 20 г печени трески и соус тартар 10г';
async function call(mode){let count=0;
 const AI={run:async (_model,req)=>{count++;const p=req.messages[0].content;
 if(count===1)return wrap(mode==='complete'?[egg,cod,tartar]:[tartar]);
 if(mode==='fail')return wrap([tartar]);
 if(p.includes('РАСПОЗНАЙ ТОЛЬКО СЛЕДУЮЩИЙ ФРАГМЕНТ')){
   if(p.includes('2 яйца'))return wrap([egg]);
   if(p.includes('20 г печени трески'))return wrap([cod]);
   if(p.includes('соус тартар 10г'))return wrap([tartar]);
 }
 throw Error('Unexpected AI prompt '+String(p).slice(-100));
 }};
 const form=new FormData();form.set('text',query);
 const r=await worker.fetch(new Request(u,{method:'POST',body:form}),{AI});
 return {status:r.status, json:await r.json(),calls:count};
}
let a=await call('repair');
assert.equal(a.status,200,JSON.stringify(a.json).slice(0,500));
assert.equal(a.json.food.dishes.length,3);
assert.equal(a.json.food.dishes.find(x=>x.name==='Яйца').main_weight_g,110);
assert.equal(a.json.food.dishes.find(x=>x.name==='Печень трески').main_weight_g,20);
assert.equal(a.json.food.dishes.find(x=>x.name==='Соус тартар').main_weight_g,10);
assert.equal(a.json.coverage.initial_missing.length,3);
assert.equal(a.json.coverage.final_missing.length,0);
assert.equal(a.calls,4);
console.log('Partial AI answer recovered',a.json.coverage);
a=await call('complete');assert.equal(a.status,200);assert.equal(a.calls,1);console.log('Already complete answer accepted with no extra AI calls');
a=await call('fail');assert.equal(a.status,422);assert.equal(a.json.coverage.final_missing.length,2);console.log('Unrecovered missing products fail safely with 422');

// The live model sometimes groups all three servings into ONE composite dish.
// Such a group must be replaced with three AI-resolved items, never doubled.
{
 let calls=0;
 const composite=mk('Яйца с печенью трески и соусом тартар','1 блюдо',140);
 const AI={run:async(_model,req)=>{
   calls++;
   const prompt=req.messages[0].content;
   if(calls===1)return wrap([composite]);
   if(prompt.includes('РАСПОЗНАЙ ТОЛЬКО СЛЕДУЮЩИЙ ФРАГМЕНТ')){
     if(prompt.includes('2 яйца'))return wrap([egg]);
     if(prompt.includes('20 г печени трески'))return wrap([cod]);
     if(prompt.includes('соус тартар 10г'))return wrap([tartar]);
   }
   throw Error('Unexpected grouped AI request');
 }};
 const fd=new FormData();fd.set('text',query);
 const response=await worker.fetch(new Request(u,{method:'POST',body:fd}),{AI});
 const body=await response.json();
 assert.equal(response.status,200,JSON.stringify(body).slice(0,300));
 assert.equal(body.coverage.grouping_repaired,true);
 assert.equal(body.food.dishes.length,3);
 assert.deepEqual(body.food.dishes.map(x=>x.main_weight_g).sort((a,b)=>a-b),[10,20,110]);
 assert.equal(body.food.dishes.some(x=>x.name.includes(' с печенью')),false);
 assert.equal(calls,4);
 console.log('Composite AI dish replaced, no double counting');
}
