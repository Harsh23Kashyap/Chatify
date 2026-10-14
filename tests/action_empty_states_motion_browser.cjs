const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 for(const width of [320,1280])for(const reducedMotion of ['reduce','no-preference'])for(const motion of ['full','subtle','none','calm']){
 const p=await b.newPage({viewport:{width,height:900},reducedMotion});await p.addInitScript(()=>localStorage.setItem('cc_tour','1'));let empty=true;
 await p.route('**/api/actions',r=>r.fulfill({json:empty?[]:[{id:'list_notes',label:'List my notes',mode:'read',fields:{}}]}));
 await p.route('**/api/actions/prepare',r=>r.fulfill({json:{ticket:'fixture',label:'List my notes',mode:'read',tool:'list_notes',args:{}}}));
 await p.route('**/api/actions/execute',r=>r.fulfill({json:{notes:[]}}));
 await p.goto(process.env.CUSTOMCHAT_TEST_URL+'/');await p.locator('.playground-action').first().waitFor();await p.evaluate(m=>{const t=JSON.parse(JSON.stringify(CCTheme.value));t.motion=m;CCTheme.apply(t)},motion);
 for(const kind of ['catalog','notes']){
 await p.locator('#actionsBtn').focus();await p.keyboard.press('Enter');await p.locator('.action-dialog').waitFor();
 if(kind==='notes'){await p.getByRole('button',{name:'List my notes',exact:true}).focus();await p.keyboard.press('Enter');await p.getByRole('button',{name:'Preview action',exact:true}).focus();await p.keyboard.press('Enter');await p.getByRole('button',{name:'Confirm action',exact:true}).waitFor();await p.getByRole('button',{name:'Confirm action',exact:true}).focus();await p.keyboard.press('Enter');await p.getByRole('heading',{name:'Your notes',exact:true}).waitFor()}
 const state=p.locator('.action-empty');await state.waitFor();assert.equal(await state.innerText(),kind==='catalog'?'No actions enabled.':'No notes saved yet.');
 const s=await state.evaluate(n=>({name:getComputedStyle(n).animationName,duration:getComputedStyle(n).animationDuration,transform:getComputedStyle(n).transform,role:n.getAttribute('role'),media:n.querySelectorAll('img,svg,canvas,video').length,frames:n.getAnimations().flatMap(a=>a.effect.getKeyframes()).map(k=>({opacity:k.opacity,transform:k.transform||'none'}))}));
 const off=reducedMotion==='reduce'||motion==='none'||motion==='calm';assert.equal(s.name,off?'none':'m-in');assert.equal(s.role,'status');assert.equal(s.media,0);assert.equal(s.transform,'none');if(!off){assert.equal(s.duration,'0.14s');assert(s.frames.every(k=>k.transform==='none'))}
 await p.waitForTimeout(200);await p.screenshot({path:`/downloads/cc29-action-empty-${kind}-${width}-${motion}-${reducedMotion}.png`});
 await p.getByRole('button',{name:'Close',exact:true}).focus();await p.keyboard.press('Enter');assert(await p.locator('#actionsBtn').evaluate(n=>n===document.activeElement));await p.locator('.action-dialog').waitFor({state:'detached'});assert.equal(await p.locator('.action-empty').count(),0);empty=false;
 }assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.close();
 }await b.close();console.log('PASS action catalog+notes empty140opacity only full/subtle NoneCalmReduceoff keyboard enter focus cleanreplacement3201280')})().catch(e=>{console.error(e);process.exit(1)});
