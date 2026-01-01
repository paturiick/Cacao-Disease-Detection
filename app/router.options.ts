import type { RouterConfig } from '@nuxt/schema'

export default <RouterConfig> {
  routes: (_routes) => [
    {
      name: 'home',
      path: '/',
      component: () => import('~/pages/index.vue')
    },
    
    {
      name: 'login',
      path: '/login',
      component: () => import('~/pages/login.vue')
    },

    {
      name: 'signup',
      path: '/signup',
      component: () => import('~/pages/signup.vue')
    },
    {
      name: 'mission-planner',
      path: '/mission-planner',
      component: () => import('~/pages/main-pages/mission-planner.vue')
    },
    {
      name: 'live-monitor',
      path: '/live-monitor',
      component: () => import('~/pages/main-pages/live-monitor.vue')
    },
    {
      name: 'map-geotagging',
      path: '/map-geotagging',
      component: () => import('~/pages/main-pages/map-geotagging.vue')
    }
  ],
}