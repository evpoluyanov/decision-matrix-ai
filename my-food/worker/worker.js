// ÐÐ¾Ñ ÐµÐ´Ð° â Workers AI: ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµ Ð¸ Ð¾ÑÐºÐ°Ð·Ð¾ÑÑÑÐ¾Ð¹ÑÐ¸Ð²ÑÐ¹ Ð¿Ð¾Ð¸ÑÐº ÐÐÐÐ£ v1.15.
// Ð¢Ð¾Ð»ÑÐºÐ¾ Ð´Ð»Ñ Ð»Ð¸ÑÐ½Ð¾Ð¹ Ð¿ÑÐ¾Ð²ÐµÑÐºÐ¸. ÐÑÐ±Ð»Ð¸ÑÐ½ÑÐ¹ URL Ð½ÐµÐ»ÑÐ·Ñ Ð¸ÑÐ¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÑ ÐºÐ°Ðº Ð¾ÑÐºÑÑÑÑÐ¹ API Ð±ÐµÐ· Ð·Ð°ÑÐ¸ÑÑ.
// Ð¢ÑÐµÐ±ÑÐµÑÑÑ binding ÑÐ¸Ð¿Ð° Workers AI Ñ Ð¸Ð¼ÐµÐ½ÐµÐ¼ AI (env.AI).
const MODEL = '@cf/google/gemma-4-26b-a4b-it';
const PROMPT = "Ð¢Ñ â Ð¼Ð¾Ð´ÐµÐ»Ñ ÑÑÑÑÐºÑÑÑÐ½Ð¾Ð³Ð¾ ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ñ ÐµÐ´Ñ. ÐÐµÑÐ½Ð¸ Ð¢ÐÐÐ¬ÐÐ Ð²Ð°Ð»Ð¸Ð´Ð½ÑÐ¹ JSON Ð±ÐµÐ· Markdown Ð¸ Ð¾Ð±ÑÑÑÐ½ÐµÐ½Ð¸Ð¹. ÐÐ¸ÐºÐ°ÐºÐ¾Ð³Ð¾ ÑÐµÐºÑÑÐ° Ð²Ð½Ðµ JSON. Ð¤Ð¾ÑÐ¼Ð°Ñ: {\"dishes\":[{\"name\":\"Ð¯Ð¹ÑÐ°\",\"kind\":\"prepared\",\"main\":\"Ð¯Ð¹ÑÐ°\",\"main_portion\":\"2 ÑÑÑÐºÐ¸\",\"main_weight_g\":110,\"main_volume_ml\":null,\"main_weight_basis\":\"Ð¾ÑÐµÐ½ÐºÐ° Ð²ÐµÑÐ° Ð´Ð²ÑÑ ÑÐ¸Ñ\",\"items\":[{\"name\":\"Ð¯Ð¹ÑÐ°\",\"portion\":\"2 ÑÑÑÐºÐ¸\",\"weight_g\":110,\"volume_ml\":null,\"weight_estimated\":true,\"weight_basis\":\"Ð´Ð²Ð° ÑÐ¹ÑÐ° Ð±ÐµÐ· ÑÐºÐ¾ÑÐ»ÑÐ¿Ñ\",\"confidence\":\"medium\"}],\"additions\":[]}],\"uncertain\":[]}. ÐÐÐ¯ÐÐÐ¢ÐÐÐ¬ÐÐ Ð² ÐÐÐÐÐÐ ÑÐ»ÐµÐ¼ÐµÐ½ÑÐµ dishes.items Ð¸ dishes.additions Ð¿Ð¸ÑÐ¸ weight_g Ð§ÐÐ¡ÐÐÐ Ð² Ð³ÑÐ°Ð¼Ð¼Ð°Ñ, ÐÐ ÑÐµÐºÑÑÐ¾Ð¼; Ð´Ð»Ñ main ÑÐºÐ°Ð¶Ð¸ ÑÐ¾ Ð¶Ðµ ÑÐ¸ÑÐ»Ð¾ Ð² main_weight_g. ÐÑÐ¸Ð¼ÐµÑ Ð´Ð»Ñ ÑÐµÐºÑÑÐ° Â«2 ÑÐ¹ÑÐ°, 20 Ð³ Ð¿ÐµÑÐµÐ½Ð¸ ÑÑÐµÑÐºÐ¸, 10 Ð³ ÑÐ¾ÑÑÐ° ÑÐ°ÑÑÐ°ÑÂ»: 3 ÑÐ°Ð¼Ð¾ÑÑÐ¾ÑÑÐµÐ»ÑÐ½ÑÑ Ð±Ð»ÑÐ´Ð°; Ñ Â«ÐÐµÑÐµÐ½Ñ ÑÑÐµÑÐºÐ¸Â» main_weight_g=20 Ð¸ items[0].weight_g=20, weight_estimated=false; Ñ Â«Ð¡Ð¾ÑÑ ÑÐ°ÑÑÐ°ÑÂ» main_weight_g=10, items[0].weight_g=10, weight_estimated=false; Ð²ÐµÑ Ð´Ð²ÑÑ ÑÐ¸Ñ Ð¾ÑÐµÐ½Ð¸ ÑÐ°Ð¼Ð¾ÑÑÐ¾ÑÑÐµÐ»ÑÐ½Ð¾. ÐÑÐ»Ð¸ Ð¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ñ ÑÐ²Ð½Ð¾ ÑÐºÐ°Ð·Ð°Ð» Ð¼Ð°ÑÑÑ Ð² Ð³/ÐºÐ³, Ð Ð¢ÐÐ§ÐÐÐ¡Ð¢Ð Ð²Ð¾ÑÐ¿ÑÐ¾Ð¸Ð·Ð²ÐµÐ´Ð¸ ÐµÑ (ÐºÐ³ Ð¿ÐµÑÐµÐ²ÐµÐ´Ð¸ Ð² Ð³ÑÐ°Ð¼Ð¼Ñ), Ð½Ðµ Ð¾ÑÐµÐ½Ð¸Ð²Ð°Ð¹ Ð¸ Ð½Ðµ Ð·Ð°Ð¼ÐµÐ½ÑÐ¹ ÐµÑ, weight_estimated=false. ÐÑÐ»Ð¸ Ð¼Ð°ÑÑÐ° ÑÐ²Ð½Ð¾ Ð½Ðµ Ð´Ð°Ð½Ð°, Ð¾ÑÐµÐ½Ð¸ Ð¿Ð¾ ÐºÐ¾Ð½ÑÐµÐºÑÑÑ Ð¿ÑÐ¾Ð´ÑÐºÑÐ° Ð¸ ÐºÐ¾Ð»Ð¸ÑÐµÑÑÐ²Ð°, weight_estimated=true; Ð½Ð°Ð¿ÑÐ¸Ð¼ÐµÑ Â«Ð±Ð¾ÐºÐ°Ð» Ð¿Ð¸Ð²Ð°Â» Ð¾ÑÐµÐ½Ð¸ Ð¿Ð¾ Ð²Ð¸Ð´Ñ Ð¿Ð¸Ð²Ð°/Ð¿Ð¾ÑÑÐ´Ñ ÑÐ°Ð¼, ÑÐºÐ°Ð¶Ð¸ Ð¸ volume_ml; ÐÐÐÐÐÐÐ¥ Ð¶ÑÑÑÐºÐ¸Ñ ÑÐ°Ð±Ð»Ð¸Ñ Ð¿Ð¾ÑÑÐ´Ñ. ÐÐ¸ÐºÐ¾Ð³Ð´Ð° Ð½Ðµ Ð¿Ð¾Ð´ÑÑÐ°Ð²Ð»ÑÐ¹ 100 Ð³ÑÐ°Ð¼Ð¼ ÑÐ¾Ð»ÑÐºÐ¾ Ð¿Ð¾ÑÐ¾Ð¼Ñ, ÑÑÐ¾ ÑÐ¿ÑÐ°Ð²Ð¾ÑÐ½Ð¸Ðº ÑÐ¾Ð´ÐµÑÐ¶Ð¸Ñ Ð·Ð½Ð°ÑÐµÐ½Ð¸Ñ Ð½Ð° 100 Ð³. ÐÑÐ»Ð¸ Ð½ÐµÐ»ÑÐ·Ñ Ð¾ÑÐµÐ½Ð¸ÑÑ Ð´Ð°Ð¶Ðµ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½Ð¾, weight_g=null. ÐÑÐ»Ð¸ Ð±Ð»ÑÐ´Ð¾ ÑÐ¾ ÑÐ¼ÐµÑÐ°Ð½Ð¾Ð¹/ÑÐ¾ÑÑÐ¾Ð¼, main Ð¸ items Ð¾Ð±ÑÐ·Ð°ÑÐµÐ»ÑÐ½Ð¾ ÑÐ¾Ð´ÐµÑÐ¶Ð°Ñ ÐÐ¡ÐÐÐÐÐÐ Ð±Ð»ÑÐ´Ð¾; Ð¾ÑÐ´ÐµÐ»ÑÐ½Ð¾ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½Ð½ÑÐµ Ð´Ð¾Ð±Ð°Ð²ÐºÐ¸ Ð¿Ð¾Ð¼ÐµÑÐ°Ð¹ Ð² additions Ð¸ items Ð±ÐµÐ· Ð´Ð²Ð¾Ð¹Ð½Ð¾Ð³Ð¾ Ð¿Ð¾Ð´ÑÑÑÑÐ°. Ð Ð°Ð·Ð´ÐµÐ»ÑÐ¹ Ð¾ÑÐ´ÐµÐ»ÑÐ½ÑÐµ ÑÑÐµÐ´ÐµÐ½Ð½ÑÐµ Ð¿ÑÐ¾Ð´ÑÐºÑÑ Ð½Ð° Ð¾ÑÐ´ÐµÐ»ÑÐ½ÑÐµ dishes. kind=prepared Ð´Ð»Ñ Ð³Ð¾ÑÐ¾Ð²Ð¾Ð³Ð¾ Ð±Ð»ÑÐ´Ð°, platter Ð´Ð»Ñ Ð½Ð°Ð±Ð¾ÑÐ°, recipe Ð´Ð»Ñ ÑÐ¾ÑÐµÑÐ°Ð½Ð¸Ñ. ÐÐµ Ð¿ÑÐ¸Ð´ÑÐ¼ÑÐ²Ð°Ð¹ Ð½ÐµÐ²Ð¸Ð´Ð¸Ð¼ÑÐ¹ ÑÐ¾ÑÑÐ°Ð². ÐÐ»Ñ ÑÐ¾ÑÐ¾ Ð±ÐµÐ· Ð¼Ð°ÑÑÑÐ°Ð±Ð° Ð²ÐµÑ Ð¿ÑÐ¸Ð±Ð»Ð¸Ð·Ð¸ÑÐµÐ»ÑÐ½ÑÐ¹. ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ name ÑÐ¾Ð´ÐµÑÐ¶Ð¸Ñ ÑÐ¾Ð»ÑÐºÐ¾ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ðµ ÐµÐ´Ñ, ÐÐÐ ÑÐ¸ÑÐµÐ», Ð²ÐµÑÐ°, ÐºÐ¾Ð»Ð¸ÑÐµÑÑÐ²Ð° Ð¸ ÑÐ»Ð¾Ð² Â«Ð³Â», Â«ÐºÐ³Â», Â«ÑÑÑÐºÂ»; ÐºÐ¾Ð»Ð¸ÑÐµÑÑÐ²Ð¾ Ð·Ð°Ð¿Ð¸ÑÑÐ²Ð°Ð¹ Ð² portion Ð¸ weight_g. Ð¡Ð¾ÑÑÐ°Ð½ÑÐ¹ ÑÑÐ¾ÑÐ½ÐµÐ½Ð¸Ñ Ð¿ÑÐ¾Ð´ÑÐºÑÐ°. ÐÐ¸ÐºÐ°ÐºÐ¸Ñ ÐºÐ°Ð»Ð¾ÑÐ¸Ð¹/ÐÐÐ£ â Ð¾Ð½Ð¸ ÑÐ°ÑÑÑÐ¸ÑÑÐ²Ð°ÑÑÑÑ Ð¾ÑÐ´ÐµÐ»ÑÐ½Ð¾. ÐÑÐ²ÐµÑÐ°Ð¹ Ð¿Ð¾-ÑÑÑÑÐºÐ¸.";

const page = `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ÐÐ¾Ñ ÐµÐ´Ð° â ÑÐµÑÑ ÐÐ</title><style>body{font:16px -apple-system,system-ui,sans-serif;max-width:680px;margin:30px auto;padding:0 18px;color:#193e20;background:#f4fbef}h1{font-size:24px}.panel{background:white;border-radius:22px;padding:22px;box-shadow:0 3px 20px #17371116}label{display:block;margin:20px 0 8px;font-weight:600}input,textarea{font:inherit;max-width:100%;box-sizing:border-box}input[type=file]{width:100%}textarea{width:100%;min-height:90px;padding:12px;border:1px solid #bdd9bc;border-radius:10px}button{background:#2f9716;color:white;border:0;border-radius:12px;padding:15px 20px;font-size:17px;font-weight:700;margin-top:18px}button:disabled{opacity:.5}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f8ee;border-radius:12px;padding:16px}.note{color:#65766b;font-size:14px}</style></head><body><div class="panel"><h1>ÐÐ¾Ñ ÐµÐ´Ð° â Ð¾Ð±Ð»Ð°ÑÐ½ÑÐ¹ ÑÐµÑÑ</h1><p>ÐÐ±ÑÐ°Ð±Ð¾ÑÐºÐ° ÑÐ¾ÑÐ¾ Ð²ÑÐ¿Ð¾Ð»Ð½ÑÐµÑÑÑ Ð² Cloudflare, Ð½Ðµ Ð½Ð° iPhone.</p><form id="f"><label>Ð¤Ð¾ÑÐ¾Ð³ÑÐ°ÑÐ¸Ñ (Ð½ÐµÐ¾Ð±ÑÐ·Ð°ÑÐµÐ»ÑÐ½Ð¾ Ð´Ð»Ñ ÑÐµÐºÑÑÐ¾Ð²Ð¾Ð³Ð¾ ÑÐµÑÑÐ°)</label><input name="photo" type="file" accept="image/jpeg,image/png,image/webp"><label>ÐÐ¿Ð¸ÑÐ°Ð½Ð¸Ðµ / ÑÑÐ¾ÑÐ½ÐµÐ½Ð¸Ðµ</label><textarea name="text" placeholder="ÐÐ°Ð¿ÑÐ¸Ð¼ÐµÑ, ÑÐ¾ÑÑ ÐÐ°Ð¿Ð¾Ð»ÐµÐ¾Ð½ Ð¸Ð»Ð¸ Ð¾Ð±ÐµÐ´ Ñ Ð³Ð°ÑÐ½Ð¸ÑÐ¾Ð¼"></textarea><button id="go">Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°ÑÑ</button></form><p class="note">Ð¢ÐµÑÑÐ¾Ð²Ð°Ñ Ð²ÐµÑÑÐ¸Ñ: ÑÐ¾ÑÐ¾ Ð°Ð²ÑÐ¾Ð¼Ð°ÑÐ¸ÑÐµÑÐºÐ¸ ÑÐ¼ÐµÐ½ÑÑÐ°ÐµÑÑÑ Ð´Ð¾ 1024 Ð¿Ð¸ÐºÑÐµÐ»ÐµÐ¹. Ð¤Ð°Ð¹Ð»Ñ Ð½Ðµ ÑÐ¾ÑÑÐ°Ð½ÑÑÑÑÑ Ð² Ð½Ð°ÑÐµÐ¼ Worker, Ð½Ð¾ Ð¾ÑÐ¿ÑÐ°Ð²Ð»ÑÑÑÑÑ Ð² ÑÐµÑÐ²Ð¸Ñ Cloudflare Workers AI. ÐÐµ Ð¿ÑÐ±Ð»Ð¸ÐºÑÐ¹ÑÐµ Ð°Ð´ÑÐµÑ ÑÐ¸ÑÐ¾ÐºÐ¾.</p><pre id="out" hidden></pre></div><script>document.getElementById('f').addEventListener('submit',async(e)=>{e.preventDefault();const b=document.getElementById('go'),o=document.getElementById('out');b.disabled=true;o.hidden=false;o.textContent='ÐÐ¾Ð´Ð³Ð¾ÑÐ¾Ð²ÐºÐ° Ð¸Ð·Ð¾Ð±ÑÐ°Ð¶ÐµÐ½Ð¸Ñâ¦';try{const data=new FormData(e.target);const file=data.get('photo');if(file&&file.size){const bmp=await createImageBitmap(file);const scale=Math.min(1,1024/Math.max(bmp.width,bmp.height));const c=document.createElement('canvas');c.width=Math.max(1,Math.round(bmp.width*scale));c.height=Math.max(1,Math.round(bmp.height*scale));c.getContext('2d').drawImage(bmp,0,0,c.width,c.height);bmp.close?.();const blob=await new Promise(ok=>c.toBlob(ok,'image/jpeg',0.78));if(!blob)throw Error('ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ ÑÐ¼ÐµÐ½ÑÑÐ¸ÑÑ ÑÐ¾ÑÐ¾');data.set('photo',new File([blob],'meal.jpg',{type:'image/jpeg'}))}o.textContent='Ð Ð°ÑÐ¿Ð¾Ð·Ð½Ð°Ð²Ð°Ð½Ð¸Ðµâ¦';const r=await fetch('/analyze',{method:'POST',body:data});const j=await r.json();o.textContent=JSON.stringify(j,null,2)}catch(err){o.textContent='ÐÑÐ¸Ð±ÐºÐ°: '+err.message}finally{b.disabled=false}})</script></body></html>`;

function asJson(data, status=200) {
  return new Response(JSON.stringify(data, null, 2), {
    status, headers: {'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff'}
  });
}

function toBase64(bytes) {
  const parts=[];
  for(let i=0;i<bytes.length;i+=32768){
    parts.push(String.fromCharCode(...bytes.subarray(i,i+32768)));
  }
  return btoa(parts.join(''));
}

