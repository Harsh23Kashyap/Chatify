const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 for(const reducedMotion of ['reduce','no-preference'])for(const width of [320,1280])for(const phase of ['prepare','execute'])for(const failed of [false,true]){
  const p=await b.newPage({viewport:{width,height:900},reducedMotion});
  await p.addInitScript(()=>localStorage.setItem('cc_tour','1'));
  let release,startedResolve;const started=new Promise(r=>startedResolve=r),gate=new Promise(r=>release=r);let held=false;
  await p.route('**/api/actions',r=>r.fulfill({json:[{id:'save_note',label:'Save a private note',mode:'write',fields:{title:{maxLength:120},text:{maxLength:4000}}}]}));
  await p.route('**/api/actions/prepare',async r=>{
   const d=r.request().postDataJSON();if(phase==='prepare'&&!held){held=true;startedResolve();await gate;if(failed)return r.fulfill({status:503,json:{error:'Old preview failed.'}})}
   return r.fulfill({json:{ticket:'fixture',label:'Save a private note',mode:'write',tool:d.tool,args:d.args}});
  });
  await p.route('**/api/actions/execute',async r=>{held=true;startedResolve();await gate;return failed?r.fulfill({status:503,json:{error:'Old execution failed.'}}):r.fulfill({json:{saved:true}})});
  await p.goto(process.env.CHATIFY_TEST_URL+'/');await p.locator('.playground-action').first().waitFor();
  await p.locator('#actionsBtn').click();await p.getByRole('button',{name:'Save a private note',exact:true}).click();
  await p.getByRole('textbox',{name:'Note title',exact:true}).fill('Old draft');
  await p.getByRole('button',{name:'Preview action',exact:true}).click();
  if(phase==='execute'){await p.getByRole('button',{name:'Confirm action',exact:true}).waitFor();await p.getByRole('button',{name:'Confirm action',exact:true}).click()}
  await started;await p.getByRole('button',{name:'Close',exact:true}).click();assert(await p.locator('#actionsBtn').evaluate(n=>n===document.activeElement));
  await p.locator('#actionsBtn').click();await p.getByRole('button',{name:'Save a private note',exact:true}).click();
  await p.getByRole('textbox',{name:'Note title',exact:true}).fill('New draft');
  await p.getByRole('textbox',{name:'Note text',exact:true}).fill('New pending text');
  const oldResponse=p.waitForResponse(r=>r.url().endsWith('/api/actions/'+phase));release();await oldResponse;
  await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
  assert.equal(await p.locator('.action-dialog').count(),1);
  assert.equal(await p.getByRole('textbox',{name:'Note title',exact:true}).inputValue(),'New draft');
  assert.equal(await p.getByRole('textbox',{name:'Note text',exact:true}).inputValue(),'New pending text');
  assert(await p.getByRole('textbox',{name:'Note text',exact:true}).evaluate(n=>n===document.activeElement),`late ${phase} failed=${failed} keeps new focus`);
  assert(!/Old draft|Old preview failed|Old execution failed|Note saved/.test(await p.locator('.action-body').innerText()));
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
  await p.getByRole('button',{name:'Close',exact:true}).click();await p.close();
 }
 await b.close();console.log('PASS closed prepare/execute success/503 late responses keep reopened draft focus 3201280 normalReduce');
})().catch(e=>{console.error(e);process.exit(1)});
