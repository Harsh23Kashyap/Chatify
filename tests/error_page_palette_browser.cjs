const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const rgb=hex=>{let h=hex.trim().replace('#','');if(h.length===3)h=[...h].map(c=>c+c).join('');return `rgb(${parseInt(h.slice(0,2),16)}, ${parseInt(h.slice(2,4),16)}, ${parseInt(h.slice(4,6),16)})`};
for(const theme of ['light','dark']){
 const p=await b.newPage({viewport:{width:1280,height:900}});
 await p.addInitScript(t=>{localStorage.setItem('cc_mode',t)},theme);
 const res=await p.goto(process.env.CHATIFY_TEST_URL+'/no-such-page-unslop');
 assert.equal(res.status(),404,theme+': missing page is a 404');
 await p.waitForSelector('body.chatify-error .act a',{timeout:15000});
 const t=await p.evaluate(()=>{const cs=getComputedStyle(document.documentElement);const g=n=>cs.getPropertyValue(n).trim();return {ground:g('--ui-ground'),ink:g('--ui-ink'),muted:g('--ui-muted'),action:g('--ui-action'),onAction:g('--ui-on-action')}});
 assert.equal(await p.evaluate(()=>getComputedStyle(document.body).backgroundColor),rgb(t.ground),theme+': error page ground');
 const home=await p.locator('.act a').first().evaluate(n=>({bg:getComputedStyle(n).backgroundColor,color:getComputedStyle(n).color}));
 assert.equal(home.bg,rgb(t.action),theme+': home action');
 assert.equal(home.color,rgb(t.onAction),theme+': home on-action');
 assert.equal(await p.locator('.code').evaluate(n=>getComputedStyle(n).color),rgb(t.muted),theme+': code muted');
 assert.equal(await p.locator('h1').evaluate(n=>getComputedStyle(n).color),rgb(t.ink),theme+': title ink');
 assert.equal(await p.locator('main svg').evaluate(n=>getComputedStyle(n).color),rgb(t.action),theme+': art action');
 assert.equal(await p.evaluate(()=>document.documentElement.dataset.theme),theme,theme+': stored theme applies');
 await p.close();
}
await b.close();console.log('PASS error page shares the vermilion+sand tokens and follows the stored light/dark theme')})().catch(e=>{console.error(e);process.exit(1)});
