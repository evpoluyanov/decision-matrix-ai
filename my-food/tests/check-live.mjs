// Check the live Cloudflare model's response, not a static fixture.
import fs from 'node:fs';
const file=process.argv[2],mode=process.argv[3]||'multi';
const data=JSON.parse(fs.readFileSync(file,'utf8'));
const d=data.food?.dishes||[];
const perGood=x=>x&&['k','p','f','c'].every(k=>Number.isFinite(x[k])&&x[k]>=0);
const good=x=>x.mode==='ingredients'?[...(x.items||[]),...(x.additions||[])].length>0 && [...(x.items||[]),...(x.additions||[])].every(z=>z.weight_g>0&&perGood(z.per100)):
 (x.mode==='whole'&&Number(x.weight_g??x.main_weight_g)>0&&perGood(x.per100));
if(!data.ok||!d.length||!d.every(good)){
 console.error('AI per100 contract failed',JSON.stringify({ok:data.ok,stage:data.stage,message:data.message,dishes:d,missing:data.missing}).slice(0,2200));
 process.exit(1);
}
const n=x=>String(x||'').toLowerCase().replaceAll('ё','е');
if(mode==='multi'){
 const find=regex=>d.find(z=>regex.test(n(z.name)));
 const egg=find(/яйц/),liver=find(/печен.*треск/),sauce=find(/тартар/);
 if(d.length!==3||!egg||!liver||!sauce||(liver.weight_g??liver.main_weight_g)!==20||(sauce.weight_g??sauce.main_weight_g)!==10){
  console.error('Independent dishes incomplete',d.map(z=>({name:z.name,weight:z.weight_g,mode:z.mode})));process.exit(1);
 }
}else if(mode==='composite'){
 if(d.length!==1){console.error('Expected one composite dish',d.map(x=>x.name));process.exit(1);}
 if(d[0].mode==='ingredients'){
  const rows=[...(d[0].items||[]),...(d[0].additions||[])];
  const names=rows.map(z=>n(z.name));
  if(![/блин/,/творож|сыр/,/семг/].every(re=>names.some(x=>re.test(x)))){
   console.error('Missing recipe component',names);process.exit(1);
  }
 }
}
console.log('PASS: real AI returned per-100g nutrition',d.map(z=>({name:z.name,mode:z.mode,grams:z.weight_g??z.main_weight_g,per100:z.per100||z.items?.map(i=>[i.name,i.per100])})));
