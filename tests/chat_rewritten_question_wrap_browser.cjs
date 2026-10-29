const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const chrome=process.env.CHROME_BIN||'/usr/bin/google-chrome';
 const browser=await chromium.launch({headless:true,...(require('fs').existsSync(chrome)?{executablePath:chrome}:{})});
 try{for(const width of [390,1280]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});
  await page.addInitScript(()=>localStorage.setItem('cc_tour','1'));
  const rewritten='Explain the previous answer more simply while keeping the randomized-trial and observational evidence comparison, all study populations and evidence limitations, using exactly the same cited sources. '+('UnbrokenIdentifier'.repeat(12));
  const turn={id:'wrap-test',chat:'wrap-chat',topic:'wrap-topic',question:'Explain that more simply',standalone:rewritten,answer:'A supported answer. [1]',evidence:[{n:1,title:'Evidence record',text:'A supported answer.',source:'fixture'}],ledger:[]};
  await page.route('**/api/chats*',r=>r.fulfill({json:[]}));
  await page.route('**/api/ask-stream',r=>r.fulfill({contentType:'application/x-ndjson',body:JSON.stringify({type:'done',data:turn})+'\n'}));
  await page.goto(process.env.CHATIFY_TEST_URL||'http://127.0.0.1:8145');
  await page.locator('#q').fill(turn.question);await page.locator('#send').click();
  const chip=page.locator('.understood-as');await chip.waitFor();await chip.scrollIntoViewIfNeeded();
  const state=await chip.evaluate(n=>({text:n.textContent,scroll:n.scrollWidth,client:n.clientWidth,rect:n.getBoundingClientRect().toJSON(),thread:n.closest('#thread').getBoundingClientRect().toJSON()}));
  assert(state.text.includes(rewritten));assert(state.scroll<=state.client+1);
  assert(state.rect.x>=state.thread.x-1&&state.rect.right<=state.thread.right+1);
  assert.equal(await page.locator('.meta .copy').innerText(),'Copy');
  await page.screenshot({path:'/downloads/chatify-rewrite-regression-'+width+'.png',fullPage:true});
  await page.close();console.log('PASS rewritten-question wrapping',width);
 }}finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
