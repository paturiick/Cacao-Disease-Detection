// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  components: true,

  css: ['~/assets/css/tailwind.css', 'leaflet/dist/leaflet.css'],

  postcss: {
    plugins: {
      tailwindcss: { config: './tailwind.config.cjs' },
      autoprefixer: {},
    },
  },

  app:{
    head: {
      link: [
      {
        rel: 'preconnect',
        href: 'https://fonts.googleapis.com'
      },
      {
        rel: 'preconnect',
        href: 'https://fonts.gstatic.com',
        crossorigin: ''
      },
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Open+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,300;1,400;1,500;1,600;1,700;1,800&display=swap'
      }
      ]
    }
  }
})
