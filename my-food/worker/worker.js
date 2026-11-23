// Моя еда — Workers AI: распознавание и отказоустойчивый поиск КБЖУ v2.1.
// Только для личной проверки. Публичный URL нельзя использовать как открытый API без защиты.
// Требуется binding типа Workers AI с именем AI (env.AI).
const MODEL = '@cf/google/gemma-4-26b-a4b-it';
const PROMPT = `Ты — специалист по распознаванию питания. Возвращай ОДИН полный JSON без текста снаружи. Основное правило: САМОСТОЯТЕЛЬНО по своим знаниям оцени ВЕС порции в граммах и КАЛОРИИ, БЕЛКИ, ЖИРЫ, УГЛЕВОДЫ ИСКЛЮЧИТЕЛЬНО НА 100 ГРАММ. НИКОГДА не возвращай КБЖУ целой порции в поле per100. Не подменяй нулём неизвестные значения: используй null. Все числа — JSON numbers, не строки. Не используй внешний справочник как скрытый источник пересчёта массы.
Обязательная схема: {"input_mode":"text","recognized_text":null,"consumed_description":"","dishes":[{"name":"Название блюда","kind":"prepared","mode":"whole","weight_g":150,"main":"Название","main_portion":"одна порция","main_weight_g":150,"main_weight_basis":"оценка ИИ или вес указан пользователем","weight_estimated":true,"per100":{"k":210,"p":12,"f":9,"c":20},"items":[],"additions":[]}],"uncertain":[]}.
Если хорошо известны готовое БЛЮДО, его приблизительный вес и КБЖУ на 100 г, возврати ОДИН dish с mode:"whole"; items и additions ПУСТЫ, per100 содержит КБЖУ именно блюда со всеми включёнными соусами/начинкой, без двойного учёта.
Если нет достаточных знаний о КБЖУ готового блюда, возврати ОДИН dish с mode:"ingredients", kind:"recipe", per100:null, items:[{ "name":"Название ингредиента","portion":"его объём/счёт","weight_g":60,"volume_ml":null,"weight_estimated":true,"weight_basis":"оценка ИИ","per100":{"k":200,"p":10,"f":8,"c":14},"confidence":"medium"}]. Для КАЖДОГО названного компонента обязательно дай собственный weight_g и собственный per100 на 100 г ингредиента. Если дополнения представлены в additions, все они тоже обязаны иметь weight_g и per100. Ингредиент никогда не должен считаться одновременно в items и additions. Масса готового блюда weight_g должна равняться сумме масс ингредиентов; если неизвестна — оставь null, приложение суммирует известные составляющие.
Каждый отдельно съеденный продукт из перечисления — отдельный dish. Для «2 яйца, 20 г печени трески и соус тартар 10г» верни ТРИ dishes с весами: яйца оценка ИИ, печень 20, соус 10. Для «2 блина, каждый с начинкой из чайной ложки творожного сыра и кусочком слабосоленой семги» верни ОДНО блюдо, включающее все три продукта; количества начинки суммарно на оба блина. Не пропускай основную часть блюда. Не добавляй неупомянутую еду. Если вес указан явно («20 г», «0,2 кг»), перенеси его БЕЗ ИЗМЕНЕНИЯ и weight_estimated:false, в остальных случаях оцени вес самостоятельно и weight_estimated:true. Для жидкостей при возможности добавь volume_ml, но КБЖУ всегда на 100 ГРАММ, не на 100 мл.
Для ФОТО самостоятельно определи: это изображение еды или текст с меню/этикетки/рецепта. При фото еды используй input_mode:"photo_food" и оцени вес и per100 по видимой пище. При фото с текстом используй input_mode:"photo_text", перепиши относящийся к питанию текст в recognized_text, отдельно в consumed_description напиши ТОЛЬКО фразу с названиями и количеством еды (без строк с калориями и пищевой ценностью); затем разбери его ТОЧНО ТАК ЖЕ, как пользовательский текст. Если на этикетке прямо написано КБЖУ на 100 г, бери именно эти значения. Если написано на порцию или на 100 мл, самостоятельно переведи в 100 г с необходимой оценкой массы; не называй такие значения точными. Не считай все позиции сфотографированного меню съеденными без указания пользователя. Пожалуйста, не путай вес порции и вес продукта на 100 г.
Поля k,p,f,c: ккал, белки г, жиры г, углеводы г. Реалистичные числа на 100 г: k 0..900, p,f,c 0..100; не придумывай значения, если невозможно оценить, укажи null и пометь в uncertain. Если НЕ МОЖЕШЬ назвать достоверные КБЖУ целого блюда, ОБЯЗАТЕЛЬНО разложи на ингредиенты. Макс. 8 блюд, до 15 составляющих. Ответ на русском.`;

const page = `<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Моя еда — тест ИИ</title><style>body{font:16px -apple-system,system-ui,sans-serif;max-width:680px;margin:30px auto;padding:0 18px;color:#193e20;background:#f4fbef}h1{font-size:24px}.panel{background:white;border-radius:22px;padding:22px;box-shadow:0 3px 20px #17371116}label{display:block;margin:20px 0 8px;font-weight:600}input,textarea{font:inherit;max-width:100%;box-sizing:border-box}input[type=file]{width:100%}textarea{width:100%;min-height:90px;padding:12px;border:1px solid #bdd9bc;border-radius:10px}button{background:#2f9716;color:white;border:0;border-radius:12px;padding:15px 20px;font-size:17px;font-weight:700;margin-top:18px}button:disabled{opacity:.5}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f1f8ee;border-radius:12px;padding:16px}.note{color:#65766b;font-size:14px}</style></head><body><div class="panel"><h1>Моя еда — облачный тест</h1><p>Обработка фото выполняется в Cloudflare, не на iPhone.</p><form id="f"><label>Фотография (необязательно для текстового теста)</label><input name="photo" type="file" accept="image/jpeg,image/png,image/webp"><label>Описание / уточнение</label><textarea name="text" placeholder="Например, торт Наполеон или обед с гарниром"></textarea><button id="go">Распознать</button></form><p class="note">Тестовая версия: фото автоматически уменьшается до 1024 пикселей. Файлы не сохраняются в нашем Worker, но отправляются в сервис Cloudflare Workers AI. Не публикуйте адрес широко.</p><pre id="out" hidden></pre></div><script>document.getElementById('f').addEventListener('submit',async(e)=>{e.preventDefault();const b=document.getElementById('go'),o=document.getElementById('out');b.disabled=true;o.hidden=false;o.textContent='Подготовка изображения…';try{const data=new FormData(e.target);const file=data.get('photo');if(file&&file.size){const bmp=await createImageBitmap(file);const scale=Math.min(1,1024/Math.max(bmp.width,bmp.height));const c=document.createElement('canvas');c.width=Math.max(1,Math.round(bmp.width*scale));c.height=Math.max(1,Math.round(bmp.height*scale));c.getContext('2d').drawImage(bmp,0,0,c.width,c.height);bmp.close?.();const blob=await new Promise(ok=>c.toBlob(ok,'image/jpeg',0.78));if(!blob)throw Error('Не удалось уменьшить фото');data.set('photo',new File([blob],'meal.jpg',{type:'image/jpeg'}))}o.textContent='Распознавание…';const r=await fetch('/analyze',{method:'POST',body:data});const j=await r.json();o.textContent=JSON.stringify(j,null,2)}catch(err){o.textContent='Ошибка: '+err.message}finally{b.disabled=false}})</script></body></html>`;

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
    throw Error('ИИ вернул JSON без ожидаемых полей');
  }
  const text=String(value||'').trim().replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'').trim();
  if(!text) throw Error('Пустой ответ ИИ');
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
  if(!found.length) throw Error('Ответ нейросети не содержит завершённого JSON нужного формата');
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
  if(!answer) throw new Error('Модель не вернула финальный content. finish_reason='+String(result?.choices?.[0]?.finish_reason||'unknown'));
  const parsed=parseModelJson(answer,x=>x&&typeof x==='object'&&
    (Array.isArray(x.dishes)&&x.dishes.length>0||Array.isArray(x.items)&&x.items.length>0));
  return {data:normalizeFood(parsed),answer};
}
function massNumber(value){
 if(value==null || value==='')return null;
 const v=Number(String(value).replace(',','.'));
 return Number.isFinite(v)&&v>0&&v<=10000?Math.round(v*10)/10:null;
}
function normalizePer100(raw){
 const x=raw?.per100 ?? raw?.nutrition_per100 ?? raw?.kbju_per100 ?? null;
 if(!x || typeof x!=='object')return null;
 const out={};
 for(const key of ['k','p','f','c']){
   const value=x[key] ?? ({k:x.kcal,p:x.protein,f:x.fat,c:x.carbs})[key];
   const parsed=value===null||value===undefined||value===''?null:Number(String(value).replace(',','.'));
   out[key]=Number.isFinite(parsed)&&parsed>=0&&parsed<= (key==='k'?1000:100)?parsed:null;
 }
 return out;
}
function isCompletePer100(per100){return !!per100&&['k','p','f','c'].every(x=>Number.isFinite(per100[x])&&per100[x]>=0)}
function normalizeFood(obj){
 if(!obj || (!Array.isArray(obj.dishes)&&!Array.isArray(obj.items)))throw Error('Модель не вернула dishes[] или items[]');
 const normItems=(items)=>Array.isArray(items)?items.slice(0,20).filter(x=>x&&typeof x.name==='string'&&x.name.trim()).map(x=>({
   name:x.name.slice(0,100).trim(),portion:String(x.portion||'1 порция').slice(0,100),
   weight_g:massNumber(x.weight_g??x.grams),volume_ml:massNumber(x.volume_ml),
   weight_estimated:x.weight_estimated!==false,weight_basis:String(x.weight_basis||'').slice(0,180),
   per100:normalizePer100(x),
   confidence:['high','medium','low'].includes(x.confidence)?x.confidence:'medium'
 })) : [];
 let dishes=Array.isArray(obj.dishes)?obj.dishes.slice(0,8).map(x=>{
   const items=normItems(x?.items),additions=normItems(x?.additions),main=String(x?.main||x?.name||'').slice(0,100).trim();
   const mainItem=items.find(z=>z.name.toLowerCase()===main.toLowerCase())|| (items.length===1?items[0]:null);
   const kind=['prepared','platter','recipe'].includes(x?.kind)?x.kind:'prepared';
   // Never infer the choice from a directory or hard-coded food catalogue:
   // it is AI's own decision between a complete dish and ingredients.
   const mode=x?.mode==='ingredients'||x?.mode==='whole'?x.mode:(kind==='recipe' && items.length+additions.length>1?'ingredients':'whole');
   const ownWeight=massNumber(x?.weight_g);
   return {name:String(x?.name||'Блюдо').slice(0,100).trim(),kind,mode,
     weight_g:ownWeight,
     per100:normalizePer100(x),main,
     main_portion:String(x?.main_portion||mainItem?.portion||'1 порция').slice(0,100).trim(),
     main_weight_g:(mode==='ingredients' ? mainItem?.weight_g??massNumber(x?.main_weight_g) : ownWeight??massNumber(x?.main_weight_g)??mainItem?.weight_g)??null,
     main_volume_ml:massNumber(x?.main_volume_ml)??mainItem?.volume_ml??null,
     main_weight_basis:String((mode==='ingredients'&&mainItem?.weight_g?mainItem?.weight_basis:null)||x?.main_weight_basis||mainItem?.weight_basis||'').slice(0,180),
     weight_estimated:x?.weight_estimated!==false,
     additions,items};
 }).filter(x=>x.name||x.items.length):[];
 if(!dishes.length){const items=normItems(obj.items);if(items.length)dishes=[{name:String(obj.name||'Блюдо').slice(0,100),kind:'recipe',mode:'ingredients',weight_g:null,per100:null,main:items[0].name,main_portion:items[0].portion,main_weight_g:items[0].weight_g,main_volume_ml:items[0].volume_ml,main_weight_basis:items[0].weight_basis,additions:[],items}];}
 if(!dishes.length)throw Error('Нейросеть не выделила ни одного блюда');
 return {dishes,items:dishes.flatMap(x=>x.items),input_mode:['text','photo_food','photo_text'].includes(obj.input_mode)?obj.input_mode:'text',recognized_text:String(obj.recognized_text||'').slice(0,1000),consumed_description:String(obj.consumed_description||'').slice(0,500),uncertain:Array.isArray(obj.uncertain)?obj.uncertain.slice(0,10).map(x=>String(x).slice(0,160)):[]};
}
function missingAINutrition(data){
 const missing=[];
 for(let i=0;i<(data.dishes||[]).length;i++){
  const d=data.dishes[i];
  if(d.mode==='whole'){
   if(!isCompletePer100(d.per100)||!massNumber(d.weight_g??d.main_weight_g))missing.push({dish_index:i,mode:'whole',name:d.name,weight_g:d.weight_g??d.main_weight_g});
  }else{
   const all=[...(d.items||[]),...(d.additions||[])];
   if(!all.length)missing.push({dish_index:i,mode:'ingredients',name:d.name,missing:'ingredients'});
   for(const item of all){if(!isCompletePer100(item.per100)||!massNumber(item.weight_g))missing.push({dish_index:i,mode:'ingredients',name:item.name,weight_g:item.weight_g,per100:item.per100});}
  }
 }
 return missing;
}
async function retryMissingAINutrition(data,source,env,originalMessages){
 const missing=missingAINutrition(data);
 if(!missing.length)return {retried:false,missing:0};
 // Ask the SAME multimodal model to regenerate a complete answer from original
 // input, never filling nutritional values from the external directories.
 const suffix=' ПРЕДЫДУЩИЙ ОТВЕТ БЫЛ НЕПОЛНЫМ. Обязательно укажи для КАЖДОГО целого блюда или КАЖДОГО ингредиента weight_g и ЧЕТЫРЕ ЧИСЛА per100:{k,p,f,c} НА 100 ГРАММ. Не оставляй ни один продукт без КБЖУ. Ответ только JSON. Отсутствующие значения: '+JSON.stringify(missing).slice(0,1200);
 const corrected=originalMessages.map(message=>typeof message.content==='string'?{...message,content:message.content+suffix}:{...message,content:message.content.map(part=>part.type==='text'?{...part,text:part.text+suffix}:part)});
 try{
  const result=await env.AI.run(MODEL,{messages:corrected,chat_template_kwargs:{enable_thinking:false},response_format:{type:'json_object'},max_completion_tokens:4000,temperature:0});
  const rerun=parseFoodResponse(result).data;
  // Only accept a complete replacement which keeps all original dishes.
  const complete=missingAINutrition(rerun).length===0&&rerun.dishes.length>=data.dishes.length;
  if(complete){data.dishes=rerun.dishes;data.items=rerun.items;data.input_mode=rerun.input_mode;data.recognized_text=rerun.recognized_text;data.consumed_description=rerun.consumed_description;return {retried:true,repaired:true,missing:0};}
  return {retried:true,repaired:false,missing:missingAINutrition(rerun).length};
 }catch(e){return {retried:true,repaired:false,missing:missing.length,error:String(e?.message||e)};}
}

