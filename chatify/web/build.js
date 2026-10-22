/* Guided build: describe -> confirm sources -> build. Deterministic source suggestions, no model calls before the build itself. */
(() => {
"use strict";
const $ = (s, r = document) => r.querySelector(s);
const el = (tag, cls, text) => { const n = document.createElement(tag); if (cls) n.className = cls; if (text !== undefined) n.textContent = text; return n; };
const BASE = window.CC_APP_BASE || "";
const headers = () => { const h = { "Content-Type": "application/json" }; const t = localStorage.getItem("cc_token"); if (t) h.Authorization = "Bearer " + t; return h; };
async function api(path, body) { const r = await fetch("/api/settings/build/" + path, { method: "POST", headers: headers(), body: JSON.stringify(body || {}) }); const d = await r.json().catch(() => ({})); if (!r.ok) throw Error(d.error || "Request failed"); return d; }

const SECTIONS_ALL = ['schema_version','actions','budget','app','provider','sources','retrieval','prompt','memory','citations','auth','storage','server','appearance','pipeline_prompts','helper_drafts','api_suggestions'];

const ICONS = {
  book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20V4H6.5A2.5 2.5 0 0 0 4 6.5v13z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H20v-5"/></svg>',
  flask: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 3h6M10 3v6L4.5 19a2 2 0 0 0 1.8 3h11.4a2 2 0 0 0 1.8-3L14 9V3"/><path d="M7.5 15h9"/></svg>',
  graph: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="6" cy="6" r="2.5"/><circle cx="18" cy="8" r="2.5"/><circle cx="9" cy="18" r="2.5"/><circle cx="18.5" cy="17.5" r="2.5"/><path d="M8.2 7.2l7.3.6M7.2 8.4l1.2 7M10.9 16.5l5-6.9M11.4 18h4.6"/></svg>',
  globe: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.8 5.7 3.8 9S14.5 18.4 12 21c-2.5-2.6-3.8-5.7-3.8-9S9.5 5.6 12 3z"/></svg>',
  folder: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V7z"/></svg>',
  plug: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 7V3M15 7V3M7 7h10v4a5 5 0 0 1-10 0V7zM12 16v5"/></svg>'
};

const CONNECTORS = [
  { id: "pubmed", name: "PubMed", icon: "book", what: "Biomedical research articles and abstracts from the U.S. National Library of Medicine.", why: "Strong fit for health, medicine and life-science questions that need citable studies.", kw: ["medic", "health", "clinic", "biomed", "cancer", "disease", "drug", "therap", "patient", "diet", "nutrition", "immun", "vaccine", "genom", "diabetes", "covid", "surgery", "neuroscience"], names: ["pubmed"] },
  { id: "arxiv", name: "arXiv", icon: "flask", what: "Open preprints in physics, mathematics, computer science and quantitative fields.", why: "Strong fit for technical and preprint research questions.", kw: ["physics", "math", "quantum", "machine learning", "deep learning", "neural", "algorithm", "preprint", "computer science", "astro", "robot", "cryptograph"], names: ["arxiv"] },
  { id: "openalex", name: "OpenAlex", icon: "graph", what: "Open scholarly metadata: papers, authors, venues and citation links across all fields.", why: "Broad scholarly coverage that fits research questions in any field.", kw: ["research", "paper", "scholar", "citation", "literature", "studies", "study", "journal", "academic", "science"], names: ["openalex", "open alex"] },
  { id: "crossref", name: "Crossref", icon: "graph", what: "DOI registration metadata for scholarly works across publishers.", why: "Complements scholarly coverage with publisher metadata and DOIs.", kw: ["doi", "publisher metadata"], names: ["crossref"] },
  { id: "wikipedia", name: "Wikipedia", icon: "globe", what: "General encyclopedic background: people, places, concepts and history.", why: "Reliable background and definitions alongside more specialized sources.", kw: ["history", "biograph", "general", "encyclop", "concept", "geograph", "culture", "war", "politic", "background", "explain"], names: ["wikipedia", "wiki"] },
  { id: "local_files", name: "Your documents", icon: "folder", what: "Files you provide - Markdown, text, CSV or PDF - indexed as the app's evidence.", why: "Grounds every answer in material you supply yourself.", kw: ["document", "file", "pdf", "notes", "upload", "internal", "lecture", "course", "slides", "our data", "my data"], names: ["documents", "files", "local files"] },
  { id: "web_search", name: "Live web search", icon: "globe", what: "Recent public web results for current events and fast-moving topics.", why: "Keeps answers current where published sources lag.", kw: ["news", "current", "recent", "today", "latest", "breaking", "headline", "this week"], names: ["web search", "web"] },
  { id: "http_json", name: "Custom JSON API", icon: "plug", what: "Any documented HTTP JSON API you point the app at.", why: "Connects a specific service you name, once you supply its endpoint.", kw: [], names: ["api", "json api"] }
];

const state = { brief: "", selected: [], provider: null, model: "", canEdit: false, providerOk: false, jobId: null, timer: null, running: false };

const screens = [$("#buildDescribe"), $("#buildSources"), $("#buildProgress")];
function goStep(i) {
  screens.forEach((s, j) => { s.hidden = j !== i; });
  document.querySelectorAll(".build-step").forEach((n, j) => { if (j === i) n.setAttribute("aria-current", "step"); else n.removeAttribute("aria-current"); });
  window.scrollTo({ top: 0, behavior: "instant" });
}

/* Step 1: describe */
const brief = $("#buildBrief"), toSources = $("#buildToSources");
brief.addEventListener("input", () => { toSources.disabled = brief.value.trim().length < 12; brief.style.height = "auto"; brief.style.height = Math.min(180, brief.scrollHeight + 2) + "px"; });
const EXAMPLES = [
  "A research assistant that answers questions about recent cancer immunotherapy papers, for graduate students. Answers must cite the papers they use.",
  "A nutrition Q&A for my students that answers questions about diet and health, cited from biomedical research.",
  "A helper over our internal lecture notes and slides that answers questions with citations to the documents."
];
document.querySelectorAll(".build-chip").forEach((chip, i) => { chip.addEventListener("click", () => { brief.value = EXAMPLES[i] || chip.textContent; brief.dispatchEvent(new Event("input")); brief.focus(); }); });
if (BASE) { const g = $("#buildGalleryLink"); g.href = "/"; g.textContent = "Browse the app gallery"; }

function suggest(text) {
  const lower = " " + text.toLowerCase() + " ";
  const scored = CONNECTORS.map(c => {
    let score = 0;
    for (const n of c.names) if (lower.includes(n)) score += 6;
    for (const k of c.kw) if (lower.includes(k)) score += 1;
    return { c, score };
  }).filter(x => x.score > 0).sort((a, b) => b.score - a.score);
  const explicit = scored.filter(x => x.score >= 6).map(x => x.c.id);
  const picked = [];
  for (const x of scored) { if (picked.length >= 3) break; picked.push(x.c.id); }
  for (const e of explicit) if (!picked.includes(e)) picked.push(e);
  return picked.slice(0, 4);
}

/* Step 2: sources */
function connById(id) { return CONNECTORS.find(c => c.id === id); }
function paintSources() {
  const wrap = $("#sourceCards"); wrap.replaceChildren();
  state.selected.forEach((id, idx) => {
    const c = connById(id); if (!c) return;
    const card = el("article", "build-card"); card.setAttribute("role", "listitem"); card.style.animationDelay = (idx * 0.06) + "s";
    const icon = el("span", "build-card-icon"); icon.innerHTML = ICONS[c.icon] || ICONS.globe;
    const body = el("div", "build-card-body");
    const head = el("div", "build-card-head");
    head.append(el("b", null, c.name));
    head.append(el("span", "build-card-tag" + (idx > 0 ? " optional" : ""), idx === 0 ? "Recommended" : "Optional"));
    body.append(head);
    body.append(el("p", null, c.what));
    body.append(el("p", "why", "Why it fits: " + c.why));
    body.append(el("p", "status", "Suggested - not connected or tested yet. Chatify checks sources after the build."));
    const remove = el("button", "build-card-remove", "Remove"); remove.type = "button";
    remove.setAttribute("aria-label", "Remove " + c.name);
    remove.onclick = () => { state.selected = state.selected.filter(x => x !== id); paintSources(); };
    card.append(icon, body, remove);
    wrap.append(card);
  });
  if (!state.selected.length) wrap.append(el("p", "build-note", "No sources selected. Pick from the catalog below, or go back and describe what your app should answer in more detail."));
  const cat = $("#sourceCatalog"); cat.replaceChildren();
  for (const c of CONNECTORS) {
    const b = el("button", "build-cat", "+ " + c.name); b.type = "button"; b.setAttribute("role", "listitem");
    b.disabled = state.selected.includes(c.id);
    b.title = c.what;
    b.onclick = () => { state.selected.push(c.id); paintSources(); };
    cat.append(b);
  }
  updateStart();
}
function paintWhy() {
  $("#sourcesWhy").textContent = "Chatify matched words in your description against a small fixed registry of supported source types - no AI was used for these suggestions, and no source has been contacted yet. The build drafts the full configuration for the sources you confirm; you review everything before saving.";
}
async function checkProvider() {
  const note = $("#buildProviderNote");
  note.textContent = "";
  try {
    const r = await fetch("/api/settings", { headers: headers() });
    const s = await r.json();
    const st = s.settings || {};
    state.provider = st.provider; state.model = st.model; state.canEdit = s.can_edit === true;
    const pr = await fetch("/api/provider/status", { headers: headers() });
    const pd = await pr.json().catch(() => ({}));
    const k = (pd.keys || {})[state.provider] || {};
    const hasKey = state.provider === "ollama" || state.provider === "openai_compatible" || k.has || k.needed === false;
    state.providerOk = !!state.model && state.provider && state.provider !== "mock" && !!hasKey && state.canEdit;
    if (!state.providerOk) {
      if (state.canEdit !== true) note.textContent = "Only the app owner can build on this app.";
      else if (!state.provider || state.provider === "mock") note.textContent = "The offline Demo has no AI model. Choose a real provider and model in Configuration first.";
      else if (!state.model) note.textContent = "Choose a model in Configuration first.";
      else note.textContent = "Save an API key for " + state.provider + " in Configuration first.";
      const go = el("a", null, "Open Configuration"); go.href = BASE + "/settings.html"; go.style.marginLeft = "6px";
      note.append(go);
    }
  } catch (e) { note.textContent = "Could not read model settings: " + e.message; state.providerOk = false; }
  updateStart();
}
function updateStart() { $("#buildStart").disabled = !(state.providerOk && $("#buildConsent").checked); }
$("#buildConsent").addEventListener("change", updateStart);

toSources.addEventListener("click", () => {
  state.brief = brief.value.trim();
  state.selected = suggest(state.brief);
  $("#sourcesRecap").textContent = "Your app: “" + (state.brief.length > 160 ? state.brief.slice(0, 157) + "…" : state.brief) + "”";
  paintWhy(); paintSources(); checkProvider();
  goStep(1);
});
$("#buildBack1").addEventListener("click", () => goStep(0));

/* Step 3: build */
const GROUP_LABEL = { config: "app settings", appearance: "design", prompt: "answer prompts", helper: "helper code", api: "API recommendations" };
const PART_LABEL = { "config:app": "app identity", "config:provider": "model connection", "config:sources": "sources", "config:budget": "usage limits", "config:retrieval": "retrieval", "config:memory": "memory", "config:prompt": "answer style", "api": "API recommendations" };
function partName(id) { if (PART_LABEL[id]) return PART_LABEL[id]; const g = id.split(":")[0]; if (id.startsWith("prompt:")) return "prompt: " + id.slice(7).replaceAll("_", " "); if (id.startsWith("appearance:")) return "design: " + id.slice(11).replaceAll("_", " "); if (id.startsWith("helper:")) return "helper: " + id.slice(7); return GROUP_LABEL[g] || id; }

function orbitHtml() {
  return '<svg viewBox="0 0 88 88" style="position:absolute;inset:0;width:88px;height:88px;transform:rotate(-90deg);animation:cc-orbit-spin 2.6s linear infinite"><circle fill="none" stroke="rgba(23,63,53,.14)" stroke-width="2.5" cx="44" cy="44" r="38"/><circle fill="none" stroke="#7fae3c" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="64 175" cx="44" cy="44" r="38" style="animation:cc-orbit-chase 1.5s cubic-bezier(.45,.15,.55,.85) infinite"/></svg><img src="' + BASE + '/icons/chatify.svg" alt="" style="width:46px;height:46px;border-radius:13px;animation:cc-orbit-breathe 2.2s ease-in-out infinite">';
}
$("#buildOrbit").innerHTML = orbitHtml();

function paintJob(d) {
  const counts = (d.parts || []).reduce((c, p) => { c[p.state] = (c[p.state] || 0) + 1; return c; }, {});
  const runningPart = (d.parts || []).find(p => p.state === "running");
  const phase = $("#buildPhase"), countsEl = $("#buildCounts"), statesEl = $("#buildStates");
  countsEl.textContent = (d.completed || 0) + " / " + (d.total || "?") + " areas ready · " + (d.calls || 0) + " model requests";
  statesEl.textContent = ["Ready " + (counts.done || 0), "Working " + (counts.running || 0), "Queued " + (counts.waiting || 0)].join(" · ") + ((counts.error || 0) ? " · Needs retry " + counts.error : "");
  state.running = d.state === "running";
  $("#buildCancel").hidden = !state.running;
  if (d.state === "running") {
    phase.textContent = runningPart ? "Drafting " + partName(runningPart.id) + "…" : (d.phase || "Shaping your app") + "…";
  } else if (d.state === "done") {
    $("#buildOrbit").innerHTML = "";
    const mark = el("span", "build-done-mark", "✓"); mark.setAttribute("aria-hidden", "true");
    $("#buildOrbit").append(mark);
    $("#progressTitle").textContent = "Your draft is ready";
    phase.textContent = "Review everything - nothing is saved until you confirm.";
    statesEl.textContent = "";
    const review = $("#buildReview"); review.hidden = false;
    review.onclick = () => { location.href = BASE + "/settings.html#build-draft=" + d.id; };
  } else if (d.state === "partial") {
    phase.textContent = "Some areas need a retry";
    $("#buildRetryWrap").hidden = false;
    const err = $("#buildError"); err.hidden = false;
    err.textContent = "Ready drafts are kept on this server. Retry finishes the remaining areas.";
  } else if (d.state === "cancelled") {
    phase.textContent = "Build cancelled. No files were saved.";
  }
}
async function poll() {
  clearTimeout(state.timer);
  try {
    const r = await fetch("/api/settings/build/job?id=" + encodeURIComponent(state.jobId), { headers: headers() });
    const d = await r.json();
    if (!r.ok) throw Error(d.error || "Build status unavailable");
    paintJob(d);
    if (d.state === "running") state.timer = setTimeout(poll, 1500);
  } catch (e) {
    $("#buildPhase").textContent = "Status check failed - the build may still be running.";
    const err = $("#buildError"); err.hidden = false; err.textContent = e.message + " Reopen this page to check again.";
  }
}
$("#buildStart").addEventListener("click", async () => {
  const btn = $("#buildStart"); btn.disabled = true;
  const names = state.selected.map(id => connById(id).name).join(", ");
  const plan = state.selected.length
    ? "\n\nEvidence plan confirmed by the user: " + names + ". Treat these as the chosen sources: recommend and configure exactly these connectors for this app, and do not propose unrelated sources."
    : "\n\nThe user skipped source selection. Propose sensible default sources for this app.";
  try {
    const d = await api("start", { selection: { provider: state.provider, model: state.model, base_url: "" }, brief: state.brief + plan, sections: SECTIONS_ALL, consent: true });
    state.jobId = d.id;
    goStep(2);
    paintJob(d);
    poll();
  } catch (e) {
    btn.disabled = false;
    const note = $("#buildProviderNote"); note.textContent = e.message;
  }
});
$("#buildCancel").addEventListener("click", async () => {
  const btn = $("#buildCancel"); btn.disabled = true;
  try { await api("cancel", { id: state.jobId }); $("#buildPhase").textContent = "Cancelling - in-flight model requests may still finish and cost money."; poll(); }
  catch (e) { const err = $("#buildError"); err.hidden = false; err.textContent = e.message; }
  finally { btn.disabled = false; }
});
$("#buildRetry").addEventListener("click", async () => {
  try { const d = await api("retry", { id: state.jobId }); $("#buildRetryWrap").hidden = true; const err = $("#buildError"); err.hidden = true; paintJob(d); poll(); }
  catch (e) { const err = $("#buildError"); err.hidden = false; err.textContent = e.message; }
});

/* resume a running build if the page is reopened with ?job= */
const m = (location.search || "").match(/[?&]job=([0-9a-f]{32})/);
if (m) { state.jobId = m[1]; goStep(2); poll(); }

/* boot veil */
window.addEventListener("load", () => { const b = document.getElementById("cc-boot"); if (b) { b.classList.add("cc-boot-out"); setTimeout(() => b.remove(), 300); } });
setTimeout(() => { const b = document.getElementById("cc-boot"); if (b) { b.classList.add("cc-boot-out"); setTimeout(() => b.remove(), 300); } }, 2500);
})();
