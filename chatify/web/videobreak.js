/* Same-origin feature stories. Only the visible builder may start its selected story. */
(()=>{'use strict';
function mount(host){
 if(!host||host.dataset.storiesMounted)return;host.dataset.storiesMounted='true';
 const title=document.createElement('h2');title.textContent='A short feature story';title.style.margin='20px 20px 0';
 const note=document.createElement('p');note.className='cfg-video-copy';note.textContent='Illustrated Chatify examples. The selected story starts automatically; pause any time. Building works without it.';
 const label=document.createElement('label');label.textContent='Choose a story';label.style.margin='0 20px';
 const select=document.createElement('select');select.setAttribute('aria-label','Choose a feature story');select.dataset.native='true';label.append(select);
 const status=document.createElement('p');status.className='cfg-video-copy';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 const video=document.createElement('video');video.controls=true;video.playsInline=true;video.preload='none';video.setAttribute('aria-label','Illustrated Chatify story');
 const retry=document.createElement('button');retry.type='button';retry.className='go ghost';retry.textContent='Retry story';retry.hidden=true;
 const unmute=document.createElement('button');unmute.type='button';unmute.className='go ghost';unmute.textContent='Turn sound on';unmute.hidden=true;
 host.replaceChildren(title,note,label,status,retry,unmute,video);
 let items=[],generation=0,base=window.CC_APP_BASE?window.CC_APP_BASE.replace(/\/$/,'')+'/media/stories/':new URL('media/stories/',location.href).href;
 const active=()=>!document.hidden&&document.body.classList.contains('cfgtop-builder')&&host.getClientRects().length>0&&!document.querySelector('dialog.app-builder[open]');
 function state(s,text){host.dataset.mediaState=s;status.textContent=text;retry.hidden=s!=='error';video.hidden=s==='error'}
 async function start(){if(!video.src||!active())return;const token=++generation;for(const other of document.querySelectorAll('video'))if(other!==video)other.pause();try{await video.play()}catch(error){if(token!==generation||!active())return;if(video.error||host.dataset.mediaState==='error')return;if(error.name!=='NotAllowedError'){state('idle','Playback did not start. Use Play or Retry if the file cannot load.');return}video.muted=true;unmute.hidden=false;try{await video.play()}catch(_){if(token===generation)state('idle','Your browser paused automatic playback. Use Play to start.')}}if(!active())video.pause()}
 function choose(){const item=items.find(i=>i.id===select.value);if(!item)return;generation++;video.pause();video.src=base+item.src;video.poster=base+item.poster;video.setAttribute('aria-label',item.label+'; illustrated feature story');state('idle','Starting the selected story...');start()}
 video.addEventListener('loadedmetadata',()=>{if(video.paused)state('ready','Story ready. Use Play, sound and fullscreen controls.')});
 video.addEventListener('playing',()=>state('playing',video.muted?'Playing muted. Turn sound on when you want to listen.':'Playing illustrated story. Pause any time.'));
 video.addEventListener('volumechange',()=>{unmute.hidden=!video.muted;if(!video.paused)state('playing',video.muted?'Playing muted. Turn sound on when you want to listen.':'Playing illustrated story. Pause any time.')});
 video.addEventListener('ended',()=>state('ended','Story finished. Choose another or return to your build.'));
 video.addEventListener('error',()=>state('error','Could not load this story. Retry it or choose another; your build is unaffected.'));
 select.onchange=choose;retry.onclick=choose;unmute.onclick=()=>{video.muted=false;unmute.hidden=true;video.play().catch(()=>state('ready','Use Play to continue with sound.'))};
 document.addEventListener('cc-builder-window-open',()=>{generation++;video.pause()});
 document.addEventListener('visibilitychange',()=>{if(document.hidden){generation++;video.pause()}});
 document.addEventListener('cc-settings-topmode',e=>{if(e.detail!=='builder'){generation++;video.pause()}else start()});
 state('loading','Loading the available stories...');
 fetch(base+'manifest.json').then(r=>{if(!r.ok)throw Error('manifest');return r.json()}).then(data=>{
  items=(data.stories||[]).filter(i=>/^[a-z0-9-]+$/.test(i.id)&&i.src===i.id+'.mp4'&&i.poster===i.id+'.jpg');if(!items.length)throw Error('empty');
  for(const item of items){const o=document.createElement('option');o.value=item.id;o.textContent=item.label;select.append(o)}select.selectedIndex=Math.floor(Math.random()*items.length);choose();
 }).catch(()=>{select.disabled=true;state('error','Story list is unavailable. Reload this page to try again; your build is unaffected.');retry.hidden=true});
}
window.CCVideoBreak={mount};
})();