// Explicit enumeration coverage is a STRUCTURAL check, not a portion estimator.
// Splitting clauses never extracts grams or assigns weights: only the AI does that.
const COVERAGE_STOP=new Set('и или с со на по в во из для без к под при г гр кг мл л шт штука штуки штук порция порции порцию примерно около приблизительно два две один одна одно несколько каждый каждая каждое каждого каждом каждой каждые каждым каждой начинкой начинка начинку начинке чайной чайная чайную чайный ложкой ложки ложка ложечкой кусочком кусочек кусочками кусочка куском кусочек каждого всех'.split(' '));
// A dependent description after a comma specifies the contents of the SAME food,
// not another eaten serving. No quantities or food masses are derived from it.
const DEPENDENT_SOURCE=/^(?:(?:в|на|у|для)\s+)?кажд(?:ый|ая|ое|ом|ого|ой|ую|ые|ых|ыми)(?:\s|$)|^(?:с|со)\s+(?:начинк|наполнен|добавлен)|^(?:внутри|начинкой|фарширован|наполнен)(?:\s|$)/i;
function sourceClauses(text){
  if(!text || !text.trim())return [];
  const commaParts=String(text).replace(/\r/g,'').split(/,(?!\d)|;|\n+/).map(x=>x.trim()).filter(Boolean);
  const joined=[];
  let composed=false;
  for(const part of commaParts){
    if(joined.length && DEPENDENT_SOURCE.test(part)){
      joined[joined.length-1]+= ', '+part;
      composed=true;
    }else joined.push(part);
  }
  const clauses=[];
  for(const part of joined){
    // Do not split the conjunction inside a dependent filling description.
    const parts=DEPENDENT_SOURCE.test(part.split(',').slice(-1)[0]?.trim()||'')?[part]:part.split(/\s+и\s+/i).map(x=>x.trim()).filter(Boolean);
    // Independent explicitly quantified servings are separate. Do NOT read any
    // gram amounts here: all portion weights are AI output only.
    if(parts.length>1 && parts.length<=4 && parts.every(s=>/\d/.test(s) && /[а-яёa-z]/i.test(s))) clauses.push(...parts);
    else clauses.push(part);
  }
  return (clauses.length>1||composed)&&clauses.length<=8?clauses:[];
}
function coverageTokens(phrase){
  return [...new Set(String(phrase||'').toLowerCase().replaceAll('ё','е')
    .replace(/\d+(?:[.,]\d+)?/g,' ')
    .match(/[а-яa-z]+/g)?.filter(t=>t.length>=3 && !COVERAGE_STOP.has(t))
    .map(t=>t.length>=5?t.slice(0,4):t)||[])];
}
function uncoveredClauses(data,clauses){
  if(!clauses.length)return [];
  const composed=clauses.length===1 && clauses[0].includes(',') &&
    DEPENDENT_SOURCE.test(clauses[0].split(',').slice(-1)[0].trim());
  if(composed){
    // For one filled dish, validate all named food components against the AI's
    // actual ingredient list, not against the dish title alone.
    const needed=coverageTokens(clauses[0]);
    const dependent=clauses[0].split(',').slice(1).join(',');
    const minIngredients=/\s+и\s+/i.test(dependent)?3:2;
    const ok=(data.dishes||[]).length===1 && data.dishes.some(dish=>{
      const ingredients=[...(dish.items||[]),...(dish.additions||[])];
      if(dish.mode==='whole' && isCompletePer100(dish.per100)&&massNumber(dish.weight_g??dish.main_weight_g))return true;
      const distinct=new Set(ingredients.map(x=>coverageTokens(x.name).join('|')).filter(Boolean));
      if(distinct.size<minIngredients)return false;
      const present=coverageTokens(ingredients.map(x=>x.name).join(' '));
      return needed.every(t=>present.some(k=>k===t||k.startsWith(t)||t.startsWith(k)));
    });
    return ok?[]:[clauses[0]];
  }
  // Distinct, independently enumerated servings still require distinct dishes.
  const used=new Set();
  return clauses.filter(clause=>{
    const needed=coverageTokens(clause);
    if(!needed.length)return false;
    const matchedDish=data.dishes.findIndex((dish,index)=>{
      if(used.has(index))return false;
      const tokens=coverageTokens([dish.name,dish.main].join(' '));
      const matched=needed.filter(t=>tokens.some(k=>k===t || k.startsWith(t) || t.startsWith(k))).length;
      return matched>=Math.max(1,Math.ceil(needed.length*.7));
    });
    if(matchedDish<0)return true;
    used.add(matchedDish);
    return false;
  });
}
function sameFoodDish(a,b){
  const x=coverageTokens(a.main||a.name).join('|');
  const y=coverageTokens(b.main||b.name).join('|');
  return !!x&&x===y;
}
// Normalize a filled dish without inventing masses: the AI's own ingredient
// weight takes precedence over an inconsistent summary field.
function alignCompositeMainWeight(dish){
  if(dish.mode==='whole')return;
  dish.kind='recipe';
  const mainTokens=coverageTokens(dish.main);
  const ingredient=(dish.items||[]).find(x=>{
    const tokens=coverageTokens(x.name);
    return !!mainTokens.length&&mainTokens.every(t=>tokens.some(k=>t===k||t.startsWith(k)||k.startsWith(t)));
  });
  if(ingredient?.weight_g){
    dish.main_weight_g=ingredient.weight_g;
    dish.main_volume_ml=ingredient.volume_ml;
    dish.main_weight_basis=ingredient.weight_basis;
  }
}
async function recoverMissingDishes(data,source,env){
  const clauses=sourceClauses(source);
  // When Gemma merges several explicitly listed servings into one dish,
  // simply appending the omitted entries would double-count their macros.
  // In that case rebuild ALL independent entries from model results for
  // their original fragments, replacing (not supplementing) the wrong group.
  const grouped=clauses.length>1 && (data.dishes.length<clauses.length || data.dishes.some(d=>
    clauses.filter(fragment=>uncoveredClauses({dishes:[d]},[fragment]).length===0).length>1));
  const composed=clauses.length===1 && clauses[0].includes(',') && DEPENDENT_SOURCE.test(clauses[0].split(',').slice(-1)[0].trim());
  const initiallyMissing=grouped?[...clauses]:uncoveredClauses(data,clauses);
  const report={checked:clauses.length>0,fragments:clauses,grouping_repaired:grouped,composed,initial_missing:initiallyMissing,restored:[],final_missing:[],attempts:0};
  if(!initiallyMissing.length){
    if(composed && data.dishes.length===1)alignCompositeMainWeight(data.dishes[0]);
    return report;
  }
  const added=[];
  // A short, independent model call for each omitted source clause avoids the
  // common failure where Gemma's structured answer contains only its last item.
  // We never derive grams from regexes: the model returns all weights.
  const repairs=await Promise.all(initiallyMissing.map(async fragment=>{
    try{
      const instruction=PROMPT+(composed?' ВАЖНО: это ОДНО составное блюдо с начинкой; верни ОДИН dish kind:recipe, укажи отдельные items для основы и КАЖДОГО ингредиента начинки, общую массу каждого продукта на все штуки. НЕ создавай отдельные dishes для начинки.':' РАСПОЗНАЙ ТОЛЬКО СЛЕДУЮЩИЙ ФРАГМЕНТ исходного перечня продуктов; не добавляй другие части перечня.')+' ИСХОДНЫЙ ФРАГМЕНТ: '+JSON.stringify(fragment)+'; верни все упомянутые в нём продукты и их числовые веса.';
      const result=await env.AI.run(MODEL,{messages:[{role:'user',content:instruction}],chat_template_kwargs:{enable_thinking:false},response_format:{type:'json_object'},temperature:0,max_completion_tokens:1100});
      const fixed=parseFoodResponse(result).data;
      const matched=fixed.dishes.filter(d=>uncoveredClauses({dishes:[d]},[fragment]).length===0);
      if(!matched.length)throw Error('ИИ повторно пропустил продукт');
      // Source clauses contain independent servings. The AI chooses the
      // main component and weight, not the JavaScript code.
      if(composed)alignCompositeMainWeight(matched[0]);
      return {fragment,dishes:matched.slice(0,1)};
    }catch(e){return {fragment,error:String(e?.message||e)}}
  }));
  report.attempts=repairs.length;
  for(const repair of repairs){
    if(repair.error)continue;
    for(const d of repair.dishes){
      if(!added.some(existing=>sameFoodDish(existing,d)) && (grouped || composed || !data.dishes.some(existing=>sameFoodDish(existing,d)))){
        added.push(d);
        if(!grouped && !composed)data.dishes.push(d);
      }
    }
    report.restored.push(repair.fragment);
  }
  if(grouped||composed)data.dishes=added;
  data.items=data.dishes.flatMap(x=>x.items);
  report.final_missing=uncoveredClauses(data,clauses);
  return report;
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
  const instruction='ДОПОЛНИ ОТСУТСТВУЮЩИЕ ЧИСЛОВЫЕ ВЕСА ДЛЯ ДНЕВНИКА ПИТАНИЯ. Верни только JSON {"portions":[{"dish_index":0,"item_index":0,"weight_g":110,"volume_ml":null,"weight_estimated":true,"weight_basis":"2 яйца"}]}. Индексы должны СОВПАДАТЬ с данными ниже. Если добавка — addition_index; если основной продукт без item — main:true. Чётко написанные граммы НЕ переоценивай: «20 г» -> weight_g:20, weight_estimated:false; «10 г» -> weight_g:10, weight_estimated:false. «2 яйца» или «бокал пива» — оцени САМ, weight_estimated:true. Никакого определения веса по таблицам, никакого дефолта 100 г; если невозможно — null. Только JSON. Оригинальная фраза: '+originalText.slice(0,400)+'; недостающие поля: '+JSON.stringify(missing);
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
   if(record.main){dish.main_weight_g=mass;dish.main_volume_ml=massNumber(piece.volume_ml);dish.main_weight_basis=String(piece.weight_basis||'Ответ ИИ').slice(0,180);}
   else{target.weight_g=mass;target.volume_ml=massNumber(piece.volume_ml);target.weight_basis=String(piece.weight_basis||'Ответ ИИ').slice(0,180);target.weight_estimated=piece.weight_estimated!==false;}
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
    if(url.pathname==='/health' && request.method==='GET') return asJson({ok:true, ai_binding:!!env.AI, model:MODEL, version:"2.1"});
    if(url.pathname!=='/analyze' || request.method!=='POST') return asJson({error:'Not found'},404);
    if(!env.AI) return asJson({error:'Не добавлен Workers AI binding с именем AI'},500);
    const type=request.headers.get('content-type')||'';
    if(!type.toLowerCase().includes('multipart/form-data')) return asJson({error:'Нужен multipart/form-data'},415);
    const length=Number(request.headers.get('content-length')||0);
    if(length>3_000_000) return asJson({error:'Слишком большой запрос (лимит ~2 МБ для фотографии)'},413);
    try {
      const form=await request.formData();
      const text=String(form.get('text')||'').trim().slice(0,500);
      const photo=form.get('photo');
      const messages=[];
      if(photo && typeof photo==='object' && photo.size) {
        if(photo.size>2_000_000) return asJson({error:'Фото больше 2 МБ. Уменьшите изображение.'},413);
        const mime=photo.type.toLowerCase();
        if(!['image/jpeg','image/png','image/webp'].includes(mime)) return asJson({error:'Нужен JPEG, PNG или WebP'},415);
        const bytes=new Uint8Array(await photo.arrayBuffer());
        messages.push({role:'user',content:[
          {type:'text',text:PROMPT+(text?' Дополнительная информация пользователя: '+text:'')},
          {type:'image_url',image_url:{url:`data:${mime};base64,${toBase64(bytes)}`}}
        ]});
      } else {
        if(!text) return asJson({error:'Добавьте фото или текст'},400);
        const fragments=sourceClauses(text);
        const directive=fragments.length?' ОБЯЗАТЕЛЬНО отрази ВСЕ '+fragments.length+' явно перечисленных части исходной фразы: '+JSON.stringify(fragments)+'; используй составной dish для ингредиентов одного блюда.':'';
        messages.push({role:'user',content:PROMPT+directive+' Пользователь написал: '+text});
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
        max_completion_tokens:3500,
        temperature:0
      });
      let data,recovered=false,firstError='';
      try {({data}=parseFoodResponse(result));}
      catch(err){
        firstError=String(err?.message||err);
        const corrected=messages.map(message=>{
          const suffix=' ВАЖНО: ответ должен быть ОДНИМ завершённым JSON-объектом, без второго объекта и без пояснений. Каждый продукт со своей массой weight_g и main_weight_g. Если граммы названы явно, строго перепиши их в числовое поле.';
          if(typeof message.content==='string')return {...message,content:message.content+suffix};
          return {...message,content:message.content.map(part=>part.type==='text'?{...part,text:part.text+suffix}:part)};
        });
        result=await env.AI.run(MODEL,{
          messages:corrected,chat_template_kwargs:{enable_thinking:false},
          response_format:{type:'json_object'},max_completion_tokens:4000,temperature:0
        });
        ({data}=parseFoodResponse(result));
        recovered=true;
      }
      // Photo text is a two-stage AI task. The vision model first reads the
      // writing; then a TEXT model reads that exact OCR output and uses its
      // stated weights and per-100g label values. No JS extraction of grams,
      // OCR or portion inference is performed here.
      let ocr_text_retry={retried:false,used:false};
      if(photo && photo.size && data.input_mode==='photo_text' && data.recognized_text?.trim()){
        try{
          const ocrText=data.recognized_text.slice(0,1000);
          const correction='Это задача извлечения ТОЧНЫХ чисел с текстовой фотографии, а не угадывания продуктов. Отвечай только одним JSON по схеме в инструкции. Если в тексте написано «Творог, 150 г» — weight_g ОБЯЗАТЕЛЬНО 150, не 200. Если на этикетке указано «КБЖУ на 100 г: 120 ккал; Б 17 г; Ж 5 г; У 2 г» — per100 ОБЯЗАТЕЛЬНО {"k":120,"p":17,"f":5,"c":2}; не заменяй этикетку приблизительными знаниями. Для любых продуктов точно сохраняй написанные граммы и значения на 100 г. Ничего не выдумывай, не применяй стандартных порций там, где есть явное число. input_mode:"photo_text"; recognized_text: перепиши оригинал. Вот ПОЛНЫЙ ТЕКСТ, распознанный с фотографии: '+JSON.stringify(ocrText);
          const refined=await env.AI.run(MODEL,{messages:[{role:'user',content:PROMPT+'\n'+correction}],chat_template_kwargs:{enable_thinking:false},response_format:{type:'json_object'},max_completion_tokens:2800,temperature:0});
          const improved=parseFoodResponse(refined).data;
          if(improved.dishes.length){
            improved.input_mode='photo_text';improved.recognized_text=ocrText;
            improved.consumed_description=improved.consumed_description||data.consumed_description;
            data=improved;ocr_text_retry={retried:true,used:true};
          }
        }catch(e){ocr_text_retry={retried:true,used:false,error:String(e?.message||e)};}
      }
      // Do not accept a syntactically valid but incomplete model answer.
      const sourceForCoverage=(photo && photo.size)?(data.input_mode==='photo_text'?data.consumed_description:''):text;
      const coverage=sourceForCoverage?await recoverMissingDishes(data,sourceForCoverage,env):{checked:false,fragments:[],initial_missing:[],restored:[],final_missing:[],attempts:0};
      if(coverage.final_missing.length){
        return asJson({ok:false,stage:'coverage',message:'ИИ распознал не все перечисленные продукты. Данные не сохранены; повторите расчёт.',coverage},422);
      }
      const portion_retry=await retryMissingMasses(data,sourceForCoverage||text,env);
      const nutrition_retry=await retryMissingAINutrition(data,sourceForCoverage||text,env,messages);
      const missingNutrition=missingAINutrition(data);
      if(missingNutrition.length) return asJson({ok:false,stage:'nutrition',message:'ИИ не указал вес и КБЖУ на 100 г для всех продуктов. Сохранён исходный ввод; повторите расчёт.',missing:missingNutrition,nutrition_retry},422);
      return asJson({ok:true,model:MODEL,food:data,coverage,portion_retry,nutrition_retry,
        json_recovery:{retried:recovered,first_error:recovered?firstError:null},ocr_text_retry,usage:{
        neurons:result?.usage?.neurons ?? null,
        input_tokens:result?.usage?.prompt_tokens ?? null,
        output_tokens:result?.usage?.completion_tokens ?? null
      }});
    } catch(error) {
      return asJson({ok:false,stage:'inference',message:String(error?.message||error)},502);
    }
  }
};



