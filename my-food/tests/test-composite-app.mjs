import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
const script=fs.readFileSync('my-food/site/app.js','utf8');
const start=script.indexOf('function inferGroupPlan(group){');
const end=script.indexOf('async function batchNutritionQueries',start);
assert(start>0&&end>start);
const context={
  MEAL_PLATTER_RE:/^$/,
  itemKey:s=>String(s||'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,''),
  exactEnough:(a,b)=>String(a||'').toLowerCase()===String(b||'').toLowerCase(),
  clean:s=>String(s||'').toLowerCase(),
  capital:s=>String(s||''),
};
vm.createContext(context);
vm.runInContext(script.slice(start,end)+'\nthis.testPlan = inferGroupPlan;',context);
const group={name:'Блины с творожным сыром и семгой',kind:'recipe',main:'Блины',main_portion:'2 штуки',main_weight_g:120,main_weight_basis:'общая оценка',items:[{name:'Блины',portion:'2 штуки',weight_g:100,weight_estimated:true,weight_basis:'оценка ИИ'}],additions:[{name:'Творожный сыр',portion:'2 чайные ложки',weight_g:20,weight_estimated:true},{name:'Сёмга слабосолёная',portion:'2 кусочка',weight_g:30,weight_estimated:true}]};
const plan=context.testPlan(group);
assert.equal(plan.kind,'recipe');
assert.equal(plan.mainMeta.weight_g,100,JSON.stringify(plan));
assert.equal(plan.additions.length,2);
assert.equal(plan.items.length,1);
assert(script.includes("p.kind==='recipe'&&(p.items.length+p.additions.length)>=2?"));
console.log('PASS: PWA counts filling additions and uses ingredient weight 100g rather than header weight 120g');
