/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        brand: {
          950: '#020817',
          900: '#0f172a',
          800: '#111827',
          700: '#1e293b',
          600: '#2563eb',
          500: '#38bdf8',
        },
      },
    },
  },
  plugins: [],
};
