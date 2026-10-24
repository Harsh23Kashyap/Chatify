// Behavioral harness for the workspace review Confirm flow (workspace.js).
// Runs the real workspace.js against a stub DOM + scripted fetch; no browser.
// Usage: node workspace_review_confirm_harness.cjs <consent-gate|confirm-once|failure-retry|no-zombies>
const fs=require('fs'),path=require('path'),assert=require('node:assert/strict');
const scenario=process.argv[2]||'consent-gate';
const calls=[];let removeN=0;
let attachedSeq=0;
function mkNode(tag){const n={tagName:(tag||'').toUpperCase(),children:[],parent:null,_text:'',className:'',attrs:{},style:{},dataset:{},disabled:false,hidden:false,checked:false,value:'',type:'',href:'',attached:false,_id:++attachedSeq,
 listeners:{},onclick:null,onchange:null,
 append(...cs){for(const c of cs){c.parent=n;c.attached=true;n.children.push(c);markAttached(c)}},
 appendChild(c){n.append(c)},
 replaceChildren(...cs){for(const c of n.children)markDetached(c);n.children=[];n.append(...cs)},
 remove(){if(n.parent){const i=n.parent.children.indexOf(n);if(i>=0)n.parent.children.splice(i,1)}markDetached(n)},
 setAttribute(k,v){n.attrs[k]=String(v)},getAttribute(k){return n.attrs[k]??null},removeAttribute(k){delete n.attrs[k]},
 addEventListener(t,f){n.listeners[t]=f},removeEventListener(t){delete n.listeners[t]},
 click(){if(n.onclick)return n.onclick();if(n.listeners.click)return n.listeners.click()},
 focus(){},blur(){},scrollIntoView(){},
 classList:{_s:new Set(),add(c){this._s.add(c)},remove(c){this._s.delete(c)},contains(c){return this._s.has(c)},toggle(c){this._s.has(c)?this._s.delete(c):this._s.add(c)}},
 querySelector(sel){return n.querySelectorAll(sel)[0]||null},
 querySelectorAll(sel){const out=[];walk(n,c=>{if(matches(c,sel))out.push(c)});return out},
 get isConnected(){let p=n;while(p.parent)p=p.parent;return p===DOCROOT},
 get textContent(){return n._text+n.children.map(c=>c.textContent).join('')},
 set textContent(v){n._text=String(v);for(const c of n.children)markDetached(c);n.children=[]},
};return n}
function markDetached(n){n.attached=false;n.parent=null;for(const c of n.children)markDetached(c)}
function markAttached(n){n.attached=true;for(const c of n.children){c.parent=n;markAttached(c)}}
function walk(n,f){for(const c of [...n.children]){f(c);walk(c,f)}}
function matches(n,sel){if(sel.startsWith('.'))return String(n.className).split(/\s+/).includes(sel.slice(1));return n.tagName===sel.toUpperCase()}
const DOCROOT=mkNode('html');DOCROOT.attached=true;
const panel=mkNode('div');panel.attrs.id='workspacePanel';DOCROOT.append(panel);
const docListeners={};
global.window=global;
global.document={getElementById:id=>id==='workspacePanel'?panel:null,
 createElement:t=>mkNode(t),createTextNode:t=>{const n=mkNode('#text');n._text=String(t);return n},
 querySelector:s=>DOCROOT.querySelector(s),querySelectorAll:s=>DOCROOT.querySelectorAll(s),
 addEventListener(t,f){docListeners[t]=f},removeEventListener(t){delete docListeners[t]},
 body:mkNode('body'),documentElement:DOCROOT,activeElement:null,hidden:false,visibilityState:'visible'};
global.addEventListener=()=>{};global.removeEventListener=()=>{};
global.localStorage={getItem:()=>null,setItem(){},removeItem(){}};
global.sessionStorage={getItem:()=>null,setItem(){},removeItem(){}};
global.location={href:'',hash:'',reload(){}};
global.history={replaceState(){},pushState(){}};
global.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});
global.requestAnimationFrame=f=>setTimeout(f,0);
global.scrollTo=()=>{};global.scrollX=0;global.scrollY=0;
global.navigator={clipboard:{writeText:async()=>{}}};
global.URL={createObjectURL:()=>'blob:x',revokeObjectURL(){}};
global.Blob=class{};
function respond(ok,payload,status){return{ok,status:status||(ok?200:400),json:async()=>payload,text:async()=>JSON.stringify(payload)};}
const wsList=()=>({workspaces:scenario==='no-zombies'
 ?[{id:'nerd-aaa111',title:'First WS',running:false,url:''},{id:'nerd-bbb222',title:'Second WS',running:false,url:''}]
 :removeN>0?[]:[{id:'nerd-aaa111',title:'Test WS',running:false,url:''}]});
