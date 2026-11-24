import assert from 'node:assert/strict';
import fs from 'node:fs';import vm from 'node:vm';
const records={
 'Яйца':{english_query:'egg',items:[],diagnostics:['USDA 429','OFF 503']},
 'Печень трески':{english_query:'Cod liver',items:[{name:'Oil, cod liver',k:899,p:0,f:99.9,c:0,source:'CoFID',match_score:38}],diagnostics:['USDA 429','OFF 503']},
 'Соус тартар':{english_query:'Tartar sauce',items:[{name:'Tartare sauce',k:299,p:1.3,f:24.6,c:17.9,source:'CoFID (Великобритания)',match_score:38}],diagnostics:[]}
};
const dummy={replaceChildren(){},append(){},addEventListener(){},setAttribute(){},getAttribute(){return null},hidden:true,textContent:'',value:'',classList:{add(){},remove(){},toggle(){}},style:{setProperty(){}}};
const doc={getElementById:()=>dummy,addEventListener(){},querySelector:()=>null,querySelectorAll:()=>[],createElement:()=>({...dummy})};
const context={document:doc,window:{visualViewport:null,matchMedia:()=>({matches:true})},console,setTimeout,clearTimeout,AbortController,FormData,URL,crypto:globalThis.crypto,
 fetch:async(_url,opt)=>({ok:true,json:async()=>({ok:true,results:JSON.parse(opt.body).queries.map(query=>({query,...(records[query]||{items:[]})}))})})};
vm.createContext(context);
let app=fs.readFileSync('my-food/site/app.js','utf8');app=app.slice(0,app.indexOf('(async()=>{try{db=await openDB();'));
vm.runInContext(app,context);
const {resolveCloudDishes,nutritionFor,canSaveDish,localWholeMatch}=vm.runInContext('({resolveCloudDishes,nutritionFor,canSaveDish,localWholeMatch})',context);
assert.equal(localWholeMatch('Печень трески').k,525);
assert.equal(localWholeMatch('Печень трески сырая').k,553);
const plan=(name,grams)=>({name,kind:'prepared',main:name,main_portion:String(grams)+' г',main_weight_g:grams,
 items:[{name,portion:String(grams)+' г',weight_g:grams,weight_estimated:false}],additions:[]});
const result=await resolveCloudDishes({food:{dishes:[plan('Яйца',100),plan('Печень трески',20),plan('Соус тартар',10)]}},'text');
assert.equal(result.length,3);
const cod=result.find(x=>x.name==='Печень трески');
assert(cod,'Cod liver dish present');
assert.equal(cod.manual.grams,20);
assert.equal(cod.manual.k,105);
assert.equal(cod.manual.p,1.2);
assert(Math.abs(cod.manual.f-11.092)<1e-8);
assert.equal(cod.manual.c,0);
assert.match(cod.nutritionSource,/JUOR/);
assert(cod.nutritionApproximate,'Generic canned liver reference is approximate');
assert.equal(cod.items.length,0,'Whole food avoids double-counting');
assert(result.every(canSaveDish),'All three foods saveable during USDA 429 + OFF 503');
assert(result[0].manual.k>0 && result[2].manual.k>0);
const rejected=nutritionFor('Печень трески',new Map([['Печень трески',records['Печень трески']]]),true);
assert.equal(rejected.k,525);
assert(!/cod liver oil|oil, cod liver/i.test(rejected.name||''));
const raw=nutritionFor('Печень трески сырая',new Map(),true);
assert.equal(raw.k,553);
console.log('PASS: 3 foods save with proper K/B/F/C despite USDA 429 / OFF 503; no cod liver oil substitution');
