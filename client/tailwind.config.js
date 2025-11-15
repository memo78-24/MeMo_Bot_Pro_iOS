/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Opera GX Gaming Theme
        'gx-dark': '#0d0d10',
        'gx-card': '#1a1a1e',
        'gx-card-light': '#25252b',
        'gx-pink': '#FF0050',
        'gx-pink-bright': '#FF3377',
        'gx-pink-dark': '#D10042',
        'gx-text': '#e8e8e8',
        'gx-text-muted': '#a8a8a8',
      },
    },
  },
  plugins: [],
}
