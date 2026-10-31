// Actual bundled media; the forced policy path checks fallback without a new sound button.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'/tmp/cc-ui-tools/node_modules/playwright-core');
const assert=require('node:assert/strict');
(async()=>{const browser=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
for(const denySound of [false,true]){const page=await browser.newPage({viewport:{width:1280,height:900}});
await page.addInitScript(({denySound})=>{localStorage.setItem('cc_cfg_tour_v1','1');window.storyPlayAttempts=[];const play=HTMLMediaElement.prototype.play;HTMLMediaElement.prototype.play=function(){if(this.closest('.cfg-video-break')){storyPlayAttempts.push({muted:this.muted,controls:this.controls});if(denySound&&!this.muted)return Promise.reject(new DOMException('Forced browser policy','NotAllowedError'))}return play.call(this)}},{denySound});
await page.goto(process.env.CHATIFY_TEST_URL+'/settings.html');await page.getByRole('button',{name:'Build with AI',exact:true}).first().click();
const host=page.locator('.cfg-video-break'),video=host.locator('video');await page.waitForFunction(()=>document.querySelector('.cfg-video-break video')?.currentTime>0.2);
assert.equal(await host.getByRole('heading').innerText(),'Features of Chatify');assert.equal(await host.getByRole('combobox').count(),0);assert.equal(await host.locator('label').count(),0);assert.equal(await video.evaluate(v=>v.controls),true);assert.equal(await host.getByRole('button',{name:/sound/i}).count(),0);assert(!/Playing illustrated story|Playing muted|Pause any time|Turn sound on/.test(await host.innerText()));
assert.equal(await host.locator('[role=status]').isVisible(),false);const attempts=await page.evaluate(()=>storyPlayAttempts);assert.equal(attempts[0].muted,false,'audible playback is attempted initially');if(denySound){assert(attempts.some(a=>a.muted),'policy rejection falls back to muted playback');assert.equal(await video.evaluate(v=>v.muted),true)}
// Native media control state remains functional without a second custom sound control.
await video.evaluate(v=>{v.muted=true});assert.equal(await video.evaluate(v=>v.muted),true);await video.evaluate(v=>{v.muted=false});assert.equal(await video.evaluate(v=>v.muted),false);
await page.getByRole('button',{name:'How-to',exact:true}).click();assert.equal(await video.evaluate(v=>v.paused),true);assert.equal(await page.locator('#cfgWalkthroughVideo').evaluate(v=>v.paused),true);
if(!denySound){await page.getByRole('button',{name:'Build with AI',exact:true}).first().click();await video.scrollIntoViewIfNeeded();await page.screenshot({path:'/downloads/chatify-features-simple-local.png'});}await page.close();}
await browser.close();console.log('PASS actualstory clean-copy nativecontrols audible-first muted-policy-fallback off-route manualwalkthrough');})().catch(e=>{console.error(e);process.exit(1)});
