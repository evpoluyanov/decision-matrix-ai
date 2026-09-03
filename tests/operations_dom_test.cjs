// Deterministic DOM contract tests, NOT a browser/layout/accessibility certification.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const code=fs.readFileSync('app/static/operations.js','utf8');
const json=(data,status=200)=>new Response(JSON.stringify(data),{status,headers:{'Content-Type':'application/json'}});
function environment({path='/projects/1',stored=new Map(),matrix=false,navigation='navigate'}={}){
  const nodes=new Map(),domReady=[],windowEvents={},calls=[],scrolls=[],timers=[];
  let handler=async()=>json({status:'ok'}),reloads=0;
  class Element {
    constructor(id=''){this.id=id;this.dataset={};this.listeners={};this.children=[];this.attrs={};this.disabled=false;this.textContent='';this.scrollLeft=0;
      this.classList={toggle(){},add(){},remove(){}};if(id)nodes.set(id,this);}
    set innerHTML(html){this._html=html;for(const id of html.matchAll(/id="([^"]+)"/g))new Element(id[1]);}
    get innerHTML(){return this._html||'Start';}
    append(...items){this.children.push(...items);}
    prepend(...items){this.children.unshift(...items);}
    replaceChildren(...items){this.children=items;}
    setAttribute(k,v){this.attrs[k]=v;}
    removeAttribute(k){delete this.attrs[k];}
    addEventListener(k,fn,capture){(this.listeners[k]||=[]).push({fn,capture});}
    async emit(type,event={}){event.preventDefault ||= ()=>{event.defaultPrevented=true};event.stopImmediatePropagation ||= ()=>{event.stopped=true};
      for(const {fn} of [...(this.listeners[type]||[])].sort((a,b)=>!!b.capture-!!a.capture)){await fn(event);if(event.stopped)break;}}
    closest(){return card;}
    focus(){document.activeElement=this;}
    showModal(){this.open=true;}
    close(){this.open=false;}
    querySelector(){return null;}
    querySelectorAll(){return [];}
  }
  const card=new Element('card'),body=new Element('body');
  ['ai-alternatives-button','ai-criteria-button','ai-scores-button','ai-result-button','ai-decision-risks-button','saved-ai-analysis'].forEach(id=>new Element(id));
  nodes.get('saved-ai-analysis').textContent='{}';
  const table=new Element('matrix-scroll');table.scrollLeft=240;
  let form,fields=[],saveButton;
  if(matrix){form=new Element('matrix-form');form.action='https://preview.test'+path+'/scores';form.reportValidity=()=>true;
    saveButton=new Element('save');fields=Array.from({length:100},(_,i)=>{const field=new Element('score_'+(Math.floor(i/10)+1)+'_'+(i%10+1));field.value='7';return field;});
    form.elements={matrix_revision:{value:'0'},request_key:{value:''},namedItem:id=>nodes.get(id)};
    form.querySelector=()=>saveButton;form.querySelectorAll=()=>fields;new Element('matrix-save-status');}
  const document={body,activeElement:nodes.get('ai-result-button'),getElementById:id=>nodes.get(id)||null,
    createElement:()=>new Element(),createTextNode:text=>({textContent:text}),querySelector:()=>null,
    querySelectorAll:selector=>selector==='.table-responsive'?[table]:[],
    addEventListener:(type,fn)=>{if(type==='DOMContentLoaded')domReady.push(fn);}};
  const location={pathname:path,href:'https://preview.test'+path,origin:'https://preview.test',reload:()=>reloads++};
  const context={document,location,URL,Headers,Response,AbortController,crypto:require('node:crypto').webcrypto,
    FormData:class {constructor(f){this.values=f.elements;this.fields=fields;}},
    setTimeout,clearTimeout,scrollX:0,scrollY:800,requestAnimationFrame:fn=>fn(),
    performance:{getEntriesByType:()=>[{type:navigation}]},sessionStorage:{getItem:k=>stored.get(k)||null,setItem:(k,v)=>stored.set(k,v),removeItem:k=>stored.delete(k)},
    fetch:async(input,opts)=>{calls.push({input,opts});return handler(input,opts);},
    scrollTo:(x,y)=>scrolls.push([x,y]),addEventListener:(type,fn)=>windowEvents[type]=fn};
  context.window=context;vm.createContext(context);vm.runInContext(code,context);domReady.forEach(fn=>fn());
  return {context,nodes,card,calls,stored,scrolls,fields,form,saveButton,get reloads(){return reloads;},setHandler:fn=>handler=fn};
}
async function main(){
  // Slow AI: immediate busy state, hide/reopen is not a second call; double submission rejected.
  let done;const e=environment();e.setHandler(()=>new Promise(resolve=>done=resolve));
  const path='/projects/1/ai/result-explanation';
  const pending=e.context.fetch(path,{method:'POST'});
  assert.equal(e.nodes.get('ai-result-button').disabled,true);
  const dialog=e.context.document.body.children[0];assert.equal(dialog.open,true);
  await e.nodes.get('analysis-hide').emit('click');assert.equal(dialog.open,false);
  const reopen=e.card.children[0].children.find(c=>c.textContent==='Показать состояние');
  await reopen.emit('click');assert.equal(dialog.open,true);assert.equal(e.calls.length,1);
  const duplicate=await e.context.fetch(path,{method:'POST'});assert.equal(duplicate.status,409);assert.equal(e.calls.length,1);
  done(json({status:'ok',summary:'Done'}));await pending;
  assert.equal(e.nodes.get('ai-result-button').disabled,false);assert.equal(dialog.open,false);
  assert.equal(e.stored.has('dmatrix-operation:'+path),false);

  // Unknown network outcome: status checks only, then a separately initiated retry after confirmed failure.
  const u=environment();u.setHandler(async()=>{throw Error('disconnect');});
  await u.context.fetch(path,{method:'POST'});assert.equal(u.nodes.get('ai-result-button').disabled,false);
  u.setHandler(async()=>json({status:'uncertain',message:'Waiting'}));
  await u.nodes.get('ai-result-button').emit('click');assert.equal(u.calls.filter(c=>c.opts?.method==='POST').length,1);
  assert.match(String(u.calls.at(-1).input),/\/operations\//);
  u.setHandler(async()=>json({status:'failed',message:'Ended'}));await u.nodes.get('analysis-check').emit('click');
  u.setHandler(async()=>json({status:'ok',summary:'Retry'}));await u.context.fetch(path,{method:'POST'});
  assert.equal(u.calls.filter(c=>c.opts?.method==='POST').length,2);

  const batch=environment();batch.setHandler(async()=>json({status:'in_progress',message:'20 / 100',completed:20,total:100}));
  await batch.context.fetch('/projects/1/ai/scores',{method:'POST'});
  assert.equal(batch.nodes.get('ai-scores-button').disabled,true);
  batch.setHandler(async()=>json({status:'ok',completed:100,total:100}));
  await batch.context.fetch('/projects/1/ai/scores',{method:'POST'});
  assert.equal(batch.nodes.get('ai-scores-button').disabled,false);

  // Scroll data is per path, includes horizontal position and focus, and skips history traversal.
  e.context.dmatrixReload();const position=JSON.parse(e.stored.get('dmatrix-position:/projects/1'));
  assert.equal(position.y,800);assert.equal(position.horizontal[0][1],240);
  const restored=environment({stored:new Map(e.stored)});assert.deepEqual(restored.scrolls,[[0,800]]);
  assert.equal(environment({path:'/projects/2',stored:new Map(e.stored)}).scrolls.length,0);
  assert.equal(environment({stored:new Map(e.stored),navigation:'back_forward'}).scrolls.length,0);

  // Save holds all 100 inputs in place, allows only one POST and restores controls on errors.
  const m=environment({matrix:true});let finish;m.setHandler(()=>new Promise(resolve=>finish=resolve));
  const saving=m.form.emit('submit');assert.equal(m.saveButton.disabled,true);assert.equal(m.fields[0].readOnly,true);
  await m.form.emit('submit');assert.equal(m.calls.length,1);assert.equal(m.calls[0].opts.body.fields.length,100);
  finish(json({message:'Invalid value',field:'score_1_1'},422));await saving;
  assert.equal(m.saveButton.disabled,false);assert.equal(m.fields[0].readOnly,false);assert.equal(m.fields[0].value,'7');
  assert.equal(m.context.document.activeElement.id,'score_1_1');assert.equal(m.reloads,0);
  m.setHandler(async()=>json({status:'ok',matrix_revision:1}));await m.form.emit('submit');assert.equal(m.reloads,1);
  assert.equal(m.calls.filter(c=>String(c.input).includes('/ai/')).length,0);

  // Failed connection and edited input cannot replay an old save ID or discard edits on status recovery.
  const v=environment({matrix:true});v.setHandler(async()=>{throw Error('offline');});await v.form.emit('submit');
  v.fields[0].value='8';await v.fields[0].emit('input');assert.equal(v.saveButton.disabled,false);
  v.setHandler(async()=>json({status:'saved',matrix_revision:1}));await v.form.emit('submit');
  assert.equal(v.calls.filter(c=>c.opts?.method==='POST').length,1);assert.equal(v.reloads,0);assert.equal(v.fields[0].value,'8');
  console.log('Operation DOM contracts passed (not real browser layout).');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
