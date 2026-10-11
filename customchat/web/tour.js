/* Shared local walkthrough. It never edits settings or contacts a model. */
(() => {
  'use strict';
  const node=(tag,cls,text)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text)n.textContent=text;return n;};
  const stored=k=>{try{return localStorage.getItem(k)}catch{return null}};
  const mark=k=>{try{localStorage.setItem(k,'1')}catch{}};
  async function show({key,title,steps,replay=false,onClose}) {
    if(!replay){try{const r=await fetch("/api/guide-seen"),d=await r.json();if(d[key])return}catch{}}
    if(document.querySelector('.cc-tour')||(!replay&&stored(key)))return;
    mark(key);fetch('/api/guide-seen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({key})}).catch(()=>{});
    const before=document.activeElement,scroll=window.scrollY;
    const dialog=node('dialog','cc-tour');dialog.setAttribute('aria-label',title);
    const glow=node('div','cc-tour-focus');glow.setAttribute('aria-hidden','true');document.body.append(glow);
    let i=0,target=null;
    const motion=()=>!matchMedia('(prefers-reduced-motion: reduce)').matches;
    function locate(){
      if(!target){glow.hidden=true;dialog.dataset.edge='none';dialog.style.left='16px';dialog.style.top='16px';return}
      const r=target.getBoundingClientRect(),top=Math.max(8,r.top),bottom=Math.min(innerHeight-8,r.bottom),left=Math.max(8,r.left),right=Math.min(innerWidth-8,r.right);
      glow.hidden=bottom<=top||right<=left;Object.assign(glow.style,{top:top+'px',left:left+'px',width:Math.max(0,right-left)+'px',height:Math.max(0,bottom-top)+'px'});
      const w=dialog.offsetWidth,h=dialog.offsetHeight,gap=20,pad=16;let x,y,edge;
      if(innerWidth>760 && innerWidth-r.right>=w+gap+pad){x=r.right+gap;y=Math.max(pad,Math.min(innerHeight-h-pad,r.top+6));edge='left'}
      else if(innerWidth>760 && r.left>=w+gap+pad){x=r.left-w-gap;y=Math.max(pad,Math.min(innerHeight-h-pad,r.top+6));edge='right'}
      else if(innerHeight-r.bottom>=h+gap+pad){x=Math.max(pad,Math.min(innerWidth-w-pad,r.left));y=r.bottom+gap;edge='top'}
      else if(r.top>=h+gap+pad){x=Math.max(pad,Math.min(innerWidth-w-pad,r.left));y=r.top-h-gap;edge='bottom'}
      else{x=Math.max(pad,(innerWidth-w)/2);y=Math.max(pad,innerHeight-h-pad);edge='top'}
      dialog.dataset.edge=edge;Object.assign(dialog.style,{left:x+'px',top:y+'px',bottom:'auto',right:'auto'});
    }
    function end(){mark(key);dialog.close();dialog.remove();glow.remove();window.removeEventListener('resize',locate);window.removeEventListener('scroll',locate);window.scrollTo({top:scroll,behavior:'instant'});if(before?.isConnected)before.focus({preventScroll:true});onClose?.();}
    function draw(){
      const s=steps[i];target=document.querySelector(s.target||'');
      if(target&&(!target.getClientRects().length||getComputedStyle(target).display==='none'))target=document.querySelector('#settingsNavTop')||document.querySelector('#cfgmode');
      target?.scrollIntoView({block:'start',behavior:'instant'});
      const header=node('header','cc-tour-head'),count=node('span','cc-tour-count',`${i+1} / ${steps.length}`),skip=node('button','cc-tour-skip','Skip');skip.type='button';skip.onclick=end;
      header.append(node('span','cc-tour-label',title),count,skip);
      const scene=node('div','cc-tour-scene');scene.setAttribute('aria-hidden','true');scene.dataset.kind=s.kind||'tabs';
      const rail=node('div','cc-tour-rail');(s.tabs||['Ask','Sources','Answer']).forEach((t,j)=>{const chip=node('span','cc-tour-tab'+(j===0?' active':''),t);chip.style.setProperty('--n',j);rail.append(chip)});
      const sample=node('div','cc-tour-sample');sample.append(node('span','cc-tour-orb',s.icon||'✦'),node('div','cc-tour-lines'));for(let j=0;j<3;j++)sample.lastChild.append(node('i'));
      scene.append(rail,sample);
      const content=node('div','cc-tour-content');const h=node('h2','',s.title);h.id='cc-tour-title';dialog.setAttribute('aria-labelledby',h.id);content.append(h,node('p','',s.text));
      const progress=node('div','cc-tour-progress');progress.setAttribute('aria-label',`Step ${i+1} of ${steps.length}`);steps.forEach((_,j)=>progress.append(node('i',j<=i?'done':'')));
      const footer=node('footer','cc-tour-actions'),back=node('button','cc-tour-back','Back'),next=node('button','cc-tour-next',i===steps.length-1?'Done':'Next');back.type=next.type='button';back.disabled=i===0;back.onclick=()=>{i--;draw()};next.onclick=()=>{if(i===steps.length-1)end();else{i++;draw()}};footer.append(back,next);
      dialog.replaceChildren(header,content,progress,footer);locate();requestAnimationFrame(locate);
      if(motion())dialog.animate([{opacity:.5,transform:'translateY(10px)'},{opacity:1,transform:'none'}],{duration:240,easing:'ease-out'});
      next.focus({preventScroll:true});
    }
    dialog.addEventListener('cancel',e=>{e.preventDefault();end()});
    dialog.addEventListener('keydown',e=>{if(e.key==='ArrowRight'){e.preventDefault();dialog.querySelector('.cc-tour-next').click()}else if(e.key==='ArrowLeft'&&i){e.preventDefault();i--;draw()}});
    window.addEventListener('resize',locate);window.addEventListener('scroll',locate,{passive:true});document.body.append(dialog);dialog.showModal();draw();
  }
  const configSteps=[
    {title:'Four tabs, one setup',text:'Workspace loads and shares your Nerd. Answers controls models and sources. Appearance changes the look. Maintenance checks documents and limits. The selected tab shows its smaller sections beside the editor, or above it on a phone.',target:'#settingsNavTop',tabs:['Workspace','Answers','Appearance','Maintenance']},
    {title:'Everyday or detailed',text:'Simple shows useful everyday controls. Advanced adds specialist settings and fine design controls. Switching levels keeps your unsaved values. Find any setting searches labels and opens the right section, including Advanced when needed.',target:'#cfgmode',tabs:['Simple','Advanced','Find']},
    {title:'Choose who answers',text:'In Answers, Model and key selects the provider and model. Demo works offline without a key or a real model. A required missing key appears when needed. Test connection checks the selected setup; selecting a provider alone does not verify it.',target:'#menu',tabs:['Provider','Model','Test']},
    {title:'Set answer behavior',text:'Evidence passages per answer controls how much retrieved text goes to the model, not the number of publishers. Answer style appears only where the provider supports it. Follow-up rewriting helps search a new question. Save answer settings commits this section; unsaved changes stay marked if a save fails.',target:'#menu',tabs:['Evidence','Follow-ups','Save']},
    {title:'Sources, prompts and helpers',text:'The Answers sections include Sources and APIs, Prompts and Code helpers. Open a section to see its full controls. Source keys, prompt drafts and helper code have their own save actions. Generated drafts need review; a static code check is not a security sandbox.',target:'#menu',tabs:['Sources','Prompts','Helpers']},
    {title:'Make it yours',text:'Appearance starts with ready-made looks. Presets change appearance only, and appearance changes save automatically. More settings opens colors, fonts, wording, background and motion. Named setups also restore model settings, but not prompts, sources or keys.',target:'#settingsNavTop',tabs:['Presets','Details','Saved setups']},
    {title:'Load, share and maintain',text:'Workspace holds Load and share, imported workspaces, changes, backups and test questions. An exported bundle includes configured local documents, not keys or private chats: review its contents before sharing. Maintenance contains document checks and usage limits. A dollar cap is not a verified billing meter.',target:'#settingsNavTop',tabs:['Workspace','Documents','Limits']},
    {title:'Preview when you want it',text:'Show chat preview makes the optional preview visible; it does not send a chat message. Open your chat from Workspace when ready. Guide replays this walkthrough at any time. Reading the guide does not change your settings.',target:'.preview-toggle',tabs:['Preview','Chat','Guide']}
  ];
  const chatSteps=[
    {title:'Ask from your sources',text:'Add documents or a web link, then ask a question. Answers use the retrieved sources; check citations for important facts.',target:'#q',tabs:['Ask','Retrieve','Cite'],icon:'⌕'},
    {title:'Keep the conversation going',text:'Follow-ups use bounded context from this conversation. Start a new conversation for a fresh subject. History is not unlimited recall.',target:'#newTopic',tabs:['Question','Follow-up','Context'],icon:'↻'},
    {title:'Choose what stays with you',text:'Temporary chat saves no conversation. My profile adds optional background to saved chats. Configuration controls the model, sources and look.',target:'#profileBtn',tabs:['Temporary','Profile','Configure'],icon:'☺'}
  ];
  window.CCTour={chat:(replay=false,onClose)=>show({key:'cc_tour',title:'Quick tour',steps:chatSteps,replay,onClose}),config:(replay=false)=>show({key:'cc_cfg_tour_v1',title:'Configuration guide',steps:configSteps,replay})};
})();
