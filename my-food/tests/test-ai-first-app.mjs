import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const code=fs.readFileSync('my-food/site/app.js','utf8');
const start=code.indexOf('function validAIMacros(per100){');
const end=code.indexOf('\nfunction scrollToDish',start);
assert(start>0&&end>start);
const events=[];
const ctx={
 MACRO_KEYS:['k','p','f','c'],macroNames:{k:'Калории',p:'Белки',f:'Жиры',c:'Углеводы'},
 capital:s=>s,devRecord:(name,data)=>events.push({name,data}),
 itemKey:s=>String(s||'').toLowerCase().trim(),
 newDish:(name,items=[],unresolved=[],manual=null)=>({name,items,manual}),
 makeKnownItem:(name,portion,food,source,meta)=>({name,grams:meta.weight_g,k:food.k,p:food.p,f:food.f,c:food.c}),
 nutritionFor:(name)=>name==='Курица'?{k:240,p:22,f:18,c:1,source:'Тестовый справочник',name:'Chicken'}:null,
 batchNutritionQueries:async()=>new Map(),
};
vm.createContext(ctx);vm.runInContext(code.slice(start,end)+'\nthis.aiDishFromResponse=aiDishFromResponse;this.ratioDifference=ratioDifference;this.auditAIPer100=auditAIPer100;this.resolveCloudDishes=resolveCloudDishes;',ctx);
const per=(k,p,f,c)=>({k,p,f,c});
let d=ctx.aiDishFromResponse({name:'Суп',mode:'whole',weight_g:200,per100:per(80,4,3,11)},'text');
assert.equal(d.manual.grams,200);assert.equal(d.manual.k,160);assert.equal(d.per100.k,80);
console.log('PASS: PWA multiplies dish 100g macros by weight/100');
d=ctx.aiDishFromResponse({name:'Блины с начинкой',mode:'ingredients',weight_g:165,main:'Блины',items:[{name:'Блины',weight_g:100,per100:per(200,5,6,32)}],additions:[{name:'Сыр',weight_g:20,per100:per(280,6,25,2)},{name:'Рыба',weight_g:30,per100:per(200,20,12,0)}]},'text');
assert.equal(d.items.length,3);assert.equal(d.items.reduce((s,i)=>s+i.grams,0),150);
const kcal=d.items.reduce((s,i)=>s+i.grams*i.k/100,0);assert.equal(kcal,316);
console.log('PASS: PWA adds ingredients once and uses model component masses, not conflicting dish summary');
const factor=ctx.ratioDifference(80,150,'k');assert.equal(factor.factor,1.88);
assert.equal(ctx.ratioDifference(100,150,'k'),null);
console.log('PASS: diagnostic threshold is strictly > 1.5');
const response={food:{dishes:[{name:'Курица',mode:'whole',per100:per(100,22,3,0)}]}};
await ctx.auditAIPer100(response,'text',()=>true);
const report=events.find(e=>e.name.startsWith('Проверка КБЖУ по справочникам'));
assert(report,JSON.stringify(events));
assert(report.data.differences.length===1);
assert.equal(response.food.dishes[0].per100.k,100,'Directory may not overwrite model macro');
console.log('PASS: independent reference check logs mismatch without changing model values');
