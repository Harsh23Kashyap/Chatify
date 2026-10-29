const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({headless:true});try{
for(const width of [390,1280]){
const p=await browser.newPage({viewport:{width,height:1000},reducedMotion:'reduce'});
await p.route('**/api/settings/build/job?*',r=>r.fulfill({json:{id:'a'.repeat(32),state:'done',completed:31,total:31,calls:31,yaml:'app:\n  title: Fixture\n',title:'Fixture'}}));
const logo='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aZ1cAAAAASUVORK5CYII=';
await p.route('**/api/settings/build/review',r=>r.fulfill({json:{ticket:'fixture',config:{app:{title:'Review fixture',examples:['What is supported?']},sources:[{id:'wiki',type:'wikipedia',label:'Wikipedia'}],appearance:{mode:'dark',dark:{accent:'#d7ef72'},logo},helper_drafts:{search:{brief:'Broken fixture',code:'',review_problems:['Missing required function.']},clean_query:{brief:'Static fixture',code:'',review_problems:[]}}}}}));
await p.goto((process.env.CHATIFY_TEST_URL||'http://127.0.0.1:8145')+'/build.html?job='+'a'.repeat(32));
await p.locator('#buildToReview').click();await p.locator('#reviewSave').waitFor();await p.locator('.build-logo-review').evaluate(n=>n.decode());
const text=await p.locator('#reviewBody').innerText();assert(text.includes('Needs repair: Missing required function.'));assert(text.includes('Static checks passed; endpoint and behavior not verified.'));assert(text.includes('Generated logo draft, not quality-verified.'));
assert.equal(await p.locator('.build-logo-review').count(),1);assert.equal(await p.locator('.build-logo-review').getAttribute('alt'),'Generated app logo draft');
await p.locator('#reviewBody').evaluate(n=>{for(const a of n.getAnimations({subtree:true}))a.finish()});await p.screenshot({path:'/downloads/chatify-guided-review-contract-'+width+'.png',fullPage:true});await p.close();console.log('PASS guided helper/logo review',width);
}
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exitCode=1});
