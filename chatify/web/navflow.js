/* Smooth page transitions between Chatify pages. Decoration only: if anything here fails,
   links keep working as plain links. */
(function () {
  try {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var root = document.documentElement;
    if (root.classList.contains("nav-in")) setTimeout(function () { root.classList.remove("nav-in"); }, 450);
    window.addEventListener("pageshow", function (e) {
      if (e.persisted) { root.classList.remove("nav-out"); root.classList.remove("nav-in"); }
    });
    if (reduce) return;
    document.addEventListener("click", function (e) {
      try {
        if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
        var a = e.target && e.target.closest ? e.target.closest("a[href]") : null;
        if (!a || a.target || a.hasAttribute("download")) return;
        var href = a.getAttribute("href") || "";
        if (!href || href.charAt(0) === "#") return;
        var url = new URL(href, location.href);
        if (url.protocol !== "http:" && url.protocol !== "https:") return;
        if (url.origin !== location.origin) return;
        if (url.pathname === location.pathname && url.search === location.search) return;
        e.preventDefault();
        try { sessionStorage.setItem("cc_nav", "1"); } catch (e2) { }
        root.classList.add("nav-out");
        setTimeout(function () { location.href = url.href; }, 150);
      } catch (e2) { /* fall through to a normal navigation */ }
    });
  } catch (e) { /* decoration only */ }
})();