// v1.4 — nutrition lookup. OFF is primarily for packaged foods;
// USDA FoodData Central complements it for generic ingredients and prepared dishes.
// Neither provider guarantees a suitable match. The UI shows candidates and source.
// Documented standard food: USDA FDC 173423 (Egg, whole, cooked, fried), per 100g.
const VERIFIED_PREPARED_FOODS=[{test:/яичниц|глазун|жарен.*яйц|яйц.*жарен|fried egg/i, row:{name:'Egg, whole, cooked, fried',name_ru:'Яичница-глазунья',k:196,p:13.61,f:14.84,c:0.83,source:'USDA FoodData Central',fdcId:173423,match_score:160}}];
const NUT_CACHE=new Map();
const FOOD_ENGLISH={
 'пиво нефильтрованное':'unfiltered beer', 'пиво фильтрованное':'filtered beer', 'нефильтрованного пива':'unfiltered beer', 'фильтрованного пива':'filtered beer', 'пиво':'beer',
 'медовик':'honey layer cake','наполеон':'napoleon pastry','сырный соус':'cheese sauce','соус сырный':'cheese sauce',
 'бисквит':'sponge cake','взбитые сливки':'whipped cream','шоколадный соус':'chocolate syrup','дробленые орехи':'mixed nuts',
 'торт':'cake','булочка':'hamburger bun','говяжья котлета':'beef patty','помидор':'tomato','томат':'tomato',
 'айсберг':'iceberg lettuce','салат латук':'lettuce','сыр':'cheese','яйцо':'egg','яйца':'egg',
 'молоко':'milk','гречка':'buckwheat cooked','рис':'rice cooked','творог':'cottage cheese',
 'курица':'chicken cooked','куриная грудка':'chicken breast cooked','говядина':'beef cooked',
 'картофель':'potato cooked','картошка':'potato','фри':'french fries','масло сливочное':'butter',
 'масло':'oil','морковь':'carrot','свекла':'beet','яблоко':'apple','банан':'banana',
 'макароны':'pasta cooked','йогурт':'yogurt','орехи':'mixed nuts','лосось':'salmon',
 'треска':'cod','суп':'soup','борщ':'beet soup','круассан':'croissant',
 'хлеб':'bread','шоколад':'chocolate','сметана':'sour cream','майонез':'mayonnaise',
 'сахар':'sugar','печенье':'cookies','овсяная каша':'oatmeal','пельмени':'dumplings','бекон':'bacon','бекона':'bacon','ветчина':'ham','грудинка':'bacon','черри':'cherry tomatoes','руккола':'arugula','шпинат':'spinach','сало':'pork fat','семечки':'seeds'
};
function englishTerm(q){const s=q.toLowerCase().replaceAll('ё','е');const key=Object.keys(FOOD_ENGLISH).sort((a,b)=>b.length-a.length).find(k=>s.includes(k));return key?FOOD_ENGLISH[key]:q}
async function translateNutritionQuery(q,env){
 const s=englishTerm(q);if(s!==q||!/[А-Яа-яЁё]/.test(q)||!env.AI)return s;
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
  if(!response.ok){const fragment=(await response.text()).slice(0,160).replace(/\s+/g,' ');return {items:[],ok:false,diagnostic:`${label}: HTTP ${response.status}; ${fragment}; ${Date.now()-started} мс`}}
  if(!type.includes('json') && !(label==='CoFID (UK)' && /^(text\/plain|application\/octet-stream)/i.test(type))){const fragment=(await response.text()).slice(0,120);return {items:[],ok:false,diagnostic:`${label}: не JSON (${type}); ${fragment}`}}
  return {json:await response.json(),items:[],ok:true,diagnostic:`${label}: HTTP 200; ${Date.now()-started} мс`};
 }catch(e){return {items:[],ok:false,diagnostic:`${label}: ${e?.name||'Error'} ${e?.message||String(e)}; ${Date.now()-started} мс`}}
 finally{clearTimeout(t)}
}
// One batched translation per cache miss. Keep the original USDA description alongside Russian.
async function addRussianNames(items,env,translateWithAI=true){
 const usda=items.filter(x=>x.source!=='Open Food Facts'&&!x.name_ru);
 if(!usda.length)return;
 const known={CAKE:'Торт', 'SPONGE CAKE':'Бисквит', 'WHIPPED CREAM':'Взбитые сливки', YOGURT:'Йогурт',MILK:'Молоко',EGG:'Яйцо',EGGS:'Яйца',CHEESE:'Сыр',TOMATO:'Помидор',TOMATOES:'Помидоры',CHICKEN:'Курица',BREAD:'Хлеб',POTATO:'Картофель',BUTTER:'Сливочное масло',APPLE:'Яблоко',BANANA:'Банан'};
 for(const x of usda){const t=x.name.toUpperCase().trim();if(known[t])x.name_ru=known[t]}
 if(!env.AI||!translateWithAI)return;
 try{
  const raw=await env.AI.run(MODEL,{
    messages:[{role:'user',content:'Переведи на русский названия пищевых продуктов. Не меняй состав, способ приготовления, виды продуктов или бренды. Верни ТОЛЬКО JSON-массив ровно из '+usda.length+' русских строк в том же порядке, без объяснений. Названия: '+JSON.stringify(usda.map(x=>x.name))}],
    chat_template_kwargs:{enable_thinking:false},temperature:0,max_completion_tokens:750
  });
  let txt=raw?.choices?.[0]?.message?.content??raw?.response??'';
  if(Array.isArray(txt))txt=txt.map(v=>v?.text||'').join('');
  txt=String(txt).replace(/^```(?:json)?\s*/i,'').replace(/\s*```$/,'').trim();
  const begin=txt.indexOf('['),end=txt.lastIndexOf(']');
  const arr=JSON.parse(txt.slice(begin,end+1));
  if(Array.isArray(arr)&&arr.length===usda.length){arr.forEach((str,i)=>{if(typeof str==='string'&&str.trim().length>=2&&/[А-Яа-яЁё]/.test(str))usda[i].name_ru=str.slice(0,120).trim()})}
 }catch(_){/* Name lookup must succeed even if translation inference fails. */}
}

// v1.12: Additional independent nutrition providers. Their publicly published
// datasets are retrieved server-side and cached in a Worker isolate; failures
// are isolated and never invalidate the other databases. CoFID is the UK
// government OGL-licensed static extract published by Scranbook (no API key).
const EXTRA_INDEX_CACHE = new Map();
async function extraIndex(key,url,selector){
 const cached=EXTRA_INDEX_CACHE.get(key);
 if(cached&&cached.until>Date.now())return {items:cached.items,diagnostic:key+': кэш индекса '+cached.items.length};
 if(cached?.pending)return cached.pending;
 const pending=(async()=>{
  const resp=await sourceJson(url,{headers:{'Accept':'application/json'}},key);
  if(!resp.ok)return {items:[],diagnostic:resp.diagnostic};
  const items=selector(resp.json);
  if(!Array.isArray(items)||!items.length)return {items:[],diagnostic:key+': неизвестный формат ответа'};
  EXTRA_INDEX_CACHE.set(key,{items,until:Date.now()+24*3600*1000});
  return {items,diagnostic:key+': индекс '+items.length+'; '+resp.diagnostic};
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
 const found=extraBest(candidates,en,4).map(({x,score})=>extraFood(x.name,x.energyKcal,x.proteinG,x.fatG,x.carbsG,'CoFID (Великобритания)',{source_id:x.id,match_score:score})).filter(Boolean);
 return {ok:!!index.items.length,items:found,diagnostic:index.diagnostic+'; совпадений '+found.length};
}
async function searchNorway(en){
 const key='Matvaretabellen (Norway)';const index=await extraIndex(key,'https://www.matvaretabellen.no/api/en/foods.json',j=>Array.isArray(j)?j:Array.isArray(j.foods)?j.foods:[]);
 const found=extraBest(index.items,en,4).map(({x,score})=>{
  const n=x.constituents||{};
  // Norwegian source uses these identifiers for total fat, available carbohydrates and protein.
  const constituent=id=>n[id]??(Array.isArray(n)?n.find(v=>v.nutrientId===id):undefined);
  return extraFood(x.foodName||x.name,x.energyKcal??x.energy?.kcal,constituent('Protein'),constituent('Fett'),constituent('Karbo'),'Matvaretabellen (Норвегия)',{source_id:x.id,match_score:score});
 }).filter(Boolean);
 return {ok:!!index.items.length,items:found,diagnostic:index.diagnostic+'; совпадений '+found.length};
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
  return extraFood(x.name,nutrient([208,268],['energy (kcal)','energy, kcal','energy (kilocalories)']),nutrient([203],['protein']),nutrient([204],['fat, total lipid','total fat']),nutrient([205],['carbohydrate, by difference','carbohydrate, total']),'Canadian Nutrient File (Канада)',{source_id:x.food_code,match_score:score});
 }));
 const found=details.filter(Boolean);
 return {ok:!!index.items.length,items:found,diagnostic:index.diagnostic+'; совпадений '+found.length};
}
async function tryExtra(fn,label,en){try{return await fn(en)}catch(e){return {ok:false,items:[],diagnostic:label+': '+String(e?.message||e)}}}

