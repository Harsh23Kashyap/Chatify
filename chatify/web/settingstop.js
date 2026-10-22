/* Top-level Configuration view: Build with AI (default) or Manual settings. */
(()=>{
  const KEY='cc_cfg_top_v1';
  const bar=document.createElement('div');bar.className='seg mini toptabs';bar.id='cfgtop';bar.setAttribute('role','radiogroup');bar.setAttribute('aria-label','Configuration view');
  const mk=(mode,label)=>{const b=document.createElement('button');b.type='button';b.dataset.t=mode;b.setAttribute('role','radio');b.innerHTML=label;return b};
  const bBuilder=mk('builder','<span aria-hidden="true">&#10022;</span> Build with AI');
  const bManual=mk('manual','Manual settings');
  bar.append(bBuilder,bManual);
  const lead=document.getElementById('lead');(lead||document.querySelector('main.card')).after(bar);
  function set(mode,persist){
    const m=mode==='manual'?'manual':'builder';
    document.body.classList.toggle('cfgtop-builder',m==='builder');
    document.body.classList.toggle('cfgtop-manual',m==='manual');
    for(const b of [bBuilder,bManual]){const on=b.dataset.t===m;b.setAttribute('aria-checked',String(on));b.classList.toggle('on',on)}
    if(persist!==false){try{localStorage.setItem(KEY,m)}catch(e){} if(m==='builder'&&location.hash.startsWith('#sec-'))history.replaceState(null,'',location.pathname+location.search)}
    document.dispatchEvent(new CustomEvent('cc-settings-topmode',{detail:m}));
  }
  bar.addEventListener('click',e=>{const b=e.target.closest('button[data-t]');if(b)set(b.dataset.t)});
  /* Any navigation into a manual section (search results, guide, deep links, todo shortcuts) opens the Manual view. */
  document.addEventListener('click',e=>{const t=e.target;if(t.closest&&t.closest('#menu a,.category-tabs button'))set('manual')},true);
  window.CCSettingsTop={set:set};
  let initial='builder';try{initial=localStorage.getItem(KEY)||'builder'}catch(e){}
  if(location.hash.startsWith('#sec-'))initial='manual';
  set(initial,false);
  window.addEventListener('popstate',()=>{if(location.hash.startsWith('#sec-'))set('manual',false)});
})();
