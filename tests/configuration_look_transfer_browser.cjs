const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict'),fs=require('node:fs');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1280,height:900},acceptDownloads:true});
await p.addInitScript(()=>localStorage.setItem('cc_cfg_tour_v1','1'));
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-presets');
await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names&&document.querySelector('#exp'));
await p.waitForSelector('#sec-presets.settings-active-panel');
await p.evaluate(()=>document.querySelector('.look-more > summary').click());
// Export produces a real look file
const [download]=await Promise.all([p.waitForEvent('download',{timeout:15000}),p.evaluate(()=>document.querySelector('#exp').click())]);
const exported=await download.path();
const look=JSON.parse(fs.readFileSync(exported,'utf8'));
assert.ok(look&&typeof look==='object'&&('txt_title' in look||'light' in look),'export is a look file');
const original=await p.evaluate(async()=>(await (await fetch('/api/theme')).json()).txt_title);
// Change the wording, then restore it by importing the file back
await p.evaluate(()=>document.querySelector('a[href="#sec-wording"]').click());
await p.waitForSelector('#sec-wording.settings-active-panel');
await p.locator('[data-k=txt_title] input').fill('ZZZ Transfer Probe');
await p.waitForFunction(async()=>{const t=await (await fetch('/api/theme')).json();return t.txt_title==='ZZZ Transfer Probe'},{timeout:20000});
await p.evaluate(()=>document.querySelector('a[href="#sec-presets"]').click());
await p.waitForSelector('#sec-presets.settings-active-panel');
await p.evaluate(()=>document.querySelector('.look-more > summary').click());
await p.locator('#imp').setInputFiles(exported,{timeout:10000});
const dlg=p.locator('dialog[open]');
await dlg.waitFor();
await dlg.getByRole('button',{name:'Import'}).click();
await p.waitForFunction(async(orig)=>{const t=await (await fetch('/api/theme')).json();return t.txt_title===orig},{timeout:20000},original);
// A bogus file is rejected without touching the look
fs.writeFileSync('/tmp/not-a-look.json',JSON.stringify({nonsense:true}));
await p.locator('#imp').setInputFiles('/tmp/not-a-look.json');
await p.waitForFunction(()=>/not a Chatify look file/.test(document.querySelector('#lookTransferStatus')?.textContent||''),{timeout:10000});
const after=await p.evaluate(async()=>(await (await fetch('/api/theme')).json()).txt_title);
assert.equal(after,original,'rejected import leaves the look untouched');
await b.close();console.log('PASS look transfer: export downloads a real look file, re-import confirms and restores wording, bogus files are rejected without changes')})().catch(e=>{console.error(e);process.exit(1)});
