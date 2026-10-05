import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import TicketsView from '../views/TicketsView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/login', name: 'login', component: LoginView },
  { path: '/register', name: 'register', component: RegisterView },
  { 
    path: '/dashboard', 
    name: 'dashboard', 
    component: DashboardView,
    meta: { requiresAuth: true, roles: ['admin', 'agent'] }
  },
  { 
    path: '/tickets', 
    name: 'tickets', 
    component: TicketsView,
    meta: { requiresAuth: true }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from) => {
  const auth = useAuthStore()
  
  // If we don't have a user in state, try to fetch from cookie session
  if (!auth.user && !auth.loading) {
    await auth.fetchUser()
  }

  // If route requires auth and we have no user, redirect to login
  if (to.meta.requiresAuth && !auth.user) {
    return { name: 'login' }
  }

  // If route requires specific roles, check them
  if (to.meta.roles && auth.user) {
    const hasRole = to.meta.roles.some(role => 
      auth.user.roles.some(r => r.name === role)
    )
    if (!hasRole) {
      return { name: 'home' }
    }
  }
})

export default router