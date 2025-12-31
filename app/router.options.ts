import type { RouterConfig } from '@nuxt/schema'

// You can use this file to explicitly define routes
export default <RouterConfig> {
  routes: (_routes) => [
    // 1. The Home/Welcome Screen
    {
      name: 'home',
      path: '/',
      component: () => import('~/pages/index.vue')
    },
    
    // 2. The Login Screen
    {
      name: 'login',
      path: '/login',
      component: () => import('~/pages/login.vue')
    },

    // 3. The Sign Up Screen
    {
      name: 'signup',
      path: '/signup', // You can explicitly set the URL path here
      component: () => import('~/pages/signup.vue')
    },
    {
      name: 'mission-planner',
      path: '/mission-planner',
      component: () => import('~/pages/main pages/mission-planner.vue')
    }
  ],
}