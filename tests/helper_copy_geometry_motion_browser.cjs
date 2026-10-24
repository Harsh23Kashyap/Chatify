const{chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const width of[320,1280])for(const reducedMotion of['reduce','no-preference']){
const p=await b.newPage({viewport:{width,height:900},reducedMotion});await p.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_cfg_mode_v2','advanced');Object.defineProperty(navigator,'clipboard',{value:{writeText:async()=>new Promise(r=>window.fixtureRelease=r)}})});
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-code');await p.waitForFunction(()=>document.querySelector('#codeEditor .helper'));
const h=p.locator('#codeEditor .helper'),copy=h.getByRole('button',{name:'Copy',exact:true}),chk=h.getByRole('button',{name:'Check again',exact:true});
assert.equal(await h.getByRole('button',{name:'Save helper draft',exact:true}).count(),0);
await copy.evaluate(n=>n.dataset.fixtureCopy='1');const button=h.locator('[data-fixture-copy="1"]');
await button.scrollIntoViewIfNeeded();await p.waitForTimeout(200);
const original={copy:await button.boundingBox(),check:await chk.boundingBox()};
await button.click();await p.waitForFunction(()=>!!window.fixtureRelease);await p.waitForTimeout(150);
const pending={copy:await button.boundingBox(),check:await chk.boundingBox()};
for(const id of ['copy','check'])for(const k of['x','y','width','height'])assert(Math.abs(original[id][k]-pending[id][k])<.5,JSON.stringify({width,reducedMotion,id,k,original,pending}));
await p.evaluate(()=>window.fixtureRelease());await h.getByText('Copied.',{exact:true}).waitFor();await p.waitForTimeout(200);
const success={copy:await button.boundingBox(),check:await chk.boundingBox()};
for(const id of ['copy','check'])for(const k of['x','y','width','height'])assert(Math.abs(original[id][k]-success[id][k])<.5,JSON.stringify({width,reducedMotion,id,k,original,success}));
await p.screenshot({path:`/downloads/cc29-helper-copy-geometry-${width}-${reducedMotion}.png`});
await p.close();
}await b.close();console.log('PASS helper Copy Copying Copied geometry and adjacent Check stable3201280normalReduce')})().catch(e=>{console.error(e);process.exit(1)});
