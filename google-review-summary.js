/* Google-sourced business totals. Individual testimonials and schema are untouched. */
(function (root, factory) {
  if (typeof module === 'object' && module.exports) module.exports = factory;
  else factory(root).load();
}(typeof window !== 'undefined' ? window : this, function (env) {
  'use strict';
  var API = 'https://bathroom.onpointprostx.com/api/reviews';
  var MAX_AGE = 86400000;
  var expiry;
  function valid(data) {
    var age = data && typeof data.fetchedAt === 'string' ? Date.now() - Date.parse(data.fetchedAt) : NaN;
    return !!(data && data.status === 'ok' && Number.isFinite(data.rating) && data.rating >= 1 && data.rating <= 5 &&
      Number.isSafeInteger(data.count) && data.count > 0 && Number.isFinite(age) && age >= 0 && age < MAX_AGE);
  }
  function render(data) {
    env.clearTimeout(expiry);
    var fresh = valid(data);
    env.document.querySelectorAll('[data-google-review-summary]').forEach(function (node) {
      if (node.dataset.reviewFallback === undefined) node.dataset.reviewFallback = node.textContent;
      node.textContent = fresh ? data.rating.toFixed(1) + ' / 5 · ' + data.count.toLocaleString('en-US') + ' Google reviews' : node.dataset.reviewFallback;
    });
    // A page left open cannot keep displaying an expired total.
    if (fresh) expiry = env.setTimeout(function () { render(null); }, Math.max(0, MAX_AGE - (Date.now() - Date.parse(data.fetchedAt))));
    return fresh;
  }
  function load() {
    if (!env.document.querySelector('[data-google-review-summary]')) return Promise.resolve(false);
    var controller = typeof env.AbortController === 'function' ? new env.AbortController() : null;
    var timer;
    var request = Promise.resolve().then(function () {
      return env.fetch(API, { credentials: 'omit', signal: controller ? controller.signal : undefined });
    }).then(function (response) {
      if (!response.ok) throw new Error('Review totals unavailable');
      return response.json();
    });
    var timeout = new Promise(function (_, reject) {
      timer = env.setTimeout(function () {
        if (controller) controller.abort();
        reject(new Error('Review totals timed out'));
      }, 6000);
    });
    return Promise.race([request, timeout]).then(render, function () { return render(null); }).finally(function () { env.clearTimeout(timer); });
  }
  return Object.freeze({ load: load, render: render, valid: valid });
}));
