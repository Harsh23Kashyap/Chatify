/* Failure-only diagnostics for synthetic, offline regression pages. Never use on user sessions. */
const fs=require('node:fs'),path=require('node:path');
async function captureFixtureFailure(page,name,context={}){
 if(!process.env.CI_CASE||!process.env.CHATIFY_TEST_URL)return;
 try{
  const root=new URL(process.env.CHATIFY_TEST_URL),current=new URL(page.url());
  if(!['127.0.0.1','localhost'].includes(root.hostname)||root.origin!==current.origin)return;
  const dir='/downloads/chatify-ci-failures';fs.mkdirSync(dir,{recursive:true});
  const base=path.join(dir,name.replace(/[^a-zA-Z0-9_-]/g,'_'));
  const geometry=await page.evaluate(()=>{
   const rect=e=>{if(!e)return null;const r=e.getBoundingClientRect(),s=getComputedStyle(e);return {x:r.x,y:r.y,width:r.width,height:r.height,scrollTop:e.scrollTop,scrollHeight:e.scrollHeight,clientHeight:e.clientHeight,display:s.display,visibility:s.visibility,opacity:s.opacity,transform:s.transform,fontFamily:s.fontFamily,fontSize:s.fontSize,lineHeight:s.lineHeight,animationName:s.animationName,animationDuration:s.animationDuration}};
   const dialog=document.querySelector('dialog.app-builder');const entry=document.querySelector('.app-builder-open');const r=entry?.getBoundingClientRect();
   return {viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},fonts:{status:document.fonts?.status},motion:{reduced:matchMedia('(prefers-reduced-motion:reduce)').matches,level:document.documentElement.dataset.motion},focus:{tag:document.activeElement?.tagName,id:document.activeElement?.id},dialog:{open:dialog?.open,className:dialog?.className,rect:rect(dialog)},entry:rect(entry),entryCenterStack:r?[...document.elementsFromPoint(r.x+r.width/2,r.y+r.height/2)].slice(0,8).map(e=>({tag:e.tagName,id:e.id,className:String(e.className)})):[],thread:rect(document.querySelector('#thread')),live:rect(document.querySelector('#live')),thinking:rect(document.querySelector('#think')),pipelineStatus:rect(document.querySelector('#pipelineStatus')),activeEditor:rect(document.activeElement?.closest('.cm-editor')),activeScroller:rect(document.activeElement?.closest('.cm-scroller')),selectionRects:getSelection()?.rangeCount?[...getSelection().getRangeAt(0).getClientRects()].map(r=>({x:r.x,y:r.y,width:r.width,height:r.height,top:r.top,bottom:r.bottom})):[],recentPointerTargets:window.fixturePointerTargets||[],animations:document.getAnimations().slice(0,24).map(a=>({target:a.effect?.target?.id||String(a.effect?.target?.className||''),playState:a.playState,currentTime:a.currentTime,timing:a.effect?.getComputedTiming()}))};
  });
  fs.writeFileSync(base+'.json',JSON.stringify({case:process.env.CI_CASE,name,context,geometry},null,2));
  await page.screenshot({path:base+'.png'});
  console.error('OFFLINE_FAILURE_CAPTURE '+name);
 }catch(error){console.error('OFFLINE_FAILURE_CAPTURE_ERROR '+error.name+': '+error.message)}
}
module.exports={captureFixtureFailure};
