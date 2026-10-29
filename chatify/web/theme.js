/* Applies the saved look (colours, fonts, background, motion, layout) to a page. Shared by the chat and the Configuration preview. */
(() => {
"use strict";
const FONT_STACKS = {
  "dm-sans": ['"DM Sans",system-ui,sans-serif', "DM+Sans:wght@400;500;700;800"], inter: ['"Inter",system-ui,sans-serif', "Inter:wght@400;500;700"],
  system: ['-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif', null], georgia: ["Georgia,'Times New Roman',serif", null],
  fraunces: ['"Fraunces",Georgia,serif', "Fraunces:wght@600;700"], playfair: ['"Playfair Display",Georgia,serif', "Playfair+Display:wght@500;700"],
  lora: ['"Lora",Georgia,serif', "Lora:wght@400;600"], "space-grotesk": ['"Space Grotesk",system-ui,sans-serif', "Space+Grotesk:wght@400;500;700"],
  nunito: ['"Nunito",system-ui,sans-serif', "Nunito:wght@400;600;800"], poppins: ['"Poppins",system-ui,sans-serif', "Poppins:wght@400;500;600"],
  jetbrains: ['"JetBrains Mono",ui-monospace,monospace', "JetBrains+Mono:wght@400;600"], mono: ["ui-monospace,SFMono-Regular,Menlo,Consolas,monospace", null],
};
const lum = (hex) => { const v = [1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4)); return 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; };
const onColor = (hex) => ((lum(hex)+.05)/.05 >= 1.05/(lum(hex)+.05) ? "#000000" : "#ffffff");
const rgba = (hex, a) => `rgba(${[1, 3, 5].map((i) => parseInt(hex.substr(i, 2), 16)).join(",")},${a})`;

function patternImage(name, c, op) {
  const col = rgba(c, op / 100);
  switch (name) {
    case "dots": return `radial-gradient(${col} 1.4px, transparent 1.6px)`;
    case "grid": return `linear-gradient(${col} 1px, transparent 1px), linear-gradient(90deg, ${col} 1px, transparent 1px)`;
    case "lines": return `repeating-linear-gradient(0deg, ${col} 0 1px, transparent 1px 100%)`;
    case "diagonal": return `repeating-linear-gradient(45deg, ${col} 0 1px, transparent 1px 8px)`;
    case "checker": return `conic-gradient(${col} 25%, transparent 0 50%, ${col} 0 75%, transparent 0)`;
    case "plus": return `linear-gradient(${col},${col}), linear-gradient(${col},${col})`;
    case "waves": return `radial-gradient(circle at 50% 100%, transparent 38%, ${col} 39% 41%, transparent 42%), radial-gradient(circle at 50% 0%, transparent 38%, ${col} 39% 41%, transparent 42%)`;
    default: return "none";
  }
}

function loadFonts(t) {
  const fams = [];
  for (const k of [t.font, t.heading_font]) { const f = FONT_STACKS[k]; if (f && f[1]) fams.push(f[1]); }
  if (t.custom_font && (t.font === "custom" || t.heading_font === "custom")) fams.push(t.custom_font.trim().replace(/ /g, "+") + ":wght@400;500;700");
  const href = fams.length ? "https://fonts.googleapis.com/css2?" + [...new Set(fams)].map((f) => "family=" + f).join("&") + "&display=swap" : "";
  let l = document.getElementById("cc-fonts");
  if (!href) { if (l) l.remove(); return; }
  if (!l) { l = document.createElement("link"); l.id = "cc-fonts"; l.rel = "stylesheet"; document.head.append(l); }
  if (l.getAttribute("href") !== href) l.setAttribute("href", href);
}
const stack = (k, custom, fallback) => (k === "custom" && custom ? `"${custom}",${fallback}` : (FONT_STACKS[k] || FONT_STACKS["dm-sans"])[0]);


const autoColors = new Map();
let contrastFrame = 0, contrastSettle = 0;
function readableFonts(){
  if (!window.CCBrand || !document.body) return;
  // Only text colour is corrected. Keep width, visibility, panel and
  // background transitions running while reading their final surface colours.
  const colorTransitions=new Map();
  document.querySelectorAll("body *").forEach(node=>{if(node instanceof HTMLElement && !node.matches("option,optgroup,select.cs-native")){
    const cs=getComputedStyle(node),properties=cs.transitionProperty.split(",").map(x=>x.trim());
    if(properties.includes("color")||properties.includes("all")){
      colorTransitions.set(node,[node.style.getPropertyValue("transition"),node.style.getPropertyPriority("transition")]);
      node.style.setProperty("transition",cs.transition+", color 0s","important");
    }
  }});
  autoColors.forEach((value,node)=>{if(node.isConnected){node.style.removeProperty("color");if(value)node.style.color=value;}});autoColors.clear();
  void document.documentElement.offsetWidth;
  const shadeCache=new Map();
  const parse=value=>{
    const m=value.match(/^rgba?\(([^)]+)\)/);if(m){const v=m[1].split(/[, /]+/).map(Number);return v.length>=3?[...v.slice(0,3),v[3]??1]:null;}
    const srgb=value.match(/^color\(srgb ([^)]+)\)/);if(srgb){const v=srgb[1].split(/[ /]+/).map(Number);return [...v.slice(0,3).map(x=>x*255),v[3]??1];}return null;
  };
  const hex=v=>"#"+v.slice(0,3).map(x=>Math.round(Math.max(0,Math.min(255,x))).toString(16).padStart(2,"0")).join("");
  const parseHex=value=>[1,3,5].map(i=>parseInt(value.slice(i,i+2),16));
  const blend=(front,back,alpha)=>front.slice(0,3).map((v,i)=>v*alpha+back[i]*(1-alpha));
  const styleCache=new Map();
  const measuredStyle=node=>{let style=styleCache.get(node);if(!style){const cs=getComputedStyle(node);style={color:cs.color,backgroundColor:cs.backgroundColor,opacity:cs.opacity};const bg=node.getAnimations().find(a=>a.transitionProperty==="background-color");if(bg){const frames=bg.effect.getKeyframes();style.backgroundColor=frames[frames.length-1].backgroundColor||style.backgroundColor;}styleCache.set(node,style);}return style;};
  const corrections=[];
  const background=node=>{
    const layers=[];for(let host=node;host;host=host.parentElement){const c=parse(measuredStyle(host).backgroundColor);if(c&&c[3]>0)layers.push(c);if(c&&c[3]===1)break;}
    let result=[255,255,255];for(const c of layers.reverse())result=blend(c,result,c[3]);return result;
  };
  document.querySelectorAll("body *").forEach(node=>{
    if (!(node instanceof HTMLElement) || node.matches("option,optgroup,select.cs-native") || node.closest("#cc-watermark") || !([...node.childNodes].some(n=>n.nodeType===3&&n.textContent.trim()) || (node.matches("button,a")&&node.querySelector("svg")))) return;
    const cs=measuredStyle(node),values=parse(cs.color);if(!values)return;
    const color=hex(values),backValues=background(node),back=hex(backValues);
    let opacity=values[3];for(let host=node;host;host=host.parentElement)opacity*=Number(measuredStyle(host).opacity);
    if(opacity<=0)return;
    const key=color+back+opacity;let changed=shadeCache.get(key);
    if(!changed){
      changed=color;
      const possible=Math.max(...["#000000","#ffffff"].map(end=>CCBrand.contrast(hex(blend(parseHex(end),backValues,opacity)),back)))>=4.6;
      if(opacity===1){changed=CCBrand.shade(color,back);}
      else if(!possible){changed=CCBrand.shade(color,back,20.9);}
      else for(let target=4.7;target<=21.01;target+=.2){changed=CCBrand.shade(color,back,target);if(CCBrand.contrast(hex(blend(parseHex(changed),backValues,opacity)),back)>=4.6)break;}
      shadeCache.set(key,changed);
    }
    if(changed!==color)corrections.push([node,changed]);
  });
  corrections.forEach(([node,changed])=>{autoColors.set(node,node.style.color);node.style.setProperty("color",changed,"important");});
  void document.documentElement.offsetWidth;
  colorTransitions.forEach(([value,priority],node)=>{if(value)node.style.setProperty("transition",value,priority);else node.style.removeProperty("transition");});

}
function queueContrast(){cancelAnimationFrame(contrastFrame);contrastFrame=requestAnimationFrame(readableFonts);clearTimeout(contrastSettle);contrastSettle=setTimeout(readableFonts,400);}
window.CCReadableFonts=queueContrast;
document.addEventListener("DOMContentLoaded",()=>{
  queueContrast();new MutationObserver(queueContrast).observe(document.body,{childList:true,subtree:true});
  for(const type of ["pointerover","pointerout","focusin","focusout"])document.addEventListener(type,event=>{if(event.target instanceof Element&&event.target.closest(".srcs button.s"))queueContrast();});
});

