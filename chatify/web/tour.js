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
      const s=steps[i];if(window.CCSettingsTop&&s.target){if(s.target==='.app-builder-open')window.CCSettingsTop.set('builder',false);else if(['#settingsNavTop','#menu','#cfgmode'].includes(s.target))window.CCSettingsTop.set('manual',false)}target=document.querySelector(s.target||'');
      if(target&&(!target.getClientRects().length||getComputedStyle(target).display==='none'))target=document.querySelector('#settingsNavTop')||document.querySelector('#cfgmode');
      target?.scrollIntoView({block:'start',behavior:'instant'});
      const header=node('header','cc-tour-head'),count=node('span','cc-tour-count',`${i+1} / ${steps.length}`),skip=node('button','cc-tour-skip','Skip');skip.type='button';skip.onclick=end;
      header.append(node('span','cc-tour-label',title),count,skip);
      const content=node('div','cc-tour-content');const h=node('h2','',s.title);h.id='cc-tour-title';dialog.setAttribute('aria-labelledby',h.id);content.append(h,node('p','',s.text));
      const progress=node('div','cc-tour-progress');progress.setAttribute('aria-label',`Step ${i+1} of ${steps.length}`);steps.forEach((_,j)=>progress.append(node('i',j<=i?'done':'')));
      const footer=node('footer','cc-tour-actions'),back=node('button','cc-tour-back','Back'),next=node('button','cc-tour-next',i===steps.length-1?'Done':'Next');back.type=next.type='button';back.disabled=i===0;back.onclick=()=>{i--;draw()};next.onclick=()=>{if(i===steps.length-1)end();else{i++;draw()}};footer.append(back,next);
      dialog.replaceChildren(header,content,progress,footer);locate();requestAnimationFrame(locate);
      if(motion())dialog.animate([{opacity:0},{opacity:1}],{duration:160,easing:'ease-out'});
      next.focus({preventScroll:true});
    }
    dialog.addEventListener('cancel',e=>{e.preventDefault();end()});
    dialog.addEventListener('keydown',e=>{if(e.key==='Escape'){e.preventDefault();e.stopPropagation();end()}else if(e.key==='ArrowRight'){e.preventDefault();dialog.querySelector('.cc-tour-next').click()}else if(e.key==='ArrowLeft'&&i){e.preventDefault();i--;draw()}});
    window.addEventListener('resize',locate);window.addEventListener('scroll',locate,{passive:true});document.body.append(dialog);dialog.show();draw();
  }
  const configSteps=[
    {title:'Start with Build with AI',text:'The easiest path. Describe your app in plain words and AI drafts the whole setup: name, look, prompts and suggested sources. Review the draft, validate it, then confirm Save. Nothing is saved automatically. On this site a model is already configured, so there is nothing to connect first.',target:'.app-builder-open',tabs:['Describe','Review','Save']},
    {title:'Four tabs, one setup',text:'Workspace loads, shares and backs up your app. Answers controls the model and sources. Appearance changes the look. Maintenance checks documents and limits.',target:'#settingsNavTop',tabs:['Workspace','Answers','Appearance','Maintenance']},
    {title:'Choose who answers',text:'In Answers, pick a provider card and a model. Test connection checks the setup. Demo works offline without a key or a real model.',target:'#menu',tabs:['Provider','Model','Test']},
    {title:'Everyday or detailed',text:'Simple shows the everyday controls. Advanced adds specialist settings. Switching keeps your unsaved values. Use Find a setting for free local matches as you type.',target:'#cfgmode',tabs:['Simple','Advanced','Find']},
    {title:'Preview when you want it',text:'Show chat preview makes the optional preview visible. Guide replays this walkthrough at any time; reading it changes nothing.',target:'.preview-toggle',tabs:['Preview','Chat','Guide']}
  ];
  const chatSteps=[
    {title:'Ask a question',text:'Type in the box at the bottom and press Enter. Answers come only from this app\'s sources, and each answer cites where it found the facts.',target:'#q',tabs:['Ask','Retrieve','Cite'],icon:'⌕'},
    {title:'Keep the conversation going',text:'Ask a follow-up and Chatify remembers the topic. When you change subjects, start a new conversation so answers stay on track.',target:'#newTopic',tabs:['Question','Follow-up','Context'],icon:'↻'},
    {title:'Make it yours',text:'Configuration controls sources, model and look. The easiest setup is Build with AI: describe the app in plain words and review what it drafts. You can skip this tour at any time; nothing is locked while it is open.',target:'#profileBtn',tabs:['Temporary','Profile','Configure'],icon:'☺'}
  ];
  window.CCTour={chat:(replay=false,onClose)=>show({key:'cc_tour',title:'Quick tour',steps:chatSteps,replay,onClose}),config:(replay=false)=>show({key:'cc_cfg_tour_v1',title:'Configuration guide',steps:configSteps,replay})};
})();
