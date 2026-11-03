const{chromium}=require(process.env.PLAYWRIGHT_MODULE),assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 try{
  const p=await b.newPage({viewport:{width:1440,height:1050},reducedMotion:'reduce'});let saved=false,fail=false,owner=true,posts=[],sourcePosts=[],calls=[];
  await p.route('**/api/settings',r=>r.fulfill({json:{can_edit:owner,settings:{provider:'openai',model:'fixture-model'}}}));
  await p.route('**/api/provider/status',r=>r.fulfill({json:{keys:{openai:{has:saved,needed:true}}}}));
  await p.route('**/api/provider/key',r=>{posts.push(r.request().postDataJSON());if(fail)return r.fulfill({status:503,json:{error:'Controlled outage'}});saved=true;return r.fulfill({json:{key:{has:true,source:'saved'}}})});
  await p.route('**/api/catalog/key',r=>{sourcePosts.push(r.request().postDataJSON());return r.fulfill({json:{has_key:true}})});
  p.on('request',r=>{if(/\/api\/(provider\/test|settings\/build\/start|catalog\/test)/.test(r.url()))calls.push(r.url())});
  const sourceStep=async()=>{await p.goto(process.env.CHATIFY_TEST_URL+'/build.html');await p.locator('#buildBrief').fill('Research about public health');await p.locator('#buildToSources').click();await p.locator('#buildModelKeySetup').waitFor()};
  await sourceStep();await p.locator('#buildModelKeySetup summary').click();
  assert.match(await p.locator('#buildModelKeyScope').innerText(),/fixture-model.*openai/);
  await p.locator('#buildModelKeySave').click();assert.equal(posts.length,0);
  await p.locator('#buildModelKey').fill('FAKE-OFFLINE-FIXTURE-ONE');await p.locator('#buildModelKeySave').click();
  await p.waitForFunction(()=>document.querySelector('#buildModelKeyStatus').textContent.includes('saved privately'));
  assert.equal(await p.locator('#buildModelKey').inputValue(),'');assert.equal(posts[0].provider,'openai');assert.match(await p.locator('#buildModelKeyStatus').innerText(),/not tested/);
  await p.locator('#buildModelKeySetup').scrollIntoViewIfNeeded();await p.screenshot({path:'/downloads/chatify-inline-key-saved-20261103.png'});
  await p.locator('#buildSourceKeySetup summary').click();await p.getByLabel('OpenAlex source API key',{exact:true}).fill('FAKE-OPENALEX-FIXTURE');await p.getByRole('button',{name:'Save OpenAlex source key',exact:true}).click();await p.waitForFunction(()=>document.querySelector('#buildSourceKeySetup [role=status]').textContent.includes('saved privately'));assert.equal(sourcePosts[0].id,'openalex');assert.equal(await p.getByLabel('OpenAlex source API key',{exact:true}).inputValue(),'');
  await p.locator('#buildSourceKeySetup').scrollIntoViewIfNeeded();await p.screenshot({path:'/downloads/chatify-inline-openalex-key-saved-20261103.png'});
  fail=true;await p.locator('#buildModelKey').fill('FAKE-OFFLINE-REPLACEMENT');await p.locator('#buildModelKeySave').click();
  await p.waitForFunction(()=>document.querySelector('#buildModelKeyStatus').textContent.includes('Could not confirm'));
  assert.equal(await p.locator('#buildModelKey').inputValue(),'FAKE-OFFLINE-REPLACEMENT');assert.equal(posts.length,2);
  owner=false;await p.reload();await p.locator('#buildBrief').fill('Research about public health');await p.locator('#buildToSources').click();await p.waitForFunction(()=>document.querySelector('#buildProviderNote').textContent.includes('Only the app owner'));
  assert.equal(await p.locator('#buildModelKeySetup').isHidden(),true);assert.equal(await p.locator('#buildSourceKeySetup input').count(),0);assert.equal(calls.length,0);
  await p.goto(process.env.CHATIFY_TEST_URL+'/about.html');await p.locator('#featureMore').click();
  await p.locator('#feature-tab-motion').click();await p.waitForFunction(()=>document.querySelector('.feature-copy h3')?.textContent==='Motion and emoji');
  assert.equal(await p.locator('.feature-next-step a').getAttribute('href'),'/settings.html#sec-motion');assert.match(await p.locator('.feature-next-step').innerText(),/Full.*Subtle.*Calm\/None.*reduced motion/);
  await p.locator('.feature-next-step').scrollIntoViewIfNeeded();await p.screenshot({path:'/downloads/chatify-feature-motion-guide-20261103.png'});
  const link=await p.locator('.feature-next-step a').getAttribute('href');
  await p.goto(process.env.CHATIFY_TEST_URL+link);await p.waitForFunction(()=>document.body.dataset.settingsSection==='motion');
  await p.locator('#sec-motion').waitFor({state:'visible'});
  await p.goto(process.env.CHATIFY_TEST_URL+'/about.html');await p.locator('#featureMore').click();
  const guideLinks=[];
  for(const tab of await p.locator('#featureTabs [role=tab]').all()){
   await tab.click();await p.waitForFunction(()=>!document.querySelector('[aria-busy=true]'));
   assert.ok((await p.locator('.feature-next-step p').innerText()).length>30);
   guideLinks.push(await p.locator('.feature-next-step a').getAttribute('href'));
  }
  assert.equal(guideLinks.length,23);
  for(const href of [...new Set(guideLinks)].filter(x=>x.includes('#sec-'))){
   await p.goto(process.env.CHATIFY_TEST_URL+href);const id=href.split('#')[1];
   await p.locator('#'+id).waitFor({state:'visible'});
  }
  console.log(JSON.stringify({inlineKey:'saved and error preserved',providerBound:'openai',ownerGate:'passed',automaticProviderOrBuildCalls:calls.length,featureMotionRoute:'real control opened'}));
 }finally{await b.close()}
})().catch(e=>{console.error(e);process.exit(1)});
