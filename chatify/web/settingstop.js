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
    setText('.builder-hero-sub','Describe your idea. AI drafts the setup, then you review each change.');
    setText('.builder-hero-sub-m','Describe your idea. Review the setup before saving.');
    const composer=document.createElement('div');composer.className='cfg-composer';
    const label=document.createElement('label');label.htmlFor='cfgIdea';label.textContent='Your app idea';
    const idea=document.createElement('textarea');idea.id='cfgIdea';idea.rows=4;idea.maxLength=4000;idea.placeholder='A diet assistant that answers from my nutrition guidelines, explains its sources, and helps me plan meals...';
    composer.append(label,idea);const heroCopy=hero.querySelector('.builder-hero-copy');(heroCopy||hero).after(composer);
    const entry=hero.querySelector('.app-builder-open');if(entry){const entryLabel=entry.querySelector('span');if(entryLabel)entryLabel.textContent='Build with AI';
    entry.addEventListener('click',()=>{if(idea.value.trim())queueMicrotask(()=>{const brief=document.getElementById('builderBrief');if(brief&&!brief.value.trim()){brief.value=idea.value.trim();brief.dispatchEvent(new Event('input',{bubbles:true}))}})})}
    const costNote=document.createElement('p');costNote.className='builder-hero-cost h';costNote.textContent='AI drafting uses your saved model key; requests may cost money. Nothing is saved until you review.';composer.append(costNote);
    const heroExamples=[idea.placeholder,'A study buddy that quizzes me from my own lecture notes and cites the page it used...','A support assistant that answers customer questions from our help center articles...','A research aide that reads papers I upload and answers with citations...'];let hx=0;setInterval(()=>{if(idea.value||document.activeElement===idea||document.hidden)return;hx=(hx+1)%heroExamples.length;idea.placeholder=heroExamples[hx]},4500);
    setText('.builder-hero-note','Review first. Nothing changes until you confirm.');
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
