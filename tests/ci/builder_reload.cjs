// Controlled HTTP responses test browser state only, not providers or restart durability.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE),assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 try{
  const p=await browser.newPage({viewport:{width:1440,height:1000}});
  let starts=0,activeReads=0,fail=false,malformed=false,empty=false,pending=false,resolveActive;
  const job={id:'1234567890abcdef1234567890abcdef',state:'running',completed:12,total:31,calls:12,call_cap:36,phase:'Drafting prompts',parts:[{id:'app',state:'done'}],errors:{}};
  await p.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_cfg_mode_v2','advanced')});
  await p.route('**/api/provider/status',r=>r.fulfill({json:{keys:{openai:{has:true}}}}));
  await p.route('**/api/settings/build/start',r=>{starts++;return r.fulfill({json:job})});
  await p.route('**/api/settings/build/job?id=*',r=>r.fulfill({json:job}));
  await p.route('**/api/settings/build/active',async r=>{
   activeReads++;
   if(pending)await new Promise(resolve=>resolveActive=resolve);
   return r.fulfill(fail?{status:503,json:{error:'Controlled outage'}}:{json:malformed?{}:{active:starts>0,running_total:starts>0?1:0,mine:starts&&!empty?[{id:job.id,phase:job.phase,completed:12,total:31,calls:12}]:[]}});
  });
  const ready=async()=>{await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names);await p.evaluate(()=>{const orig=CCSettingsSimple.state;CCSettingsSimple.state=()=>({...orig(),provider:'openai',model:'fixture-only',canEdit:true})})};
  const open=async()=>{await p.getByRole('button',{name:'Build with AI',exact:true}).first().click();await p.locator('.app-builder-open').click()};
  await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html');await ready();await open();
  await p.locator('#builderBrief').fill('Reload continuity fixture');await p.locator('#builderSend').click();
  await p.waitForFunction(()=>document.querySelector('.builder-background')?.dataset.state==='running');
  await p.reload();await ready();await open();
  await p.waitForFunction(()=>document.querySelector('.app-builder-open')?.textContent.includes('12/31'));
  assert.equal(starts,1);assert.equal(activeReads,2);assert.equal(await p.locator('.builder-background').isVisible(),true);
  await p.screenshot({path:process.env.CHATIFY_TEST_OUTPUT?process.env.CHATIFY_TEST_OUTPUT+'/reload.png':'/downloads/chatify-reload-recovery-candidate-20261103.png'});
  // Outage and malformed snapshots must not enable a second build. Reopen checks again.
  for(const mode of ['outage','malformed']){
   await p.reload();await ready();fail=mode==='outage';malformed=mode==='malformed';await open();
   await p.waitForFunction(()=>document.querySelector('#builderActionBar')?.dataset.state==='unknown');
   await p.locator('#builderBrief').fill('Preserve my new description');await p.waitForFunction(()=>document.querySelector('#builderProvider')?.hidden);assert.equal(await p.locator('#builderSend').isDisabled(),true);
   assert.match(await p.locator('#builderStatus').innerText(),/Could not check/);
   await p.locator('#builderClose').click();fail=false;malformed=false;await p.locator('.app-builder-open').click();
   await p.waitForFunction(()=>document.querySelector('.app-builder-open')?.textContent.includes('12/31'));
   assert.equal(await p.locator('#builderBrief').inputValue(),'Preserve my new description');assert.equal(starts,1);
  }
  // Closing during the read may not reset a description typed during the check.
  await p.reload();await ready();empty=true;pending=true;await open();
  await p.locator('#builderBrief').fill('Keep this unsaved description');await p.locator('#builderClose').click();
  pending=false;resolveActive();await p.waitForFunction(()=>!document.querySelector('#builderStatus')?.textContent.includes('Checking for a build'));
  await p.locator('.app-builder-open').click();await p.locator('#builderSend').waitFor();
  await p.waitForFunction(()=>!document.querySelector('#builderSend').disabled);
  assert.equal(await p.locator('#builderBrief').inputValue(),'Keep this unsaved description');assert.equal(starts,1);
  // An older failed discovery response cannot overwrite a newer successful reopen.
  await p.reload();await ready();let oldRelease,read=0;
  await p.route('**/api/settings/build/active',async r=>{
   read++;
   if(read===1){await new Promise(resolve=>oldRelease=resolve);return r.fulfill({status:503,json:{error:'Older response'}})}
   return r.fulfill({json:{mine:[{id:job.id}]}});
  });
  await open();await p.locator('#builderClose').click();await p.locator('.app-builder-open').click();
  await p.waitForFunction(()=>document.querySelector('.app-builder-open')?.textContent.includes('12/31'));
  const oldResponse=p.waitForResponse(r=>r.url().includes('/api/settings/build/active')&&r.status()===503);
  oldRelease();await oldResponse;
  await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  assert.equal(await p.locator('.builder-background').getAttribute('data-state'),'running');assert.equal(starts,1);
  console.log(JSON.stringify({controlledBrowserRecovery:'passed',activeReads,starts,checks:['reload reconnect','outage blocked','malformed blocked','reopen recovery','unsaved description preserved','no duplicate start','stale read ignored']}));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
