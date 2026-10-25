const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../estimate-form.js'), 'utf8');

function render({ pathname, bodyService = '', sectionService = '', hasForm = false }) {
  const appended = [];
  const section = hasForm ? {
    getAttribute: () => sectionService,
    querySelector: selector => selector === '.opp-est-form' ? {} : null
  } : null;
  const document = {
    readyState: 'complete',
    getElementById: id => id === 'estimate' ? section : null,
    querySelector: () => null,
    createElement: () => ({ style: {}, innerHTML: '', className: '' }),
    body: {
      getAttribute: name => name === 'data-contact-service' ? bodyService : null,
      appendChild: node => appended.push(node),
      classList: { add() {} }, style: {}
    }
  };
  vm.runInNewContext(source, {
    location: { pathname }, document, window: {},
    fetch() { throw new Error('Rendering must not submit or validate a lead'); }
  });
  return appended[0]?.innerHTML || '';
}

for (const [service, pathname] of [
  ['flooring', '/blog/flooring-cost-dfw.html'],
  ['painting', '/blog/painting-cost-dfw.html'],
  ['repairs', '/blog/drywall-repair-cost-dfw.html']
]) {
  test(`${service} guide keeps the quote service selection`, () => {
    assert.match(render({ pathname, bodyService: service }), new RegExp('href="/contact.html\\?service=' + service + '"'));
  });
}
test('an inline city form remains the mobile quote destination', () => {
  assert.match(render({ pathname: '/drywall/plano.html', hasForm: true }), /href="#estimate"/);
});
test('section service takes priority over body declaration', () => {
  const html = render({ pathname: '/custom.html', hasForm: true, sectionService: 'bathroom', bodyService: 'flooring' });
  assert.match(html, /href="#estimate"/);
  assert.match(html, />Planning Call<\/a>/);
});
test('homepage keeps the service chooser', () => {
  assert.match(render({ pathname: '/', bodyService: 'flooring' }), /href="\/contact.html"/);
});
test('an undeclared general guide keeps the service chooser', () => {
  assert.match(render({ pathname: '/blog/permits-dfw.html' }), /href="\/contact.html"/);
});
test('unknown service declaration cannot inject an arbitrary destination', () => {
  const html = render({ pathname: '/blog/guide.html', bodyService: '\"><script>alert(1)</script>' });
  assert.match(html, /href="\/contact.html"/);
  assert.doesNotMatch(html, /<script>/);
});
test('existing service path inference still works without a declaration', () => {
  assert.match(render({ pathname: '/flooring/plano.html' }), /href="\/contact.html\?service=flooring"/);
});
for (const pathname of ['/contact.html', '/list/', '/list/index.html']) {
  test(`${pathname} retains its separate form flow`, () => {
    assert.equal(render({ pathname, bodyService: 'flooring' }), '');
  });
}
