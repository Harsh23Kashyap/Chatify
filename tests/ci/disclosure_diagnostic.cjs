/* One diagnostic execution of the ORIGINAL assertions. Only failure context is added. */
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const original=path.resolve(__dirname,'../settings_disclosure_cue_audit_browser.cjs');
let source=fs.readFileSync(original,'utf8');
const timeline=`await s.evaluate(n=>{window.ccCueTrace=[];const record=(type,e)=>ccCueTrace.push({type,at:performance.now(),open:n.parentElement.open,transform:getComputedStyle(n,'::before').transform,property:e?.propertyName,pseudo:e?.pseudoElement,elapsed:e?.elapsedTime});for(const type of ['transitionrun','transitionstart','transitionend','transitioncancel'])n.addEventListener(type,e=>record(type,e));n.parentElement.addEventListener('toggle',()=>record('toggle'));record('registered');let frames=0;const sample=()=>{record('frame');if(++frames<30)requestAnimationFrame(sample)};requestAnimationFrame(sample)});`;
const marker="const pos=await s.boundingBox();";
if(!source.includes(marker))throw Error('Original diagnostic insertion marker changed');
source=source.replace(marker,marker+timeline);
source=source.replace("at:performance.now(),open:n.parentElement.open", "trace:window.ccCueTrace,at:performance.now(),open:n.parentElement.open");
process.env.CHATIFY_AUDIT_COMBO='320:no-preference';
const originalModule=new Module(original,module);originalModule.filename=original;originalModule.paths=Module._nodeModulePaths(path.dirname(original));
originalModule._compile(source,original);
