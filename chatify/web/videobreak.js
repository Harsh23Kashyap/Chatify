/* Same-origin feature stories. Only the visible builder may start its selected story. */
(()=>{'use strict';
function mount(host){
 if(!host||host.dataset.storiesMounted)return;host.dataset.storiesMounted='true';
 const title=document.createElement('h2');title.textContent='Features of Chatify';title.style.margin='20px 20px 0';
 const status=document.createElement('p');status.className='cfg-video-copy';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 const video=document.createElement('video');video.controls=true;video.playsInline=true;video.preload='none';video.setAttribute('aria-label','Illustrated Chatify story');
 const retry=document.createElement('button');retry.type='button';retry.className='go ghost';retry.textContent='Retry story';retry.hidden=true;
 host.replaceChildren(title,status,retry,video);
 let item=null,generation=0,base=window.CC_APP_BASE?window.CC_APP_BASE.replace(/\/$/,'')+'/media/stories/':new URL('media/stories/',location.href).href;
 const active=()=>!document.hidden&&document.body.classList.contains('cfgtop-builder')&&host.getClientRects().length>0&&!document.querySelector('dialog.app-builder[open]');
 function state(s,text){host.dataset.mediaState=s;status.textContent=text;status.hidden=!text;retry.hidden=s!=='error';video.hidden=s==='error'}
 async function start(){if(!video.src||!active())return;const token=++generation;for(const other of document.querySelectorAll('video'))if(other!==video)other.pause();try{await video.play()}catch(error){if(token!==generation||!active())return;if(video.error||host.dataset.mediaState==='error')return;if(error.name!=='NotAllowedError'){state('idle','Playback did not start. Use Play or Retry if the file cannot load.');return}video.muted=true;try{await video.play()}catch(_){if(token===generation&&!video.error&&host.dataset.mediaState!=='error')state('idle','Your browser paused automatic playback. Use Play to start.')}}if(!active())video.pause()}
 function choose(){if(!item)return;generation++;video.pause();video.src=base+item.src;video.poster=base+item.poster;video.setAttribute('aria-label',item.label+'; illustrated feature story');state('idle','');start()}
 video.addEventListener('loadedmetadata',()=>{if(video.paused)state('ready','')});
 video.addEventListener('playing',()=>state('playing',''));
 video.addEventListener('ended',()=>state('ended','Video finished.'));
 video.addEventListener('error',()=>state('error','Optional video unavailable. Package videos need internet; your build works without it.'));
 retry.onclick=choose;
 document.addEventListener('cc-builder-window-open',()=>{generation++;video.pause()});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){generation++;video.pause()}});
 document.addEventListener('cc-settings-topmode',e=>{if(e.detail!=='builder'){generation++;video.pause()}else start()});
 state('loading','Loading the available stories...');
 fetch(base+'manifest.json').then(r=>{if(!r.ok)throw Error('manifest');return r.json()}).then(data=>{
  const items=(data.stories||[]).filter(i=>/^[a-z0-9-]+$/.test(i.id)&&i.src===i.id+'.mp4'&&i.poster===i.id+'.jpg');if(!items.length)throw Error('empty');
  item=items[Math.floor(Math.random()*items.length)];choose();
 }).catch(()=>{state('error','Story list is unavailable. Reload this page to try again; your build is unaffected.');retry.hidden=true});
}
window.CCVideoBreak={mount};
})();
