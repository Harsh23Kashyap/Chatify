const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const url=process.env.CHATIFY_TEST_URL+'/settings.html';
const ready=p=>p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
// Fresh visitor: Build with AI is the default view
let p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(url);await ready(p);
assert.equal(await p.locator('#cfgtop [data-t=builder]').getAttribute('aria-current'),'page','builder is the default view');
assert.ok(await p.locator('.builder-hero').isVisible(),'builder hero visible by default');
assert.ok(!(await p.locator('.modebar').isVisible()),'manual controls hidden by default');
// Manual persists across reload
await p.locator('#cfgtop [data-t=manual]').click();
assert.ok(await p.locator('.modebar').isVisible(),'manual controls open');
assert.equal(await p.evaluate(()=>localStorage.getItem('cc_cfg_top_v1')),'manual','manual choice stored');
await p.reload();await ready(p);
assert.equal(await p.locator('#cfgtop [data-t=manual]').getAttribute('aria-current'),'page','manual restored after reload');
assert.ok(await p.locator('.modebar').isVisible(),'manual controls visible after reload');
// How-to persists across reload and keeps its walkthrough picker
await p.locator('#cfgtop [data-t=guide]').click();
assert.ok(await p.locator('#cfgWalkthrough').isVisible(),'how-to walkthrough visible');
const walkthroughs=await p.locator('.cfg-walkthrough-choice select option').allInnerTexts();
assert.ok(walkthroughs.length>=2,'walkthrough picker offers scenarios: '+walkthroughs.join(' | '));
assert.equal(await p.locator('#cfgWalkthroughVideo').getAttribute('preload'),'none','walkthrough video does not preload');
await p.reload();await ready(p);
assert.ok(await p.locator('#cfgWalkthrough').isVisible(),'how-to restored after reload');
assert.equal(await p.locator('#cfgtop [data-t=guide]').getAttribute('aria-current'),'page','guide restored after reload');
// Switching the walkthrough swaps heading and video source
const firstSrc=await p.locator('#cfgWalkthroughVideo').getAttribute('src');
await p.locator('.cfg-walkthrough-choice select').evaluate(el=>{el.value=el.options[1].value;el.dispatchEvent(new Event('change',{bubbles:true}))});
await p.waitForTimeout(200);
assert.notEqual(await p.locator('#cfgWalkthroughVideo').getAttribute('src'),firstSrc,'walkthrough choice swaps the video');
await p.close();
// A #sec- deep link forces Manual, and leaving Manual clears the stale hash
p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_cfg_top_v1','builder')});
await p.goto(url+'#sec-presets');await ready(p);
assert.equal(await p.locator('#cfgtop [data-t=manual]').getAttribute('aria-current'),'page','sec- hash opens manual');
await p.locator('#cfgtop [data-t=builder]').click();
assert.equal(await p.evaluate(()=>location.hash),'','leaving manual clears the stale sec- hash');
assert.equal(await p.locator('#cfgtop [data-t=builder]').getAttribute('aria-current'),'page','builder active after clearing hash');
await p.close();
await b.close();console.log('PASS configuration views: builder default, manual/how-to persist across reloads, walkthrough picker swaps videos without preloading, sec- deep links force manual and stale hashes clear')})().catch(e=>{console.error(e);process.exit(1)});
