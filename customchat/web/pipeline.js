(() => {
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const token = localStorage.getItem("cc_token") || "";
async function api(path, body) {
  const h = { "Content-Type": "application/json" }; if (token) h.Authorization = "Bearer " + token;
  const r = await fetch(path, body === undefined ? { headers: h } : { method: "POST", headers: h, body: JSON.stringify(body) });
  const d = await r.json().catch(() => ({})); if (!r.ok) throw new Error(d.error || "Request failed"); return d;
}
const el = (t, p = {}, ...k) => { const e = document.createElement(t); for (const [a, v] of Object.entries(p)) { if (v == null) continue; if (a === "class") e.className = v; else if (a === "text") e.textContent = v; else if (a.startsWith("on")) e.addEventListener(a.slice(2), v); else e.setAttribute(a, v); } e.append(...k.filter((x) => x != null)); return e; };
const NOTE = (m) => { const n = $("#msg"); if (n) { n.textContent = m; n.className = "msg"; } };
let stages = [], real = false, helperState = {}, connectorKeys={};

function diagram() {
  const box = el("div", { class: "pipe", role: "list", "aria-label": "Order of steps for each question" });
  const order = ["question_check", "standalone", "queries", "relevance", "answer", "faithfulness", "followups"];
  const names = { question_check: "Check question", standalone: "Make standalone", queries: "Write searches", relevance: "Keep relevant", answer: "Write answer", faithfulness: "Check support", followups: "Suggest follow-ups" };
  order.forEach((k, i) => {
    const s = stages.find((x) => x.key === k); const on = !s || !s.optional || s.on;
    if (i) box.append(el("span", { class: "arrow", "aria-hidden": "true", text: "\u203A" }));
    box.append(el("a", { href: "#st-" + k, role: "listitem", class: "step" + (on ? "" : " off"), text: names[k] + (on ? "" : " (off)") }));
  });
  return box;
}

function stageCard(s) {
  const area = el("textarea", { rows: "6", maxlength: "6000", "aria-label": s.label + " prompt", spellcheck: "false" });
  area.value = s.text || s.default;
  const fit=()=>{area.style.height='auto';area.style.height=Math.min(560,Math.max(200,area.scrollHeight))+'px'};area.addEventListener('input',()=>{area.classList.remove('prompt-draft-updated');clearTimeout(area._draftTimer);fit();st.textContent='Manual edits. Review, then save.'});requestAnimationFrame(fit);
  const brief = el("input", { placeholder: "Topic (optional)", "aria-label": "About your topic" });
  const st = el("span", { class: "testres", role: "status" });
  const sw = s.optional ? el("label", { class: "check sw" }, el("input", { type: "checkbox", id: "on-" + s.key }), " Use this step") : null;
  if (sw) { $("input", sw).checked = !!s.on; $("input", sw).addEventListener("click",e=>{if(e.currentTarget.getAttribute("aria-busy")==="true")e.preventDefault()}); $("input", sw).addEventListener("change", async (e) => {const control=e.target;if(control.disabled)return;if(control.getAttribute("aria-busy")==="true"){control.checked=control.dataset.pendingChecked==="true";return}const previous=!!s.on,requested=control.checked;control.dataset.pendingChecked=String(requested);control.setAttribute("aria-busy","true");control.setAttribute("aria-disabled","true");st.textContent="Saving step state...";try { await api("/api/prompts/save", { key: s.key, on: requested }); s.on = requested;control.checked=requested; const sm = $("summary small", $("#st-" + s.key)); if (sm) sm.textContent = s.on ? "On" : "Off"; redrawDiagram(); st.textContent = requested ? "On." : "Off."; } catch (x) { st.textContent = x.message; control.checked=previous; }finally{control.removeAttribute("aria-busy");control.removeAttribute("aria-disabled");delete control.dataset.pendingChecked} }); }
  const save = el("button", { type: "button", class: "go blue", text: "Save", onclick: async () => {if(save.disabled)return;clearTimeout(save._savedTimer);save.classList.remove("save-confirmed");let didSave=false;save.disabled=true;reset.disabled=gen.disabled=true;save.textContent="Saving...";const txt = area.value.trim() === s.default.trim() ? "" : area.value;try { const r = await api("/api/prompts/save", { key: s.key, text: txt }); s.text = txt; st.textContent = area.value.trim()===(txt||s.default).trim()?"Saved. New questions use it.":"Previous edits saved. Newer prompt edits are still unsaved.";didSave=true; } catch (x) { st.textContent = x.message; }finally{save.disabled=false;reset.disabled=gen.disabled=false;save.textContent="Save";if(didSave)window.CCSavedFeedback?.(save,"Save")} } });
  const reset = el("button", { type: "button", class: "go ghost", text: "Use default",title:"Replace this prompt with the default and save it immediately", onclick: async () => {if(reset.disabled)return;try { if(area.value.trim()!==s.default.trim()&&!confirm("Replace this customized prompt with the default?"))return;reset.disabled=true;save.disabled=gen.disabled=true;reset.textContent="Restoring default...";const before=area.value;await api("/api/prompts/reset", { key: s.key });s.text="";if(area.value===before){area.value=s.default;st.textContent="Back to the default.";fit()}else{st.textContent="Default saved. Newer manual edits are still unsaved."} } catch (x) { st.textContent = x.message; }finally{reset.disabled=false;save.disabled=gen.disabled=false;reset.textContent="Use default"} } });
  const gen = el("button", { type: "button", class: "go ghost", text: "Write it with AI", onclick: async () => {if(gen.disabled)return;gen.disabled = true;gen.textContent="Writing...";save.disabled=reset.disabled=true; st.classList.add("ai-working");st.textContent = "Writing with your selected model...";const original=area.value;try { const r = await api("/api/prompts/generate", { key: s.key, brief: brief.value, current: original });if(area.value!==original){st.textContent="Prompt changed during writing. Your newer edits were kept. Write again when ready.";return}area.value = r.prompt;area.classList.add("prompt-draft-updated");clearTimeout(area._draftTimer);area._draftTimer=setTimeout(()=>area.classList.remove("prompt-draft-updated"),1400); st.textContent = r.model_used ? "Written. Review, then save." : "Offline stage draft. Review assumptions, then save.";st.className="testres";why.className="why h";if (r.rationale && r.rationale.length) why.textContent = r.rationale.join(" "); } catch (x) { st.textContent = x.message; } finally {gen.disabled = false;gen.textContent="Write it with AI";save.disabled=reset.disabled=false;st.classList.remove("ai-working");fit()}  } });
  const why = el("p", { class: "h" });
  return el("details", { class: "stage", id: "st-" + s.key }, el("summary", {}, el("b", { text: s.label }), el("small", { text: s.optional ? (s.on ? "On" : "Off") : "Always on" })), el("div", { class: "sbody" }, el("p", { class: "h", text: s.help }), sw, area, el("div", { class: "keyrow" }, brief, gen), why, el("div", { class: "keyrow" }, save, reset, st)));
}
let selected = {},focusSection="";
function placePrompt(){const focused=document.activeElement,scroll=focused?.scrollTop,layout=$(".layout"),preview=$("#pvbox");if(!layout)return;const desktop=false,active=focusSection==="prompts"||focusSection==="code";document.body.classList.toggle("prompt-pane-active",active&&desktop);for(const kind of ["prompts","code"]){const pane=$("#"+kind+"Editor"),section=$("#sec-"+kind);if(!pane||!section)continue;if(focusSection===kind&&desktop){pane.classList.add("prompt-side-editor");if(pane.parentElement!==layout||pane.nextSibling!==preview)layout.insertBefore(pane,preview)}else{pane.classList.remove("prompt-side-editor");const list=$(".editor-list",section),before=focusSection===kind&&!desktop?list:null;if(pane.parentElement!==section||pane.nextSibling!==before)section.insertBefore(pane,before)}}if(preview)preview.hidden=active&&desktop;if(focused?.isConnected&&focused!==document.body&&document.activeElement===document.body&&focused.closest(".pipeline-editor-pane")&&focused.getClientRects().length)focused.focus({preventScroll:true});if(focused?.isConnected&&focused.closest(".pipeline-editor-pane")&&document.activeElement===focused){focused.scrollTop=scroll;requestAnimationFrame(()=>{if(document.activeElement===focused)focused.scrollTop=scroll})}}
window.CCPipelineFocus=section=>{focusSection=section;document.body.classList.toggle("settings-editor-wide",section==="prompts"||section==="code");placePrompt()};window.addEventListener("resize",placePrompt);

function editorList(section, cards, kind) {
  const pane = el("div", {class:"pipeline-editor-pane inline-editor",id:kind+"Editor", "aria-label":kind === "prompts" ? "Selected prompt editor" : "Selected code editor"});
  const list = el("div", {class:"editor-list", role:"list", "aria-label":kind === "prompts" ? "Prompt stages" : "Code helpers"});
  const choose = (card, button) => {
    if (selected[kind]){const old=selected[kind].card,area=$("textarea",old);if(kind==="prompts"&&area)old._promptView={scroll:area.scrollTop,start:area.selectionStart,end:area.selectionEnd};old.hidden=true;}
    cards.forEach(c => c.classList.remove("selected-editor"));
    list.querySelectorAll("button").forEach(b => b.setAttribute("aria-pressed", String(b === button)));
    card.hidden = false; card.open = true; card.classList.add("selected-editor");
    selected[kind] = {card,button};
    pane.replaceChildren(card);placePrompt();
    if(kind==="prompts"){const area=$("textarea",card),view=card._promptView;if(area&&view){area.setSelectionRange(view.start,view.end);area.scrollTop=view.scroll;requestAnimationFrame(()=>{if(selected[kind]?.card===card)area.scrollTop=view.scroll})}placePrompt()}
  };
  cards.forEach(card => {
    const title = $("summary b", card)?.textContent || "Editor";
    const button = el("button", {type:"button",class:"editor-choice", "aria-pressed":"false",onclick:()=>choose(card,button)}, el("b", {text:title}));
    button.dataset.stage = card.id.replace(/^st-/, ""); card.hidden = true; list.append(button);
  });
  section.append(list, pane);
  section._editorCards=cards;
  if (cards[0]) choose(cards[0],list.querySelector("button"));
  section._choose=choose;placePrompt();
}
let dg;
function redrawDiagram() { if (dg) { const n = diagram(); dg.replaceWith(n); dg = n; } }

function codeCard(kind, title, help, ph) {
  const brief = el("textarea", { rows: "3", "aria-label": title + " description", placeholder: "Describe what this helper should do." });
  const example = el("details", {class:"helper-example"}, el("summary",{text:"Example description"}),el("p",{class:"h",text:ph.replace(/^Example: /, "")}));
  let recognized = "";
  const connectorHelpId="connectorKeyHelp-"+kind;const apiKey=el("input",{type:"password",autocomplete:"off",spellcheck:"false","aria-label":"Optional connector API key","aria-describedby":connectorHelpId,placeholder:"API key"});
  const detected=el("p",{class:"h",role:"status"});
  let detectSequence=0;const infer=async(saveKey=false)=>{const seq=++detectSequence,submittedBrief=brief.value,submittedKey=apiKey.value;const r=await api("/api/codegen/infer",{brief:submittedBrief,key:submittedKey,save_key:saveKey});if(seq!==detectSequence||brief.value!==submittedBrief){detected.textContent=saveKey?"Previous connector key request finished. Check the current connector again.":"Connector changed during detection. Detect the current connector again.";return r}recognized=r.recognized?r.id:"";detected.textContent=r.recognized?"Detected: "+r.name+". Requests go to "+r.endpoint+". Review before testing.":r.message;if(r.recognized&&saveKey){if(apiKey.value===submittedKey)apiKey.value="";detected.textContent+=" Key saved privately."}return r};
  const saveConnectorKey=el("button",{type:"button",class:"go ghost",text:"Save key privately",onclick:async()=>{if(saveConnectorKey.disabled)return;if(!apiKey.value.trim()){detected.textContent="Enter a key first. If your service needs no key, use Detect API.";return}saveConnectorKey.disabled=true;detected.textContent="Saving key...";try{await infer(true)}catch(e){detected.textContent=e.message}finally{saveConnectorKey.disabled=false}}});
  const detect=el("button",{type:"button",class:"go ghost",text:"Detect API",onclick:async()=>{if(detect.disabled)return;if(!brief.value.trim()&&!apiKey.value.trim()){detected.textContent="Add the service name or documentation URL above first.";return}detect.disabled=true;detect.textContent="Detecting...";const statusHeight=detected.getBoundingClientRect().height;detected.style.minHeight=statusHeight+"px";detected.textContent="Detecting API...";try{await infer(false)}catch(e){detected.textContent=e.message}finally{detect.disabled=false;detect.textContent="Detect API";detected.style.minHeight=""}}});
  const host = el("div", { class: "cmhost" }),dirty=el("p",{class:"h helper-dirty",role:"status"});const markDirty=()=>{dirty.textContent="Unsaved helper draft edits.";};
  const ed = window.CCEditor ? window.CCEditor.create(host, { doc: "",onChange:markDirty }) : null;
  const fallback = ed ? null : el("textarea", { rows: "12", class: "code", spellcheck: "false", "aria-label": title + " code" });
  if(fallback)fallback.addEventListener("input",markDirty);
  const code = { get value() { return ed ? ed.get() : fallback.value; }, set value(v) { if (ed) ed.set(v); else fallback.value = v; } };
  if (ed) { let free = false; host.addEventListener("keydown", (e) => { if (e.key === "Escape") { free = true; return; } if (e.key === "Tab" && free) { e.stopImmediatePropagation(); free = false; return; } free = false; }, true); }
  if (ed) { host.dataset.ph = "The code appears here after you press Write the code."; const sync = () => host.classList.toggle("filled", !!ed.get()); new MutationObserver(sync).observe(host, { childList: true, subtree: true, characterData: true }); sync(); }
  const out = el("div", { class: "review", role: "status", "aria-live": "polite" });
  let checking=false;async function review() {if(checking)return;checking=true;const inspected=code.value;out.textContent="Checking code...";try { const r = await api("/api/codegen/review", { kind, code: inspected });if(code.value!==inspected){out.textContent="Code changed during checking. Check the current code again.";return} out.className = "review " + (r.ok ? "ok" : "bad"); if (ed) { host._marks = r.marks || []; ed.mark(host._marks); } out.replaceChildren(el("b", { text: r.ok ? "Static checks passed - not a security sandbox" : "Needs changes" }), ...(r.problems || []).map((p) => el("div", { text: p }))); } catch (x) { out.textContent = x.message; }finally{checking=false} }
  const gen = el("button", { type: "button", class: "go blue", text: "Write the code", onclick: async () => { if(gen.disabled)return;if (!brief.value.trim() && !apiKey.value.trim() && !recognized) { out.className = "review bad"; out.textContent = "Describe what it should do first."; return; } const originalCode=code.value;gen.disabled = true;gen.textContent="Writing...";brief.disabled=true;out.className = "review ai-working"; out.textContent = "Writing..."; try { if(kind==="search"&&!recognized)await infer(false); if(kind==="search"&&!recognized&&!brief.value.trim()){out.textContent="Name the API or paste its docs URL first.";return} const r = await api("/api/codegen", { kind, brief: brief.value, sample, ...(recognized?{known_provider:recognized}:{}) }); sample = "";if(code.value!==originalCode){out.textContent="Code changed during writing. Your newer edits were kept. Write again when ready.";return}code.value = r.code || ""; await review(); if (!r.model_used && !r.known_provider) out.append(el("div", { class: "h", text: "No model is connected. Review this offline draft; unknown API endpoint/schema stays non-operational until supplied." })); } catch (x) { out.className = "review bad"; out.textContent = x.message; } finally {gen.disabled = false;gen.textContent="Write the code";brief.disabled=false;out.classList.remove("ai-working")} } });
  let sample = "";
  brief.addEventListener("input",()=>{recognized=""});
  const tq = el("input", { placeholder: "Sample question to try", "aria-label": "Sample question", value: kind === "search" ? "vitamin D and sleep" : "Can you tell me about vitamin D?" });
  const tres = el("div", { class: "review helper-run-result", role: "status", "aria-live": "polite" });
  const tryBtn = el("button", { type: "button", class: "go ghost", text: "Try it", title: "Runs reviewed code once in a bounded process, NOT a sandbox. Host files/network remain accessible.", onclick: async () => {
    if(tryBtn.disabled)return;const runCode=code.value,runQuery=tq.value,runConnector=recognized;tryBtn.disabled = true;tryBtn.textContent="Checking..."; out.className = "review"; out.textContent = ""; if (ed) ed.mark([]); tres.className = "review helper-run-result"; tres.textContent = "Checking before running..."; try {
      const checked=await api("/api/codegen/review",{kind,code:runCode});
      if(code.value!==runCode||tq.value!==runQuery||recognized!==runConnector){tres.textContent="Helper or sample changed during checking. Review the current code and try again. Nothing ran.";return}
      if(!checked.ok){tres.className="review helper-run-result bad";tres.textContent="Fix compilation/safety errors first: "+checked.problems.join(" ");return}
      if(kind==="search"&&runConnector){
        if(!confirm("Run one live search using the saved key through the built-in "+recognized+" connector? This can use provider credits. Edited code is not run with your key.")){tres.textContent="Not run.";return}
        tryBtn.textContent="Running...";tres.textContent="Running one live search...";const r=await api("/api/websearch/test",{id:runConnector,query:runQuery});tres.textContent=r.ok?"Built-in connector returned "+r.items.length+" results. Edited helper code was not run with your key.":r.error;return;
      }
      tryBtn.textContent="Running...";tres.textContent="Running once...";const r = await api("/api/codegen/test", { kind, code: runCode, query: runQuery }); tres.className = "review helper-run-result " + (r.ok ? "ok" : "bad");
      const rows = [el("b", { text: r.ok ? "Worked" + (kind === "search" ? ": " + r.count + " result" + (r.count === 1 ? "" : "s") + " in " + r.seconds + "s" : ": " + (r.result || "")) : r.error || (r.empty ? "It ran but returned no results. Try another sample question, or show a raw response and rewrite the parsing." : "Needs changes")})];
      (r.problems || []).forEach((x) => rows.push(el("div", { text: x }))); (r.items || []).forEach((it) => rows.push(el("div", { class: "item", text: (it.title || "(no title)") + (it.year ? " (" + it.year + ")" : "") + ": " + (it.text || "").slice(0, 110) })));
      if (r.ok && (r.items || []).length) { const norm = JSON.stringify(r.items, null, 2); const parts = [el("div", { class: "h", text: "Normalized: what the chat receives from your code" }), el("pre", { class: "code", text: norm.slice(0, 4000) })]; if (raw.value.trim()) parts.unshift(el("div", { class: "h", text: "Raw: what the API sent (the box above)" }), el("pre", { class: "code", text: raw.value.slice(0, 1500) })); rows.push(el("details", { class: "stage inner" }, el("summary", {}, el("b", { text: "Compare raw and normalized" })), el("div", { class: "sbody" }, ...parts))); }
      tres.replaceChildren(...rows); } catch (x) { tres.className = "review helper-run-result bad"; tres.textContent = x.message; } finally {tryBtn.disabled = false;tryBtn.textContent="Try it";tres.classList.remove("helper-result-enter");void tres.offsetWidth;tres.classList.add("helper-result-enter")} } });
  const url = el("input", { placeholder: "https://api.example.org/search?q={query}", "aria-label": "API address for a sample response" });
  const raw = el("textarea", { rows: "5", class: "code", "aria-label": "Raw response", placeholder: "A raw response from the API appears here. You can also paste one.", spellcheck: "false" });
  const sampleStatus=el("div",{class:"review",role:"status","aria-live":"polite"});
  const show = el("button", { type: "button", class: "go ghost", text: "Show raw response", onclick: async () => {if(show.disabled)return;if(!url.value.trim()){sampleStatus.textContent="Enter an API address first.";return}show.disabled=true;show.textContent="Fetching...";const originalRaw=raw.value,requestUrl=url.value,requestQuery=tq.value;sampleStatus.textContent="Fetching one sample response...";try { const r = await api("/api/codegen/sample", { url: requestUrl, query: requestQuery });if(raw.value!==originalRaw||url.value!==requestUrl||tq.value!==requestQuery){sampleStatus.textContent="Sample changed while fetching. Your newer edits were kept. Fetch again when ready.";return} raw.value = r.body; sampleStatus.className = "review"; sampleStatus.textContent = "Got HTTP " + r.status + " (" + (r.type || "unknown type") + "). Now press Rewrite parsing."; } catch (x) { sampleStatus.className = "review bad"; sampleStatus.textContent = x.message; }finally{show.disabled=false;show.textContent="Show raw response"} } });
  const rewrite = el("button", { type: "button", class: "go blue", text: "Rewrite parsing from this response", onclick: () => { sample = raw.value; gen.click(); } });
  const live = kind === "search" ? el("details", { class: "stage inner" }, el("summary", {}, el("b", { text: "Match a real response" }), el("small", { text: "Optional" })), el("div", { class: "sbody" }, el("p", { class: "h", text: "Fetch one real response so the parsing fits it." }), el("div", { class: "keyrow" }, url, show),sampleStatus, raw, rewrite)) : null;
  const initial=helperState[kind];if(initial){brief.value=initial.brief||"";code.value=initial.code||"";}
  dirty.textContent="";brief.addEventListener("input",markDirty);
  const pids=Object.keys(connectorKeys).filter(k=>new RegExp("\\b"+k+"\\b","i").test(brief.value));recognized=pids.length===1?pids[0]:"";
  const filled=el("p",{class:"h",role:"status",text:initial?.code?"Existing helper loaded from this workspace.":"No saved helper draft. Describe what it should do, then write the code."});
  
  if(recognized){apiKey.placeholder=connectorKeys[recognized]?"Saved key available (replace only)":"API key";detected.textContent=recognized+": "+(connectorKeys[recognized]?"Key saved privately.":"No key saved. Add one only if this service needs it.");}else{apiKey.placeholder="API key";detected.textContent="No API detected yet. Add its name or documentation URL above.";}
  const saveDraft=el("button",{type:"button",class:"go ghost",text:"Save helper draft",onclick:async()=>{if(saveDraft.disabled)return;clearTimeout(saveDraft._savedTimer);saveDraft.classList.remove("save-confirmed");saveDraft.disabled=true;saveDraft.textContent="Saving...";let didSave=false;const snapshot={kind,brief:brief.value,code:code.value};try{await api("/api/codegen/draft",snapshot);const unchanged=brief.value===snapshot.brief&&code.value===snapshot.code;dirty.textContent=unchanged?"All helper draft edits saved.":"Unsaved helper draft edits.";filled.textContent=snapshot.code.trim()?"Helper draft saved in this workspace.":"No saved helper code.";out.textContent=unchanged?"Draft saved in this workspace. Not activated or run.":"Previous draft saved. Newer helper edits are still unsaved.";didSave=true;}catch(e){out.textContent=e.message}finally{saveDraft.disabled=false;saveDraft.textContent="Save helper draft";if(didSave)window.CCSavedFeedback?.(saveDraft,"Save helper draft");if(saveDraft.isConnected&&document.activeElement===document.body)saveDraft.focus()}}});
  const copy = el("button", { type: "button", class: "go ghost", text: "Copy", onclick: async () => {if(copy.disabled)return;clearTimeout(copy._copyTimer);copy.classList.remove("copy-done");copy.disabled=true;copy.textContent="Copying...";const copiedCode=code.value;try{if(!navigator.clipboard)throw Error("Clipboard unavailable. Select and copy the code instead.");await navigator.clipboard.writeText(copiedCode);copy.classList.add("copy-done");copy.textContent="Copied";copy._copyTimer=setTimeout(()=>{copy.classList.remove("copy-done");copy.textContent="Copy"},1400);out.textContent="Copied."}catch(e){copy.classList.remove("copy-done");copy.textContent="Copy";out.textContent=e.message}finally{copy.disabled=false;if(copy.isConnected&&document.activeElement===document.body)copy.focus()}} });
  const chk = el("button", { type: "button", class: "go ghost", text: "Check again", onclick: review });
  return el("details", { class: "sub helper" }, el("summary", {}, el("b", { text: title }), el("small", { text: help })), el("h4",{text:"Configure connector"}), kind==="search"?el("p",{class:"h",text:"Add the service name or documentation URL below. Detect API identifies supported services locally; it does not test a connection."}):null, brief, example, filled, kind==="search"?el("label",{class:"connector-key-label",text:"Connector API key (optional)"},el("div",{class:"keyrow"},apiKey,saveConnectorKey,detect)):null, kind==="search"?el("p",{class:"h",id:connectorHelpId,text:"Enter a key only if this service requires one. This field is editable before detection. Save key privately stores it on this computer after identifying a supported service. The key entered here is not included in generated code or sent to the writing model. Do not put keys in the description above."}):null, kind==="search"?detected:null, live,el("h4",{text:"Generate and review"}),el("div", { class: "keyrow tight" }, gen, chk),el("div", { class: "keyrow tight secondary-actions" }, copy, saveDraft), ed ? host : fallback,dirty, ed ? el("small", { class: "h", text: "Press Esc, then Tab, to move past the editor." }) : null, out, el("h4",{text:"Try the helper"}),el("p",{class:"h",text:"Enter one sample question. Try it runs code once, not in a security sandbox. Code can access files and the network on this computer. Review it before running."}),el("div", { class: "keyrow" }, tq, tryBtn), tres);
}

function build(col) {
  const prompts = el("section", { class: "tile", id: "sec-prompts" }, el("div", { class: "head" }, el("span", { class: "ic purple", text: "\u2630" }), el("div", {}, el("b", { text: "Prompts" }), el("small", { text: "The instructions behind each step of an answer" }))),
    el("div", { class: "help", text: "Always-on steps run for each question. Optional checks start off and add model calls when enabled. Select a step to read its purpose and edit its prompt." }));
  dg = diagram(); prompts.append(dg);
  const GROUPS = [["Understand the question", ["question_check", "standalone", "queries"]], ["Find the evidence", ["relevance"]], ["Write and check the answer", ["answer", "faithfulness", "revise", "followups", "summary"]]];
  const used = new Set(); GROUPS.forEach(([t, ks]) => { const list = stages.filter((s) => ks.includes(s.key)); if (!list.length) return; list.forEach((s) => used.add(s.key)); prompts.append(el("div", { class: "pgroup", text: t })); list.forEach((s) => prompts.append(stageCard(s))); });
  stages.filter((s) => !used.has(s.key)).forEach((s) => prompts.append(stageCard(s)));

  const code = el("section", { class: "tile", id: "sec-code" }, el("div", { class: "head" }, el("span", { class: "ic green", text: "</>" }), el("div", {}, el("b", { text: "Code helpers" }), el("small", { text: "Describe it, read the code, then use it yourself" }))),
    el("div", { class: "help", text: "These write small Python helpers. Static checks run before display; they do not prove safety. Try it runs only on your click in a bounded process, NOT a sandbox. Host files and network remain accessible." }),
    codeCard("search", "Search connector", "Pulls passages from your own API or website.", "Example: search my clinic's JSON API at https://example.org/api, using the q parameter, and return title, text and link."),
    codeCard("clean_query", "Query cleaning", "Tidies a question before it is searched.", "Example: remove filler words, keep drug names and numbers, and lowercase everything."));

  const promptCards = [...prompts.querySelectorAll(":scope > details.stage")];
  const codeCards = [...code.querySelectorAll(":scope > details.helper")];
  promptCards.forEach(c=>c.remove());codeCards.forEach(c=>c.remove());
  prompts.querySelectorAll(".pgroup").forEach(n=>n.remove());
  editorList(prompts,promptCards,"prompts");editorList(code,codeCards,"code");
  prompts.querySelector(".help").textContent="";
  const m = $("#sec-model"); const anchor = $("#sec-presets");
  col.insertBefore(prompts, anchor); col.insertBefore(code, anchor);

}
async function init() {
  try { const d = await api("/api/prompts"); stages = d.stages; real = d.real_model; } catch (e) { return; }
  try { const current=await api("/api/configuration-state");helperState=current.helpers||{};connectorKeys=current.connector_keys||{}; } catch(e) {}
  build($("#col"));
  window.CCSettingsRefreshNavigation?.();
}
init();
})();
