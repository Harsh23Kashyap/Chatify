/* Branded navigation + startup states. When a page transition waits on the network
   (the demo host can sleep), a branded veil covers the wait so it never reads as a
   blank screen. Decoration only: links keep working as plain links if anything fails. */
(() => {
  const root = document.documentElement;
  let veilTimer, veilNote;

  const dismissBoot = () => {
    const b = document.getElementById("cc-boot");
    if (!b) return;
    b.classList.add("cc-boot-out");
    setTimeout(() => b.remove(), 280);
  };

  const dropVeil = () => {
    clearTimeout(veilTimer);
    root.classList.remove("cc-page-leaving");
    const v = document.querySelector(".cc-veil");
    if (v) v.remove();
  };

  const ready = () => { dropVeil(); dismissBoot(); };

  const leave = label => {
    root.classList.add("cc-page-leaving");
    if (document.querySelector(".cc-veil")) return;
    let icon = "icons/chatify.svg";
    try { icon = new URL("icons/chatify.svg", location.href).href; } catch (e) { }
    const v = document.createElement("div");
    v.className = "cc-veil";
    v.setAttribute("role", "status");
    v.innerHTML = '<div class="cc-veil-card"><img class="cc-veil-logo" src="' + icon + '" alt=""><div class="cc-veil-name">Chatify</div><div class="cc-veil-bar"><i></i></div><div class="cc-veil-text"></div></div>';
    veilNote = v.querySelector(".cc-veil-text");
    veilNote.textContent = "Opening " + (label || "page") + "…";
    v.addEventListener("click", () => { dropVeil(); });
    root.appendChild(v);
    requestAnimationFrame(() => v.classList.add("cc-veil-show"));
    veilTimer = setTimeout(() => {
      if (veilNote && v.isConnected) veilNote.textContent = "Waking up the server - the first visit can take up to a minute.";
    }, 7000);
  };

  window.CCLoading = { ready, leave };

  window.addEventListener("pageshow", e => { if (e.persisted) dropVeil(); });

  document.addEventListener("click", e => {
    const a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
    if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || a.target || a.download) return;
    let u;
    try { u = new URL(a.getAttribute("href"), location.href); } catch (e2) { return; }
    if (u.origin !== location.origin) return;
    if (u.pathname === location.pathname && u.search === location.search) return;
    leave((a.textContent || "").trim());
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => setTimeout(dismissBoot, 120));
  } else {
    dismissBoot();
  }
})();