async function searchNutrition(query,env,{fast=false}={}){
 const q=String(query||'').trim().slice(0,100);if(q.length<2)return {ok:false,error:'Запрос слишком короткий',items:[],diagnostics:[]};
 const trusted=VERIFIED_PREPARED_FOODS.find(x=>x.test.test(q));if(trusted)return {ok:true,items:[{...trusted.row}],diagnostics:['Проверенная стандартная запись USDA'],query:q,sources:{usda:true}};
 const key=q.toLowerCase();const cached=NUT_CACHE.get(key);if(cached&&cached.until>Date.now())return {...cached.value,diagnostics:['Кеш поиска (до 20 минут)',...(cached.value.diagnostics||[])]};
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
 // Public APIs can be rate-limited (USDA DEMO_KEY -> 429) or temporarily
 // unavailable (OFF -> 503). Supplement missing genuine liver data with a
 // published food label. A bottle of cod-liver OIL is never cod LIVER.
 // This is an approximate canned-food analogue, NOT an inferred serving size.
 const codLiverRequest=/(?:печен[ьи]\s+треск|тресков(?:ая|ой|ую|ой)\s+печен|\bcod liver\b)/i.test(q+' '+en);
 const isOilQuery=/(?:\b(?:cod liver oil|fish oil)\b|масло\s+печен|жир\s+печен|рыбий\s+жир)/i.test(q+' '+en);
 if(codLiverRequest&&!isOilQuery){
  const actual=raw.some(x=>/(?:\bcod liver\b|печен[ьи]\s+треск)/i.test(x.name+' '+String(x.name_ru||''))&&
       !/\b(?:oil|pate|capsules?|supplement|extract|powder)\b|масло\s+печен/i.test(x.name+' '+String(x.name_ru||'')));
  if(!actual){
   const rawRequested=/(?:сырая|сырой|\braw\b)/i.test(q+' '+en);
   raw.push(rawRequested?
    {name:'Cod liver, raw',name_ru:'Печень трески сырая',k:553,p:5.5,f:59,c:0,
     source:'Matvaretabellen (Норвегия) · сохранённая справочная запись',
     reference_url:'https://matvaretabellen.mattilsynet.io/en/cod-liver-raw/',reference_fallback:true,approximate:true}:
    {name:'Cod liver, canned in natural fat',name_ru:'Печень трески',k:525,p:6,f:55.46,c:0,
     source:'Этикетка JUOR · приблизительный аналог консервированной печени трески',
     reference_url:'https://en.juor.pl/the-offering/cod-liver-in-natural-fat-2/',reference_fallback:true,approximate:true});
  }
 }

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
     else if(item.source==='CoFID (Великобритания)'||/Foundation|SR Legacy|FNDDS/i.test(item.dataType||''))sc+=18;
     if(!item.brand && n.startsWith(en.toLowerCase()+','))sc+=27;
     if(/pretzel|raisin|almond|peanut|coated|flavored|dessert/.test(n) && !/pretzel|raisin|almond|peanut|dessert/.test(en.toLowerCase()))sc-=28;
     return sc;};
   raw.forEach(x=>x.match_score=x.reference_fallback?125:score(x));raw.sort((x,y)=>y.match_score-x.match_score);
   const seen=new Set(),sourceCounts=new Map(),items=[];for(const item of raw){if(item.match_score< -10)continue;const id=item.source+':'+(item.code||item.fdcId||item.source_id||item.name);if(seen.has(id)||(sourceCounts.get(item.source)||0)>=3)continue;seen.add(id);sourceCounts.set(item.source,(sourceCounts.get(item.source)||0)+1);items.push(item);if(items.length>=18)break}
 await addRussianNames(items,env,!fast);
 const result={ok:a.ok||b.ok||sw.ok||cofid.ok||norway.ok||canada.ok||items.some(x=>x.reference_fallback),english_query:en,items,diagnostics:[a.diagnostic,b.diagnostic,sw.diagnostic,cofid.diagnostic,norway.diagnostic,canada.diagnostic],query:q,sources:{off:a.ok,usda:b.ok,sweden:sw.ok,cofid:cofid.ok,norway:norway.ok,canada:canada.ok}};
 if(items.some(x=>x.reference_fallback))result.diagnostics.push('Резерв: опубликованная пищевая ценность продукта; КБЖУ ориентировочные, вес берётся только от ИИ.');
 if(!result.ok)result.error='Источники недоступны — см. diagnostics';
 // Empty/failed searches must be retried soon when providers recover; valid hits can be cached longer.
 NUT_CACHE.set(key,{until:Date.now()+(items.some(x=>x.reference_fallback)?5*60*1000:items.length?60*60*1000:45*1000),value:result});if(NUT_CACHE.size>100)NUT_CACHE.delete(NUT_CACHE.keys().next().value);
 return result;
}

