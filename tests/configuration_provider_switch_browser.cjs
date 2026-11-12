const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const url=process.env.CHATIFY_TEST_URL+'/settings.html#sec-model';
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(url);await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
const note=()=>p.locator('.simple-provider-note').innerText();
assert.match(await note(),/offline/i,'mock starts with the offline note');
assert.equal(await p.locator('.seg button[data-p=mock]').getAttribute('aria-checked'),'true','mock preselected');
const keyNeeded=()=>p.locator('#keybox').evaluate(el=>el.classList.contains('simple-key-needed'));
assert.ok(!(await keyNeeded()),'no key demanded for mock');
// Switch to a hosted provider: key is asked for, the choice is flagged unsaved, nothing is written yet
await p.locator('.seg button[data-p=openai]').click();
await p.waitForTimeout(300);
assert.equal(await p.locator('.seg button[data-p=openai]').getAttribute('aria-checked'),'true','openai selected');
assert.match(await note(),/not verified|Ready/i,'note reports the unverified hosted provider');
assert.ok(await keyNeeded(),'key entry offered for hosted provider');
assert.match(await p.locator('#answerDirty').innerText(),/Unsaved answer changes/,'switch is marked unsaved until Apply');
const saved=await p.evaluate(async()=>{const r=await fetch('/api/settings');return (await r.json()).settings||await r.json()});
assert.equal(saved.provider,'mock','server state still mock before Apply');
// Switching back restores the offline story without a save
if((await p.locator('.seg button[data-p=mock]').count())===0){await p.locator('#seg .chipmore').click();await p.waitForTimeout(200)}
await p.locator('.seg button[data-p=mock]').click();
await p.waitForTimeout(300);
assert.match(await note(),/offline/i,'mock note restored');
assert.ok(!(await keyNeeded()),'key entry withdrawn for mock');
await b.close();console.log('PASS provider switch: hosted provider asks for a key and marks unsaved changes without writing state, mock restores the offline story')})().catch(e=>{console.error(e);process.exit(1)});
