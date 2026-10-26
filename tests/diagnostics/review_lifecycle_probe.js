/* Read-only observations of natural review motion. Inject before page scripts.
 * Original animate arguments, Animation return, playback and timeouts are unchanged.
 * Diagnostic coverage only, not a replacement for product assertions.
 */
(() => {
  const events = window.__reviewLifecycle = [];
  const box = n => {
    if (!n) return null;
    const r = n.getBoundingClientRect();
    return {x:r.x,y:r.y,width:r.width,height:r.height,connected:n.isConnected};
  };
  const snapshot = (stage, target) => {
    const host = document.querySelector('#builderReviewResult');
    events.push({stage,at:performance.now(),target:box(target),host:box(host),
      inert:host?.inert,children:host?.childElementCount,
      heading:host?.querySelector('h4')?.textContent,
      display:host ? getComputedStyle(host).display : null,
      dialog:box(document.querySelector('dialog.app-builder')),
      header:box(document.querySelector('.app-builder .settings-help-head')),
      footer:box(document.querySelector('.builder-shell-footer')),
      scrollX,scrollY});
  };
  window.__reviewSnapshot = snapshot;
  const original = Element.prototype.animate;
  Element.prototype.animate = function (...args) {
    const animation = original.apply(this,args);
    if (this.matches('.builder-change-group,.builder-change-actions>small')) {
      const target = this;
      snapshot('animate-return',target);
      events.push({stage:'animation-declared',at:performance.now(),
        duration:animation.effect.getTiming().duration,
        frames:animation.effect.getKeyframes(),targetClass:target.className});
      animation.addEventListener('finish',()=>snapshot('finish-event',target),{once:true});
      animation.addEventListener('cancel',()=>snapshot('cancel-event',target),{once:true});
      for (const ms of [0,80,140,180,250])
        setTimeout(()=>snapshot('natural-timeout-'+ms,target),ms);
    }
    return animation;
  };
  new MutationObserver(records=>{
    if (records.some(r=>r.target.id==='builderReviewResult'||
      r.target.closest?.('#builderReviewResult')))
      snapshot('review-mutation',null);
  }).observe(document,{childList:true,subtree:true,attributes:true,
    attributeFilter:['inert','hidden','style']});
})();
