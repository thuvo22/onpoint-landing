const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync(require('node:path').join(__dirname, '../site-measurement.js'), 'utf8');
function page(url, { consent = true, referrer = '', stored = null } = {}) {
  const data = new Map(stored ? [['opp_visit_v1', stored]] : []), scripts = [];
  const window = { OnPointConsent: { get: () => ({ statistics: consent }) }, addEventListener() {} };
  const document = { title: 'OnPoint Pros', referrer, querySelector: () => null, getElementById: () => null,
    createElement: () => ({}), head: { appendChild: script => scripts.push(script) }, addEventListener() {} };
  const sessionStorage = { getItem: key => data.get(key), setItem: (key, value) => data.set(key, value), removeItem: key => data.delete(key) };
  vm.runInNewContext(source, { window, document, location: new URL(url), URL, URLSearchParams, sessionStorage, Date });
  return { window, data, scripts, events: name => (window.dataLayer || []).map(x => Array.from(x)).filter(x => x[0] === 'event' && x[1] === name) };
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
