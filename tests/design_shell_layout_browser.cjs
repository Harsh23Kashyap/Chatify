const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});for(const width of [390,1280])for(const theme of ['light','dark'])for(const reducedMotion of ['no-preference','reduce']){const p=await browser.newPage({viewport:{width,height:width===1280?720:844},reducedMotion});await p.addInitScript(t=>{localStorage.setItem('cc_tour','1');localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_mode',t)},theme);await p.route('**/api/chats*',r=>r.fulfill({json:[]}));await p.goto(process.env.CHATIFY_TEST_URL+'/');await p.locator('.doc-scene').waitFor();await p.waitForTimeout(650);assert.equal(await p.locator('.doc-scene').evaluate(n=>n.getAnimations({subtree:true}).filter(a=>a.playState==='running').length),0);if(width===1280){const edge=await p.locator('#thread').evaluate(n=>n.getBoundingClientRect().bottom);for(const row of await p.locator('.playground-question,.playground-action').all()){const r=await row.boundingBox();assert(r.height>=44);assert(r.y+r.height<=edge+1,JSON.stringify({r,edge}));}}assert.equal(await p.locator('.history-empty-art svg').count(),1);assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));if(width<861)await p.locator('#menu').click();await p.locator('#tempPill').click();await p.locator('.ephemeral-scene').waitFor();await p.waitForTimeout(600);const back=p.getByRole('button',{name:'Back to saved chats ↗',exact:true}),r=await back.boundingBox(),edge=await p.locator('#thread').evaluate(n=>n.getBoundingClientRect().bottom);assert(r.y+r.height<=edge+1);assert(r.height>=44);await p.locator('#q').focus();assert.equal(await p.locator('#q').evaluate(n=>getComputedStyle(n).outlineWidth),'0px');assert.notEqual(await p.locator('.box').evaluate(n=>getComputedStyle(n).boxShadow),'none');assert.equal(await p.locator('.ephemeral-scene').evaluate(n=>n.getAnimations({subtree:true}).filter(a=>a.playState==='running').length),0);await p.screenshot({path:`/downloads/design-final-temporary-${width}-${theme}-${reducedMotion}.png`});await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html');await p.locator('#cfgIdea').waitFor();assert.equal(await p.locator('html').getAttribute('data-theme'),theme);const disclosure=await p.locator('#cfgImproveCost').boundingBox(),idea=await p.locator('#cfgIdea').boundingBox(),improve=await p.locator('#cfgImproveIdea').boundingBox();assert(disclosure.y>=idea.y+idea.height);assert(disclosure.y+disclosure.height<=improve.y+1);assert.equal(await p.locator('#cfgImproveIdea').getAttribute('aria-describedby'),'cfgImproveCost');assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.screenshot({path:`/downloads/design-final-settings-${width}-${theme}-${reducedMotion}.png`});await p.close()}for(const fail of [false,true]){
 const p=await browser.newPage({viewport:{width:1280,height:720}});
 await p.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_mode','dark')});
 let release;const held=new Promise(r=>release=r);
 await p.route('**/api/config',async r=>{await held;if(fail)await r.fulfill({status:503,json:{error:'Configuration unavailable for fixture'}});else await r.continue()});
 await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html',{waitUntil:'domcontentloaded'});
 await p.locator('#cfgIdea').waitFor();
 assert.equal(await p.locator('#cc-boot').evaluate(n=>n.classList.contains('cc-boot-out')),false,'held initial data stays behind loader');
 await p.screenshot({path:`/downloads/design-config-held-${fail}.png`});
 release();await p.locator('#cc-boot').waitFor({state:'detached'});
 if(fail){assert.match(await p.locator('#settingsBootError').innerText(),/Configuration unavailable/);const retry=await p.getByRole('button',{name:'Reload configuration',exact:true}).boundingBox();assert(retry.y+retry.height<720);}
 else {await p.waitForFunction(()=>window.CCSettingsSimple?.state()?.ready);assert.equal(await p.locator('body').evaluate(n=>n.classList.contains('settings-tabs')),true);
  for(const section of ['background','shape']){
   await p.locator('#menu a[href="#sec-'+section+'"]').evaluate(n=>n.click());
   const selected=p.locator('.'+section+'-shortcuts [aria-pressed=true]');
   assert.equal(await selected.evaluate(n=>{const a=document.createElement('i');a.style.color='var(--ui-action)';document.body.append(a);const same=getComputedStyle(n).outlineColor===getComputedStyle(a).color;a.remove();return same}),true,'selection uses shell action token');
   await p.screenshot({path:`/downloads/design-shortcut-${section}.png`});
  }
 }
 await p.screenshot({path:`/downloads/design-config-ready-${fail}.png`});await p.close();
}
for(const theme of ['light','dark']){
 const p=await browser.newPage({viewport:{width:390,height:844}});await p.addInitScript(t=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_cfg_top_v1','manual');localStorage.setItem('cc_cfg_mode_v2','advanced');localStorage.setItem('cc_mode',t)},theme);
 await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html#sec-model');await p.locator('#cc-boot').waitFor({state:'detached'});
 await p.waitForFunction(()=>{const r=document.querySelector('#sec-model')?.getBoundingClientRect();return r&&r.top>=0&&r.top<innerHeight-80});
 await p.screenshot({path:`/downloads/design-mobile-deeplink-${theme}.png`});await p.close();
}
await browser.close();console.log('PASS design pass shell light/dark, 390/1280, normal/reduce, visible starter/tool targets, temporary explanation/return, one focus surface, disclosure adjacency, settled SVGs')})().catch(e=>{console.error(e);process.exit(1)});
