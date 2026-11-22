import assert from 'node:assert/strict';
import worker from '../worker/worker.js';
// Real endpoints may fail. Test the durable built-in published reference
// without contacting third-party databases.
const originalFetch=globalThis.fetch;
globalThis.fetch=async()=>({ok:false,status:429,headers:new Headers({'content-type':'application/json'}),text:async()=>'{"error":"OVER_RATE_LIMIT"}'});
try {
 const request=new Request('https://food-ai-inference.evpoluyanov.workers.dev/nutrition-search?q=%D0%9F%D0%B5%D1%87%D0%B5%D0%BD%D1%8C%20%D1%82%D1%80%D0%B5%D1%81%D0%BA%D0%B8');
 const r=await worker.fetch(request,{AI:null});
 assert.equal(r.status,200);
 const data=await r.json();
 const liver=data.items.find(x=>/печень трески/i.test(x.name_ru||'') && !/\boil\b/i.test(x.name||''));
 assert(liver,JSON.stringify(data).slice(0,600));
 assert.equal(liver.k,525);assert.equal(liver.p,6);assert.equal(liver.f,55.46);assert.equal(liver.c,0);
 assert.equal(liver.reference_fallback,true);
 const oilResponse=await worker.fetch(new Request('https://food-ai-inference.evpoluyanov.workers.dev/nutrition-search?q=cod%20liver%20oil'),{AI:null});
 const oilData=await oilResponse.json();
 assert(!oilData.items.some(x=>x.reference_fallback && x.name==='Cod liver, canned in natural fat'));
 console.log('PASS: public databases unavailable; edible cod liver reference remains; cod liver oil is distinct');
} finally {globalThis.fetch=originalFetch}
