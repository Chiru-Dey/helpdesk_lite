<template>
  <div id="app" style="font-family: sans-serif;">
    <nav style="background: #f4f4f4; padding: 1rem; display: flex; gap: 1.5rem; align-items: center; border-bottom: 1px solid #ddd;">
      <router-link to="/" style="text-decoration: none; font-weight: bold; color: #333;">HelpDesk Lite</router-link>
      
      <template v-if="auth.user">
        <router-link to="/tickets" style="text-decoration: none; color: #555;">Tickets</router-link>
        <router-link to="/dashboard" v-if="hasRole('admin', 'agent')" style="text-decoration: none; color: #555;">Dashboard</router-link>
      </template>

      <div style="margin-left: auto; display: flex; gap: 1rem; align-items: center;">
        <template v-if="auth.user">
          <span style="color: #666;">Hello, {{ auth.user.name }}</span>
          <button @click="handleLogout" style="cursor: pointer;">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login" style="text-decoration: none; color: #0066cc;">Login</router-link>
          <router-link to="/register" style="text-decoration: none; color: #0066cc;">Register</router-link>
        </template>
      </div>
    </nav>
    <main style="padding: 2rem;">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

const hasRole = (...roles) => {
  if (!auth.user) return false
  return roles.some(role => auth.user.roles.some(r => r.name === role))
}

const handleLogout = async () => {
  await auth.logout()
  router.push('/login')
}
</script>