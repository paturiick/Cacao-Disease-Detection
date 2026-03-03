/** @type {import('tailwindcss').Config} */
module.exports = {
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
        // Open Sans is now the project-wide font; legacy class names also resolve to it
        'sans':       ['"Open Sans"', 'sans-serif'],
        'open-sans':  ['"Open Sans"', 'sans-serif'],
        'inter':      ['"Open Sans"', 'sans-serif'],
        'poppins':    ['"Open Sans"', 'sans-serif'],
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