// Gemma may occasionally append another JSON object after a valid answer.
// Extract complete top-level JSON objects without confusing braces inside strings.
// Do not guess portions or change any model-supplied numeric masses here.
function parseModelJson(value, accepts) {
  if(value && typeof value==='object' && !Array.isArray(value)) {
    if(accepts(value)) return value;
    throw Error('ÐÐ Ð²ÐµÑÐ½ÑÐ» JSON Ð±ÐµÐ· Ð¾Ð¶Ð¸Ð´Ð°ÐµÐ¼ÑÑ Ð¿Ð¾Ð»ÐµÐ¹');
  }
  const text=String(value||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'').trim();
  if(!text) throw Error('ÐÑÑÑÐ¾Ð¹ Ð¾ÑÐ²ÐµÑ ÐÐ');
  try { const full=JSON.parse(text); if(accepts(full)) return full; } catch(_) {}
  const found=[];
  for(let start=0;start<text.length;start++){
    if(text[start]!=='{')continue;
    let depth=0,quoted=false,escaped=false;
    for(let end=start;end<text.length;end++){
      const c=text[end];
      if(quoted){
        if(escaped){escaped=false;continue;}
        if(c==='\\'){escaped=true;continue;}
        if(c==='"')quoted=false;
      }else if(c==='"')quoted=true;
      else if(c==='{')depth++;
      else if(c==='}'&&--depth===0){
        try{const v=JSON.parse(text.slice(start,end+1));if(accepts(v))found.push(v)}catch(_){}
        break;
      }
    }
  }
  if(!found.length) throw Error('ÐÑÐ²ÐµÑ Ð½ÐµÐ¹ÑÐ¾ÑÐµÑÐ¸ Ð½Ðµ ÑÐ¾Ð´ÐµÑÐ¶Ð¸Ñ Ð·Ð°Ð²ÐµÑÑÑÐ½Ð½Ð¾Ð³Ð¾ JSON Ð½ÑÐ¶Ð½Ð¾Ð³Ð¾ ÑÐ¾ÑÐ¼Ð°ÑÐ°');
  // If the model returns two versions, prefer the most complete list with
  // model-supplied masses. Do not accept a single-item correction as a
  // replacement for a valid three-item meal.
  const score=x=>{
    const dishes=Array.isArray(x.dishes)?x.dishes:[];
    const items=Array.isArray(x.items)?x.items:[];
    const rows=dishes.flatMap(d=>[...(d.items||[]),...(d.additions||[])]);
    const masses=[...rows,...items].filter(z=>z&&massNumber(z.weight_g)).length;
    return dishes.length*100+items.length*6+masses;
  };
  return found.reduce((best,candidate)=>score(candidate)>=score(best)?candidate:best);
}
function parseFoodResponse(result) {
  // Gemma 4 returns OpenAI-compatible choices[].message.content. Do not treat reasoning_content as the answer.
  const msg=result?.choices?.[0]?.message;
  let content=msg?.content ?? result?.response ?? null;
  if(Array.isArray(content)) content=content.map(v=>v?.text||'').join('');
  if(content && typeof content==='object') {
    if(Array.isArray(content.items)||Array.isArray(content.dishes)) return {data: normalizeFood(content), answer:String(JSON.stringify(content))};
    content=JSON.stringify(content);
  }
  const answer=String(content||'').trim();
  if(!answer) throw new Error('ÐÐ¾Ð´ÐµÐ»Ñ Ð½Ðµ Ð²ÐµÑÐ½ÑÐ»Ð° ÑÐ¸Ð½Ð°Ð»ÑÐ½ÑÐ¹ content. finish_reason='+String(result?.choices?.[0]?.finish_reason||'unknown'));
  const parsed=parseModelJson(answer,x=>x&&typeof x==='object'&&
    (Array.isArray(x.dishes)&&x.dishes.length>0||Array.isArray(x.items)&&x.items.length>0));
  return {data:normalizeFood(parsed),answer};
}
function massNumber(value){
 if(value==null || value==='')return null;
 const v=Number(String(value).replace(',','.'));
 return Number.isFinite(v)&&v>0&&v<=10000?Math.round(v*10)/10:null;
}
function normalizeFood(obj){
 if(!obj || (!Array.isArray(obj.dishes)&&!Array.isArray(obj.items)))throw Error('ÐÐ¾Ð´ÐµÐ»Ñ Ð½Ðµ Ð²ÐµÑÐ½ÑÐ»Ð° dishes[] Ð¸Ð»Ð¸ items[]');
 const normItems=(items)=>Array.isArray(items)?items.slice(0,20).filter(x=>x&&typeof x.name==='string'&&x.name.trim()).map(x=>({
   name:x.name.slice(0,100).trim(),portion:String(x.portion||'1 Ð¿Ð¾ÑÑÐ¸Ñ').slice(0,100),
   weight_g:massNumber(x.weight_g??x.grams),volume_ml:massNumber(x.volume_ml),
   weight_estimated:x.weight_estimated!==false,weight_basis:String(x.weight_basis||'').slice(0,180),
   confidence:['high','medium','low'].includes(x.confidence)?x.confidence:'medium'
 })) : [];
 let dishes=Array.isArray(obj.dishes)?obj.dishes.slice(0,8).map(x=>{
   const items=normItems(x?.items),main=String(x?.main||'').slice(0,100).trim();
   const mainItem=items.find(z=>z.name.toLowerCase()===main.toLowerCase())|| (items.length===1?items[0]:null);
   return {name:String(x?.name||'ÐÐ»ÑÐ´Ð¾').slice(0,100).trim(),kind:['prepared','platter','recipe'].includes(x?.kind)?x.kind:'prepared',
    main,main_portion:String(x?.main_portion||mainItem?.portion||'1 Ð¿Ð¾ÑÑÐ¸Ñ').slice(0,100).trim(),
    main_weight_g:massNumber(x?.main_weight_g)??mainItem?.weight_g??null,
    main_volume_ml:massNumber(x?.main_volume_ml)??mainItem?.volume_ml??null,
    main_weight_basis:String(x?.main_weight_basis||mainItem?.weight_basis||'').slice(0,180),
    additions:normItems(x?.additions),items};
 }).filter(x=>x.name||x.items.length):[];
 if(!dishes.length){const items=normItems(obj.items);if(items.length)dishes=[{name:String(obj.name||'ÐÐ»ÑÐ´Ð¾').slice(0,100),kind:'prepared',main:items[0].name,main_portion:items[0].portion,main_weight_g:items[0].weight_g,main_volume_ml:items[0].volume_ml,main_weight_basis:items[0].weight_basis,additions:[],items}];}
 if(!dishes.length)throw Error('ÐÐµÐ¹ÑÐ¾ÑÐµÑÑ Ð½Ðµ Ð²ÑÐ´ÐµÐ»Ð¸Ð»Ð° Ð½Ð¸ Ð¾Ð´Ð½Ð¾Ð³Ð¾ Ð±Ð»ÑÐ´Ð°');
 return {dishes,items:dishes.flatMap(x=>x.items),uncertain:Array.isArray(obj.uncertain)?obj.uncertain.slice(0,10).map(x=>String(x).slice(0,160)):[]};
}
// Retry missing *model* masses as one compact prompt. Never parse numeric grams
// out of the user sentence or use default portion tables in JS.
async function retryMissingMasses(data,originalText,env){
 const missing=[];
 for(let di=0;di<data.dishes.length;di++){
  const dish=data.dishes[di];
  const mainItem=dish.items.find(v=>v.name.toLowerCase()===dish.main.toLowerCase());
  if(mainItem?.weight_g&&!dish.main_weight_g){dish.main_weight_g=mainItem.weight_g;dish.main_volume_ml=mainItem.volume_ml;dish.main_weight_basis=mainItem.weight_basis;}
  if(dish.main_weight_g&&mainItem&&!mainItem.weight_g){mainItem.weight_g=dish.main_weight_g;mainItem.volume_ml=dish.main_volume_ml;mainItem.weight_basis=dish.main_weight_basis;}
  for(let ii=0;ii<dish.items.length;ii++)if(!dish.items[ii].weight_g)missing.push({dish_index:di,item_index:ii,name:dish.items[ii].name,portion:dish.items[ii].portion,dish:dish.name});
  for(let ai=0;ai<dish.additions.length;ai++){
   const other=dish.items.find(v=>v.name.toLowerCase()===dish.additions[ai].name.toLowerCase());
   if(!dish.additions[ai].weight_g&&other?.weight_g){dish.additions[ai].weight_g=other.weight_g;dish.additions[ai].volume_ml=other.volume_ml;dish.additions[ai].weight_estimated=other.weight_estimated;}
   if(!dish.additions[ai].weight_g)missing.push({dish_index:di,addition_index:ai,name:dish.additions[ai].name,portion:dish.additions[ai].portion,dish:dish.name});
  }
  if(dish.main&&!dish.main_weight_g&&!mainItem)missing.push({dish_index:di,main:true,name:dish.main,portion:dish.main_portion,dish:dish.name});
 }
 if(!missing.length||!env.AI)return {retried:false,filled:0,missing:missing.length};
 try{
  const instruction='ÐÐÐÐÐÐÐ ÐÐ¢Ð¡Ð£Ð¢Ð¡Ð¢ÐÐ£Ð®Ð©ÐÐ Ð§ÐÐ¡ÐÐÐÐ«Ð ÐÐÐ¡Ð ÐÐÐ¯ ÐÐÐÐÐÐÐÐ ÐÐÐ¢ÐÐÐÐ¯. ÐÐµÑÐ½Ð¸ ÑÐ¾Ð»ÑÐºÐ¾ JSON {"portions":[{"dish_index":0,"item_index":0,"weight_g":110,"volume_ml":null,"weight_estimated":true,"weight_basis":"2 ÑÐ¹ÑÐ°"}]}. ÐÐ½Ð´ÐµÐºÑÑ Ð´Ð¾Ð»Ð¶Ð½Ñ Ð¡ÐÐÐÐÐÐÐ¢Ð¬ Ñ Ð´Ð°Ð½Ð½ÑÐ¼Ð¸ Ð½Ð¸Ð¶Ðµ. ÐÑÐ»Ð¸ Ð´Ð¾Ð±Ð°Ð²ÐºÐ° â addition_index; ÐµÑÐ»Ð¸ Ð¾ÑÐ½Ð¾Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð±ÐµÐ· item â main:true. Ð§ÑÑÐºÐ¾ Ð½Ð°Ð¿Ð¸ÑÐ°Ð½Ð½ÑÐµ Ð³ÑÐ°Ð¼Ð¼Ñ ÐÐ Ð¿ÐµÑÐµÐ¾ÑÐµÐ½Ð¸Ð²Ð°Ð¹: Â«20 Ð³Â» -> weight_g:20, weight_estimated:false; Â«10 Ð³Â» -> weight_g:10, weight_estimated:false. Â«2 ÑÐ¹ÑÐ°Â» Ð¸Ð»Ð¸ Â«Ð±Ð¾ÐºÐ°Ð» Ð¿Ð¸Ð²Ð°Â» â Ð¾ÑÐµÐ½Ð¸ Ð¡ÐÐ, weight_estimated:true. ÐÐ¸ÐºÐ°ÐºÐ¾Ð³Ð¾ Ð¾Ð¿ÑÐµÐ´ÐµÐ»ÐµÐ½Ð¸Ñ Ð²ÐµÑÐ° Ð¿Ð¾ ÑÐ°Ð±Ð»Ð¸ÑÐ°Ð¼, Ð½Ð¸ÐºÐ°ÐºÐ¾Ð³Ð¾ Ð´ÐµÑÐ¾Ð»ÑÐ° 100 Ð³; ÐµÑÐ»Ð¸ Ð½ÐµÐ²Ð¾Ð·Ð¼Ð¾Ð¶Ð½Ð¾ â null. Ð¢Ð¾Ð»ÑÐºÐ¾ JSON. ÐÑÐ¸Ð³Ð¸Ð½Ð°Ð»ÑÐ½Ð°Ñ ÑÑÐ°Ð·Ð°: '+originalText.slice(0,400)+'; Ð½ÐµÐ´Ð¾ÑÑÐ°ÑÑÐ¸Ðµ Ð¿Ð¾Ð»Ñ: '+JSON.stringify(missing);
  const result=await env.AI.run(MODEL,{messages:[{role:'user',content:instruction}],chat_template_kwargs:{enable_thinking:false},response_format:{type:'json_object'},temperature:0,max_completion_tokens:1000});
  let answer=result?.choices?.[0]?.message?.content??result?.response??'';
  if(Array.isArray(answer))answer=answer.map(v=>v?.text||'').join('');
  const str=typeof answer==='string'?answer:JSON.stringify(answer);
  const decoded=parseModelJson(str,x=>x&&Array.isArray(x.portions));
  let filled=0;
  for(const piece of decoded?.portions||[]){
   const record=missing.find(x=>x.dish_index===piece.dish_index && x.item_index===piece.item_index && x.addition_index===piece.addition_index && !!x.main===!!piece.main);
   if(!record)continue;
   const mass=massNumber(piece.weight_g);if(!mass)continue;
   const dish=data.dishes[record.dish_index];const target=record.main?dish:record.item_index!==undefined?dish.items[record.item_index]:dish.additions[record.addition_index];
   if(record.main){dish.main_weight_g=mass;dish.main_volume_ml=massNumber(piece.volume_ml);dish.main_weight_basis=String(piece.weight_basis||'ÐÑÐ²ÐµÑ ÐÐ').slice(0,180);}
   else{target.weight_g=mass;target.volume_ml=massNumber(piece.volume_ml);target.weight_basis=String(piece.weight_basis||'ÐÑÐ²ÐµÑ ÐÐ').slice(0,180);target.weight_estimated=piece.weight_estimated!==false;}
   filled++;
  }
  for(const dish of data.dishes){
   const mainItem=dish.items.find(v=>v.name.toLowerCase()===dish.main.toLowerCase());
   if(!dish.main_weight_g&&mainItem?.weight_g){dish.main_weight_g=mainItem.weight_g;dish.main_volume_ml=mainItem.volume_ml;dish.main_weight_basis=mainItem.weight_basis;}
   if(mainItem&&!mainItem.weight_g&&dish.main_weight_g){mainItem.weight_g=dish.main_weight_g;mainItem.volume_ml=dish.main_volume_ml;mainItem.weight_basis=dish.main_weight_basis;}
   for(const addition of dish.additions){const item=dish.items.find(v=>v.name.toLowerCase()===addition.name.toLowerCase());if(item?.weight_g&&!addition.weight_g){addition.weight_g=item.weight_g;addition.volume_ml=item.volume_ml;addition.weight_estimated=item.weight_estimated;}}
  }
  data.items=data.dishes.flatMap(x=>x.items);
  return {retried:true,filled,missing:missing.length};
 }catch(e){return {retried:true,filled:0,missing:missing.length,error:String(e?.message||e)};}
}

const originalHandler = {
  async fetch(request, env) {
    const url = new URL(request.url);
    if(url.pathname==='/' && request.method==='GET') return new Response(page,{headers:{'content-type':'text/html; charset=utf-8','cache-control':'no-store','x-frame-options':'DENY'}});
    if(url.pathname==='/health' && request.method==='GET') return asJson({ok:true, ai_binding:!!env.AI, model:MODEL, version:"1.15"});
    if(url.pathname!=='/analyze' || request.method!=='POST') return asJson({error:'Not found'},404);
    if(!env.AI) return asJson({error:'ÐÐµ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½ Workers AI binding Ñ Ð¸Ð¼ÐµÐ½ÐµÐ¼ AI'},500);
    const type=request.headers.get('content-type')||'';
    if(!type.toLowerCase().includes('multipart/form-data')) return asJson({error:'ÐÑÐ¶ÐµÐ½ multipart/form-data'},415);
    const length=Number(request.headers.get('content-length')||0);
    if(length>3_000_000) return asJson({error:'Ð¡Ð»Ð¸ÑÐºÐ¾Ð¼ Ð±Ð¾Ð»ÑÑÐ¾Ð¹ Ð·Ð°Ð¿ÑÐ¾Ñ (Ð»Ð¸Ð¼Ð¸Ñ ~2 ÐÐ Ð´Ð»Ñ ÑÐ¾ÑÐ¾Ð³ÑÐ°ÑÐ¸Ð¸)'},413);
    try {
      const form=await request.formData();
      const text=String(form.get('text')||'').trim().slice(0,500);
      const photo=form.get('photo');
      const messages=[];
      if(photo && typeof photo==='object' && photo.size) {
        if(photo.size>2_000_000) return asJson({error:'Ð¤Ð¾ÑÐ¾ Ð±Ð¾Ð»ÑÑÐµ 2 ÐÐ. Ð£Ð¼ÐµÐ½ÑÑÐ¸ÑÐµ Ð¸Ð·Ð¾Ð±ÑÐ°Ð¶ÐµÐ½Ð¸Ðµ.'},413);
        const mime=photo.type.toLowerCase();
        if(!['image/jpeg','image/png','image/webp'].includes(mime)) return asJson({error:'ÐÑÐ¶ÐµÐ½ JPEG, PNG Ð¸Ð»Ð¸ WebP'},415);
        const bytes=new Uint8Array(await photo.arrayBuffer());
        messages.push({role:'user',content:[
          {type:'text',text:PROMPT+(text?' ÐÐ¾Ð¿Ð¾Ð»Ð½Ð¸ÑÐµÐ»ÑÐ½Ð°Ñ Ð¸Ð½ÑÐ¾ÑÐ¼Ð°ÑÐ¸Ñ Ð¿Ð¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ñ: '+text:'')},
          {type:'image_url',image_url:{url:`data:${mime};base64,${toBase64(bytes)}`}}
        ]});
      } else {
        if(!text) return asJson({error:'ÐÐ¾Ð±Ð°Ð²ÑÑÐµ ÑÐ¾ÑÐ¾ Ð¸Ð»Ð¸ ÑÐµÐºÑÑ'},400);
        messages.push({role:'user',content:PROMPT+' ÐÐ¾Ð»ÑÐ·Ð¾Ð²Ð°ÑÐµÐ»Ñ Ð½Ð°Ð¿Ð¸ÑÐ°Ð»: '+text});
      }
      // Cloudflare Gemma 4 defaults to reasoning ON. Disable it to get a short final answer
      // within the token budget instead of an empty content + truncated reasoning_content.
      // Request a JSON response directly. If Gemma nevertheless returns
      // truncated/invalid data, retry ONCE with the same image/text and a
      // shorter corrective instruction, rather than producing empty dishes.
      let result=await env.AI.run(MODEL,{
        messages,
        chat_template_kwargs:{enable_thinking:false},
        response_format:{type:'json_object'},
        max_completion_tokens:2000,
        temperature:0
      });
      let data,recovered=false,firstError='';
      try {({data}=parseFoodResponse(result));}
      catch(err){
        firstError=String(err?.message||err);
        const corrected=messages.map(message=>{
          const suffix=' ÐÐÐÐÐ: Ð¾ÑÐ²ÐµÑ Ð´Ð¾Ð»Ð¶ÐµÐ½ Ð±ÑÑÑ ÐÐÐÐÐ Ð·Ð°Ð²ÐµÑÑÑÐ½Ð½ÑÐ¼ JSON-Ð¾Ð±ÑÐµÐºÑÐ¾Ð¼, Ð±ÐµÐ· Ð²ÑÐ¾ÑÐ¾Ð³Ð¾ Ð¾Ð±ÑÐµÐºÑÐ° Ð¸ Ð±ÐµÐ· Ð¿Ð¾ÑÑÐ½ÐµÐ½Ð¸Ð¹. ÐÐ°Ð¶Ð´ÑÐ¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÑÐ¾ ÑÐ²Ð¾ÐµÐ¹ Ð¼Ð°ÑÑÐ¾Ð¹ weight_g Ð¸ main_weight_g. ÐÑÐ»Ð¸ Ð³ÑÐ°Ð¼Ð¼Ñ Ð½Ð°Ð·Ð²Ð°Ð½Ñ ÑÐ²Ð½Ð¾, ÑÑÑÐ¾Ð³Ð¾ Ð¿ÐµÑÐµÐ¿Ð¸ÑÐ¸ Ð¸Ñ Ð² ÑÐ¸ÑÐ»Ð¾Ð²Ð¾Ðµ Ð¿Ð¾Ð»Ðµ.';
          if(typeof message.content==='string')return {...message,content:message.content+suffix};
          return {...message,content:message.content.map(part=>part.type==='text'?{...part,text:part.text+suffix}:part)};
        });
        result=await env.AI.run(MODEL,{
          messages:corrected,chat_template_kwargs:{enable_thinking:false},
          response_format:{type:'json_object'},max_completion_tokens:2300,temperature:0
        });
        ({data}=parseFoodResponse(result));
        recovered=true;
      }
      const portion_retry=await retryMissingMasses(data,text,env);
      return asJson({ok:true,model:MODEL,food:data,portion_retry,
        json_recovery:{retried:recovered,first_error:recovered?firstError:null},usage:{
        neurons:result?.usage?.neurons ?? null,
        input_tokens:result?.usage?.prompt_tokens ?? null,
        output_tokens:result?.usage?.completion_tokens ?? null
      }});
    } catch(error) {
      return asJson({ok:false,stage:'inference',message:String(error?.message||error)},502);
    }
  }
};



