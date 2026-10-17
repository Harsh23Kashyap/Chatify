const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{
 const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
 for(const reducedMotion of ['reduce','no-preference'])for(const width of [320,1280])for(const moved of [false,true]){
  const p=await b.newPage({viewport:{width,height:900},reducedMotion});
  await p.addInitScript(()=>localStorage.setItem('cc_tour','1'));
  let prepares=0,executes=0;
  await p.route('**/api/actions',r=>r.fulfill({json:[{id:'save_note',label:'Save a private note',mode:'write',fields:{title:{maxLength:120},text:{maxLength:4000}}}]}));
  await p.route('**/api/actions/prepare',async r=>{
   prepares++;const d=r.request().postDataJSON();await new Promise(x=>setTimeout(x,200));
   return prepares===1?r.fulfill({status:503,json:{error:'Fixture preview interrupted.'}}):r.fulfill({json:{ticket:'fixture',label:'Save a private note',mode:'write',tool:d.tool,args:d.args}});
  });
  await p.route('**/api/actions/execute',r=>{executes++;return r.fulfill({json:{saved:true}})});
  await p.goto(process.env.CHATIFY_TEST_URL+'/');await p.locator('.playground-action').first().waitFor();
  await p.locator('#actionsBtn').click();await p.getByRole('button',{name:'Save a private note',exact:true}).click();
  await p.getByRole('textbox',{name:'Note title',exact:true}).fill('Keep this title');
  await p.getByRole('textbox',{name:'Note text',exact:true}).fill('Keep this draft');
  await p.getByRole('button',{name:'Preview action',exact:true}).dblclick();
  if(moved)await p.getByRole('button',{name:'Close',exact:true}).focus();
  await p.getByText('Fixture preview interrupted.',{exact:true}).waitFor();
  assert.equal(prepares,1);assert.equal(executes,0);
  assert.equal(await p.getByRole('textbox',{name:'Note text',exact:true}).inputValue(),'Keep this draft');
  const target=p.getByRole('button',{name:moved?'Close':'Preview action',exact:true});
  assert(await target.evaluate(n=>n===document.activeElement),`preview failure focus ${width} ${reducedMotion} moved=${moved}`);
  await p.getByRole('button',{name:'Preview action',exact:true}).focus();await p.keyboard.press('Enter');
  await p.getByRole('button',{name:'Confirm action',exact:true}).waitFor();
  assert.equal(prepares,2);assert.equal(executes,0);assert.match(await p.locator('.action-body').innerText(),/Keep this draft/);
  await p.getByRole('button',{name:'Close',exact:true}).click();assert(await p.locator('#actionsBtn').evaluate(n=>n===document.activeElement));
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await p.close();
 }
 await b.close();console.log('PASS prepare503 recovery focus preserved draft singleflight nativeEnter freshreview noexecute 3201280 normalReduce movedClose');
})().catch(e=>{console.error(e);process.exit(1)});
