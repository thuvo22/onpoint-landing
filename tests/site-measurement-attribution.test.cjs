const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../site-measurement.js'), 'utf8');
function page(url, { consent = true, referrer = '', stored = null } = {}) {
  const data = new Map(stored ? [['opp_visit_v1', stored]] : []), scripts = [], listeners = {}, reads = [];
  const window = { OnPointConsent: { get: () => ({ statistics: consent }) }, addEventListener(name, handler) { listeners[name] = handler; } };
  const document = { title: 'OnPoint Pros', referrer, querySelector: () => null, getElementById: () => null,
    createElement: () => ({}), head: { appendChild: script => scripts.push(script) }, addEventListener() {} };
  const sessionStorage = { getItem: key => { reads.push(key); return data.get(key); }, setItem: (key, value) => data.set(key, value), removeItem: key => data.delete(key) };
  vm.runInNewContext(source, { window, document, location: new URL(url), URL, URLSearchParams, sessionStorage, Date });
  return { window, data, scripts, reads, setConsent(value) { consent = value; listeners['opp:consent'](); },
    events: name => (window.dataLayer || []).map(x => Array.from(x)).filter(x => x[0] === 'event' && x[1] === name),
    configs: () => (window.dataLayer || []).map(x => Array.from(x)).filter(x => x[0] === 'config') };
}
const base = 'https://onpointprostx.com/';
test('known GBP post tags remain distinct from Google organic', () => {
  const p = page(base + '?utm_source=gbp&utm_medium=post', { referrer: 'https://www.google.com/' });
  assert.match(p.window.OnPointMeasurement.leadContext(), /gbp \/ post/);
  const event = p.events('page_view')[0][2];
  assert.equal(event.entry_source, 'gbp'); assert.equal(event.entry_medium, 'post');
  assert.equal(event.page_location, base);
});
test('consented GBP source survives internal navigation and an accepted-lead event', () => {
  const first = page(base + '?utm_source=gbp&utm_medium=post');
  const second = page(base + 'contact.html?service=bathroom', { referrer: base, stored: first.data.get('opp_visit_v1') });
  assert.match(second.window.OnPointMeasurement.leadContext(), /gbp \/ post; entry path: \//);
  assert.equal(second.window.OnPointMeasurement.acceptedLead({ok: true, lead_id: 'private-mock'}, 'contact_form', 'bathroom'), true);
  assert.equal(second.window.OnPointMeasurement.acceptedLead({ok: true, lead_id: 'private-mock'}, 'contact_form', 'bathroom'), false);
  const events = second.events('generate_lead');
  assert.equal(events.length, 1); assert.equal(events[0][2].entry_source, 'gbp'); assert.equal(events[0][2].service_type, 'bathroom');
  assert(!JSON.stringify(events).includes('private-mock'));
});
test('without consent GBP context stays current-page only with no storage or analytics', () => {
  const p = page(base + '?utm_source=gbp&utm_medium=post', { consent: false });
  assert.match(p.window.OnPointMeasurement.leadContext(), /gbp \/ post/);
  assert.equal(p.data.size, 0); assert.equal(p.scripts.length, 0);
  assert.equal(p.window.OnPointMeasurement.acceptedLead({ok: true, lead_id: 'mock'}, 'contact_form', 'bathroom'), false);
  assert.equal(p.events('generate_lead').length, 0);
});
test('ordinary search and paid click-ID attribution keep their existing meanings', () => {
  const organic = page(base, { referrer: 'https://www.google.com/search?q=bathroom' });
  assert.match(organic.window.OnPointMeasurement.leadContext(), /google \/ organic/);
  for (const key of ['gclid', 'gbraid', 'wbraid']) {
    const paid = page(base + '?' + key + '=private-value');
    assert.match(paid.window.OnPointMeasurement.leadContext(), /google \/ cpc/);
    assert(!JSON.stringify(paid.window.dataLayer).includes('private-value'));
  }
});
test('arbitrary source/medium input is never copied to analytics or private context', () => {
  const p = page(base + '?utm_source=person%40example.test&utm_medium=private-note');
  assert.match(p.window.OnPointMeasurement.leadContext(), /direct \/ none/);
  assert(!JSON.stringify(p.window.dataLayer).includes('person@example.test'));
  assert(!p.window.OnPointMeasurement.leadContext().includes('private-note'));
  const known = page(base + '?utm_source=gbp&utm_medium=private-note');
  assert.match(known.window.OnPointMeasurement.leadContext(), /gbp \/ campaign/);
});
test('spam-style ok without persisted lead ID does not produce an accepted-lead event', () => {
  const p = page(base + '?utm_source=gbp&utm_medium=post');
  assert.equal(p.window.OnPointMeasurement.acceptedLead({ok:true},'contact_form','bathroom'),false);
  assert.equal(p.events('generate_lead').length,0);
});

const projects = [
  { source: 'facebook', medium: 'social', campaign: 'allen_bath_project_20261025', path: 'bathroom/allen.html' },
  { source: 'houzz', medium: 'referral', campaign: 'plano_bath_project_20261025', path: 'blog/plano-tile-shower-tub-project.html' }
];
function projectUrl(project) {
  return base + project.path + '?utm_source=' + project.source + '&utm_medium=' + project.medium + '&utm_campaign=' + project.campaign;
}
for (const project of projects) {
  test(project.source + ' approved project reaches analytics and private form context', () => {
    const p = page(projectUrl(project) + '&utm_content=private-person&fbclid=private-click#private-hash', {
      referrer: 'https://www.' + project.source + '.com/private-profile?private=detail'
    });
    const event = p.events('page_view')[0][2];
    assert.equal(event.entry_source, project.source);
    assert.equal(event.entry_medium, project.medium);
    assert.equal(event.entry_campaign, project.campaign);
    assert.equal(event.page_location, base + project.path);
    assert.equal(event.page_referrer, '');
    assert.equal(p.configs()[0][2].campaign_name, project.campaign);
    assert.match(p.window.OnPointMeasurement.leadContext(), new RegExp('campaign: ' + project.campaign));
    const captured = JSON.stringify([...p.data]) + JSON.stringify(p.window.dataLayer) + p.window.OnPointMeasurement.leadContext();
    for (const secret of ['private-person', 'private-click', 'private-hash', 'private-profile', 'private=detail']) assert(!captured.includes(secret));
  });
  test(project.source + ' campaign survives consented navigation to the contact form', () => {
    const first = page(projectUrl(project));
    const contact = page(base + 'contact.html?service=bathroom', { referrer: base + project.path, stored: first.data.get('opp_visit_v1') });
    assert.match(contact.window.OnPointMeasurement.leadContext(), new RegExp('campaign: ' + project.campaign));
    assert.equal(contact.window.OnPointMeasurement.acceptedLead({ ok: true, lead_id: 'mock-private-id' }, 'contact_form', 'bathroom'), true);
    assert.equal(contact.events('generate_lead')[0][2].entry_campaign, project.campaign);
    assert.equal(contact.events('generate_lead')[0][2].landing_path, '/' + project.path);
    assert(!JSON.stringify(contact.window.dataLayer).includes('mock-private-id'));
  });
}
test('Houzz referrer is recognized only on the exact host or its subdomains', () => {
  for (const host of ['houzz.com', 'www.houzz.com', 'm.houzz.com']) {
    const p = page(base, { referrer: 'https://' + host + '/project?private=detail' });
    assert.match(p.window.OnPointMeasurement.leadContext(), /houzz \/ referral/);
    assert.equal(p.events('page_view')[0][2].entry_campaign, '(not set)');
  }
  for (const host of ['nothouzz.com', 'houzz.com.example.test']) {
    const p = page(base, { referrer: 'https://' + host + '/' });
    assert.match(p.window.OnPointMeasurement.leadContext(), /referral \/ referral/);
  }
});
test('campaign requires an exact ID and matching source, medium and entry path', () => {
  const first = projects[0];
  const invalid = [
    projectUrl(first).replace(first.campaign, 'person%40example.test'),
    projectUrl(first).replace(first.campaign, '__proto__'),
    projectUrl(first).replace(first.campaign, first.campaign.toUpperCase()),
    projectUrl(first).replace('utm_source=facebook', 'utm_source=houzz'),
    projectUrl(first).replace('utm_medium=social', 'utm_medium=cpc'),
    projectUrl(first).replace(first.path, 'bathroom/plano.html'),
    base + first.path + '?utm_campaign=' + first.campaign
  ];
  for (const url of invalid) {
    const p = page(url, { referrer: 'https://www.facebook.com/' });
    assert.equal(p.events('page_view')[0][2].entry_campaign, '(not set)');
    assert(!p.window.OnPointMeasurement.leadContext().includes('; campaign:'));
    assert(!JSON.stringify(p.window.dataLayer).includes('person@example.test'));
  }
});
test('new tagged visit replaces the previous campaign and untagged external visits clear it', () => {
  const first = page(projectUrl(projects[0]));
  const houzz = page(projectUrl(projects[1]), { stored: first.data.get('opp_visit_v1') });
  assert.equal(houzz.events('page_view')[0][2].entry_campaign, projects[1].campaign);
  const ordinary = page(base + '?utm_source=facebook&utm_medium=social', { stored: houzz.data.get('opp_visit_v1') });
  assert.equal(ordinary.events('page_view')[0][2].entry_campaign, '(not set)');
  assert(!ordinary.window.OnPointMeasurement.leadContext().includes(projects[1].campaign));
  const organic = page(base, { referrer: 'https://www.google.com/search?q=private', stored: first.data.get('opp_visit_v1') });
  assert.equal(organic.events('page_view')[0][2].entry_source, 'google');
  assert.equal(organic.events('page_view')[0][2].entry_campaign, '(not set)');
});
test('stored metadata is rebuilt and unknown, mismatched or expired campaigns are discarded', () => {
  const first = page(projectUrl(projects[0]));
  const stored = JSON.parse(first.data.get('opp_visit_v1'));
  for (const changed of [
    { campaign: 'private-person@example.test' },
    { campaign: projects[1].campaign },
    { expires: Date.now() - 1 },
    { landing: '/bathroom/plano.html' }
  ]) {
    const p = page(base + 'contact.html', { referrer: base, stored: JSON.stringify({ ...stored, ...changed, unexpected: 'private-metadata' }) });
    assert.equal(p.events('page_view')[0][2].entry_campaign, '(not set)');
    assert(!JSON.stringify([...p.data]).includes('private-'));
    assert(!JSON.stringify(p.window.dataLayer).includes('private-'));
  }
});
test('no consent means no stored reads, campaign persistence or analytics; consent can be granted later', () => {
  const first = page(projectUrl(projects[0]));
  const p = page(projectUrl(projects[1]), { consent: false, stored: first.data.get('opp_visit_v1') });
  assert.equal(p.reads.length, 0); assert.equal(p.data.size, 0); assert.equal(p.scripts.length, 0);
  assert.equal(p.events('page_view').length, 0);
  // Existing private form context is current-page-only even without Statistics.
  assert.match(p.window.OnPointMeasurement.leadContext(), new RegExp(projects[1].campaign));
  const next = page(base + 'contact.html', { consent: false, referrer: base + projects[1].path });
  assert(!next.window.OnPointMeasurement.leadContext().includes('; campaign:'));
  p.setConsent(true);
  assert.equal(p.scripts.length, 1);
  assert.equal(p.events('page_view')[0][2].entry_campaign, projects[1].campaign);
});
test('withdrawing consent drops restored campaign and does not revive it on regrant', () => {
  const first = page(projectUrl(projects[0]));
  const p = page(base + 'contact.html', { referrer: base, stored: first.data.get('opp_visit_v1') });
  assert.match(p.window.OnPointMeasurement.leadContext(), new RegExp(projects[0].campaign));
  const beforeWithdrawal = p.window.dataLayer.length;
  p.setConsent(false);
  assert.equal(p.data.size, 0);
  assert.equal(p.window.dataLayer.length, beforeWithdrawal);
  assert(!p.window.OnPointMeasurement.leadContext().includes('; campaign:'));
  assert.equal(p.window.OnPointMeasurement.acceptedLead({ ok: true, lead_id: 'mock-opted-out' }, 'contact_form', 'bathroom'), false);
  p.setConsent(true);
  assert.equal(p.configs().at(-1)[2].campaign_name, '(not set)');
  assert.equal(p.scripts.length, 1);
});
test('localhost never loads analytics or stores attribution', () => {
  const p = page(projectUrl(projects[0]).replace('https://onpointprostx.com', 'http://localhost:8768'));
  assert.equal(p.data.size, 0); assert.equal(p.scripts.length, 0); assert.equal(p.reads.length, 0);
});

for (const kind of ['estimate', 'contact']) {
  test(kind + ' form includes approved campaign in mocked lead payload without sending form values to analytics', async () => {
    const project = kind === 'estimate' ? projects[0] : projects[1];
    const first = page(projectUrl(project));
    const url = kind === 'contact' ? base + 'contact.html?service=bathroom' : projectUrl(project);
    const p = kind === 'contact' ? page(url, { referrer: base + project.path, stored: first.data.get('opp_visit_v1') }) : first;
    const requests = [], handlers = {};
    const node = (value = '') => ({ value, textContent: '', style: {}, classList: { add() {}, remove() {} },
      addEventListener() {}, focus() {}, remove() {}, querySelectorAll: () => [], reset() {} });
    const message = node(), button = node(), selectedService = node('bathroom');
    const form = Object.assign(node(), {
      name: node('Private mock person'), phone: node('2025550100'), zip: node('75002'), message: node('Private mock project'),
      budget: node('30k_45k'), website: node(), sms_consent: { checked: false },
      addEventListener: (name, handler) => { handlers[name] = handler; },
      querySelector: selector => selector === '.opp-est-msg' ? message : button
    });
    let mounted = false;
    const section = {
      getAttribute: () => 'bathroom', appendChild: () => { mounted = true; },
      querySelector: selector => selector === '.opp-est-form' ? (mounted ? form : null)
        : selector === '.opp-est-form input[name=phone]' ? form.phone : null
    };
    const nodes = { estimateForm: form, estimateMsg: message, estimateBtn: button, contactService: selectedService, estimate: section };
    const document = {
      readyState: 'complete', getElementById: id => nodes[id] || (nodes[id] = node()),
      querySelector: selector => selector === '.opp-sticky-bar' ? {} : null,
      createElement: () => ({ firstChild: {} })
    };
    // No network API exists in this VM: each request is captured by this stub.
    const fetch = async (requestUrl, options) => {
      requests.push({ url: requestUrl, body: JSON.parse(options.body) });
      if (requestUrl.endsWith('/phone-check')) return { ok: true, json: async () => ({ valid: true }) };
      assert.equal(requestUrl, 'https://api.onpointpros.io/leads/landing-list');
      return { ok: true, json: async () => ({ ok: true, lead_id: 'private-local-mock-id' }) };
    };
    vm.runInNewContext(fs.readFileSync(require('node:path').join(__dirname, '../' + kind + '-form.js'), 'utf8'), {
      window: p.window, document, location: new URL(url), URL, URLSearchParams, fetch, AbortController, setTimeout, clearTimeout
    });
    assert.equal(typeof handlers.submit, 'function');
    await handlers.submit({ preventDefault() {} });
    const payload = requests.find(request => request.url.endsWith('/landing-list')).body;
    assert.match(payload.list_text, new RegExp('Visit context: ' + project.source + ' / ' + project.medium));
    assert.match(payload.list_text, new RegExp('campaign: ' + project.campaign));
    assert.match(payload.list_text, /SMS consent: not given/);
    assert.equal(p.events('generate_lead').length, 1);
    assert.equal(p.events('generate_lead')[0][2].entry_campaign, project.campaign);
    const analytics = JSON.stringify(p.window.dataLayer);
    for (const privateValue of ['Private mock person', '2025550100', 'Private mock project', 'private-local-mock-id']) assert(!analytics.includes(privateValue));
  });
}
