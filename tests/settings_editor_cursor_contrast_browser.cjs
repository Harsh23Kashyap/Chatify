const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({headless:true,executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 try{
  for(const motion of ['no-preference','reduce']){
   const page=await browser.newPage({viewport:{width:1280,height:900},reducedMotion:motion});
   await page.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_cfg_mode_v2','advanced')});
   await page.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-code');
   const editor=page.locator('#codeEditor .cm-content').first();
   await editor.waitFor();await editor.focus();await page.keyboard.insertText('cursor contrast fixture 123');
   await page.locator('#codeEditor .cm-cursor').first().waitFor({state:'attached'});
   const result=await editor.evaluate(n=>{
    const cursor=n.closest('.cm-editor').querySelector('.cm-cursor'),style=getComputedStyle(cursor),bg=getComputedStyle(n.closest('.cm-scroller')).backgroundColor;
    const rgb=s=>s.match(/[\d.]+/g).slice(0,3).map(Number),lum=s=>rgb(s).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
    const a=lum(style.borderLeftColor),b=lum(bg),r=cursor.getBoundingClientRect();
    return{color:style.borderLeftColor,background:bg,contrast:(Math.max(a,b)+.05)/(Math.min(a,b)+.05),width:r.width,height:r.height,borderWidth:parseFloat(style.borderLeftWidth),borderStyle:style.borderLeftStyle,text:n.textContent};
   });
   console.log(motion,result);
   assert(result.contrast>=4.5,'custom cursor must contrast with dark editor background');
   assert(result.borderWidth>0&&result.height>0&&result.borderStyle==='solid','custom cursor must be painted');
   assert(result.text.includes('cursor contrast fixture 123'),'typed text preserved');
   // Freeze the blink only for decisive screenshots, not for the style assertions.
   await page.addStyleTag({content:'.cm-cursorLayer{animation:none!important;visibility:visible!important}'});
   await page.locator('#codeEditor').screenshot({path:'/downloads/editor-cursor-contrast-'+motion+'.png'});
   await page.close();
  }
 }finally{await browser.close()}
 console.log('PASS custom CodeMirror cursor contrast at desktop normal and reduced motion');
})().catch(e=>{console.error(e);process.exit(1)});