// A small, server-side snapshot parsed from the user's official-format PDF dated 2026-05-25.
// Actual official site may publish a newer revision: never misrepresent this snapshot as live.
const CHAIN_PDF_DATE='2026-05-25';
const CHAIN_OFFICIAL_PDF='https://vkusnoitochka.ru/sostav.pdf';
const CHAIN_ROWS=[{"name":"Чизбургер","base_name":"Чизбургер","w":109.0,"k":291.0,"p":14.0,"f":11.0,"c":33.0,"page":1,"portion":""},{"name":"Двойной Чизбургер","base_name":"Двойной Чизбургер","w":158.0,"k":416.0,"p":24.0,"f":21.0,"c":34.0,"page":1,"portion":""},{"name":"Гамбургер","base_name":"Гамбургер","w":97.0,"k":252.0,"p":12.0,"f":8.2,"c":33.0,"page":1,"portion":""},{"name":"Фиш Бургер","base_name":"Фиш Бургер","w":133.0,"k":331.0,"p":15.0,"f":14.0,"c":36.0,"page":1,"portion":""},{"name":"Двойной Фиш Бургер","base_name":"Двойной Фиш Бургер","w":196.0,"k":475.0,"p":26.0,"f":21.0,"c":45.0,"page":2,"portion":""},{"name":"Чикенбургер","base_name":"Чикенбургер","w":129.0,"k":337.0,"p":12.0,"f":16.0,"c":37.0,"page":2,"portion":""},{"name":"Гранд","base_name":"Гранд","w":202.0,"k":514.0,"p":30.0,"f":26.0,"c":38.0,"page":2,"portion":""},{"name":"Двойной Гранд","base_name":"Двойной Гранд","w":282.0,"k":732.0,"p":49.0,"f":42.0,"c":38.0,"page":2,"portion":""},{"name":"Гранд Де Люкс","base_name":"Гранд Де Люкс","w":251.0,"k":570.0,"p":31.0,"f":31.0,"c":40.0,"page":2,"portion":""},{"name":"Чикен Премьер","base_name":"Чикен Премьер","w":234.0,"k":525.0,"p":26.0,"f":24.0,"c":51.0,"page":2,"portion":""},{"name":"Биг Спешиал","base_name":"Биг Спешиал","w":340.0,"k":800.0,"p":43.0,"f":47.0,"c":49.0,"page":3,"portion":""},{"name":"Двойной Биг Спешиал","base_name":"Двойной Биг Спешиал","w":450.0,"k":1098.0,"p":70.0,"f":69.0,"c":49.0,"page":3,"portion":""},{"name":"Биг Спешиал Джуниор","base_name":"Биг Спешиал Джуниор","w":231.0,"k":573.0,"p":31.0,"f":33.0,"c":36.0,"page":3,"portion":""},{"name":"Чикен Хит","base_name":"Чикен Хит","w":198.0,"k":484.0,"p":21.0,"f":22.0,"c":49.0,"page":3,"portion":""},{"name":"Биг Хит","base_name":"Биг Хит","w":228.0,"k":524.0,"p":27.0,"f":28.0,"c":40.0,"page":3,"portion":""},{"name":"Двойной Биг Хит","base_name":"Двойной Биг Хит","w":303.0,"k":711.0,"p":43.0,"f":41.0,"c":41.0,"page":3,"portion":""},{"name":"Биг Чикен Бургер","base_name":"Биг Чикен Бургер","w":323.0,"k":700.0,"p":44.0,"f":35.0,"c":51.0,"page":3,"portion":""},{"name":"Биг Спешиал Перец гриль","base_name":"Биг Спешиал Перец гриль","w":376.0,"k":751.0,"p":43.0,"f":38.0,"c":59.0,"page":4,"portion":""},{"name":"Тройной Фреш","base_name":"Тройной Фреш","w":232.0,"k":577.0,"p":33.0,"f":34.0,"c":35.0,"page":4,"portion":""},{"name":"Цезарь Ролл","base_name":"Цезарь Ролл","w":211.0,"k":472.0,"p":19.0,"f":22.0,"c":48.0,"page":4,"portion":""},{"name":"Биг Спешиал Ролл","base_name":"Биг Спешиал Ролл","w":241.0,"k":525.0,"p":27.0,"f":30.0,"c":36.0,"page":4,"portion":""},{"name":"Шримп Ролл","base_name":"Шримп Ролл","w":164.0,"k":411.0,"p":15.0,"f":17.0,"c":49.0,"page":4,"portion":""},{"name":"Биг Спешиал ролл Перец гриль","base_name":"Биг Спешиал ролл Перец гриль","w":295.0,"k":556.0,"p":27.0,"f":29.0,"c":47.0,"page":4,"portion":""},{"name":"Чикен Премьер Перец гриль","base_name":"Чикен Премьер Перец гриль","w":255.0,"k":516.0,"p":21.0,"f":22.0,"c":59.0,"page":5,"portion":""},{"name":"Биг Чикен Бургер Перец гриль","base_name":"Биг Чикен Бургер Перец гриль","w":374.0,"k":703.0,"p":39.0,"f":39.0,"c":70.0,"page":5,"portion":""},{"name":"Панини Тоскана","base_name":"Панини Тоскана","w":273.0,"k":636.0,"p":29.0,"f":32.0,"c":58.0,"page":5,"portion":""},{"name":"Панини Тоскана острый","base_name":"Панини Тоскана острый","w":279.0,"k":638.0,"p":29.0,"f":32.0,"c":59.0,"page":5,"portion":""},{"name":"Тройной Чизбургер Три Сыра","base_name":"Тройной Чизбургер Три Сыра","w":202.0,"k":538.0,"p":34.0,"f":29.0,"c":34.0,"page":5,"portion":""},{"name":"Биг Чикен Бургер Базиликовый","base_name":"Биг Чикен Бургер Базиликовый","w":320.0,"k":750.0,"p":39.0,"f":40.0,"c":59.0,"page":5,"portion":""},{"name":"Наггетсы (4 шт)","base_name":"Наггетсы","w":72.0,"k":179.0,"p":11.0,"f":9.1,"c":12.0,"page":6,"portion":"4 шт"},{"name":"Наггетсы (6 шт)","base_name":"Наггетсы","w":108.0,"k":268.0,"p":17.0,"f":14.0,"c":19.0,"page":6,"portion":"6 шт"},{"name":"Наггетсы (9 шт)","base_name":"Наггетсы","w":162.0,"k":402.0,"p":25.0,"f":21.0,"c":28.0,"page":6,"portion":"9 шт"},{"name":"Наггетсы (18 шт)","base_name":"Наггетсы","w":324,"k":804.0,"p":50.0,"f":42.0,"c":56.0,"page":6,"portion":"18 шт"},{"name":"Изделия кулинарные креветки жареные (4 шт)","base_name":"Изделия кулинарные креветки жареные","w":72.0,"k":180.0,"p":9.9,"f":9.0,"c":15.0,"page":6,"portion":"4 шт"},{"name":"Изделия кулинарные креветки жареные (6 шт)","base_name":"Изделия кулинарные креветки жареные","w":108.0,"k":271.0,"p":15.0,"f":14.0,"c":22.0,"page":6,"portion":"6 шт"},{"name":"Изделия кулинарные креветки жареные (9 шт)","base_name":"Изделия кулинарные креветки жареные","w":162.0,"k":406.0,"p":22.0,"f":20.0,"c":34.0,"page":6,"portion":"9 шт"},{"name":"Изделия кулинарные креветки жареные (18 шт)","base_name":"Изделия кулинарные креветки жареные","w":324.0,"k":812.0,"p":44.0,"f":40.0,"c":68.0,"page":6,"portion":"18 шт"},{"name":"Куриные крылышки (5 шт)","base_name":"Куриные крылышки","w":125.0,"k":350.0,"p":21.25,"f":22.5,"c":15.0,"page":6,"portion":"5 шт"},{"name":"Куриные Стрипсы (3 шт)","base_name":"Куриные Стрипсы","w":99.0,"k":223.0,"p":14.0,"f":10.0,"c":19.0,"page":6,"portion":"3 шт"},{"name":"Куриные Стрипсы (5 шт)","base_name":"Куриные Стрипсы","w":165.0,"k":371.0,"p":23.0,"f":17.0,"c":31.0,"page":6,"portion":"5 шт"},{"name":"Куриные Стрипсы (7 шт)","base_name":"Куриные Стрипсы","w":231.0,"k":520.0,"p":32.0,"f":24.0,"c":44.0,"page":6,"portion":"7 шт"},{"name":"Снэк Бокс","base_name":"Снэк Бокс","w":196.0,"k":500.0,"p":20.0,"f":24.0,"c":49.0,"page":6,"portion":""},{"name":"Средний Бокс","base_name":"Средний Бокс","w":152.0,"k":319.2,"p":22.8,"f":19.76,"c":24.32,"page":6,"portion":""},{"name":"Большой Бокс","base_name":"Большой Бокс","w":304.0,"k":638.4,"p":45.6,"f":39.52,"c":48.64,"page":7,"portion":""},{"name":"Мега Бокс","base_name":"Мега Бокс","w":608.0,"k":1276.8,"p":91.2,"f":79.04,"c":97.28,"page":7,"portion":""},{"name":"Картофель Фри (маленькая)","base_name":"Картофель Фри","w":76.0,"k":220.0,"p":2.6,"f":10.0,"c":28.0,"page":7,"portion":"маленькая"},{"name":"Картофель Фри (средняя)","base_name":"Картофель Фри","w":110.0,"k":318.0,"p":3.7,"f":15.0,"c":40.0,"page":7,"portion":"средняя"},{"name":"Картофель Фри (большая)","base_name":"Картофель Фри","w":147.0,"k":425.0,"p":5.0,"f":20.0,"c":53.0,"page":7,"portion":"большая"},{"name":"Картофель по-деревенски (средняя)","base_name":"Картофель по-деревенски","w":165.0,"k":331.0,"p":4.6,"f":15.0,"c":42.0,"page":7,"portion":"средняя"},{"name":"Картофель по-деревенски (большая)","base_name":"Картофель по-деревенски","w":220,"k":441.0,"p":6.2,"f":20.0,"c":57.0,"page":7,"portion":"большая"},{"name":"Картофель Фри Двойной","base_name":"Картофель Фри Двойной","w":220.0,"k":636.0,"p":7.5,"f":30.0,"c":80.0,"page":7,"portion":""},{"name":"Картофель по-деревенски Двойной","base_name":"Картофель по-деревенски Двойной","w":330.0,"k":766.0,"p":9.2,"f":38.0,"c":97.0,"page":7,"portion":""},{"name":"Салат Овощной","base_name":"Салат Овощной","w":96.0,"k":31.0,"p":0.8,"f":2.0,"c":1.8,"page":8,"portion":""},{"name":"Салат Цезарь","base_name":"Салат Цезарь","w":156.0,"k":199.0,"p":13.0,"f":9.7,"c":14.0,"page":8,"portion":""},{"name":"Салат Цезарь с креветками","base_name":"Салат Цезарь с креветками","w":146.0,"k":186.0,"p":11.0,"f":9.7,"c":13.0,"page":8,"portion":""},{"name":"Картофель с сыром и беконом","base_name":"Картофель с сыром и беконом","w":151.0,"k":634.2,"p":15.1,"f":34.73,"c":60.4,"page":8,"portion":""},{"name":"Картофель по-деревенски с сыром и беконом","base_name":"Картофель по-деревенски с сыром и беконом","w":206.0,"k":891.98,"p":22.66,"f":47.38,"c":88.58,"page":8,"portion":""},{"name":"Картофель с сыром","base_name":"Картофель с сыром","w":140.0,"k":513.8,"p":9.66,"f":26.6,"c":56.0,"page":8,"portion":""},{"name":"Картофель по-деревенски с сыром","base_name":"Картофель по-деревенски с сыром","w":195.0,"k":741.0,"p":15.21,"f":37.05,"c":83.85,"page":8,"portion":""},{"name":"Чай Липтон лимонный (маленькая)","base_name":"Чай Липтон лимонный","w":250.0,"k":67.0,"p":0.0,"f":0.0,"c":17.0,"page":9,"portion":"маленькая"},{"name":"Чай Липтон лимонный (средняя)","base_name":"Чай Липтон лимонный","w":400.0,"k":107.0,"p":0.0,"f":0.0,"c":27.0,"page":9,"portion":"средняя"},{"name":"Чай Липтон лимонный (большая)","base_name":"Чай Липтон лимонный","w":500.0,"k":134.0,"p":0.0,"f":0.0,"c":34.0,"page":9,"portion":"большая"},{"name":"Чай Липтон зеленый (маленькая)","base_name":"Чай Липтон зеленый","w":250.0,"k":67.0,"p":0.0,"f":0.0,"c":17.0,"page":9,"portion":"маленькая"},{"name":"Чай Липтон зеленый (средняя)","base_name":"Чай Липтон зеленый","w":400.0,"k":107.0,"p":0.0,"f":0.0,"c":27.0,"page":9,"portion":"средняя"},{"name":"Чай Липтон зеленый (большая)","base_name":"Чай Липтон зеленый","w":500.0,"k":134.0,"p":0.0,"f":0.0,"c":34.0,"page":9,"portion":"большая"},{"name":"Добрый Кола (маленькая)","base_name":"Добрый Кола","w":250.0,"k":106.0,"p":0.0,"f":0.0,"c":27.0,"page":9,"portion":"маленькая"},{"name":"Добрый Кола (средняя)","base_name":"Добрый Кола","w":400.0,"k":170.0,"p":0.0,"f":0.0,"c":42.0,"page":9,"portion":"средняя"},{"name":"Добрый Кола (большая)","base_name":"Добрый Кола","w":500.0,"k":212.0,"p":0.0,"f":0.0,"c":53.0,"page":9,"portion":"большая"},{"name":"Добрый Апельсин (маленькая)","base_name":"Добрый Апельсин","w":250.0,"k":48.0,"p":0.0,"f":0.0,"c":12.0,"page":9,"portion":"маленькая"},{"name":"Добрый Апельсин (средняя)","base_name":"Добрый Апельсин","w":400.0,"k":76.0,"p":0.0,"f":0.0,"c":18.0,"page":9,"portion":"средняя"},{"name":"Добрый Апельсин (большая)","base_name":"Добрый Апельсин","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":9,"portion":"большая"},{"name":"Добрый Лимон-Лайм (маленькая)","base_name":"Добрый Лимон-Лайм","w":250.0,"k":47.5,"p":0.0,"f":0.0,"c":12.0,"page":9,"portion":"маленькая"},{"name":"Добрый Лимон-Лайм (средняя)","base_name":"Добрый Лимон-Лайм","w":400.0,"k":76.0,"p":0.0,"f":0.0,"c":18.0,"page":9,"portion":"средняя"},{"name":"Добрый Лимон-Лайм (большая)","base_name":"Добрый Лимон-Лайм","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":9,"portion":"большая"},{"name":"Добрый Кола без сахара (маленькая)","base_name":"Добрый Кола без сахара","w":250.0,"k":0.75,"p":0.0,"f":0.0,"c":0.25,"page":10,"portion":"маленькая"},{"name":"Добрый Кола без сахара (средняя)","base_name":"Добрый Кола без сахара","w":400.0,"k":1.2,"p":0.0,"f":0.0,"c":0.4,"page":10,"portion":"средняя"},{"name":"Добрый Кола без сахара (большая)","base_name":"Добрый Кола без сахара","w":500.0,"k":1.5,"p":0.0,"f":0.0,"c":0.5,"page":10,"portion":"большая"},{"name":"Сок восстановленный яблочный (маленькая)","base_name":"Сок восстановленный яблочный","w":300.0,"k":144.0,"p":0.0,"f":0.0,"c":34.0,"page":10,"portion":"маленькая"},{"name":"Сок восстановленный яблочный (средняя)","base_name":"Сок восстановленный яблочный","w":400.0,"k":192.0,"p":0.0,"f":0.0,"c":45.0,"page":10,"portion":"средняя"},{"name":"Сок восстановленный яблочный (большая)","base_name":"Сок восстановленный яблочный","w":500.0,"k":240.0,"p":0.0,"f":0.0,"c":57.0,"page":10,"portion":"большая"},{"name":"Сок восстановленный апельсиновый (маленькая)","base_name":"Сок восстановленный апельсиновый","w":300.0,"k":140.0,"p":0.0,"f":0.0,"c":26.0,"page":10,"portion":"маленькая"},{"name":"Сок восстановленный апельсиновый (средняя)","base_name":"Сок восстановленный апельсиновый","w":400,"k":187.0,"p":0.0,"f":0.0,"c":34.0,"page":10,"portion":"средняя"},{"name":"Сок восстановленный апельсиновый (большая)","base_name":"Сок восстановленный апельсиновый","w":500.0,"k":234.0,"p":0.0,"f":0.0,"c":43.0,"page":10,"portion":"большая"},{"name":"Бамбл кофе","base_name":"Бамбл кофе","w":294.0,"k":162.0,"p":1.9,"f":1.9,"c":34.0,"page":10,"portion":""},{"name":"Физз Черноголовка Вишня (Физз Вишня) (маленькая)","base_name":"Физз Черноголовка Вишня (Физз Вишня)","w":250.0,"k":113.0,"p":0.0,"f":0.0,"c":28.0,"page":10,"portion":"маленькая"},{"name":"Физз Черноголовка Вишня (Физз Вишня) (средняя)","base_name":"Физз Черноголовка Вишня (Физз Вишня)","w":400.0,"k":180.0,"p":0.0,"f":0.0,"c":44.0,"page":10,"portion":"средняя"},{"name":"Физз Черноголовка Вишня (Физз Вишня) (большая)","base_name":"Физз Черноголовка Вишня (Физз Вишня)","w":500.0,"k":225.0,"p":0.0,"f":0.0,"c":55.0,"page":10,"portion":"большая"},{"name":"Лимонад Дольче манго","base_name":"Лимонад Дольче манго","w":266.0,"k":93.0,"p":0.0,"f":0.0,"c":23.0,"page":10,"portion":""},{"name":"Санрайз Дольче манго","base_name":"Санрайз Дольче манго","w":316.0,"k":187.0,"p":0.0,"f":0.0,"c":38.0,"page":11,"portion":""},{"name":"Айс Кофе Карамель","base_name":"Айс Кофе Карамель","w":300.0,"k":135.0,"p":3.6,"f":3.8,"c":21.0,"page":11,"portion":""},{"name":"Коктейль молочный с клубничным сиропом (маленькая)","base_name":"Коктейль молочный с клубничным сиропом","w":300.0,"k":232.0,"p":5.5,"f":4.5,"c":42.0,"page":11,"portion":"маленькая"},{"name":"Коктейль молочный с клубничным сиропом (средняя)","base_name":"Коктейль молочный с клубничным сиропом","w":400.0,"k":309.0,"p":7.3,"f":6.0,"c":57.0,"page":11,"portion":"средняя"},{"name":"Коктейль молочный с клубничным сиропом (большая)","base_name":"Коктейль молочный с клубничным сиропом","w":500.0,"k":387.0,"p":9.1,"f":7.5,"c":71.0,"page":11,"portion":"большая"},{"name":"Коктейль молочный с ванильным сиропом (маленькая)","base_name":"Коктейль молочный с ванильным сиропом","w":300.0,"k":229.0,"p":5.4,"f":4.5,"c":42.0,"page":11,"portion":"маленькая"},{"name":"Коктейль молочный с ванильным сиропом (средняя)","base_name":"Коктейль молочный с ванильным сиропом","w":400.0,"k":303.0,"p":7.2,"f":6.0,"c":55.0,"page":11,"portion":"средняя"},{"name":"Коктейль молочный с ванильным сиропом (большая)","base_name":"Коктейль молочный с ванильным сиропом","w":500.0,"k":380.0,"p":9.0,"f":7.5,"c":69.0,"page":11,"portion":"большая"},{"name":"Коктейль молочный с шоколадным сиропом (маленькая)","base_name":"Коктейль молочный с шоколадным сиропом","w":300.0,"k":231.0,"p":5.8,"f":4.8,"c":41.0,"page":11,"portion":"маленькая"},{"name":"Коктейль молочный с шоколадным сиропом (средняя)","base_name":"Коктейль молочный с шоколадным сиропом","w":400.0,"k":305.0,"p":7.7,"f":6.4,"c":54.0,"page":11,"portion":"средняя"},{"name":"Коктейль молочный с шоколадным сиропом (большая)","base_name":"Коктейль молочный с шоколадным сиропом","w":500.0,"k":384.0,"p":9.7,"f":8.0,"c":68.0,"page":11,"portion":"большая"},{"name":"Молочный коктейль Черешня","base_name":"Молочный коктейль Черешня","w":300.0,"k":216.0,"p":5.3,"f":4.4,"c":39.0,"page":11,"portion":""},{"name":"Мороженое мягкое молочное Карамель","base_name":"Мороженое мягкое молочное Карамель","w":175.0,"k":312.0,"p":5.2,"f":6.7,"c":58.0,"page":12,"portion":""},{"name":"Мороженое мягкое молочное Шоколад","base_name":"Мороженое мягкое молочное Шоколад","w":173.0,"k":308.0,"p":5.7,"f":9.3,"c":49.0,"page":12,"portion":""},{"name":"Мороженое мягкое молочное Клубника","base_name":"Мороженое мягкое молочное Клубника","w":172.0,"k":256.0,"p":4.8,"f":4.9,"c":48.0,"page":12,"portion":""},{"name":"Мороженое мягкое молочное в вафельном рожке","base_name":"Мороженое мягкое молочное в вафельном рожке","w":98.0,"k":164.0,"p":3.8,"f":3.6,"c":29.0,"page":12,"portion":""},{"name":"Пирожок с вишневой начинкой","base_name":"Пирожок с вишневой начинкой","w":80.0,"k":290.0,"p":2.4,"f":12.0,"c":43.0,"page":13,"portion":""},{"name":"Пирожок Клубника со сливками","base_name":"Пирожок Клубника со сливками","w":80.0,"k":277.0,"p":3.6,"f":13.0,"c":36.0,"page":13,"portion":""},{"name":"Пирожок Лесные Ягоды-кремчиз","base_name":"Пирожок Лесные Ягоды-кремчиз","w":79.0,"k":271.0,"p":3.1,"f":14.0,"c":33.0,"page":14,"portion":""},{"name":"Венецианские пончики","base_name":"Венецианские пончики","w":80.0,"k":251.0,"p":3.3,"f":11.0,"c":34.0,"page":14,"portion":""},{"name":"Чай зеленый (маленькая)","base_name":"Чай зеленый","w":200.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"маленькая"},{"name":"Чай зеленый (средняя)","base_name":"Чай зеленый","w":300.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"средняя"},{"name":"Чай чёрный (маленькая)","base_name":"Чай чёрный","w":200.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"маленькая"},{"name":"Чай чёрный (средняя)","base_name":"Чай чёрный","w":300.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"средняя"},{"name":"Чай черный Эрл Грей (маленькая)","base_name":"Чай черный Эрл Грей","w":200.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"маленькая"},{"name":"Чай черный Эрл Грей (средняя)","base_name":"Чай черный Эрл Грей","w":300.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":14,"portion":"средняя"},{"name":"Двойной эспрессо","base_name":"Двойной эспрессо","w":70.0,"k":2.0,"p":0.2,"f":0.1,"c":0.2,"page":14,"portion":""},{"name":"Американо (Маленькая)","base_name":"Американо","w":200.0,"k":7.0,"p":0.6,"f":0.2,"c":0.6,"page":15,"portion":"Маленькая"},{"name":"Американо (Средняя)","base_name":"Американо","w":300.0,"k":10.0,"p":0.9,"f":0.3,"c":0.9,"page":15,"portion":"Средняя"},{"name":"Американо (Большая)","base_name":"Американо","w":400.0,"k":14.0,"p":1.2,"f":0.4,"c":1.2,"page":15,"portion":"Большая"},{"name":"Молочный составной продукт Капучино (Маленькая)","base_name":"Молочный составной продукт Капучино","w":200.0,"k":71.0,"p":3.6,"f":3.8,"c":5.6,"page":15,"portion":"Маленькая"},{"name":"Молочный составной продукт Капучино (Средняя)","base_name":"Молочный составной продукт Капучино","w":300.0,"k":113.0,"p":5.8,"f":6.0,"c":8.9,"page":15,"portion":"Средняя"},{"name":"Молочный составной продукт Капучино (Большая)","base_name":"Молочный составной продукт Капучино","w":400.0,"k":132.0,"p":6.8,"f":7.0,"c":10.0,"page":15,"portion":"Большая"},{"name":"Молочный составной продукт Латте (Средняя)","base_name":"Молочный составной продукт Латте","w":300.0,"k":122.0,"p":6.2,"f":6.5,"c":9.6,"page":15,"portion":"Средняя"},{"name":"Молочный составной продукт Латте (Большая)","base_name":"Молочный составной продукт Латте","w":400.0,"k":135.0,"p":6.9,"f":7.2,"c":11.0,"page":15,"portion":"Большая"},{"name":"Кофе глясе","base_name":"Кофе глясе","w":280.0,"k":123.0,"p":3.6,"f":3.3,"c":20.0,"page":15,"portion":""},{"name":"Молочный составной продукт Флэт Уайт (Средняя)","base_name":"Молочный составной продукт Флэт Уайт","w":300.0,"k":101.0,"p":5.2,"f":5.4,"c":8.0,"page":15,"portion":"Средняя"},{"name":"Молочный составной продукт Флэт Уайт (Большая)","base_name":"Молочный составной продукт Флэт Уайт","w":400.0,"k":144.0,"p":7.4,"f":7.7,"c":11.0,"page":15,"portion":"Большая"},{"name":"Маффин с яйцом и сыром","base_name":"Маффин с яйцом и сыром","w":116.0,"k":289.0,"p":16.0,"f":13.0,"c":26.0,"page":15,"portion":""},{"name":"Маффин с яйцом и ветчиной","base_name":"Маффин с яйцом и ветчиной","w":156.0,"k":312.0,"p":20.0,"f":14.0,"c":26.0,"page":15,"portion":""},{"name":"Маффин с яйцом и беконом","base_name":"Маффин с яйцом и беконом","w":121.0,"k":317.0,"p":18.0,"f":15.0,"c":26.0,"page":16,"portion":""},{"name":"Маффин с яйцом и свиной котлетой","base_name":"Маффин с яйцом и свиной котлетой","w":161.0,"k":434.0,"p":25.0,"f":25.0,"c":26.0,"page":16,"portion":""},{"name":"Двойной Маффин с яйцом и свиной котлетой","base_name":"Двойной Маффин с яйцом и свиной котлетой","w":220.0,"k":628.0,"p":38.0,"f":40.0,"c":28.0,"page":16,"portion":""},{"name":"Маффин со свиной котлетой","base_name":"Маффин со свиной котлетой","w":116.0,"k":344.0,"p":18.0,"f":18.0,"c":26.0,"page":16,"portion":""},{"name":"Фреш Маффин","base_name":"Фреш Маффин","w":150.0,"k":368.0,"p":18.0,"f":20.0,"c":28.0,"page":16,"portion":""},{"name":"Двойной Фреш Маффин","base_name":"Двойной Фреш Маффин","w":196.0,"k":513.0,"p":28.0,"f":32.0,"c":28.0,"page":16,"portion":""},{"name":"Чикен Фреш Маффин","base_name":"Чикен Фреш Маффин","w":142.0,"k":325.0,"p":13.0,"f":14.0,"c":37.0,"page":16,"portion":""},{"name":"Омлеттер с беконом и сыром","base_name":"Омлеттер с беконом и сыром","w":133.0,"k":297.0,"p":16.0,"f":12.0,"c":29.0,"page":17,"portion":""},{"name":"Фреш Ролл","base_name":"Фреш Ролл","w":215.0,"k":537.0,"p":23.0,"f":34.0,"c":34.0,"page":17,"portion":""},{"name":"Чикен Фреш Ролл","base_name":"Чикен Фреш Ролл","w":250.0,"k":563.0,"p":24.0,"f":30.0,"c":48.0,"page":17,"portion":""},{"name":"Утренний Ролл","base_name":"Утренний Ролл","w":225.0,"k":550.0,"p":25.0,"f":29.0,"c":46.0,"page":17,"portion":""},{"name":"Омлет","base_name":"Омлет","w":149.0,"k":292.0,"p":17.0,"f":13.0,"c":26.0,"page":17,"portion":""},{"name":"Омлет с беконом","base_name":"Омлет с беконом","w":157.0,"k":331.0,"p":20.0,"f":16.0,"c":26.0,"page":17,"portion":""},{"name":"Омлет с ветчиной","base_name":"Омлет с ветчиной","w":189.0,"k":344.0,"p":24.0,"f":15.0,"c":27.0,"page":17,"portion":""},{"name":"Омлет с сыром","base_name":"Омлет с сыром","w":177.0,"k":389.0,"p":23.0,"f":21.0,"c":27.0,"page":18,"portion":""},{"name":"Яичница","base_name":"Яичница","w":149.0,"k":292.0,"p":17.0,"f":13.0,"c":26.0,"page":18,"portion":""},{"name":"Яичница с беконом","base_name":"Яичница с беконом","w":157.0,"k":331.0,"p":20.0,"f":16.0,"c":26.0,"page":18,"portion":""},{"name":"Яичница с ветчиной","base_name":"Яичница с ветчиной","w":189.0,"k":344.0,"p":24.0,"f":15.0,"c":26.0,"page":18,"portion":""},{"name":"Яичница с сыром","base_name":"Яичница с сыром","w":177.0,"k":389.0,"p":23.0,"f":21.0,"c":27.0,"page":18,"portion":""},{"name":"Блины","base_name":"Блины","w":110.0,"k":207.0,"p":8.3,"f":6.6,"c":29.0,"page":18,"portion":""},{"name":"Рулетики с творогом и шоколадом","base_name":"Рулетики с творогом и шоколадом","w":72.0,"k":223.0,"p":6.5,"f":10.0,"c":27.0,"page":18,"portion":""},{"name":"Тост с сыром","base_name":"Тост с сыром","w":78.0,"k":240.0,"p":10.0,"f":9.7,"c":27.0,"page":19,"portion":""},{"name":"Тост с ветчиной и сыром","base_name":"Тост с ветчиной и сыром","w":98.0,"k":266.0,"p":13.0,"f":11.0,"c":28.0,"page":19,"portion":""},{"name":"Сырники","base_name":"Сырники","w":120.0,"k":221.0,"p":18.0,"f":2.6,"c":31.0,"page":19,"portion":""},{"name":"Большой завтрак","base_name":"Большой завтрак","w":194.0,"k":431.0,"p":26.0,"f":24.0,"c":26.0,"page":19,"portion":""},{"name":"Картофельный Оладушек","base_name":"Картофельный Оладушек","w":44.0,"k":94.0,"p":1.7,"f":5.0,"c":9.9,"page":19,"portion":""},{"name":"Фреш Маффин Базиликовый","base_name":"Фреш Маффин Базиликовый","w":159.0,"k":396.0,"p":18.0,"f":21.0,"c":33.0,"page":19,"portion":""},{"name":"Клубничный чизкейк","base_name":"Клубничный чизкейк","w":115.0,"k":296.0,"p":4.8,"f":15.0,"c":35.0,"page":20,"portion":""},{"name":"Торт Шоколадный","base_name":"Торт Шоколадный","w":112.0,"k":419.0,"p":4.5,"f":25.0,"c":45.0,"page":20,"portion":""},{"name":"Творожник","base_name":"Творожник","w":70.0,"k":197.0,"p":6.0,"f":9.0,"c":23.0,"page":21,"portion":""},{"name":"Чизкейк классический","base_name":"Чизкейк классический","w":125.0,"k":426.0,"p":7.5,"f":26.0,"c":40.0,"page":21,"portion":""},{"name":"Лимонный тарт","base_name":"Лимонный тарт","w":108.0,"k":432.0,"p":4.9,"f":28.0,"c":40.0,"page":21,"portion":""},{"name":"Шоколадный тарт с вишней","base_name":"Шоколадный тарт с вишней","w":120.0,"k":298.0,"p":4.1,"f":11.0,"c":46.0,"page":21,"portion":""},{"name":"Чизкейк Сан-Себастьян","base_name":"Чизкейк Сан-Себастьян","w":90.0,"k":233.0,"p":4.2,"f":15.0,"c":20.0,"page":22,"portion":""},{"name":"Пирожное Картошка","base_name":"Пирожное Картошка","w":60.0,"k":341.0,"p":3.6,"f":22.0,"c":33.0,"page":22,"portion":""},{"name":"Малиновая тарталетка","base_name":"Малиновая тарталетка","w":120.0,"k":311.0,"p":4.2,"f":16.0,"c":38.0,"page":22,"portion":""},{"name":"Пирожное Шу с ореховой начинкой","base_name":"Пирожное Шу с ореховой начинкой","w":55.0,"k":219.0,"p":3.6,"f":16.0,"c":15.0,"page":22,"portion":""},{"name":"Премиальный яблочный пирог","base_name":"Премиальный яблочный пирог","w":145.0,"k":285.0,"p":2.9,"f":9.3,"c":47.0,"page":23,"portion":""},{"name":"Пирожное Ягодный космос","base_name":"Пирожное Ягодный космос","w":95.0,"k":360.0,"p":3.3,"f":15.0,"c":52.0,"page":23,"portion":""},{"name":"Капкейк Соленая карамель","base_name":"Капкейк Соленая карамель","w":95.0,"k":388.0,"p":4.3,"f":25.0,"c":37.0,"page":24,"portion":""},{"name":"Муравейник","base_name":"Муравейник","w":80.0,"k":403.0,"p":5.6,"f":22.0,"c":45.0,"page":24,"portion":""},{"name":"Круассан","base_name":"Круассан","w":62.0,"k":213.0,"p":4.3,"f":12.0,"c":22.0,"page":24,"portion":""},{"name":"Круассан классический","base_name":"Круассан классический","w":74.0,"k":253.0,"p":4.5,"f":13.0,"c":30.0,"page":24,"portion":""},{"name":"Печенье шоколадное с кусочками шоколада","base_name":"Печенье шоколадное с кусочками шоколада","w":70.0,"k":310.0,"p":4.1,"f":15.0,"c":40.0,"page":25,"portion":""},{"name":"Шоколадный круассан","base_name":"Шоколадный круассан","w":72.0,"k":274.0,"p":4.7,"f":14.0,"c":33.0,"page":25,"portion":""},{"name":"Печенье Малина-Белый шоколад","base_name":"Печенье Малина-Белый шоколад","w":75.0,"k":332.0,"p":3.8,"f":13.0,"c":49.0,"page":25,"portion":""},{"name":"Печенье Апельсин-миндаль","base_name":"Печенье Апельсин-миндаль","w":75.0,"k":305.0,"p":4.4,"f":14.0,"c":40.0,"page":25,"portion":""},{"name":"Улитка с карамелью","base_name":"Улитка с карамелью","w":95.0,"k":301.0,"p":4.5,"f":16.0,"c":34.0,"page":26,"portion":""},{"name":"Круассан с ветчиной и сыром","base_name":"Круассан с ветчиной и сыром","w":130.0,"k":351.0,"p":17.0,"f":20.0,"c":25.0,"page":26,"portion":""},{"name":"Круассан классический с ветчиной и сыром","base_name":"Круассан классический с ветчиной и сыром","w":142.0,"k":391.0,"p":17.0,"f":21.0,"c":33.0,"page":26,"portion":""},{"name":"Чиабатта с ветчиной и сыром","base_name":"Чиабатта с ветчиной и сыром","w":212.0,"k":432.0,"p":23.0,"f":17.0,"c":47.0,"page":26,"portion":""},{"name":"Чиабатта с тунцом","base_name":"Чиабатта с тунцом","w":168.0,"k":371.0,"p":22.0,"f":11.0,"c":44.0,"page":26,"portion":""},{"name":"Венский Кофе (Средняя)","base_name":"Венский Кофе","w":250.0,"k":174.0,"p":1.8,"f":17.0,"c":3.8,"page":27,"portion":"Средняя"},{"name":"Венский Кофе (Большая)","base_name":"Венский Кофе","w":350.0,"k":177.0,"p":2.1,"f":17.0,"c":4.1,"page":27,"portion":"Большая"},{"name":"Молочный составной продукт Раф (Средняя)","base_name":"Молочный составной продукт Раф","w":300.0,"k":285.0,"p":5.9,"f":22.0,"c":17.0,"page":27,"portion":"Средняя"},{"name":"Молочный составной продукт Раф (Большая)","base_name":"Молочный составной продукт Раф","w":400.0,"k":316.0,"p":7.5,"f":24.0,"c":19.0,"page":27,"portion":"Большая"},{"name":"Молочный составной продукт Горячий шоколад","base_name":"Молочный составной продукт Горячий шоколад","w":300.0,"k":319.0,"p":8.1,"f":19.0,"c":31.0,"page":27,"portion":""},{"name":"Чай Зеленый с жасмином","base_name":"Чай Зеленый с жасмином","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Чай черный с чабрецом","base_name":"Чай черный с чабрецом","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Чай Зеленый Хуго Коктейль","base_name":"Чай Зеленый Хуго Коктейль","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Чай зеленый лайм-имбирь","base_name":"Чай зеленый лайм-имбирь","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":27,"portion":""},{"name":"Чай черный тропические фрукты","base_name":"Чай черный тропические фрукты","w":400.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":28,"portion":""},{"name":"Фраппе Карамельный (Средняя)","base_name":"Фраппе Карамельный","w":330.0,"k":290.0,"p":4.4,"f":14.0,"c":37.0,"page":28,"portion":"Средняя"},{"name":"Фраппе Карамельный (Большая)","base_name":"Фраппе Карамельный","w":440.0,"k":360.0,"p":5.1,"f":14.0,"c":53.0,"page":28,"portion":"Большая"},{"name":"Фраппе Клубничный (Средняя)","base_name":"Фраппе Клубничный","w":330.0,"k":283.0,"p":3.3,"f":14.0,"c":36.0,"page":28,"portion":"Средняя"},{"name":"Фраппе Клубничный (Большая)","base_name":"Фраппе Клубничный","w":440.0,"k":332.0,"p":3.4,"f":14.0,"c":48.0,"page":28,"portion":"Большая"},{"name":"Фраппе Малина-белый шоколад","base_name":"Фраппе Малина-белый шоколад","w":330.0,"k":359.0,"p":3.1,"f":25.0,"c":30.0,"page":28,"portion":""},{"name":"Бабл Айс Кофе","base_name":"Бабл Айс Кофе","w":400.0,"k":240.0,"p":6.0,"f":6.0,"c":40.0,"page":28,"portion":""},{"name":"Бабл-ти Ананас-лемонграсс","base_name":"Бабл-ти Ананас-лемонграсс","w":310.0,"k":166.0,"p":0.0,"f":0.0,"c":41.0,"page":29,"portion":""},{"name":"Молочный составной продукт Айс Матча Кокос","base_name":"Молочный составной продукт Айс Матча Кокос","w":310.0,"k":334.0,"p":9.1,"f":20.0,"c":29.0,"page":29,"portion":""},{"name":"Эспрессо-тоник Гранат","base_name":"Эспрессо-тоник Гранат","w":294.0,"k":107.0,"p":0.4,"f":0.3,"c":26.0,"page":29,"portion":""},{"name":"Капучино Миндальный (Маленькая)","base_name":"Капучино Миндальный","w":176.0,"k":30.0,"p":0.7,"f":1.6,"c":3.3,"page":29,"portion":"Маленькая"},{"name":"Капучино Миндальный (Средняя)","base_name":"Капучино Миндальный","w":176.0,"k":42.0,"p":0.9,"f":2.2,"c":4.6,"page":29,"portion":"Средняя"},{"name":"Капучино Миндальный (Большая)","base_name":"Капучино Миндальный","w":325.0,"k":54.0,"p":1.2,"f":2.8,"c":5.9,"page":29,"portion":"Большая"},{"name":"Капучино Кокосовый (Маленькая)","base_name":"Капучино Кокосовый","w":176.0,"k":40.0,"p":1.3,"f":1.7,"c":4.9,"page":29,"portion":"Маленькая"},{"name":"Капучино Кокосовый (Средняя)","base_name":"Капучино Кокосовый","w":176.0,"k":56.0,"p":1.8,"f":2.4,"c":6.9,"page":29,"portion":"Средняя"},{"name":"Капучино Кокосовый (Большая)","base_name":"Капучино Кокосовый","w":325.0,"k":72.0,"p":2.3,"f":3.0,"c":8.9,"page":29,"portion":"Большая"},{"name":"Латте Миндальный (Средняя)","base_name":"Латте Миндальный","w":270.0,"k":47.0,"p":1.0,"f":2.5,"c":5.2,"page":30,"portion":"Средняя"},{"name":"Латте Миндальный (Большая)","base_name":"Латте Миндальный","w":270.0,"k":51.0,"p":1.1,"f":2.7,"c":5.7,"page":30,"portion":"Большая"},{"name":"Латте Кокосовый (Средняя)","base_name":"Латте Кокосовый","w":270.0,"k":63.0,"p":2.0,"f":2.7,"c":7.8,"page":30,"portion":"Средняя"},{"name":"Латте Кокосовый (Большая)","base_name":"Латте Кокосовый","w":270.0,"k":69.0,"p":2.2,"f":2.9,"c":8.5,"page":30,"portion":"Большая"},{"name":"Флэт Уайт Миндальный (Средняя)","base_name":"Флэт Уайт Миндальный","w":245.0,"k":42.0,"p":0.9,"f":2.2,"c":4.6,"page":30,"portion":"Средняя"},{"name":"Флэт Уайт Миндальный (Большая)","base_name":"Флэт Уайт Миндальный","w":245.0,"k":59.0,"p":1.3,"f":3.1,"c":6.5,"page":30,"portion":"Большая"},{"name":"Флэт Уайт Кокосовый (Средняя)","base_name":"Флэт Уайт Кокосовый","w":245.0,"k":56.0,"p":1.8,"f":2.3,"c":6.9,"page":30,"portion":"Средняя"},{"name":"Флэт Уайт Кокосовый (Большая)","base_name":"Флэт Уайт Кокосовый","w":245.0,"k":79.0,"p":2.5,"f":3.3,"c":9.8,"page":30,"portion":"Большая"},{"name":"Айс Кофе Карамель Миндальный","base_name":"Айс Кофе Карамель Миндальный","w":194.0,"k":90.0,"p":0.6,"f":1.3,"c":19.0,"page":30,"portion":""},{"name":"Айс Кофе Карамель Кокосовый","base_name":"Айс Кофе Карамель Кокосовый","w":194.0,"k":96.0,"p":1.1,"f":1.4,"c":20.0,"page":30,"portion":""},{"name":"Кетчуп","base_name":"Кетчуп","w":25.0,"k":30.0,"p":0.38,"f":0.05,"c":6.75,"page":30,"portion":""},{"name":"Соус Кисло-Сладкий","base_name":"Соус Кисло-Сладкий","w":25.0,"k":40.0,"p":0.12,"f":0.25,"c":9.5,"page":31,"portion":""},{"name":"Соус Горчичный","base_name":"Соус Горчичный","w":25.0,"k":53.75,"p":0.5,"f":3.0,"c":5.75,"page":31,"portion":""},{"name":"Соус Барбекю","base_name":"Соус Барбекю","w":25.0,"k":40.0,"p":0.12,"f":0.25,"c":9.0,"page":31,"portion":""},{"name":"Соус Сырный","base_name":"Соус Сырный","w":25.0,"k":90.0,"p":0.5,"f":9.25,"c":1.5,"page":31,"portion":""},{"name":"Соус 1000 островов","base_name":"Соус 1000 островов","w":25.0,"k":77.5,"p":0.25,"f":7.25,"c":3.0,"page":32,"portion":""},{"name":"Соус Сладкий Чили","base_name":"Соус Сладкий Чили","w":25.0,"k":42.5,"p":0.05,"f":0.03,"c":10.25,"page":32,"portion":""},{"name":"Соус десертный Шоколадный","base_name":"Соус десертный Шоколадный","w":25.0,"k":72.5,"p":0.88,"f":0.88,"c":15.0,"page":32,"portion":""},{"name":"Соус Сырный халапеньо","base_name":"Соус Сырный халапеньо","w":25.0,"k":77.5,"p":0.25,"f":7.25,"c":2.75,"page":32,"portion":""},{"name":"Соус Чили-Лайм","base_name":"Соус Чили-Лайм","w":25.0,"k":35.0,"p":0.5,"f":0.12,"c":8.0,"page":32,"portion":""},{"name":"Артезианская вода Черноголовка негазированная","base_name":"Артезианская вода Черноголовка негазированная","w":500.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":33,"portion":""},{"name":"Питьевая вода Черноголовка газированная","base_name":"Питьевая вода Черноголовка газированная","w":500.0,"k":0.0,"p":0.0,"f":0.0,"c":0.0,"page":33,"portion":""},{"name":"Джем клубничный","base_name":"Джем клубничный","w":20.0,"k":48.0,"p":0.0,"f":0.0,"c":12.0,"page":33,"portion":""},{"name":"Оливковое масло","base_name":"Оливковое масло","w":10.0,"k":82.0,"p":0.0,"f":9.13,"c":0.0,"page":33,"portion":""},{"name":"Соус Цезарь","base_name":"Соус Цезарь","w":25.0,"k":60.0,"p":0.62,"f":5.5,"c":1.75,"page":33,"portion":""},{"name":"Морковные палочки","base_name":"Морковные палочки","w":80.0,"k":28.0,"p":1.04,"f":0.08,"c":5.52,"page":33,"portion":""},{"name":"Яблочные дольки","base_name":"Яблочные дольки","w":80.0,"k":37.6,"p":0.32,"f":0.32,"c":7.84,"page":33,"portion":""},{"name":"Добрый \"Кола\"","base_name":"Добрый \"Кола\"","w":500.0,"k":210.0,"p":0.0,"f":0.0,"c":53.0,"page":34,"portion":""},{"name":"Добрый \"Кола без сахара\"","base_name":"Добрый \"Кола без сахара\"","w":500.0,"k":1.5,"p":0.0,"f":0.0,"c":0.5,"page":34,"portion":""},{"name":"Добрый \"Лимон-Лайм\"","base_name":"Добрый \"Лимон-Лайм\"","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":34,"portion":""},{"name":"Добрый \"Апельсин\"","base_name":"Добрый \"Апельсин\"","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":34,"portion":""},{"name":"Липтон Лимон","base_name":"Липтон Лимон","w":500.0,"k":95.0,"p":0.0,"f":0.0,"c":23.0,"page":34,"portion":""},{"name":"Малиновый мусс","base_name":"Малиновый мусс","w":100.0,"k":229.0,"p":2.3,"f":13.3,"c":25.1,"page":34,"portion":""},{"name":"Фруктовые пастилки","base_name":"Фруктовые пастилки","w":15.0,"k":49.5,"p":0.15,"f":0.01,"c":12.3,"page":35,"portion":""},{"name":"Бифштекс из говядины рубленый 80 г / Бифштекс","base_name":"Бифштекс из говядины рубленый 80 г / Бифштекс","w":80.0,"k":213.6,"p":19.2,"f":15.2,"c":0.0,"page":35,"portion":""},{"name":"Соус Тар Тар","base_name":"Соус Тар Тар","w":20.0,"k":40.0,"p":0.1,"f":3.8,"c":1.2,"page":35,"portion":""},{"name":"Соус Биг Спешиал","base_name":"Соус Биг Спешиал","w":10.0,"k":33.0,"p":0.2,"f":3.2,"c":0.9,"page":36,"portion":""},{"name":"Горчица / Соус горчичный","base_name":"Горчица / Соус горчичный","w":0.5,"k":0.35,"p":0.02,"f":0.02,"c":0.01,"page":36,"portion":""},{"name":"Топпинг клубничный / Топпинг \"Джем клубничный\"","base_name":"Топпинг клубничный / Топпинг \"Джем клубничный\"","w":30.0,"k":59.4,"p":0.12,"f":0.03,"c":14.49,"page":36,"portion":""},{"name":"Топпинг шоколадный / Топпинг \"Шоколадная помадка\"","base_name":"Топпинг шоколадный / Топпинг \"Шоколадная помадка\"","w":30.0,"k":103.5,"p":0.78,"f":3.93,"c":15.99,"page":36,"portion":""},{"name":"Топпинг карамельный / Топпинг \"Карамельная помадка\"","base_name":"Топпинг карамельный / Топпинг \"Карамельная помадка\"","w":30.0,"k":96.9,"p":0.6,"f":1.5,"c":20.22,"page":37,"portion":""},{"name":"Сироп ванильный","base_name":"Сироп ванильный","w":24.0,"k":50.4,"p":0.0,"f":0.0,"c":12.72,"page":37,"portion":""},{"name":"Сироп карамельный","base_name":"Сироп карамельный","w":24.0,"k":50.4,"p":0.0,"f":0.0,"c":12.72,"page":37,"portion":""},{"name":"Молоко","base_name":"Молоко","w":30.0,"k":18.0,"p":0.9,"f":0.96,"c":1.41,"page":38,"portion":""},{"name":"Шоколадная крошка / Крошка печенья с какао","base_name":"Шоколадная крошка / Крошка печенья с какао","w":8.0,"k":35.2,"p":0.6,"f":1.12,"c":5.6,"page":38,"portion":""},{"name":"Халапеньо","base_name":"Халапеньо","w":9.0,"k":1.53,"p":0.04,"f":0.02,"c":0.22,"page":38,"portion":""},{"name":"Топпинг Ананас-питахайя","base_name":"Топпинг Ананас-питахайя","w":30.0,"k":55.2,"p":0.06,"f":0.0,"c":13.62,"page":38,"portion":""},{"name":"Топпинг Маракуйя с косточкой","base_name":"Топпинг Маракуйя с косточкой","w":30.0,"k":64.8,"p":0.15,"f":0.02,"c":15.84,"page":38,"portion":""}];
// Values independently verified against the official currently available PDF.
// Other rows still await full-document re-extraction and comparison.
const CHAIN_VERIFIED_CURRENT={"Фиш Бургер":{"w":130,"k":327,"p":13,"f":13,"c":40},"Биг Хит":{"w":216,"k":503,"p":25,"f":25,"c":45},"Чикен Хит":{"w":190,"k":445,"p":19,"f":19,"c":50},"Биг Спешиал":{"w":326,"k":756,"p":41,"f":42,"c":52},"Двойной Биг Спешиал":{"w":433,"k":1042,"p":67,"f":63,"c":52},"Двойной Биг Хит":{"w":284,"k":676,"p":40,"f":37,"c":46}};
for(const row of CHAIN_ROWS){const current=CHAIN_VERIFIED_CURRENT[row.base_name];if(current && row.portion===''){Object.assign(row,current,{source_date:'2026-11-20'})}}
const chainNormalize=(s)=>String(s||'').toLowerCase().replaceAll('ё','е').replace(/[«»"']/g,'').replace(/(?:^|\s)(?:из\s+)?мак(?:а|е|ом)?(?=\s|$)/g,' ').replace(/вкусно\s*[-—–]?\s*и\s*точка/gi,' ').replace(/^добрый\s+/i,' ').replace(/[()]/g,' ').replace(/[^a-zа-я0-9\s]/gi,' ').replace(/\s+/g,' ').trim();
function chainFind(query,top=8){
 const raw=chainNormalize(query)
   .replace(/наггетс(?:ов|ами|ы|а)?/g,'наггетсы').replace(/картошк(?:а|и|у|ой)?/g,'картофель')
   .replace(/кола\s*(?:зеро|zero)/g,'кола без сахара').replace(/чизбургера(?![а-я])/g,'чизбургер').replace(/гамбургера(?![а-я])/g,'гамбургер');
 const qwords=raw.split(' ').filter(x=>x.length>2&&!['шт','порция','порции','грамм','два','три','одна','один','маленькая','средняя','большая'].includes(x));
 const qty=(raw.match(/\b(4|6|9|18)\s*(?:шт|наггетсов|наггетсы)/)||[])[1]
      ||(raw.match(/\b(4|6|9|18)\b/)&&/наггетс/.test(raw)?(raw.match(/\b(4|6|9|18)\b/)||[])[1]:null);
 const wantedSize=/маленьк|малый|мал\b/.test(raw)?'маленькая':/больш|бол\b/.test(raw)?'большая':/средн|сред\b/.test(raw)?'средняя':'';
 const scored=[];
 for(const r of CHAIN_ROWS){const base=chainNormalize(r.base_name),label=chainNormalize(r.name);let score=0;
  if(raw===label)score+=130;else if(raw===base)score+=110;
  if(qwords.length && qwords.every(w=>label.includes(w)))score+=40;
  if(qwords.length && qwords.every(w=>base.includes(w)))score+=35;
  if(qwords.some(w=>!label.includes(w)))score-=38;
  if(raw.includes(base)&&base.length>5)score+=15;
  if(qty)score+=label.includes(qty+' шт')?60:-60;
  if(wantedSize)score+=r.portion.toLowerCase().includes(wantedSize)?40:-25;
  if(!wantedSize && r.portion){score+=/средн/.test(r.portion.toLowerCase())?3:0;}
  if(/\bдвойн/.test(raw)&&!base.includes('двойн'))score-=90;
  if(/\bбез сахара/.test(raw)&&!base.includes('без сахара'))score-=140;
  if(base.includes('без сахара')&&!raw.includes('без сахара'))score-=50;
  if(score>=25)scored.push({...r,source:'Вкусно — и точка',official_url:CHAIN_OFFICIAL_PDF,score});
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
 const c=find(['CHOAVL','CHOAVLDF'],['kolhydrater, tillgängliga','carbohydrate, available','carbohydrates available']);
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
   if(!foods.length)throw Error('Не получен список продуктов');
   SWEDISH_INDEX_CACHE={until:Date.now()+24*60*60*1000,items:foods};
  }
  const terms=q.toLowerCase().match(/[a-z]{3,}/g)||[];
  if(!terms.length)return {ok:true,items:[],diagnostic:'Швеция: для поиска нужен перевод на английский'};
  const best=foods.map(x=>{const s=String(x.namn||'').toLowerCase();let score=0;
    if(s===q.toLowerCase())score+=100;
    if(s.startsWith(q.toLowerCase()+' '))score+=70;
    terms.forEach(t=>{if(s.includes(t))score+=22;else score-=45});
    return {...x,score};}).filter(x=>x.score>=22).sort((a,b)=>b.score-a.score).slice(0,3);
  const detail=await Promise.all(best.map(async x=>{
   const r=await sourceJson(SLV_URL+'/livsmedel/'+encodeURIComponent(x.nummer)+'/naringsvarden?sprak=2',{},'SLV food');
   const n=r.ok?swedishNutrients(r.json):null;
   return n?{name:x.namn,source:'Livsmedelsverket (Швеция)',slv_id:x.nummer,match_score:x.score,...n}:null;
  }));
  return {ok:true,items:detail.filter(Boolean),diagnostic:`Livsmedelsverket: список ${foods.length}; совпадений ${detail.filter(Boolean).length}; ${Date.now()-started} мс`};
 }catch(e){return {ok:false,items:[],diagnostic:`Livsmedelsverket: ${String(e.message||e)}; ${Date.now()-started} мс`};}
}

// v1.3: allow calls from the PWA origin without exposing a wildcard CORS policy.
// Note: Origin checking restricts browser access; it is NOT a substitute for
// authentication/rate limits, because non-browser clients can spoof Origin.

// Restaurant order recognition v1.9: first ask the model to segment the whole order,
// then independently validate all words against the restaurant's real menu.
// The lexical pass prevents missing commas from collapsing an entire order.
const ORDER_ALIASES_RAW = [
 ['двойной биг тейсти','Двойной Биг Спешиал'],
 ['биг тейсти джуниор','Биг Спешиал Джуниор'],
 ['биг тейсти','Биг Спешиал'],
 ['биг тэйсти','Биг Спешиал'],
 ['big tasty','Биг Спешиал'],
 ['двойной биг хит','Двойной Биг Хит'],
 ['биг хит','Биг Хит'],
 ['биг хита','Биг Хит'],
 ['картошка по деревенски','Картофель по-деревенски'],
 ['картошку по деревенски','Картофель по-деревенски'],
 ['картофель по деревенски','Картофель по-деревенски'],
 ['картошка деревенская','Картофель по-деревенски'],
 ['деревенская картошка','Картофель по-деревенски'],
 ['картошка фри','Картофель Фри'],
 ['картошку фри','Картофель Фри'],
 ['картофель фри','Картофель Фри'],
 ['фри','Картофель Фри'],
 ['кола без сахара','Добрый Кола без сахара'],
 ['кока кола без сахара','Добрый Кола без сахара'],
 ['кола зеро','Добрый Кола без сахара'],
 ['кола zero','Добрый Кола без сахара'],
 ['добрый кола без сахара','Добрый Кола без сахара'],
 ['добрый кола','Добрый Кола'],
 ['кола','Добрый Кола'],
 ['кока кола','Добрый Кола'],
 ['сырный соус','Соус Сырный'],
 ['соус сырный','Соус Сырный'],
 ['соус с сыром','Соус Сырный'],
 ['наггетсов','Наггетсы'],['наггетсы','Наггетсы'],
 ['чизбургера','Чизбургер'],['чизбургер','Чизбургер'],
 ['гамбургера','Гамбургер'],['гамбургер','Гамбургер']
];
const orderWords=s=>String(s||'').toLowerCase().replaceAll('ё','е').match(/[a-zа-я0-9]+/gi)||[];
const orderSize=t=>/^(?:маленькая|маленький|маленькое|маленьк|малый|малая|малую|малаю|маленькую|небольшая|небольшой|небольшую|мал)$/.test(t)?'маленькая':/^(?:средн|средняя|средний|среднюю|среднее|средней)$/.test(t)?'средняя':/^(?:больш|большая|большой|большую|крупная|огромная)$/.test(t)?'большая':'';
const ORDER_FILLERS=new Set(['из','в','мак','мака','маке','маком','и','еще','ещё','мне','дай','пожалуйста','заказ','заказал','заказала','возьми','хочу','съел','съела','сегодня','плюс','добавь','два','один','одна','шт','штуки','штук','порция','порции','порций']);
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
 const raw=original.replace(/вкусно\s*[-—–]?\s*и\s*точка/ig,' ').replace(/макдоналдс/ig,' ')
  .replace(/(^|[\s,:;])(?:из\s+|в\s+)?мак(?:а|е|ом)?(?=$|[\s,:;])/gi,'$1 ');
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
  if(f.count && !/наггетс/.test(f.base.toLowerCase()))f.amount=Math.max(1,Math.min(f.count,12));
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
 if(!candidates.length)return {found:false,reason:'Товар не найден в каталоге'};
 const q=item.count||0;
 if(/наггетс/i.test(item.base)&&q){
  const exact=candidates.find(r=>String(r.portion).includes(String(q)+' шт'));
  if(exact)return {found:true,row:exact,quantity:1};
  return {found:false,reason:`Нет проверенной порции наггетсов: ${q} шт`};
 }
 let chosen=null;
 if(item.size){chosen=candidates.find(r=>String(r.portion||'').toLowerCase().includes(item.size));}
 if(!chosen&&!item.size){chosen=candidates.find(r=>!r.portion)||candidates.find(r=>/средн/i.test(r.portion))||candidates[0]}
 if(!chosen){
  // Single-size drink data is only an estimate for 250/400ml; never claim this is
  // a new official PDF row, and report the scaling in the technical diagnostics.
  if(/кола|лимон лайм|апельсин/i.test(item.base)){
    const drink=candidates.find(r=>!r.portion&&r.w>0);
    const sizeML={маленькая:250,средняя:400,большая:500}[item.size];
    if(drink&&sizeML){const scale=sizeML/drink.w;return {found:true,quantity:1,row:{...drink,name:`${drink.base_name} (${item.size})`,w:sizeML,k:drink.k*scale,p:drink.p*scale,f:drink.f*scale,c:drink.c*scale,estimated_portion:true},reason:'Пропорциональный расчёт по значению каталога для '+drink.w+' мл, не отдельная строка официальной таблицы'};}
  }
  return {found:false,reason:'Для указанного размера нет строки в каталоге'};
 }
 return {found:true,row:chosen,quantity:item.amount};
}
function validateAIDishes(aiData){
 return (aiData?.dishes||[]).map(d=>String(d.name||'').trim()).filter(Boolean);
}
async function analyzeRestaurantOrder(text,env){
 const started=Date.now();let neural=[],aiError=null,usage=null,attempts=0;
 const prompt='Разбей текст заказа из ресторана «Вкусно — и точка» на ВСЕ отдельные продукты, даже если нет запятых и союза «и». Прочти текст целиком: ресторан указан один для всех позиций. Исправь известные разговорные названия, но не придумывай неизвестных. «Биг Тейсти» = «Биг Спешиал». Верни только JSON вида {"dishes":[{"name":"Биг Спешиал","items":[{"name":"Биг Спешиал","portion":"1 штука"}]}],"uncertain":[]}; каждый продукт отдельным блюдом. Размер колы/картофеля оставляй в названии или portion. Текст: '+String(text).slice(0,500);
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
   const repairPrompt=`Проверь только НЕРАСПОЗНАННЫЕ ФРАГМЕНТЫ заказа из «Вкусно — и точка». Исходный заказ: ${String(text).slice(0,450)}. Уже выделено: ${lexical.found.map(x=>x.base).join(', ')}. Не распознано: ${lexical.leftovers.join(', ')}. Если во фрагменте есть ещё одно блюдо, верни JSON {"dishes":[{"name":"Название продукта","items":[{"name":"Название продукта","portion":"1 шт"}]}]}; иначе верни {"dishes":[],"uncertain":[]}. Не повторяй уже распознанные блюда.`;
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
   const p=phrase.replace(/(?:^|\s)(маленькая|средняя|большая)(?=\s|$)/gi,' ').trim();
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
  parsed.push({input:leftover,canonical:leftover,found:false,reason:'Не удалось сопоставить фрагмент заказа с меню'});
 }
 if(!parsed.length){
  parsed=neural.map(x=>{const entry={base:x,size:'',amount:1,count:null};return {input:x,canonical:x,...menuEntryForOrder(entry)}});
 }
 if(!parsed.length)parsed=[{input:text,canonical:text,found:false,reason:'Не удалось разделить заказ'}];
 return {ok:true,restaurant:'Вкусно — и точка',dishes:parsed,diagnostics:{elapsed_ms:Date.now()-started,neural,second_pass:recovery,neural_error:aiError,ai_attempts:attempts,usage,scanner:lexical,matched:parsed.map(p=>({input:p.input,name:p.row?.name,score:p.row?.score||null,estimated:p.row?.estimated_portion||false,found:p.found,reason:p.reason||null})),missing:parsed.filter(x=>!x.found).map(x=>x.input)}};
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
      if(!env.AI) return asJson({ok:false,error:'Не добавлен Workers AI binding AI'},503);
      let body;try{body=await request.json()}catch(_){return asJson({ok:false,error:'Нужен JSON с полем text'},400)}
      const text=String(body?.text||'').slice(0,500).trim();
      if(!text) return asJson({ok:false,error:'Не указан текст заказа'},400);
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
      return asJson({ok:true,source_date:CHAIN_PDF_DATE,rows:CHAIN_ROWS.length,official,notice:'Проверка доступности PDF не является публикацией новых КБЖУ.'});
    }
    if(request.method==='POST'&&u.pathname==='/nutrition-batch'){
      let qs=[];try{const body=await request.json();qs=Array.isArray(body.queries)?body.queries.slice(0,12).map(q=>String(q).slice(0,100)):[]}catch(_){return asJson({ok:false,error:'Bad JSON'},400)}
      const unique=[...new Set(qs.filter(q=>q.trim().length>=2))];
      const results=await Promise.all(unique.map(async q=>{
        try{const r=await searchNutrition(q,env,{fast:true});return {query:q,...r};}
        catch(e){return {query:q,ok:false,items:[],error:String(e?.message||e),diagnostics:['Ошибка отдельного запроса: '+String(e?.message||e)]};}
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
