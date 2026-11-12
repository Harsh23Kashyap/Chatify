const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-model');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
await p.locator('.seg button[data-p=openai]').click();
await p.waitForTimeout(300);
// A hosted provider without a key cannot be tested
assert.ok(await p.locator('#testconn').isDisabled(),'test is blocked without a key');
assert.equal(await p.locator('#testconn').getAttribute('title'),'Save a key first, then test it','block is explained on the control');
assert.match(await p.locator('#testres').innerText(),/Save a key first/,'block is explained inline');
// Saving any key unblocks the test without leaving the page
await p.locator('#apikey').fill('sk-test-PLACEHOLDER-1234567890abcdef');
await p.locator('#keysave').click();
await p.waitForFunction(()=>/Key saved privately/.test(document.querySelector('#msg')?.textContent||''),{timeout:10000});
assert.ok(await p.locator('#testconn').isEnabled(),'test unblocks once a key exists');
assert.ok(!/Save a key first/.test(await p.locator('#testres').innerText()),'inline block clears');
// Tidy up: remove the key and restore the offline provider
await p.locator('#keyclear').click();
await p.waitForFunction(()=>/Key removed/.test(document.querySelector('#msg')?.textContent||''),{timeout:10000});
const more=p.locator('#seg .chipmore');if(await more.isVisible())await more.click();
await p.locator('.seg button[data-p=mock]').click();
await b.close();console.log('PASS test gating: hosted provider without a key blocks Test connection with explanations, saving a key unblocks it')})().catch(e=>{console.error(e);process.exit(1)});
