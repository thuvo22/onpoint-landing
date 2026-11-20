/*
 * phone-format.js — every tel input on the site formats as you type:
 * 4123456789 → (412) 345-6789. Handles paste, a leading 1 or +1, and
 * backspace without fighting the caret. Submit handlers already strip to
 * digits, so nothing downstream changes.
 */
(function () {
  function fmt(raw) {
    var d = (raw.match(/\d/g) || []).join('');
    // Country code: "+1 …", "1 (412)…", or 11 digits starting with 1.
    if (d[0] === '1' && (/^\s*\+?1[\s(.-]/.test(raw) || d.length === 11)) d = d.slice(1);
    d = d.slice(0, 10);
    if (!d) return '';
    if (d.length < 4) return '(' + d;
    if (d.length < 7) return '(' + d.slice(0, 3) + ') ' + d.slice(3);
    return '(' + d.slice(0, 3) + ') ' + d.slice(3, 6) + '-' + d.slice(6);
  }
  function wire(el) {
    if (el.dataset.oppFmt) return;
    el.dataset.oppFmt = '1';
    el.setAttribute('inputmode', 'tel');
    el.setAttribute('autocomplete', 'tel');
    if (!el.placeholder || /phone/i.test(el.placeholder)) el.placeholder = '(469) 555-0123';
    el.addEventListener('input', function (e) {
      // Let a backspace over a formatting character remove the digit before it.
      var before = el.value, pos = el.selectionStart;
      var next = fmt(before);
      if (e.inputType === 'deleteContentBackward' && before.length && /[^\d]$/.test(before.slice(0, pos))) {
        var digits = (before.slice(0, pos).match(/\d/g) || []).join('');
        next = fmt(digits.slice(0, -1) + before.slice(pos));
        el.value = next; el.setSelectionRange(next.length, next.length); return;
      }
      el.value = next;
      var atEnd = pos >= before.length;
      if (atEnd) el.setSelectionRange(next.length, next.length);
    });
    if (el.value) el.value = fmt(el.value);
  }
  function scan() { document.querySelectorAll('input[type="tel"]').forEach(wire); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', scan); else scan();
  // Forms injected later (estimate-form.js) get picked up too.
  new MutationObserver(scan).observe(document.documentElement, { childList: true, subtree: true });
})();

/*
 * Website call line (Thu 2026-11-19). Real visitors see and dial (469) 238-1719, so a call that starts on the
 * website can be told apart from a call that starts on the Google listing, which keeps (469) 617-5235.
 * The HTML, the schema and llms.txt keep 617-5235: that is the number Google, Bing, AI crawlers and the
 * directories read, so search engines and other automated readers are left alone here.
 * Colony pages carry their own number and are not touched.
 */
(function () {
  var ua = (navigator.userAgent || '').toLowerCase();
  var AUTOMATED = /bot\b|bot\/|crawl|spider|slurp|inspectiontool|googleother|google-extended|google page renderer|mediapartners|feedfetcher|lighthouse|headless|pagespeed|gtmetrix|pingdom|facebookexternalhit|whatsapp|preview|oai-searchbot|chatgpt-user|gptbot|claude|anthropic|perplexity|ccbot|bytespider|amazonbot|duckassist|semrush|ahrefs|dataforseo|python|curl|wget/;
  if (navigator.webdriver || AUTOMATED.test(ua)) return;
  var LISTING_DIGITS = '4696175235', SITE_E164 = '+14692381719';
  var SKIP = /^(SCRIPT|STYLE|NOSCRIPT|TEXTAREA)$/;
  function fixText(node) {
    if (node.nodeValue.indexOf('617-5235') === -1) return;
    var parent = node.parentNode;
    if (parent && SKIP.test(parent.nodeName)) return;
    node.nodeValue = node.nodeValue.replace(/\(469\)\s?617-5235/g, '(469) 238-1719').replace(/469-617-5235/g, '469-238-1719');
  }
  function fix(root) {
    if (!root) return;
    if (root.nodeType === 3) { fixText(root); return; }
    if (root.nodeType !== 1 && root.nodeType !== 9) return;
    if (root.nodeType === 1 && SKIP.test(root.nodeName)) return;
    var links = root.querySelectorAll('a[href^="tel:"], a[href^="sms:"]'), i;
    if (root.nodeType === 1 && root.matches && root.matches('a[href^="tel:"], a[href^="sms:"]')) links = [root].concat([].slice.call(links));
    for (i = 0; i < links.length; i++) {
      var href = links[i].getAttribute('href') || '';
      if (href.replace(/\D/g, '').indexOf(LISTING_DIGITS) !== -1) links[i].setAttribute('href', href.replace(/^(tel|sms):[^?&;]*/i, '$1:' + SITE_E164));
    }
    var labelled = root.querySelectorAll('[aria-label*="617-5235"], [title*="617-5235"]');
    for (i = 0; i < labelled.length; i++) {
      ['aria-label', 'title'].forEach(function (name) {
        var v = labelled[i].getAttribute(name);
        if (v && v.indexOf('617-5235') !== -1) labelled[i].setAttribute(name, v.replace(/\(469\)\s?617-5235/g, '(469) 238-1719').replace(/469-617-5235/g, '469-238-1719'));
      });
    }
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null), n, hits = [];
    while ((n = walker.nextNode())) if (n.nodeValue.indexOf('617-5235') !== -1) hits.push(n);
    for (i = 0; i < hits.length; i++) fixText(hits[i]);
  }
  function start() {
    fix(document.body);
    // Content added later (the estimate form, the review summary) is corrected as it arrives.
    new MutationObserver(function (records) {
      for (var r = 0; r < records.length; r++) for (var a = 0; a < records[r].addedNodes.length; a++) fix(records[r].addedNodes[a]);
    }).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
})();
