/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'telegram-blue': '#0088cc',
        'telegram-bg': '#f4f4f5',
      },
    },
  },
  plugins: [],
}
