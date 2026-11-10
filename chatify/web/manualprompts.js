(()=>{
function mount(){
const section=document.querySelector('#sec-prompts');if(!section||section.dataset.manualPromptsMounted||!section.querySelector('#promptsEditor'))return;
section.dataset.manualPromptsMounted='true';
section.classList.add('manual-prompt-candidate');
const intro=section.querySelector('.head small');if(intro)intro.textContent='Choose an answer step, edit its prompt, then save.';section.querySelector(':scope>.section-summary')?.remove();
const more=section.querySelector(':scope>.workspace-fields'),moreButton=section.querySelector(':scope>.simple-more');if(moreButton)section.append(moreButton);if(more)section.append(more);
const list=section.querySelector('.editor-list'),buttons=[...list.querySelectorAll('button.editor-choice')],pane=section.querySelector('#promptsEditor');
const picker=document.createElement('details');picker.className='manual-step-picker';
const trigger=document.createElement('summary');trigger.className='manual-step-trigger';trigger.setAttribute('aria-label','Choose an answer step');trigger.title='Choose an answer step';
const count=document.createElement('span');count.className='manual-step-count';
const title=document.createElement('span');title.className='manual-step-title';
const caret=document.createElementNS('http://www.w3.org/2000/svg','svg');caret.setAttribute('viewBox','0 0 24 24');caret.setAttribute('aria-hidden','true');caret.innerHTML='<path d="m7 10 5 5 5-5" fill="none" stroke="currentColor" stroke-width="1.5"/>';
trigger.append(count,title,caret);picker.append(trigger);list.before(picker);picker.append(list);
list.setAttribute('aria-label','All answer steps');
buttons.forEach((b,i)=>{const num=document.createElement('span');num.className='manual-step-number';num.textContent=String(i+1).padStart(2,'0');b.prepend(num);b.addEventListener('click',()=>{update();picker.open=false;trigger.focus({preventScroll:true})});});
function update(){for(const extra of section.querySelectorAll(':scope>.simple-more,:scope>.workspace-fields'))if(pane.compareDocumentPosition(extra)&Node.DOCUMENT_POSITION_PRECEDING)section.append(extra);const active=buttons.findIndex(b=>b.getAttribute('aria-pressed')==='true');count.textContent=String(active+1).padStart(2,'0')+' / '+buttons.length;title.textContent=buttons[active]?.querySelector('b').textContent||'Choose a step';}
update();
picker.addEventListener('keydown',e=>{if(e.key==='Escape'){picker.open=false;trigger.focus();e.preventDefault()}if(e.key==='ArrowDown'&&e.target===trigger){picker.open=true;buttons.find(b=>b.getAttribute('aria-pressed')==='true')?.focus();e.preventDefault()}});
buttons.forEach((b,i)=>b.addEventListener('keydown',e=>{const n=e.key==='ArrowDown'?i+1:e.key==='ArrowUp'?i-1:e.key==='Home'?0:e.key==='End'?buttons.length-1:null;if(n!==null){buttons[(n+buttons.length)%buttons.length].focus();e.preventDefault()}}));
document.addEventListener('click',e=>{if(!picker.contains(e.target))picker.open=false});
const enhanced=new WeakSet();
function enhance(){const card=pane.querySelector('.stage'),area=card?.querySelector('textarea');if(!card||!area||enhanced.has(card))return;enhanced.add(card);
const body=card.querySelector('.sbody'),actions=[...body.querySelectorAll(':scope > .keyrow')].find(n=>[...n.querySelectorAll('button')].some(b=>b.textContent==='Save'));
if(actions){actions.classList.add('manual-prompt-actions');body.prepend(actions)}
const wrap=document.createElement('div');wrap.className='manual-numbered-editor';const gutter=document.createElement('div');gutter.className='manual-line-gutter';gutter.setAttribute('aria-hidden','true');const lines=document.createElement('div');gutter.append(lines);area.before(wrap);wrap.append(gutter,area);const description=body.querySelector(':scope>p.h');if(description)wrap.before(description);
const measure=document.createElement('div');measure.className='manual-line-measure';measure.setAttribute('aria-hidden','true');wrap.append(measure);
let lastPaint='';const repaint=()=>{const s=getComputedStyle(area);const signature=[area.value,area.clientWidth,s.font,s.lineHeight,s.paddingLeft,s.paddingRight].join('\0');if(signature===lastPaint)return;lastPaint=signature;measure.style.font=s.font;measure.style.lineHeight=s.lineHeight;measure.style.width=(area.clientWidth-parseFloat(s.paddingLeft)-parseFloat(s.paddingRight))+'px';const heights=new Map(),fragment=document.createDocumentFragment();for(const [i,line]of area.value.split('\n').entries()){if(!heights.has(line)){measure.textContent=line||' ';heights.set(line,Math.max(parseFloat(s.lineHeight),measure.getBoundingClientRect().height))}const n=document.createElement('span');n.textContent=i+1;n.style.height=heights.get(line)+'px';fragment.append(n)}lines.replaceChildren(fragment);lines.style.transform='translateY(-'+area.scrollTop+'px)'};
area.addEventListener('input',repaint);area.addEventListener('scroll',()=>{lines.style.transform='translateY(-'+area.scrollTop+'px)'});new ResizeObserver(repaint).observe(area);new MutationObserver(repaint).observe(card.querySelector('.testres'),{childList:true,characterData:true,subtree:true});requestAnimationFrame(repaint);
}
new MutationObserver(()=>{update();enhance()}).observe(pane,{childList:true});new MutationObserver(update).observe(section,{childList:true});enhance();
}
const col=document.querySelector('#col');if(col)new MutationObserver(mount).observe(col,{childList:true});mount();
})();
