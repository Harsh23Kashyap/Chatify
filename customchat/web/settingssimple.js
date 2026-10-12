/* A small everyday surface over the same controls and values. */
(()=>{
 const body=document.body;let baseline=null;fetch('/api/settings').then(r=>r.json()).then(d=>{baseline=d.settings;refresh()}).catch(()=>{});
 function advanced(){window.CCSettingsSetMode?.('advanced');document.dispatchEvent(new CustomEvent('cc-settings-mode'));}
 function refresh(){
  const simple=body.classList.contains('simple'),state=window.CCSettingsSimple?.state();
  const search=document.querySelector('.settings-search');search?.classList.add('search-open');

  for(const section of document.querySelectorAll('#col>section.tile,#look>section.tile')){
   if(!section.querySelector(':scope>.simple-more')){const b=document.createElement('button');b.type='button';b.className='simple-more mini';b.textContent=section.id==='sec-finish'?'Workspace tools':'More settings';b.onclick=advanced;section.append(b)}
  }
  const model=document.querySelector('#sec-model');if(model){
   if(!model.querySelector('#simpleProvider')){const label=document.createElement('label');label.className='simple-provider';label.textContent='Answer with';const select=document.createElement('select');select.id='simpleProvider';select.setAttribute('aria-label','Answer provider');const note=document.createElement('small');note.id='simpleProviderNote';note.className='h';select.onchange=()=>{window.CCSettingsSimple?.select(select.value);refresh();};label.append(select,note);model.querySelector('#seg').before(label)}
   const select=model.querySelector('#simpleProvider');if(state?.provider){const signature=state.provider;if(select.dataset.signature!==signature){select.dataset.signature=signature;select.replaceChildren(...Object.entries(state.names).map(([key,name])=>{const o=document.createElement('option');o.value=key;o.textContent=name;o.selected=key===state.provider;return o}));}select.disabled=!state.canEdit;model.querySelector('#simpleProviderNote').textContent=state.provider==='mock'?'Demo works offline. No key needed.':'Provider selected. Connection not verified.';}


   if(!model.querySelector('.evidence-range')){const ends=document.createElement('small');ends.className='range-endpoints evidence-range';ends.textContent='1 passage · 20 passages';model.querySelector('#topk').closest('label').append(ends)}
   for(const node of model.children){node.classList.toggle('simple-model-hidden',!node.matches('.head,.simple-provider,.two,#apply,#keybox,#model,.simple-more,label[for=modelPick],.keyrow:has(#modelPick),.testrow,label.check'))}
   const key=model.querySelector('#keybox');if(key&&state)key.classList.toggle('simple-key-needed',state.provider!=='mock'&&state.provider!=='ollama'&&!!state.key?.needed&&!state.key?.has);
   const head=model.querySelector('.head b');if(head)head.textContent=simple?'Answer settings':'Model';
   const temperature=model.querySelector('#temp')?.closest('label');if(temperature&&state){temperature.classList.toggle('simple-temperature-hidden',state.provider==='mock'||(state.provider==='openai'&&/^(gpt-[56]|o[134])/.test((state.model||'').toLowerCase())));if(!temperature.querySelector('.range-endpoints')){const ends=document.createElement('small');ends.className='range-endpoints';ends.textContent='More precise · More creative';temperature.append(ends)}}
   const temp=model.querySelector('.range-setting-label');if(temp)temp.textContent=simple?'Answer style':'Temperature';
   const label=model.querySelector('#topk')?.closest('label');if(label){const text=label.querySelector('.range-setting-label');if(text)text.textContent=simple?'Evidence passages per answer':'Sources per answer'}
   const apply=model.querySelector('#apply');if(apply)apply.textContent=simple?'Save answer settings':'Apply';
   let scope=model.querySelector('.simple-save-scope');if(!scope){scope=document.createElement('small');scope.className='simple-save-scope h';scope.textContent='Saves answer settings only.';apply.after(scope)}
   let dirty=model.querySelector('#answerDirty');if(!dirty){dirty=document.createElement('small');dirty.id='answerDirty';dirty.className='simple-save-scope h';apply.before(dirty)}const changed=baseline&&state&&(state.provider!==baseline.provider||Number(model.querySelector('#temp').value)!==baseline.temperature||Number(model.querySelector('#topk').value)!==baseline.top_k||state.model!==baseline.model||model.querySelector('#rewrite').checked!==!!baseline.query_rewrite);dirty.textContent=changed?'Unsaved answer changes':'';

  }
  const workspace=document.querySelector('#sec-finish');if(workspace&&!workspace.querySelector('.simple-workspace')){const p=document.createElement('p');p.className='simple-workspace';p.textContent='Edit this Nerd here. Open the chat to try its current settings.';workspace.prepend(p)}
  if(body.dataset.settingsSection==='presets'){let note=document.querySelector('#sec-presets .simple-appearance-note');if(!note){note=document.createElement('small');note.className='simple-appearance-note h';note.textContent='Appearance changes save automatically. Presets change the look only.';document.querySelector('#presets').after(note)}const b=document.querySelector('#sec-presets .head b');if(b)b.textContent='Choose a look'}
 }
 document.addEventListener('cc-settings-nav-ready',refresh);document.addEventListener('cc-settings-mode',refresh);document.addEventListener('click',e=>{if(e.target.id==='apply')setTimeout(()=>fetch('/api/settings').then(r=>r.json()).then(d=>{baseline=d.settings;refresh()}),500);setTimeout(refresh,0)});document.addEventListener('input',refresh);document.addEventListener('change',refresh);new MutationObserver(()=>refresh()).observe(document.querySelector('#look'),{childList:true});setTimeout(refresh,800);setTimeout(refresh,1600);
})();
