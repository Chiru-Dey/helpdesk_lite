<template>
  <div class="auth-card">
    <h1>Login</h1>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="email">Email</label>
        <input id="email" v-model.trim="email" type="email" required autocomplete="email" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" required autocomplete="current-password" />
      </div>

      <button class="btn" type="submit" :disabled="submitting">
        {{ submitting ? 'Logging in...' : 'Login' }}
      </button>
    </form>

    <p class="auth-footer">
      Don't have an account?
      <router-link to="/register">Register here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const errorMessage = ref('')
const submitting = ref(false)

const handleLogin = async () => {
  errorMessage.value = ''
  submitting.value = true

  try {
    await auth.login(email.value, password.value)

    const roles = auth.user.roles.map((role) => role.name)

    if (roles.includes('admin') || roles.includes('agent')) {
      router.push('/dashboard')
    } else {
      router.push('/tickets')
    }
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error || 'Login failed. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>