global.fetch=async(url,opts={})=>{
 const method=opts.method||(opts.body?'POST':'GET');
 const body=opts.body?JSON.parse(opts.body):undefined;
 calls.push({url:String(url),method,body});
 const u=String(url);
 if(u.endsWith('/api/settings'))return respond(true,{can_edit:true});
 if(u.endsWith('/api/workspace/status'))return respond(true,{rows:[]});
 if(u.endsWith('/api/nerds')&&method==='GET')return respond(true,wsList());
 if(u.endsWith('/api/nerds/remove')){removeN++;
  if(scenario==='failure-retry'&&removeN===1)return respond(false,{error:'Workspace still running. Stop it first.'},409);
  return respond(true,{removed:true});}
 return respond(true,{});
};
const flush=async()=>{for(let i=0;i<8;i++)await new Promise(r=>setImmediate(r));};
const SRC=fs.readFileSync(path.join(__dirname,'..','chatify','web','workspace.js'),'utf8');
function allNodes(){const out=[];walk(DOCROOT,n=>out.push(n));return out}
function findButtons(){return allNodes().filter(n=>n.tagName==='BUTTON')}
function reviewBoxes(){return DOCROOT.querySelectorAll('.workspace-review')}
async function openWorkspace(){
 assert(docListeners['cc-workspace-open'],'workspace open listener registered');
 docListeners['cc-workspace-open']({detail:'Workspace'});await flush();
}
async function clickRemove(which=0){
 const btns=findButtons().filter(b=>/^Remove .+…$/.test(b.textContent));
 assert(btns.length>which,'Remove button present');
 await btns[which].click();await flush();
}
function consentAndGo(){
 const boxes=reviewBoxes();assert.equal(boxes.length,1,'exactly one review panel');
 const box=boxes[0];
 const consent=box.querySelectorAll('INPUT').find(n=>n.type==='checkbox');
 assert(consent,'consent checkbox present');
 const go=findButtons().filter(b=>b.textContent==='Confirm').pop();
 assert(go,'Confirm button present');
 const err=box.querySelectorAll('P').find(n=>n.attrs.role==='alert');
 assert(err,'alert slot present');
 return{box,consent,go,err};
}
(async()=>{
 eval(SRC);await flush(); // boot: /api/settings -> open('Setup')
 calls.length=0;
 await openWorkspace();
 if(scenario==='consent-gate'){
  await clickRemove();
  const{consent,go}=consentAndGo();
  assert.equal(go.disabled,true,'Confirm disabled before consent');
  await go.click();await flush();
  assert.equal(calls.filter(c=>c.url.endsWith('/api/nerds/remove')).length,0,'no remove request without consent');
  assert.equal(consent.checked,false);
  console.log('PASS consent-gate: Confirm without consent fired zero requests, button stayed disabled-guarded');
 }else if(scenario==='confirm-once'){
  await clickRemove();
  const{box,consent,go}=consentAndGo();
  consent.checked=true;consent.onchange();
  assert.equal(go.disabled,false,'consent enables Confirm');
  await go.click();await flush();
  const removes=calls.filter(c=>c.url.endsWith('/api/nerds/remove'));
  assert.equal(removes.length,1,'exactly one remove request');
  assert.deepEqual(removes[0].body,{id:'nerd-aaa111',confirmed:true});
  assert.equal(reviewBoxes().length,0,'panel closed after success');
  console.log('PASS confirm-once: consent -> exactly one confirmed remove, panel closed');
 }else if(scenario==='failure-retry'){
  await clickRemove();
  const{box,consent,go,err}=consentAndGo();
  consent.checked=true;consent.onchange();
  await go.click();await flush();
  assert.equal(calls.filter(c=>c.url.endsWith('/api/nerds/remove')).length,1);
  assert.equal(err.textContent,'Workspace still running. Stop it first.','server error shown in alert slot');
  assert.equal(go.textContent,'Confirm','label restored after failure');
  assert.equal(go.disabled,false,'re-enabled for retry');
  assert.equal(reviewBoxes().length,1,'panel kept open after failure');
  await go.click();await flush();
  assert.equal(calls.filter(c=>c.url.endsWith('/api/nerds/remove')).length,2,'retry fired exactly one more request');
  assert.equal(reviewBoxes().length,0,'panel closed after retry success');
  console.log('PASS failure-retry: error visible, label restored, retry fired exactly one more request');
 }else if(scenario==='no-zombies'){
  await clickRemove(0);
  assert.equal(reviewBoxes().length,1);
  await clickRemove(1);
  assert.equal(reviewBoxes().length,1,'second review replaces the first - no stacked panels');
  console.log('PASS no-zombies: repeated reviews leave exactly one panel');
 }else{throw new Error('unknown scenario '+scenario)}
})().catch(e=>{console.error(e);process.exit(1)});
