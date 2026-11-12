const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const url=process.env.CHATIFY_TEST_URL+'/settings.html#sec-model';
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(url);await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
// Mock provider hides temperature (offline demo), sources-per-answer stays editable
assert.ok(await p.locator('#temp').isHidden(),'temperature hidden for the offline mock provider');
assert.ok(await p.locator('#topk').isVisible(),'sources-per-answer slider visible');
const before=await p.locator('#topk').inputValue();
const target=before==='20'?'18':'20';
await p.locator('#topk').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))},target);
assert.equal(await p.locator('#kv').innerText(),target,'output follows the slider');
assert.match(await p.locator('#answerDirty').innerText(),/Unsaved answer changes/,'dirty hint appears before saving');
await p.locator('#apply').click();
await p.waitForFunction(()=>/Applied|saved/i.test(document.querySelector('#msg')?.textContent||''),{timeout:10000});
await p.reload();await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
assert.equal(await p.locator('#topk').inputValue(),target,'slider choice persists across reload');
// restore the fixture default so reruns stay symmetric
await p.locator('#topk').evaluate((el,v)=>{el.value=v;el.dispatchEvent(new Event('input',{bubbles:true}));el.dispatchEvent(new Event('change',{bubbles:true}))},before);
await p.locator('#apply').click();
await p.waitForFunction(()=>/Applied|saved/i.test(document.querySelector('#msg')?.textContent||''),{timeout:10000});
await b.close();console.log('PASS sliders: mock hides temperature, sources slider updates its output, saves through Apply and persists across reload')})().catch(e=>{console.error(e);process.exit(1)});
