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
