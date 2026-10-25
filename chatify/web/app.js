(() => {
"use strict";
const $ = (s) => document.querySelector(s);
const el = (tag, props = {}, ...kids) => {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props)) {
    if (k === "class") e.className = v; else if (k === "text") e.textContent = v;
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v);
  }
  for (const c of kids.flat()) if (c != null) e.append(c.nodeType ? c : document.createTextNode(c));
  return e;
};
// Display-time mirror of the server-side plain_text(): retrieved titles and
// passages can carry raw markdown ("##", "**") and arXiv LaTeX ("$z>10$",
// "MgAl$_2$O$_4$"); the sources UI shows readable text, stored evidence stays raw.
const LATEX_SYMBOLS = {
  approx: "~", simeq: "~", cong: "~", sim: "~", propto: "~",
  geq: ">=", ge: ">=", leq: "<=", le: "<=", neq: "!=", ne: "!=",
  times: "\u00d7", pm: "\u00b1", mp: "-/+",
  to: "\u2192", rightarrow: "\u2192", leftarrow: "\u2190", Rightarrow: "=>",
  odot: "\u2299", circ: "\u00b0", deg: "\u00b0", cdot: "\u00b7",
  in: "in", infty: "infinity", sqrt: "sqrt",
  alpha: "\u03b1", beta: "\u03b2", gamma: "\u03b3", delta: "\u03b4", epsilon: "\u03b5",
  zeta: "\u03b6", eta: "\u03b7", theta: "\u03b8", iota: "\u03b9", kappa: "\u03ba",
  lambda: "\u03bb", mu: "\u03bc", nu: "\u03bd", xi: "\u03be", pi: "\u03c0", rho: "\u03c1",
  sigma: "\u03c3", tau: "\u03c4", phi: "\u03c6", chi: "\u03c7", psi: "\u03c8", omega: "\u03c9",
  Delta: "\u0394", Omega: "\u03a9", Sigma: "\u03a3", Pi: "\u03a0", Gamma: "\u0393",
  Lambda: "\u039b", Theta: "\u0398", Phi: "\u03a6", Psi: "\u03a8",
};
const LATEX_NAMES = Object.keys(LATEX_SYMBOLS).sort((a, b) => b.length - a.length);
const LATEX_KNOWN = new RegExp("\\\\(" + LATEX_NAMES.join("|") + ")(?![A-Za-z])", "g");
function plainText(t) {
  t = String(t || "");
  t = t.replace(/\$\$([^$]+)\$\$/g, (m, c) => " " + c.trim() + " ");
  t = t.replace(/\$([^$\n]+)\$/g, (m, c) => c);
  // Bare legacy font switches carry no content: drop them ("M_{\rm UV}" ->
  // "M_{UV}", never "Mrm UV"). Mirrors the server plain_text.
  t = t.replace(/\\(?:rm|bf|it|sf|tt|cal)(?![A-Za-z])/g, "");
  for (const name of ["mathrm", "mathbf", "mathit", "mathsf", "mathtt", "text", "textbf", "textit", "boldsymbol"])
    t = t.replace(new RegExp("\\\\" + name + "\\{([^{}]*)\\}", "g"), (m, c) => c);
  t = t.replace(LATEX_KNOWN, (m, n) => LATEX_SYMBOLS[n]);
  t = t.replace(/\\([A-Za-z]+)/g, (m, run) => {
    const k = LATEX_NAMES.find((k) => run !== k && run.startsWith(k));
    return k ? LATEX_SYMBOLS[k] + run.slice(k.length) : run;
  });
  t = t.replace(/\\[,;:!]/g, " ").replace(/\\\s+/g, " ");
  // Scripts keep an explicit marker: flattening concatenated the script into
  // the base and corrupted magnitudes (10^{9} -> "109"). 10^{9} -> 10^9,
  // MgAl$_2$O$_4$ -> MgAl_2O_4. Mirrors the server plain_text.
  t = t.replace(/_\{([^{}]*)\}/g, (m, c) => "_" + c.trim()).replace(/\^\{([^{}]*)\}/g, (m, c) => "^" + c.trim());
  t = t.replace(/_(\S)/g, (m, c) => "_" + c).replace(/\^(\S)/g, (m, c) => "^" + c);
  t = t.replace(/[{}]/g, "");
  t = t.replace(/^\s{0,3}#{1,6}\s*/gm, "");
  t = t.replace(/\*\*(.+?)\*\*/g, "$1").replace(/__(.+?)__/g, "$1").replace(/\*(.+?)\*/g, "$1");
  t = t.replace(/`+([^`]*)`+/g, "$1");
  t = t.replace(/\[([^\]]*)\]\(([^)\s]*)\)/g, (m, a, u) => (a + " (" + u + ")").trim());
  t = t.replace(/[ \t]{2,}/g, " ");
  return t.trim();
}
// Display-time mirror of the server-side match-span window: the evidence
// excerpt must show the span that supports the displayed answer, not the chunk
// head (design review 2026-10-25: the sources panel showed generic intro text
// while the answer quoted the matching passage further down).
const EXCERPT_STOP = new Set(("what which when where does about this that with from your have into tell more than then them they their there were will would could should " +
  "the and for are how why who is it of to in on a an do did can i me my mine we our us").split(" "));
function excerptWindow(text, question, size) {
  const low = text.toLowerCase();
  const terms = [...new Set(((question || "").toLowerCase().match(/[a-z0-9]{3,}/g) || [])
    .filter((w) => !/^\d+$/.test(w) && !EXCERPT_STOP.has(w)))];
  const groups = [];
  for (const w of terms) {
    const ps = [];
    let i = -1;
    while ((i = low.indexOf(w, i + 1)) >= 0) {
      const before = i === 0 || !/[a-z0-9]/.test(low[i - 1]);
      const after = i + w.length >= low.length || !/[a-z0-9]/.test(low[i + w.length]);
      if (before && after) ps.push(i);
    }
    if (ps.length) groups.push(ps);
  }
  if (!groups.length || text.length <= size) return text.slice(0, size) + (text.length > size ? "\u2026" : "");
  // Rarity-weighted hits, like the server: a term repeated all over the passage
  // must not outvote the few distinctive hits that actually answer the question.
  // Cluster selection uses the server's 320-char span even when the displayed
  // excerpt is shorter, or a tighter display window favors the chunk head again.
  const span = Math.max(size, 320);
  const hits = groups.flatMap((ps) => ps.map((p) => [p, 1 / ps.length]));
  let best = 0, bestScore = -1;
  for (const [h] of hits) {
    const s = Math.max(0, h - Math.floor(span / 3));
    const c = hits.reduce((a, [x, wt]) => a + (x >= s && x <= s + span ? wt : 0), 0);
    if (c > bestScore) { bestScore = c; best = s; }
  }
  let start = best;
  if (start > 0) { const sp = text.indexOf(" ", start); if (sp >= 0 && sp < start + 40) start = sp + 1; }
  let win = text.slice(start, start + size);
  if (win.length === size) win = win.replace(/\s+\S*$/, "");
  return (start > 0 ? "\u2026" : "") + win + (start + win.length < text.length ? "\u2026" : "");
}
const ICON = {
  clip: "M21 11.5l-8.6 8.6a5 5 0 01-7-7l9-9a3.3 3.3 0 014.7 4.7l-9 9a1.7 1.7 0 01-2.4-2.4l8.3-8.3",
  pin: "M12 17v5M9 3h6l-1 7 3 3v2H7v-2l3-3z",
  trash: "M4 7h16M10 11v6M14 11v6M6 7l1 13h10l1-13M9 7V4h6v3",
  edit: "M4 20h4L19 9l-4-4L4 16z",
  down: "M12 4v12M6 12l6 6 6-6",
  tray: "M12 3v11M7 10l5 5 5-5M5 20h14",
  topic: "M12 5v14M5 12h14",
  send: "M12 19V5M5 12l7-7 7 7",
  stop: "M7 7h10v10H7z",
  mic: "M12 15a3 3 0 003-3V6a3 3 0 00-6 0v6a3 3 0 003 3zM6 11a6 6 0 0012 0M12 17v4",
  temp: "M12 3a9 9 0 100 18 9 9 0 000-18zM12 7v5l3 2",
  user: "M12 12a4 4 0 100-8 4 4 0 000 8zM4 21a8 8 0 0116 0",
  up: "M12 20V8M6 12l6-6 6 6",
  menu: "M4 7h16M4 12h16M4 17h16",
  collapse: "M15 5l-7 7 7 7",
  close: "M6 6l12 12M18 6L6 18",
};
const svg = (n) => { const e = document.createElementNS("http://www.w3.org/2000/svg", "svg"); e.setAttribute("viewBox", "0 0 24 24"); e.setAttribute("width", "18"); e.setAttribute("height", "18"); e.setAttribute("fill", "none"); e.setAttribute("stroke", "currentColor"); e.setAttribute("stroke-width", "2"); e.setAttribute("stroke-linecap", "round"); e.setAttribute("stroke-linejoin", "round"); const p = document.createElementNS("http://www.w3.org/2000/svg", "path"); p.setAttribute("d", ICON[n]); e.append(p); return e; };
const S = { view: "chat", scope: null, suggestions: null, cfg: null, chat: null, topic: null, newTopic: false, tab: "chats", sources: new Set(), turns: [], ratings: {}, temp: false, useProfile: localStorage.getItem("cc_profile_on") === "1", busy: false, token: localStorage.getItem("cc_token") || "" };

const TV = (k) => ((window.CCTheme && window.CCTheme.value) || {})[k] || "";
const PREVIEW = !!window.__ccPreview;
function avatar(kind) {
  const e = TV(kind === "bot" ? "emoji_bot" : "emoji_you"), a = S.cfg.app;
  return el("div", { class: "av " + kind + (e ? " emo" : "") },e?CCEmoji.node(e,TV((kind==="bot"?"emoji_bot":"emoji_you")+"_animated"),"",["calm","none"].includes(TV("motion"))):document.createTextNode(kind==="bot"?(TV("txt_title")||a.title||"AI").replace(/[^A-Za-z]/g,"").slice(0,2):"You"));
}
async function api(path, body) {
  const h = { "Content-Type": "application/json" };
  if (S.token) h.Authorization = "Bearer " + S.token;
  const r = await fetch(path, body === undefined ? { headers: h } : { method: "POST", headers: h, body: JSON.stringify(body) });
  const d = await r.json().catch(() => ({}));
  if (r.status === 401 && S.cfg && S.cfg.auth === "accounts" && !path.startsWith("/api/account/")) { location.reload(); return new Promise(() => {}); }
  if (r.status === 401 && S.cfg && S.cfg.auth === "token") {
    const t = await CCDialog.prompt("Access token","",{secret:true,title:"Access token",okText:"Continue"}); if (t) { S.token = t; localStorage.setItem("cc_token", t); return api(path, body); }
  }
  if (!r.ok) throw new Error(d.error || "Request failed");
  return d;
}
function centerToast(t) { const m = document.querySelector(".main"); if (m) { const r = m.getBoundingClientRect(); t.style.left = (r.left + r.width / 2) + "px"; } return t; }
function toast(msg, actionLabel, action) {
  document.querySelectorAll(".toast").forEach(x=>x.dismissNotice ? x.dismissNotice() : x.remove());
  const message=el("span",{class:"toast-message",text:msg});
  const t=el("div",{class:"toast",role:"status","aria-live":"polite"},message);let timer,observer;
  const close=()=>{clearTimeout(timer);observer?.disconnect();window.removeEventListener("resize",place);t.remove()};t.dismissNotice=close;
  const place=()=>{t.style.bottom=(innerHeight-($(".composer")?.getBoundingClientRect().top||innerHeight-110)+16)+"px";centerToast(t)};
  if(action){const button=el("button",{type:"button",class:"toast-action",text:actionLabel,onclick:async()=>{if(button.disabled)return;button.disabled=true;try{await action();close()}catch(e){message.textContent=e.message||"Could not complete that action. Try again.";button.disabled=false}}});t.append(button)}
  t.append(el("button",{type:"button",class:"toast-dismiss","aria-label":"Dismiss notification",title:"Dismiss notification",text:"×",onclick:close}));
  document.body.append(t);place();if(window.ResizeObserver&&$(".composer")){observer=new ResizeObserver(place);observer.observe($(".composer"))}window.addEventListener("resize",place);
  const lifetime=Math.min(16000,Math.max(3500,1500+String(msg).length*65));
  const wait=()=>{clearTimeout(timer);if(!action)timer=setTimeout(close,lifetime)};
  t.addEventListener("mouseenter",()=>clearTimeout(timer));t.addEventListener("mouseleave",wait);t.addEventListener("focusin",()=>clearTimeout(timer));t.addEventListener("focusout",wait);wait();return t;
}


function inline(parent, text, evidence) {
  // safe inline markdown: **bold**, `code`, and [n] citations. Everything is text nodes.
  let afterCite = false;
  text.split(/(\*\*[^*]+\*\*|`[^`]+`|\[\d+\])/).forEach((p) => {
    let m; const wasCite = afterCite; afterCite = false;
    if ((m = p.match(/^\[(\d+)\]$/)) && evidence.some((e) => e.n === +m[1])) { parent.append(el("button", { class: "cite", title: "Show source " + m[1], onclick: (ev) => showSources(evidence, +m[1], ev.currentTarget) }, "[" + m[1] + "]")); afterCite = true; }
    else if (/^\*\*[^*]+\*\*$/.test(p)) parent.append(el("strong", { text: p.slice(2, -2) }));
    else if (/^`[^`]+`$/.test(p)) parent.append(el("code", { text: p.slice(1, -1) }));
    else if (p) parent.append(document.createTextNode((wasCite && /^[.,;:!?)]/.test(p) ? "\u2060" : "") + p));
  });
}
function renderAnswer(text, evidence) {
  const box = el("div", { class: "a" });
  let list = null, listType = null; const lines=text.split(/\n/);
  const cells=tableCells;
  for(let i=0;i<lines.length;i++) {
    const line=lines[i];
    if(/^\s*```/.test(line)){const buf=[];i++;while(i<lines.length&&!/^\s*```\s*$/.test(lines[i])){buf.push(lines[i]);i++}
      const wrap=el("div",{class:"codeblock-wrap"}),pre=el("pre",{class:"codeblock"}),code=el("code",{text:buf.join("\n")});pre.append(code);
      const cp=el("button",{type:"button",class:"codeblock-copy","aria-label":"Copy code",onclick:async(ev)=>{const b=ev.currentTarget;try{await navigator.clipboard.writeText(code.textContent);b.textContent="Copied";b.dataset.copied="true"}catch(e){b.textContent="Copy failed"}setTimeout(()=>{b.textContent="Copy";delete b.dataset.copied},1400)}},"Copy");
      wrap.append(cp,pre);box.append(wrap);list=null;continue}
    if(line.includes("|")&&i+1<lines.length&&/^\s*\|?\s*:?-{3,}/.test(lines[i+1])) {
      list=null;const head=cells(line), table=el("table",{class:"answer-table"}), top=el("tr"),body=el("tbody");
      head.forEach(t=>{const th=el("th",{scope:"col"});inline(th,t,evidence);top.append(th)});
      table.append(el("thead",{},top),body);i++;
      while(i+1<lines.length&&lines[i+1].includes("|")){const row=cells(lines[++i]);const tr=el("tr");head.forEach((_,n)=>{const td=el("td",{"data-label":head[n]});inline(td,row[n]||"",evidence);tr.append(td)});body.append(tr)}
      box.append(el("div",{class:"answer-table-wrap",tabindex:"0","aria-label":"Answer table"},table));continue;
    }
    const li=line.match(/^\s*([-*]|\d+[.)])\s+(.*)/),h=line.match(/^#{1,3}\s+(.*)/);
    if(li){const type=/^\d/.test(li[1])?"ol":"ul";if(!list||listType!==type){list=el(type,type==="ol"?{start:String(parseInt(li[1],10))}:{});listType=type;box.append(list)}const x=el("li");inline(x,li[2],evidence);list.append(x);continue}
    list=null;if(!line.trim())continue;const p=el(h?"h4":"p");inline(p,h?h[1]:line,evidence);box.append(p);
  }
  return box;
}
// Parse escaped pipes as literal label text, not as another column.
function tableCells(line) {
  const text=line.trim().replace(/^\||(?<!\\)\|$/g, "");
  return text.split(/(?<!\\)\|/).map(x=>x.trim().replace(/\\\|/g,"|"));
}
function headlineCounts(evidence) {
  const counts=new Map(), seen=new Map();
  evidence.forEach(e=>{
    const key=String(e.source||"Source"), id=e.url||e.id||String(e.n);
    if(!seen.has(key))seen.set(key,new Set());
    if(!seen.get(key).has(id)){seen.get(key).add(id);counts.set(key,(counts.get(key)||0)+1)}
  });
  return counts;
}
function chartData(answer, evidence) {
  const lines=answer.split(/\n/), start=lines.findIndex((x,i)=>x.includes("|")&&i+1<lines.length&&/^\s*\|?\s*:?-{3,}/.test(lines[i+1]));
  if(start<0)return null; // No chart when the answer gives no supported count table.
  const headers=tableCells(lines[start]), counts=headlineCounts(evidence), rows=[], labels=new Set();
  if(headers.length!==3||!/^source$/i.test(headers[0])||!/^headline count$/i.test(headers[1])||!/^citations$/i.test(headers[2]))return null;
  for(let i=start+2;i<lines.length&&lines[i].includes("|");i++){
    const c=tableCells(lines[i]);
    if(c.length!==3||!/^\d+$/.test(c[1])||labels.has(c[0])||counts.get(c[0])!==Number(c[1]))return null;
    const cites=[...c[2].matchAll(/\[(\d+)\]/g)].map(m=>Number(m[1]));
    if(!cites.length||cites.some(n=>!evidence.some(e=>e.n===n&&String(e.source||"Source")===c[0])))return null;
    labels.add(c[0]);rows.push({label:c[0],value:Number(c[1])});
  }
  return rows.length&&rows.length<=20?rows:null;
}
function answerChart(answer, evidence) {
  const rows=chartData(answer,evidence);if(!rows)return null;
  const chart=el("figure",{class:"answer-chart","aria-label":"Retrieved headline count by source"}),max=Math.max(...rows.map(r=>r.value),1);
  chart.append(el("figcaption",{text:"Retrieved headline count by source"}));
  rows.forEach(r=>chart.append(el("div",{class:"answer-chart-row"},el("span",{text:r.label}),el("div",{class:"answer-chart-track"},el("div",{class:"answer-chart-bar",style:"width:"+(r.value/max*100)+"%"})),el("span",{text:String(r.value)}))));
  chart.append(el("small",{text:"Counts of unique retrieved headlines only. Not a real-world trend or topic breakdown."}));return chart;
}

function highlight(node, text, terms) {
  if (!terms.length) { node.textContent = text; return node; }
  const re = new RegExp("(" + terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|") + ")", "gi");
  text.split(re).forEach((p, i) => node.append(i % 2 ? el("mark", { text: p }) : document.createTextNode(p)));
  return node;
}
function chatTitleFrom(q, limit = 60) {
  q = q.trim();
  if (q.length <= limit) return q;
  if (q[limit] === " ") return q.slice(0, limit).replace(/[\s,;:]+$/, "");
  const cut = q.slice(0, limit).replace(/\s+\S*$/, "").replace(/[\s,;:]+$/, "");
  return cut.length >= 20 ? cut : q.slice(0, limit).trim();
}
function sendIcon(name, label) {
  const send = $("#send"); send.replaceChildren(name === "send" && TV("emoji_send") ? CCEmoji.node(TV("emoji_send"),TV("emoji_send_animated"),"",["calm","none"].includes(TV("motion"))) : svg(name)); send.setAttribute("aria-label", label); rdy();
  if (motionAllowed() && send.animate) send.animate([{opacity:.5,transform:"scale(.95)"},{opacity:1,transform:"scale(1)"}],{duration:150,easing:"ease-out"});
}
function motionAllowed() { return !["none","calm"].includes(document.documentElement.dataset.motion) && !matchMedia("(prefers-reduced-motion: reduce)").matches; }
let sourceExit, sourceTrigger, sourceShield = new Map();
function quietSourceMotion(){
  if(motionAllowed())return;
  const closing=!!sourceExit;
  if(sourceExit){sourceExit.onfinish=null;sourceExit.cancel();sourceExit=null;}
  $("#sources")?.getAnimations({subtree:true}).forEach(a=>a.cancel());
  if(closing)$("#app").classList.remove("src");
}
matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change",quietSourceMotion);
new MutationObserver(quietSourceMotion).observe(document.documentElement,{attributes:true,attributeFilter:["data-motion"]});

function sourceModal(open) {
  const pane = $("#sources"), mobile = matchMedia("(max-width:860px)").matches;
  if (!open || !mobile) { for (const [n, value] of sourceShield) n.inert = value; sourceShield.clear(); pane.removeAttribute("role"); pane.removeAttribute("aria-modal"); return; }
  pane.setAttribute("role", "dialog"); pane.setAttribute("aria-modal", "true");
  for (const n of [$(".toolbar"),$("#side"),$(".main")]) if(n&&!sourceShield.has(n)){sourceShield.set(n,n.inert);n.inert=true}
  pane.querySelector("button")?.focus({preventScroll:true});
}
function closeSources() {
  const pane = $("#sources");
  sourceModal(false);
  if (sourceTrigger?.isConnected) sourceTrigger.focus({preventScroll:true});
  if (!motionAllowed() || !pane.animate) { $("#app").classList.remove("src"); return; }
  sourceExit = pane.animate([{opacity:1, transform:"translateX(0)"}, {opacity:0, transform:"translateX(12px)"}], {duration:160, easing:"ease-in"});
  sourceExit.onfinish = () => { $("#app").classList.remove("src"); sourceExit = null; };
}
function showSources(evidence, hl, trigger) {
  sourceTrigger = trigger || document.activeElement;
  const terms = [...new Set(((S.turns[S.turns.length - 1] || {}).standalone || "").toLowerCase().match(/[a-z0-9]{4,}/g) || [])].slice(0, 8);
  const pane = $("#sources");
  if (sourceExit) { sourceExit.onfinish = null; sourceExit.cancel(); sourceExit = null; }
  const opening = !$("#app").classList.contains("src"); pane.replaceChildren();
  $("#app").classList.add("src");
  const types = [...new Set(evidence.map((e) => e.source))];
  const filters = el("div", { class: "filters" });
  const list = el("div");
  const draw = (only) => {
    list.replaceChildren(...evidence.filter((e) => !only || e.source === only).map((e) => el("div", { class: "src" + (e.n === hl ? " hl" : "") },
      el("b", { text: e.n + ". " + plainText(e.title) }),
      el("small", { text: [(e.authors || []).slice(0, 3).join(", "), e.year, e.venue, e.document, e.page ? "page " + e.page : e.section, e.version ? "version " + e.version.slice(0, 12) : "", e.ocr ? "OCR text, check original" : ""].filter(Boolean).join(" · ") }),
      highlight(el("p", {class:e.text ? "source-text" : "source-unavailable"}), e.text ? excerptWindow(plainText(e.text), (S.turns[S.turns.length - 1] || {}).standalone || "", 280) : "Source excerpt unavailable. This saved reference has no text to inspect.", terms),
      e.url ? el("a", { href: e.url, target: "_blank", rel: "noopener noreferrer", text: "Open source" }) : null)));
  };
  if (types.length > 1) types.forEach((t) => filters.append(el("button", { class: "chip", "aria-pressed":"false", onclick: (ev) => {
    const button=ev.currentTarget,on=button.classList.toggle("on"); filters.querySelectorAll(".chip").forEach(c=>{if(c!==button)c.classList.remove("on");c.setAttribute("aria-pressed",String(c===button&&on))}); draw(on ? t : null);
  } }, (S.cfg.sources.find((s) => s.id === t) || {}).label || t)));
  pane.append(el("button", { class: "icon", style: "float:right", "aria-label": "Close sources", title: "Close sources", onclick: closeSources }, svg("close")),
    el("h3", { text: "Sources" }), el("div", { class: "sub", text: evidence.length + " used for this answer" }), filters, list);
  draw(null); sourceModal(true);
  if (opening && motionAllowed() && pane.animate) pane.animate([{opacity:0, transform:"translateX(4px)"}, {opacity:1, transform:"translateX(0)"}], {duration:240, easing:"cubic-bezier(.2,.8,.2,1)"});
  const selected = list.querySelector(".hl");
  document.querySelectorAll(".cite-selected").forEach(x=>x.classList.remove("cite-selected"));
  if(trigger?.classList.contains("cite")) trigger.classList.add("cite-selected");
  if(trigger?.classList.contains("s")) trigger.classList.add("cite-selected");
  if (selected) {
    selected.scrollIntoView({block:"nearest", behavior:motionAllowed() ? "smooth" : "auto"});
    if (motionAllowed() && selected.animate) selected.animate([{opacity:.7, transform:"translateY(2px)"},{opacity:1, transform:"none"}],{duration:180,easing:"ease-out"});
  }
}

function turnView(t, prev) {
  const nodes = [];
  if (prev && prev.chat !== t.chat) nodes.push(el("div", { class: "divider", text: "Earlier chat" }));
  nodes.push(el("div", { class: "row u" }, avatar("you"), el("div", { class: "bubble ub", text: t.question })));
  const bub = el("div", { class: "bubble bb" + (t.evidence.length ? "" : " none") }, renderAnswer(t.answer, t.evidence));
  if(/\b(chart|graph|plot)\b/i.test(t.question)){const chart=answerChart(t.answer,t.evidence);if(chart)bub.append(chart);}
  const failedSources = Object.entries(t.source_errors || {});
  if (failedSources.length) {
    const srcName = (id) => (S.cfg.sources.find((x) => x.id === id) || {}).label || id;
    const allFailed = failedSources.length >= ((S.cfg.sources || []).length || 1);
    // A sentence-valued error names the concrete cause (for example a missing free API
    // key); a bare exception type name stays behind the generic wording.
    const named = failedSources.map(([id, msg]) => typeof msg === "string" && msg.includes(" ") ? srcName(id) + ": " + msg : null).filter(Boolean);
    const note = named.length
      ? named.join(" ") + (allFailed ? "" : " Answered from the other sources.")
      : failedSources.map(([id]) => srcName(id)).join(", ") + " could not be reached" + (allFailed ? " for this question." : " - answered from the other sources.");
    bub.append(el("div", { class: "src-note", role: "note", text: note }));
  }
  if (!t.evidence.length) {
    const ill = document.createElementNS("http://www.w3.org/2000/svg", "svg"); ill.setAttribute("viewBox", "0 0 96 96"); ill.setAttribute("class", "nf-ill"); ill.setAttribute("aria-hidden", "true");
    ill.innerHTML = '<g fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M26 14h30l14 14v50H26z"/><path d="M56 14v15h14"/><path d="M36 42h24M36 52h18" opacity=".5"/><circle cx="58" cy="62" r="13" class="nf-lens"/><path d="m67 71 12 12"/></g>';
    bub.prepend(el("div", { class: "nf-h", text: "No evidence found" }));
    bub.prepend(ill);
    const tip = (txt, fn) => el("button", { class: "tip", onclick: fn }, el("span", { text: txt }), el("span", { class: "go", "aria-hidden": "true", text: "\u203a" }));
    bub.append(el("div", { class: "nf-tips" }, tip("Try a different question", () => { $("#q").focus(); }), tip("Use words from your documents", () => { $("#q").focus(); }), tip("See which documents this chat uses", () => { location.href = (window.CC_APP_BASE||"") + "/settings.html"; })));
  }
  const srcLabel = (e) => (S.cfg.sources.find((x) => x.id === e.source) || {}).label || e.source || "";
  const srcs = !t.evidence.length ? null : (el("div", { class: "srcs" }, el("div", { class: "srcs-h", text: "Evidence for this answer" }), t.evidence.slice(0, 5).map((e) => el("button", { class: "s", title: plainText(e.title), onclick: (ev) => showSources(t.evidence, e.n, ev.currentTarget) }, el("span", { class: "n", text: "[" + e.n + "]" }), el("span", { class: "sx" }, el("span", { class: "st", text: srcLabel(e) ? srcLabel(e) + " / " + plainText(e.title) : plainText(e.title) }), el("span", {class:"source-excerpt",text:e.text ? excerptWindow(plainText(e.text), t.question, 240) : "Source excerpt unavailable"}), el("span", { class: "sm", text: [srcLabel(e), e.year, e.page ? "page " + e.page : e.section, e.ocr ? "OCR text, check original" : ""].filter(Boolean).join(" \u00b7 ") })), el("span", { class: "go", "aria-hidden": "true", text: "\u203a" })))));
  nodes.push(el("div", { class: "row" }, avatar("bot"), bub));
  const meta = el("div", { class: "meta" });
  const weak = (t.ledger || []).filter((l) => !l.supported || (l.overlap !== undefined && l.overlap < 0.35));
  if (t.evidence.length && weak.length) meta.append(el("button", { class: "chip warn", title: "Sentences without a valid citation or with little overlap with the cited text. Click to see them.", onclick: () => CCDialog.alert("Check these sentences:\n\n" + weak.map((l) => "- " + l.claim).join("\n"),{title:"Sentences to check"}) }, weak.length + " to check"));
  if (t.seconds !== undefined) meta.append(el("span", { "data-more": "1", class: "chip", title: "Time to answer" }, t.seconds < 1 ? "<1s" : t.seconds + "s"));
  if (t.standalone && t.standalone !== t.question) meta.append(el("span", { class: "chip", title: "Understood as" }, "Understood as: " + t.standalone));
  if (t.scope) meta.append(el("span", {class:"chip scope-used", text:"Scoped: " + (t.scope.document || t.scope.source)}));
  meta.append(el("button", { "data-more": "1", class: "chip", title: "How this answer was built", onclick: () => contextDialog(t) }, "Context"));
  let answerCopyStatus;
  if (t.evidence.length) {
    const status=el("span",{class:"copy-status","role":"status",hidden:true});
    let copying=false,resetTimer;
    const copy=el("button",{class:"chip copy",onclick:async()=>{
      if(copying)return;copying=true;clearTimeout(resetTimer);copy.classList.remove("done");copy.textContent="Copying...";copy.setAttribute("aria-busy","true");status.hidden=true;
      try{
        if(!navigator.clipboard)throw Error("Clipboard unavailable. Select and copy the answer instead.");
        await navigator.clipboard.writeText(t.answer);copy.textContent="Copied";copy.classList.add("done");status.textContent="Answer copied.";status.hidden=false;
        resetTimer=setTimeout(()=>{copy.textContent="Copy";copy.classList.remove("done");status.hidden=true},1600);
      }catch(e){copy.textContent="Copy";copy.classList.remove("done");status.textContent=e.message||"Could not copy. Select and copy the answer instead.";status.hidden=false}
      finally{copying=false;copy.removeAttribute("aria-busy")}
    }},"Copy");
    meta.append(copy);answerCopyStatus=status;
  }
  if (t.evidence.length) {
    meta.append(el("button", { "data-more": "1", class: "chip", onclick: () => download("/api/bibtex?turn=" + t.id, "references.bib") }, "BibTeX"));
    meta.append(el("button", {"data-more":"1",class:"chip",onclick:()=>download("/api/answer-markdown?turn="+t.id,"answer.md")},"Markdown"));
    meta.append(el("button", { "data-more": "1", class: "chip", onclick: () => download("/api/pdf?turn=" + t.id, "answer.pdf") }, "PDF"));
    for (const s of ["quick", "deep"]) if (S.cfg.styles.includes(s)) meta.append(el("button", { "data-more": "1", class: "chip", onclick: () => regen(t.id, s) }, s === "quick" ? "Shorter" : "Deeper"));
  }
  if (srcs) bub.append(srcs);
  bub.append(meta);if(answerCopyStatus)bub.append(answerCopyStatus);
  if (t.followups && t.followups.length) {
    const f = el("div", { class: "meta fu" });
    t.followups.forEach((x) => f.append(el("button", { class: "chip", onclick: () => { $("#q").value = x; send(); } }, x)));
    nodes.push(el("div", { class: "fu-label", text: "Related" }), f);
  }
  meta.append(el("button", { "data-more": "1", class: "chip", onclick: () => branchQuestion(t) }, "Edit + branch"));
  meta.append(el("button", { "data-more": "1", class: "chip del", title: "Delete this answer", onclick: async () => {
    await api("/api/delete-turn", { turn: t.id }); S.turns = S.turns.filter((x) => x.id !== t.id); drawThread();
    toast("Answer deleted.", "Undo", async () => { await api("/api/restore-turn", { turn: t.id }); S.turns = await api(S.view === "topic" && S.topic ? "/api/topic-turns?topic=" + S.topic : "/api/turns?chat=" + S.chat); drawThread(); }); } }, "Delete"));
  const more = [...meta.querySelectorAll("[data-more]")];
  if (more.length) { const d = el("details", { class: "more" }, el("summary", { class: "chip" }, t.evidence.length ? "More" : "Details")); const box = el("div", { class: "more-box" }); more.forEach((b) => box.append(b)); d.append(box);d.addEventListener('toggle',()=>{positionAnswerMore(d);requestAnimationFrame(()=>positionAnswerMore(d))}); meta.append(d); }
  return nodes;
}
function positionAnswerMore(d) {
  if(!d.open)return;
  const box=d.querySelector('.more-box'),summary=d.querySelector('summary'),thread=d.closest('.thread');if(!box||!thread)return;
  const bounds=thread.getBoundingClientRect(),r=summary.getBoundingClientRect(),above=Math.max(0,r.top-bounds.top-22),below=Math.max(0,bounds.bottom-r.bottom-22),up=above>=box.scrollHeight||above>=below;
  box.style.maxHeight=Math.max(44,up?above:below)+'px';box.style.overflowY='auto';box.style.boxSizing='border-box';box.style.bottom=up?'calc(100% + 6px)':'auto';box.style.top=up?'auto':'calc(100% + 6px)';
  box.style.left='0px';const br=box.getBoundingClientRect();box.style.left=Math.min(0,bounds.right-8-br.right)+'px';
}
window.addEventListener('resize',()=>document.querySelectorAll('.more[open]').forEach(positionAnswerMore));
document.addEventListener('scroll',e=>{if(e.target.classList?.contains('thread'))e.target.querySelectorAll('.more[open]').forEach(positionAnswerMore)},true);
async function branchQuestion(t) {
  if (S.busy) return toast("Wait for the current answer or stop it first");
  const question = await CCDialog.prompt("Edit this question. A new branch keeps earlier context and leaves the original unchanged.", t.question, {title:"Edit + branch", multiline:true, okText:"Branch"});
  if (question == null || !question.trim()) return;
  if (S.temp) return toast("Edit + branch needs a saved chat. Temporary chats stay unsaved.");
  try {
    const result = await api("/api/branch", {turn:t.id, question});
    await openChat(result.chat);
    $("#q").value = result.question; autosize(); rdy(); $("#q").focus();
    const notice = el("div", {class:"branch-notice"}, "New branch. Original unchanged. ", el("button", {class:"chip", onclick:()=>{$("#q").value="";autosize();rdy();openChat(result.original_chat)}}, "Open original"));
    $("#thread .wrap").prepend(notice);
    toast("Branch ready. Review and send your edited question.");
  } catch(e) { toast(e.message); }
}
async function download(path, name) {
  const h = S.token ? { Authorization: "Bearer " + S.token } : {};
  const r = await fetch(path, { headers: h }); if (!r.ok) { const failure = await r.json().catch(() => ({})); return toast(typeof failure.error === "string" ? failure.error : "Download failed"); }
  const a = el("a", { href: URL.createObjectURL(await r.blob()), download: name }); a.click();
}

function scopeChip() {
 const p=$("#scopeChip");p.replaceChildren();
 $("#scopeBtn").setAttribute("aria-label","Source scope: "+(S.scope?("only "+(S.scope.document||S.scope.source)):"all documents"));
 if (S.scope) p.append(el("span",{class:"scope-selected-label",text:"Only " + (S.scope.document || S.scope.source),title:"Only " + (S.scope.document || S.scope.source)}),el("button",{class:"chip",onclick:()=>{S.scope=null;scopeChip();$("#scopeBtn").focus()}},"Clear"));
}
async function scopeDialog() {
 const origin=document.activeElement,trigger=$("#scopeBtn");if(trigger.dataset.running==="true")return;trigger.dataset.running="true";trigger.setAttribute("aria-busy","true");const original=trigger.textContent,originalMinWidth=trigger.style.minWidth;trigger.style.minWidth=trigger.getBoundingClientRect().width+"px";trigger.textContent="Loading...";$("#scopeError").hidden=true;
 try {
  const rows=await api("/api/scopes");const dialog=el("dialog",{class:"reading-dialog scope-dialog","aria-label":"Choose source scope"});
  dialog.append(el("header",{class:"reading-head"},el("h2",{text:"Choose source scope"})));
  const options=el("div",{class:"scope-options"});
  for (const row of rows) {
   const choose=(document)=>{S.scope={source:row.source,...(document?{document}:{})};scopeChip();dialog.close()};
   options.append(el("button",{class:"chip",onclick:()=>choose()},"Collection: "+row.label));
   row.documents.forEach(doc=>options.append(el("button",{class:"chip",onclick:()=>choose(doc)},doc)));
  }
  if (!rows.length) options.append(el("p",{class:"scope-empty",role:"status",text:"No configured sources"}));
  dialog.append(options,el("footer",{},el("button",{class:"reading-done",onclick:()=>dialog.close()},"Done")));
  dialog.addEventListener("close",()=>{dialog.remove();(origin?.isConnected&&origin!==document.body?origin:trigger).focus()});document.body.append(dialog);dialog.showModal();
 } catch(e){const error=$("#scopeError");error.textContent="Could not load sources: "+e.message+". Try Source scope again.";error.hidden=false}finally{trigger.dataset.running="false";trigger.removeAttribute("aria-busy");trigger.textContent=original;trigger.style.minWidth=originalMinWidth}
}
async function loadSuggestions() {
  if (PREVIEW) return;
  try { S.suggestions = await api("/api/suggestions", {temporary: S.temp}); if (!S.turns.length) drawThread(); }
  catch (_) { /* Configured examples remain usable if budget/provider is unavailable. */ }
}
function recentQuestions() {
  if (S.temp || !S.suggestions || !S.suggestions.recent.length) return null;
  const starters=TV("txt_examples")?TV("txt_examples").split("\n"):S.suggestions.questions;
  const shown=new Set(starters.map(x=>x.trim().toLocaleLowerCase()));
  const recent=S.suggestions.recent.filter(x=>!shown.has(x.trim().toLocaleLowerCase()));
  if(!recent.length)return null;
  return el("div", {class:"recent-questions"}, el("p", {class:"fu-label",text:"Your recent questions"}),
    el("div",{class:"ex"}, recent.map(x=>el("button",{onclick:()=>{$("#q").value=x;send();}},x))));
}
function gettingStarted() {
  if (PREVIEW || S.temp) return null;
  const cards = [
    ["1", "How do I ask my first question?", "Use a sample below, or type a question about your documents.", () => { $("#q").focus(); }],
    ["2", "How do I add my documents?", "Upload a PDF or text file, then ask about it.", uploadDialog],
    ["3", "How do I choose what to search?", "Limit the next answer to one collection or document.", scopeDialog],
    ["4", "How do I change the reading view?", "Choose your text size and answer width.", () => $("#readingBtn").click()],
  ];
  if (document.querySelector('.common-nav a[href="/settings.html"]')) cards.push(
    ["5", "How do I connect an AI model?", "Demo is offline. Choose a provider and test it in Configuration.", () => { location.href=(window.CC_APP_BASE||"") + "/settings.html#sec-model"; }]);
  cards.push([String(cards.length+1), "How do I try an action?", "Preview a local note action. Nothing is saved until you confirm.", () => $("#actionsBtn").click()]);
  const box = el("section", {class:"getting-started", "aria-label":"Getting started"}, el("h2", {text:"Start here"}),
    el("p", {class:"getting-started-note",text:S.cfg.provider.type === "mock" ? "You're in offline Demo. Try the app first, then connect an AI model when you're ready." : "Follow these steps at your own pace. Your existing documents and chats stay unchanged."}));
  box.append(el("div", {class:"start-grid"}, cards.map(([n,title,detail,action]) => el("button", {class:"start-card",onclick:action},
    el("span", {class:"start-number",text:n}), el("span", {},el("b", {text:title}),el("small", {text:detail}))))));
  box.append(el("p", {class:"getting-started-note",text:"After an answer: click [1] to check its source. Use the download button to export your chat."}));
  return box;
}
function temporaryScene(){return el("div",{class:"temp-concept"},el("h1",{text:"Temporary chat"}),el("p",{text:"This conversation is not saved. Your profile and uploaded sources stay out of it."}),el("button",{type:"button",text:"Back to saved chats",onclick:()=>$("#tempPill").click()}));}
function playgroundLanding(a, exs) {
  const scene=el("div",{class:"playground-scene","aria-hidden":"true"});
  const custom=TV("logo"), emoji=TV("emoji_hero")||TV("emoji_bot");
  if(custom)scene.prepend(el("img",{class:"playground-logo",src:custom,alt:""}));
  else if(emoji)scene.prepend(CCEmoji.node(emoji,TV((TV("emoji_hero")?"emoji_hero":"emoji_bot")+"_animated"),"",["calm","none"].includes(TV("motion"))));
  const actions=[
    ["↥","Add documents","Upload your files",uploadDialog],
    ["⌕","Choose sources","Select existing sources",scopeDialog],
    ["Aa","Reading view","Text size and width",()=>$("#readingBtn").click()]
  ];
  if(document.querySelector('.common-nav a[href="/settings.html"]'))actions.push(["↗","Connect a model","Choose an AI provider",()=>{location.href=(window.CC_APP_BASE||"") + "/settings.html#sec-model"}]);
  return el("section",{class:"hero playground"},
    el("div",{class:"playground-intro"},el("div",{class:"rise"},
      el("div",{class:"kicker","aria-hidden":"true"},document.createTextNode("Grounded in your sources")),
      el("h1",{text:TV("txt_title")||((a.title==="Chatify")?"Ask the documents, get the receipts.":a.title)}),el("p",{class:"lede",text:TV("txt_tagline")||((a.title==="Chatify")?"Answers grounded in the sources you choose, with the passages shown so you can check them.":a.tagline)})),scene),
    exs.length?el("div",{class:"rise",style:"--rise-order:1"},el("h2",{class:"playground-label",text:"Follow your curiosity"}),
      el("div",{class:"playground-questions"},exs.map((x,i)=>el("button",{class:"playground-question",style:"--question-order:"+i,onclick:()=>{$("#q").value=x;send()}},el("span",{text:x}),el("b",{"aria-hidden":"true",text:"↗"}))))):null,
    el("div",{class:"rise",style:"--rise-order:2"},el("h2",{class:"playground-label shortcut-label",text:"Chat tools"}),el("div",{class:"playground-actions"},actions.map(([icon,title,detail,action])=>el("button",{class:"playground-action",title:title+": "+detail,onclick:action},el("em",{"aria-hidden":"true",text:icon}),el("b",{text:title}),el("small",{text:detail}))))),
    el("p",{class:"playground-quiet",text:S.cfg.provider.type==="mock"?"Demo uses built-in answers. No model or paid calls.":"Answers use your configured sources and model."}));
}
function heroView() {
  if(S.temp&&!PREVIEW)return temporaryScene();
  const a = S.cfg.app;
  const he = TV("emoji_hero") || TV("emoji_bot"), exs = TV("txt_examples") ? TV("txt_examples").split("\n").map((x) => x.trim()).filter(Boolean).slice(0, 8) : (S.suggestions ? S.suggestions.questions : a.examples);
  if(!PREVIEW)return playgroundLanding(a,exs);
  return el("div", { class: "hero" + (PREVIEW ? " mini" : "") }, TV("logo") ? el("img", { class: "hero-logo", src: TV("logo"), alt: "" }) : el("div", { class: "av bot" + (he ? " emo emo-"+TV((TV("emoji_hero")?"emoji_hero":"emoji_bot")+"_motion") : ""), },he?CCEmoji.node(he,TV((TV("emoji_hero")?"emoji_hero":"emoji_bot")+"_animated"),"",["calm","none"].includes(TV("motion"))):document.createTextNode((TV("txt_title")||a.title||"AI").replace(/[^A-Za-z]/g,"").slice(0,2))), el("div", {}, el("h1", { text: S.temp ? "Temporary chat" : TV("txt_title") || a.title }), el("p", { text: S.temp ? "This chat is not saved. Your profile and uploaded sources are not used." : TV("txt_tagline") || a.tagline }),
    el("div", { class: "ex" }, exs.map((x) => el("button", { onclick: () => { $("#q").value = x; send(); } }, x))), gettingStarted()));
}
function chartCard() {
  const parts = [["Group A", 46, "var(--brand)"], ["Group B", 31, "var(--lime)"], ["Group C", 23, "var(--mut)"]];
  let off = 0; const C = 2 * Math.PI * 15.9155;
  const ring = parts.map(([n, v, c]) => { const e = '<circle r="15.9155" cx="21" cy="21" fill="none" stroke="' + c + '" stroke-width="6" stroke-dasharray="' + (v * C / 100) + ' ' + C + '" stroke-dashoffset="' + (-off * C / 100) + '" transform="rotate(-90 21 21)"></circle>'; off += v; return e; }).join("");
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg"); svg.setAttribute("viewBox", "0 0 42 42"); svg.setAttribute("class", "donut"); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Sample chart: groups of documents"); svg.innerHTML = ring;
  return el("div", { class: "chartcard" }, el("b", { text: "Sample chart: groups of documents" }), el("div", { class: "chartrow" }, svg, el("ul", {}, parts.map(([n, v, c]) => el("li", {}, el("i", { style: "background:" + c }), n + " " + v + "%")))));
}
function composerSwap() {
  const s = $("#send"), m = $("#mic"); if (!s || !m) return;
  const sr = !!(window.SpeechRecognition || window.webkitSpeechRecognition);
  if (!sr) { s.hidden = false; return; }
  const has = !!(($("#q") || {}).value || "").trim();
  if (S.busy) { s.hidden = false; m.hidden = true; return; }
  s.hidden = !has; m.hidden = has;
}
function rdy() { const q = $("#q"), s = $("#send"); if (!q || !s) return; const on = !!q.value.trim(); s.disabled = !S.busy && !on; s.classList.toggle("idle", s.disabled); if (S.busy) return; if (on && !s.classList.contains("on")) { s.classList.add("ready"); setTimeout(() => s.classList.remove("ready"), 200); } s.classList.toggle("on", on); composerSwap(); }
function syncLatest() {
  const th = $("#thread"), jump = $("#jump"); if (!th || !jump) return;
  jump.style.bottom = ($(".composer")?.offsetHeight || 96) + 16 + "px";
  const away = th.scrollHeight - th.scrollTop - th.clientHeight > 100;
  if (!away) jump.dataset.reply = "";
  const ready = jump.dataset.reply === "ready";
  const showJump = away && !th.querySelector(".hero");
  jump.classList.toggle("show", showJump); jump.tabIndex = showJump ? 0 : -1;
  jump.setAttribute("aria-label", ready ? "Reply ready. Scroll to latest" : "Scroll to latest");
  jump.title = ready ? "Reply ready. Scroll to latest" : "Scroll to latest";
  jump.classList.toggle("reply-ready", ready);
  jump.replaceChildren(svg("down"), ...(ready ? [el("span", {text:"Reply ready"})] : []));
}
function drawThread() {
  const th = $("#thread"), priorScroll = th.scrollTop, keep = th.scrollHeight - th.scrollTop - th.clientHeight > 100; th.replaceChildren();
  const w = el("div", { class: "wrap" });
  if (!S.turns.length) {
    const a = S.cfg.app;
    const he = TV("emoji_hero") || TV("emoji_bot"), exs = TV("txt_examples") ? TV("txt_examples").split("\n").map((x) => x.trim()).filter(Boolean).slice(0, 8) : (S.suggestions ? S.suggestions.questions : a.examples);
    w.append(heroView()); const recent = recentQuestions(); if (recent) w.append(recent);
  } else { if (PREVIEW) w.append(heroView()); S.turns.forEach((t, i) => w.append(...turnView(t, S.turns[i - 1]))); if (PREVIEW) w.append(chartCard()); }
  { const rows = [...w.querySelectorAll(".row")], same = th.dataset.chat === String(S.chat), prev = same ? +th.dataset.n || 0 : 0; rows.forEach((r, i) => { if (i >= prev) r.classList.add("fresh"); }); th.dataset.chat = String(S.chat); th.dataset.n = rows.length; }
  th.append(w); th.scrollTop = PREVIEW || !S.turns.length ? 0 : (keep ? priorScroll : th.scrollHeight);
  $("#pills").replaceChildren(); syncLatest();
}

function activateHistory(e,open){if(e.target!==e.currentTarget)return;if(e.key==='Enter'||e.key===' '){e.preventDefault();open()}}
function dayLabel(ts) {
  const d = new Date(ts * 1000), n = new Date(), day = 86400000, start = new Date(n.getFullYear(), n.getMonth(), n.getDate()).getTime();
  if (d.getTime() >= start) return "Today"; if (d.getTime() >= start - day) return "Yesterday"; if (d.getTime() >= start - 7 * day) return "This week"; return "Earlier";
}
let historySkeletonTimer=0,historyShimmerTimer=0;
async function loadList() {
  const seq = (loadList.seq = (loadList.seq || 0) + 1); const list = $("#list"), tab = S.tab, query = $("#search").value.trim();if(list.querySelector(".history-state")?.contains(document.activeElement))$("#search").focus();
  clearTimeout(historySkeletonTimer);clearTimeout(historyShimmerTimer);list.querySelector(".history-skeleton")?.remove();list.setAttribute("aria-busy","true");list.querySelector(".history-state")?.remove();
  const state=el("div",{class:"history-state",role:"status",text:"Loading history..."});if(list.querySelector(".item"))list.append(state);else list.prepend(state);
  if(!list.querySelector(".item")){historySkeletonTimer=setTimeout(()=>{if(seq!==loadList.seq)return;const skeleton=el("div",{class:"history-skeleton","aria-hidden":"true"});for(let i=0;i<3;i++)skeleton.append(el("div",{class:"history-skeleton-row"},el("span"),el("span")));state.append(skeleton);historyShimmerTimer=setTimeout(()=>{if(seq===loadList.seq)skeleton.classList.add("slow")},750)},250)}
  try {
    if (tab === "chats") {
      const rows = await api("/api/chats?q=" + encodeURIComponent($("#search").value)); if (seq !== loadList.seq) return;delete list.dataset.topicsSignature;const signature=JSON.stringify([tab,query,rows]);if(list.dataset.chatsSignature===signature&&list.querySelectorAll(".item").length===rows.length){const items=list.querySelectorAll(".item");rows.forEach((c,i)=>{items[i].classList.toggle("on",c.id===S.chat);if(c.id===S.chat)items[i].setAttribute("aria-current","true");else items[i].removeAttribute("aria-current")});return}list.dataset.chatsSignature=signature;list.replaceChildren();
      if (!rows.length) list.append(el("div", { class: "empty", text: query ? "No chats match your search. Try another word or clear the search." : "Your conversations will appear here. Ask a question to start." }));
      let lastGroup = "";
      const cnt = {}; rows.forEach((c) => { cnt[c.title] = (cnt[c.title] || 0) + 1; });
      rows.forEach((c) => { const g = c.pinned ? "Pinned" : dayLabel(c.created); if (g !== lastGroup) { list.append(el("div", { class: "group", text: g })); lastGroup = g; } list.append(el("div", { class: "item" + (c.id === S.chat ? " on" : ""), title: c.title, "aria-current":c.id===S.chat?"true":"false", role:"button",tabindex:"0","aria-label":"Open chat: "+c.title,onkeydown:e=>activateHistory(e,()=>openChat(c.id)), onclick: () => openChat(c.id) },
        el("span", { class: "t", text: c.title }), cnt[c.title] > 1 ? el("span", { class: "tm", text: new Date(c.created * 1000).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) }) : null, c.pinned ? el("span", { class: "pinned", title: "Pinned" }, svg("pin")) : null,
        el("span", { class: "acts" },
          el("button", { class: c.pinned ? "is-pinned" : "", title: c.pinned ? "Unpin" : "Pin", "aria-label": (c.pinned ? "Unpin " : "Pin ") + c.title, "aria-pressed": c.pinned ? "true" : "false", onclick: async (e) => { e.stopPropagation(); await api("/api/pin", { chat: c.id, pinned: !c.pinned }); loadList(); } }, svg("pin")),
          el("button", { title: "Rename", "aria-label": "Rename " + c.title, onclick: e => { e.stopPropagation(); renameDialog(c, false); } }, svg("edit")),
          el("button", { title: "Delete", "aria-label": "Delete " + c.title, onclick: async (e) => {
            e.stopPropagation();const button=e.currentTarget;if(button.dataset.running==="true")return;
            const row=button.closest(".item");if(row.nextElementSibling?.classList.contains("history-action-error"))row.nextElementSibling.remove();
            button.dataset.running="true";button.setAttribute("aria-busy","true");const wasOpen=S.chat===c.id;
            try{await api("/api/delete",{chat:c.id});if(wasOpen)newChat();await loadList();toast("Chat deleted.","Undo",async()=>{await api("/api/restore",{chat:c.id});await loadList();if(wasOpen)await openChat(c.id)})}
            catch(error){row.after(el("div",{class:"history-action-error",role:"status",text:"Could not delete chat: "+error.message+". Try Delete again."}))}
            finally{button.dataset.running="false";button.removeAttribute("aria-busy")}
          } }, svg("trash"))))); });
    } else {
      const rows = await api("/api/topics"); if (seq !== loadList.seq) return;delete list.dataset.chatsSignature;const signature=JSON.stringify([tab,rows]);if(list.dataset.topicsSignature===signature&&list.querySelectorAll(".item").length===rows.length){const items=list.querySelectorAll(".item");rows.forEach((t,i)=>{items[i].classList.toggle("on",t.id===S.topic);items[i].setAttribute("aria-current",String(t.id===S.topic))});return}list.dataset.topicsSignature=signature;list.replaceChildren();
      if (!rows.length) list.append(el("div", { class: "empty", text: "Conversations appear after your first question." }));
      rows.forEach((t) => list.append(el("div", { class: "item" + (t.id === S.topic ? " on" : ""), role:"button",tabindex:"0","aria-current":t.id===S.topic?"true":"false","aria-label":"Open conversation: "+t.title,onkeydown:e=>activateHistory(e,()=>openTopic(t.id)),onclick: () => openTopic(t.id) },
        el("span", { class: "t" }, t.title, el("span", { class: "sub", text: (t.summary ? t.summary.slice(0, 70) : t.turns + " question" + (t.turns === 1 ? "" : "s")) })),
        el("span", { class: "acts" }, el("button", { title: "Rename", "aria-label": "Rename " + t.title, onclick: e => { e.stopPropagation(); renameDialog(t, true); } }, svg("edit"))))));
    }
  } catch (e) { if(seq!==loadList.seq)return;clearTimeout(historySkeletonTimer);clearTimeout(historyShimmerTimer);state.replaceChildren(el("span",{text:"History could not load. " + e.message}),el("button",{type:"button",class:"history-retry",text:"Try again",onclick:e=>{e.stopPropagation();loadList()}})); }
  finally {if(seq===loadList.seq){clearTimeout(historySkeletonTimer);clearTimeout(historyShimmerTimer);list.removeAttribute("aria-busy");if(state.textContent==="Loading history...")state.remove()}}
}

function renameDialog(row, topic = false) {
  const title = topic ? "Rename conversation" : "Rename chat";
  const back = el("div", {class:"modal-back"}), input = el("input", {id:"renameTitle",value:row.title,maxlength:"140",required:"",type:"text",autocomplete:"off"});
  const status = el("p", {role:"status","aria-live":"polite",class:"rename-error"});
  const cancel = el("button", {type:"button",class:"btn-out",text:"Cancel"});
  const save = el("button", {type:"submit",class:"btn-out",text:"Save name"});
  const form = el("form", {class:"modal rename-dialog",role:"dialog","aria-label":title}, el("h2",{text:title}),el("label",{for:"renameTitle",text:"Name"}),input,status,el("div",{class:"modal-act"},cancel,save));
  let pending=false;
  const close=()=>{if(!pending)back.remove()};back.ccDismiss=close;cancel.onclick=close;
  form.onsubmit=async e=>{e.preventDefault();if(pending)return;const name=input.value.trim();if(!name){status.textContent="Enter a name.";input.focus();return}pending=true;save.disabled=cancel.disabled=true;status.textContent="Saving name...";
    try{await api(topic?"/api/rename-topic":"/api/rename",topic?{topic:row.id,title:name}:{chat:row.id,title:name});if((topic&&S.view==="topic"&&S.topic===row.id)||(!topic&&S.chat===row.id)){ $("#chatTitle").textContent=name;document.title=name+" - "+S.cfg.app.title;}await loadList();back.remove();toast("Name saved.")}
    catch(error){status.textContent="Could not save name: "+error.message+". Try again.";input.focus()}
    finally{pending=false;save.disabled=cancel.disabled=false}
  };back.append(form);mountModal(back);input.focus();input.select();
}

async function openChat(id) {
  if (!(await confirmTemporaryExit())) return;
  $("#jump").dataset.reply = "";
  S.view = "chat";
  setTemp(false);
  S.chat = id; S.newTopic = false;
  S.turns = await api("/api/turns?chat=" + id);
  try { S.ratings = await api("/api/ratings?chat=" + id); } catch (e) { S.ratings = {}; }
  S.topic = S.turns.length ? S.turns[S.turns.length - 1].topic : null;
  $("#chatTitle").textContent = (await api("/api/chats")).find((c) => c.id === id)?.title || "Chat";
  document.title = $("#chatTitle").textContent + " - " + S.cfg.app.title;
  $("#app").classList.remove("menu-open", "src"); drawThread(); loadList(); $("#q").focus();
}
async function openTopic(id) {
  if (!(await confirmTemporaryExit())) return;
  $("#jump").dataset.reply = "";
  S.view = "topic";
  setTemp(false);
  S.topic = id; S.newTopic = false;
  S.turns = await api("/api/topic-turns?topic=" + id);
  S.chat = S.turns.length ? S.turns[S.turns.length - 1].chat : null;
  $("#chatTitle").textContent = "Conversation"; $("#app").classList.remove("menu-open"); drawThread(); loadList(); $("#q").focus();
}
async function newChat() { if (!(await confirmTemporaryExit())) return; S.view = "chat"; setTemp(false); loadSuggestions(); S.chat = null; S.topic = null; S.newTopic = false; S.turns = []; $("#chatTitle").textContent = "New chat"; $("#app").classList.remove("src", "menu-open"); drawThread(); loadList(); $("#q").focus(); }

let aborter = null;
async function stream(body, onEvent) {
  aborter = new AbortController();
  const h = { "Content-Type": "application/json" };
  if (S.token) h.Authorization = "Bearer " + S.token;
  const r = await fetch("/api/ask-stream", { method: "POST", headers: h, body: JSON.stringify(body), signal: aborter.signal });
  if (!r.ok) { const d = await r.json().catch(() => ({})); throw new Error(d.error || ("The app returned an error (HTTP " + r.status + ")")); }
  const reader = r.body.getReader(), dec = new TextDecoder(); let buf = "";
  for (;;) {
    const { value, done } = await reader.read(); if (done) break;
    buf += dec.decode(value, { stream: true });
    let i; while ((i = buf.indexOf("\n")) >= 0) { const line = buf.slice(0, i).trim(); buf = buf.slice(i + 1); if (line) { let ev; try { ev = JSON.parse(line); } catch (e) { continue; } onEvent(ev); } }
  }
}
async function send() {
  if (PREVIEW) {
    const inp = $("#q"), text = inp.value.trim(); if (!text || S.busy) return;
    inp.value = ""; autosize(); rdy();
    ($("#thread .wrap") || $("#thread")).querySelector(".hero")?.remove();
    S.turns.push({ id: "p" + (S.turns.length + 1), chat: "p", question: text, answer: "This is a sample answer with a source citation [1].\n\nAdjust the appearance on the left to see it here. This preview does not contact your model or sources.", evidence: [{ n: 1, title: "Sample source for visual preview", text: "Preview sample only, not a retrieved document." }], ledger: [], seconds: 0 });
    drawThread();
    const t = $("#thread"); if (t) t.scrollTop = t.scrollHeight;
    return;
  }
  const q = $("#q").value.trim(); if (!q || S.busy) return;
  const status = $("#pipelineStatus"); status.hidden = true; status.dataset.state="working"; status.textContent = "Preparing your answer";
  S.busy = true; clearTimeout(simTimer); $("#similar").replaceChildren(); sendIcon("stop", "Stop"); $("#q").value = ""; autosize(); S.lastQ = q;
  const w = $("#thread .wrap") || $("#thread");
  w.querySelector(".hero")?.remove();
  const live = el("div", { class: "a", id: "live" });
  const thinkSpin = el("span", { class: "cc-spin", "aria-hidden": "true" });
  thinkSpin.innerHTML = '<svg viewBox="0 0 88 88"><circle class="cc-spin-track" cx="44" cy="44" r="38"/><circle class="cc-spin-head" cx="44" cy="44" r="38"/></svg>';
  const skel = el("div", { class: "answer-sk", "aria-hidden": "true" }, el("span"), el("span"), el("span"));
  live.append(skel);
  w.querySelector(".recent-questions")?.remove();
  w.append(el("div", { class: "row u user-arrive" }, el("div", { class: "bubble ub", text: q })), el("div", { class: "think", id: "think" }, thinkSpin, el("span", { class: "tt", id: "thinkTxt", text: "Preparing your answer" })), live);
  const th = $("#thread"); $("#jump").dataset.reply = ""; th.scrollTop = th.scrollHeight; syncLatest();
  let text = "", result = null, err = null;
  try {
    await stream({ scope: S.scope, chat: S.temp ? null : S.chat, question: q, style: $("#style").value, topic: S.topic, new_topic: S.newTopic, sources: S.sources.size ? [...S.sources] : null, temporary: S.temp, history: S.temp ? S.turns.slice(-200).map((t) => ({ question: t.question, answer: t.answer })) : undefined, use_profile: S.useProfile && !S.temp }, (ev) => {
      if (ev.type === "progress") { status.textContent = ev.data.label; const tt = $("#thinkTxt"); if (tt) tt.textContent = ev.data.label; }
      else if (ev.type === "token") {
        const thinking = $("#think");
        if (thinking) {
          if (motionAllowed() && thinking.animate) {
            thinking.removeAttribute("id"); thinking.style.overflow = "hidden";
            const fade = thinking.animate([{opacity:1,height:thinking.getBoundingClientRect().height+"px",padding:"4px 0"},{opacity:0,height:"0px",padding:"0px"}],{duration:120,easing:"ease-out"}); fade.onfinish = () => thinking.remove();
            live.classList.add("answer-arrive");
          } else thinking.remove();
        }
        text += ev.data; const follow = th.scrollHeight - th.scrollTop - th.clientHeight < 100; const rendered=renderAnswer(text, []); [...rendered.children].forEach(n=>n.classList.add("tk")); live.replaceChildren(...rendered.childNodes); if (follow) th.scrollTop = th.scrollHeight; syncLatest(); }
      else if (ev.type === "done") result = ev.data;
      else if (ev.type === "error") err = ev.data;
    });
  } catch (e) { err = e.name === "AbortError" ? "Stopped" : (e instanceof TypeError ? "Could not reach the app. Is it still running?" : e.message); }
  if (!result && !err) err = text ? "The answer was cut short" : "No answer came back";
  if (result) {
    if (!S.temp) { S.chat = result.chat; S.topic = result.topic; S.newTopic = false; }
    S.turns.push(result);
    if (S.turns.length === 1 && !S.temp) $("#chatTitle").textContent = chatTitleFrom(q);
  } else {
    toast((err || "Something went wrong").replace(/[.?!]+$/, "") + ".", "Retry", async () => { if(S.busy)throw Error("Wait for the current answer or stop it first."); if($("#q").value.trim() && $("#q").value.trim()!==q)throw Error("Your new draft is still here. Send or clear it before retrying the earlier question."); $("#q").value=q;await send(); });
  }
  status.dataset.state=result?"done":"error"; status.textContent = result ? "Reply ready" : ""; status.hidden = !result; setTimeout(() => { if (!S.busy) status.hidden = true; }, 2500);
  const readingEarlier = th.scrollHeight - th.scrollTop - th.clientHeight > 100;
  if (result && readingEarlier) $("#jump").dataset.reply = "ready";
  S.busy = false; applyIcons(); sendIcon("send", "Send"); drawThread(); loadList(); $("#q").focus({preventScroll:true});
  if (!result) {
    // keep what the user typed, and any text that did arrive, instead of losing both
    if (text && err !== "Stopped") { const w2 = $("#thread .wrap") || $("#thread"); w2.querySelector(".hero")?.remove(); w2.append(el("div", { class: "row u" }, el("div", { class: "bubble ub", text: q })), renderAnswer(text + "\n\n(Cut short. Use Retry to ask again.)", [])); }
    else if (!$("#q").value) { $("#q").value = q; autosize(); }
  }
  syncLatest(); rdy();
}
// Overlay lifecycle shared by source, context and account dialogs.
function mountModal(back, dismiss = true) {
  const previous = document.activeElement, box = back.querySelector('[role="dialog"]');
  box.setAttribute('aria-modal', 'true'); box.tabIndex = -1;
  const saved = new Map();
  const shield = () => { for (const n of document.body.children) if (n !== back && !saved.has(n)) { saved.set(n, n.inert); n.inert = true; } };
  const items = () => [...box.querySelectorAll('button,input,textarea,select,a[href],[tabindex="0"]')].filter(n => !n.disabled && n.getClientRects().length && !n.closest('[hidden]'));
  const key = e => {
    if (e.key === 'Escape') { e.preventDefault(); e.stopImmediatePropagation(); if (dismiss) {if(back.ccDismiss)back.ccDismiss();else back.remove();} }
    if (e.key === 'Tab') { const list = items(), first = list[0] || box, last = list.at(-1) || box;
      if (!box.contains(document.activeElement) || (e.shiftKey && document.activeElement === first) || (!e.shiftKey && document.activeElement === last)) { e.preventDefault(); (e.shiftKey ? last : first).focus(); }
    }
  };
  const focus = e => { if (!box.contains(e.target)) (items()[0] || box).focus(); };
  const observer = new MutationObserver(() => { if (!back.isConnected) { observer.disconnect(); document.removeEventListener('keydown', key, true); document.removeEventListener('focusin', focus); for (const [n, value] of saved) n.inert = value; if (previous?.isConnected) previous.focus(); } else shield(); });
  document.body.append(back); shield(); observer.observe(document.body, {childList:true});
  document.addEventListener('keydown', key, true); document.addEventListener('focusin', focus); (items()[0] || box).focus();
}
async function uploadDialog() {
 const modal=el('div',{class:'modal-back'}),box=el('div',{class:'modal source-add-modal',role:'dialog','aria-label':'Add sources'}),files=el('input',{id:'sourceFiles',type:'file',multiple:'','aria-label':'Choose source files'}),url=el('input',{id:'sourceUrl',type:'url',placeholder:'https://example.com/article','aria-label':'Web address',inputmode:'url'}),fileStatus=el('div',{class:'source-entry-status',role:'status','aria-live':'polite'}),urlStatus=el('p',{class:'source-entry-status',role:'status','aria-live':'polite'});let pending=false;
 const closeFlow=async()=>{if(pending){urlStatus.textContent='Please wait for the current source to finish adding.';return}if(url.value.trim()&&!(await CCDialog.confirm('You typed a web address but have not added it yet. To add it, choose \"Add link\". Close and discard the address? Sources already added are kept.',{title:'Discard address?',okText:'Discard'})))return;modal.remove()};modal.ccDismiss=closeFlow;
 const close=el('button',{class:'btn-out',text:'Done',onclick:closeFlow}),addLink=el('button',{class:'btn-out',text:'Add link'});
 const setBusy=on=>{pending=on;files.disabled=on;url.disabled=on;addLink.disabled=on;close.disabled=on;box.setAttribute('aria-busy',String(on))};
 const upload=async()=>{if(pending)return;const selected=[...files.files];if(!selected.length)return;fileStatus.replaceChildren();setBusy(true);
  const tasks=selected.map(f=>{const row=el('div',{class:'source-upload-row','data-state':'queued'}),name=el('b',{text:f.name}),state=el('span',{class:'source-upload-state',text:'Waiting to add'});row.append(name,state);fileStatus.append(row);return {f,row,state}});
  for(const {f,row,state} of tasks){try{if(f.size>8e6)throw Error('File is over 8 MB');row.dataset.state='reading';state.textContent='Reading file';const bytes=new Uint8Array(await f.arrayBuffer());let bin='';for(let i=0;i<bytes.length;i+=8192)bin+=String.fromCharCode.apply(null,bytes.subarray(i,i+8192));row.dataset.state='saving';state.textContent='Adding source. Waiting for this server to finish.';const result=await api('/api/upload-file',{name:f.name,data:btoa(bin)});state.textContent='Added '+result.name+'. '+result.chars+' text characters.';row.dataset.state='added'}catch(e){state.textContent='Could not add: '+e.message;row.dataset.state='error'}}
  files.value='';setBusy(false);if(box.isConnected&&(document.activeElement===document.body||document.activeElement===box))files.focus();
 };
 files.addEventListener('change',upload);addLink.onclick=async()=>{if(pending)return;const text=url.value.trim();let parsed;try{parsed=new URL(/^[a-zA-Z][a-zA-Z0-9+.-]*:\/\//.test(text)?text:'https://'+text)}catch{urlStatus.textContent='Enter a full web address, such as https://example.com/article.';url.setAttribute('aria-invalid','true');url.focus();return}if(!['https:','http:'].includes(parsed.protocol)){urlStatus.textContent='Use an HTTP or HTTPS web address.';url.setAttribute('aria-invalid','true');url.focus();return}url.setAttribute('aria-invalid','false');setBusy(true);urlStatus.textContent='Adding link...';try{const r=await api('/api/load-url',{url:parsed.href});urlStatus.textContent='Added '+r.name+'. Ready to use in saved chats.';url.value=''}catch(e){urlStatus.textContent='Could not add this link: '+e.message+'. Check the address and try again.';url.setAttribute('aria-invalid','true')}finally{setBusy(false);if(box.isConnected&&(document.activeElement===document.body||document.activeElement===box))addLink.focus()}};
 const fileGroup=el('section',{class:'source-entry-group'},el('h3',{text:'Upload files'}),el('p',{class:'mut',text:'PDF, Word, text and spreadsheets. Up to 8 MB per file.'}),el('label',{for:'sourceFiles',text:'Choose source files'}),files,fileStatus,el('p',{class:'mut',text:'Images use text recognition, not visual analysis.'}));
 const linkGroup=el('section',{class:'source-entry-group'},el('h3',{text:'Add a web page'}),el('label',{for:'sourceUrl',text:'Web address'}),url,addLink,urlStatus);
 const content=el('div',{class:'source-add-content'},el('p',{class:'mut',text:S.temp?'Added sources are saved, but not used in temporary chats.':'Each source is saved when added. Done closes this dialog.'}),fileGroup,linkGroup);box.append(el('h2',{text:'Add sources'}),content,el('div',{class:'modal-act'},close));modal.append(box);mountModal(modal);files.focus();
}

function contextDialog(t) {
  const m = el("div", { class: "modal-back", onclick: (e) => e.target === m && m.remove() }, el("div", { class: "modal", role: "dialog", "aria-label": "Answer context" },
    el("h2", { text: "How this answer was built" }),
    el("p", { text: "You asked: " + t.question }),
    el("p", { text: "Understood as: " + (t.standalone || t.question) }),
    el("p", { text: (t.evidence || []).length + " source" + ((t.evidence || []).length === 1 ? "" : "s") + " used" + (t.seconds !== undefined ? ", answered in " + (t.seconds < 1 ? "under 1s" : t.seconds + "s") : "") + "." }),
    el("div", { class: "modal-act" }, el("button", { class: "btn-out", onclick: () => m.remove() }, "Close"))));
  mountModal(m);
}
async function regen(turn, style) {
  try { const r = await api("/api/regenerate", { turn, style }); S.turns.push(r); drawThread(); } catch (e) { toast(e.message); }
}
const autosize = () => { const q = $("#q"); q.style.height = "auto"; q.style.height = Math.min(q.scrollHeight, 160) + "px"; };

function updateModelBadge() {
  const providerNames = {mock:"Demo",openai:"OpenAI",claude:"Claude",gemini:"Gemini",ollama:"Ollama",openai_compatible:"Custom provider",openrouter:"OpenRouter",deepseek:"DeepSeek",groq:"Groq",mistral:"Mistral",minimax:"MiniMax",mimo:"Xiaomi MiMo"};
  const badge=$("#modelBadge"), demo=S.cfg.provider.type === "mock";
  const noKey = !demo && S.cfg.provider.key_present === false;
  badge.textContent = demo ? "Demo · offline" : (providerNames[S.cfg.provider.type] || S.cfg.provider.type) + (S.cfg.provider.model ? " · " + S.cfg.provider.model : "") + (noKey ? " · no key" : "");
  badge.title = demo ? "Offline Demo: built-in answers from your documents. No AI model or paid calls. Choose a provider in Configuration to use AI." : noKey ? "Provider configured but no API key saved yet - the model cannot answer until a key is added in Configuration." : "Configured AI provider and model";
  badge.classList.toggle("badge-warn", noKey);
  let bar = $("#keyBar");
  if (noKey && !bar) {
    bar = el("div", { id: "keyBar", class: "key-bar", role: "note" },
      el("span", { text: "This app has no API key yet, so answers come from source previews, not the AI model. " }),
      el("a", { href: (window.CC_APP_BASE || "") + "/settings.html#sec-model", text: "Add a key in Configuration" }));
    const main = document.querySelector("main") || document.body;
    main.prepend(bar);
  } else if (!noKey && bar) bar.remove();
}
async function refreshModelBadge() { try { const cfg = await api("/api/config"); S.cfg.provider = cfg.provider; updateModelBadge(); } catch (_) {} }
window.addEventListener("focus", refreshModelBadge);
document.addEventListener("visibilitychange", () => { if (!document.hidden) refreshModelBadge(); });
window.addEventListener("storage", (e) => { if (e.key === "cc_config_changed") refreshModelBadge(); });

async function init() {
  S.cfg = await api("/api/config");
  if (S.cfg.auth === "accounts" && !PREVIEW) await accountGate();
  { const h = S.cfg.app.accent.replace("#", ""), v = [0, 2, 4].map((i) => parseInt(h.substr(i, 2), 16) / 255).map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4));
    const L = 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; document.documentElement.style.setProperty("--on-accent", L > 0.5 ? "#000" : "#fff"); }
  const a = S.cfg.app; document.title = a.title;
  $("#brand").textContent = a.title; $("#sideTitle").textContent = "Conversations"; $("#noteName").textContent = a.title; $("#noteText").textContent = a.footer; $("#noteName").closest(".note").hidden = PREVIEW; $("#tempPill").addEventListener("click", toggleTemp); $("#themeBtn").addEventListener("click", () => { const dark = document.documentElement.dataset.theme === "dark"; localStorage.setItem("cc_mode", dark ? "light" : "dark"); CCTheme.apply(CCTheme.value); });
  updateModelBadge();
  $("#themeBtn").title = "Switch between light and dark theme";
  const modeHelp={quick:"2 to 4 sentences.",standard:"Short paragraphs.",deep:"More detail, with sections and caveats."};
  S.cfg.styles.forEach((s) => $("#style").append(el("option", {title:(modeHelp[s] || "Answer style: "+s)+" Changes answer length, not model or source quality.", "data-description":modeHelp[s] || "", value: s === "standard" ? s : s, ...(s === "standard" ? { selected: "" } : {}) }, s[0].toUpperCase() + s.slice(1))));
  if (S.cfg.sources.length > 1) {
    const f = el("div", { class: "pills" });
    S.cfg.sources.forEach((s) => f.append(el("button", { class: "pill", onclick: (e) => { S.sources.has(s.id) ? S.sources.delete(s.id) : S.sources.add(s.id); e.target.style.opacity = S.sources.has(s.id) || !S.sources.size ? 1 : .45; [...f.children].forEach((c, i) => c.style.opacity = !S.sources.size || S.sources.has(S.cfg.sources[i].id) ? 1 : .45); } }, s.label)));
    $(".composer").prepend(f);
  }
  $("#scopeBtn").onclick=scopeDialog;
  const toolsT = $("#toolsToggle"), toolsM = $("#toolsMenu");
  if (toolsT && toolsM) {
    const setTools = (open) => { toolsM.hidden = !open; toolsT.setAttribute("aria-expanded", String(open)); if (open) toolsM.querySelector("button").focus(); };
    toolsT.addEventListener("click", (e) => { e.stopPropagation(); setTools(toolsM.hidden); });
    toolsM.addEventListener("click", (e) => { e.stopPropagation(); if (e.target.id === "toolsScope" || e.target.id === "toolsActions") { setTools(false); $(e.target.id === "toolsScope" ? "#scopeBtn" : "#actionsBtn").click(); } });
    toolsM.addEventListener("keydown", (e) => { const items = [...toolsM.querySelectorAll("button")]; const i = items.indexOf(document.activeElement); if (e.key === "Escape") { setTools(false); toolsT.focus(); } if (e.key === "ArrowDown") { e.preventDefault(); items[(i + 1) % items.length].focus(); } if (e.key === "ArrowUp") { e.preventDefault(); items[(i - 1 + items.length) % items.length].focus(); } });
    document.addEventListener("click", () => { if (!toolsM.hidden) setTools(false); });
  }
  $("#q").addEventListener("keydown",e=>{if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){e.preventDefault();send()}});
  $("#actionsBtn").onclick=async()=>{
   const trigger=$("#actionsBtn");if(trigger.dataset.running==="true")return;trigger.dataset.running="true";trigger.setAttribute("aria-busy","true");const original=trigger.textContent,originalMinWidth=trigger.style.minWidth;trigger.style.minWidth=trigger.getBoundingClientRect().width+"px";trigger.textContent="Wait...";$("#actionsError").hidden=true;
   try {
    const catalog=await api('/api/actions');const dialog=el('dialog',{class:'reading-dialog action-dialog','aria-label':'Review an action'});
    dialog.append(el('header',{class:'reading-head'},el('h2',{text:'Review an action'})));
    const content=el('div',{class:'action-body'});dialog.append(content);
    for(const tool of catalog) content.append(el('button',{class:'reading-done',onclick:()=>{
     const inputs={},labels={title:'Note title',text:'Note text'};
     const form=()=>{content.replaceChildren(el('h3',{text:tool.label}));
      for(const [name,spec] of Object.entries(tool.fields)){const id='action-field-'+name,input=el(name==='text'?'textarea':'input',{id,maxlength:spec.maxLength,'aria-label':labels[name]||name});input.value=inputs[name]?.value||'';inputs[name]=input;content.append(el('label',{for:id,text:labels[name]||name}),input)}
      const error=el('p',{class:'action-error',role:'status'});content.append(error);
      const preview=el('button',{class:'reading-done',text:'Preview action',onclick:async()=>{if(preview.disabled)return;preview.disabled=true;preview.textContent='Preparing...';error.textContent='';
       try{const args=Object.fromEntries(Object.entries(inputs).map(([k,v])=>[k,v.value])),review=await api('/api/actions/prepare',{tool:tool.id,args});
        const focusReview=dialog.open&&(document.activeElement===document.body||document.activeElement===dialog||content.contains(document.activeElement));content.replaceChildren(el('h3',{text:review.label}),el('p',{text:review.mode==='write'?'This will save a note in this app.':'This will show your notes in this app.'}));
        for(const [name,value] of Object.entries(review.args))content.append(el('section',{class:'action-value'},el('h4',{text:labels[name]||name}),el('p',{text:value})));
        content.append(el('p',{text:'Saved under this app identity. Shared-login modes share notes. Review expires in 5 minutes.'}));
        const failure=el('p',{class:'action-error',role:'status'}),back=el('button',{class:'chip',text:'Back to edit',onclick:form});
        const confirm=el('button',{class:'reading-done',text:'Confirm action',onclick:async()=>{if(confirm.disabled)return;confirm.disabled=true;back.disabled=true;confirm.textContent='Working...';
         try{const result=await api('/api/actions/execute',{ticket:review.ticket}),focusResult=dialog.open&&(document.activeElement===document.body||document.activeElement===dialog||content.contains(document.activeElement));content.replaceChildren(el('h3',{text:result.saved?'Note saved':'Your notes'}));
          if(result.saved)content.append(el('p',{text:'Your note was saved in this app.'}));
          else if(Array.isArray(result.notes)){if(!result.notes.length)content.append(el('p',{class:'action-empty',role:'status',text:'No notes saved yet.'}));for(const note of result.notes)content.append(el('section',{class:'action-value'},el('h4',{text:note.title}),el('p',{text:note.text})))}
          else content.append(el('p',{text:'Action complete.'}));const heading=content.querySelector('h3');heading.tabIndex=-1;if(focusResult)heading.focus();
         }catch(err){failure.textContent=err.message+' Return to the form to review a fresh action. If the connection was interrupted, check your notes before saving again.';confirm.textContent='Action not confirmed';back.disabled=false;if(dialog.open&&(document.activeElement===document.body||document.activeElement===dialog||document.activeElement===confirm))back.focus()}
        }});content.append(failure,back,confirm);if(focusReview)back.focus();
       }catch(err){error.textContent=err.message;preview.disabled=false;preview.textContent='Preview action';if(dialog.open&&(document.activeElement===document.body||document.activeElement===dialog||document.activeElement===preview))preview.focus()}
      }});content.append(preview);(Object.values(inputs)[0]||preview).focus();
     };form();
    }},tool.label));
    if(!catalog.length)content.append(el('p',{class:'action-empty',role:'status',text:'No actions enabled.'}));
    dialog.append(el('footer',{},el('button',{class:'chip',onclick:()=>dialog.close()},'Close')));dialog.addEventListener('close',()=>{dialog.remove();$('#actionsBtn').focus()});document.body.append(dialog);dialog.showModal();
   }catch(err){const error=$('#actionsError');error.textContent='Could not load actions: '+err.message+'. Try Actions again.';error.hidden=false}finally{trigger.dataset.running='false';trigger.removeAttribute('aria-busy');trigger.textContent=original;trigger.style.minWidth=originalMinWidth}
  };
  $("#hint").textContent = "Answers cite their sources. Check important facts.";
  $("#q").addEventListener("input", autosize);
  $("#q").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } });
  $("#exportChat").addEventListener("click", () => S.chat && S.turns.length ? download("/api/export?chat=" + S.chat, "chat.md") : toast("Nothing to export yet"));
  $("#q").addEventListener("input", rdy); rdy(); $("#send").addEventListener("click", () => (S.busy ? aborter && aborter.abort() : send())); $("#newChat").addEventListener("click", newChat);
  const sidebarOverlay = () => matchMedia("(max-width:860px)").matches || document.documentElement.dataset.sidebar === "hidden";
  const syncSidebar = () => {
    const open = sidebarOverlay() ? $("#app").classList.contains("menu-open") : !$("#app").classList.contains("side-collapsed");
    const menu = $("#menu"), docked = !sidebarOverlay();
    if(menu.dataset.docked !== String(docked)){menu.dataset.docked=String(docked);menu.replaceChildren(svg(docked?"collapse":"menu"));}
    $("#menu").setAttribute("aria-expanded", String(open));
    $("#menu").setAttribute("aria-label", open ? "Close chats" : "Open chats");
    $("#menu").title = open ? "Close chats" : "Open chats";
    $("#side").inert = !open;
  };
  $("#menu").setAttribute("aria-controls", "side");
  const navT = $("#navToggle");
  if (navT) {
    const setNavOpen = (open) => { document.body.classList.toggle("nav-open", open); navT.setAttribute("aria-expanded", String(open)); const main = $("#app"); if (main) main.inert = open; };
    navT.addEventListener("click", (e) => { e.stopPropagation(); setNavOpen(!document.body.classList.contains("nav-open")); });
    document.addEventListener("click", (e) => { if (document.body.classList.contains("nav-open") && !e.target.closest(".common-nav") && !e.target.closest("#navToggle")) setNavOpen(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && document.body.classList.contains("nav-open")) { setNavOpen(false); navT.focus(); } });
  }
  $("#menu").addEventListener("click", () => { $("#app").classList.toggle(sidebarOverlay() ? "menu-open" : "side-collapsed"); syncSidebar(); });
  $("#sideClose").addEventListener("click", () => { $("#app").classList.remove("menu-open"); if (!sidebarOverlay()) $("#app").classList.add("side-collapsed"); $("#menu").focus(); syncSidebar(); });
  new MutationObserver(syncSidebar).observe($("#app"), {attributes:true, attributeFilter:["class"]});
  new MutationObserver(syncSidebar).observe(document.documentElement, {attributes:true, attributeFilter:["data-sidebar"]});
  matchMedia("(max-width:860px)").addEventListener("change", syncSidebar);
  syncSidebar();
  $("#search").addEventListener("input", () => S.tab === "chats" && loadList());
  const historyTabs = [...document.querySelectorAll(".tabs [role=tab]")];
  historyTabs.forEach((b, index) => { b.addEventListener("click", () => { historyTabs.forEach((x) => { x.classList.toggle("on", x === b); x.setAttribute("aria-selected", String(x === b)); x.tabIndex = x === b ? 0 : -1; }); $("#list").setAttribute("aria-labelledby", b.id); S.tab = b.dataset.tab; loadList(); }); b.addEventListener("keydown", e => { let next; if(e.key === "ArrowRight") next=(index+1)%historyTabs.length; else if(e.key === "ArrowLeft") next=(index+historyTabs.length-1)%historyTabs.length; else if(e.key === "Home") next=0; else if(e.key === "End") next=historyTabs.length-1; else return; e.preventDefault(); historyTabs[next].focus(); historyTabs[next].click(); }); });
  document.addEventListener("keydown", (e) => {
    if ($("#app").classList.contains("src")) {
      if (e.key === "Escape") { e.preventDefault(); closeSources(); return; }
      if (e.key === "Tab" && $("#sources").getAttribute("aria-modal") === "true") {
        const controls = [...$("#sources").querySelectorAll("button,a[href]")].filter(n=>n.getClientRects().length), first=controls[0], last=controls.at(-1);
        if((e.shiftKey&&document.activeElement===first)||(!e.shiftKey&&document.activeElement===last)){e.preventDefault();(e.shiftKey?last:first)?.focus()}
      }
    } else if (e.key === "Escape") $("#app").classList.remove("menu-open");
  });
  matchMedia("(max-width:860px)").addEventListener("change",()=>sourceModal($("#app").classList.contains("src")));
  const th = $("#thread"), jump = $("#jump");
  th.addEventListener("scroll", syncLatest);
  new ResizeObserver(syncLatest).observe($(".composer"));
  jump.addEventListener("click", () => th.scrollTo({ top: th.scrollHeight, behavior: motionAllowed()?"smooth":"auto" }));
  $("#menu").replaceChildren(svg($("#menu").dataset.docked==="true"?"collapse":"menu")); $("#upload").replaceChildren(svg("clip")); $("#exportChat").replaceChildren(svg("tray")); $("#newTopic").replaceChildren(svg("topic")); $("#newTopic").onclick = () => { S.newTopic = true; S.topic = null; toast("Next question starts a new conversation"); }; $("#send").replaceChildren(svg("send")); $("#jump").replaceChildren(svg("down"));
  $("#upload").addEventListener("click", uploadDialog);
  document.addEventListener("keydown", (e) => { if ((e.metaKey || e.ctrlKey) && e.key === "k") { e.preventDefault(); $("#search").focus(); } });
  $("#tempBtn").replaceChildren(svg("temp")); $("#profileBtn").replaceChildren(svg("user")); $("#prevQ").replaceChildren(svg("up")); $("#nextQ").replaceChildren(svg("down"));
  $("#tempBtn").addEventListener("click", toggleTemp); $("#profileBtn").addEventListener("click", profileDialog);
  $("#prevQ").addEventListener("click", () => jumpQ(-1)); $("#nextQ").addEventListener("click", () => jumpQ(1));
  setupMic(); setupSimilar(); setupResizer();
  document.addEventListener("keydown", (e) => { const t = e.target.tagName; if (["INPUT", "TEXTAREA", "SELECT"].includes(t) || e.metaKey || e.ctrlKey || e.altKey) return; if (e.key === "j") jumpQ(1); else if (e.key === "k") jumpQ(-1); });
  applyWording(); applyIcons();
  if (PREVIEW) { previewMode(); return; }
  drawThread(); loadList(); loadSuggestions(); tour();
}
init().then(()=>window.CCLoading?.ready()).catch((e) => { window.CCLoading?.ready();document.body.textContent = "Could not start: " + e.message; });

document.addEventListener("keydown", (e) => {
  const t = e.target.tagName;
  if (t === "INPUT" || t === "TEXTAREA" || t === "SELECT" || e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.key === "/") { e.preventDefault(); const s = document.getElementById("search"); if (s) s.focus(); }
  else if (e.key === "n") { e.preventDefault(); const b = document.getElementById("newChat"); if (b) b.click(); }
  else if (e.key === "?") { toast("Shortcuts: / search, n new chat, Enter send, Shift+Enter new line, Esc close"); }
});
document.addEventListener("click", (e) => {
  const app = document.getElementById("app");
  if (app && app.classList.contains("menu-open") && !e.target.closest(".side") && !e.target.closest(".toast") && !e.target.closest("#menu")) app.classList.remove("menu-open");
});

// ---- temporary chat, profile, mic, similar questions, question navigation, resizer, tour ----
async function confirmTemporaryExit() {
  if (!S.temp) return true;
  if (S.busy) { toast("Wait for the temporary reply or stop it before leaving."); return false; }
  return !S.turns.length || (await CCDialog.confirm("Leave this temporary conversation? Its questions and replies are not saved and will be cleared. Your unsent question stays in the composer.",{title:"Leave temporary conversation?",okText:"Leave",danger:true}));
}
function setTemp(on) {
  S.temp = on; document.body.classList.toggle("temp", on);
  const b = $("#tempBtn"); if (b) b.setAttribute("aria-pressed", String(on)); $("#tempPill").setAttribute("aria-pressed", String(on)); $("#tempPill").title = on ? "Leave temporary mode" : "Start a chat that is not saved"; $("#q").placeholder = on ? "Ask without saving this chat" : "Ask a question";
}
function toggleTemp() {
  if (S.temp) { newChat(); return; }
  S.chat = null; S.topic = null; S.turns = []; S.newTopic = false; S.scope = null; S.sources.clear(); scopeChip(); setTemp(true); $("#app").classList.remove("menu-open", "src");
  $("#chatTitle").textContent = "Temporary chat"; drawThread();
  const t = $("#thread .hero"); if (t) { t.querySelector("h1").textContent = "Temporary chat"; t.querySelector("p").textContent = "Nothing here is saved, and your profile and uploads are not used. Closing the chat clears it."; }
  $("#q").focus();
}
async function profileDialog() {
  let fields=[];try{const r=await api("/api/profile");fields=r.fields||(r.text?[{label:"Background",value:r.text}]:[])}catch(e){toast(e.message);return}
  const previous=document.activeElement,rows=el("div",{class:"profile-fields"}),on=el("input",{type:"checkbox",id:"useProfile","aria-label":"Use in saved chats"}),count=el("span",{text:"0 / 3,000 characters"});on.checked=S.useProfile;
  const updateCount=()=>{const n=[...rows.querySelectorAll("input,textarea")].reduce((n,e)=>n+e.value.length,0);count.textContent=n.toLocaleString()+" / 3,000 characters"};
  const add=(f={label:"",value:""})=>{if(rows.children.length>=20){toast("Use at most 20 fields");return}const id="profile-field-"+Math.random().toString(36).slice(2),label=el("input",{id,type:"text",placeholder:"e.g. Goals, interests, preferences",maxlength:60,"aria-label":"What should it know?",oninput:updateCount}),value=el("textarea",{id:id+"-value",rows:2,placeholder:"Tell it what matters to you…",maxlength:1000,"aria-label":"Details",oninput:updateCount});label.value=f.label;value.value=f.value;const row=el("div",{class:"profile-field"},el("div",{class:"profile-field-head"},el("label",{for:id,text:"What should it know?"}),el("button",{type:"button",class:"profile-remove",text:"Remove",onclick:()=>{row.remove();updateCount()}})),label,el("label",{for:id+"-value",text:"Details"}),value);rows.append(row);updateCount();return label};
  fields.forEach(add);if(!fields.length)add();const close=()=>{back.remove();previous?.focus()};const save=async()=>{try{const fields=[...rows.children].map(r=>({label:r.querySelector("input").value,value:r.querySelector("textarea").value}));await api("/api/profile",{fields});S.useProfile=on.checked&&fields.some(f=>f.value.trim());localStorage.setItem("cc_profile_on",S.useProfile?"1":"0");toast("Profile saved");close();drawThread()}catch(e){toast(e.message)}};
  const box=el("div",{class:"modal profile-design",role:"dialog","aria-modal":"true","aria-label":"My profile"},el("header",{},el("div",{},el("h2",{text:"My profile"})),el("button",{type:"button",class:"profile-close","aria-label":"Close profile",title:"Close profile",text:"×",onclick:close})),el("p",{class:"profile-intro",text:"A little background for better replies. Not evidence. Never used in temporary chats. Up to 20 details."}),rows,el("button",{type:"button",class:"profile-add",text:"+ Add another detail",onclick:()=>add()?.focus()}),el("div",{class:"profile-use"},el("div",{},el("b",{text:"Use in saved chats"}),el("span",{text:"Stored on this server. You can change it anytime."})),on),el("footer",{},count,el("div",{},el("button",{type:"button",class:"profile-cancel",text:"Cancel",onclick:close}),el("button",{type:"button",class:"profile-save",text:"Save profile",onclick:save}))));
  const back=el("div",{class:"modal-back",onclick:e=>e.target===back&&close()},box);
  mountModal(back);rows.querySelector("input").focus();
}
function setupMic() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition; const m = $("#mic");
  if (!SR || !m) return;
  m.hidden = false; m.replaceChildren(svg("mic")); composerSwap();
  let rec = null;
  const reset = active => { if (rec !== active) return; rec = null; m.classList.remove("rec"); m.setAttribute("aria-label", "Dictate"); m.title = "Dictate a question"; m.setAttribute("aria-pressed", "false"); };
  m.title = "Dictate a question"; m.setAttribute("aria-pressed", "false");
  m.addEventListener("click", () => {
    if (rec) { const active = rec; active.stop(); reset(active); return; }
    const active = new SR(); rec = active; active.lang = (S.cfg.app.language || "en"); active.interimResults = true; active.continuous = false;
    const base = $("#q").value;
    active.onstart = () => { if (rec !== active) return; m.classList.add("rec"); m.setAttribute("aria-label", "Stop dictation"); m.title = "Listening. Click to stop dictation"; m.setAttribute("aria-pressed", "true"); };
    active.onresult = (e) => { if (rec !== active) return; let t = ""; for (const r of e.results) t += r[0].transcript; $("#q").value = (base ? base + " " : "") + t; autosize(); rdy(); };
    active.onerror = (e) => { if (rec !== active) return; reset(active); if (e.error === "aborted") return; const messages = {"not-allowed":"Microphone access was denied. Allow it in your browser settings, or type your question.","service-not-allowed":"Your browser blocked dictation. Check microphone and speech permissions, or type your question.","audio-capture":"No microphone was found. Connect one, or type your question.","no-speech":"No speech was heard. Try again, or type your question.","network":"Dictation could not connect. Check your connection, or type your question."}; toast(messages[e.error] || "Dictation could not start. Try again, or type your question."); };
    active.onend = () => { if (rec !== active) return; reset(active); $("#q").focus({preventScroll:true}); };
    try { active.start(); } catch (e) { reset(active); toast("Dictation could not start. Try again, or type your question."); }
  });
}
let simTimer = null;
function setupSimilar() {
  $("#q").addEventListener("input", () => {
    clearTimeout(simTimer);
    const q = $("#q").value.trim(), box = $("#similar");
    if (S.temp || q.split(/\s+/).length < 3) { box.replaceChildren(); return; }
    simTimer = setTimeout(async () => {
      try {
        const r = await api("/api/similar?q=" + encodeURIComponent(q));
        if (S.busy || $("#q").value.trim() !== q) return;
        if (!r.length) { box.replaceChildren(); return; }
        const history = el("details", {class:"similar-history"}, el("summary", {text:"Related saved questions (" + r.length + ")"}));
        history.append(el("p", {class:"mut",text:"From earlier chats. Open one to revisit it; your current question stays separate."}), ...r.map((x) => el("button", {class:"pill", title:"Open the saved chat", onclick:()=>{box.replaceChildren();openChat(x.chat);}},x.question)));
        box.replaceChildren(history);
      } catch (e) { /* ignore */ }
    }, 500);
  });
}
function jumpQ(dir) {
  const qs = [...document.querySelectorAll("#thread .row.u")]; if (!qs.length) return;
  const th = $("#thread"), top = th.getBoundingClientRect().top + 8;
  const idx = qs.findIndex((n) => n.getBoundingClientRect().top > top + 4);
  let target = dir > 0 ? qs[idx === -1 ? qs.length - 1 : idx] : qs[(idx === -1 ? qs.length : idx) - 2] || qs[0];
  if (dir < 0 && idx === -1) target = qs[Math.max(0, qs.length - 2)];
  target.scrollIntoView({ behavior: motionAllowed()?"smooth":"auto", block: "start" });
}
function setupResizer() {
  const r = $("#resizer"), app = $("#app"); if (!r) return;
  const saved = parseInt(localStorage.getItem("cc_side") || "0", 10); if (saved) document.documentElement.style.setProperty("--side-w", saved + "px");
  r.addEventListener("pointerdown", (e) => {
    e.preventDefault(); r.setPointerCapture(e.pointerId);
    const move = (ev) => { const w = Math.min(460, Math.max(200, document.documentElement.dataset.sidebar === "right" ? app.getBoundingClientRect().right - ev.clientX : ev.clientX - app.getBoundingClientRect().left)); document.documentElement.style.setProperty("--side-w", w + "px"); localStorage.setItem("cc_side", String(w)); };
    const up = () => { r.removeEventListener("pointermove", move); r.removeEventListener("pointerup", up); };
    r.addEventListener("pointermove", move); r.addEventListener("pointerup", up);
  });
  r.addEventListener("dblclick", () => { document.documentElement.style.setProperty("--side-w", (window.CCTheme?.value.sidebar_width || 250) + "px"); localStorage.removeItem("cc_side"); });
}
async function accountGate() {
  const post = (p, b) => api("/api/account/" + p, b);
  let me = await api("/api/account/me");
  while (!me.user) {
    me = await new Promise((resolve) => {
      let mode = "in";
      const back = el("div", { class: "modal-back" }), err = el("div", { id:"signin-error",class: "auth-err", role: "alert" });
      const email = el("input", { type: "email", placeholder: "Email", autocomplete: "email", "aria-label": "Email" });
      const name = el("input", { type: "text", placeholder: "Your name (optional)", autocomplete: "name", "aria-label": "Name" });
      const pw = el("input", { type: "password", placeholder: "Password (8+ characters)", autocomplete: "current-password", "aria-label": "Password" });
      const go = el("button", { class: "chip on" }, "Sign in"), sw = el("button", { class: "linkbtn", type: "button" });
      const invalid=(input,message)=>{input.setAttribute("aria-invalid","true");input.setAttribute("aria-describedby","signin-error");err.textContent=message;input.focus()};
      for(const input of [email,pw])input.addEventListener("input",()=>{const valid=input===email?input.value.trim()&&input.checkValidity():input.value&&(mode==='in'||input.value.length>=8);if(valid){input.removeAttribute("aria-invalid");input.removeAttribute("aria-describedby");if(![email,pw].some(n=>n.getAttribute("aria-invalid")==="true"))err.textContent=""}});
      const draw = () => {
        name.hidden = mode === "in"; go.textContent = mode === "in" ? "Sign in" : "Create account";
        sw.textContent = mode === "in" ? "New here? Create an account" : "Have an account? Sign in"; sw.hidden = mode === "in" && !me.signup;
        pw.autocomplete = mode === "in" ? "current-password" : "new-password"; err.textContent = "";for(const input of [email,pw]){input.removeAttribute("aria-invalid");input.removeAttribute("aria-describedby")}
      };
      const submit = async () => {
        if(go.disabled)return;if(!email.value.trim()||!pw.value){invalid(!email.value.trim()?email:pw,'Enter your email and password.');return}if(!email.checkValidity()){invalid(email,'Enter a valid email address.');return}if(mode==='up'&&pw.value.length<8){invalid(pw,'Use at least eight characters for your password.');return}go.disabled = true;sw.disabled=true;go.textContent=mode==='in'?'Signing in...':'Creating account...';
        try { resolve(await post(mode === "in" ? "login" : "signup", { email: email.value, name: name.value, password: pw.value }).then(() => post("me"))); back.remove(); }
        catch (e) { err.textContent = e.message; go.disabled = false;sw.disabled=false;go.textContent=mode==='in'?'Sign in':'Create account'; }
      };
      go.addEventListener("click", submit); pw.addEventListener("keydown", (e) => e.key === "Enter" && submit());
      sw.addEventListener("click", () => { mode = mode === "in" ? "up" : "in"; draw(); });
      back.append(el("form", { class: "modal auth", onsubmit: (e) => e.preventDefault(), role: "dialog", "aria-modal": "true", "aria-label": "Sign in" },
        el("h2", { text: S.cfg.app.title }), el("p", { class: "mut", text: "Sign in to keep your chats private to you." }), email, name, pw, err, el("div", { class: "modal-act" }, sw, go)));
      mountModal(back, false); draw(); email.focus();
    });
  }
  S.user = me.user;
  const tb = $(".toolbar"), menu = el("div", { class: "acct-menu", hidden: "" });
  const btn = el("button", { class: "acct-btn", "aria-haspopup": "true", "aria-label": "Account" }, el("span", { class: "acct-dot", text: (me.user.name || "?")[0].toUpperCase() }), el("span", { text: me.user.name }));
  const item = (t, f) => el("button", { class: "acct-item", onclick: () => { menu.hidden = true; f(); } }, t);
  menu.append(el("div", { class: "acct-mail mut", text: me.user.email }),
    item("Change password", () => {
      const o = el("input", { type: "password", placeholder: "Current password", "aria-label": "Current password", autocomplete: "current-password" }), n = el("input", { type: "password", placeholder: "New password (8+ characters)", "aria-label": "New password", autocomplete: "new-password" });
      const e = el("div", {id:"password-error",class: "auth-err", role: "alert" }), back = el("div", { class: "modal-back" });
      const invalid=(input,message)=>{input.setAttribute("aria-invalid","true");input.setAttribute("aria-describedby","password-error");e.textContent=message;input.focus()};
      for(const input of [o,n])input.addEventListener("input",()=>{if(input.value&&(input===o||input.value.length>=8)){input.removeAttribute("aria-invalid");input.removeAttribute("aria-describedby");if(![o,n].some(x=>x.getAttribute("aria-invalid")==="true"))e.textContent=""}});
      const save = el("button", { class: "chip on", onclick: async () => {if(save.disabled)return;if(!o.value||n.value.length<8){invalid(!o.value?o:n,!o.value?'Enter your current password.':'Use at least eight characters for the new password.');return}save.disabled=true;save.textContent='Saving...';try { await post("password", { old: o.value, new: n.value }); back.remove(); toast("Password changed. Other devices were signed out."); } catch (x) { e.textContent = x.message; }finally{save.disabled=false;save.textContent='Save'} } }, "Save");
      back.append(el("div", { class: "modal auth", role: "dialog", "aria-modal": "true", "aria-label": "Change password" }, el("h2", { text: "Change password" }), o, n, e, el("div", { class: "modal-act" }, el("button", { class: "chip", onclick: () => back.remove() }, "Cancel"), save)));
      mountModal(back); o.focus();
    }),
    item("Sign out", async () => { await post("logout", {}); location.reload(); }));
  btn.addEventListener("click", (e) => { e.stopPropagation(); menu.hidden = !menu.hidden; });
  document.addEventListener("click", () => (menu.hidden = true));
  $("#themeBtn").parentElement.insertBefore(el("div", { class: "acct" }, btn, menu), $("#themeBtn"));
}
function applyWording() {
  const a = S.cfg.app;
  { const b = $("#brand"); b.replaceChildren(el("img",{class:"tb-logo",src:"/icons/chatify.svg",alt:""}),document.createTextNode("Chatify"));b.title="Workspace: "+(TV("txt_title")||a.title); } document.title = TV("txt_title") || a.title;
  $("#noteName").textContent = TV("txt_title") || a.title; $("#noteText").textContent = TV("txt_footer") || a.footer; $("#noteName").closest(".note").hidden = PREVIEW;
  $("#q").placeholder = TV("txt_placeholder") || "Ask a question"; $("#hint").textContent = TV("txt_hint") || "Answers cite their sources. Check important facts.";
  const d = document.querySelector(".cmeta span:last-child"); if (d) d.textContent = TV("txt_disclaimer") || "Not a substitute for professional advice.";
  $("#sideTitle").textContent = TV("txt_sidebar") || "Chats";
}
function applyIcons() {
  for (const [id, key, name] of [["#send", "emoji_send", "send"], ["#upload", "emoji_attach", "clip"], ["#tempBtn", "emoji_temp", "temp"]]) {
    const b = $(id); if (!b) continue; const e = TV(key); if (id === "#send" && S.busy) continue; b.classList.remove("emo-bounce","emo-pulse","emo-wiggle");if(e&&["bounce","pulse","wiggle"].includes(TV(key+"_motion")))b.classList.add("emo-"+TV(key+"_motion"));b.replaceChildren(e ? CCEmoji.node(e,TV(key+"_animated"),"",["calm","none"].includes(TV("motion"))) : svg(name));
  }
}
function updatePreviewAvatars() {
  for(const kind of ["bot","you"]){
    const key=kind==="bot"?"emoji_bot":"emoji_you",emoji=TV(key);
    document.querySelectorAll(".row>.av."+kind).forEach(node=>{
      const signature=JSON.stringify([emoji,TV(key+"_animated"),TV("motion")]);
      if(node.dataset.iconValue===signature)return;node.dataset.iconValue=signature;
      node.classList.toggle("emo",!!emoji);
      node.replaceChildren(emoji?CCEmoji.node(emoji,TV(key+"_animated"),"",["calm","none"].includes(TV("motion"))):document.createTextNode(kind==="bot"?(TV("txt_title")||S.cfg.app.title||"AI").replace(/[^A-Za-z]/g,"").slice(0,2):"You"));
    });
  }
}
function pvBottom() { const t = $("#thread"); if (t) { t.style.scrollBehavior = "auto"; t.scrollTop = 0; } }
function previewMode() {
  let demoAnimation=null;window.ccStopPreviewMotion=()=>{if(demoAnimation){demoAnimation.cancel();demoAnimation=null}};window.ccPreviewMotion=(t)=>{window.ccStopPreviewMotion();const node=[...document.querySelectorAll('.row:not(.u)')].at(-1);if(!node)return;if(matchMedia('(prefers-reduced-motion:reduce)').matches||['calm','none'].includes(t.motion)||t.entrance==='none')return;const frames=t.entrance==='slide'?[{opacity:0,transform:'translateY(18px)'},{opacity:1,transform:'none'}]:t.entrance==='pop'?[{opacity:0,transform:'scale(.94)'},{opacity:1,transform:'none'}]:[{opacity:0},{opacity:1}];demoAnimation=node.animate(frames,{duration:(t.motion==='subtle'?180:420)*100/t.speed,easing:'ease-out'})};
  document.querySelectorAll("input,textarea,select,button").forEach(control => { control.disabled=true; control.tabIndex=-1; });
  for (const id of ["q", "send", "menu", "sideClose", "jump"]) { const n = document.getElementById(id); if (n) { n.disabled = false; n.tabIndex = 0; } }
  $("#q").placeholder="Ask a sample question";
  $("#q").value="";
  document.documentElement.classList.add("preview");
  S.turns = [{ id: "p1", chat: "p", question: "How will answers look in this app?", answer: "This is a sample answer with a source citation [1].\n\nAdjust the appearance on the left to see it here. This preview does not contact your model or sources.", evidence: [{ n: 1, title: "Sample source for visual preview", text: "Preview sample only, not a retrieved document." }], ledger: [], seconds: 0 }];
  S.chat = "p"; drawThread(); pvBottom(); $("#chatTitle").textContent = "Sample conversation";
  const list = $("#list"); list.replaceChildren(...["Sample conversation", "Another conversation"].map((t, i) => el("div", { class: "item" + (i ? "" : " on") }, el("span", { text: t }))));
  const previewCopy = () => JSON.stringify(["txt_title","txt_tagline","txt_examples","logo"].map(TV));
  let lastCopy = previewCopy();
  window.addEventListener("message", (e) => { if (e.origin === location.origin && e.data && e.data.ccTheme) {
    if(["calm","none"].includes(TV("motion"))||matchMedia("(prefers-reduced-motion:reduce)").matches)window.ccStopPreviewMotion();
    const thread = $("#thread"), scroll = thread.scrollTop, copy = previewCopy();
    applyWording(); applyIcons(); updatePreviewAvatars();
    if (copy !== lastCopy) { drawThread(); thread.scrollTop = scroll; lastCopy = copy; }
    $("#q").placeholder = "Ask a sample question"; $("#chatTitle").textContent = "Sample conversation";
  } });
}
function tour(replay=false) {
  CCTour.chat(replay, () => $("#q").focus());
}
$("#chatGuide")?.addEventListener("click", () => tour(true));

})();

document.getElementById("sideClose")?.addEventListener("click", () => document.getElementById("app").classList.remove("menu-open"));
(() => { const c = document.querySelector(".composer"); if (!c) return; const set = () => document.documentElement.style.setProperty("--composer-h", Math.ceil(c.getBoundingClientRect().height + (window.innerHeight - c.getBoundingClientRect().bottom)) + "px"); set(); window.addEventListener("resize", set); if (window.ResizeObserver) new ResizeObserver(set).observe(c); })();


// if saving is not possible (disk full, read-only folder) the server keeps answering; say so once
try { fetch("/api/health").then((r) => r.json()).then((h) => { if (h && h.degraded && typeof toast === "function") toast(h.degraded); }).catch(() => {}); } catch (e) { /* notice only */ }
