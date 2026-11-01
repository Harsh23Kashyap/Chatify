const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 try{for(const reducedMotion of ['no-preference','reduce']){
  const page=await browser.newPage({viewport:{width:1280,height:950},reducedMotion});
  await page.addInitScript(()=>localStorage.setItem('cc_tour','1'));
  await page.route('**/api/chats*',r=>r.fulfill({json:[]}));
  const rows=[{n:1,id:'doi:10.1201/9781351114585-6',title:'Soil sampling for soil health assessment',text:'Soil sampling for soil health assessment',year:'2018',source:'crossref',url:'https://doi.org/10.1201/9781351114585-6',content_kind:'title_only'},{n:2,id:'short-abstract',title:'Short abstract control',text:'Soil testing.',year:'2026',source:'crossref'}];
  await page.route('**/api/ask-stream',r=>r.fulfill({contentType:'application/x-ndjson',body:JSON.stringify({type:'done',data:{id:'fixture',chat:'fixture',question:'Soil health',answer:'Reference titles shown, not study findings [1] [2].',evidence:rows,answer_verified:false}})+'\n'}));
  await page.goto(process.env.CHATIFY_TEST_URL+'/');await page.locator('.playground-question').first().waitFor();
  await page.locator('#q').fill('Soil health');await page.locator('#send').click();
  await page.locator('.srcs .s').first().waitFor();
  assert.match(await page.locator('.srcs .s').nth(0).innerText(),/Title only; no abstract or article text/);
  assert(!/Title only/.test(await page.locator('.srcs .s').nth(1).innerText()));
  await page.locator('.srcs .s').first().click();
  assert.match(await page.locator('#sources .src').nth(0).innerText(),/Title only; no abstract or article text/);
  assert(!/Title only/.test(await page.locator('#sources .src').nth(1).innerText()));
  assert.equal(await page.locator('#sources .src a').first().getAttribute('href'),rows[0].url);
  assert((await page.locator('#sources .src').nth(1).innerText()).includes('Soil testing.'));
  await page.waitForFunction(()=>!document.getAnimations().some(a=>a.playState==='running'&&a.effect?.getTiming().iterations!==Infinity));
  await page.screenshot({path:'/downloads/crossref-title-provenance-'+reducedMotion+'.png'});await page.close();
 }}finally{await browser.close()}
 console.log('PASS Crossref captured title-only provenance card/drawer and short abstract negative control, desktop normal/reduced motion; fixture only');
})().catch(e=>{console.error(e);process.exit(1)});
