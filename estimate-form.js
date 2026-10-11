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
 *   - pages with no #estimate get only the sticky bar, linking to contact.
 *   - the main bathroom hub (or #estimate[data-service="bathroom"]) starts
 *     a planning call; other service/city pages retain their estimate flow.
 * Never on /list/ (Meta funnel has its own form) or /contact.html.
 *
 * Posts to the same endpoint as contact.html with page = the path, so the
 * lead's note says which page converted. Source is SEO server-side.
 */
(function () {
  var path = location.pathname;
  if (/^\/list\/?/.test(path) || /\/contact\.html$/.test(path)) return;
  var PHONE_DISPLAY = '(469) 617-5235', PHONE_TEL = 'tel:+14696175235';
  var API = 'https://api.onpointpros.io/leads/landing-list';
  var isBathroom = false;
  var isHomepage = path === '/' || path === '/index.html';
  var serviceType = 'unspecified';
  var serviceLabels = {
    bathroom: 'Full bathroom remodel', repairs: 'Drywall & interior repairs',
    painting: 'Painting', flooring: 'Flooring', other: 'Other residential project'
  };

  function submitLabel() { return isBathroom ? 'Request my bathroom planning call' : 'Get my free estimate'; }

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


  // ---- phone validity (Twilio Lookup via our API) ------------------------
  // On blur: a mistyped or made-up number is caught before submit. Invalid
  // blocks the send; a landline is allowed but told we will call, not text.
  var PHONE_CHECK = 'https://api.onpointpros.io/leads/phone-check';
  var phoneVerdicts = {};
  async function checkPhone(raw) {
    var digits = (raw.match(/\d/g) || []).join('').slice(-10);
    if (digits.length < 10) return { valid: false, reason: 'Please enter a 10 digit phone number.' };
    if (phoneVerdicts[digits]) return phoneVerdicts[digits];
    try {
      var r = await fetch(PHONE_CHECK, { method: 'POST', headers: { 'Content-Type': 'application/json' },
                                         body: JSON.stringify({ phone: digits }) });
      var v = r.ok ? await r.json() : { valid: true, textable: true };
      phoneVerdicts[digits] = v;
      return v;
    } catch (_) { return { valid: true, textable: true }; }
  }
  function phoneHint(input) {
    var h = input.parentNode.querySelector('.opp-phone-hint');
    if (!h) { h = document.createElement('p'); h.className = 'opp-phone-hint text-xs mt-1'; input.insertAdjacentElement('afterend', h); }
    return h;
  }
  function wirePhone(input) {
    input.addEventListener('blur', async function () {
      var digits = (input.value.match(/\d/g) || []).join('');
      if (digits.length < 10) return;
      var v = await checkPhone(input.value), h = phoneHint(input);
      if (!v.valid) { h.textContent = v.reason || 'Please enter a valid phone number.'; h.className = 'opp-phone-hint text-xs mt-1 text-red-600'; input.classList.add('border-red-500'); }
      else if (v.textable === false) { h.textContent = 'This looks like a landline, so we will call you instead of texting.'; h.className = 'opp-phone-hint text-xs mt-1 text-amber-700'; input.classList.remove('border-red-500'); }
      else { h.textContent = ''; input.classList.remove('border-red-500'); }
    });
  }

  // ---- form -------------------------------------------------------------
  function formHtml() {
    var fieldClass = 'mt-1 w-full rounded-lg border border-slate-300 p-3 text-slate-900 focus:ring-2 focus:ring-red-600 focus:outline-none';
    return '' +
      '<form class="opp-est-form mt-8 mx-auto max-w-xl text-left bg-white rounded-2xl shadow-2xl p-5 sm:p-6" novalidate>' +
        '<input type="text" name="website" tabindex="-1" autocomplete="off" class="hidden" aria-hidden="true">' +
        '<p class="text-slate-900 font-extrabold text-lg mb-1">' + (isBathroom ? 'Tell us about your bathroom' : 'Or get your price by text') + '</p>' +
        '<p class="text-slate-600 text-sm mb-4">' + (isBathroom
          ? 'Full bathroom remodels start at $25,000. Begin with a planning call. If the project is a fit, a paid Blueprint planning session is next: usually $1,000, credited toward your remodel. We will explain the scope and fee before you book it.'
          : 'Tell us what you need. We reply the same day, no obligation.') + '</p>' +
        '<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">' +
          '<label class="block text-sm font-semibold text-slate-900">Name<input type="text" name="name" required autocomplete="name" placeholder="Your name" class="' + fieldClass + '"></label>' +
          '<label class="block text-sm font-semibold text-slate-900">Phone<input type="tel" name="phone" required autocomplete="tel" placeholder="Mobile phone" class="' + fieldClass + '"></label>' +
        '</div>' +
        (isBathroom ? '<label class="block mt-3 text-sm font-semibold text-slate-900">Project ZIP code (optional)<input type="text" name="zip" inputmode="numeric" autocomplete="postal-code" maxlength="10" placeholder="75002" class="' + fieldClass + '"></label>' : '') +
        '<label class="block mt-3 text-sm font-semibold text-slate-900">' + (isBathroom ? 'Project scope &amp; preferred timing' : 'What do you need done?') +
          '<textarea name="message" rows="3" required placeholder="' + (isBathroom ? 'What would you change in your bathroom, and when would you like to begin?' : 'Tell us about your project.') + '" class="' + fieldClass + '"></textarea></label>' +
        '<label class="mt-3 flex items-start gap-2 text-xs text-slate-600 leading-relaxed">' +
          '<input type="checkbox" name="sms_consent" value="yes" class="mt-0.5 h-4 w-4 shrink-0 accent-red-600">' +
          '<span>I agree to receive text messages from OnPoint Pros about my project request at the number above. Message frequency varies. Msg and data rates may apply. Reply STOP to opt out or HELP for help. Consent is optional and is not a condition of purchase. <a href="/privacy.html" class="underline">Privacy</a> and <a href="/terms.html" class="underline">Terms</a>.</span>' +
        '</label>' +
        '<button type="submit" class="mt-4 w-full py-3.5 rounded-lg bg-red-600 hover:bg-red-700 text-white font-bold shadow-lg transition">' + submitLabel() + '</button>' +
        '<p class="opp-est-msg hidden mt-3 text-sm font-medium" role="status" aria-live="polite" tabindex="-1"></p>' +
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
      if (!form.name.value.trim()) { say('Please enter your name.', false); form.name.focus(); return; }
      if (digits.length < 10) { say('Please enter a 10 digit phone number.', false); form.phone.focus(); return; }
      if (!form.message.value.trim()) { say('Please tell us what you need done.', false); form.message.focus(); return; }
      btn.disabled = true; btn.textContent = 'Checking number...';
      var verdict = await checkPhone(form.phone.value);
      if (!verdict.valid) {
        btn.disabled = false; btn.textContent = submitLabel();
        say(verdict.reason || 'Please enter a valid phone number we can reach you at.', false);
        form.phone.focus();
        return;
      }
      btn.textContent = 'Sending...';
      try {
        var r = await fetch(API, {
          method: 'POST', headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: form.name.value, phone: form.phone.value, zip: form.zip ? form.zip.value.trim() : '', date: '',
            list_text: (serviceLabels[serviceType] ? '[Service: ' + serviceLabels[serviceType] + ']\n\n' : '') + form.message.value +
              (form.sms_consent.checked
                ? '\n\n[SMS consent: YES, checked on onpointprostx.com/' + pageName() + ']'
                : '\n\n[SMS consent: not given]'),
            budget: '', website: form.website.value, page: pageName()
          })
        });
        if (r.status === 422) { var j = await r.json().catch(function(){return {};}); throw new Error(j.detail || 'invalid'); }
        if (!r.ok) throw new Error('failed');
        form.querySelectorAll('input,textarea').forEach(function (el) { if (el.type !== 'hidden') el.disabled = true; });
        btn.remove();
        say((isBathroom ? 'Thank you. We will contact you about your bathroom planning call.' : 'Thank you. We will contact you about your project request.') + ' Need us sooner? Call ' + PHONE_DISPLAY + '.', true);
        msg.focus();
        try { if (window.gtag) window.gtag('event', 'generate_lead', { page: pageName(), method: 'estimate_form', service_type: serviceType }); } catch (_) {}
      } catch (err) {
        btn.disabled = false; btn.textContent = submitLabel();
        say(err && err.message && err.message !== 'failed' ? err.message
            : 'Something went wrong. Please call or text us at ' + PHONE_DISPLAY + '.', false);
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
    wirePhone(holder.querySelector('.opp-est-form input[name=phone]'));
    return true;
  }

  // ---- sticky bar (mobile only) ----------------------------------------
  function mountBar(hasForm) {
    if (document.querySelector('.opp-sticky-bar')) return;
    var target = isHomepage ? '/contact.html' : (hasForm ? '#estimate' : '/contact.html');
    var actionLabel = isBathroom ? 'Planning Call' : (isHomepage ? 'Request a Quote' : 'Free Estimate');
    var bar = document.createElement('div');
    bar.className = 'opp-sticky-bar sm:hidden fixed inset-x-0 bottom-0 z-40 bg-white/95 backdrop-blur border-t border-slate-200 px-3 py-2 flex gap-2';
    bar.style.paddingBottom = 'calc(0.5rem + env(safe-area-inset-bottom))';
    bar.innerHTML =
      '<a href="' + PHONE_TEL + '" class="flex-1 inline-flex items-center justify-center py-3 rounded-lg bg-slate-900 text-white font-bold text-sm">Call ' + PHONE_DISPLAY + '</a>' +
      '<a href="' + target + '" class="flex-1 inline-flex items-center justify-center py-3 rounded-lg bg-red-600 text-white font-bold text-sm">' + actionLabel + '</a>';
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
    var sec = document.getElementById('estimate');
    var declaredService = sec ? sec.getAttribute('data-service') : '';
    isBathroom = path === '/services/bathroom-remodel.html' || declaredService === 'bathroom';
    serviceType = isBathroom ? 'bathroom' : (Object.prototype.hasOwnProperty.call(serviceLabels, declaredService) ? declaredService : 'unspecified');
    var hasForm = mountForm();
    mountBar(hasForm);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
