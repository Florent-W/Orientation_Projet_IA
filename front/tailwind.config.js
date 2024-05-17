/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#004bff"
      },
      fontFamily: {
        ferveur: ["'Ferveur Compact'", "sans-serif"],
        montserrat: ["Montserrat", "sans-serif"],
      }
    },
  },
  plugins: [],
}

