/* Primary website GA4. Verified OnPoint Pros stream 16108687638, 2026-10-11.
 * Basic consent mode: no Google library or analytics events before Statistics.
 * No form values, CRM lead IDs, raw URL queries, hashes, or click IDs go to GA4.
 * Only the explicitly approved project campaign IDs below can be retained.
 */
(function () {
  'use strict';
  if (window.OnPointMeasurement) return;
  var ID = 'G-2ZDYTR9YYK';
  var KEY = 'opp_visit_v1';
  var loaded = false, viewed = false, accepted = Object.create(null);
  var productionHost = /^(www\.)?onpointprostx\.com$/.test(location.hostname);
  var services = ['bathroom', 'repairs', 'painting', 'flooring', 'other', 'unspecified'];
  // Existing Business Profile posts use the fixed gbp / post tags. Keep the
  // allowlist explicit so free-form campaign values never enter analytics.
  var sourceNames = ['gbp', 'google', 'bing', 'yahoo', 'duckduckgo', 'facebook', 'instagram', 'nextdoor', 'youtube', 'chatgpt', 'perplexity', 'email', 'houzz'];
  var mediumNames = ['post', 'organic', 'cpc', 'ppc', 'paid_search', 'paid_social', 'social', 'email', 'referral'];
  var projectCampaigns = {
    allen_bath_project_20261025: { source: 'facebook', medium: 'social', landing: '/bathroom/allen.html' },
    plano_bath_project_20261025: { source: 'houzz', medium: 'referral', landing: '/blog/plano-tile-shower-tub-project.html' }
  };

  function allowed() {
    var consent = window.OnPointConsent && window.OnPointConsent.get();
    return productionHost && !!(consent && consent.statistics === true);
  }
  function safePath(value) {
    return /^\/[a-z0-9/_-]*(?:\.html)?$/i.test(value || '') ? value : '/';
  }
  function service(value) { return services.indexOf(value) >= 0 ? value : 'unspecified'; }
  function campaign(value, source, medium, landing) {
    if (typeof value !== 'string' || !Object.prototype.hasOwnProperty.call(projectCampaigns, value)) return '';
    var expected = projectCampaigns[value];
    return expected.source === source && expected.medium === medium && expected.landing === landing ? value : '';
  }
  function pageService() {
    var declared = document.querySelector('#estimate[data-service]');
    var selected = document.getElementById('contactService');
    if (selected && selected.value) return service(selected.value);
    if (declared) return service(declared.getAttribute('data-service'));
    if (/^\/bathroom\/|\/bathroom-remodel\.html$/.test(location.pathname)) return 'bathroom';
    if (/^\/drywall\/|\/drywall-repair\.html$/.test(location.pathname)) return 'repairs';
    if (/^\/painting\/|\/painting\.html$/.test(location.pathname)) return 'painting';
    if (/^\/flooring\/|\/flooring\.html$/.test(location.pathname)) return 'flooring';
    return 'unspecified';
  }
  function classifyVisit() {
    var q = new URLSearchParams(location.search);
    var source = (q.get('utm_source') || '').toLowerCase();
    var medium = (q.get('utm_medium') || '').toLowerCase();
    if (sourceNames.indexOf(source) >= 0) {
      medium = mediumNames.indexOf(medium) >= 0 ? medium : 'campaign';
      var landing = safePath(location.pathname);
      return { source: source, medium: medium, landing: landing,
        campaign: campaign(q.get('utm_campaign'), source, medium, landing) };
    }
    if (q.has('gclid') || q.has('gbraid') || q.has('wbraid')) return { source: 'google', medium: 'cpc', landing: safePath(location.pathname) };
    var host = '';
    try { host = new URL(document.referrer).hostname.toLowerCase(); } catch (_) {}
    if (!host) source = 'direct';
    else if (/(^|\.)onpointprostx\.com$/.test(host)) source = 'internal';
    else if (/(^|\.)google\.[a-z.]+$/.test(host)) source = 'google';
    else if (/(^|\.)bing\.com$/.test(host)) source = 'bing';
    else if (/(^|\.)search\.yahoo\.com$/.test(host)) source = 'yahoo';
    else if (/(^|\.)duckduckgo\.com$/.test(host)) source = 'duckduckgo';
    else if (/(^|\.)(chatgpt\.com|chat\.openai\.com)$/.test(host)) source = 'chatgpt';
    else if (/(^|\.)perplexity\.ai$/.test(host)) source = 'perplexity';
    else if (/(^|\.)houzz\.com$/.test(host)) source = 'houzz';
    else if (/(^|\.)(facebook\.com|instagram\.com|nextdoor\.com|youtube\.com)$/.test(host)) source = host.replace(/^.*\.(?=[^.]+\.com$)/, '').replace('.com', '');
    else source = 'referral';
    medium = ['google', 'bing', 'yahoo', 'duckduckgo'].indexOf(source) >= 0 ? 'organic' : (source === 'direct' ? 'none' : 'referral');
    return { source: source, medium: medium, landing: safePath(location.pathname) };
  }
  var visit = classifyVisit();
  function rememberVisit() {
    if (!allowed()) return;
    try {
      var previous = JSON.parse(sessionStorage.getItem(KEY) || 'null');
      if (previous && (sourceNames.concat(['direct', 'internal', 'referral'])).indexOf(previous.source) >= 0 &&
          (mediumNames.concat(['none', 'campaign'])).indexOf(previous.medium) >= 0 && safePath(previous.landing) === previous.landing &&
          typeof previous.expires === 'number' && previous.expires > Date.now()) {
        // An explicit new campaign takes precedence; internal navigation retains its entry source.
        if (visit.source === 'internal' || visit.source === 'direct') {
          // Rebuild from validated fields; never reuse arbitrary stored metadata.
          visit = { source: previous.source, medium: previous.medium, landing: previous.landing,
            campaign: campaign(previous.campaign, previous.source, previous.medium, previous.landing) };
        }
      }
      visit.expires = Date.now() + 30 * 60 * 1000;
      sessionStorage.setItem(KEY, JSON.stringify(visit));
    } catch (_) {}
  }
  function event(name, fields) {
    if (!allowed() || !loaded) return false;
    var params = {
      send_to: ID, site_section: 'primary_website', page_location: location.origin + safePath(location.pathname),
      page_referrer: '', page_title: document.title, service_type: pageService(),
      entry_source: visit.source, entry_medium: visit.medium, landing_path: visit.landing,
      entry_campaign: visit.campaign || '(not set)'
    };
    Object.keys(fields || {}).forEach(function (key) { params[key] = fields[key]; });
    window.gtag('event', name, params);
    return true;
  }
  function consentChanged() {
    window['ga-disable-' + ID] = !allowed();
    if (!allowed()) {
      try { sessionStorage.removeItem(KEY); } catch (_) {}
      // Withdrawal also drops any attribution restored from a previous page.
      visit = classifyVisit();
      return;
    }
    rememberVisit();
    var firstLoad = !loaded;
    if (!loaded) {
      loaded = true;
      window.dataLayer = window.dataLayer || [];
      window.gtag = window.gtag || function () { window.dataLayer.push(arguments); };
      window.gtag('js', new Date());
    }
    // Refresh sanitized campaign fields if Statistics is granted again after
    // withdrawal, so the loaded tag cannot retain a previous page's campaign.
    window.gtag('config', ID, {
      send_page_view: false, allow_google_signals: false, allow_ad_personalization_signals: false,
      campaign_source: visit.source === 'direct' ? '(direct)' : visit.source,
      campaign_medium: visit.medium === 'none' ? '(none)' : visit.medium,
      campaign_name: visit.campaign || '(not set)', campaign_id: '(not set)', campaign_term: '(not set)', campaign_content: '(not set)',
      page_location: location.origin + safePath(location.pathname), page_referrer: '', page_title: document.title
    });
    if (firstLoad) {
      var script = document.createElement('script');
      script.async = true;
      script.src = 'https://www.googletagmanager.com/gtag/js?id=' + ID;
      document.head.appendChild(script);
    }
    if (!viewed) { viewed = true; event('page_view'); }
  }
  window.OnPointMeasurement = {
    // lead_id validates server acceptance and deduplicates locally. It is never sent to GA4.
    acceptedLead: function (response, form, selectedService) {
      if (!response || response.ok !== true || typeof response.lead_id !== 'string' || !response.lead_id.trim()) return false;
      if (accepted[response.lead_id]) return false;
      accepted[response.lead_id] = true;
      return event('generate_lead', { form_id: form === 'contact_form' ? 'contact_form' : 'estimate_form', service_type: service(selectedService) });
    },
    // This non-sensitive context stays with the existing private project request.
    // No persistent attribution is read or written unless Statistics is allowed.
    leadContext: function () {
      return '\n\n[Visit context: ' + visit.source + ' / ' + visit.medium + '; entry path: ' + visit.landing +
        (visit.campaign ? '; campaign: ' + visit.campaign : '') + ']';
    }
  };
  document.addEventListener('click', function (e) {
    var link = e.target.closest ? e.target.closest('a[href]') : null;
    if (!link) return;
    var href = link.getAttribute('href') || '';
    var method = /^tel:/i.test(href) ? 'phone' : (/^sms:/i.test(href) ? 'text' : (/^mailto:/i.test(href) ? 'email' : ''));
    if (method) event('contact_click', { contact_method: method });
  });
  window.addEventListener('opp:consent', consentChanged);
  consentChanged();
})();
