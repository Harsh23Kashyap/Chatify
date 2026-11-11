(()=>{const catalog=window.CCFeatureCatalog,tabs=document.getElementById('featureTabs'),panel=document.getElementById('featurePanel'),more=document.getElementById('featureMore');let expanded=false,active=0,selectionTimer;
 const drawings={conversation:'M43 48h104v51H89l-18 17V99H43zM139 117h93v39h-39l-12 13v-13h-42z',sources:'M46 36h67l20 20v91H46zM113 36v20h20M62 76h54M62 91h45M160 83h57v44h-57z',documents:'M49 39h63v91H49zM74 53h68v94H74zM101 72h66v94h-66zM117 97h34M117 111h29',audio:'M120 44a15 15 0 0 1 30 0v53a15 15 0 0 1-30 0zM108 88a27 27 0 0 0 54 0M135 124v25M116 151h38',builder:'M47 42h174v112H47zM63 63h87M63 81h61M63 99h78M63 119h91M175 72h24v40h-24z',assistant:'M58 66h154v83H58zM95 66V44h80v22M96 99h1M174 99h1M108 125h53',search:'M93 45a40 40 0 1 0 0 80a40 40 0 1 0 0-80M123 116l48 45M193 55h39M193 77h29M193 99h34',temporary:'M102 46a47 47 0 1 1-19 76M102 46l-19-3 3 19M132 63v32l21 15M47 145h44',import:'M47 57h72l17 19h84v79H47zM136 31v77M117 89l19 19 19-19',export:'M47 57h72l17 19h84v79H47zM136 108V31M117 50l19-19 19 19',model:'M94 56h81v81H94zM107 70h54v54h-54zM72 72h22M72 94h22M72 116h22M175 72h22M175 94h22M175 116h22M110 36v20M134 36v20M158 36v20',presets:'M41 42h67v48H41zM124 42h67v48h-67zM41 106h67v48H41zM124 106h67v48h-67z',color:'M135 36c-55 0-91 25-91 62s41 62 82 62c18 0 24-10 13-23-11-14 2-22 19-21 42 4 70-9 70-34 0-25-41-46-93-46z',fonts:'M63 146l36-101 36 101M75 115h49M159 86h45M161 85v62M159 117h43',motion:'M53 96h29M65 76h29M65 116h29M129 58l17 30 35 7-24 26 3 35-31-17-31 17 3-35-24-26 35-7z',layout:'M40 44h185v111H40zM40 66h185M90 66v89M105 85h102v51H105z',status:'M44 49h101v102H44zM63 74h54M63 96h42M64 122h59M162 112l18 18 43-48',pipeline:'M43 82h42v35H43zM109 82h42v35h-42zM175 82h42v35h-42zM85 99h24M151 99h24M62 64v-18h133v18',connections:'M133 91l-61-40M133 91l65-38M133 91l-62 56M133 91l67 57M114 73h38v38h-38z',budget:'M62 68h151v80H62zM62 68v-20h128v20M170 91h43v31h-43zM83 96h44M83 115h30',workspace:'M44 46h72v105H44zM147 78h71v73h-71zM133 111h14M73 151v14h111v-14',access:'M88 84V62a45 45 0 0 1 90 0v22M69 84h128v75H69zM133 107v27'};
 const details={
  conversation:'<path class="scene-detail" d="M59 65h67M59 78h49M155 133h58M155 144h37"/>',
  sources:'<path class="scene-detail" d="M62 108h37M62 121h46M170 98h33M170 111h21M133 91h16"/><path class="scene-accent-line" d="M61 90h47M171 119h23"/>',
  documents:'<path class="scene-detail" d="M58 55h7M58 68h7M85 77h7M85 90h7M117 125h34M117 139h23"/><path class="scene-accent-line" d="M117 85h18"/>',
  audio:'<path class="scene-detail" d="M56 84v22M68 72v46M80 80v30M190 80v30M202 72v46M214 84v22"/><path class="scene-accent-line" d="M130 53h10M130 64h10M130 75h10"/>',
  builder:'<path class="scene-detail" d="M47 55h174M181 90l5 5 8-11"/><path class="scene-accent-line" d="M63 136h39"/>',
  assistant:'<path class="scene-detail" d="M73 81h25M73 92h16M187 117h10M187 128h10"/><path class="scene-accent-line" d="M124 44v-8h23"/>',
  search:'<path class="scene-detail" d="M73 71h39M73 84h30M73 97h35"/><path class="scene-accent-line" d="M194 77h29"/>',
  temporary:'<path class="scene-detail" d="M113 149h50M56 57h22M60 70h14"/><path class="scene-accent-line" d="M132 63v32l21 15"/>',
  import:'<path class="scene-detail" d="M65 121h51M65 134h31M177 94h25M177 107h17"/><path class="scene-accent-line" d="M136 48v58M120 90l16 16 16-16"/>',
  export:'<path class="scene-detail" d="M65 121h51M65 134h31M177 94h25M177 107h17"/><path class="scene-accent-line" d="M136 108V33M120 49l16-16 16 16"/>',
  model:'<path class="scene-detail" d="M119 83h30M119 96h21M119 109h26M110 137v18M134 137v18M158 137v18"/>',
  presets:'<path class="scene-detail" d="M52 55h43M52 66h27M52 119h43M52 130h27M136 119h43M136 130h27"/><path class="scene-accent-line" d="M143 64l8 8 17-17"/>',
  color:'<circle class="scene-accent" cx="81" cy="83" r="8"/><circle class="scene-paint" cx="111" cy="62" r="8"/><circle class="scene-ink" cx="150" cy="62" r="8"/><circle class="scene-paper" cx="183" cy="79" r="8"/>',
  fonts:'<path class="scene-detail" d="M51 162h166M51 29h87M151 70h65"/><path class="scene-accent-line" d="M151 162h65"/>',
  motion:'<path class="scene-detail" d="M58 139h34M51 153h25"/><path class="scene-accent-line" d="M53 96h29"/>',
  layout:'<path class="scene-detail" d="M53 82h23M53 96h23M53 110h16M117 98h76M117 111h49M117 124h62"/><path class="scene-accent-line" d="M55 55h16"/>',
  status:'<path class="scene-detail" d="M154 51h58M154 65h38"/><path class="scene-accent-line" d="M162 112l18 18 43-48"/>',
  pipeline:'<path class="scene-detail" d="M54 94h20M54 103h13M120 94h20M120 103h13M186 94h20M186 103h13"/><path class="scene-accent-line" d="M62 133h26M129 133h26M195 133h22"/>',
  connections:'<circle class="scene-paper" cx="67" cy="48" r="14"/><circle class="scene-paper" cx="202" cy="50" r="14"/><circle class="scene-paper" cx="67" cy="150" r="14"/><circle class="scene-paper" cx="203" cy="151" r="14"/><path class="scene-accent-line" d="M123 91h20M133 81v20"/>',
  budget:'<path class="scene-detail" d="M83 132h65M83 55h44"/><circle class="scene-accent" cx="186" cy="106" r="4"/>',
  workspace:'<path class="scene-detail" d="M57 64h46M57 78h29M57 92h37M159 96h45M159 110h32M159 124h37"/><path class="scene-accent-line" d="M57 128h28"/>',
  access:'<circle class="scene-accent" cx="133" cy="111" r="6"/><path class="scene-accent-line" d="M133 115v19"/>'
 };
 function scene(kind){return `<svg viewBox="0 0 270 195" aria-hidden="true" focusable="false"><g class="scene-lines"><path class="scene-object" d="${drawings[kind]||drawings.builder}"/>${details[kind]||''}</g></svg>`}

 const guides={
 chat:['/','Ask a question, then follow up in the same chat. Open a saved conversation from the sidebar.'],
 sources:['/','Ask a question, then open a numbered citation. Read the source passage before relying on the answer.'],
 upload:['/','Choose Add documents beside the question box, then select a supported file. Check that readable text was imported.'],
 mic:['/','Choose the microphone, allow browser permission, and review the transcribed question before sending it.'],
 builder:['/build.html','Describe the app, confirm sources, then review the generated draft. Saving and opening the app are separate steps.'],
 ask:['/settings.html','Use the settings help assistant with your selected model. Review what will be sent; suggestions do not change settings for you.'],
 search:['/settings.html','Use Find a setting, enter an everyday phrase, then choose the matching control.'],
 temporary:['/','Choose Temporary before asking. Do not use it as a promise that your model provider keeps no records.'],
 'zip-in':['/settings.html#sec-portable','Choose the app ZIP or YAML, inspect its contents, then confirm loading. Review code before allowing it to run.'],
 'zip-out':['/settings.html#sec-portable','Choose Download app ZIP. Keep keys excluded and review included documents before sharing.'],
 models:['/settings.html#sec-model','Choose the provider and model, save your own key if needed, then use the optional connection test. Provider charges may apply.'],
 presets:['/settings.html#sec-presets','Preview a preset, then apply it if you want its appearance. Named setups do not restore source keys.'],
 colors:['/settings.html#sec-colors','Choose light or dark colors and inspect the preview. Appearance changes save automatically after a short pause.'],
 fonts:['/settings.html#sec-fonts','Choose body and heading fonts, then check text size in the preview. Offline font loading may use a fallback.'],
 motion:['/settings.html#sec-motion','Choose Full for all effects, Subtle for quieter effects, or Calm/None for no decorative motion. Device reduced motion overrides these choices.'],
 layout:['/settings.html#sec-layout','Choose sidebar and chat width, then inspect the preview. Appearance changes save automatically.'],
 status:['/settings.html#sec-finish','Read the setup checks. A saved key only proves presence; use an optional live test when you want to check the connection.'],
 prompts:['/settings.html#sec-prompts','Choose the answer step, edit its instructions and save it. Test a real question; a saved prompt is not proof of answer accuracy.'],
 connectors:['/settings.html#sec-search','Inspect configured sources and their key requirements. Model keys and source API keys are separate. Test only after reviewing possible costs.'],
 budget:['/settings.html#sec-budget','Set local usage limits and save them. These controls do not replace your provider billing account.'],
 exports:['/','Open an answer and choose copy or download. Keep the source links and check important claims yourself.'],
 workspace:['/settings.html#sec-finish','Open Setup for workspace tools. Review each change before confirming; a deployment plan does not publish the app.'],
 access:['/run-locally.html','Review the access and hosting configuration before sharing your app. Check its audience rather than assuming the app is private.']
 };
 const guide=document.createElement('section');guide.className='feature-next-step';guide.setAttribute('aria-live','polite');panel.after(guide);
 function choose(i,focus=false){active=i;clearTimeout(selectionTimer);const f=catalog[i];for(const b of tabs.children){b.setAttribute('aria-selected',String(Number(b.dataset.i)===i));b.tabIndex=Number(b.dataset.i)===i?0:-1}if(focus)tabs.children[i]?.focus();const reveal=()=>{panel.id='feature-panel-'+f[0];panel.setAttribute('aria-labelledby','feature-tab-'+f[0]);panel.innerHTML=`<div class="feature-art" data-scene="${f[3]}">${scene(f[3])}<small>${f[4]}</small></div><div class="feature-copy"><small>${String(i+1).padStart(2,'0')} / ${catalog.length} features</small><h3></h3><p></p><a href="${['chat','sources','upload','mic','temporary','exports'].includes(f[0])?'/':'/settings.html'}">Try this in ${['chat','sources','upload','mic','temporary','exports'].includes(f[0])?'Chat':'Configuration'} ↗</a></div>`;const instruction=guides[f[0]];if(instruction){panel.querySelector(".feature-copy a").href=(window.CC_APP_BASE||'')+instruction[0];guide.replaceChildren();const title=document.createElement('h4'),text=document.createElement('p');title.textContent='What to do next';text.textContent=instruction[1];const action=document.createElement('a');action.href=(window.CC_APP_BASE||'')+instruction[0];action.textContent='Open this feature';guide.append(title,text,action)}panel.querySelector('h3').textContent=f[1];panel.querySelector('.feature-copy p').textContent=f[2];panel.querySelector('.feature-copy').classList.add('feature-copy-arrive');panel.removeAttribute('aria-busy')};const quiet=matchMedia('(prefers-reduced-motion: reduce)').matches||['none','calm'].includes(document.documentElement.dataset.motion);if(panel.children.length&&!quiet){panel.setAttribute('aria-busy','true');panel.querySelector('.feature-copy')?.classList.remove('feature-copy-arrive');panel.querySelector('.feature-copy')?.classList.add('feature-copy-leave');selectionTimer=setTimeout(reveal,80)}else reveal()}

 function render(){if(!expanded){while(tabs.children.length>6)tabs.lastElementChild.remove()}catalog.forEach((f,i)=>{if((!expanded&&i>=6)||i<tabs.children.length)return;const b=document.createElement('button');b.type='button';b.id='feature-tab-'+f[0];b.dataset.i=i;b.setAttribute('role','tab');b.setAttribute('aria-controls','feature-panel-'+f[0]);b.textContent=f[1];if(expanded&&i>=6&&i<10){b.classList.add('feature-added');b.style.animationDelay=((i-6)*25)+'ms'}b.onclick=()=>choose(i);b.onkeydown=e=>{const count=expanded?catalog.length:6;let next=i;if(e.key==='ArrowRight')next=(i+1)%count;else if(e.key==='ArrowLeft')next=(i-1+count)%count;else if(e.key==='Home')next=0;else if(e.key==='End')next=count-1;else return;e.preventDefault();choose(next,true)};tabs.append(b)});if(!panel.children.length||(!expanded&&active>5))choose(expanded?active:Math.min(active,5));more.textContent=expanded?'Show fewer features':'Load more features ('+(catalog.length-6)+')';more.setAttribute('aria-expanded',String(expanded))}
 more.onclick=()=>{expanded=!expanded;render()};render();
 function revealIntro(){
  if(matchMedia('(prefers-reduced-motion: reduce)').matches||['none','calm'].includes(document.documentElement.dataset.motion))return;
  let seen=false;try{seen=sessionStorage.getItem('cc_about_intro_seen')==='1';sessionStorage.setItem('cc_about_intro_seen','1')}catch{}
  if(seen)return;
  document.querySelector('main>h1')?.animate([{opacity:0},{opacity:1}],{duration:180,easing:'ease-out'});
  document.querySelector('main>p')?.animate([{opacity:0},{opacity:1}],{duration:180,delay:40,easing:'ease-out',fill:'backwards'});
 }
 fetch('/api/theme').then(r=>r.json()).then(r=>{const motion=(r.theme||r).motion;document.documentElement.dataset.motion=["calm","none"].includes(motion)?"none":motion;revealIntro()}).catch(revealIntro);
})();
