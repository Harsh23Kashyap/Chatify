const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true});try{
 for(const width of [390,1280]){const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});await page.addInitScript(()=>localStorage.setItem('cc_tour','1'));
 let refusal=true;
 await page.route('**/api/chats*',r=>r.fulfill({json:[]}));
 await page.route('**/api/ask-stream',r=>r.fulfill({contentType:'application/x-ndjson',body:JSON.stringify({type:'done',data:{id:'reason-test',chat:'reason-chat',question:refusal?'Personal dose?':'Missing research',answer:refusal?'Personal dosing cannot be provided.':'No matching research was found.',evidence:[],ledger:[],response_kind:refusal?'question_refused':'answer'}})+'\n'}));
 await page.goto(process.env.CHATIFY_TEST_URL||'http://127.0.0.1:8145');await page.locator('#q').fill('Personal dose?');await page.locator('#send').click();await page.locator('.nf-h').waitFor();
 assert.equal(await page.locator('.nf-h').last().innerText(),'Question not answered');assert.equal(await page.locator('.nf-tips').count(),0);
 await page.screenshot({path:'/downloads/chatify-refusal-contract-'+width+'.png',fullPage:true});
 refusal=false;await page.locator('#q').fill('Missing research');await page.locator('#send').click();await page.waitForFunction(()=>Array.from(document.querySelectorAll('.nf-h')).some(n=>n.textContent==='No evidence found'));
 assert.equal(await page.locator('.nf-h').last().innerText(),'No evidence found');assert.equal(await page.locator('.nf-tips button').count(),3);
 await page.close();console.log('PASS refusal distinct from empty retrieval',width);
 }
 }finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
