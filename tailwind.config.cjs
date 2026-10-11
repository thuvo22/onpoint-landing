/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './*.html',
    './{services,dfw,bathroom,drywall,flooring,painting,blog,before,list}/**/*.html',
    './*.js',
  ],
  theme: {
    extend: {
      colors: { brand: { red: '#dc0f0f', redDark: '#a00b0b', gold: '#d49538' } },
      fontFamily: { sans: ['Montserrat', 'Helvetica', 'sans-serif'] },
    },
  },
  plugins: [],
};
