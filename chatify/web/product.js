(()=>{
  const nav=document.querySelector('.toolbar .common-nav,.about-nav .common-nav');
  if(!nav||document.getElementById('navToggle'))return;
  const toggle=document.createElement('button');toggle.type='button';toggle.className='product-nav-toggle';toggle.textContent='Menu';toggle.setAttribute('aria-expanded','false');
  nav.id=nav.id||'productNavigation';toggle.setAttribute('aria-controls',nav.id);nav.before(toggle);
  function set(open){toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('product-nav-open',open)}
  toggle.onclick=()=>set(toggle.getAttribute('aria-expanded')!=='true');
  nav.addEventListener('keydown',e=>{if(e.key==='Escape'){set(false);toggle.focus()}});
  document.addEventListener('click',e=>{if(!nav.contains(e.target)&&e.target!==toggle)set(false)});
})();
