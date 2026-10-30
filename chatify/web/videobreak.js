/* Optional same-origin stories. No autoplay, no build state, no model requests. */
(()=>{'use strict';
function mount(host){
 if(!host||host.dataset.storiesMounted)return;host.dataset.storiesMounted='true';
 const title=document.createElement('h2');title.textContent='A short feature story';title.style.margin='20px 20px 0';
 const note=document.createElement('p');note.className='cfg-video-copy';note.textContent='Illustrated Chatify examples. Play only when you want a break; building works without them.';
 const label=document.createElement('label');label.textContent='Choose a story';label.style.margin='0 20px';
 const select=document.createElement('select');select.setAttribute('aria-label','Choose a feature story');select.dataset.native='true';label.append(select);
 const status=document.createElement('p');status.className='cfg-video-copy';status.setAttribute('role','status');status.setAttribute('aria-live','polite');
 const video=document.createElement('video');video.controls=true;video.playsInline=true;video.preload='none';video.setAttribute('aria-label','Optional illustrated Chatify story');
 const retry=document.createElement('button');retry.type='button';retry.className='go ghost';retry.textContent='Retry story';retry.hidden=true;
 const caveat=document.createElement('p');caveat.className='cfg-video-copy';caveat.textContent='New reconstructions, not live answers. Sound included; soundtrack mix review is still open. The full story library is not finished.';
 host.replaceChildren(title,note,label,status,retry,video,caveat);
 let items=[],base=window.CC_APP_BASE?window.CC_APP_BASE.replace(/\/$/,'')+'/media/stories/':new URL('media/stories/',location.href).href;
 function state(s,text){host.dataset.mediaState=s;status.textContent=text;retry.hidden=s!=='error';video.hidden=s==='error'}
 function choose(load){const item=items.find(i=>i.id===select.value);if(!item)return;video.pause();video.src=base+item.src;video.poster=base+item.poster;video.setAttribute('aria-label',item.label+'; illustrated 90-second story');state('idle','90-second story selected. Use Play, sound and fullscreen controls.');if(load)video.load()}
 video.addEventListener('loadstart',()=>state('idle','Story selected. Press Play to load and watch.'));
 video.addEventListener('loadedmetadata',()=>state('ready','Story ready. Use Play, sound and fullscreen controls.'));
 video.addEventListener('play',()=>state('playing','Playing illustrated story. Pause any time.'));
 video.addEventListener('ended',()=>state('ended','Story finished. Choose another or return to your build.'));
 video.addEventListener('error',()=>state('error','Could not load this story. Retry it or choose another; your build is unaffected.'));
 select.onchange=()=>choose(true);retry.onclick=()=>choose(true);
 document.addEventListener('visibilitychange',()=>{if(document.hidden)video.pause()});
 document.addEventListener('cc-settings-topmode',e=>{if(e.detail!=='builder')video.pause()});
 state('loading','Loading the available stories...');
 fetch(base+'manifest.json').then(r=>{if(!r.ok)throw Error('manifest');return r.json()}).then(data=>{
  items=(data.stories||[]).filter(i=>/^[a-z0-9-]+$/.test(i.id)&&i.src===i.id+'.mp4'&&i.poster===i.id+'.jpg');if(!items.length)throw Error('empty');
  for(const item of items){const o=document.createElement('option');o.value=item.id;o.textContent=item.label;select.append(o)}select.selectedIndex=Math.floor(Math.random()*items.length);choose(false);
 }).catch(()=>{select.disabled=true;state('error','Story list is unavailable. Reload this page to try again; your build is unaffected.');retry.hidden=true});
}
window.CCVideoBreak={mount};
})();
