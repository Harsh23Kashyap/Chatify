const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/tmp/chatify-browser/node_modules/playwright'),assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 for(const hosted of [true,false])for(const direct of [true,false]){
  const p=await b.newPage({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
  await p.addInitScript(()=>{localStorage.setItem('cc_cfg_tour_v1','1');localStorage.setItem('cc_cfg_mode_v2','advanced')});
  const yaml='app: {title: Garden Evidence Guide}\nsources: []\n';
  await p.route('**/*',async r=>{if(!r.request().url().startsWith(process.env.CHATIFY_TEST_URL))return r.abort();return r.continue()});
  await p.route('**/api/settings/build/drafts',r=>r.fulfill({json:{drafts:[{id:'fixture',title:'Recovered fixture'}]}}));
  await p.route('**/api/settings/build/draft?id=*',r=>r.fulfill({json:{yaml,sections:['app','sources']}}));
  await p.route('**/api/settings/build/review',async r=>{const body=r.request().postDataJSON();delete body.draft_id;const response=await r.fetch({postData:JSON.stringify(body)}),data=await response.json();assert(response.ok(),JSON.stringify(data));data.hosted=hosted;data.notice=hosted?'Own copy. Shared app unchanged.':data.notice;await r.fulfill({json:data})});
  await p.route('**/api/settings/build/save',r=>r.fulfill({json:{message:hosted?'Your reviewed app is saved as your own build.':'Reviewed configuration saved.',launch_ticket:'fixture'}}));
  p.on('pageerror',e=>console.log('PAGEERROR',e.message));await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html');try{await p.waitForFunction(()=>!!window.CCSettingsSimple?.state()?.names,{},{timeout:15000})}catch(e){console.log('DEBUG',await p.locator('body').innerText());await p.screenshot({path:'/downloads/hosted-label-error.png'});throw e};
  await p.locator('.app-builder-open').click();await p.locator('.builder-secondary-setup > summary').click();await p.locator('.builder-draft-library summary').click();await p.getByRole('button',{name:/Open draft/}).click();
  await p.locator('#builderReview').click();await p.waitForFunction(()=>!document.querySelector('#builderNext').hidden&&!document.querySelector('#builderNext').disabled);if(direct)await p.getByRole('button',{name:'3. Save configuration',exact:true}).click();else await p.locator('#builderNext').click();
  assert.equal(await p.locator('#builderSave').textContent(),hosted?'Save own build':'Update Parent fixture');
  assert.equal(await p.locator('#builderConfirmation h4').first().textContent(),hosted?'Save this app as your own build?':'Update Parent fixture with this app setup?');
  const allText=await p.locator('dialog.app-builder').innerText();assert(!allText.includes('then Apply'));if(hosted)assert(!allText.includes('until save and restart'));const note=await p.locator('#builderConfirmation > p').first().textContent();assert.match(note,hosted?/shared Parent fixture app stays unchanged/:/replaces the reviewed configuration/);
  await p.locator('#builderSave').scrollIntoViewIfNeeded();await p.screenshot({path:'/downloads/hosted-save-label-'+hosted+'-'+direct+'-confirm.png',fullPage:true});
  await p.locator('#builderSave').click();await p.getByRole('button',{name:'Use this app',exact:true}).waitFor();
  if(hosted){const savedText=await p.locator('dialog.app-builder').innerText();assert(!savedText.includes('until you restart'));assert(!savedText.includes('until save and restart'));assert(savedText.includes('no server restart is needed'));}assert.equal(await p.locator('#builderConfirmation h4').first().textContent(),hosted?'Your own app build is saved':'Updated Parent fixture setup is saved');
  await p.screenshot({path:'/downloads/hosted-save-label-'+hosted+'-'+direct+'-saved.png',fullPage:true});await p.close();
 }
 await b.close();console.log('PASS hosted own-build and local-update labels, confirmation scope and saved heading. Controlled UI only, no provider calls.');
})().catch(e=>{console.error(e);process.exit(1)});