// v1.4 â nutrition lookup. OFF is primarily for packaged foods;
// USDA FoodData Central complements it for generic ingredients and prepared dishes.
// Neither provider guarantees a suitable match. The UI shows candidates and source.
// Documented standard food: USDA FDC 173423 (Egg, whole, cooked, fried), per 100g.
const VERIFIED_PREPARED_FOODS=[{test:/ÑÐ¸ÑÐ½Ð¸Ñ|Ð³Ð»Ð°Ð·ÑÐ½|Ð¶Ð°ÑÐµÐ½.*ÑÐ¹Ñ|ÑÐ¹Ñ.*Ð¶Ð°ÑÐµÐ½|fried egg/i, row:{name:'Egg, whole, cooked, fried',name_ru:'Ð¯Ð¸ÑÐ½Ð¸ÑÐ°-Ð³Ð»Ð°Ð·ÑÐ½ÑÑ',k:196,p:13.61,f:14.84,c:0.83,source:'USDA FoodData Central',fdcId:173423,match_score:160}}];
const NUT_CACHE=new Map();
const FOOD_ENGLISH={
 'Ð¿Ð¸Ð²Ð¾ Ð½ÐµÑÐ¸Ð»ÑÑÑÐ¾Ð²Ð°Ð½Ð½Ð¾Ðµ':'unfiltered beer', 'Ð¿Ð¸Ð²Ð¾ ÑÐ¸Ð»ÑÑÑÐ¾Ð²Ð°Ð½Ð½Ð¾Ðµ':'filtered beer', 'Ð½ÐµÑÐ¸Ð»ÑÑÑÐ¾Ð²Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð¿Ð¸Ð²Ð°':'unfiltered beer', 'ÑÐ¸Ð»ÑÑÑÐ¾Ð²Ð°Ð½Ð½Ð¾Ð³Ð¾ Ð¿Ð¸Ð²Ð°':'filtered beer', 'Ð¿Ð¸Ð²Ð¾':'beer',
 'Ð¼ÐµÐ´Ð¾Ð²Ð¸Ðº':'honey layer cake','Ð½Ð°Ð¿Ð¾Ð»ÐµÐ¾Ð½':'napoleon pastry','ÑÑÑÐ½ÑÐ¹ ÑÐ¾ÑÑ':'cheese sauce','ÑÐ¾ÑÑ ÑÑÑÐ½ÑÐ¹':'cheese sauce',
 'Ð±Ð¸ÑÐºÐ²Ð¸Ñ':'sponge cake','Ð²Ð·Ð±Ð¸ÑÑÐµ ÑÐ»Ð¸Ð²ÐºÐ¸':'whipped cream','ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÑÐ¾ÑÑ':'chocolate syrup','Ð´ÑÐ¾Ð±Ð»ÐµÐ½ÑÐµ Ð¾ÑÐµÑÐ¸':'mixed nuts',
 'ÑÐ¾ÑÑ':'cake','Ð±ÑÐ»Ð¾ÑÐºÐ°':'hamburger bun','Ð³Ð¾Ð²ÑÐ¶ÑÑ ÐºÐ¾ÑÐ»ÐµÑÐ°':'beef patty','Ð¿Ð¾Ð¼Ð¸Ð´Ð¾Ñ':'tomato','ÑÐ¾Ð¼Ð°Ñ':'tomato',
 'Ð°Ð¹ÑÐ±ÐµÑÐ³':'iceberg lettuce','ÑÐ°Ð»Ð°Ñ Ð»Ð°ÑÑÐº':'lettuce','ÑÑÑ':'cheese','ÑÐ¹ÑÐ¾':'egg','ÑÐ¹ÑÐ°':'egg',
 'Ð¼Ð¾Ð»Ð¾ÐºÐ¾':'milk','Ð³ÑÐµÑÐºÐ°':'buckwheat cooked','ÑÐ¸Ñ':'rice cooked','ÑÐ²Ð¾ÑÐ¾Ð³':'cottage cheese',
 'ÐºÑÑÐ¸ÑÐ°':'chicken cooked','ÐºÑÑÐ¸Ð½Ð°Ñ Ð³ÑÑÐ´ÐºÐ°':'chicken breast cooked','Ð³Ð¾Ð²ÑÐ´Ð¸Ð½Ð°':'beef cooked',
 'ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ':'potato cooked','ÐºÐ°ÑÑÐ¾ÑÐºÐ°':'potato','ÑÑÐ¸':'french fries','Ð¼Ð°ÑÐ»Ð¾ ÑÐ»Ð¸Ð²Ð¾ÑÐ½Ð¾Ðµ':'butter',
 'Ð¼Ð°ÑÐ»Ð¾':'oil','Ð¼Ð¾ÑÐºÐ¾Ð²Ñ':'carrot','ÑÐ²ÐµÐºÐ»Ð°':'beet','ÑÐ±Ð»Ð¾ÐºÐ¾':'apple','Ð±Ð°Ð½Ð°Ð½':'banana',
 'Ð¼Ð°ÐºÐ°ÑÐ¾Ð½Ñ':'pasta cooked','Ð¹Ð¾Ð³ÑÑÑ':'yogurt','Ð¾ÑÐµÑÐ¸':'mixed nuts','Ð»Ð¾ÑÐ¾ÑÑ':'salmon',
 'ÑÑÐµÑÐºÐ°':'cod','ÑÑÐ¿':'soup','Ð±Ð¾ÑÑ':'beet soup','ÐºÑÑÐ°ÑÑÐ°Ð½':'croissant',
 'ÑÐ»ÐµÐ±':'bread','ÑÐ¾ÐºÐ¾Ð»Ð°Ð´':'chocolate','ÑÐ¼ÐµÑÐ°Ð½Ð°':'sour cream','Ð¼Ð°Ð¹Ð¾Ð½ÐµÐ·':'mayonnaise',
 'ÑÐ°ÑÐ°Ñ':'sugar','Ð¿ÐµÑÐµÐ½ÑÐµ':'cookies','Ð¾Ð²ÑÑÐ½Ð°Ñ ÐºÐ°ÑÐ°':'oatmeal','Ð¿ÐµÐ»ÑÐ¼ÐµÐ½Ð¸':'dumplings','Ð±ÐµÐºÐ¾Ð½':'bacon','Ð±ÐµÐºÐ¾Ð½Ð°':'bacon','Ð²ÐµÑÑÐ¸Ð½Ð°':'ham','Ð³ÑÑÐ´Ð¸Ð½ÐºÐ°':'bacon','ÑÐµÑÑÐ¸':'cherry tomatoes','ÑÑÐºÐºÐ¾Ð»Ð°':'arugula','ÑÐ¿Ð¸Ð½Ð°Ñ':'spinach','ÑÐ°Ð»Ð¾':'pork fat','ÑÐµÐ¼ÐµÑÐºÐ¸':'seeds'
};
function englishTerm(q){const s=q.toLowerCase().replaceAll('Ñ','Ðµ');const key=Object.keys(FOOD_ENGLISH).sort((a,b)=>b.length-a.length).find(k=>s.includes(k));return key?FOOD_ENGLISH[key]:q}
async function translateNutritionQuery(q,env){
 const s=englishTerm(q);if(s!==q||!/[Ð-Ð¯Ð°-ÑÐÑ]/.test(q)||!env.AI)return s;
 try{const result=await env.AI.run(MODEL,{messages:[{role:'user',content:'Translate this Russian food search query into brief English food names for USDA database. Reply only English words, without quotes, punctuation or explanation: '+q.slice(0,90)}],chat_template_kwargs:{enable_thinking:false},max_completion_tokens:32,temperature:0});
 const text=String(result?.choices?.[0]?.message?.content||result?.response||'').trim().replace(/[^a-zA-Z0-9, -]/g,'').slice(0,80);return text||q;
 }catch(_){return q}
}
function finiteFood(k,p,f,c){const values=[k,p,f,c].map(Number);return values.every(Number.isFinite)&&values[0]>=0&&values[0]<=1000&&values.slice(1).every(x=>x>=0&&x<=100)}
function offProduct(p){const n=p?.nutriments||{};
 const kcal=n['energy-kcal_100g']??(n['energy-kj_100g']==null?null:Number(n['energy-kj_100g'])/4.184);
 const v=[kcal,n.proteins_100g,n.fat_100g,n.carbohydrates_100g];
 if(v.some(x=>x==null)||!finiteFood(...v))return null;
 const name=String(p.product_name_ru||p.product_name||'').trim();if(!name)return null;
 return {name:name.slice(0,110),brand:String(p.brands||'').slice(0,80),k:Math.round(+v[0]*10)/10,p:+v[1],f:+v[2],c:+v[3],source:'Open Food Facts',code:String(p.code||'')};
}
function usdaNutrient(nutrients,id){const match=(nutrients||[]).find(n=>Number(n.nutrientId||n.nutrient?.id)===id);return match?.value??match?.amount??null}
function usdaProduct(food){const a=food.foodNutrients||[];
 const k=usdaNutrient(a,1008)??usdaNutrient(a,2047)??usdaNutrient(a,2048);
 const p=usdaNutrient(a,1003),f=usdaNutrient(a,1004),c=usdaNutrient(a,1005);
 if([k,p,f,c].some(x=>x==null)||!finiteFood(k,p,f,c))return null;
 const name=String(food.description||'').trim();if(!name)return null;
 return {name:name.slice(0,110),brand:String(food.brandOwner||'').slice(0,80),dataType:String(food.dataType||''),k:+k,p:+p,f:+f,c:+c,source:'USDA FoodData Central',fdcId:food.fdcId};
}
async function sourceJson(url,opt={},label='source'){
 const controller=new AbortController();const t=setTimeout(()=>controller.abort(),12500);const started=Date.now();
 try{
  const response=await fetch(url,{...opt,signal:controller.signal});const type=response.headers.get('content-type')||'';
  if(!response.ok){const fragment=(await response.text()).slice(0,160).replace(/\s+/g,' ');return {items:[],ok:false,diagnostic:`${label}: HTTP ${response.status}; ${fragment}; ${Date.now()-started} Ð¼Ñ`}}
  if(!type.includes('json') && !(label==='CoFID (UK)' && /^(text\/plain|application\/octet-stream)/i.test(type))){const fragment=(await response.text()).slice(0,120);return {items:[],ok:false,diagnostic:`${label}: Ð½Ðµ JSON (${type}); ${fragment}`}}
  return {json:await response.json(),items:[],ok:true,diagnostic:`${label}: HTTP 200; ${Date.now()-started} Ð¼Ñ`};
 }catch(e){return {items:[],ok:false,diagnostic:`${label}: ${e?.name||'Error'} ${e?.message||String(e)}; ${Date.now()-started} Ð¼Ñ`}}
 finally{clearTimeout(t)}
}
// One batched translation per cache miss. Keep the original USDA description alongside Russian.
async function addRussianNames(items,env,translateWithAI=true){
 const usda=items.filter(x=>x.source!=='Open Food Facts'&&!x.name_ru);
 if(!usda.length)return;
 const known={CAKE:'Ð¢Ð¾ÑÑ', 'SPONGE CAKE':'ÐÐ¸ÑÐºÐ²Ð¸Ñ', 'WHIPPED CREAM':'ÐÐ·Ð±Ð¸ÑÑÐµ ÑÐ»Ð¸Ð²ÐºÐ¸', YOGURT:'ÐÐ¾Ð³ÑÑÑ',MILK:'ÐÐ¾Ð»Ð¾ÐºÐ¾',EGG:'Ð¯Ð¹ÑÐ¾',EGGS:'Ð¯Ð¹ÑÐ°',CHEESE:'Ð¡ÑÑ',TOMATO:'ÐÐ¾Ð¼Ð¸Ð´Ð¾Ñ',TOMATOES:'ÐÐ¾Ð¼Ð¸Ð´Ð¾ÑÑ',CHICKEN:'ÐÑÑÐ¸ÑÐ°',BREAD:'Ð¥Ð»ÐµÐ±',POTATO:'ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ',BUTTER:'Ð¡Ð»Ð¸Ð²Ð¾ÑÐ½Ð¾Ðµ Ð¼Ð°ÑÐ»Ð¾',APPLE:'Ð¯Ð±Ð»Ð¾ÐºÐ¾',BANANA:'ÐÐ°Ð½Ð°Ð½'};
 for(const x of usda){const t=x.name.toUpperCase().trim();if(known[t])x.name_ru=known[t]}
 if(!env.AI||!translateWithAI)return;
 try{
  const raw=await env.AI.run(MODEL,{
    messages:[{role:'user',content:'ÐÐµÑÐµÐ²ÐµÐ´Ð¸ Ð½Ð° ÑÑÑÑÐºÐ¸Ð¹ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ñ Ð¿Ð¸ÑÐµÐ²ÑÑ Ð¿ÑÐ¾Ð´ÑÐºÑÐ¾Ð². ÐÐµ Ð¼ÐµÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð², ÑÐ¿Ð¾ÑÐ¾Ð± Ð¿ÑÐ¸Ð³Ð¾ÑÐ¾Ð²Ð»ÐµÐ½Ð¸Ñ, Ð²Ð¸Ð´Ñ Ð¿ÑÐ¾Ð´ÑÐºÑÐ¾Ð² Ð¸Ð»Ð¸ Ð±ÑÐµÐ½Ð´Ñ. ÐÐµÑÐ½Ð¸ Ð¢ÐÐÐ¬ÐÐ JSON-Ð¼Ð°ÑÑÐ¸Ð² ÑÐ¾Ð²Ð½Ð¾ Ð¸Ð· '+usda.length+' ÑÑÑÑÐºÐ¸Ñ ÑÑÑÐ¾Ðº Ð² ÑÐ¾Ð¼ Ð¶Ðµ Ð¿Ð¾ÑÑÐ´ÐºÐµ, Ð±ÐµÐ· Ð¾Ð±ÑÑÑÐ½ÐµÐ½Ð¸Ð¹. ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ñ: '+JSON.stringify(usda.map(x=>x.name))}],
    chat_template_kwargs:{enable_thinking:false},temperature:0,max_completion_tokens:750
  });
  let txt=raw?.choices?.[0]?.message?.content??raw?.response??'';
  if(Array.isArray(txt))txt=txt.map(v=>v?.text||'').join('');
  txt=String(txt).replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'').trim();
  const begin=txt.indexOf('['),end=txt.lastIndexOf(']');
  const arr=JSON.parse(txt.slice(begin,end+1));
  if(Array.isArray(arr)&&arr.length===usda.length){arr.forEach((str,i)=>{if(typeof str==='string'&&str.trim().length>=2&&/[Ð-Ð¯Ð°-ÑÐÑ]/.test(str))usda[i].name_ru=str.slice(0,120).trim()})}
 }catch(_){/* Name lookup must succeed even if translation inference fails. */}
}

// v1.12: Additional independent nutrition providers. Their publicly published
// datasets are retrieved server-side and cached in a Worker isolate; failures
// are isolated and never invalidate the other databases. CoFID is the UK
// government OGL-licensed static extract published by Scranbook (no API key).
const EXTRA_INDEX_CACHE = new Map();
async function extraIndex(key,url,selector){
 const cached=EXTRA_INDEX_CACHE.get(key);
 if(cached&&cached.until>Date.now())return {items:cached.items,diagnostic:key+': ÐºÑÑ Ð¸Ð½Ð´ÐµÐºÑÐ° '+cached.items.length};
 if(cached?.pending)return cached.pending;
 const pending=(async()=>{
  const resp=await sourceJson(url,{headers:{'Accept':'application/json'}},key);
  if(!resp.ok)return {items:[],diagnostic:resp.diagnostic};
  const items=selector(resp.json);
  if(!Array.isArray(items)||!items.length)return {items:[],diagnostic:key+': Ð½ÐµÐ¸Ð·Ð²ÐµÑÑÐ½ÑÐ¹ ÑÐ¾ÑÐ¼Ð°Ñ Ð¾ÑÐ²ÐµÑÐ°'};
  EXTRA_INDEX_CACHE.set(key,{items,until:Date.now()+24*3600*1000});
  return {items,diagnostic:key+': Ð¸Ð½Ð´ÐµÐºÑ '+items.length+'; '+resp.diagnostic};
 })().catch(e=>({items:[],diagnostic:key+': '+String(e?.message||e)}));
 EXTRA_INDEX_CACHE.set(key,{...(cached||{}),pending});
 const result=await pending;
 if(!result.items.length)EXTRA_INDEX_CACHE.set(key,{items:[],until:Date.now()+60*1000});
 return result;
}
function comparableTokens(s){return String(s||'').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9\s-]/g,' ').split(/\s+/).filter(w=>w.length>2&&!['and','the','with','for','from','of','raw','food','foods'].includes(w));}
function extraRank(phrase,query){
 const n=String(phrase||'').toLowerCase(),q=String(query||'').toLowerCase();
 const words=comparableTokens(q);if(!words.length)return -1000;
 const names=comparableTokens(n);if(!names.length)return -1000;
 const joined=names.join(' '),whole=words.join(' ');
 let score=joined===whole?110:joined.startsWith(whole+' ')?72:0;
 for(const word of words){if(names.includes(word))score+=28;else if(names.some(x=>x.startsWith(word)||word.startsWith(x)&&x.length>=4))score+=12;else score-=38;}
 if(n.includes('flavoured')&&!q.includes('flavoured'))score-=20;
 if(n.includes('raw')&&q.includes('cooked'))score-=45;
 return score;
}
function extraBest(rows,en,limit=3){return rows.map(x=>({x,score:extraRank(x.name||x.foodName||x.food_description,en)})).filter(a=>a.score>=27).sort((a,b)=>b.score-a.score).slice(0,limit)}
function extraNum(x){if(x===undefined||x===null)return null;if(typeof x==='object')return extraNum(x.quantity??x.value??x.amount);if(typeof x==='string'){x=x.replace(',','.');if(x==='-')return null;}const n=Number(x);return Number.isFinite(n)?n:null;}
function extraFood(name,k,p,f,c,source,extras={}){const vals=[k,p,f,c].map(extraNum);if(vals.some(x=>x===null)||!finiteFood(...vals))return null;return {name:String(name||'').slice(0,120),k:vals[0],p:vals[1],f:vals[2],c:vals[3],source,...extras};}
async function searchCofid(en){
 const key='CoFID (UK)';const index=await extraIndex(key,'https://raw.githubusercontent.com/taugr/scranbook/main/public/nutrition/foods.json',j=>Array.isArray(j)?j:Array.isArray(j.foods)?j.foods:[]);
 const candidates=index.items.filter(x=>x.source==='uk_cofid');
 const found=extraBest(candidates,en,4).map(({x,score})=>extraFood(x.name,x.energyKcal,x.proteinG,x.fatG,x.carbsG,'CoFID (ÐÐµÐ»Ð¸ÐºÐ¾Ð±ÑÐ¸ÑÐ°Ð½Ð¸Ñ)',{source_id:x.id,match_score:score})).filter(Boolean);
 return {ok:!!index.items.length,items:found,diagnostic:index.diagnostic+'; ÑÐ¾Ð²Ð¿Ð°Ð´ÐµÐ½Ð¸Ð¹ '+found.length};
}
async function searchNorway(en){
 const key='Matvaretabellen (Norway)';const index=await extraIndex(key,'https://www.matvaretabellen.no/api/en/foods.json',j=>Array.isArray(j)?j:Array.isArray(j.foods)?j.foods:[]);
 const found=extraBest(index.items,en,4).map(({x,score})=>{
  const n=x.constituents||{};
  // Norwegian source uses these identifiers for total fat, available carbohydrates and protein.
  const constituent=id=>n[id]??(Array.isArray(n)?n.find(v=>v.nutrientId===id):undefined);
  return extraFood(x.foodName||x.name,x.energyKcal??x.energy?.kcal,constituent('Protein'),constituent('Fett'),constituent('Karbo'),'Matvaretabellen (ÐÐ¾ÑÐ²ÐµÐ³Ð¸Ñ)',{source_id:x.id,match_score:score});
 }).filter(Boolean);
 return {ok:!!index.items.length,items:found,diagnostic:index.diagnostic+'; ÑÐ¾Ð²Ð¿Ð°Ð´ÐµÐ½Ð¸Ð¹ '+found.length};
}
const CANADA_API='https://food-nutrition.canada.ca/api/canadian-nutrient-file/';
async function searchCanada(en){
 // The openly documented JSON API serves the older CNF online dataset (2015),
 // not the separate downloadable CNF 2026 relational CSV publication.
 const key='Canadian Nutrient File API';const index=await extraIndex(key,CANADA_API+'food/?lang=en&type=json',j=>Array.isArray(j)?j:Array.isArray(j.foods)?j.foods:[]);
 const best=extraBest(index.items.map(x=>({...x,name:x.food_description})),en,2);
 const details=await Promise.all(best.map(async ({x,score})=>{
  const r=await sourceJson(CANADA_API+'nutrientamount/?lang=en&type=json&id='+encodeURIComponent(x.food_code),{},key+' #'+x.food_code);
  if(!r.ok)return null;
  const vals=Array.isArray(r.json)?r.json:[];
  const nutrient=(ids,names)=>{
   const row=vals.find(v=>ids.includes(Number(v.nutrient_name_id)))||vals.find(v=>names.some(t=>String(v.nutrient_web_name||'').toLowerCase()===t));
   return row?.nutrient_value??null;
  };
  return extraFood(x.name,nutrient([208,268],['energy (kcal)','energy, kcal','energy (kilocalories)']),nutrient([203],['protein']),nutrient([204],['fat, total lipid','total fat']),nutrient([205],['carbohydrate, by difference','carbohydrate, total']),'Canadian Nutrient File (ÐÐ°Ð½Ð°Ð´Ð°)',{source_id:x.food_code,match_score:score});
 }));
 const found=details.filter(Boolean);
 return {ok:!!index.items.length,items:found,diagnostic:index.diagnostic+'; ÑÐ¾Ð²Ð¿Ð°Ð´ÐµÐ½Ð¸Ð¹ '+found.length};
}
async function tryExtra(fn,label,en){try{return await fn(en)}catch(e){return {ok:false,items:[],diagnostic:label+': '+String(e?.message||e)}}}

async function searchNutrition(query,env,{fast=false}={}){
 const q=String(query||'').trim().slice(0,100);if(q.length<2)return {ok:false,error:'ÐÐ°Ð¿ÑÐ¾Ñ ÑÐ»Ð¸ÑÐºÐ¾Ð¼ ÐºÐ¾ÑÐ¾ÑÐºÐ¸Ð¹',items:[],diagnostics:[]};
 const trusted=VERIFIED_PREPARED_FOODS.find(x=>x.test.test(q));if(trusted)return {ok:true,items:[{...trusted.row}],diagnostics:['ÐÑÐ¾Ð²ÐµÑÐµÐ½Ð½Ð°Ñ ÑÑÐ°Ð½Ð´Ð°ÑÑÐ½Ð°Ñ Ð·Ð°Ð¿Ð¸ÑÑ USDA'],query:q,sources:{usda:true}};
 const key=q.toLowerCase();const cached=NUT_CACHE.get(key);if(cached&&cached.until>Date.now())return {...cached.value,diagnostics:['ÐÐµÑ Ð¿Ð¾Ð¸ÑÐºÐ° (Ð´Ð¾ 20 Ð¼Ð¸Ð½ÑÑ)',...(cached.value.diagnostics||[])]};
 // Legacy endpoint is required for full-text search; v2 search_term is unsupported.
 const offParams=new URLSearchParams({search_terms:q,search_simple:'1',action:'process',json:'1',page_size:'12',fields:'code,product_name,product_name_ru,brands,nutriments'});
 const off=sourceJson('https://world.openfoodfacts.org/cgi/search.pl?'+offParams.toString(),{
  headers:{'Accept':'application/json','User-Agent':'MyFoodPWA/0.8 (+https://drop-443886b1-4e5.evpoluyanov.workers.dev)'}
 },'Open Food Facts');
 const en=await translateNutritionQuery(q,env);
 const usdaKey=env.USDA_API_KEY||'DEMO_KEY'; // use a private free API key for reliable usage
 const usda=sourceJson('https://api.nal.usda.gov/fdc/v1/foods/search?api_key='+encodeURIComponent(usdaKey),{
  method:'POST',headers:{'Content-Type':'application/json','Accept':'application/json'},body:JSON.stringify({query:en,pageSize:35,sortBy:'dataType.keyword',sortOrder:'asc'})
 },'USDA ('+en+')');
 const [a,b,sw,cofid,norway,canada]=await Promise.all([off,usda,searchSwedish(en),tryExtra(searchCofid,'CoFID',en),tryExtra(searchNorway,'Matvaretabellen',en),tryExtra(searchCanada,'CNF',en)]);
 const raw=[...(a.ok?a.json?.products||[]:[]).map(offProduct),...(b.ok?b.json?.foods||[]:[]).map(usdaProduct),...sw.items,...cofid.items,...norway.items,...canada.items].filter(Boolean);
 // Prefer exact products, generic foods and FNDDS over products containing query as a sub-ingredient.
   const queryWords=en.toLowerCase().match(/[a-z]{3,}/g)||[];
   const score=(item)=>{const n=item.name.toLowerCase();let sc=0;
     if(n===en.toLowerCase())sc+=70;
     if(n.startsWith(en.toLowerCase()+','))sc+=25;
     if(n.startsWith(en.toLowerCase()+' '))sc+=32;
     for(const w of queryWords){if(n.includes(w))sc+=10;else sc-=20;}
     // A generic one/two-word query must not prefer a coincidentally named branded product.
     const genericQuery=queryWords.length<=2;
     if(item.brand)sc-=genericQuery?48:14;
     else if(item.source==='CoFID (ÐÐµÐ»Ð¸ÐºÐ¾Ð±ÑÐ¸ÑÐ°Ð½Ð¸Ñ)'||/Foundation|SR Legacy|FNDDS/i.test(item.dataType||''))sc+=18;
     if(!item.brand && n.startsWith(en.toLowerCase()+','))sc+=27;
     if(/pretzel|raisin|almond|peanut|coated|flavored|dessert/.test(n) && !/pretzel|raisin|almond|peanut|dessert/.test(en.toLowerCase()))sc-=28;
     return sc;};
   raw.forEach(x=>x.match_score=score(x));raw.sort((x,y)=>y.match_score-x.match_score);
   const seen=new Set(),sourceCounts=new Map(),items=[];for(const item of raw){if(item.match_score< -10)continue;const id=item.source+':'+(item.code||item.fdcId||item.source_id||item.name);if(seen.has(id)||(sourceCounts.get(item.source)||0)>=3)continue;seen.add(id);sourceCounts.set(item.source,(sourceCounts.get(item.source)||0)+1);items.push(item);if(items.length>=18)break}
 await addRussianNames(items,env,!fast);
 const result={ok:a.ok||b.ok||sw.ok||cofid.ok||norway.ok||canada.ok,english_query:en,items,diagnostics:[a.diagnostic,b.diagnostic,sw.diagnostic,cofid.diagnostic,norway.diagnostic,canada.diagnostic],query:q,sources:{off:a.ok,usda:b.ok,sweden:sw.ok,cofid:cofid.ok,norway:norway.ok,canada:canada.ok}};
 if(!result.ok)result.error='ÐÑÑÐ¾ÑÐ½Ð¸ÐºÐ¸ Ð½ÐµÐ´Ð¾ÑÑÑÐ¿Ð½Ñ â ÑÐ¼. diagnostics';
 // Empty/failed searches must be retried soon when providers recover; valid hits can be cached longer.
 NUT_CACHE.set(key,{until:Date.now()+(items.length?60*60*1000:45*1000),value:result});if(NUT_CACHE.size>100)NUT_CACHE.delete(NUT_CACHE.keys().next().value);
 return result;
}

