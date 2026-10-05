<template>
  <div id="app">
    <nav class="navbar">
      <router-link to="/" class="navbar-brand">HelpDesk Lite</router-link>

      <template v-if="auth.user">
        <router-link to="/tickets">Tickets</router-link>
        <router-link v-if="hasRole('admin', 'agent')" to="/dashboard">Dashboard</router-link>
        <router-link v-if="hasRole('admin')" to="/admin/users">Users</router-link>
      </template>

      <div class="navbar-spacer"></div>

      <template v-if="auth.user">
        <span class="navbar-user">Hello, {{ auth.user.name }}</span>
        <button class="btn btn-secondary" @click="handleLogout">Logout</button>
      </template>
      <template v-else>
        <router-link to="/login">Login</router-link>
        <router-link to="/register">Register</router-link>
      </template>
    </nav>
    <main>
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