/* Top-level Configuration view: Build with AI (default) or Manual settings. */
(()=>{
  const KEY='cc_cfg_top_v1';
  const bar=document.createElement('div');bar.className='cfg-path-choice';bar.id='cfgtop';bar.setAttribute('role','navigation');bar.setAttribute('aria-label','Configuration view');
  const mk=(mode,label)=>{const b=document.createElement('button');b.type='button';b.dataset.t=mode;b.innerHTML=label;return b};
  const bBuilder=mk('builder','<span aria-hidden="true">&#8592;</span> Back to Build with AI');
  const bManual=mk('manual','Prefer to edit by hand? <span>Open manual settings &#8599;</span>');
  bar.append(bBuilder,bManual);
  const lead=document.getElementById('lead');(lead||document.querySelector('main.card')).after(bar);
  function set(mode,persist){
    const m=mode==='manual'?'manual':'builder';
    document.body.classList.toggle('cfgtop-builder',m==='builder');
    document.body.classList.toggle('cfgtop-manual',m==='manual');
    for(const b of [bBuilder,bManual]){const on=b.dataset.t===m;b.setAttribute('aria-current',on?'page':'false');b.classList.toggle('on',on)}
    if(persist!==false){try{localStorage.setItem(KEY,m)}catch(e){} if(m==='builder'&&location.hash.startsWith('#sec-'))history.replaceState(null,'',location.pathname+location.search)}
    document.dispatchEvent(new CustomEvent('cc-settings-topmode',{detail:m}));
  }
  bar.addEventListener('click',e=>{const b=e.target.closest('button[data-t]');if(b)set(b.dataset.t)});
  /* Any navigation into a manual section (search results, guide, deep links, todo shortcuts) opens the Manual view. */
  document.addEventListener('click',e=>{const t=e.target;if(t.closest&&t.closest('#menu a,.category-tabs button'))set('manual')},true);
  const hero=document.querySelector('.builder-hero');
  if(hero){
    const studio=document.createElement('section');studio.className='cfg-studio';studio.setAttribute('aria-label','Build your app');hero.before(studio);studio.append(hero);
    hero.querySelector('.builder-hero-title').textContent='What would you like to build?';
    hero.querySelector('.builder-hero-sub').textContent='Describe your idea. AI drafts the setup, then you review each change.';
    hero.querySelector('.builder-hero-sub-m').textContent='Describe your idea. Review the setup before saving.';
    const composer=document.createElement('div');composer.className='cfg-composer';
    const label=document.createElement('label');label.htmlFor='cfgIdea';label.textContent='Your app idea';
    const idea=document.createElement('textarea');idea.id='cfgIdea';idea.rows=4;idea.maxLength=4000;idea.placeholder='A diet assistant that answers from my nutrition guidelines, explains its sources, and helps me plan meals...';
    composer.append(label,idea);hero.querySelector('.builder-hero-copy').after(composer);
    const entry=hero.querySelector('.app-builder-open');entry.querySelector('span').textContent='Build with AI';
    entry.addEventListener('click',()=>{if(idea.value.trim())queueMicrotask(()=>{const brief=document.getElementById('builderBrief');if(brief&&!brief.value.trim()){brief.value=idea.value.trim();brief.dispatchEvent(new Event('input',{bubbles:true}))}})});
    hero.querySelector('.builder-hero-note').textContent='Review first. Nothing changes until you confirm.';
    const preview=document.createElement('aside');preview.className='cfg-chat-preview';
    const head=document.createElement('div');head.className='cfg-preview-head';head.innerHTML='<strong>Your chat app</strong><small>Sample preview · no AI request</small>';
    const frame=document.createElement('iframe');frame.title='Chat app sample preview';frame.src='./?preview=1';
    frame.addEventListener('load',()=>{try{const st=document.createElement('style');st.textContent='html body header.toolbar{display:none!important} html body .app{height:100vh!important;min-height:0!important}';frame.contentDocument.head.append(st)}catch(e){}});preview.append(head,frame);studio.append(preview);
  }
  window.CCSettingsTop={set:set};
  let initial='builder';try{initial=localStorage.getItem(KEY)||'builder'}catch(e){}
  if(location.hash.startsWith('#sec-'))initial='manual';
  set(initial,false);
  window.addEventListener('popstate',()=>{if(location.hash.startsWith('#sec-'))set('manual',false)});
})();