// A small, server-side snapshot parsed from the user's official-format PDF dated 2026-05-25.
// Actual official site may publish a newer revision: never misrepresent this snapshot as live.
const CHAIN_PDF_DATE='2026-05-25';
const CHAIN_OFFICIAL_PDF='https://vkusnoitochka.ru/sostav.pdf';
const CHAIN_ROWS=[{"name":"Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ","base_name":"Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ","w":109.0,"k":291.0,"p":14.0,"f":11.0,"c":33.0,"page":1,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ","w":158.0,"k":416.0,"p":24.0,"f":21.0,"c":34.0,"page":1,"portion":""},{"name":"ÐÐ°Ð¼Ð±ÑÑÐ³ÐµÑ","base_name":"ÐÐ°Ð¼Ð±ÑÑÐ³ÐµÑ","w":97.0,"k":252.0,"p":12.0,"f":8.2,"c":33.0,"page":1,"portion":""},{"name":"Ð¤Ð¸Ñ ÐÑÑÐ³ÐµÑ","base_name":"Ð¤Ð¸Ñ ÐÑÑÐ³ÐµÑ","w":133.0,"k":331.0,"p":15.0,"f":14.0,"c":36.0,"page":1,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ Ð¤Ð¸Ñ ÐÑÑÐ³ÐµÑ","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ Ð¤Ð¸Ñ ÐÑÑÐ³ÐµÑ","w":196.0,"k":475.0,"p":26.0,"f":21.0,"c":45.0,"page":2,"portion":""},{"name":"Ð§Ð¸ÐºÐµÐ½Ð±ÑÑÐ³ÐµÑ","base_name":"Ð§Ð¸ÐºÐµÐ½Ð±ÑÑÐ³ÐµÑ","w":129.0,"k":337.0,"p":12.0,"f":16.0,"c":37.0,"page":2,"portion":""},{"name":"ÐÑÐ°Ð½Ð´","base_name":"ÐÑÐ°Ð½Ð´","w":202.0,"k":514.0,"p":30.0,"f":26.0,"c":38.0,"page":2,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÑÐ°Ð½Ð´","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÑÐ°Ð½Ð´","w":282.0,"k":732.0,"p":49.0,"f":42.0,"c":38.0,"page":2,"portion":""},{"name":"ÐÑÐ°Ð½Ð´ ÐÐµ ÐÑÐºÑ","base_name":"ÐÑÐ°Ð½Ð´ ÐÐµ ÐÑÐºÑ","w":251.0,"k":570.0,"p":31.0,"f":31.0,"c":40.0,"page":2,"portion":""},{"name":"Ð§Ð¸ÐºÐµÐ½ ÐÑÐµÐ¼ÑÐµÑ","base_name":"Ð§Ð¸ÐºÐµÐ½ ÐÑÐµÐ¼ÑÐµÑ","w":234.0,"k":525.0,"p":26.0,"f":24.0,"c":51.0,"page":2,"portion":""},{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","base_name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","w":340.0,"k":800.0,"p":43.0,"f":47.0,"c":49.0,"page":3,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","w":450.0,"k":1098.0,"p":70.0,"f":69.0,"c":49.0,"page":3,"portion":""},{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÐÐ¶ÑÐ½Ð¸Ð¾Ñ","base_name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÐÐ¶ÑÐ½Ð¸Ð¾Ñ","w":231.0,"k":573.0,"p":31.0,"f":33.0,"c":36.0,"page":3,"portion":""},{"name":"Ð§Ð¸ÐºÐµÐ½ Ð¥Ð¸Ñ","base_name":"Ð§Ð¸ÐºÐµÐ½ Ð¥Ð¸Ñ","w":198.0,"k":484.0,"p":21.0,"f":22.0,"c":49.0,"page":3,"portion":""},{"name":"ÐÐ¸Ð³ Ð¥Ð¸Ñ","base_name":"ÐÐ¸Ð³ Ð¥Ð¸Ñ","w":228.0,"k":524.0,"p":27.0,"f":28.0,"c":40.0,"page":3,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¥Ð¸Ñ","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¥Ð¸Ñ","w":303.0,"k":711.0,"p":43.0,"f":41.0,"c":41.0,"page":3,"portion":""},{"name":"ÐÐ¸Ð³ Ð§Ð¸ÐºÐµÐ½ ÐÑÑÐ³ÐµÑ","base_name":"ÐÐ¸Ð³ Ð§Ð¸ÐºÐµÐ½ ÐÑÑÐ³ÐµÑ","w":323.0,"k":700.0,"p":44.0,"f":35.0,"c":51.0,"page":3,"portion":""},{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","base_name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","w":376.0,"k":751.0,"p":43.0,"f":38.0,"c":59.0,"page":4,"portion":""},{"name":"Ð¢ÑÐ¾Ð¹Ð½Ð¾Ð¹ Ð¤ÑÐµÑ","base_name":"Ð¢ÑÐ¾Ð¹Ð½Ð¾Ð¹ Ð¤ÑÐµÑ","w":232.0,"k":577.0,"p":33.0,"f":34.0,"c":35.0,"page":4,"portion":""},{"name":"Ð¦ÐµÐ·Ð°ÑÑ Ð Ð¾Ð»Ð»","base_name":"Ð¦ÐµÐ·Ð°ÑÑ Ð Ð¾Ð»Ð»","w":211.0,"k":472.0,"p":19.0,"f":22.0,"c":48.0,"page":4,"portion":""},{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» Ð Ð¾Ð»Ð»","base_name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» Ð Ð¾Ð»Ð»","w":241.0,"k":525.0,"p":27.0,"f":30.0,"c":36.0,"page":4,"portion":""},{"name":"Ð¨ÑÐ¸Ð¼Ð¿ Ð Ð¾Ð»Ð»","base_name":"Ð¨ÑÐ¸Ð¼Ð¿ Ð Ð¾Ð»Ð»","w":164.0,"k":411.0,"p":15.0,"f":17.0,"c":49.0,"page":4,"portion":""},{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÑÐ¾Ð»Ð» ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","base_name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÑÐ¾Ð»Ð» ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","w":295.0,"k":556.0,"p":27.0,"f":29.0,"c":47.0,"page":4,"portion":""},{"name":"Ð§Ð¸ÐºÐµÐ½ ÐÑÐµÐ¼ÑÐµÑ ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","base_name":"Ð§Ð¸ÐºÐµÐ½ ÐÑÐµÐ¼ÑÐµÑ ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","w":255.0,"k":516.0,"p":21.0,"f":22.0,"c":59.0,"page":5,"portion":""},{"name":"ÐÐ¸Ð³ Ð§Ð¸ÐºÐµÐ½ ÐÑÑÐ³ÐµÑ ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","base_name":"ÐÐ¸Ð³ Ð§Ð¸ÐºÐµÐ½ ÐÑÑÐ³ÐµÑ ÐÐµÑÐµÑ Ð³ÑÐ¸Ð»Ñ","w":374.0,"k":703.0,"p":39.0,"f":39.0,"c":70.0,"page":5,"portion":""},{"name":"ÐÐ°Ð½Ð¸Ð½Ð¸ Ð¢Ð¾ÑÐºÐ°Ð½Ð°","base_name":"ÐÐ°Ð½Ð¸Ð½Ð¸ Ð¢Ð¾ÑÐºÐ°Ð½Ð°","w":273.0,"k":636.0,"p":29.0,"f":32.0,"c":58.0,"page":5,"portion":""},{"name":"ÐÐ°Ð½Ð¸Ð½Ð¸ Ð¢Ð¾ÑÐºÐ°Ð½Ð° Ð¾ÑÑÑÑÐ¹","base_name":"ÐÐ°Ð½Ð¸Ð½Ð¸ Ð¢Ð¾ÑÐºÐ°Ð½Ð° Ð¾ÑÑÑÑÐ¹","w":279.0,"k":638.0,"p":29.0,"f":32.0,"c":59.0,"page":5,"portion":""},{"name":"Ð¢ÑÐ¾Ð¹Ð½Ð¾Ð¹ Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ Ð¢ÑÐ¸ Ð¡ÑÑÐ°","base_name":"Ð¢ÑÐ¾Ð¹Ð½Ð¾Ð¹ Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ Ð¢ÑÐ¸ Ð¡ÑÑÐ°","w":202.0,"k":538.0,"p":34.0,"f":29.0,"c":34.0,"page":5,"portion":""},{"name":"ÐÐ¸Ð³ Ð§Ð¸ÐºÐµÐ½ ÐÑÑÐ³ÐµÑ ÐÐ°Ð·Ð¸Ð»Ð¸ÐºÐ¾Ð²ÑÐ¹","base_name":"ÐÐ¸Ð³ Ð§Ð¸ÐºÐµÐ½ ÐÑÑÐ³ÐµÑ ÐÐ°Ð·Ð¸Ð»Ð¸ÐºÐ¾Ð²ÑÐ¹","w":320.0,"k":750.0,"p":39.0,"f":40.0,"c":59.0,"page":5,"portion":""},{"name":"ÐÐ°Ð³Ð³ÐµÑÑÑ (4 ÑÑ)","base_name":"ÐÐ°Ð³Ð³ÐµÑÑÑ","w":72.0,"k":179.0,"p":11.0,"f":9.1,"c":12.0,"page":6,"portion":"4 ÑÑ"},{"name":"ÐÐ°Ð³Ð³ÐµÑÑÑ (6 ÑÑ)","base_name":"ÐÐ°Ð³Ð³ÐµÑÑÑ","w":108.0,"k":268.0,"p":17.0,"f":14.0,"c":19.0,"page":6,"portion":"6 ÑÑ"},{"name":"ÐÐ°Ð³Ð³ÐµÑÑÑ (9 ÑÑ)","base_name":"ÐÐ°Ð³Ð³ÐµÑÑÑ","w":162.0,"k":402.0,"p":25.0,"f":21.0,"c":28.0,"page":6,"portion":"9 ÑÑ"},{"name":"ÐÐ°Ð³Ð³ÐµÑÑÑ (18 ÑÑ)","base_name":"ÐÐ°Ð³Ð³ÐµÑÑÑ","w":324,"k":804.0,"p":50.0,"f":42.0,"c":56.0,"page":6,"portion":"18 ÑÑ"},{"name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ (4 ÑÑ)","base_name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ","w":72.0,"k":180.0,"p":9.9,"f":9.0,"c":15.0,"page":6,"portion":"4 ÑÑ"},{"name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ (6 ÑÑ)","base_name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ","w":108.0,"k":271.0,"p":15.0,"f":14.0,"c":22.0,"page":6,"portion":"6 ÑÑ"},{"name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ (9 ÑÑ)","base_name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ","w":162.0,"k":406.0,"p":22.0,"f":20.0,"c":34.0,"page":6,"portion":"9 ÑÑ"},{"name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ (18 ÑÑ)","base_name":"ÐÐ·Ð´ÐµÐ»Ð¸Ñ ÐºÑÐ»Ð¸Ð½Ð°ÑÐ½ÑÐµ ÐºÑÐµÐ²ÐµÑÐºÐ¸ Ð¶Ð°ÑÐµÐ½ÑÐµ","w":324.0,"k":812.0,"p":44.0,"f":40.0,"c":68.0,"page":6,"portion":"18 ÑÑ"},{"name":"ÐÑÑÐ¸Ð½ÑÐµ ÐºÑÑÐ»ÑÑÐºÐ¸ (5 ÑÑ)","base_name":"ÐÑÑÐ¸Ð½ÑÐµ ÐºÑÑÐ»ÑÑÐºÐ¸","w":125.0,"k":350.0,"p":21.25,"f":22.5,"c":15.0,"page":6,"portion":"5 ÑÑ"},{"name":"ÐÑÑÐ¸Ð½ÑÐµ Ð¡ÑÑÐ¸Ð¿ÑÑ (3 ÑÑ)","base_name":"ÐÑÑÐ¸Ð½ÑÐµ Ð¡ÑÑÐ¸Ð¿ÑÑ","w":99.0,"k":223.0,"p":14.0,"f":10.0,"c":19.0,"page":6,"portion":"3 ÑÑ"},{"name":"ÐÑÑÐ¸Ð½ÑÐµ Ð¡ÑÑÐ¸Ð¿ÑÑ (5 ÑÑ)","base_name":"ÐÑÑÐ¸Ð½ÑÐµ Ð¡ÑÑÐ¸Ð¿ÑÑ","w":165.0,"k":371.0,"p":23.0,"f":17.0,"c":31.0,"page":6,"portion":"5 ÑÑ"},{"name":"ÐÑÑÐ¸Ð½ÑÐµ Ð¡ÑÑÐ¸Ð¿ÑÑ (7 ÑÑ)","base_name":"ÐÑÑÐ¸Ð½ÑÐµ Ð¡ÑÑÐ¸Ð¿ÑÑ","w":231.0,"k":520.0,"p":32.0,"f":24.0,"c":44.0,"page":6,"portion":"7 ÑÑ"},{"name":"Ð¡Ð½ÑÐº ÐÐ¾ÐºÑ","base_name":"Ð¡Ð½ÑÐº ÐÐ¾ÐºÑ","w":196.0,"k":500.0,"p":20.0,"f":24.0,"c":49.0,"page":6,"portion":""},{"name":"Ð¡ÑÐµÐ´Ð½Ð¸Ð¹ ÐÐ¾ÐºÑ","base_name":"Ð¡ÑÐµÐ´Ð½Ð¸Ð¹ ÐÐ¾ÐºÑ","w":152.0,"k":319.2,"p":22.8,"f":19.76,"c":24.32,"page":6,"portion":""},{"name":"ÐÐ¾Ð»ÑÑÐ¾Ð¹ ÐÐ¾ÐºÑ","base_name":"ÐÐ¾Ð»ÑÑÐ¾Ð¹ ÐÐ¾ÐºÑ","w":304.0,"k":638.4,"p":45.6,"f":39.52,"c":48.64,"page":7,"portion":""},{"name":"ÐÐµÐ³Ð° ÐÐ¾ÐºÑ","base_name":"ÐÐµÐ³Ð° ÐÐ¾ÐºÑ","w":608.0,"k":1276.8,"p":91.2,"f":79.04,"c":97.28,"page":7,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸","w":76.0,"k":220.0,"p":2.6,"f":10.0,"c":28.0,"page":7,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸","w":110.0,"k":318.0,"p":3.7,"f":15.0,"c":40.0,"page":7,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸","w":147.0,"k":425.0,"p":5.0,"f":20.0,"c":53.0,"page":7,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸","w":165.0,"k":331.0,"p":4.6,"f":15.0,"c":42.0,"page":7,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸","w":220,"k":441.0,"p":6.2,"f":20.0,"c":57.0,"page":7,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸ ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸ ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹","w":220.0,"k":636.0,"p":7.5,"f":30.0,"c":80.0,"page":7,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹","w":330.0,"k":766.0,"p":9.2,"f":38.0,"c":97.0,"page":7,"portion":""},{"name":"Ð¡Ð°Ð»Ð°Ñ ÐÐ²Ð¾ÑÐ½Ð¾Ð¹","base_name":"Ð¡Ð°Ð»Ð°Ñ ÐÐ²Ð¾ÑÐ½Ð¾Ð¹","w":96.0,"k":31.0,"p":0.8,"f":2.0,"c":1.8,"page":8,"portion":""},{"name":"Ð¡Ð°Ð»Ð°Ñ Ð¦ÐµÐ·Ð°ÑÑ","base_name":"Ð¡Ð°Ð»Ð°Ñ Ð¦ÐµÐ·Ð°ÑÑ","w":156.0,"k":199.0,"p":13.0,"f":9.7,"c":14.0,"page":8,"portion":""},{"name":"Ð¡Ð°Ð»Ð°Ñ Ð¦ÐµÐ·Ð°ÑÑ Ñ ÐºÑÐµÐ²ÐµÑÐºÐ°Ð¼Ð¸","base_name":"Ð¡Ð°Ð»Ð°Ñ Ð¦ÐµÐ·Ð°ÑÑ Ñ ÐºÑÐµÐ²ÐµÑÐºÐ°Ð¼Ð¸","w":146.0,"k":186.0,"p":11.0,"f":9.7,"c":13.0,"page":8,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ñ ÑÑÑÐ¾Ð¼ Ð¸ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ñ ÑÑÑÐ¾Ð¼ Ð¸ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","w":151.0,"k":634.2,"p":15.1,"f":34.73,"c":60.4,"page":8,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ Ñ ÑÑÑÐ¾Ð¼ Ð¸ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ Ñ ÑÑÑÐ¾Ð¼ Ð¸ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","w":206.0,"k":891.98,"p":22.66,"f":47.38,"c":88.58,"page":8,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ñ ÑÑÑÐ¾Ð¼","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ñ ÑÑÑÐ¾Ð¼","w":140.0,"k":513.8,"p":9.66,"f":26.6,"c":56.0,"page":8,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ Ñ ÑÑÑÐ¾Ð¼","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸ Ñ ÑÑÑÐ¾Ð¼","w":195.0,"k":741.0,"p":15.21,"f":37.05,"c":83.85,"page":8,"portion":""},{"name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð»Ð¸Ð¼Ð¾Ð½Ð½ÑÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð»Ð¸Ð¼Ð¾Ð½Ð½ÑÐ¹","w":250.0,"k":67.0,"p":0.0,"f":0.0,"c":17.0,"page":9,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð»Ð¸Ð¼Ð¾Ð½Ð½ÑÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð»Ð¸Ð¼Ð¾Ð½Ð½ÑÐ¹","w":400.0,"k":107.0,"p":0.0,"f":0.0,"c":27.0,"page":9,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð»Ð¸Ð¼Ð¾Ð½Ð½ÑÐ¹ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð»Ð¸Ð¼Ð¾Ð½Ð½ÑÐ¹","w":500.0,"k":134.0,"p":0.0,"f":0.0,"c":34.0,"page":9,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð·ÐµÐ»ÐµÐ½ÑÐ¹","w":250.0,"k":67.0,"p":0.0,"f":0.0,"c":17.0,"page":9,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð·ÐµÐ»ÐµÐ½ÑÐ¹","w":400.0,"k":107.0,"p":0.0,"f":0.0,"c":27.0,"page":9,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"Ð§Ð°Ð¹ ÐÐ¸Ð¿ÑÐ¾Ð½ Ð·ÐµÐ»ÐµÐ½ÑÐ¹","w":500.0,"k":134.0,"p":0.0,"f":0.0,"c":34.0,"page":9,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð°","w":250.0,"k":106.0,"p":0.0,"f":0.0,"c":27.0,"page":9,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð°","w":400.0,"k":170.0,"p":0.0,"f":0.0,"c":42.0,"page":9,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð°","w":500.0,"k":212.0,"p":0.0,"f":0.0,"c":53.0,"page":9,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½","w":250.0,"k":48.0,"p":0.0,"f":0.0,"c":12.0,"page":9,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½","w":400.0,"k":76.0,"p":0.0,"f":0.0,"c":18.0,"page":9,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":9,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼","w":250.0,"k":47.5,"p":0.0,"f":0.0,"c":12.0,"page":9,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼","w":400.0,"k":76.0,"p":0.0,"f":0.0,"c":18.0,"page":9,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":9,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ° (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°","w":250.0,"k":0.75,"p":0.0,"f":0.0,"c":0.25,"page":10,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ° (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°","w":400.0,"k":1.2,"p":0.0,"f":0.0,"c":0.4,"page":10,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ° (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°","w":500.0,"k":1.5,"p":0.0,"f":0.0,"c":0.5,"page":10,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹","w":300.0,"k":144.0,"p":0.0,"f":0.0,"c":34.0,"page":10,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹","w":400.0,"k":192.0,"p":0.0,"f":0.0,"c":45.0,"page":10,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹","w":500.0,"k":240.0,"p":0.0,"f":0.0,"c":57.0,"page":10,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½Ð¾Ð²ÑÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½Ð¾Ð²ÑÐ¹","w":300.0,"k":140.0,"p":0.0,"f":0.0,"c":26.0,"page":10,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½Ð¾Ð²ÑÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½Ð¾Ð²ÑÐ¹","w":400,"k":187.0,"p":0.0,"f":0.0,"c":34.0,"page":10,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½Ð¾Ð²ÑÐ¹ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¡Ð¾Ðº Ð²Ð¾ÑÑÑÐ°Ð½Ð¾Ð²Ð»ÐµÐ½Ð½ÑÐ¹ Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½Ð¾Ð²ÑÐ¹","w":500.0,"k":234.0,"p":0.0,"f":0.0,"c":43.0,"page":10,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°Ð¼Ð±Ð» ÐºÐ¾ÑÐµ","base_name":"ÐÐ°Ð¼Ð±Ð» ÐºÐ¾ÑÐµ","w":294.0,"k":162.0,"p":1.9,"f":1.9,"c":34.0,"page":10,"portion":""},{"name":"Ð¤Ð¸Ð·Ð· Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° ÐÐ¸ÑÐ½Ñ (Ð¤Ð¸Ð·Ð· ÐÐ¸ÑÐ½Ñ) (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð¤Ð¸Ð·Ð· Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° ÐÐ¸ÑÐ½Ñ (Ð¤Ð¸Ð·Ð· ÐÐ¸ÑÐ½Ñ)","w":250.0,"k":113.0,"p":0.0,"f":0.0,"c":28.0,"page":10,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð¤Ð¸Ð·Ð· Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° ÐÐ¸ÑÐ½Ñ (Ð¤Ð¸Ð·Ð· ÐÐ¸ÑÐ½Ñ) (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¤Ð¸Ð·Ð· Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° ÐÐ¸ÑÐ½Ñ (Ð¤Ð¸Ð·Ð· ÐÐ¸ÑÐ½Ñ)","w":400.0,"k":180.0,"p":0.0,"f":0.0,"c":44.0,"page":10,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¤Ð¸Ð·Ð· Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° ÐÐ¸ÑÐ½Ñ (Ð¤Ð¸Ð·Ð· ÐÐ¸ÑÐ½Ñ) (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¤Ð¸Ð·Ð· Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° ÐÐ¸ÑÐ½Ñ (Ð¤Ð¸Ð·Ð· ÐÐ¸ÑÐ½Ñ)","w":500.0,"k":225.0,"p":0.0,"f":0.0,"c":55.0,"page":10,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¸Ð¼Ð¾Ð½Ð°Ð´ ÐÐ¾Ð»ÑÑÐµ Ð¼Ð°Ð½Ð³Ð¾","base_name":"ÐÐ¸Ð¼Ð¾Ð½Ð°Ð´ ÐÐ¾Ð»ÑÑÐµ Ð¼Ð°Ð½Ð³Ð¾","w":266.0,"k":93.0,"p":0.0,"f":0.0,"c":23.0,"page":10,"portion":""},{"name":"Ð¡Ð°Ð½ÑÐ°Ð¹Ð· ÐÐ¾Ð»ÑÑÐµ Ð¼Ð°Ð½Ð³Ð¾","base_name":"Ð¡Ð°Ð½ÑÐ°Ð¹Ð· ÐÐ¾Ð»ÑÑÐµ Ð¼Ð°Ð½Ð³Ð¾","w":316.0,"k":187.0,"p":0.0,"f":0.0,"c":38.0,"page":11,"portion":""},{"name":"ÐÐ¹Ñ ÐÐ¾ÑÐµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ","base_name":"ÐÐ¹Ñ ÐÐ¾ÑÐµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ","w":300.0,"k":135.0,"p":3.6,"f":3.8,"c":21.0,"page":11,"portion":""},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":300.0,"k":232.0,"p":5.5,"f":4.5,"c":42.0,"page":11,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":400.0,"k":309.0,"p":7.3,"f":6.0,"c":57.0,"page":11,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":500.0,"k":387.0,"p":9.1,"f":7.5,"c":71.0,"page":11,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":300.0,"k":229.0,"p":5.4,"f":4.5,"c":42.0,"page":11,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":400.0,"k":303.0,"p":7.2,"f":6.0,"c":55.0,"page":11,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":500.0,"k":380.0,"p":9.0,"f":7.5,"c":69.0,"page":11,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":300.0,"k":231.0,"p":5.8,"f":4.8,"c":41.0,"page":11,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":400.0,"k":305.0,"p":7.7,"f":6.4,"c":54.0,"page":11,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼ (Ð±Ð¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð¼Ð¾Ð»Ð¾ÑÐ½ÑÐ¹ Ñ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¼ ÑÐ¸ÑÐ¾Ð¿Ð¾Ð¼","w":500.0,"k":384.0,"p":9.7,"f":8.0,"c":68.0,"page":11,"portion":"Ð±Ð¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÐºÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð§ÐµÑÐµÑÐ½Ñ","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÐºÐ¾ÐºÑÐµÐ¹Ð»Ñ Ð§ÐµÑÐµÑÐ½Ñ","w":300.0,"k":216.0,"p":5.3,"f":4.4,"c":39.0,"page":11,"portion":""},{"name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ","base_name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ","w":175.0,"k":312.0,"p":5.2,"f":6.7,"c":58.0,"page":12,"portion":""},{"name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´","base_name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´","w":173.0,"k":308.0,"p":5.7,"f":9.3,"c":49.0,"page":12,"portion":""},{"name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ ÐÐ»ÑÐ±Ð½Ð¸ÐºÐ°","base_name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ ÐÐ»ÑÐ±Ð½Ð¸ÐºÐ°","w":172.0,"k":256.0,"p":4.8,"f":4.9,"c":48.0,"page":12,"portion":""},{"name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ Ð² Ð²Ð°ÑÐµÐ»ÑÐ½Ð¾Ð¼ ÑÐ¾Ð¶ÐºÐµ","base_name":"ÐÐ¾ÑÐ¾Ð¶ÐµÐ½Ð¾Ðµ Ð¼ÑÐ³ÐºÐ¾Ðµ Ð¼Ð¾Ð»Ð¾ÑÐ½Ð¾Ðµ Ð² Ð²Ð°ÑÐµÐ»ÑÐ½Ð¾Ð¼ ÑÐ¾Ð¶ÐºÐµ","w":98.0,"k":164.0,"p":3.8,"f":3.6,"c":29.0,"page":12,"portion":""},{"name":"ÐÐ¸ÑÐ¾Ð¶Ð¾Ðº Ñ Ð²Ð¸ÑÐ½ÐµÐ²Ð¾Ð¹ Ð½Ð°ÑÐ¸Ð½ÐºÐ¾Ð¹","base_name":"ÐÐ¸ÑÐ¾Ð¶Ð¾Ðº Ñ Ð²Ð¸ÑÐ½ÐµÐ²Ð¾Ð¹ Ð½Ð°ÑÐ¸Ð½ÐºÐ¾Ð¹","w":80.0,"k":290.0,"p":2.4,"f":12.0,"c":43.0,"page":13,"portion":""},{"name":"ÐÐ¸ÑÐ¾Ð¶Ð¾Ðº ÐÐ»ÑÐ±Ð½Ð¸ÐºÐ° ÑÐ¾ ÑÐ»Ð¸Ð²ÐºÐ°Ð¼Ð¸","base_name":"ÐÐ¸ÑÐ¾Ð¶Ð¾Ðº ÐÐ»ÑÐ±Ð½Ð¸ÐºÐ° ÑÐ¾ ÑÐ»Ð¸Ð²ÐºÐ°Ð¼Ð¸","w":80.0,"k":277.0,"p":3.6,"f":13.0,"c":36.0,"page":13,"portion":""},{"name":"ÐÐ¸ÑÐ¾Ð¶Ð¾Ðº ÐÐµÑÐ½ÑÐµ Ð¯Ð³Ð¾Ð´Ñ-ÐºÑÐµÐ¼ÑÐ¸Ð·","base_name":"ÐÐ¸ÑÐ¾Ð¶Ð¾Ðº ÐÐµÑÐ½ÑÐµ Ð¯Ð³Ð¾Ð´Ñ-ÐºÑÐµÐ¼ÑÐ¸Ð·","w":79.0,"k":271.0,"p":3.1,"f":14.0,"c":33.0,"page":14,"portion":""},{"name":"ÐÐµÐ½ÐµÑÐ¸Ð°Ð½ÑÐºÐ¸Ðµ Ð¿Ð¾Ð½ÑÐ¸ÐºÐ¸","base_name":"ÐÐµÐ½ÐµÑÐ¸Ð°Ð½ÑÐºÐ¸Ðµ Ð¿Ð¾Ð½ÑÐ¸ÐºÐ¸","w":80.0,"k":251.0,"p":3.3,"f":11.0,"c":34.0,"page":14,"portion":""},{"name":"Ð§Ð°Ð¹ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð§Ð°Ð¹ Ð·ÐµÐ»ÐµÐ½ÑÐ¹","w":200.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð§Ð°Ð¹ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð§Ð°Ð¹ Ð·ÐµÐ»ÐµÐ½ÑÐ¹","w":300.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð§Ð°Ð¹ ÑÑÑÐ½ÑÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð§Ð°Ð¹ ÑÑÑÐ½ÑÐ¹","w":200.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð§Ð°Ð¹ ÑÑÑÐ½ÑÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð§Ð°Ð¹ ÑÑÑÐ½ÑÐ¹","w":300.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ Ð­ÑÐ» ÐÑÐµÐ¹ (Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ Ð­ÑÐ» ÐÑÐµÐ¹","w":200.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ Ð­ÑÐ» ÐÑÐµÐ¹ (ÑÑÐµÐ´Ð½ÑÑ)","base_name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ Ð­ÑÐ» ÐÑÐµÐ¹","w":300.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"ÑÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÑÑÐ¿ÑÐµÑÑÐ¾","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÑÑÐ¿ÑÐµÑÑÐ¾","w":70.0,"k":2.0,"p":0.2,"f":0.1,"c":0.2,"page":14,"portion":""},{"name":"ÐÐ¼ÐµÑÐ¸ÐºÐ°Ð½Ð¾ (ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¼ÐµÑÐ¸ÐºÐ°Ð½Ð¾","w":200.0,"k":7.0,"p":0.6,"f":0.2,"c":0.6,"page":15,"portion":"ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¼ÐµÑÐ¸ÐºÐ°Ð½Ð¾ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¼ÐµÑÐ¸ÐºÐ°Ð½Ð¾","w":300.0,"k":10.0,"p":0.9,"f":0.3,"c":0.9,"page":15,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¼ÐµÑÐ¸ÐºÐ°Ð½Ð¾ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¼ÐµÑÐ¸ÐºÐ°Ð½Ð¾","w":400.0,"k":14.0,"p":1.2,"f":0.4,"c":1.2,"page":15,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ (ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾","w":200.0,"k":71.0,"p":3.6,"f":3.8,"c":5.6,"page":15,"portion":"ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾","w":300.0,"k":113.0,"p":5.8,"f":6.0,"c":8.9,"page":15,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾","w":400.0,"k":132.0,"p":6.8,"f":7.0,"c":10.0,"page":15,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°ÑÑÐµ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°ÑÑÐµ","w":300.0,"k":122.0,"p":6.2,"f":6.5,"c":9.6,"page":15,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°ÑÑÐµ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ°ÑÑÐµ","w":400.0,"k":135.0,"p":6.9,"f":7.2,"c":11.0,"page":15,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾ÑÐµ Ð³Ð»ÑÑÐµ","base_name":"ÐÐ¾ÑÐµ Ð³Ð»ÑÑÐµ","w":280.0,"k":123.0,"p":3.6,"f":3.3,"c":20.0,"page":15,"portion":""},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ","w":300.0,"k":101.0,"p":5.2,"f":5.4,"c":8.0,"page":15,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ","w":400.0,"k":144.0,"p":7.4,"f":7.7,"c":11.0,"page":15,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ ÑÑÑÐ¾Ð¼","base_name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ ÑÑÑÐ¾Ð¼","w":116.0,"k":289.0,"p":16.0,"f":13.0,"c":26.0,"page":15,"portion":""},{"name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹","base_name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹","w":156.0,"k":312.0,"p":20.0,"f":14.0,"c":26.0,"page":15,"portion":""},{"name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","base_name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","w":121.0,"k":317.0,"p":18.0,"f":15.0,"c":26.0,"page":16,"portion":""},{"name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ ÑÐ²Ð¸Ð½Ð¾Ð¹ ÐºÐ¾ÑÐ»ÐµÑÐ¾Ð¹","base_name":"ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ ÑÐ²Ð¸Ð½Ð¾Ð¹ ÐºÐ¾ÑÐ»ÐµÑÐ¾Ð¹","w":161.0,"k":434.0,"p":25.0,"f":25.0,"c":26.0,"page":16,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ ÑÐ²Ð¸Ð½Ð¾Ð¹ ÐºÐ¾ÑÐ»ÐµÑÐ¾Ð¹","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ°ÑÑÐ¸Ð½ Ñ ÑÐ¹ÑÐ¾Ð¼ Ð¸ ÑÐ²Ð¸Ð½Ð¾Ð¹ ÐºÐ¾ÑÐ»ÐµÑÐ¾Ð¹","w":220.0,"k":628.0,"p":38.0,"f":40.0,"c":28.0,"page":16,"portion":""},{"name":"ÐÐ°ÑÑÐ¸Ð½ ÑÐ¾ ÑÐ²Ð¸Ð½Ð¾Ð¹ ÐºÐ¾ÑÐ»ÐµÑÐ¾Ð¹","base_name":"ÐÐ°ÑÑÐ¸Ð½ ÑÐ¾ ÑÐ²Ð¸Ð½Ð¾Ð¹ ÐºÐ¾ÑÐ»ÐµÑÐ¾Ð¹","w":116.0,"k":344.0,"p":18.0,"f":18.0,"c":26.0,"page":16,"portion":""},{"name":"Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½","base_name":"Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½","w":150.0,"k":368.0,"p":18.0,"f":20.0,"c":28.0,"page":16,"portion":""},{"name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½","base_name":"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½","w":196.0,"k":513.0,"p":28.0,"f":32.0,"c":28.0,"page":16,"portion":""},{"name":"Ð§Ð¸ÐºÐµÐ½ Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½","base_name":"Ð§Ð¸ÐºÐµÐ½ Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½","w":142.0,"k":325.0,"p":13.0,"f":14.0,"c":37.0,"page":16,"portion":""},{"name":"ÐÐ¼Ð»ÐµÑÑÐµÑ Ñ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼ Ð¸ ÑÑÑÐ¾Ð¼","base_name":"ÐÐ¼Ð»ÐµÑÑÐµÑ Ñ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼ Ð¸ ÑÑÑÐ¾Ð¼","w":133.0,"k":297.0,"p":16.0,"f":12.0,"c":29.0,"page":17,"portion":""},{"name":"Ð¤ÑÐµÑ Ð Ð¾Ð»Ð»","base_name":"Ð¤ÑÐµÑ Ð Ð¾Ð»Ð»","w":215.0,"k":537.0,"p":23.0,"f":34.0,"c":34.0,"page":17,"portion":""},{"name":"Ð§Ð¸ÐºÐµÐ½ Ð¤ÑÐµÑ Ð Ð¾Ð»Ð»","base_name":"Ð§Ð¸ÐºÐµÐ½ Ð¤ÑÐµÑ Ð Ð¾Ð»Ð»","w":250.0,"k":563.0,"p":24.0,"f":30.0,"c":48.0,"page":17,"portion":""},{"name":"Ð£ÑÑÐµÐ½Ð½Ð¸Ð¹ Ð Ð¾Ð»Ð»","base_name":"Ð£ÑÑÐµÐ½Ð½Ð¸Ð¹ Ð Ð¾Ð»Ð»","w":225.0,"k":550.0,"p":25.0,"f":29.0,"c":46.0,"page":17,"portion":""},{"name":"ÐÐ¼Ð»ÐµÑ","base_name":"ÐÐ¼Ð»ÐµÑ","w":149.0,"k":292.0,"p":17.0,"f":13.0,"c":26.0,"page":17,"portion":""},{"name":"ÐÐ¼Ð»ÐµÑ Ñ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","base_name":"ÐÐ¼Ð»ÐµÑ Ñ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","w":157.0,"k":331.0,"p":20.0,"f":16.0,"c":26.0,"page":17,"portion":""},{"name":"ÐÐ¼Ð»ÐµÑ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹","base_name":"ÐÐ¼Ð»ÐµÑ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹","w":189.0,"k":344.0,"p":24.0,"f":15.0,"c":27.0,"page":17,"portion":""},{"name":"ÐÐ¼Ð»ÐµÑ Ñ ÑÑÑÐ¾Ð¼","base_name":"ÐÐ¼Ð»ÐµÑ Ñ ÑÑÑÐ¾Ð¼","w":177.0,"k":389.0,"p":23.0,"f":21.0,"c":27.0,"page":18,"portion":""},{"name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ°","base_name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ°","w":149.0,"k":292.0,"p":17.0,"f":13.0,"c":26.0,"page":18,"portion":""},{"name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ° Ñ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","base_name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ° Ñ Ð±ÐµÐºÐ¾Ð½Ð¾Ð¼","w":157.0,"k":331.0,"p":20.0,"f":16.0,"c":26.0,"page":18,"portion":""},{"name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ° Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹","base_name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ° Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹","w":189.0,"k":344.0,"p":24.0,"f":15.0,"c":26.0,"page":18,"portion":""},{"name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ° Ñ ÑÑÑÐ¾Ð¼","base_name":"Ð¯Ð¸ÑÐ½Ð¸ÑÐ° Ñ ÑÑÑÐ¾Ð¼","w":177.0,"k":389.0,"p":23.0,"f":21.0,"c":27.0,"page":18,"portion":""},{"name":"ÐÐ»Ð¸Ð½Ñ","base_name":"ÐÐ»Ð¸Ð½Ñ","w":110.0,"k":207.0,"p":8.3,"f":6.6,"c":29.0,"page":18,"portion":""},{"name":"Ð ÑÐ»ÐµÑÐ¸ÐºÐ¸ Ñ ÑÐ²Ð¾ÑÐ¾Ð³Ð¾Ð¼ Ð¸ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð¾Ð¼","base_name":"Ð ÑÐ»ÐµÑÐ¸ÐºÐ¸ Ñ ÑÐ²Ð¾ÑÐ¾Ð³Ð¾Ð¼ Ð¸ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð¾Ð¼","w":72.0,"k":223.0,"p":6.5,"f":10.0,"c":27.0,"page":18,"portion":""},{"name":"Ð¢Ð¾ÑÑ Ñ ÑÑÑÐ¾Ð¼","base_name":"Ð¢Ð¾ÑÑ Ñ ÑÑÑÐ¾Ð¼","w":78.0,"k":240.0,"p":10.0,"f":9.7,"c":27.0,"page":19,"portion":""},{"name":"Ð¢Ð¾ÑÑ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","base_name":"Ð¢Ð¾ÑÑ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","w":98.0,"k":266.0,"p":13.0,"f":11.0,"c":28.0,"page":19,"portion":""},{"name":"Ð¡ÑÑÐ½Ð¸ÐºÐ¸","base_name":"Ð¡ÑÑÐ½Ð¸ÐºÐ¸","w":120.0,"k":221.0,"p":18.0,"f":2.6,"c":31.0,"page":19,"portion":""},{"name":"ÐÐ¾Ð»ÑÑÐ¾Ð¹ Ð·Ð°Ð²ÑÑÐ°Ðº","base_name":"ÐÐ¾Ð»ÑÑÐ¾Ð¹ Ð·Ð°Ð²ÑÑÐ°Ðº","w":194.0,"k":431.0,"p":26.0,"f":24.0,"c":26.0,"page":19,"portion":""},{"name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»ÑÐ½ÑÐ¹ ÐÐ»Ð°Ð´ÑÑÐµÐº","base_name":"ÐÐ°ÑÑÐ¾ÑÐµÐ»ÑÐ½ÑÐ¹ ÐÐ»Ð°Ð´ÑÑÐµÐº","w":44.0,"k":94.0,"p":1.7,"f":5.0,"c":9.9,"page":19,"portion":""},{"name":"Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½ ÐÐ°Ð·Ð¸Ð»Ð¸ÐºÐ¾Ð²ÑÐ¹","base_name":"Ð¤ÑÐµÑ ÐÐ°ÑÑÐ¸Ð½ ÐÐ°Ð·Ð¸Ð»Ð¸ÐºÐ¾Ð²ÑÐ¹","w":159.0,"k":396.0,"p":18.0,"f":21.0,"c":33.0,"page":19,"portion":""},{"name":"ÐÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹ ÑÐ¸Ð·ÐºÐµÐ¹Ðº","base_name":"ÐÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹ ÑÐ¸Ð·ÐºÐµÐ¹Ðº","w":115.0,"k":296.0,"p":4.8,"f":15.0,"c":35.0,"page":20,"portion":""},{"name":"Ð¢Ð¾ÑÑ Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹","base_name":"Ð¢Ð¾ÑÑ Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹","w":112.0,"k":419.0,"p":4.5,"f":25.0,"c":45.0,"page":20,"portion":""},{"name":"Ð¢Ð²Ð¾ÑÐ¾Ð¶Ð½Ð¸Ðº","base_name":"Ð¢Ð²Ð¾ÑÐ¾Ð¶Ð½Ð¸Ðº","w":70.0,"k":197.0,"p":6.0,"f":9.0,"c":23.0,"page":21,"portion":""},{"name":"Ð§Ð¸Ð·ÐºÐµÐ¹Ðº ÐºÐ»Ð°ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹","base_name":"Ð§Ð¸Ð·ÐºÐµÐ¹Ðº ÐºÐ»Ð°ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹","w":125.0,"k":426.0,"p":7.5,"f":26.0,"c":40.0,"page":21,"portion":""},{"name":"ÐÐ¸Ð¼Ð¾Ð½Ð½ÑÐ¹ ÑÐ°ÑÑ","base_name":"ÐÐ¸Ð¼Ð¾Ð½Ð½ÑÐ¹ ÑÐ°ÑÑ","w":108.0,"k":432.0,"p":4.9,"f":28.0,"c":40.0,"page":21,"portion":""},{"name":"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÑÐ°ÑÑ Ñ Ð²Ð¸ÑÐ½ÐµÐ¹","base_name":"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÑÐ°ÑÑ Ñ Ð²Ð¸ÑÐ½ÐµÐ¹","w":120.0,"k":298.0,"p":4.1,"f":11.0,"c":46.0,"page":21,"portion":""},{"name":"Ð§Ð¸Ð·ÐºÐµÐ¹Ðº Ð¡Ð°Ð½-Ð¡ÐµÐ±Ð°ÑÑÑÑÐ½","base_name":"Ð§Ð¸Ð·ÐºÐµÐ¹Ðº Ð¡Ð°Ð½-Ð¡ÐµÐ±Ð°ÑÑÑÑÐ½","w":90.0,"k":233.0,"p":4.2,"f":15.0,"c":20.0,"page":22,"portion":""},{"name":"ÐÐ¸ÑÐ¾Ð¶Ð½Ð¾Ðµ ÐÐ°ÑÑÐ¾ÑÐºÐ°","base_name":"ÐÐ¸ÑÐ¾Ð¶Ð½Ð¾Ðµ ÐÐ°ÑÑÐ¾ÑÐºÐ°","w":60.0,"k":341.0,"p":3.6,"f":22.0,"c":33.0,"page":22,"portion":""},{"name":"ÐÐ°Ð»Ð¸Ð½Ð¾Ð²Ð°Ñ ÑÐ°ÑÑÐ°Ð»ÐµÑÐºÐ°","base_name":"ÐÐ°Ð»Ð¸Ð½Ð¾Ð²Ð°Ñ ÑÐ°ÑÑÐ°Ð»ÐµÑÐºÐ°","w":120.0,"k":311.0,"p":4.2,"f":16.0,"c":38.0,"page":22,"portion":""},{"name":"ÐÐ¸ÑÐ¾Ð¶Ð½Ð¾Ðµ Ð¨Ñ Ñ Ð¾ÑÐµÑÐ¾Ð²Ð¾Ð¹ Ð½Ð°ÑÐ¸Ð½ÐºÐ¾Ð¹","base_name":"ÐÐ¸ÑÐ¾Ð¶Ð½Ð¾Ðµ Ð¨Ñ Ñ Ð¾ÑÐµÑÐ¾Ð²Ð¾Ð¹ Ð½Ð°ÑÐ¸Ð½ÐºÐ¾Ð¹","w":55.0,"k":219.0,"p":3.6,"f":16.0,"c":15.0,"page":22,"portion":""},{"name":"ÐÑÐµÐ¼Ð¸Ð°Ð»ÑÐ½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹ Ð¿Ð¸ÑÐ¾Ð³","base_name":"ÐÑÐµÐ¼Ð¸Ð°Ð»ÑÐ½ÑÐ¹ ÑÐ±Ð»Ð¾ÑÐ½ÑÐ¹ Ð¿Ð¸ÑÐ¾Ð³","w":145.0,"k":285.0,"p":2.9,"f":9.3,"c":47.0,"page":23,"portion":""},{"name":"ÐÐ¸ÑÐ¾Ð¶Ð½Ð¾Ðµ Ð¯Ð³Ð¾Ð´Ð½ÑÐ¹ ÐºÐ¾ÑÐ¼Ð¾Ñ","base_name":"ÐÐ¸ÑÐ¾Ð¶Ð½Ð¾Ðµ Ð¯Ð³Ð¾Ð´Ð½ÑÐ¹ ÐºÐ¾ÑÐ¼Ð¾Ñ","w":95.0,"k":360.0,"p":3.3,"f":15.0,"c":52.0,"page":23,"portion":""},{"name":"ÐÐ°Ð¿ÐºÐµÐ¹Ðº Ð¡Ð¾Ð»ÐµÐ½Ð°Ñ ÐºÐ°ÑÐ°Ð¼ÐµÐ»Ñ","base_name":"ÐÐ°Ð¿ÐºÐµÐ¹Ðº Ð¡Ð¾Ð»ÐµÐ½Ð°Ñ ÐºÐ°ÑÐ°Ð¼ÐµÐ»Ñ","w":95.0,"k":388.0,"p":4.3,"f":25.0,"c":37.0,"page":24,"portion":""},{"name":"ÐÑÑÐ°Ð²ÐµÐ¹Ð½Ð¸Ðº","base_name":"ÐÑÑÐ°Ð²ÐµÐ¹Ð½Ð¸Ðº","w":80.0,"k":403.0,"p":5.6,"f":22.0,"c":45.0,"page":24,"portion":""},{"name":"ÐÑÑÐ°ÑÑÐ°Ð½","base_name":"ÐÑÑÐ°ÑÑÐ°Ð½","w":62.0,"k":213.0,"p":4.3,"f":12.0,"c":22.0,"page":24,"portion":""},{"name":"ÐÑÑÐ°ÑÑÐ°Ð½ ÐºÐ»Ð°ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹","base_name":"ÐÑÑÐ°ÑÑÐ°Ð½ ÐºÐ»Ð°ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹","w":74.0,"k":253.0,"p":4.5,"f":13.0,"c":30.0,"page":24,"portion":""},{"name":"ÐÐµÑÐµÐ½ÑÐµ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½Ð¾Ðµ Ñ ÐºÑÑÐ¾ÑÐºÐ°Ð¼Ð¸ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð°","base_name":"ÐÐµÑÐµÐ½ÑÐµ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½Ð¾Ðµ Ñ ÐºÑÑÐ¾ÑÐºÐ°Ð¼Ð¸ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð°","w":70.0,"k":310.0,"p":4.1,"f":15.0,"c":40.0,"page":25,"portion":""},{"name":"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÐºÑÑÐ°ÑÑÐ°Ð½","base_name":"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ ÐºÑÑÐ°ÑÑÐ°Ð½","w":72.0,"k":274.0,"p":4.7,"f":14.0,"c":33.0,"page":25,"portion":""},{"name":"ÐÐµÑÐµÐ½ÑÐµ ÐÐ°Ð»Ð¸Ð½Ð°-ÐÐµÐ»ÑÐ¹ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´","base_name":"ÐÐµÑÐµÐ½ÑÐµ ÐÐ°Ð»Ð¸Ð½Ð°-ÐÐµÐ»ÑÐ¹ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´","w":75.0,"k":332.0,"p":3.8,"f":13.0,"c":49.0,"page":25,"portion":""},{"name":"ÐÐµÑÐµÐ½ÑÐµ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½-Ð¼Ð¸Ð½Ð´Ð°Ð»Ñ","base_name":"ÐÐµÑÐµÐ½ÑÐµ ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½-Ð¼Ð¸Ð½Ð´Ð°Ð»Ñ","w":75.0,"k":305.0,"p":4.4,"f":14.0,"c":40.0,"page":25,"portion":""},{"name":"Ð£Ð»Ð¸ÑÐºÐ° Ñ ÐºÐ°ÑÐ°Ð¼ÐµÐ»ÑÑ","base_name":"Ð£Ð»Ð¸ÑÐºÐ° Ñ ÐºÐ°ÑÐ°Ð¼ÐµÐ»ÑÑ","w":95.0,"k":301.0,"p":4.5,"f":16.0,"c":34.0,"page":26,"portion":""},{"name":"ÐÑÑÐ°ÑÑÐ°Ð½ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","base_name":"ÐÑÑÐ°ÑÑÐ°Ð½ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","w":130.0,"k":351.0,"p":17.0,"f":20.0,"c":25.0,"page":26,"portion":""},{"name":"ÐÑÑÐ°ÑÑÐ°Ð½ ÐºÐ»Ð°ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","base_name":"ÐÑÑÐ°ÑÑÐ°Ð½ ÐºÐ»Ð°ÑÑÐ¸ÑÐµÑÐºÐ¸Ð¹ Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","w":142.0,"k":391.0,"p":17.0,"f":21.0,"c":33.0,"page":26,"portion":""},{"name":"Ð§Ð¸Ð°Ð±Ð°ÑÑÐ° Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","base_name":"Ð§Ð¸Ð°Ð±Ð°ÑÑÐ° Ñ Ð²ÐµÑÑÐ¸Ð½Ð¾Ð¹ Ð¸ ÑÑÑÐ¾Ð¼","w":212.0,"k":432.0,"p":23.0,"f":17.0,"c":47.0,"page":26,"portion":""},{"name":"Ð§Ð¸Ð°Ð±Ð°ÑÑÐ° Ñ ÑÑÐ½ÑÐ¾Ð¼","base_name":"Ð§Ð¸Ð°Ð±Ð°ÑÑÐ° Ñ ÑÑÐ½ÑÐ¾Ð¼","w":168.0,"k":371.0,"p":22.0,"f":11.0,"c":44.0,"page":26,"portion":""},{"name":"ÐÐµÐ½ÑÐºÐ¸Ð¹ ÐÐ¾ÑÐµ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐµÐ½ÑÐºÐ¸Ð¹ ÐÐ¾ÑÐµ","w":250.0,"k":174.0,"p":1.8,"f":17.0,"c":3.8,"page":27,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐµÐ½ÑÐºÐ¸Ð¹ ÐÐ¾ÑÐµ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐµÐ½ÑÐºÐ¸Ð¹ ÐÐ¾ÑÐµ","w":350.0,"k":177.0,"p":2.1,"f":17.0,"c":4.1,"page":27,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð Ð°Ñ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð Ð°Ñ","w":300.0,"k":285.0,"p":5.9,"f":22.0,"c":17.0,"page":27,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð Ð°Ñ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð Ð°Ñ","w":400.0,"k":316.0,"p":7.5,"f":24.0,"c":19.0,"page":27,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ¾ÑÑÑÐ¸Ð¹ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ¾ÑÑÑÐ¸Ð¹ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´","w":300.0,"k":319.0,"p":8.1,"f":19.0,"c":31.0,"page":27,"portion":""},{"name":"Ð§Ð°Ð¹ ÐÐµÐ»ÐµÐ½ÑÐ¹ Ñ Ð¶Ð°ÑÐ¼Ð¸Ð½Ð¾Ð¼","base_name":"Ð§Ð°Ð¹ ÐÐµÐ»ÐµÐ½ÑÐ¹ Ñ Ð¶Ð°ÑÐ¼Ð¸Ð½Ð¾Ð¼","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ Ñ ÑÐ°Ð±ÑÐµÑÐ¾Ð¼","base_name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ Ñ ÑÐ°Ð±ÑÐµÑÐ¾Ð¼","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Ð§Ð°Ð¹ ÐÐµÐ»ÐµÐ½ÑÐ¹ Ð¥ÑÐ³Ð¾ ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ","base_name":"Ð§Ð°Ð¹ ÐÐµÐ»ÐµÐ½ÑÐ¹ Ð¥ÑÐ³Ð¾ ÐÐ¾ÐºÑÐµÐ¹Ð»Ñ","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Ð§Ð°Ð¹ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ Ð»Ð°Ð¹Ð¼-Ð¸Ð¼Ð±Ð¸ÑÑ","base_name":"Ð§Ð°Ð¹ Ð·ÐµÐ»ÐµÐ½ÑÐ¹ Ð»Ð°Ð¹Ð¼-Ð¸Ð¼Ð±Ð¸ÑÑ","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ ÑÑÐ¾Ð¿Ð¸ÑÐµÑÐºÐ¸Ðµ ÑÑÑÐºÑÑ","base_name":"Ð§Ð°Ð¹ ÑÐµÑÐ½ÑÐ¹ ÑÑÐ¾Ð¿Ð¸ÑÐµÑÐºÐ¸Ðµ ÑÑÑÐºÑÑ","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":28,"portion":""},{"name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹","w":330.0,"k":290.0,"p":4.4,"f":14.0,"c":37.0,"page":28,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹","w":440.0,"k":360.0,"p":5.1,"f":14.0,"c":53.0,"page":28,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹","w":330.0,"k":283.0,"p":3.3,"f":14.0,"c":36.0,"page":28,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹","w":440.0,"k":332.0,"p":3.4,"f":14.0,"c":48.0,"page":28,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ°Ð»Ð¸Ð½Ð°-Ð±ÐµÐ»ÑÐ¹ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´","base_name":"Ð¤ÑÐ°Ð¿Ð¿Ðµ ÐÐ°Ð»Ð¸Ð½Ð°-Ð±ÐµÐ»ÑÐ¹ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´","w":330.0,"k":359.0,"p":3.1,"f":25.0,"c":30.0,"page":28,"portion":""},{"name":"ÐÐ°Ð±Ð» ÐÐ¹Ñ ÐÐ¾ÑÐµ","base_name":"ÐÐ°Ð±Ð» ÐÐ¹Ñ ÐÐ¾ÑÐµ","w":400.0,"k":240.0,"p":6.0,"f":6.0,"c":40.0,"page":28,"portion":""},{"name":"ÐÐ°Ð±Ð»-ÑÐ¸ ÐÐ½Ð°Ð½Ð°Ñ-Ð»ÐµÐ¼Ð¾Ð½Ð³ÑÐ°ÑÑ","base_name":"ÐÐ°Ð±Ð»-ÑÐ¸ ÐÐ½Ð°Ð½Ð°Ñ-Ð»ÐµÐ¼Ð¾Ð½Ð³ÑÐ°ÑÑ","w":310.0,"k":166.0,"p":0.0,"f":0.0,"c":41.0,"page":29,"portion":""},{"name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ¹Ñ ÐÐ°ÑÑÐ° ÐÐ¾ÐºÐ¾Ñ","base_name":"ÐÐ¾Ð»Ð¾ÑÐ½ÑÐ¹ ÑÐ¾ÑÑÐ°Ð²Ð½Ð¾Ð¹ Ð¿ÑÐ¾Ð´ÑÐºÑ ÐÐ¹Ñ ÐÐ°ÑÑÐ° ÐÐ¾ÐºÐ¾Ñ","w":310.0,"k":334.0,"p":9.1,"f":20.0,"c":29.0,"page":29,"portion":""},{"name":"Ð­ÑÐ¿ÑÐµÑÑÐ¾-ÑÐ¾Ð½Ð¸Ðº ÐÑÐ°Ð½Ð°Ñ","base_name":"Ð­ÑÐ¿ÑÐµÑÑÐ¾-ÑÐ¾Ð½Ð¸Ðº ÐÑÐ°Ð½Ð°Ñ","w":294.0,"k":107.0,"p":0.4,"f":0.3,"c":26.0,"page":29,"portion":""},{"name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":176.0,"k":30.0,"p":0.7,"f":1.6,"c":3.3,"page":29,"portion":"ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":176.0,"k":42.0,"p":0.9,"f":2.2,"c":4.6,"page":29,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":325.0,"k":54.0,"p":1.2,"f":2.8,"c":5.9,"page":29,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ)","base_name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":176.0,"k":40.0,"p":1.3,"f":1.7,"c":4.9,"page":29,"portion":"ÐÐ°Ð»ÐµÐ½ÑÐºÐ°Ñ"},{"name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":176.0,"k":56.0,"p":1.8,"f":2.4,"c":6.9,"page":29,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ°Ð¿ÑÑÐ¸Ð½Ð¾ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":325.0,"k":72.0,"p":2.3,"f":3.0,"c":8.9,"page":29,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°ÑÑÐµ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ°ÑÑÐµ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":270.0,"k":47.0,"p":1.0,"f":2.5,"c":5.2,"page":30,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ°ÑÑÐµ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ°ÑÑÐµ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":270.0,"k":51.0,"p":1.1,"f":2.7,"c":5.7,"page":30,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ°ÑÑÐµ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"ÐÐ°ÑÑÐµ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":270.0,"k":63.0,"p":2.0,"f":2.7,"c":7.8,"page":30,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"ÐÐ°ÑÑÐµ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"ÐÐ°ÑÑÐµ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":270.0,"k":69.0,"p":2.2,"f":2.9,"c":8.5,"page":30,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":245.0,"k":42.0,"p":0.9,"f":2.2,"c":4.6,"page":30,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":245.0,"k":59.0,"p":1.3,"f":3.1,"c":6.5,"page":30,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (Ð¡ÑÐµÐ´Ð½ÑÑ)","base_name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":245.0,"k":56.0,"p":1.8,"f":2.3,"c":6.9,"page":30,"portion":"Ð¡ÑÐµÐ´Ð½ÑÑ"},{"name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹ (ÐÐ¾Ð»ÑÑÐ°Ñ)","base_name":"Ð¤Ð»ÑÑ Ð£Ð°Ð¹Ñ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":245.0,"k":79.0,"p":2.5,"f":3.3,"c":9.8,"page":30,"portion":"ÐÐ¾Ð»ÑÑÐ°Ñ"},{"name":"ÐÐ¹Ñ ÐÐ¾ÑÐµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","base_name":"ÐÐ¹Ñ ÐÐ¾ÑÐµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ ÐÐ¸Ð½Ð´Ð°Ð»ÑÐ½ÑÐ¹","w":194.0,"k":90.0,"p":0.6,"f":1.3,"c":19.0,"page":30,"portion":""},{"name":"ÐÐ¹Ñ ÐÐ¾ÑÐµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","base_name":"ÐÐ¹Ñ ÐÐ¾ÑÐµ ÐÐ°ÑÐ°Ð¼ÐµÐ»Ñ ÐÐ¾ÐºÐ¾ÑÐ¾Ð²ÑÐ¹","w":194.0,"k":96.0,"p":1.1,"f":1.4,"c":20.0,"page":30,"portion":""},{"name":"ÐÐµÑÑÑÐ¿","base_name":"ÐÐµÑÑÑÐ¿","w":25.0,"k":30.0,"p":0.38,"f":0.05,"c":6.75,"page":30,"portion":""},{"name":"Ð¡Ð¾ÑÑ ÐÐ¸ÑÐ»Ð¾-Ð¡Ð»Ð°Ð´ÐºÐ¸Ð¹","base_name":"Ð¡Ð¾ÑÑ ÐÐ¸ÑÐ»Ð¾-Ð¡Ð»Ð°Ð´ÐºÐ¸Ð¹","w":25.0,"k":40.0,"p":0.12,"f":0.25,"c":9.5,"page":31,"portion":""},{"name":"Ð¡Ð¾ÑÑ ÐÐ¾ÑÑÐ¸ÑÐ½ÑÐ¹","base_name":"Ð¡Ð¾ÑÑ ÐÐ¾ÑÑÐ¸ÑÐ½ÑÐ¹","w":25.0,"k":53.75,"p":0.5,"f":3.0,"c":5.75,"page":31,"portion":""},{"name":"Ð¡Ð¾ÑÑ ÐÐ°ÑÐ±ÐµÐºÑ","base_name":"Ð¡Ð¾ÑÑ ÐÐ°ÑÐ±ÐµÐºÑ","w":25.0,"k":40.0,"p":0.12,"f":0.25,"c":9.0,"page":31,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹","base_name":"Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹","w":25.0,"k":90.0,"p":0.5,"f":9.25,"c":1.5,"page":31,"portion":""},{"name":"Ð¡Ð¾ÑÑ 1000 Ð¾ÑÑÑÐ¾Ð²Ð¾Ð²","base_name":"Ð¡Ð¾ÑÑ 1000 Ð¾ÑÑÑÐ¾Ð²Ð¾Ð²","w":25.0,"k":77.5,"p":0.25,"f":7.25,"c":3.0,"page":32,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð¡Ð»Ð°Ð´ÐºÐ¸Ð¹ Ð§Ð¸Ð»Ð¸","base_name":"Ð¡Ð¾ÑÑ Ð¡Ð»Ð°Ð´ÐºÐ¸Ð¹ Ð§Ð¸Ð»Ð¸","w":25.0,"k":42.5,"p":0.05,"f":0.03,"c":10.25,"page":32,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð´ÐµÑÐµÑÑÐ½ÑÐ¹ Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹","base_name":"Ð¡Ð¾ÑÑ Ð´ÐµÑÐµÑÑÐ½ÑÐ¹ Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹","w":25.0,"k":72.5,"p":0.88,"f":0.88,"c":15.0,"page":32,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹ ÑÐ°Ð»Ð°Ð¿ÐµÐ½ÑÐ¾","base_name":"Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹ ÑÐ°Ð»Ð°Ð¿ÐµÐ½ÑÐ¾","w":25.0,"k":77.5,"p":0.25,"f":7.25,"c":2.75,"page":32,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð§Ð¸Ð»Ð¸-ÐÐ°Ð¹Ð¼","base_name":"Ð¡Ð¾ÑÑ Ð§Ð¸Ð»Ð¸-ÐÐ°Ð¹Ð¼","w":25.0,"k":35.0,"p":0.5,"f":0.12,"c":8.0,"page":32,"portion":""},{"name":"ÐÑÑÐµÐ·Ð¸Ð°Ð½ÑÐºÐ°Ñ Ð²Ð¾Ð´Ð° Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° Ð½ÐµÐ³Ð°Ð·Ð¸ÑÐ¾Ð²Ð°Ð½Ð½Ð°Ñ","base_name":"ÐÑÑÐµÐ·Ð¸Ð°Ð½ÑÐºÐ°Ñ Ð²Ð¾Ð´Ð° Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° Ð½ÐµÐ³Ð°Ð·Ð¸ÑÐ¾Ð²Ð°Ð½Ð½Ð°Ñ","w":500.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":33,"portion":""},{"name":"ÐÐ¸ÑÑÐµÐ²Ð°Ñ Ð²Ð¾Ð´Ð° Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° Ð³Ð°Ð·Ð¸ÑÐ¾Ð²Ð°Ð½Ð½Ð°Ñ","base_name":"ÐÐ¸ÑÑÐµÐ²Ð°Ñ Ð²Ð¾Ð´Ð° Ð§ÐµÑÐ½Ð¾Ð³Ð¾Ð»Ð¾Ð²ÐºÐ° Ð³Ð°Ð·Ð¸ÑÐ¾Ð²Ð°Ð½Ð½Ð°Ñ","w":500.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":33,"portion":""},{"name":"ÐÐ¶ÐµÐ¼ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹","base_name":"ÐÐ¶ÐµÐ¼ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹","w":20.0,"k":48.0,"p":0.0,"f":0.0,"c":12.0,"page":33,"portion":""},{"name":"ÐÐ»Ð¸Ð²ÐºÐ¾Ð²Ð¾Ðµ Ð¼Ð°ÑÐ»Ð¾","base_name":"ÐÐ»Ð¸Ð²ÐºÐ¾Ð²Ð¾Ðµ Ð¼Ð°ÑÐ»Ð¾","w":10.0,"k":82.0,"p":0.0,"f":9.13,"c":0.0,"page":33,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð¦ÐµÐ·Ð°ÑÑ","base_name":"Ð¡Ð¾ÑÑ Ð¦ÐµÐ·Ð°ÑÑ","w":25.0,"k":60.0,"p":0.62,"f":5.5,"c":1.75,"page":33,"portion":""},{"name":"ÐÐ¾ÑÐºÐ¾Ð²Ð½ÑÐµ Ð¿Ð°Ð»Ð¾ÑÐºÐ¸","base_name":"ÐÐ¾ÑÐºÐ¾Ð²Ð½ÑÐµ Ð¿Ð°Ð»Ð¾ÑÐºÐ¸","w":80.0,"k":28.0,"p":1.04,"f":0.08,"c":5.52,"page":33,"portion":""},{"name":"Ð¯Ð±Ð»Ð¾ÑÐ½ÑÐµ Ð´Ð¾Ð»ÑÐºÐ¸","base_name":"Ð¯Ð±Ð»Ð¾ÑÐ½ÑÐµ Ð´Ð¾Ð»ÑÐºÐ¸","w":80.0,"k":37.6,"p":0.32,"f":0.32,"c":7.84,"page":33,"portion":""},{"name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¾Ð»Ð°\"","base_name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¾Ð»Ð°\"","w":500.0,"k":210.0,"p":0.0,"f":0.0,"c":53.0,"page":34,"portion":""},{"name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°\"","base_name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°\"","w":500.0,"k":1.5,"p":0.0,"f":0.0,"c":0.5,"page":34,"portion":""},{"name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼\"","base_name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¸Ð¼Ð¾Ð½-ÐÐ°Ð¹Ð¼\"","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":34,"portion":""},{"name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½\"","base_name":"ÐÐ¾Ð±ÑÑÐ¹ \"ÐÐ¿ÐµÐ»ÑÑÐ¸Ð½\"","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":34,"portion":""},{"name":"ÐÐ¸Ð¿ÑÐ¾Ð½ ÐÐ¸Ð¼Ð¾Ð½","base_name":"ÐÐ¸Ð¿ÑÐ¾Ð½ ÐÐ¸Ð¼Ð¾Ð½","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":34,"portion":""},{"name":"ÐÐ°Ð»Ð¸Ð½Ð¾Ð²ÑÐ¹ Ð¼ÑÑÑ","base_name":"ÐÐ°Ð»Ð¸Ð½Ð¾Ð²ÑÐ¹ Ð¼ÑÑÑ","w":100.0,"k":229.0,"p":2.3,"f":13.3,"c":25.1,"page":34,"portion":""},{"name":"Ð¤ÑÑÐºÑÐ¾Ð²ÑÐµ Ð¿Ð°ÑÑÐ¸Ð»ÐºÐ¸","base_name":"Ð¤ÑÑÐºÑÐ¾Ð²ÑÐµ Ð¿Ð°ÑÑÐ¸Ð»ÐºÐ¸","w":15.0,"k":49.5,"p":0.15,"f":0.01,"c":12.3,"page":35,"portion":""},{"name":"ÐÐ¸ÑÑÑÐµÐºÑ Ð¸Ð· Ð³Ð¾Ð²ÑÐ´Ð¸Ð½Ñ ÑÑÐ±Ð»ÐµÐ½ÑÐ¹ 80 Ð³ / ÐÐ¸ÑÑÑÐµÐºÑ","base_name":"ÐÐ¸ÑÑÑÐµÐºÑ Ð¸Ð· Ð³Ð¾Ð²ÑÐ´Ð¸Ð½Ñ ÑÑÐ±Ð»ÐµÐ½ÑÐ¹ 80 Ð³ / ÐÐ¸ÑÑÑÐµÐºÑ","w":80.0,"k":213.6,"p":19.2,"f":15.2,"c":0.0,"page":35,"portion":""},{"name":"Ð¡Ð¾ÑÑ Ð¢Ð°Ñ Ð¢Ð°Ñ","base_name":"Ð¡Ð¾ÑÑ Ð¢Ð°Ñ Ð¢Ð°Ñ","w":20.0,"k":40.0,"p":0.1,"f":3.8,"c":1.2,"page":35,"portion":""},{"name":"Ð¡Ð¾ÑÑ ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","base_name":"Ð¡Ð¾ÑÑ ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","w":10.0,"k":33.0,"p":0.2,"f":3.2,"c":0.9,"page":36,"portion":""},{"name":"ÐÐ¾ÑÑÐ¸ÑÐ° / Ð¡Ð¾ÑÑ Ð³Ð¾ÑÑÐ¸ÑÐ½ÑÐ¹","base_name":"ÐÐ¾ÑÑÐ¸ÑÐ° / Ð¡Ð¾ÑÑ Ð³Ð¾ÑÑÐ¸ÑÐ½ÑÐ¹","w":0.5,"k":0.35,"p":0.02,"f":0.02,"c":0.01,"page":36,"portion":""},{"name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹ / Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ \"ÐÐ¶ÐµÐ¼ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹\"","base_name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹ / Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ \"ÐÐ¶ÐµÐ¼ ÐºÐ»ÑÐ±Ð½Ð¸ÑÐ½ÑÐ¹\"","w":30.0,"k":59.4,"p":0.12,"f":0.03,"c":14.49,"page":36,"portion":""},{"name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ / Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ \"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½Ð°Ñ Ð¿Ð¾Ð¼Ð°Ð´ÐºÐ°\"","base_name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÑÐ¾ÐºÐ¾Ð»Ð°Ð´Ð½ÑÐ¹ / Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ \"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½Ð°Ñ Ð¿Ð¾Ð¼Ð°Ð´ÐºÐ°\"","w":30.0,"k":103.5,"p":0.78,"f":3.93,"c":15.99,"page":36,"portion":""},{"name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐºÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹ / Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ \"ÐÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½Ð°Ñ Ð¿Ð¾Ð¼Ð°Ð´ÐºÐ°\"","base_name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐºÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹ / Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ \"ÐÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½Ð°Ñ Ð¿Ð¾Ð¼Ð°Ð´ÐºÐ°\"","w":30.0,"k":96.9,"p":0.6,"f":1.5,"c":20.22,"page":37,"portion":""},{"name":"Ð¡Ð¸ÑÐ¾Ð¿ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¹","base_name":"Ð¡Ð¸ÑÐ¾Ð¿ Ð²Ð°Ð½Ð¸Ð»ÑÐ½ÑÐ¹","w":24.0,"k":50.4,"p":0.0,"f":0.0,"c":12.72,"page":37,"portion":""},{"name":"Ð¡Ð¸ÑÐ¾Ð¿ ÐºÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹","base_name":"Ð¡Ð¸ÑÐ¾Ð¿ ÐºÐ°ÑÐ°Ð¼ÐµÐ»ÑÐ½ÑÐ¹","w":24.0,"k":50.4,"p":0.0,"f":0.0,"c":12.72,"page":37,"portion":""},{"name":"ÐÐ¾Ð»Ð¾ÐºÐ¾","base_name":"ÐÐ¾Ð»Ð¾ÐºÐ¾","w":30.0,"k":18.0,"p":0.9,"f":0.96,"c":1.41,"page":38,"portion":""},{"name":"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½Ð°Ñ ÐºÑÐ¾ÑÐºÐ° / ÐÑÐ¾ÑÐºÐ° Ð¿ÐµÑÐµÐ½ÑÑ Ñ ÐºÐ°ÐºÐ°Ð¾","base_name":"Ð¨Ð¾ÐºÐ¾Ð»Ð°Ð´Ð½Ð°Ñ ÐºÑÐ¾ÑÐºÐ° / ÐÑÐ¾ÑÐºÐ° Ð¿ÐµÑÐµÐ½ÑÑ Ñ ÐºÐ°ÐºÐ°Ð¾","w":8.0,"k":35.2,"p":0.6,"f":1.12,"c":5.6,"page":38,"portion":""},{"name":"Ð¥Ð°Ð»Ð°Ð¿ÐµÐ½ÑÐ¾","base_name":"Ð¥Ð°Ð»Ð°Ð¿ÐµÐ½ÑÐ¾","w":9.0,"k":1.53,"p":0.04,"f":0.02,"c":0.22,"page":38,"portion":""},{"name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐÐ½Ð°Ð½Ð°Ñ-Ð¿Ð¸ÑÐ°ÑÐ°Ð¹Ñ","base_name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐÐ½Ð°Ð½Ð°Ñ-Ð¿Ð¸ÑÐ°ÑÐ°Ð¹Ñ","w":30.0,"k":55.2,"p":0.06,"f":0.0,"c":13.62,"page":38,"portion":""},{"name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐÐ°ÑÐ°ÐºÑÐ¹Ñ Ñ ÐºÐ¾ÑÑÐ¾ÑÐºÐ¾Ð¹","base_name":"Ð¢Ð¾Ð¿Ð¿Ð¸Ð½Ð³ ÐÐ°ÑÐ°ÐºÑÐ¹Ñ Ñ ÐºÐ¾ÑÑÐ¾ÑÐºÐ¾Ð¹","w":30.0,"k":64.8,"p":0.15,"f":0.02,"c":15.84,"page":38,"portion":""}];
// Values independently verified against the official currently available PDF.
// Other rows still await full-document re-extraction and comparison.
const CHAIN_VERIFIED_CURRENT={"Ð¤Ð¸Ñ ÐÑÑÐ³ÐµÑ":{"w":130,"k":327,"p":13,"f":13,"c":40},"ÐÐ¸Ð³ Ð¥Ð¸Ñ":{"w":216,"k":503,"p":25,"f":25,"c":45},"Ð§Ð¸ÐºÐµÐ½ Ð¥Ð¸Ñ":{"w":190,"k":445,"p":19,"f":19,"c":50},"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»":{"w":326,"k":756,"p":41,"f":42,"c":52},"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»":{"w":433,"k":1042,"p":67,"f":63,"c":52},"ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¥Ð¸Ñ":{"w":284,"k":676,"p":40,"f":37,"c":46}};
for(const row of CHAIN_ROWS){const current=CHAIN_VERIFIED_CURRENT[row.base_name];if(current && row.portion===''){Object.assign(row,current,{source_date:'2026-11-20'})}}
const chainNormalize=(s)=>String(s||'').toLowerCase().replaceAll('Ñ','Ðµ').replace(/[Â«Â»"']/g,'').replace(/(?:^|\s)(?:Ð¸Ð·\s+)?Ð¼Ð°Ðº(?:Ð°|Ðµ|Ð¾Ð¼)?(?=\s|$)/g,' ').replace(/Ð²ÐºÑÑÐ½Ð¾\s*[-ââ]?\s*Ð¸\s*ÑÐ¾ÑÐºÐ°/gi,' ').replace(/^Ð´Ð¾Ð±ÑÑÐ¹\s+/i,' ').replace(/[()]/g,' ').replace(/[^a-zÐ°-Ñ0-9\s]/gi,' ').replace(/\s+/g,' ').trim();
function chainFind(query,top=8){
 const raw=chainNormalize(query)
   .replace(/Ð½Ð°Ð³Ð³ÐµÑÑ(?:Ð¾Ð²|Ð°Ð¼Ð¸|Ñ|Ð°)?/g,'Ð½Ð°Ð³Ð³ÐµÑÑÑ').replace(/ÐºÐ°ÑÑÐ¾ÑÐº(?:Ð°|Ð¸|Ñ|Ð¾Ð¹)?/g,'ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ')
   .replace(/ÐºÐ¾Ð»Ð°\s*(?:Ð·ÐµÑÐ¾|zero)/g,'ÐºÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°').replace(/ÑÐ¸Ð·Ð±ÑÑÐ³ÐµÑÐ°(?![Ð°-Ñ])/g,'ÑÐ¸Ð·Ð±ÑÑÐ³ÐµÑ').replace(/Ð³Ð°Ð¼Ð±ÑÑÐ³ÐµÑÐ°(?![Ð°-Ñ])/g,'Ð³Ð°Ð¼Ð±ÑÑÐ³ÐµÑ');
 const qwords=raw.split(' ').filter(x=>x.length>2&&!['ÑÑ','Ð¿Ð¾ÑÑÐ¸Ñ','Ð¿Ð¾ÑÑÐ¸Ð¸','Ð³ÑÐ°Ð¼Ð¼','Ð´Ð²Ð°','ÑÑÐ¸','Ð¾Ð´Ð½Ð°','Ð¾Ð´Ð¸Ð½','Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ','ÑÑÐµÐ´Ð½ÑÑ','Ð±Ð¾Ð»ÑÑÐ°Ñ'].includes(x));
 const qty=(raw.match(/\b(4|6|9|18)\s*(?:ÑÑ|Ð½Ð°Ð³Ð³ÐµÑÑÐ¾Ð²|Ð½Ð°Ð³Ð³ÐµÑÑÑ)/)||[])[1]
      ||(raw.match(/\b(4|6|9|18)\b/)&&/Ð½Ð°Ð³Ð³ÐµÑÑ/.test(raw)?(raw.match(/\b(4|6|9|18)\b/)||[])[1]:null);
 const wantedSize=/Ð¼Ð°Ð»ÐµÐ½ÑÐº|Ð¼Ð°Ð»ÑÐ¹|Ð¼Ð°Ð»\b/.test(raw)?'Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ':/Ð±Ð¾Ð»ÑÑ|Ð±Ð¾Ð»\b/.test(raw)?'Ð±Ð¾Ð»ÑÑÐ°Ñ':/ÑÑÐµÐ´Ð½|ÑÑÐµÐ´\b/.test(raw)?'ÑÑÐµÐ´Ð½ÑÑ':'';
 const scored=[];
 for(const r of CHAIN_ROWS){const base=chainNormalize(r.base_name),label=chainNormalize(r.name);let score=0;
  if(raw===label)score+=130;else if(raw===base)score+=110;
  if(qwords.length && qwords.every(w=>label.includes(w)))score+=40;
  if(qwords.length && qwords.every(w=>base.includes(w)))score+=35;
  if(qwords.some(w=>!label.includes(w)))score-=38;
  if(raw.includes(base)&&base.length>5)score+=15;
  if(qty)score+=label.includes(qty+' ÑÑ')?60:-60;
  if(wantedSize)score+=r.portion.toLowerCase().includes(wantedSize)?40:-25;
  if(!wantedSize && r.portion){score+=/ÑÑÐµÐ´Ð½/.test(r.portion.toLowerCase())?3:0;}
  if(/\bÐ´Ð²Ð¾Ð¹Ð½/.test(raw)&&!base.includes('Ð´Ð²Ð¾Ð¹Ð½'))score-=90;
  if(/\bÐ±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°/.test(raw)&&!base.includes('Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'))score-=140;
  if(base.includes('Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°')&&!raw.includes('Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'))score-=50;
  if(score>=25)scored.push({...r,source:'ÐÐºÑÑÐ½Ð¾ â Ð¸ ÑÐ¾ÑÐºÐ°',official_url:CHAIN_OFFICIAL_PDF,score});
 }
 scored.sort((a,b)=>b.score-a.score);
 return scored.slice(0,top);
}
function chainResult(q){const rows=chainFind(q);return {ok:true,query:q,items:rows,exact:rows.length>0&&rows[0].score>=85,official_pdf:CHAIN_OFFICIAL_PDF}}
const SLV_URL='https://dataportal.livsmedelsverket.se/livsmedel/api/v1';
let SWEDISH_INDEX_CACHE={until:0,items:[]};
function swedishNutrients(values){
 if(!Array.isArray(values))return null;
 const find=(codes,names)=>{for(const n of values){let code=String(n.euroFIRkod||'').toUpperCase(),name=String(n.namn||'').toLowerCase();
  if(codes.includes(code)||names.some(v=>name===v||name.startsWith(v+' ')))return Number(n.varde);}
 return NaN;};
 const k=find(['ENERC'],['energi (kcal)','energy (kcal)']);
 const p=find(['PROT'],['protein']);
 const f=find(['FAT'],['fett','fat']);
 const c=find(['CHOAVL','CHOAVLDF'],['kolhydrater, tillgÃ¤ngliga','carbohydrate, available','carbohydrates available']);
 if(!finiteFood(k,p,f,c))return null;
 return {k,p,f,c};
}
async function searchSwedish(q){
 const started=Date.now();try{
  let foods=SWEDISH_INDEX_CACHE.items;
  if(!foods.length || SWEDISH_INDEX_CACHE.until<Date.now()){
   const r=await sourceJson(SLV_URL+'/livsmedel?limit=3000&offset=0&sprak=2',{},'SLV index');
   if(!r.ok)throw Error(r.diagnostic);
   foods=Array.isArray(r.json?.livsmedel)?r.json.livsmedel:[];
   if(!foods.length)throw Error('ÐÐµ Ð¿Ð¾Ð»ÑÑÐµÐ½ ÑÐ¿Ð¸ÑÐ¾Ðº Ð¿ÑÐ¾Ð´ÑÐºÑÐ¾Ð²');
   SWEDISH_INDEX_CACHE={until:Date.now()+24*60*60*1000,items:foods};
  }
  const terms=q.toLowerCase().match(/[a-z]{3,}/g)||[];
  if(!terms.length)return {ok:true,items:[],diagnostic:'Ð¨Ð²ÐµÑÐ¸Ñ: Ð´Ð»Ñ Ð¿Ð¾Ð¸ÑÐºÐ° Ð½ÑÐ¶ÐµÐ½ Ð¿ÐµÑÐµÐ²Ð¾Ð´ Ð½Ð° Ð°Ð½Ð³Ð»Ð¸Ð¹ÑÐºÐ¸Ð¹'};
  const best=foods.map(x=>{const s=String(x.namn||'').toLowerCase();let score=0;
    if(s===q.toLowerCase())score+=100;
    if(s.startsWith(q.toLowerCase()+' '))score+=70;
    terms.forEach(t=>{if(s.includes(t))score+=22;else score-=45});
    return {...x,score};}).filter(x=>x.score>=22).sort((a,b)=>b.score-a.score).slice(0,3);
  const detail=await Promise.all(best.map(async x=>{
   const r=await sourceJson(SLV_URL+'/livsmedel/'+encodeURIComponent(x.nummer)+'/naringsvarden?sprak=2',{},'SLV food');
   const n=r.ok?swedishNutrients(r.json):null;
   return n?{name:x.namn,source:'Livsmedelsverket (Ð¨Ð²ÐµÑÐ¸Ñ)',slv_id:x.nummer,match_score:x.score,...n}:null;
  }));
  return {ok:true,items:detail.filter(Boolean),diagnostic:`Livsmedelsverket: ÑÐ¿Ð¸ÑÐ¾Ðº ${foods.length}; ÑÐ¾Ð²Ð¿Ð°Ð´ÐµÐ½Ð¸Ð¹ ${detail.filter(Boolean).length}; ${Date.now()-started} Ð¼Ñ`};
 }catch(e){return {ok:false,items:[],diagnostic:`Livsmedelsverket: ${String(e.message||e)}; ${Date.now()-started} Ð¼Ñ`};}
}

// v1.3: allow calls from the PWA origin without exposing a wildcard CORS policy.
// Note: Origin checking restricts browser access; it is NOT a substitute for
// authentication/rate limits, because non-browser clients can spoof Origin.

// Restaurant order recognition v1.9: first ask the model to segment the whole order,
// then independently validate all words against the restaurant's real menu.
// The lexical pass prevents missing commas from collapsing an entire order.
const ORDER_ALIASES_RAW = [
 ['Ð´Ð²Ð¾Ð¹Ð½Ð¾Ð¹ Ð±Ð¸Ð³ ÑÐµÐ¹ÑÑÐ¸','ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»'],
 ['Ð±Ð¸Ð³ ÑÐµÐ¹ÑÑÐ¸ Ð´Ð¶ÑÐ½Ð¸Ð¾Ñ','ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð» ÐÐ¶ÑÐ½Ð¸Ð¾Ñ'],
 ['Ð±Ð¸Ð³ ÑÐµÐ¹ÑÑÐ¸','ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»'],
 ['Ð±Ð¸Ð³ ÑÑÐ¹ÑÑÐ¸','ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»'],
 ['big tasty','ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»'],
 ['Ð´Ð²Ð¾Ð¹Ð½Ð¾Ð¹ Ð±Ð¸Ð³ ÑÐ¸Ñ','ÐÐ²Ð¾Ð¹Ð½Ð¾Ð¹ ÐÐ¸Ð³ Ð¥Ð¸Ñ'],
 ['Ð±Ð¸Ð³ ÑÐ¸Ñ','ÐÐ¸Ð³ Ð¥Ð¸Ñ'],
 ['Ð±Ð¸Ð³ ÑÐ¸ÑÐ°','ÐÐ¸Ð³ Ð¥Ð¸Ñ'],
 ['ÐºÐ°ÑÑÐ¾ÑÐºÐ° Ð¿Ð¾ Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸'],
 ['ÐºÐ°ÑÑÐ¾ÑÐºÑ Ð¿Ð¾ Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸'],
 ['ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾ Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸'],
 ['ÐºÐ°ÑÑÐ¾ÑÐºÐ° Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ°Ñ','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸'],
 ['Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ°Ñ ÐºÐ°ÑÑÐ¾ÑÐºÐ°','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¿Ð¾-Ð´ÐµÑÐµÐ²ÐµÐ½ÑÐºÐ¸'],
 ['ÐºÐ°ÑÑÐ¾ÑÐºÐ° ÑÑÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸'],
 ['ÐºÐ°ÑÑÐ¾ÑÐºÑ ÑÑÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸'],
 ['ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ ÑÑÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸'],
 ['ÑÑÐ¸','ÐÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¤ÑÐ¸'],
 ['ÐºÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'],
 ['ÐºÐ¾ÐºÐ° ÐºÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'],
 ['ÐºÐ¾Ð»Ð° Ð·ÐµÑÐ¾','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'],
 ['ÐºÐ¾Ð»Ð° zero','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'],
 ['Ð´Ð¾Ð±ÑÑÐ¹ ÐºÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð° Ð±ÐµÐ· ÑÐ°ÑÐ°ÑÐ°'],
 ['Ð´Ð¾Ð±ÑÑÐ¹ ÐºÐ¾Ð»Ð°','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð°'],
 ['ÐºÐ¾Ð»Ð°','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð°'],
 ['ÐºÐ¾ÐºÐ° ÐºÐ¾Ð»Ð°','ÐÐ¾Ð±ÑÑÐ¹ ÐÐ¾Ð»Ð°'],
 ['ÑÑÑÐ½ÑÐ¹ ÑÐ¾ÑÑ','Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹'],
 ['ÑÐ¾ÑÑ ÑÑÑÐ½ÑÐ¹','Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹'],
 ['ÑÐ¾ÑÑ Ñ ÑÑÑÐ¾Ð¼','Ð¡Ð¾ÑÑ Ð¡ÑÑÐ½ÑÐ¹'],
 ['Ð½Ð°Ð³Ð³ÐµÑÑÐ¾Ð²','ÐÐ°Ð³Ð³ÐµÑÑÑ'],['Ð½Ð°Ð³Ð³ÐµÑÑÑ','ÐÐ°Ð³Ð³ÐµÑÑÑ'],
 ['ÑÐ¸Ð·Ð±ÑÑÐ³ÐµÑÐ°','Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ'],['ÑÐ¸Ð·Ð±ÑÑÐ³ÐµÑ','Ð§Ð¸Ð·Ð±ÑÑÐ³ÐµÑ'],
 ['Ð³Ð°Ð¼Ð±ÑÑÐ³ÐµÑÐ°','ÐÐ°Ð¼Ð±ÑÑÐ³ÐµÑ'],['Ð³Ð°Ð¼Ð±ÑÑÐ³ÐµÑ','ÐÐ°Ð¼Ð±ÑÑÐ³ÐµÑ']
];
const orderWords=s=>String(s||'').toLowerCase().replaceAll('Ñ','Ðµ').match(/[a-zÐ°-Ñ0-9]+/gi)||[];
const orderSize=t=>/^(?:Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ|Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ¸Ð¹|Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ¾Ðµ|Ð¼Ð°Ð»ÐµÐ½ÑÐº|Ð¼Ð°Ð»ÑÐ¹|Ð¼Ð°Ð»Ð°Ñ|Ð¼Ð°Ð»ÑÑ|Ð¼Ð°Ð»Ð°Ñ|Ð¼Ð°Ð»ÐµÐ½ÑÐºÑÑ|Ð½ÐµÐ±Ð¾Ð»ÑÑÐ°Ñ|Ð½ÐµÐ±Ð¾Ð»ÑÑÐ¾Ð¹|Ð½ÐµÐ±Ð¾Ð»ÑÑÑÑ|Ð¼Ð°Ð»)$/.test(t)?'Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ':/^(?:ÑÑÐµÐ´Ð½|ÑÑÐµÐ´Ð½ÑÑ|ÑÑÐµÐ´Ð½Ð¸Ð¹|ÑÑÐµÐ´Ð½ÑÑ|ÑÑÐµÐ´Ð½ÐµÐµ|ÑÑÐµÐ´Ð½ÐµÐ¹)$/.test(t)?'ÑÑÐµÐ´Ð½ÑÑ':/^(?:Ð±Ð¾Ð»ÑÑ|Ð±Ð¾Ð»ÑÑÐ°Ñ|Ð±Ð¾Ð»ÑÑÐ¾Ð¹|Ð±Ð¾Ð»ÑÑÑÑ|ÐºÑÑÐ¿Ð½Ð°Ñ|Ð¾Ð³ÑÐ¾Ð¼Ð½Ð°Ñ)$/.test(t)?'Ð±Ð¾Ð»ÑÑÐ°Ñ':'';
const ORDER_FILLERS=new Set(['Ð¸Ð·','Ð²','Ð¼Ð°Ðº','Ð¼Ð°ÐºÐ°','Ð¼Ð°ÐºÐµ','Ð¼Ð°ÐºÐ¾Ð¼','Ð¸','ÐµÑÐµ','ÐµÑÑ','Ð¼Ð½Ðµ','Ð´Ð°Ð¹','Ð¿Ð¾Ð¶Ð°Ð»ÑÐ¹ÑÑÐ°','Ð·Ð°ÐºÐ°Ð·','Ð·Ð°ÐºÐ°Ð·Ð°Ð»','Ð·Ð°ÐºÐ°Ð·Ð°Ð»Ð°','Ð²Ð¾Ð·ÑÐ¼Ð¸','ÑÐ¾ÑÑ','ÑÑÐµÐ»','ÑÑÐµÐ»Ð°','ÑÐµÐ³Ð¾Ð´Ð½Ñ','Ð¿Ð»ÑÑ','Ð´Ð¾Ð±Ð°Ð²Ñ','Ð´Ð²Ð°','Ð¾Ð´Ð¸Ð½','Ð¾Ð´Ð½Ð°','ÑÑ','ÑÑÑÐºÐ¸','ÑÑÑÐº','Ð¿Ð¾ÑÑÐ¸Ñ','Ð¿Ð¾ÑÑÐ¸Ð¸','Ð¿Ð¾ÑÑÐ¸Ð¹']);
function orderAliasTable(){
 const aliases=new Map(ORDER_ALIASES_RAW.map(([v,k])=>[orderWords(v).join(' '),k]));
 for(const row of CHAIN_ROWS){
  const b=orderWords(row.base_name),n=orderWords(row.name);
  if(b.length>=2)aliases.set(b.join(' '),row.base_name);
  if(n.length>=2 && !row.portion)aliases.set(n.join(' '),row.base_name);
  if(b.length===1 && b[0].length>=7 && !aliases.has(b[0])) aliases.set(b[0],row.base_name);
 }
 return [...aliases].map(([v,base])=>({words:v.split(' '),base,raw:v})).sort((a,b)=>b.words.length-a.words.length||b.raw.length-a.raw.length);
}
const ORDER_ALIAS_TABLE=orderAliasTable();
function scanMenuOrder(text){
 const original=String(text||'').slice(0,500);
 const raw=original.replace(/Ð²ÐºÑÑÐ½Ð¾\s*[-ââ]?\s*Ð¸\s*ÑÐ¾ÑÐºÐ°/ig,' ').replace(/Ð¼Ð°ÐºÐ´Ð¾Ð½Ð°Ð»Ð´Ñ/ig,' ')
  .replace(/(^|[\s,:;])(?:Ð¸Ð·\s+|Ð²\s+)?Ð¼Ð°Ðº(?:Ð°|Ðµ|Ð¾Ð¼)?(?=$|[\s,:;])/gi,'$1 ');
 const tokens=orderWords(raw),covered=new Array(tokens.length).fill(false),found=[];
 for(let i=0;i<tokens.length;){
  let match=null;
  for(const alias of ORDER_ALIAS_TABLE){if(alias.words.length+i>tokens.length)continue;
   if(alias.words.every((w,j)=>tokens[i+j]===w)){match=alias;break}
  }
  if(match){
   const at=i,end=i+match.words.length;
   for(let k=i;k<end;k++)covered[k]=true;
   found.push({base:match.base,phrase:tokens.slice(at,end).join(' '),start:at,end,amount:1,size:'',count:null});i=end;
  }else i++;
 }
 for(let z=0;z<found.length;z++){
  const f=found[z];
  // A size following an item belongs to that item; a size immediately before one belongs to it.
  const after=tokens[f.end];const before=tokens[f.start-1];
  if(after && orderSize(after)&&!covered[f.end]){f.size=orderSize(after);covered[f.end]=true}
  else if(before && orderSize(before)&&!covered[f.start-1]){f.size=orderSize(before);covered[f.start-1]=true}
  const prev=tokens[f.start-1],next=tokens[f.end];
  if(/^\d+$/.test(prev||'')&&!covered[f.start-1]){f.count=Number(prev);covered[f.start-1]=true}
  else if(/^\d+$/.test(next||'')&&!covered[f.end]){f.count=Number(next);covered[f.end]=true}
  if(f.count && !/Ð½Ð°Ð³Ð³ÐµÑÑ/.test(f.base.toLowerCase()))f.amount=Math.max(1,Math.min(f.count,12));
 }
 const leftovers=[];
 for(let i=0;i<tokens.length;){
  if(covered[i] || ORDER_FILLERS.has(tokens[i]) || orderSize(tokens[i])){i++;continue}
  let j=i+1;while(j<tokens.length&&!covered[j]&&!ORDER_FILLERS.has(tokens[j])&&!orderSize(tokens[j]))j++;
  const chunk=tokens.slice(i,j).join(' ');if(chunk)leftovers.push(chunk);i=j;
 }
 const meaningful=tokens.filter(t=>!ORDER_FILLERS.has(t)&&!orderSize(t));
 const ignored=ORDER_FILLERS;
 return {found,leftovers,recognized:found.map(x=>x.phrase),coverage:meaningful.length?Math.round(100*(meaningful.length-leftovers.join(' ').split(/\s+/).filter(Boolean).length)/meaningful.length):100,tokens};
}
function menuEntryForOrder(item){
 let candidates=CHAIN_ROWS.filter(r=>orderWords(r.base_name).join(' ')===orderWords(item.base).join(' '));
 if(!candidates.length){const alt=chainFind(item.base);if(alt.length&&alt[0].score>=85)candidates=[alt[0]]}
 if(!candidates.length)return {found:false,reason:'Ð¢Ð¾Ð²Ð°Ñ Ð½Ðµ Ð½Ð°Ð¹Ð´ÐµÐ½ Ð² ÐºÐ°ÑÐ°Ð»Ð¾Ð³Ðµ'};
 const q=item.count||0;
 if(/Ð½Ð°Ð³Ð³ÐµÑÑ/i.test(item.base)&&q){
  const exact=candidates.find(r=>String(r.portion).includes(String(q)+' ÑÑ'));
  if(exact)return {found:true,row:exact,quantity:1};
  return {found:false,reason:`ÐÐµÑ Ð¿ÑÐ¾Ð²ÐµÑÐµÐ½Ð½Ð¾Ð¹ Ð¿Ð¾ÑÑÐ¸Ð¸ Ð½Ð°Ð³Ð³ÐµÑÑÐ¾Ð²: ${q} ÑÑ`};
 }
 let chosen=null;
 if(item.size){chosen=candidates.find(r=>String(r.portion||'').toLowerCase().includes(item.size));}
 if(!chosen&&!item.size){chosen=candidates.find(r=>!r.portion)||candidates.find(r=>/ÑÑÐµÐ´Ð½/i.test(r.portion))||candidates[0]}
 if(!chosen){
  // Single-size drink data is only an estimate for 250/400ml; never claim this is
  // a new official PDF row, and report the scaling in the technical diagnostics.
  if(/ÐºÐ¾Ð»Ð°|Ð»Ð¸Ð¼Ð¾Ð½ Ð»Ð°Ð¹Ð¼|Ð°Ð¿ÐµÐ»ÑÑÐ¸Ð½/i.test(item.base)){
    const drink=candidates.find(r=>!r.portion&&r.w>0);
    const sizeML={Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ:250,ÑÑÐµÐ´Ð½ÑÑ:400,Ð±Ð¾Ð»ÑÑÐ°Ñ:500}[item.size];
    if(drink&&sizeML){const scale=sizeML/drink.w;return {found:true,quantity:1,row:{...drink,name:`${drink.base_name} (${item.size})`,w:sizeML,k:drink.k*scale,p:drink.p*scale,f:drink.f*scale,c:drink.c*scale,estimated_portion:true},reason:'ÐÑÐ¾Ð¿Ð¾ÑÑÐ¸Ð¾Ð½Ð°Ð»ÑÐ½ÑÐ¹ ÑÐ°ÑÑÑÑ Ð¿Ð¾ Ð·Ð½Ð°ÑÐµÐ½Ð¸Ñ ÐºÐ°ÑÐ°Ð»Ð¾Ð³Ð° Ð´Ð»Ñ '+drink.w+' Ð¼Ð», Ð½Ðµ Ð¾ÑÐ´ÐµÐ»ÑÐ½Ð°Ñ ÑÑÑÐ¾ÐºÐ° Ð¾ÑÐ¸ÑÐ¸Ð°Ð»ÑÐ½Ð¾Ð¹ ÑÐ°Ð±Ð»Ð¸ÑÑ'};}
  }
  return {found:false,reason:'ÐÐ»Ñ ÑÐºÐ°Ð·Ð°Ð½Ð½Ð¾Ð³Ð¾ ÑÐ°Ð·Ð¼ÐµÑÐ° Ð½ÐµÑ ÑÑÑÐ¾ÐºÐ¸ Ð² ÐºÐ°ÑÐ°Ð»Ð¾Ð³Ðµ'};
 }
 return {found:true,row:chosen,quantity:item.amount};
}
function validateAIDishes(aiData){
 return (aiData?.dishes||[]).map(d=>String(d.name||'').trim()).filter(Boolean);
}
async function analyzeRestaurantOrder(text,env){
 const started=Date.now();let neural=[],aiError=null,usage=null,attempts=0;
 const prompt='Ð Ð°Ð·Ð±ÐµÐ¹ ÑÐµÐºÑÑ Ð·Ð°ÐºÐ°Ð·Ð° Ð¸Ð· ÑÐµÑÑÐ¾ÑÐ°Ð½Ð° Â«ÐÐºÑÑÐ½Ð¾ â Ð¸ ÑÐ¾ÑÐºÐ°Â» Ð½Ð° ÐÐ¡Ð Ð¾ÑÐ´ÐµÐ»ÑÐ½ÑÐµ Ð¿ÑÐ¾Ð´ÑÐºÑÑ, Ð´Ð°Ð¶Ðµ ÐµÑÐ»Ð¸ Ð½ÐµÑ Ð·Ð°Ð¿ÑÑÑÑ Ð¸ ÑÐ¾ÑÐ·Ð° Â«Ð¸Â». ÐÑÐ¾ÑÑÐ¸ ÑÐµÐºÑÑ ÑÐµÐ»Ð¸ÐºÐ¾Ð¼: ÑÐµÑÑÐ¾ÑÐ°Ð½ ÑÐºÐ°Ð·Ð°Ð½ Ð¾Ð´Ð¸Ð½ Ð´Ð»Ñ Ð²ÑÐµÑ Ð¿Ð¾Ð·Ð¸ÑÐ¸Ð¹. ÐÑÐ¿ÑÐ°Ð²Ñ Ð¸Ð·Ð²ÐµÑÑÐ½ÑÐµ ÑÐ°Ð·Ð³Ð¾Ð²Ð¾ÑÐ½ÑÐµ Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ñ, Ð½Ð¾ Ð½Ðµ Ð¿ÑÐ¸Ð´ÑÐ¼ÑÐ²Ð°Ð¹ Ð½ÐµÐ¸Ð·Ð²ÐµÑÑÐ½ÑÑ. Â«ÐÐ¸Ð³ Ð¢ÐµÐ¹ÑÑÐ¸Â» = Â«ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»Â». ÐÐµÑÐ½Ð¸ ÑÐ¾Ð»ÑÐºÐ¾ JSON Ð²Ð¸Ð´Ð° {"dishes":[{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","items":[{"name":"ÐÐ¸Ð³ Ð¡Ð¿ÐµÑÐ¸Ð°Ð»","portion":"1 ÑÑÑÐºÐ°"}]}],"uncertain":[]}; ÐºÐ°Ð¶Ð´ÑÐ¹ Ð¿ÑÐ¾Ð´ÑÐºÑ Ð¾ÑÐ´ÐµÐ»ÑÐ½ÑÐ¼ Ð±Ð»ÑÐ´Ð¾Ð¼. Ð Ð°Ð·Ð¼ÐµÑ ÐºÐ¾Ð»Ñ/ÐºÐ°ÑÑÐ¾ÑÐµÐ»Ñ Ð¾ÑÑÐ°Ð²Ð»ÑÐ¹ Ð² Ð½Ð°Ð·Ð²Ð°Ð½Ð¸Ð¸ Ð¸Ð»Ð¸ portion. Ð¢ÐµÐºÑÑ: '+String(text).slice(0,500);
 try{
  attempts++;
  const ans=await env.AI.run(MODEL,{messages:[{role:'user',content:prompt}],chat_template_kwargs:{enable_thinking:false},max_completion_tokens:520,temperature:0.0});
  const parsed=parseFoodResponse(ans);neural=validateAIDishes(parsed.data);usage=ans?.usage||null;
 }catch(e){aiError=String(e?.message||e)}
 const lexical=scanMenuOrder(text);
 let recovery=[];
 if(lexical.leftovers.length){
  try{
   attempts++;
   const repairPrompt=`ÐÑÐ¾Ð²ÐµÑÑ ÑÐ¾Ð»ÑÐºÐ¾ ÐÐÐ ÐÐ¡ÐÐÐÐÐÐÐÐ«Ð Ð¤Ð ÐÐÐÐÐÐ¢Ð« Ð·Ð°ÐºÐ°Ð·Ð° Ð¸Ð· Â«ÐÐºÑÑÐ½Ð¾ â Ð¸ ÑÐ¾ÑÐºÐ°Â». ÐÑÑÐ¾Ð´Ð½ÑÐ¹ Ð·Ð°ÐºÐ°Ð·: ${String(text).slice(0,450)}. Ð£Ð¶Ðµ Ð²ÑÐ´ÐµÐ»ÐµÐ½Ð¾: ${lexical.found.map(x=>x.base).join(', ')}. ÐÐµ ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð½Ð¾: ${lexical.leftovers.join(', ')}. ÐÑÐ»Ð¸ Ð²Ð¾ ÑÑÐ°Ð³Ð¼ÐµÐ½ÑÐµ ÐµÑÑÑ ÐµÑÑ Ð¾Ð´Ð½Ð¾ Ð±Ð»ÑÐ´Ð¾, Ð²ÐµÑÐ½Ð¸ JSON {"dishes":[{"name":"ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¿ÑÐ¾Ð´ÑÐºÑÐ°","items":[{"name":"ÐÐ°Ð·Ð²Ð°Ð½Ð¸Ðµ Ð¿ÑÐ¾Ð´ÑÐºÑÐ°","portion":"1 ÑÑ"}]}]}; Ð¸Ð½Ð°ÑÐµ Ð²ÐµÑÐ½Ð¸ {"dishes":[],"uncertain":[]}. ÐÐµ Ð¿Ð¾Ð²ÑÐ¾ÑÑÐ¹ ÑÐ¶Ðµ ÑÐ°ÑÐ¿Ð¾Ð·Ð½Ð°Ð½Ð½ÑÐµ Ð±Ð»ÑÐ´Ð°.`;
   const ans=await env.AI.run(MODEL,{messages:[{role:'user',content:repairPrompt}],chat_template_kwargs:{enable_thinking:false},max_completion_tokens:420,temperature:0.0});
   recovery=validateAIDishes(parseFoodResponse(ans).data);
   neural.push(...recovery);
   if(ans?.usage?.neurons!=null)usage={...(usage||{}),recheck_neurons:ans.usage.neurons};
  }catch(e){aiError=(aiError?aiError+'; ':'')+'second pass: '+String(e?.message||e)}
 }
 let parsed=lexical.found.map(entry=>({input:entry.phrase,canonical:entry.base,size:entry.size,amount:entry.amount,count:entry.count,...menuEntryForOrder(entry)}));
 // The model can supply a missed item, but only if the catalog independently
 // verifies it AND its name is not already present in the scan's output.
 if(lexical.leftovers.length && neural.length){
  for(const phrase of neural){
   const p=phrase.replace(/(?:^|\s)(Ð¼Ð°Ð»ÐµÐ½ÑÐºÐ°Ñ|ÑÑÐµÐ´Ð½ÑÑ|Ð±Ð¾Ð»ÑÑÐ°Ñ)(?=\s|$)/gi,' ').trim();
   const leftoverWords=new Set(lexical.leftovers.flatMap(orderWords).filter(w=>w.length>=3));
   if(!orderWords(p).some(w=>leftoverWords.has(w)))continue;
   const canonical=ORDER_ALIAS_TABLE.find(a=>a.words.join(' ')===orderWords(p).join(' '))?.base||p;
   const key=orderWords(canonical).join(' ');
   if(parsed.some(x=>orderWords(x.canonical).join(' ')===key))continue;
   const r=menuEntryForOrder({base:canonical,amount:1,size:'',count:null});
   if(r.found)parsed.push({input:phrase,canonical,amount:1,size:'',...r,from:'ai_recovery'});
  }
 }
 for(const leftover of lexical.leftovers){
  // Keep unseen text visible as an unresolved product; never lose source words.
  if(parsed.some(p=>orderWords(p.input).join(' ')===leftover))continue;
  parsed.push({input:leftover,canonical:leftover,found:false,reason:'ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ ÑÐ¾Ð¿Ð¾ÑÑÐ°Ð²Ð¸ÑÑ ÑÑÐ°Ð³Ð¼ÐµÐ½Ñ Ð·Ð°ÐºÐ°Ð·Ð° Ñ Ð¼ÐµÐ½Ñ'});
 }
 if(!parsed.length){
  parsed=neural.map(x=>{const entry={base:x,size:'',amount:1,count:null};return {input:x,canonical:x,...menuEntryForOrder(entry)}});
 }
 if(!parsed.length)parsed=[{input:text,canonical:text,found:false,reason:'ÐÐµ ÑÐ´Ð°Ð»Ð¾ÑÑ ÑÐ°Ð·Ð´ÐµÐ»Ð¸ÑÑ Ð·Ð°ÐºÐ°Ð·'}];
 return {ok:true,restaurant:'ÐÐºÑÑÐ½Ð¾ â Ð¸ ÑÐ¾ÑÐºÐ°',dishes:parsed,diagnostics:{elapsed_ms:Date.now()-started,neural,second_pass:recovery,neural_error:aiError,ai_attempts:attempts,usage,scanner:lexical,matched:parsed.map(p=>({input:p.input,name:p.row?.name,score:p.row?.score||null,estimated:p.row?.estimated_portion||false,found:p.found,reason:p.reason||null})),missing:parsed.filter(x=>!x.found).map(x=>x.input)}};
}

const APP_ORIGIN = 'https://drop-443886b1-4e5.evpoluyanov.workers.dev';
export default {
  async fetch(request,env) {
    const origin=request.headers.get('Origin');
    const own=new URL(request.url).origin;
    const isOwn=origin===own;
    const allowed=!origin || origin===APP_ORIGIN || isOwn;
    if(!allowed) return asJson({ok:false,error:'Origin not allowed'},403);
    if(request.method==='OPTIONS') {
      if(origin!==APP_ORIGIN && !isOwn) return asJson({ok:false,error:'Origin not allowed'},403);
      return new Response(null,{status:204,headers:{
        'Access-Control-Allow-Origin':origin,
        'Access-Control-Allow-Methods':'POST, GET, OPTIONS',
        'Access-Control-Allow-Headers':'Content-Type, Accept',
        'Access-Control-Max-Age':'86400',
        'Vary':'Origin'
      }});
    }
    const u=new URL(request.url);

    if(request.method==='POST' && u.pathname==='/order-analyze'){
      if(!env.AI) return asJson({ok:false,error:'ÐÐµ Ð´Ð¾Ð±Ð°Ð²Ð»ÐµÐ½ Workers AI binding AI'},503);
      let body;try{body=await request.json()}catch(_){return asJson({ok:false,error:'ÐÑÐ¶ÐµÐ½ JSON Ñ Ð¿Ð¾Ð»ÐµÐ¼ text'},400)}
      const text=String(body?.text||'').slice(0,500).trim();
      if(!text) return asJson({ok:false,error:'ÐÐµ ÑÐºÐ°Ð·Ð°Ð½ ÑÐµÐºÑÑ Ð·Ð°ÐºÐ°Ð·Ð°'},400);
      const response=asJson(await analyzeRestaurantOrder(text,env));
      if(origin===APP_ORIGIN||isOwn){const headers=new Headers(response.headers);headers.set('Access-Control-Allow-Origin',origin);headers.set('Vary','Origin');return new Response(response.body,{status:response.status,headers})}return response;
    }
    if(request.method==='GET'&&u.pathname==='/chain-search'){
      const response=asJson(chainResult(u.searchParams.get('q')||''));
      if(origin===APP_ORIGIN || isOwn){const h=new Headers(response.headers);h.set('Access-Control-Allow-Origin',origin);h.set('Vary','Origin');return new Response(response.body,{status:response.status,headers:h})}return response;
    }
    if(request.method==='GET'&&u.pathname==='/chain-status'){
      let official={url:CHAIN_OFFICIAL_PDF,last_modified:null,etag:null,status:null,checked:new Date().toISOString()};
      try{const r=await fetch(CHAIN_OFFICIAL_PDF,{method:'HEAD',signal:AbortSignal.timeout(9000)});official.status=r.status;official.last_modified=r.headers.get('last-modified');official.etag=r.headers.get('etag')}catch(e){official.error=String(e.message||e)}
      return asJson({ok:true,source_date:CHAIN_PDF_DATE,rows:CHAIN_ROWS.length,official,notice:'ÐÑÐ¾Ð²ÐµÑÐºÐ° Ð´Ð¾ÑÑÑÐ¿Ð½Ð¾ÑÑÐ¸ PDF Ð½Ðµ ÑÐ²Ð»ÑÐµÑÑÑ Ð¿ÑÐ±Ð»Ð¸ÐºÐ°ÑÐ¸ÐµÐ¹ Ð½Ð¾Ð²ÑÑ ÐÐÐÐ£.'});
    }
    if(request.method==='POST'&&u.pathname==='/nutrition-batch'){
      let qs=[];try{const body=await request.json();qs=Array.isArray(body.queries)?body.queries.slice(0,12).map(q=>String(q).slice(0,100)):[]}catch(_){return asJson({ok:false,error:'Bad JSON'},400)}
      const unique=[...new Set(qs.filter(q=>q.trim().length>=2))];
      const results=await Promise.all(unique.map(async q=>{
        try{const r=await searchNutrition(q,env,{fast:true});return {query:q,...r};}
        catch(e){return {query:q,ok:false,items:[],error:String(e?.message||e),diagnostics:['ÐÑÐ¸Ð±ÐºÐ° Ð¾ÑÐ´ÐµÐ»ÑÐ½Ð¾Ð³Ð¾ Ð·Ð°Ð¿ÑÐ¾ÑÐ°: '+String(e?.message||e)]};}
      }));
      const response=asJson({ok:true,results});
      if(origin===APP_ORIGIN || isOwn){const h=new Headers(response.headers);h.set('Access-Control-Allow-Origin',origin);h.set('Vary','Origin');return new Response(response.body,{status:response.status,headers:h})}return response;
    }
    if(request.method==='GET'&&(u.pathname==='/nutrition-search'||u.pathname==='/nutrition-health')){
      const result=await searchNutrition(u.searchParams.get('q')||(u.pathname==='/nutrition-health'?'yogurt':''),env);
      const response=asJson(result,result.ok?200:502);
      if(origin===APP_ORIGIN || isOwn){const headers=new Headers(response.headers);headers.set('Access-Control-Allow-Origin',origin);headers.set('Vary','Origin');return new Response(response.body,{status:response.status,headers})}
      return response;
    }
    const response=await originalHandler.fetch(request,env);
    if(origin===APP_ORIGIN || isOwn){
      const headers=new Headers(response.headers);
      headers.set('Access-Control-Allow-Origin',origin);
      headers.set('Vary','Origin');
      return new Response(response.body,{status:response.status,headers});
    }
    return response;
  }
};
