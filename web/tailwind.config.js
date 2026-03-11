/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./components/**/*.{js,vue,ts}",
    "./sections/**/*.{js,vue,ts}",
    "./pages/**/*.{js,vue,ts}",
    "./plugins/**/*.{js,ts}",
    "./app.vue",
    "./error.vue"
  ],
  theme: {
    extend: {
      fontFamily: {
        'poppins': ['Poppins', 'cursive', 'bold', 'semibold'],
        'inter': ['Inter', 'serif', 'bold', 'semibold'],
      },
      colors: {
        'background': '#E4EDD2',
        'primary': '#40623F',
        'secondary': '#4F4F4F',
        'tertiary': '#7C0505',
      },
    },
  },
  plugins: [],
}

