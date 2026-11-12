const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
await p.evaluate(()=>window.CCSettingsTop?.set('manual',false));
// Fresh visits start in the everyday view
assert.ok(await p.evaluate(()=>document.body.classList.contains('simple')),'starts simple');
assert.equal(await p.locator('#cfgmode button[data-m=simple]').getAttribute('aria-checked'),'true','simple radio is on');
assert.match(await p.locator('#modehelp').innerText(),/Everyday settings/,'simple is explained');
// Advanced reveals the full control set and the choice survives a reload
await p.locator('#cfgmode button[data-m=advanced]').click();
assert.ok(await p.evaluate(()=>!document.body.classList.contains('simple')),'advanced clears the simple view');
assert.equal(await p.locator('#cfgmode button[data-m=advanced]').getAttribute('aria-checked'),'true','advanced radio is on');
assert.match(await p.locator('#modehelp').innerText(),/All settings and technical controls/,'advanced is explained');
assert.equal(await p.evaluate(()=>localStorage.getItem('cc_cfg_mode_v2')),'advanced','choice is stored');
await p.reload();await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);
assert.ok(await p.evaluate(()=>!document.body.classList.contains('simple')),'advanced persists across reload');
// Switching back is lossless: the provider selection is unchanged
await p.locator('#cfgmode button[data-m=simple]').click();
assert.ok(await p.evaluate(()=>document.body.classList.contains('simple')),'simple restored');
const settings=(await p.evaluate(async()=>await (await fetch('/api/settings')).json())).settings;
assert.equal(settings.provider,'mock','mode switches never touch saved settings');
await b.close();console.log('PASS mode switch: simple by default, advanced explained and persisted across reload, switching views keeps saved values')})().catch(e=>{console.error(e);process.exit(1)});
