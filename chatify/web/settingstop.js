/* Top-level Configuration view: Build with AI (default) or Manual settings. */
(()=>{
  const KEY='cc_cfg_top_v1';
  const bar=document.createElement('div');bar.className='cfg-path-choice';bar.id='cfgtop';bar.setAttribute('role','navigation');bar.setAttribute('aria-label','Configuration view');
  const mk=(mode,label)=>{const b=document.createElement('button');b.type='button';b.dataset.t=mode;b.innerHTML=label;return b};
  const bBuilder=mk('builder','<span aria-hidden="true">&#10022;</span> Build with AI <small>Describe an app instead</small>');
  const bManual=mk('manual','<small>Prefer to edit by hand?</small><span>Open manual settings</span>');
  bar.append(bBuilder,bManual);
  const lead=document.getElementById('lead');(lead||document.querySelector('main.card')).after(bar);
  function set(mode,persist){
    const m=mode==='manual'?'manual':'builder';
    document.body.classList.toggle('cfgtop-builder',m==='builder');
    document.body.classList.toggle('cfgtop-manual',m==='manual');
    for(const b of [bBuilder,bManual]){const on=b.dataset.t===m;b.setAttribute('aria-current',on?'page':'false');b.classList.toggle('on',on);b.hidden=on}
    if(persist!==false){try{localStorage.setItem(KEY,m)}catch(e){} if(m==='builder'&&location.hash.startsWith('#sec-'))history.replaceState(null,'',location.pathname+location.search)}
    document.dispatchEvent(new CustomEvent('cc-settings-topmode',{detail:m}));
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
    const head=document.createElement('div');head.className='cfg-preview-head';head.innerHTML='<strong>A little break</strong><small>Optional silent animation</small>';
    const video=document.createElement('video');video.id='cfgBuildVideo';video.playsInline=true;video.muted=true;video.preload='none';video.poster=(window.CC_APP_BASE||'')+'/media/bunny-poster.jpg';video.setAttribute('aria-label','Optional silent Big Buck Bunny excerpt');
    const copy=document.createElement('p');copy.className='cfg-video-copy';copy.textContent='Let your idea take shape. Play a short video while your app builds.';
    const controls=document.createElement('div');controls.className='cfg-video-controls';const play=document.createElement('button');play.type='button';play.className='go ghost';play.textContent='Play video';const next=document.createElement('button');next.type='button';next.className='go ghost';next.textContent='Next video';controls.append(play,next);
    const clips=['bunny-meadow.mp4','bunny-morning.mp4'];let clip=0,playSequence=0;const pause=()=>{playSequence++;video.pause();play.textContent='Play video';};
    play.onclick=async()=>{if(!video.paused){pause();return;}if(!video.getAttribute('src'))video.src=(window.CC_APP_BASE||'')+'/media/'+clips[clip];const seq=++playSequence;try{await video.play();if(seq===playSequence){play.textContent='Pause video';copy.textContent='Silent video playing. Pause or skip whenever you like.';}}catch{if(seq===playSequence)copy.textContent='Video could not play. Your build is unaffected.';}};
    next.onclick=()=>{pause();clip=(clip+1)%clips.length;video.removeAttribute('src');video.load();copy.textContent='Next silent clip selected. Choose Play when ready.';};video.onended=pause;video.onerror=()=>{pause();copy.textContent='Video is unavailable. Your build continues normally.';};document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});document.addEventListener('cc-builder-window-open',pause);document.addEventListener('cc-builder-finished',pause);document.addEventListener('cc-settings-topmode',e=>{if(e.detail!=='builder')pause();});
    const credit=document.createElement('p');credit.className='cfg-video-credit';const link=document.createElement('a');link.href='https://peach.blender.org/about/';link.target='_blank';link.rel='noopener noreferrer';link.textContent='(c) 2008 Blender Foundation / www.bigbuckbunny.org · CC BY 3.0';credit.append(link);preview.append(head,video,copy,controls,credit);studio.append(preview);
  }
  window.CCSettingsTop={set:set};
  let initial='builder';try{initial=localStorage.getItem(KEY)||'builder'}catch(e){}
  if(location.hash.startsWith('#sec-'))initial='manual';
  set(initial,false);
  window.addEventListener('popstate',()=>{if(location.hash.startsWith('#sec-'))set('manual',false)});
})();
