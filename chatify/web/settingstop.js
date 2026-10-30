/* Top-level Configuration view: Build with AI (default) or Manual settings. */
(()=>{
  const KEY='cc_cfg_top_v1';
  const bar=document.createElement('div');bar.className='cfg-path-choice';bar.id='cfgtop';bar.setAttribute('role','navigation');bar.setAttribute('aria-label','Configuration view');
  const mk=(mode,label)=>{const b=document.createElement('button');b.type='button';b.dataset.t=mode;b.innerHTML=label;return b};
  const bBuilder=mk('builder','<span aria-hidden="true">&#10022;</span> Build with AI <small>Describe an app instead</small>');
  const bManual=mk('manual','Manual settings');
  bBuilder.textContent='Build with AI';
  const bGuide=mk('guide','How-to');
  const indicator=document.createElement('i');indicator.className='cfg-route-indicator';indicator.setAttribute('aria-hidden','true');bar.append(indicator,bBuilder,bManual,bGuide);
  function moveIndicator(){const b=bar.querySelector('button.on');if(b){indicator.style.width=b.offsetWidth+'px';indicator.style.height=b.offsetHeight+'px';indicator.style.transform='translate('+b.offsetLeft+'px,'+b.offsetTop+'px)'}}
  new ResizeObserver(moveIndicator).observe(bar);
  const guide=document.createElement('section');guide.id='cfgWalkthrough';guide.className='cfg-walkthrough';guide.hidden=true;guide.setAttribute('aria-label','How-to walkthroughs');
  const guideTitle=document.createElement('h2');guideTitle.textContent='Answer questions from a PDF';
  const guideNote=document.createElement('p');guideNote.textContent='Reconstructed functional walkthrough of a fictional print-support app: upload its handbook PDF, review the prompts, Save, open a separate local workspace, and check real answers against the PDF. Edited recording, not a real-time build or a deployed child service.';
  const guideVideo=document.createElement('video');guideVideo.id='cfgWalkthroughVideo';guideVideo.controls=true;guideVideo.playsInline=true;guideVideo.preload='none';guideVideo.poster=(window.CC_APP_BASE||'')+'/media/paperworks-walkthrough-poster.jpg';guideVideo.src=(window.CC_APP_BASE||'')+'/media/paperworks-walkthrough.mp4';guideVideo.setAttribute('aria-label','Paperworks Help: idea, reviewed AI draft, Save, separate local app and real cited answer');
  const guideChoice=document.createElement('label');guideChoice.className='cfg-walkthrough-choice';guideChoice.textContent='Choose a walkthrough';
  const guideSelect=document.createElement('select');guideSelect.setAttribute('aria-label','Choose a walkthrough');guideSelect.dataset.native='true';
  const walkthroughs=[{id:'paperworks',title:'PDF answers · Paperworks Help',heading:'Answer questions from a PDF',note:guideNote.textContent,video:'paperworks-walkthrough.mp4',poster:'paperworks-walkthrough-poster.jpg',label:guideVideo.getAttribute('aria-label')},{id:'signal-desk',title:'News answers · Signal Desk · narration incomplete',heading:'Answer questions from a news API',note:'Matching narrated walkthrough is incomplete and not available here yet. A reviewed local NewsAPI build: AI suggestions, explicit prompt and source review, Save, a separate workspace, masked private key configuration, manual controls, and a real model answer with its source opened. Developer access is for development/testing, with a 24-hour delay and excerpts rather than full articles. Edited recording; no generated helper execution or public deployment.',video:'signal-desk-walkthrough.mp4',poster:'signal-desk-walkthrough-poster.png',label:'Signal Desk: reviewed AI draft, masked NewsAPI key, manual settings and real cited answer'}];
  // Local media readiness is real browser state, not a simulated progress loop.
  const mediaStatus=document.createElement('p');mediaStatus.id='cfgMediaStatus';mediaStatus.className='cfg-media-status';mediaStatus.setAttribute('role','status');mediaStatus.setAttribute('aria-live','polite');
  const mediaRetry=document.createElement('button');mediaRetry.type='button';mediaRetry.className='go';mediaRetry.textContent='Retry video';mediaRetry.hidden=true;
  const mediaState=(state,text)=>{guideVideo.hidden=state==='error';mediaStatus.dataset.state=state;mediaStatus.textContent=text;mediaRetry.hidden=state!=='error'};
  mediaState('idle','Press Play to load the PDF walkthrough. No video downloads until you choose to play.');
  guideVideo.addEventListener('loadstart',()=>{if(guideVideo.preload==='none'&&guideVideo.paused)return;mediaState('loading','Loading walkthrough...')});
  guideVideo.addEventListener('waiting',()=>mediaState('loading','Loading walkthrough...'));
  guideVideo.addEventListener('playing',()=>mediaState('ready','Walkthrough playing. Use sound and fullscreen controls below.'));
  guideVideo.addEventListener('pause',()=>{if(guideVideo.readyState>=1&&!guideVideo.error)mediaState('ready','Walkthrough paused. Use Play to continue. Use sound and fullscreen controls below.')});
  guideVideo.addEventListener('loadedmetadata',()=>mediaState('ready','Walkthrough ready. Use Play, sound and fullscreen controls below.'));
  guideVideo.addEventListener('error',()=>mediaState('error','This walkthrough could not load. Retry checks the selected file again.'));
  mediaRetry.onclick=()=>{mediaState('loading','Loading walkthrough...');const item=walkthroughs.find(x=>x.id===guideSelect.value);guideVideo.src=(window.CC_APP_BASE||'')+'/media/'+item.video;guideVideo.load()};
  const revealGuideCopy=()=>{if(matchMedia('(prefers-reduced-motion: reduce)').matches||['none','calm'].includes(document.documentElement.dataset.motion))return;for(const n of[guideTitle,guideNote]){n.getAnimations().forEach(a=>a.cancel());n.animate([{opacity:.4,transform:'translateY(6px)'},{opacity:1,transform:'translateY(0)'}],{duration:220,easing:'cubic-bezier(.22,1,.36,1)'})}};
  for(const item of walkthroughs){const option=document.createElement('option');option.value=item.id;option.textContent=item.title;guideSelect.append(option)}
  guideSelect.onchange=()=>{const item=walkthroughs.find(x=>x.id===guideSelect.value);guideVideo.pause();mediaState('idle',item.id==='paperworks'?'Press Play to load the PDF walkthrough.':'This news walkthrough is not available here.');revealGuideCopy();guideTitle.textContent=item.heading;guideNote.textContent=item.note;guideVideo.src=(window.CC_APP_BASE||'')+'/media/'+item.video;guideVideo.poster=(window.CC_APP_BASE||'')+'/media/'+item.poster;guideVideo.setAttribute('aria-label',item.label);guideVideo.load()};guideChoice.append(guideSelect);
  document.addEventListener('visibilitychange',()=>{if(document.hidden)guideVideo.pause()});
  const guideBack=document.createElement('button');guideBack.type='button';guideBack.className='go';guideBack.textContent='Start building';guideBack.onclick=()=>set('builder');guide.append(guideChoice,guideTitle,guideNote,mediaStatus,mediaRetry,guideVideo,guideBack);
  const lead=document.getElementById('lead');(lead||document.querySelector('main.card')).after(bar);bar.after(guide);
  function set(mode,persist){
    const m=['manual','guide'].includes(mode)?mode:'builder';
    document.body.classList.toggle('cfgtop-guide',m==='guide');guide.hidden=m!=='guide';if(m!=='guide')guideVideo.pause();
    document.body.classList.toggle('cfgtop-builder',m==='builder');
    document.body.classList.toggle('cfgtop-manual',m==='manual');
    for(const b of [bBuilder,bManual,bGuide]){const on=b.dataset.t===m;b.setAttribute('aria-current',on?'page':'false');b.classList.toggle('on',on);b.hidden=false}
    if(persist!==false){try{localStorage.setItem(KEY,m)}catch(e){} if(m!=='manual'&&location.hash.startsWith('#sec-'))history.replaceState(null,'',location.pathname+location.search)}
    requestAnimationFrame(moveIndicator);document.dispatchEvent(new CustomEvent('cc-settings-topmode',{detail:m}));
  }
  bar.addEventListener('click',e=>{const b=e.target.closest('button[data-t]');if(b)set(b.dataset.t)});
  /* Any navigation into a manual section (search results, guide, deep links, todo shortcuts) opens the Manual view. */
  document.addEventListener('click',e=>{const t=e.target;if(t.closest&&t.closest('#menu a,.category-tabs button'))set('manual')},true);
  const setText=(sel,text)=>{const n=hero&&hero.querySelector(sel);if(n)n.textContent=text};
  const hero=document.querySelector('.builder-hero');
  if(hero){
    const studio=document.createElement('section');studio.className='cfg-studio';studio.setAttribute('aria-label','Build your app');hero.before(studio);studio.append(hero);
    setText('.builder-hero-title','What would you like to build?');
    setText('.builder-hero-sub','Describe your idea. AI drafts the setup for your review.');
    setText('.builder-hero-sub-m','Describe your idea. AI drafts the setup for your review.');
    const composer=document.createElement('div');composer.className='cfg-composer';
    const label=document.createElement('label');label.htmlFor='cfgIdea';label.textContent='Your app idea';
    const idea=document.createElement('textarea');idea.id='cfgIdea';idea.rows=4;idea.maxLength=4000;idea.placeholder='A diet assistant that answers from my nutrition guidelines, explains its sources, and helps me plan meals...';
    composer.append(label,idea);const heroCopy=hero.querySelector('.builder-hero-copy');(heroCopy||hero).after(composer);
    const entry=hero.querySelector('.app-builder-open');if(entry){const entryLabel=entry.querySelector('span');if(entryLabel)entryLabel.textContent='Build with AI';
    entry.addEventListener('click',()=>{if(idea.value.trim())queueMicrotask(()=>{const brief=document.getElementById('builderBrief');if(brief&&!brief.value.trim()){brief.value=idea.value.trim();brief.dispatchEvent(new Event('input',{bubbles:true}))}})})}
    const costNote=document.createElement('p');costNote.className='builder-hero-cost h';costNote.textContent='Uses your saved model key; requests may cost money. Creates a draft; your active app changes only after you review and confirm.';composer.append(costNote);
    const heroExamples=[idea.placeholder,'A study buddy that quizzes me from my own lecture notes and cites the page it used...','A support assistant that answers customer questions from our help center articles...','A research aide that reads papers I upload and answers with citations...'];let hx=0,heroTimer=null;const heroCalm=matchMedia('(prefers-reduced-motion: reduce)');const heroMotionAllowed=()=>!heroCalm.matches&&!['none','calm'].includes(document.documentElement.dataset.motion);const rotateHero=()=>{if(!heroMotionAllowed()||!document.body.classList.contains('cfgtop-builder')||idea.value||document.activeElement===idea||document.hidden)return;hx=(hx+1)%heroExamples.length;idea.placeholder=heroExamples[hx]};const startHero=()=>{clearInterval(heroTimer);heroTimer=null;if(document.documentElement.hasAttribute('data-motion')&&heroMotionAllowed())heroTimer=setInterval(rotateHero,4500)};heroCalm.addEventListener('change',startHero);new MutationObserver(startHero).observe(document.documentElement,{attributes:true,attributeFilter:['data-motion']});startHero();
    hero.querySelector('.builder-hero-note')?.remove();
    const preview=document.createElement('aside');preview.className='cfg-chat-preview cfg-video-break';preview.setAttribute('aria-label','Optional video break');
    const unavailable=document.createElement('p');unavailable.className='cfg-video-copy';unavailable.textContent='Feature stories are being rebuilt and reviewed. No video is available here yet; your build is unaffected.';preview.append(unavailable);studio.append(preview);window.CCVideoBreak?.mount(preview);

  }
  window.CCSettingsTop={set:set};
  let initial='builder';try{initial=localStorage.getItem(KEY)||'builder'}catch(e){}
  if(location.hash.startsWith('#sec-'))initial='manual';
  set(initial,false);
  window.addEventListener('popstate',()=>{if(location.hash.startsWith('#sec-'))set('manual',false)});
})();
