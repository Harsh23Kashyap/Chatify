/* Actual page navigation and startup states, not simulated progress. */
(()=>{
 const root=document.documentElement;
 let timer;
 const ready=()=>{clearTimeout(timer);root.classList.remove('cc-page-loading');root.classList.remove('cc-page-leaving');document.querySelector('.cc-load-notice')?.remove()};
 const start=label=>{root.classList.add('cc-page-loading');clearTimeout(timer);timer=setTimeout(()=>{const note=document.createElement('div');note.className='cc-load-notice';note.setAttribute('role','status');note.textContent=label;document.body.append(note);setTimeout(()=>{if(note.isConnected)note.textContent=label+' Taking longer than usual; the app may be waking up. The first visit can take up to a minute.'},6000)},250)};
 window.CCLoading={ready,start};start('Opening app...');
 window.addEventListener('pageshow',()=>{if(!document.getElementById('thread'))ready()});
 window.addEventListener('pagehide',ready);
 document.addEventListener('click',e=>{const a=e.target.closest('a[href]');if(!a||e.defaultPrevented||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||a.target||a.download)return;const u=new URL(a.href,location.href);if(u.origin!==location.origin||u.pathname===location.pathname)return;root.classList.add('cc-page-leaving');start('Opening '+(a.textContent.trim()||'page')+'...')});
 window.addEventListener('error',ready);
})();
