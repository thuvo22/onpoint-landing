// The contact, legal, and campaign pages used Tailwind's default font stack.
// Keep their existing typography when replacing the browser-generated CSS.
const site = require('./tailwind.config.cjs');
module.exports = { ...site, theme: { extend: {} } };
