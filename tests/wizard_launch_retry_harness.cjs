// Behavioral harness for the guided wizard's save-and-start retry (build.js).
// Runs build.js with a stub DOM + scripted fetch; no browser or network needed.
// Usage: node wizard_launch_retry_harness.cjs <retry-ticket|expired-review>
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const scenario=process.argv[2]||'retry-ticket';
const calls=[];let saveN=0;
const elements=new Map();
function mkEl(sel){return{sel,listeners:{},children:[],hidden:false,disabled:false,textContent:'',innerText:'',href:'',value:'',open:false,style:{},dataset:{},className:'',
 addEventListener(t,f){this.listeners[t]=f},removeEventListener(){},append(...c){this.children.push(...c)},replaceChildren(...c){this.children=c},appendChild(c){this.children.push(c)},
 setAttribute(){},removeAttribute(){},getAttribute(){return null},classList:{add(){},remove(){},toggle(){},contains(){return false}},querySelector(){return mkEl('q')},querySelectorAll(){return[]},
 click(){},focus(){},blur(){},scrollIntoView(){},closest(){return null},remove(){},dispatchEvent(){return true}};}
function qs(sel){if(!elements.has(sel))elements.set(sel,mkEl(sel));return elements.get(sel);}
global.window=global;
global.addEventListener=()=>{};
global.removeEventListener=()=>{};
global.document={getElementById:()=>null,querySelector:qs,querySelectorAll:()=>[],createElement:t=>mkEl(t),addEventListener(){},removeEventListener(){},body:mkEl('body'),documentElement:mkEl('html'),hidden:false,visibilityState:'visible'};
global.localStorage={getItem:()=>null,setItem(){},removeItem(){}};
global.sessionStorage={_d:{},getItem(k){return this._d[k]||null},setItem(k,v){this._d[k]=v},removeItem(k){delete this._d[k]}};
global.location={href:'',hash:'',reload(){}};
global.history={replaceState(){},pushState(){}};
global.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});
global.requestAnimationFrame=f=>setTimeout(f,0);
global.navigator={clipboard:{writeText:async()=>{}}};
function respond(ok,payload,status){return{ok,status:status||(ok?200:400),json:async()=>payload,text:async()=>JSON.stringify(payload)};}
global.fetch=async(url,opts={})=>{
 const body=opts.body?JSON.parse(opts.body):{};
 calls.push({url:String(url),body});
 if(!String(url).includes('/api/settings/build/'))return respond(true,{});
 const ep=String(url).split('/api/settings/build/')[1];
 if(scenario==='retry-ticket'){
  if(ep==='save')return respond(true,{launch_ticket:'L1'});
  if(ep==='launch'&&body.ticket==='L1')return respond(false,{error:'Preview could not start',retry_ticket:'L2'});
  if(ep==='launch'&&body.ticket==='L2')return respond(true,{workspace:'ws-1',title:'Garden',url:'/w/ws-1/'});
  return respond(false,{error:'unexpected '+ep});
 }
 if(scenario==='expired-review'){
  if(ep==='save'){saveN++;if(saveN===1)return respond(false,{error:'Review expired or unavailable'});}
  if(ep==='review')return respond(true,{ticket:'R2',config:{app:{title:'Garden'}}});
  if(ep==='save')return respond(true,{launch_ticket:'L3'});
  if(ep==='launch'&&body.ticket==='L3')return respond(true,{workspace:'ws-2',title:'Garden',url:'/w/ws-2/'});
  return respond(false,{error:'unexpected '+ep});
 }
 throw new Error('unknown scenario');
};
const src=fs.readFileSync(path.join(__dirname,'..','chatify','web','build.js'),'utf8');
eval(src);
(async()=>{
 const save=qs('#reviewSave');assert(save.listeners.click,'wizard save button handler registered');
 await save.listeners.click();
 if(scenario==='retry-ticket'){
  const eps=calls.map(c=>c.url.split('/api/settings/build/')[1]);
  assert.deepEqual(eps.slice(0,2),['save','launch'],'save then first launch attempt');
  assert.equal(calls[1].body.ticket,'L1');
  const err=qs('#reviewError');
  assert.equal(err.hidden,false,'error surfaced after failed start');
  assert(err.textContent.includes('retry starting'),'retry guidance shown: '+err.textContent);
  await save.listeners.click();
  const launches=calls.filter(c=>c.url.endsWith('/launch'));
  assert.equal(launches.length,2,'second click retries the start, not the save');
  assert.equal(launches[1].body.ticket,'L2','retry uses the server re-issued ticket');
  assert.equal(calls.filter(c=>c.url.endsWith('/save')).length,1,'no second save with a consumed review ticket');
  assert(qs('#yourappTitle').textContent.includes('is running'),'app shown running after retry');
  assert(sessionStorage._d.cc_build_ws.includes('ws-1'),'workspace persisted for restore');
 }
 if(scenario==='expired-review'){
  const eps=calls.map(c=>c.url.split('/api/settings/build/')[1]);
  assert.deepEqual(eps,['save','review','save','launch'],'expired review ticket re-reviews once then saves and starts');
  assert.equal(calls[2].body.ticket,'R2','second save uses the fresh review ticket');
  assert(qs('#yourappTitle').textContent.includes('is running'),'app shown running after recovery');
 }
 console.log('PASS',scenario,calls.map(c=>c.url.split('/').pop()+'('+(c.body.ticket||'')+')').join(' '));
})().catch(e=>{console.error(e);process.exit(1)});
