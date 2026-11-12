const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900}});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-wording');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names&&document.querySelector('[data-k=txt_title] input'));
await p.waitForSelector('#sec-wording.settings-active-panel');
const titleInput=p.locator('[data-k=txt_title] input');
const before=await p.evaluate(async()=>(await (await fetch('/api/theme')).json()).txt_title);
await titleInput.fill('ZZZ Reset Probe');
await p.waitForFunction(async()=>{const t=await (await fetch('/api/theme')).json();return t.txt_title==='ZZZ Reset Probe'},{timeout:20000});
// Reset lives behind the danger disclosure in the presets panel; it asks before touching anything
await p.evaluate(()=>document.querySelector('a[href="#sec-presets"]').click());
await p.waitForSelector('#sec-presets.settings-active-panel');
await p.locator('.look-more > summary').click();
await p.locator('.look-danger > summary').click();
await p.locator('#resetLink').click();
const dlg=p.locator('dialog[open]');
await dlg.waitFor();
assert.match(await dlg.textContent(),/Prompts, sources, keys and helper drafts stay unchanged/,'reset dialog scopes what survives');
await dlg.getByRole('button',{name:'Reset'}).click();
await p.waitForFunction(async()=>{const t=await (await fetch('/api/theme')).json();return t.txt_title!=='ZZZ Reset Probe'},{timeout:20000});
const after=await p.evaluate(async()=>(await (await fetch('/api/theme')).json()).txt_title);
assert.equal(after,before,'app name returns to its prior value');
// Model settings are untouched by a look reset
const settings=(await p.evaluate(async()=>await (await fetch('/api/settings')).json())).settings;
assert.equal(settings.provider,'mock','provider survives a look reset');
await b.close();console.log('PASS reset look: wording change autosaves, danger-zone reset confirms and restores the default, model settings untouched')})().catch(e=>{console.error(e);process.exit(1)});
