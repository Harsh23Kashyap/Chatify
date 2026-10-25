// Ten bundled app configurations render their own palettes consistently
// (bar/heading/save share the brand color, profile surface matches the app
// paper, no horizontal scroll) in light and dark at three widths, and the
// final Markdown pass still renders streamed bold and ordered lists.
// App list and configs are derived from the repo's apps/ directory at run
// time; each app is served from a scratch copy so no state lands in apps/.
const{chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright'),assert=require('node:assert/strict'),fs=require('fs'),os=require('os'),path=require('path'),cp=require('child_process');
const repo=path.join(__dirname,'..');
const PORT=Number(process.env.CHATIFY_PALETTE_PORT||18830);
const apps=JSON.parse(cp.execSync("python3 -c \"import os,yaml,json;print(json.dumps([{'dir':os.path.join('apps',d),'title':yaml.safe_load(open(os.path.join('apps',d,'app.yaml')))['app']['title']} for d in sorted(os.listdir('apps')) if os.path.isfile(os.path.join('apps',d,'app.yaml')) and d!='hosted']))\"",{cwd:repo,maxBuffer:1<<20}).toString()).slice(0,10);
assert.equal(apps.length,10,'expected ten bundled app configurations');
async function waitReady(){const end=Date.now()+90000;for(;;){try{const r=await fetch('http://127.0.0.1:'+PORT+'/api/theme');if(r.ok)return}catch{}if(Date.now()>end)throw new Error('app server did not start on '+PORT);await new Promise(r=>setTimeout(r,400))}}
(async()=>{const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const [i,app]of apps.entries()){
 const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'cc35-'));
 fs.cpSync(path.join(repo,app.dir),path.join(scratch,'app'),{recursive:true});
 const srv=cp.spawn('python3',['-m','chatify','run',path.join(scratch,'app','app.yaml'),'--host','127.0.0.1','--port',String(PORT),'--no-browser'],{cwd:repo,env:{...process.env,PYTHONPATH:repo},stdio:'ignore'});
 try{
  await waitReady();
  for(const mode of['light','dark'])for(const width of[320,390,1280]){const p=await b.newPage({viewport:{width,height:950},reducedMotion:'reduce'});
   await p.addInitScript(m=>{localStorage.setItem('cc_tour','1');localStorage.setItem('cc_mode',m)},mode);
   await p.goto('http://127.0.0.1:'+PORT);
   await p.waitForFunction(()=>window.CCTheme?.value);
   await p.locator('#profileBtn').evaluate(n=>n.click());
   await p.locator('.profile-design').waitFor();
   await p.waitForTimeout(700);
   let v=await p.evaluate(()=>{const g=s=>getComputedStyle(document.querySelector(s));const hex=x=>{const m=x.match(/^rgba?\(([^)]+)\)/);if(!m)return x;return "#"+m[1].split(/[, ]+/).map(Number).slice(0,3).map(n=>n.toString(16).padStart(2,"0")).join("")};
    const brand=g('.bar').color,bg=g('.profile-design').backgroundColor;
    const shaded=window.CCBrand?CCBrand.shade(hex(brand),hex(bg)):brand;
    return{brand:hex(brand),head:hex(g('.profile-design h2').color),bg:hex(bg),paper:hex(g('.app').backgroundColor),save:hex(g('.profile-save').backgroundColor),shadedHead:shaded}});
   // The heading tracks the app palette directly, or through the deliberate
   // readableFonts auto-contrast shade when the brand is too light on paper.
   assert.ok(v.head===v.brand||v.head===v.shadedHead,app.title+': heading '+v.head+' is neither brand '+v.brand+' nor its contrast shade '+v.shadedHead);
   assert.equal(v.bg,v.paper,app.title);
   assert.equal(v.save,v.brand,app.title);
   assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
   if(width===390&&i<3)await p.screenshot({path:'/downloads/cc35-actual-'+i+'-'+mode+'.png'});
   await p.getByRole('button',{name:'Cancel',exact:true}).click();
   await p.locator('#q').fill('Formatting test');
   await p.route('**/api/ask-stream',r=>r.fulfill({contentType:'application/x-ndjson',body:JSON.stringify({type:'token',data:'**Safe bold**\n\n1. First\n2. Second'})+'\n'+JSON.stringify({type:'done',data:{id:'fixture',chat:'fixture',topic:'fixture',question:'Formatting test',answer:'**Safe bold**\n\n1. First\n2. Second',evidence:[],followups:[]}})+'\n'}));
   await p.locator('#send').click();
   await p.locator('#thread strong').waitFor();
   assert.equal(await p.locator('#thread ol li').count(),2);
   await p.unrouteAll({behavior:'ignoreErrors'});
   await p.close()}
 }finally{srv.kill('SIGTERM');await new Promise(r=>setTimeout(r,600));try{srv.kill('SIGKILL')}catch{}fs.rmSync(scratch,{recursive:true,force:true})}
}
await b.close();
console.log('PASS ten independent app configurations/theme palettes lightdark3203901280 profile and final Markdown60cases')})().catch(e=>{console.error(e);process.exit(1)});
