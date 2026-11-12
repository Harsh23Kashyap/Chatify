const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict');
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
const root=process.env.CHATIFY_TEST_URL;
const p=await b.newPage({viewport:{width:1280,height:900}});
// build.html is locked the same way as settings.html on a shared gallery app
await p.goto(root+'/alpha/build.html');
await p.getByRole('heading',{name:'This shared app is read-only'}).waitFor();
assert.equal(await p.locator('input,textarea,button,select').count(),0,'locked page exposes no editor');
// Locked configuration assets fail closed
for(const asset of ['/alpha/settings.js','/alpha/settings.css','/alpha/appbuilder.js']){
 const r=await p.request.get(root+asset);
 assert.equal(r.status(),403,asset+' is closed');
 assert.match((await r.json()).error,/read-only/,asset+' says why');
}
// Public config view admits the lock and hides key state
const cfg=await (await p.request.get(root+'/alpha/api/config')).json();
assert.equal(cfg.configuration_readonly,true,'config admits read-only');
assert.ok(!('key_present' in cfg.provider),'provider key state is not exposed');
// Configuration reads fail closed, and visitor-scoped reads need a visitor session
const anon=await b.newContext();
for(const api of ['/alpha/api/provider/status','/alpha/api/provider/key','/alpha/api/budget','/alpha/api/scopes']){
 const r=await anon.request.get(root+api);
 assert.equal(r.status(),403,api+' is closed without a visitor session');
}
const scopes=await anon.request.get(root+'/alpha/api/scopes');
assert.match((await scopes.json()).error,/Open the chat page first/,'scopes says how to start a session');
await anon.close();
// Public chat and health stay open
assert.equal((await p.request.get(root+'/alpha/api/health')).status(),200,'health stays open');
await p.goto(root+'/alpha/');await p.locator('#q').waitFor();
assert.equal((await p.request.get(root+'/alpha/api/scopes')).status(),200,'visitor reads open after the chat page sets the session');
await b.close();console.log('PASS shared read-only surface: build.html locked like settings, locked assets/APIs fail closed with reasons, key state hidden, public chat and health open')})().catch(e=>{console.error(e);process.exit(1)});
