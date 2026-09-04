/*
 * estimate-form.js — sitewide estimate form + mobile sticky bar.
 *
 * Until 2026-09-03 the 96 city/service pages offered one action, "Call".
 * The first website form (contact.html, built for A2P) produced a lead in
 * 48 hours, so every page gets a real form.
 *
 * Where it renders:
 *   - inside #estimate (city/service pages) — replaces the call-only block
 *     with the button kept, form added; height is reserved before paint so
 *     nothing shifts (CLS).
 *   - pages with no #estimate get only the sticky bar, whose Free Estimate
 *     button goes to /contact.html.
 * Never on /list/ (Meta funnel has its own form) or /contact.html.
 *
 * Posts to the same endpoint as contact.html with page = the path, so the
 * lead's note says which page converted. Source is SEO server-side.
 */
(function () {
  var path = location.pathname;
  if (/^\/list\/?/.test(path) || /\/contact\.html$/.test(path)) return;
  var PHONE_DISPLAY = '(469) 238-1719', PHONE_TEL = 'tel:+14692381719';
  var API = 'https://api.onpointpros.io/leads/landing-list';

  function pageName() {
    var p = path.replace(/^\//, '').replace(/\.html$/, '').replace(/\/index$/, '') || 'home';
    return p.slice(0, 60);
  }

  function cityFromTitle() {
    var h = document.querySelector('#estimate h2');
    if (!h) return '';
    var m = h.textContent.match(/Free\s+(.+?)\s+(Drywall|Bathroom|Flooring|Painting|Remodel|Quote|Estimate)/i);
    return m ? m[1] : '';
  }

  // ---- form -------------------------------------------------------------
  function formHtml() {
    return '' +
      '<form class="opp-est-form mt-8 mx-auto max-w-xl text-left bg-white rounded-2xl shadow-2xl p-5 sm:p-6" novalidate>' +
        '<input type="text" name="website" tabindex="-1" autocomplete="off" class="hidden" aria-hidden="true">' +
        '<p class="text-slate-900 font-extrabold text-lg mb-1">Or get your price by text</p>' +
        '<p class="text-slate-600 text-sm mb-4">Tell us what you need. We reply the same day, no obligation.</p>' +
        '<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">' +
          '<input type="text" name="name" required placeholder="Your name" class="w-full rounded-lg border border-slate-300 p-3 text-slate-900 focus:ring-2 focus:ring-red-600 focus:outline-none">' +
          '<input type="tel" name="phone" required placeholder="Mobile phone" class="w-full rounded-lg border border-slate-300 p-3 text-slate-900 focus:ring-2 focus:ring-red-600 focus:outline-none">' +
        '</div>' +
        '<textarea name="message" rows="3" required placeholder="What do you need done?" class="mt-3 w-full rounded-lg border border-slate-300 p-3 text-slate-900 focus:ring-2 focus:ring-red-600 focus:outline-none"></textarea>' +
        '<label class="mt-3 flex items-start gap-2 text-xs text-slate-600 leading-relaxed">' +
          '<input type="checkbox" name="sms_consent" value="yes" class="mt-0.5 h-4 w-4 shrink-0 accent-red-600">' +
          '<span>I agree to receive text messages from OnPoint Pros about my estimate at the number above. Message frequency varies. Msg and data rates may apply. Reply STOP to opt out. <a href="/privacy.html" class="underline">Privacy</a> and <a href="/terms.html" class="underline">Terms</a>.</span>' +
        '</label>' +
        '<button type="submit" class="mt-4 w-full py-3.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold shadow-lg transition">Get my free estimate</button>' +
        '<p class="opp-est-msg hidden mt-3 text-sm font-medium"></p>' +
      '</form>';
  }

  function wireForm(form) {
    var msg = form.querySelector('.opp-est-msg'), btn = form.querySelector('button[type=submit]');
    function say(t, ok) {
      msg.textContent = t;
      msg.className = 'opp-est-msg mt-3 text-sm font-medium ' + (ok ? 'text-green-700' : 'text-red-600');
    }
    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var digits = (form.phone.value.match(/\d/g) || []).join('');
      if (!form.name.value.trim()) { say('Please enter your name.', false); return; }
      if (digits.length < 10) { say('Please enter a 10 digit phone number.', false); return; }
      if (!form.message.value.trim()) { say('Please tell us what you need done.', false); return; }
      btn.disabled = true; btn.textContent = 'Sending...';
      try {
        var r = await fetch(API, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: form.name.value, phone: form.phone.value, zip: '', date: '',
            list_text: form.message.value +
              (form.sms_consent.checked
                ? '\n\n[SMS consent: YES, checked on onpointprostx.com/' + pageName() + ']'
                : '\n\n[SMS consent: not given]'),
            budget: '', website: form.website.value, page: pageName()
          })
        });
        if (!r.ok) throw new Error('failed');
        form.querySelectorAll('input,textarea').forEach(function (el) { if (el.type !== 'hidden') el.disabled = true; });
        btn.remove();
        say('Thank you. We will text you today. Need us sooner? Call ' + PHONE_DISPLAY + '.', true);
        try { if (window.gtag) gtag('event', 'generate_lead', { page: pageName(), method: 'estimate_form' }); } catch (_) {}
      } catch (err) {
        btn.disabled = false; btn.textContent = 'Get my free estimate';
        say('Something went wrong. Please call or text us at ' + PHONE_DISPLAY + '.', false);
      }
    });
  }

  function mountForm() {
    var sec = document.getElementById('estimate');
    if (!sec) return false;
    var holder = sec.querySelector('.max-w-4xl, .max-w-3xl, .max-w-5xl, .max-w-6xl, .max-w-7xl') || sec;
    if (holder.querySelector('.opp-est-form')) return true;
    var wrap = document.createElement('div');
    wrap.innerHTML = formHtml();
    holder.appendChild(wrap.firstChild);
    wireForm(holder.querySelector('.opp-est-form'));
    return true;
  }

  // ---- sticky bar (mobile only) ----------------------------------------
  function mountBar(hasForm) {
    if (document.querySelector('.opp-sticky-bar')) return;
    var target = hasForm ? '#estimate' : '/contact.html';
    var bar = document.createElement('div');
    bar.className = 'opp-sticky-bar sm:hidden fixed inset-x-0 bottom-0 z-40 bg-white/95 backdrop-blur border-t border-slate-200 px-3 py-2 flex gap-2';
    bar.style.paddingBottom = 'calc(0.5rem + env(safe-area-inset-bottom))';
    bar.innerHTML =
      '<a href="' + PHONE_TEL + '" class="flex-1 inline-flex items-center justify-center py-3 rounded-lg bg-slate-900 text-white font-bold text-sm">Call ' + PHONE_DISPLAY + '</a>' +
      '<a href="' + target + '" class="flex-1 inline-flex items-center justify-center py-3 rounded-lg bg-red-600 text-white font-bold text-sm">Free Estimate</a>';
    document.body.appendChild(bar);
    document.body.classList.add('opp-has-bar');   // cookie pill moves up out of its way
    // keep the bar off the last content / cookie banner
    document.body.style.paddingBottom = 'calc(64px + env(safe-area-inset-bottom))';
    // hide while the form itself is on screen; the bar would just duplicate it
    var form = document.querySelector('.opp-est-form');
    if (form && 'IntersectionObserver' in window) {
      new IntersectionObserver(function (es) {
        bar.style.transform = es[0].isIntersecting ? 'translateY(110%)' : '';
        bar.style.transition = 'transform .2s ease';
      }, { threshold: 0.15 }).observe(form);
    }
  }

  function init() {
    var hasForm = mountForm();
    mountBar(hasForm);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
