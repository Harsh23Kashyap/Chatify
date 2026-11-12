const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
// Locks in the palette unification: no legacy pine/lime may render anywhere on the shared pages.
const GREENS=['23, 63, 53','215, 239, 114','127, 174, 60','40, 167, 69','32, 201, 151','15, 46, 38'];
const PROPS=['color','backgroundColor','borderTopColor','borderBottomColor','outlineColor','accentColor','caretColor','boxShadow'];
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const mode of ['light','dark']){
  for(const page of ['about.html','settings.html','run-locally.html','build.html']){
    const p=await b.newPage({viewport:{width:1366,height:768}});
    await p.goto(process.env.CHATIFY_TEST_URL+'/'+page,{waitUntil:'domcontentloaded'});
    await p.evaluate(m=>localStorage.setItem('cc_mode',m),mode);
    await p.reload({waitUntil:'domcontentloaded'});
    await p.waitForTimeout(1200);
    const hits=await p.evaluate(({GREENS,PROPS})=>{const out=[];document.querySelectorAll('*').forEach(el=>{const r=el.getBoundingClientRect();if(r.width<2||r.height<2)return;const cs=getComputedStyle(el);for(const prop of PROPS){const v=cs[prop];if(v&&GREENS.some(g=>v.includes(g)))out.push(prop+'='+v+' <'+el.tagName.toLowerCase()+'>')}});return[...new Set(out)]},{GREENS,PROPS});
    assert.deepEqual(hits,[],mode+' '+page+' renders zero legacy green: '+hits.join(' | '));
    await p.close();
  }
}
// The settings toggle track reads the shared line token, not a green tint
const p=await b.newPage({viewport:{width:1366,height:768}});
await p.goto(process.env.CHATIFY_TEST_URL+'/settings.html',{waitUntil:'domcontentloaded'});
await p.evaluate(()=>localStorage.setItem('cc_mode','light'));
await p.reload({waitUntil:'domcontentloaded'});await p.waitForTimeout(1200);
const track=await p.evaluate(()=>{const el=document.querySelector('input[type=checkbox]');return el?getComputedStyle(el).backgroundColor:null});
assert.equal(track,'rgb(216, 203, 194)','toggle track uses --ui-line, got '+track);
await b.close();console.log('PASS shared surfaces: zero legacy green computed on about/settings/run-locally/build in light+dark, toggle track on shared tokens')})().catch(e=>{console.error(e);process.exit(1)});