const backgroundStates = new WeakMap();
let backgroundFade = null;
function rememberBackground(t, root, c) {
  const signature = JSON.stringify([t.bg_style,t.bg_image,t.bg_color2,t.bg_angle,c.bg,t.pattern,t.pattern_color||c.ink,t.pattern_size,t.pattern_opacity]);
  const previous = backgroundStates.get(root);
  backgroundStates.set(root, signature);
  const body = document.body;
  const reduced = matchMedia("(prefers-reduced-motion:reduce)").matches || ["calm","none"].includes(t.motion);
  if (reduced && backgroundFade) {backgroundFade.remove();backgroundFade=null;}
  if (!body || root !== document.documentElement || !previous || previous === signature || reduced) return;
  if (backgroundFade) backgroundFade.remove();
  const old = getComputedStyle(body), pattern = getComputedStyle(body,"::before");
  const cover = document.createElement("div"), texture = document.createElement("div");
  cover.className = "background-fade";cover.setAttribute("aria-hidden","true");
  cover.style.background = old.background;
  texture.style.cssText = "position:absolute;inset:0;pointer-events:none";
  texture.style.backgroundImage=pattern.backgroundImage;texture.style.backgroundSize=pattern.backgroundSize;texture.style.backgroundPosition=pattern.backgroundPosition;
  cover.append(texture);body.append(cover);backgroundFade=cover;
  const fade=cover.animate([{opacity:1},{opacity:0}],{duration:180,easing:"ease-out"});
  fade.onfinish=()=>{cover.remove();if(backgroundFade===cover)backgroundFade=null;};
}
let layoutAnimations=[];
function beginSidebarMove(t,root){
  const previous=root.dataset.sidebar;
  if(previous===t.sidebar)return null;
  layoutAnimations.forEach(a=>a.cancel());layoutAnimations=[];
  const quiet=matchMedia("(prefers-reduced-motion:reduce)").matches||["calm","none"].includes(t.motion);
  if(root!==document.documentElement||quiet||innerWidth<=860||!["left","right"].includes(previous)||!["left","right"].includes(t.sidebar))return null;
  const app=document.querySelector(".app");if(!app||app.classList.contains("side-collapsed"))return null;
  return [...app.children].filter(n=>n.matches(".side,.main,.sources")&&getComputedStyle(n).display!=="none").map(node=>({node,rect:node.getBoundingClientRect()}));
}
function finishSidebarMove(before){
  if(!before)return;
  for(const {node,rect} of before){
    const after=node.getBoundingClientRect(),x=rect.left-after.left,y=rect.top-after.top;
    if(Math.abs(x)<1&&Math.abs(y)<1)continue;
    layoutAnimations.push(node.animate([{transform:`translate(${x}px,${y}px)`},{transform:"none"}],{duration:160,easing:"cubic-bezier(.2,.8,.2,1)"}));
  }
}
function apply(t, root = document.documentElement) {
  if (!t || !t.light) return;
  const sidebarMove=beginSidebarMove(t,root);
  if(["calm","none"].includes(t.motion)||matchMedia("(prefers-reduced-motion:reduce)").matches){layoutAnimations.forEach(a=>a.cancel());layoutAnimations=[];}
  let local=null;try{local=!window.__ccPreview&&localStorage.getItem("cc_mode")}catch{}
  const mode = window.__ccPreview && !window.__ccPreviewReady ? "light" : ["light","dark","auto"].includes(local)?local:t.mode;
  const dark = mode === "dark" || (mode === "auto" && matchMedia("(prefers-color-scheme:dark)").matches);
  const c = dark ? t.dark : t.light, s = root.style, set = (k, v) => s.setProperty(k, v);
  root.dataset.theme = dark ? "dark" : "light"; root.dataset.branded = t.logo ? "on" : "off";
  set("--brand", c.brand); set("--on-brand", onColor(c.brand)); set("--accent", c.brand); set("--lime", c.accent); set("--accent2", c.accent); set("--on-lime", onColor(c.accent));
  set("--cream", c.bg); set("--paper", c.surface); set("--ink", c.ink); set("--mut", c.muted); set("--line", c.line); set("--side-bg", c.sidebar);
  set("--bot", c.bot); set("--you", c.you); set("--danger", c.danger); set("--soft", `color-mix(in srgb, ${c.sidebar} 70%, ${c.surface})`);
  set("--tool", rgba(c.brand, 0.12));
  set("--shadow", { none: "none", soft: dark ? "0 24px 70px rgba(0,0,0,.4)" : `0 24px 70px ${rgba(c.brand, 0.1)}`, strong: dark ? "0 30px 90px rgba(0,0,0,.65)" : `0 30px 90px ${rgba(c.brand, 0.28)}` }[t.shadow]);
  // fonts
  loadFonts(t);
  set("--font", stack(t.font, t.custom_font, 'system-ui,sans-serif,"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji"')); set("--serif", stack(t.heading_font, t.custom_font, 'Georgia,serif,"Apple Color Emoji","Segoe UI Emoji","Noto Color Emoji"'));
  set("--fs", t.font_size / 100); set("--lh", t.line_height / 100); set("--rs", t.radius / 100);
  set("--dens", { compact: 0.78, cozy: 1, roomy: 1.3 }[t.density]);
  set("--speed", 100 / t.speed);
  set("--side-w", t.sidebar_width + "px");
  set("--chat-max", { narrow: "680px", normal: "980px", wide: "1200px", full: "100%" }[t.chat_width]);
  // Fade only the old background layer. Text, focus and controls stay in place.
  rememberBackground(t, root, c);
  // background and pattern
  const soft = c.bg;
  const layer = { soft, solid: c.bg, gradient: `linear-gradient(${t.bg_angle}deg,${c.bg},${t.bg_color2})`, image: t.bg_image ? `linear-gradient(${rgba(c.bg, 0.55)},${rgba(c.bg, 0.55)}),url("${t.bg_image}") center/cover fixed, ${c.bg}` : soft }[t.bg_style];
  set("--bg-layer", layer);
  const pc = t.pattern_color || c.ink, ps = t.pattern_size;
  set("--pat-img", patternImage(t.pattern, pc, t.pattern_opacity));
  set("--pat-size", t.pattern === "waves" ? `${ps * 2}px ${ps}px` : `${ps}px ${ps}px`);
  set("--pat-pos", t.pattern === "plus" ? "center" : "0 0");
  if (t.pattern === "plus") { set("--pat-img", `linear-gradient(${rgba(pc, t.pattern_opacity / 100)},${rgba(pc, t.pattern_opacity / 100)}),linear-gradient(${rgba(pc, t.pattern_opacity / 100)},${rgba(pc, t.pattern_opacity / 100)})`); set("--pat-size", `${ps}px 1px, 1px ${ps}px`); }
  const d = root.dataset;
  d.shadow = t.shadow; d.pattern = t.pattern; d.motion = t.motion === "calm" ? "none" : t.motion; d.motionProfile = t.motion; d.entrance = t.entrance; d.bubble = t.bubble; d.sidebar = t.sidebar; d.chatw = t.chat_width;
  d.avatars = t.avatars; d.align = t.you_align; d.composer = t.composer; d.toolbar = t.toolbar; d.lift = t.hover_lift ? "on" : "off"; d.sources = t.sources_panel ? "on" : "off";
  const meta = document.querySelector('meta[name="theme-color"]'); if (meta) meta.content = c.brand;
  let icon = document.querySelector('link[data-cc-icon]');
  if (!icon) { icon = document.createElement("link"); icon.rel = "icon"; icon.type = "image/png"; icon.dataset.ccIcon = "1"; document.head.append(icon); }
  icon.href = t.logo || "/icons/chatify.svg"; icon.type=t.logo?"image/png":"image/svg+xml";
  const paintWatermark = () => {
    let watermark = document.getElementById("cc-watermark");
    const host = document.querySelector(".main") || document.body; if (!host) return;
    if (!watermark) { watermark = document.createElement("div"); watermark.id = "cc-watermark"; watermark.setAttribute("aria-hidden","true"); host.append(watermark); }
    watermark.style.backgroundImage = t.logo && t.logo_watermark ? `url("${t.logo}")` : "none";
    watermark.hidden = !(t.logo && t.logo_watermark);
  };
  if (document.body) paintWatermark(); else document.addEventListener("DOMContentLoaded",paintWatermark,{once:true});
  finishSidebarMove(sidebarMove);
  window.CCTheme.value = t; queueContrast();
}
window.__ccPreview = /[?&]preview=1/.test(location.search);
const fontRequests=new Map();
async function requestFont(key,custom=''){
 const spec=FONT_STACKS[key];const family=key==='custom'?custom:spec?.[0]?.split(',')[0]?.replaceAll('"','');if(!family)return false;if(spec&&!spec[1])return true;
 const request=key==='custom'?custom.trim().replaceAll(' ','+')+':wght@400;500;700':spec?.[1];if(!request)return false;if(fontRequests.has(request))return fontRequests.get(request);
 const work=new Promise(resolve=>{const link=document.createElement('link');link.rel='stylesheet';link.href='https://fonts.googleapis.com/css2?family='+request+'&display=swap';let settled=false;const done=ok=>{if(!settled){settled=true;resolve(ok)}};const timeout=setTimeout(()=>done(false),6500);link.onerror=()=>{clearTimeout(timeout);done(false)};link.onload=async()=>{try{const loaded=await document.fonts.load('16px "'+family+'"');clearTimeout(timeout);done(loaded.length>0)}catch{clearTimeout(timeout);done(false)}};document.head.append(link)});fontRequests.set(request,work);return work
}
window.CCTheme = { apply, value: null, fonts: FONT_STACKS, requestFont };
try { const el = document.getElementById("cc-theme"); if (el) apply(JSON.parse(el.textContent)); } catch (e) { /* keep defaults */ }
matchMedia("(prefers-color-scheme:dark)").addEventListener("change", () => window.CCTheme.value && apply(window.CCTheme.value));
window.addEventListener("message", (e) => { if (e.origin === location.origin && e.data && e.data.ccTheme) { window.__ccPreviewReady = true; apply(e.data.ccTheme); } });
})();
