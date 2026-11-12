const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-model');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
await p.locator('.seg button[data-p=openai]').click();
await p.waitForTimeout(300);
// The key field never shows what is typed
assert.equal(await p.locator('#apikey').getAttribute('type'),'password','key field is masked');
const KEY='sk-test-PLACEHOLDER-1234567890abcdef';
await p.locator('#apikey').fill(KEY);
await p.locator('#keysave').click();
await p.waitForFunction(()=>/Key saved privately/.test(document.querySelector('#msg')?.textContent||''),{timeout:10000});
assert.equal(await p.locator('#apikey').inputValue(),'','field clears after save');
assert.match(await p.locator('#apikey').getAttribute('placeholder'),/Saved key available/,'placeholder admits a saved key without showing it');
assert.ok(await p.locator('#keyclear').isVisible(),'clear offered once a key exists');
// No API response may echo the key material back
const status=await p.evaluate(async()=>JSON.stringify(await (await fetch('/api/provider/status')).json()));
assert.ok(!status.includes(KEY),'provider status never returns the key');
assert.ok(JSON.parse(status).keys.openai.has,'status records a saved openai key');
const settingsBody=await p.evaluate(async()=>{const r=await fetch('/api/settings');return r.text()});
assert.ok(!settingsBody.includes(KEY),'settings payload never returns the key');
// Clearing removes it and restores the paste prompt
await p.locator('#keyclear').click();
await p.waitForFunction(()=>/Key removed/.test(document.querySelector('#msg')?.textContent||''),{timeout:10000});
const after=await p.evaluate(async()=>JSON.stringify(await (await fetch('/api/provider/status')).json()));
assert.ok(!JSON.parse(after).keys.openai.has,'key is gone after clear');
assert.match(await p.locator('#apikey').getAttribute('placeholder'),/Paste a key/,'paste prompt restored');
const more=p.locator('#seg .chipmore');if(await more.isVisible())await more.click();
await p.locator('.seg button[data-p=mock]').click();
await b.close();console.log('PASS api keys: masked entry, save clears the field, status reports presence without material, clear removes and restores the prompt')})().catch(e=>{console.error(e);process.exit(1)});
