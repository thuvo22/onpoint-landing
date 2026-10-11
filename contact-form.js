/* Main contact form. Keep personal form data in the existing lead API only. */
(function () {
  var f = document.getElementById('estimateForm');
  if (!f) return;
  var msg = document.getElementById('estimateMsg'), btn = document.getElementById('estimateBtn');
  var service = document.getElementById('contactService');
  var inFlight = false, submitted = false;
  function timedFetch(url, options, milliseconds) {
    var controller = new AbortController(), timer;
    options = Object.assign({}, options, { signal: controller.signal });
    var deadline = new Promise(function (_, reject) {
      timer = setTimeout(function () { controller.abort(); reject(new Error('timeout')); }, milliseconds);
    });
    return Promise.race([fetch(url, options), deadline]).finally(function () { clearTimeout(timer); });
  }
  var serviceLabels = {
    bathroom: 'Full bathroom remodel', repairs: 'Drywall & interior repairs',
    painting: 'Painting', flooring: 'Flooring', other: 'Other residential project'
  };
  function budgetLabel(value) { return ({ under_20k: 'Under $20,000', '20k_30k': '$20,000 to $30,000', '30k_45k': '$30,000 to $45,000', '45k_plus': '$45,000 or more' })[value] || ''; }
  function validService(value) { return Object.prototype.hasOwnProperty.call(serviceLabels, value); }
  function buttonLabel() { return service.value === 'bathroom' ? 'Request my bathroom planning call' : 'Request my project quote'; }
  function updateService() {
    var bathroom = service.value === 'bathroom';
    document.getElementById('contactHeading').textContent = bathroom ? 'Start your bathroom remodel' : 'Tell us about your project';
    document.getElementById('contactIntro').textContent = bathroom
      ? 'Tell us about your bathroom, the changes you want, and your preferred timing. We will contact you to discuss the next step.'
      : (service.value ? 'Need help with drywall, painting, flooring or interior repairs? Tell us about the work so we can discuss a quote.' : 'Planning a bathroom remodel or need help with repairs? Choose your service and tell us what you have in mind.');
    document.getElementById('bathroomPlanningNote').hidden = !bathroom;
    var budgetField = document.getElementById('bathroomBudgetField');
    if (budgetField) budgetField.hidden = !bathroom;
    if (!bathroom && f.budget) f.budget.value = '';
    var repairNote = document.getElementById('repairMinimumNote');
    if (repairNote) repairNote.hidden = service.value !== 'repairs';
    f.message.placeholder = bathroom ? 'What would you change in your bathroom, and when would you like to begin?' : 'Describe your project and when you hope to get started.';
    btn.textContent = service.value ? buttonLabel() : 'Send my project request';
  }
  var requestedService = new URLSearchParams(location.search).get('service');
  if (validService(requestedService)) service.value = requestedService;
  service.addEventListener('change', updateService);
  updateService();
  function say(t, ok) {
    msg.textContent = t;
    msg.className = 'text-sm font-medium ' + (ok ? 'text-green-700' : 'text-red-600');
    msg.classList.remove('hidden');
  }
  var photos = [];
  var picker = document.getElementById('estimatePhotos');
  var grid = document.getElementById('photoGrid');
  var photoLabel = document.getElementById('photoLabel');
  picker.addEventListener('change', function () {
    Array.prototype.forEach.call(picker.files, function (file) {
      if (photos.length >= 20 || !/^image\//.test(file.type)) return;
      photos.push(file);
      var cell = document.createElement('div');
      cell.className = 'relative aspect-square rounded-lg overflow-hidden bg-gray-100';
      var img = document.createElement('img');
      img.className = 'w-full h-full object-cover';
      img.alt = 'Selected project photo';
      img.src = URL.createObjectURL(file);
      var x = document.createElement('button');
      x.type = 'button'; x.textContent = '\u00d7'; x.setAttribute('aria-label', 'Remove photo');
      x.className = 'absolute top-0 right-0 m-1 h-6 w-6 rounded-full bg-black/60 text-white text-sm leading-none';
      x.addEventListener('click', function () { photos.splice(photos.indexOf(file), 1); URL.revokeObjectURL(img.src); cell.remove(); count(); });
      cell.appendChild(img); cell.appendChild(x); grid.appendChild(cell);
    });
    picker.value = '';
    count();
  });
  function count() {
    photoLabel.textContent = photos.length ? photos.length + ' photo' + (photos.length === 1 ? '' : 's') + ' added, tap to add more' : 'Add photos of the space';
  }
  async function sendPhotos(baseUrl, acceptedMessage) {
    var sent = 0;
    for (var i = 0; i < photos.length; i++) {
      say(acceptedMessage + ' Sending photo ' + (i + 1) + ' of ' + photos.length + '...', true);
      var fd = new FormData();
      fd.append('file', photos[i], photos[i].name || 'photo.jpg');
      try {
        var r = await timedFetch(baseUrl + '/upload', { method: 'POST', body: fd }, 20000);
        if (r.ok) sent++;
      } catch (_) {}
    }
    return sent;
  }
  f.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (inFlight || submitted) return;
    var digits = (f.phone.value.match(/\d/g) || []).join('');
    if (!validService(service.value)) { say('Please choose the service you need.', false); service.focus(); return; }
    if (!f.name.value.trim()) { say('Please enter your name.', false); f.name.focus(); return; }
    if (digits.length < 10) { say('Please enter a 10 digit phone number.', false); f.phone.focus(); return; }
    if (!f.message.value.trim()) { say('Please tell us what you need done.', false); f.message.focus(); return; }
    var selectedService = service.value;
    inFlight = true;
    btn.disabled = true; btn.textContent = 'Checking number...';
    try {
      var pc = await timedFetch('https://api.onpointpros.io/leads/phone-check', { method: 'POST',
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ phone: digits }) }, 8000);
      var pv = pc.ok ? await pc.json() : { valid: true };
      if (!pv.valid) { inFlight = false; btn.disabled = false; btn.textContent = buttonLabel();
        say(pv.reason || 'Please enter a valid phone number we can reach you at.', false); f.phone.focus(); return; }
    } catch (_) {}
    btn.textContent = 'Sending...';
    try {
      var r = await fetch('https://api.onpointpros.io/leads/landing-list', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: f.name.value, phone: f.phone.value, zip: f.zip.value.trim(), date: '',
          list_text: '[Service: ' + serviceLabels[selectedService] + ']\n\n' + f.message.value +
            (window.OnPointMeasurement ? window.OnPointMeasurement.leadContext() : '') +
            (f.sms_consent.checked
              ? '\n\n[SMS consent: YES, checked on onpointprostx.com/contact.html]'
              : '\n\n[SMS consent: not given]'),
          budget: selectedService === 'bathroom' && f.budget ? budgetLabel(f.budget.value) : '', website: f.website.value, page: 'contact'
        })
      });
      if (r.status === 422) { var j = await r.json().catch(function(){return {};}); throw new Error(j.detail || 'invalid'); }
      if (!r.ok) throw new Error('failed');
      var res = await r.json().catch(function(){return {};});
      if (res.ok !== true) throw new Error('failed');
      submitted = true;
      var acceptedMessage = selectedService === 'bathroom' ? 'Thank you. We received your bathroom planning call request.' : 'Thank you. We received your project request.';
      btn.textContent = 'Request sent';
      say(acceptedMessage + ' We will contact you about the next step.', true);
      msg.focus();
      try { if (window.OnPointMeasurement) window.OnPointMeasurement.acceptedLead(res, 'contact_form', selectedService); } catch (_) {}
      var note = '';
      if (photos.length) {
        var sent = res.photo_url ? await sendPhotos(res.photo_url, acceptedMessage) : 0;
        note = sent === photos.length ? ' Your ' + (sent === 1 ? 'photo is' : sent + ' photos are') + ' in.'
             : ' ' + (photos.length - sent) + ' of your photos did not go through. You can text them to (469) 617-5235.';
      }
      grid.querySelectorAll('img').forEach(function (img) { URL.revokeObjectURL(img.src); });
      f.reset(); service.value = selectedService; updateService(); photos = []; grid.innerHTML = ''; count();
      say((selectedService === 'bathroom' ? 'Thank you. We will contact you about your bathroom planning call.' : 'Thank you. We will contact you about your project request.') + note + ' If you need us sooner, call (469) 617-5235.', true);
      msg.focus();
    } catch (err) {
      say(err && err.message && err.message !== 'failed' ? err.message
          : 'Something went wrong. Please call or text us at (469) 617-5235.', false);
    }
    inFlight = false;
    btn.disabled = submitted; btn.textContent = submitted ? 'Request sent' : buttonLabel();
  });
})();
