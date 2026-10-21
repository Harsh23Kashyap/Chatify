/* Branded replacement for native confirm/alert/prompt: same decisions, Chatify look.
   window.CCDialog.confirm(message, opts) -> Promise<boolean>
   window.CCDialog.alert(message, opts)   -> Promise<true>
   window.CCDialog.prompt(message, def, opts) -> Promise<string|null>
   opts: {title, okText, cancelText, danger, multiline, secret} */
(() => {
  if (window.CCDialog) return;
  const css = document.createElement("style");
  css.textContent = `
.cc-cdlg{border:none;padding:0;border-radius:18px;background:#fffdf7;color:#173f35;box-shadow:0 24px 70px rgba(14,43,32,.35);width:min(430px,92vw);font:15px/1.55 "DM Sans",system-ui,sans-serif}
.cc-cdlg::backdrop{background:rgba(14,43,32,.38);backdrop-filter:blur(2px)}
.cc-cdlg-card{display:grid;gap:12px;padding:24px 24px 20px}
.cc-cdlg-title{font:700 19px Fraunces,Georgia,serif;letter-spacing:-.01em;margin:0}
.cc-cdlg-msg{margin:0;color:#41544b;white-space:pre-wrap;word-break:break-word}
.cc-cdlg-input{font:15px "DM Sans",system-ui,sans-serif;color:#173f35;background:#f6f2e8;border:1px solid #ddd9c9;border-radius:10px;padding:10px 12px;width:100%;box-sizing:border-box}
.cc-cdlg-input:focus{outline:2px solid #7fae3c;outline-offset:1px}
textarea.cc-cdlg-input{min-height:110px;resize:vertical}
.cc-cdlg-actions{display:flex;justify-content:flex-end;gap:10px;margin-top:6px}
.cc-cdlg-btn{font:700 14px "DM Sans",system-ui,sans-serif;border-radius:11px;padding:10px 20px;cursor:pointer;border:1px solid transparent}
.cc-cdlg-ok{background:#173f35;color:#f4f8ee}
.cc-cdlg-ok:hover{background:#1f5345}
.cc-cdlg-ok.cc-cdlg-danger{background:#a03d2e}
.cc-cdlg-ok.cc-cdlg-danger:hover{background:#b04a38}
.cc-cdlg-cancel{background:transparent;color:#173f35;border-color:#c9c2ab}
.cc-cdlg-cancel:hover{background:#efe9d8}
html[data-theme=dark] .cc-cdlg{background:#182b23;color:#e8eee6}
html[data-theme=dark] .cc-cdlg-msg{color:#b9cabd}
html[data-theme=dark] .cc-cdlg-input{background:#101c17;border-color:#2c4438;color:#e8eee6}
html[data-theme=dark] .cc-cdlg-ok{background:#d7ef72;color:#173f35}
html[data-theme=dark] .cc-cdlg-ok:hover{background:#e4f79a}
html[data-theme=dark] .cc-cdlg-ok.cc-cdlg-danger{background:#b04a38;color:#f4f8ee}
html[data-theme=dark] .cc-cdlg-cancel{color:#e8eee6;border-color:#37524a}
html[data-theme=dark] .cc-cdlg-cancel:hover{background:#22392f}
@media(prefers-reduced-motion:no-preference){.cc-cdlg[open]{animation:cc-cdlg-in .18s cubic-bezier(.22,1,.36,1)}}
@keyframes cc-cdlg-in{from{opacity:0;transform:translateY(8px) scale(.98)}}`;
  document.head.appendChild(css);

  function open(opts) {
    return new Promise(resolve => {
      const d = document.createElement("dialog");
      d.className = "cc-cdlg";
      const card = document.createElement("div");
      card.className = "cc-cdlg-card";
      const title = document.createElement("h3");
      title.className = "cc-cdlg-title";
      title.textContent = opts.title || "Please confirm";
      const msg = document.createElement("p");
      msg.className = "cc-cdlg-msg";
      msg.textContent = opts.message;
      card.append(title, msg);
      let input = null;
      if (opts.kind === "prompt") {
        input = document.createElement(opts.multiline ? "textarea" : "input");
        input.className = "cc-cdlg-input";
        if (!opts.multiline) input.type = opts.secret ? "password" : "text";
        input.value = opts.def || "";
        card.appendChild(input);
      }
      const actions = document.createElement("div");
      actions.className = "cc-cdlg-actions";
      const done = val => { if (d.open) d.close(); resolve(val); };
      if (opts.kind === "confirm" || opts.kind === "prompt") {
        const cancel = document.createElement("button");
        cancel.type = "button";
        cancel.className = "cc-cdlg-btn cc-cdlg-cancel";
        cancel.textContent = opts.cancelText || "Cancel";
        cancel.onclick = () => done(opts.kind === "prompt" ? null : false);
        actions.appendChild(cancel);
      }
      const ok = document.createElement("button");
      ok.type = "button";
      ok.className = "cc-cdlg-btn cc-cdlg-ok" + (opts.danger ? " cc-cdlg-danger" : "");
      ok.textContent = opts.okText || (opts.kind === "alert" ? "OK" : "Continue");
      ok.onclick = () => done(opts.kind === "prompt" ? input.value : true);
      actions.appendChild(ok);
      card.appendChild(actions);
      d.appendChild(card);
      d.addEventListener("cancel", e => { e.preventDefault(); done(opts.kind === "prompt" ? null : opts.kind === "alert" ? true : false); });
      d.addEventListener("click", e => { if (e.target === d) done(opts.kind === "prompt" ? null : opts.kind === "alert" ? true : false); });
      if (opts.kind === "prompt" && !opts.multiline) {
        d.addEventListener("keydown", e => { if (e.key === "Enter" && document.activeElement === input) { e.preventDefault(); done(input.value); } });
      }
      document.body.appendChild(d);
      d.addEventListener("close", () => setTimeout(() => d.remove(), 240));
      d.showModal();
      (input || ok).focus();
      if (input && input.setSelectionRange) input.setSelectionRange(0, input.value.length);
    });
  }

  window.CCDialog = {
    confirm: (message, opts = {}) => open({ ...opts, kind: "confirm", message }),
    alert: (message, opts = {}) => open({ ...opts, kind: "alert", message }),
    prompt: (message, def = "", opts = {}) => open({ ...opts, kind: "prompt", message, def }),
  };
})();
