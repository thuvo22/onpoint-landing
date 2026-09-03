/*
 * OnPoint Pros cookie consent.
 *
 * Self-hosted, no third-party CMP, no external request. Drives Google Consent
 * Mode v2 so Google Ads / GA4 receive a real signal the moment tags are added.
 *
 * Categories map to Consent Mode signals:
 *   Necessary   -> security_storage                     (always granted)
 *   Preferences -> functionality_storage, personalization_storage
 *   Statistics  -> analytics_storage
 *   Marketing   -> ad_storage, ad_user_data, ad_personalization
 *
 * House style: no dash punctuation in customer-facing copy, no emoji.
 */
(function () {
  "use strict";

  var KEY = "opp_consent_v1";
  var CATS = ["necessary", "preferences", "statistics", "marketing"];

  // ---- Consent Mode: deny by default, before any tag can fire ----------
  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  function pushConsent(state) {
    gtag("consent", state.__mode || "update", {
      security_storage: "granted",
      functionality_storage: state.preferences ? "granted" : "denied",
      personalization_storage: state.preferences ? "granted" : "denied",
      analytics_storage: state.statistics ? "granted" : "denied",
      ad_storage: state.marketing ? "granted" : "denied",
      ad_user_data: state.marketing ? "granted" : "denied",
      ad_personalization: state.marketing ? "granted" : "denied"
    });
  }

  function load() {
    try {
      var raw = localStorage.getItem(KEY);
      return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
  }

  function save(state) {
    try { localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) {}
  }

  function newId() {
    var bytes = new Uint8Array(32);
    (window.crypto || window.msCrypto).getRandomValues(bytes);
    var bin = "";
    for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
    return btoa(bin);
  }

  function stamp() {
    try {
      return new Date().toLocaleString("en-US", {
        month: "short", day: "numeric", year: "numeric",
        hour: "numeric", minute: "2-digit", second: "2-digit",
        timeZoneName: "short"
      });
    } catch (e) { return new Date().toISOString(); }
  }

  var saved = load();
  // Default denied on a first visit. Runs before tags so nothing leaks.
  pushConsent(saved ? saved : { __mode: "default" });

  // ---- styles ----------------------------------------------------------
  var css = document.createElement("style");
  css.textContent = [
    ".opp-cc,.opp-cc *{box-sizing:border-box}",
    ".opp-cc{position:fixed;z-index:2147483000;font-family:ui-sans-serif,system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif}",
    ".opp-cc-bar{left:0;right:0;bottom:0;background:#0f172a;color:#fff;padding:18px 20px;box-shadow:0 -6px 24px rgba(0,0,0,.25)}",
    ".opp-cc-inner{max-width:1100px;margin:0 auto;display:flex;gap:18px;align-items:center;flex-wrap:wrap}",
    ".opp-cc-copy{flex:1 1 380px;font-size:14px;line-height:1.55;color:#e2e8f0}",
    ".opp-cc-copy b{color:#fff}",
    ".opp-cc-actions{display:flex;gap:10px;flex-wrap:wrap}",
    ".opp-cc-btn{border:0;border-radius:10px;padding:11px 18px;font-size:14px;font-weight:700;cursor:pointer;font-family:inherit}",
    ".opp-cc-accept{background:#dc2626;color:#fff}",
    ".opp-cc-accept:hover{background:#b91c1c}",
    ".opp-cc-reject{background:#fff;color:#0f172a}",
    ".opp-cc-reject:hover{background:#e2e8f0}",
    ".opp-cc-link{background:transparent;color:#cbd5e1;text-decoration:underline;padding:11px 6px}",
    ".opp-cc-link:hover{color:#fff}",
    ".opp-cc-scrim{inset:0;background:rgba(2,6,23,.6);display:flex;align-items:center;justify-content:center;padding:18px}",
    ".opp-cc-panel{background:#0f172a;color:#fff;border-radius:16px;width:100%;max-width:430px;max-height:88vh;overflow:auto;box-shadow:0 24px 60px rgba(0,0,0,.5)}",
    ".opp-cc-head{display:flex;align-items:center;justify-content:space-between;padding:18px 20px;border-bottom:1px solid #1e293b}",
    ".opp-cc-head h2{margin:0;font-size:17px;font-weight:700}",
    ".opp-cc-x{background:transparent;border:0;color:#94a3b8;font-size:22px;line-height:1;cursor:pointer;padding:4px 8px}",
    ".opp-cc-x:hover{color:#fff}",
    ".opp-cc-body{padding:18px 20px}",
    ".opp-cc-sub{margin:0 0 14px;font-size:14px;font-weight:700}",
    ".opp-cc-row{display:flex;align-items:flex-start;gap:12px;padding:11px 0}",
    ".opp-cc-row label{font-size:14px;font-weight:600;cursor:pointer}",
    ".opp-cc-row p{margin:3px 0 0;font-size:12.5px;line-height:1.5;color:#94a3b8}",
    ".opp-cc-row input{margin-top:3px;width:17px;height:17px;accent-color:#dc2626;cursor:pointer}",
    ".opp-cc-row input:disabled{cursor:not-allowed;opacity:.65}",
    ".opp-cc-toggle{background:transparent;border:0;color:#cbd5e1;font-size:13px;font-weight:600;cursor:pointer;padding:10px 0;display:flex;align-items:center;gap:6px;font-family:inherit}",
    ".opp-cc-toggle:hover{color:#fff}",
    ".opp-cc-details{border-top:1px solid #1e293b;margin-top:6px;padding-top:14px;font-size:12.5px;color:#94a3b8;line-height:1.6}",
    ".opp-cc-details b{color:#e2e8f0;display:block;margin-bottom:2px;font-size:12.5px}",
    ".opp-cc-details code{word-break:break-all;font-size:11.5px;color:#cbd5e1}",
    ".opp-cc-foot{border-top:1px solid #1e293b;padding:16px 20px;display:flex;flex-direction:column;gap:10px}",
    ".opp-cc-foot .opp-cc-btn{width:100%}",
    ".opp-cc-open{position:fixed;left:14px;bottom:14px;z-index:2147482000;background:#0f172a;color:#fff;border:0;border-radius:999px;padding:9px 14px;font-size:12px;font-weight:600;cursor:pointer;opacity:.82;font-family:inherit}",
    ".opp-cc-open:hover{opacity:1}",
    "@media (max-width:640px){.opp-cc-actions{width:100%}.opp-cc-actions .opp-cc-btn{flex:1 1 auto}}"
  ].join("");
  document.head.appendChild(css);

  var LABELS = {
    necessary: ["Necessary", "Required for the site to work, such as security and remembering your form entries. These cannot be switched off."],
    preferences: ["Preferences", "Remembers choices you make, like your area or a form you already started."],
    statistics: ["Statistics", "Tells us which pages people actually read, so we know what is worth writing."],
    marketing: ["Marketing", "Helps us understand how people find us so we can reach the right homeowners."]
  };

  var root = null;

  function close() {
    if (root) { root.remove(); root = null; }
    ensureReopen();
  }

  function apply(state, mode) {
    state.__mode = mode || "update";
    state.necessary = true;
    if (!state.id) state.id = newId();
    if (!state.date) state.date = stamp();
    save(state);
    pushConsent(state);
    saved = state;
  }

  function acceptAll() {
    apply({ necessary: true, preferences: true, statistics: true, marketing: true });
    close();
  }

  function rejectAll() {
    apply({ necessary: true, preferences: false, statistics: false, marketing: false });
    close();
  }

  function el(tag, cls, html) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }

  // ---- settings panel --------------------------------------------------
  function openPanel() {
    if (root) root.remove();
    var cur = load() || { necessary: true, preferences: false, statistics: false, marketing: false };

    root = el("div", "opp-cc opp-cc-scrim");
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-modal", "true");
    root.setAttribute("aria-label", "Cookie settings");

    var panel = el("div", "opp-cc-panel");

    var head = el("div", "opp-cc-head");
    head.appendChild(el("h2", null, "Cookie settings"));
    var x = el("button", "opp-cc-x", "&times;");
    x.setAttribute("aria-label", "Close cookie settings");
    x.onclick = close;
    head.appendChild(x);
    panel.appendChild(head);

    var body = el("div", "opp-cc-body");
    body.appendChild(el("p", "opp-cc-sub", cur.id ? "Your current state" : "Choose what you allow"));

    var boxes = {};
    CATS.forEach(function (c) {
      var row = el("div", "opp-cc-row");
      var inp = document.createElement("input");
      inp.type = "checkbox";
      inp.id = "opp-cc-" + c;
      inp.checked = c === "necessary" ? true : !!cur[c];
      inp.disabled = c === "necessary";
      boxes[c] = inp;
      var wrap = el("div");
      var lab = document.createElement("label");
      lab.setAttribute("for", inp.id);
      lab.textContent = LABELS[c][0];
      wrap.appendChild(lab);
      wrap.appendChild(el("p", null, LABELS[c][1]));
      row.appendChild(inp);
      row.appendChild(wrap);
      body.appendChild(row);
    });

    if (cur.id) {
      var toggle = el("button", "opp-cc-toggle", "Show details");
      var details = el("div", "opp-cc-details");
      details.style.display = "none";
      details.innerHTML =
        "<b>Consent date</b>" + (cur.date || "") +
        "<div style='height:10px'></div><b>Your consent ID</b><code>" + (cur.id || "") + "</code>";
      toggle.onclick = function () {
        var open = details.style.display !== "none";
        details.style.display = open ? "none" : "block";
        toggle.textContent = open ? "Show details" : "Hide details";
      };
      body.appendChild(toggle);
      body.appendChild(details);
    }
    panel.appendChild(body);

    var foot = el("div", "opp-cc-foot");
    var saveBtn = el("button", "opp-cc-btn opp-cc-accept", cur.id ? "Change your consent" : "Save my choices");
    saveBtn.onclick = function () {
      apply({
        necessary: true,
        preferences: boxes.preferences.checked,
        statistics: boxes.statistics.checked,
        marketing: boxes.marketing.checked
      });
      close();
    };
    foot.appendChild(saveBtn);

    if (cur.id) {
      var withdraw = el("button", "opp-cc-btn opp-cc-reject", "Withdraw your consent");
      withdraw.onclick = rejectAll;
      foot.appendChild(withdraw);
    } else {
      var all = el("button", "opp-cc-btn opp-cc-reject", "Allow all");
      all.onclick = acceptAll;
      foot.appendChild(all);
    }
    panel.appendChild(foot);

    root.appendChild(panel);
    root.addEventListener("click", function (e) { if (e.target === root) close(); });
    document.body.appendChild(root);
  }

  // ---- first-visit bar -------------------------------------------------
  function openBar() {
    if (root) root.remove();
    root = el("div", "opp-cc opp-cc-bar");
    root.setAttribute("role", "region");
    root.setAttribute("aria-label", "Cookie notice");

    var inner = el("div", "opp-cc-inner");
    inner.appendChild(el("div", "opp-cc-copy",
      "<b>We use cookies.</b> Some keep the site working. Others help us understand how people use it so we can make it better. " +
      "You choose what we may use. Read our <a href='/privacy.html' style='color:#fff'>Privacy Policy</a>."));

    var actions = el("div", "opp-cc-actions");
    var b1 = el("button", "opp-cc-btn opp-cc-accept", "Allow all");
    b1.onclick = acceptAll;
    var b2 = el("button", "opp-cc-btn opp-cc-reject", "Necessary only");
    b2.onclick = rejectAll;
    var b3 = el("button", "opp-cc-btn opp-cc-link", "Let me choose");
    b3.onclick = openPanel;
    actions.appendChild(b1); actions.appendChild(b2); actions.appendChild(b3);
    inner.appendChild(actions);
    root.appendChild(inner);
    document.body.appendChild(root);
  }

  function ensureReopen() {
    if (!load()) return;
    if (document.querySelector(".opp-cc-open")) return;
    var b = el("button", "opp-cc-open", "Cookie settings");
    b.onclick = openPanel;
    document.body.appendChild(b);
  }

  // Any element with data-cookie-settings reopens the panel (footer links).
  document.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-cookie-settings]") : null;
    if (t) { e.preventDefault(); openPanel(); }
  });

  window.OnPointConsent = { open: openPanel, get: load };

  function boot() {
    if (!load()) openBar(); else ensureReopen();
  }
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else { boot(); }
})();
