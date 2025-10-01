import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'Login',
      component: () => import('@/views/Login.vue'),
      meta: { title: 'Login' }
    },
    {
      path: '/',
      component: () => import('@/layouts/MainLayout.vue'),
      redirect: '/documents',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'documents',
          name: 'Documents',
          component: () => import('@/views/Documents.vue'),
          meta: { title: 'Knowledge Base', requiresAuth: true }
        },
        {
          path: 'search',
          name: 'Search',
          component: () => import('@/views/Search.vue'),
          meta: { title: 'Smart Search', requiresAuth: true }
        },
        {
          path: 'analysis',
          name: 'Analysis',
          component: () => import('@/views/Analysis.vue'),
          meta: { title: 'Data Analysis', requiresAuth: true }
        }
      ]
    }
  ]
})

// Route guard
router.beforeEach((to, from, next) => {
  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - XU-News-AI-RAG` : 'XU-News-AI-RAG'
  
  // Get token (re-read each time to ensure latest)
  const token = localStorage.getItem('access_token')
  
  // Whitelist paths (no authentication required)
  const whiteList = ['/login']
  
  if (token) {
    // Logged in
    if (to.path === '/login') {
      // If already logged in and accessing login page, redirect to home
      next('/documents')
    } else {
      next()
    }
  } else {
    // Not logged in
    if (whiteList.includes(to.path)) {
      // Whitelist paths allowed
      next()
    } else {
      // Pages requiring authentication redirect to login
      next('/login')
    }
  }
})

export default router

