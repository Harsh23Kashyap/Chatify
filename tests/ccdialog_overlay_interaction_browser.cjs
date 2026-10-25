const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright'),fs=require('fs'),assert=require('assert'),{confirmCCDialog,dismissCCDialog}=require('./nav_helpers.cjs');
// Regression coverage for the mountModal inert-shield fix: a CCDialog opened
// over a mounted overlay must stay fully interactive (real pointer, Escape,
// labelled buttons), the overlay must stay open behind it and shielded, and
// closing everything restores focus. Exercises 1280 and 320 (mobile pointer).
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});for(const width of [1280,320]){const p=await b.newPage({viewport:{width,height:900}});p.setDefaultTimeout(8000);await p.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_tour','1')});await p.goto((process.env.CHATIFY_TEST_URL || 'http://127.0.0.1:8142')+'/');
const trigger=p.getByRole('button',{name:/Add documents/});
const triggerId=await trigger.evaluate(e=>e.id||e.className);
await trigger.click();
const overlay=p.getByRole('dialog',{name:'Add sources',exact:true}),url=p.getByLabel('Web address',{exact:true});
await url.fill('https://example.invalid/pending');
await overlay.getByRole('button',{name:'Done',exact:true}).click();
const ccdlg=p.locator('dialog.cc-cdlg[open]');
await ccdlg.waitFor();
// shield contract: overlay + page children inert, CCDialog itself not inert
const shieldState=await p.evaluate(()=>{const c=document.querySelector('dialog.cc-cdlg[open]');const done=[...document.querySelectorAll('.modal-back button')].find(n=>n.textContent.trim()==='Done');const dr=done.getBoundingClientRect();return {ccdlgInert:c.inert,overlayDoneHit:document.elementsFromPoint(dr.x+dr.width/2,dr.y+dr.height/2).map(e=>e.tagName)[0],pageShielded:[...document.body.children].filter(n=>!n.classList.contains('modal-back')&&!(n.matches&&n.matches('dialog[open]'))).every(n=>n.inert)}});
assert.equal(shieldState.ccdlgInert,false,'CCDialog must not be inert');
assert.notEqual(shieldState.overlayDoneHit,'BUTTON','overlay button must be hit-blocked under a modal CCDialog');
assert.equal(shieldState.pageShielded,true,'page background must stay shielded');
// real pointer hit at the cancel button centre (the exact regression)
const r=await ccdlg.locator('.cc-cdlg-cancel').boundingBox();
await p.mouse.click(r.x+r.width/2,r.y+r.height/2);
await ccdlg.waitFor({state:'detached'});
assert.equal(await overlay.isVisible(),true,'overlay must stay open after CCDialog cancel');
assert.equal(await url.inputValue(),'https://example.invalid/pending','typed address kept after cancel');
assert.equal(await p.evaluate(()=>{const done=[...document.querySelectorAll('.modal-back button')].find(n=>n.textContent.trim()==='Done');const r=done.getBoundingClientRect();return document.elementsFromPoint(r.x+r.width/2,r.y+r.height/2).map(e=>e.tagName)[0]}),'BUTTON','overlay must regain hit-testing after CCDialog closes');
// Escape resolves as cancel
await overlay.getByRole('button',{name:'Done',exact:true}).click();
await ccdlg.waitFor();
await p.keyboard.press('Escape');
await ccdlg.waitFor({state:'detached'});
assert.equal(await overlay.isVisible(),true,'overlay must stay open after Escape');
assert.equal(await url.inputValue(),'https://example.invalid/pending');
// accept path closes both
await overlay.getByRole('button',{name:'Done',exact:true}).click();
await ccdlg.waitFor();
await confirmCCDialog(p,'Discard');
await overlay.waitFor({state:'detached'});
// focus restore to the trigger after the overlay closes
await p.waitForTimeout(150);
const focusBack=await p.evaluate(()=>{const a=document.activeElement;return a&&(a.id||a.className)||''});
assert(focusBack.includes(triggerId)||triggerId.includes(focusBack),'focus must return to the Add documents trigger, got: '+focusBack);
await p.screenshot({path:(process.env.CHATIFY_TEST_OUTPUT || '/tmp')+'/cc-overlay-shield-'+width+'.png'});
await p.close()}
await b.close();console.log('PASS ccdialog_overlay_interaction_browser')})().catch(e=>{console.error(e);process.exit(1)});
