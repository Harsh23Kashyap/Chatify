const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
// The guide replays on demand from the toolbar
await p.locator('#configGuide').click();
const tour=p.locator('dialog.cc-tour');
await tour.waitFor();
assert.equal(await tour.getAttribute('aria-label'),'Configuration guide','guide is labelled');
assert.match(await p.locator('.cc-tour-count').innerText(),/1 \/ 13/,'starts at step 1 of 13');
assert.ok(await p.locator('.cc-tour-back').isDisabled(),'Back disabled on the first step');
await p.locator('.cc-tour-next').click();
assert.match(await p.locator('.cc-tour-count').innerText(),/2 \/ 13/,'Next advances');
assert.ok(await p.locator('.cc-tour-back').isEnabled(),'Back enabled after advancing');
await p.locator('.cc-tour-back').click();
assert.match(await p.locator('.cc-tour-count').innerText(),/1 \/ 13/,'Back returns');
// Arrow keys drive the same steps, Escape ends the guide
await p.keyboard.press('ArrowRight');
assert.match(await p.locator('.cc-tour-count').innerText(),/2 \/ 13/,'ArrowRight advances');
await p.keyboard.press('Escape');
assert.ok(await p.locator('dialog.cc-tour').count()===0,'Escape closes the guide');
assert.equal(await p.evaluate(()=>localStorage.getItem('cc_cfg_tour_v1')),'1','guide completion is remembered');
// A full pass ends with Done and leaves settings untouched
await p.locator('#configGuide').click();
await tour.waitFor();
for(let i=0;i<12;i++)await p.locator('.cc-tour-next').click();
assert.equal(await p.locator('.cc-tour-next').innerText(),'Done','last step offers Done');
await p.locator('.cc-tour-next').click();
assert.ok(await p.locator('dialog.cc-tour').count()===0,'Done closes the guide');
const settings=(await p.evaluate(async()=>await (await fetch('/api/settings')).json())).settings;
assert.equal(settings.provider,'mock','the guide never changes settings');
await b.close();console.log('PASS tour: replay opens the 13-step guide, buttons and arrow keys navigate, Escape/Done close, completion is remembered, settings untouched')})().catch(e=>{console.error(e);process.exit(1)});
