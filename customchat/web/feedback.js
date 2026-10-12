/* Give existing status messages a consistent, non-colour-only error treatment. */
(()=>{
 const pattern=/\b(error|failed|failure|invalid|denied|not allowed|cannot|could not|out of range|fix the|use a non-negative|needs retry|not found)\b/i;
 const selector='[id$="Status"],#status,.testres,.auth-err,#builderStatus';
 let queued=false;
 function paint(){queued=false;for(const node of document.querySelectorAll(selector)){
  const text=node.textContent.trim(),bad=!!text&&pattern.test(text)&&!node.querySelector('input,textarea');
  if(bad){if(node.dataset.feedback!=='error')node.dataset.feedback='error';if(node.getAttribute('aria-live')!=='polite')node.setAttribute('aria-live','polite')}
  else if(node.dataset.feedback==='error')delete node.dataset.feedback;
 }}
 new MutationObserver(()=>{if(!queued){queued=true;queueMicrotask(paint)}}).observe(document.body,{childList:true,characterData:true,subtree:true});paint();
})();
