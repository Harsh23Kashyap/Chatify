const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-model');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
await p.evaluate(()=>window.CCSettingsSetMode?.('advanced'));
const baseLabel=p.locator('label:has(#base)');
// The demo provider has no server address to edit
assert.ok(await baseLabel.isHidden(),'base URL hidden for the offline demo');
// A local server exposes it
await p.locator('.seg button[data-p=ollama]').click();
await p.waitForTimeout(300);
assert.ok(await baseLabel.isVisible(),'base URL shown for a local Ollama server');
// So does a custom OpenAI-compatible server (nothing is saved by browsing)
await p.reload();await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
await p.evaluate(()=>window.CCSettingsSetMode?.('advanced'));
await p.locator('#seg .chipmore').click();
await p.locator('.seg button[data-p=openai_compatible]').click();
await p.waitForTimeout(300);
assert.ok(await baseLabel.isVisible(),'base URL shown for a custom OpenAI-compatible server');
assert.ok(await p.locator('#keybox').isVisible(),'custom servers can take a key');
// A reload confirms browsing never wrote anything
await p.reload();await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
assert.ok(await p.locator('label:has(#base)').isHidden(),'base URL hidden again for the demo');
const settings=(await p.evaluate(async()=>await (await fetch('/api/settings')).json())).settings;
assert.equal(settings.provider,'mock','no provider change was saved');
assert.ok(!settings.base_url,'no base URL was saved');
await b.close();console.log('PASS base URL: hidden for the demo, shown for local and custom servers, nothing written while browsing providers')})().catch(e=>{console.error(e);process.exit(1)});
