<template>
  <div class="auth-card">
    <h1>Register</h1>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label for="name">Full Name</label>
        <input id="name" v-model.trim="name" type="text" required autocomplete="name" />
      </div>

      <div class="form-group">
        <label for="email">Email</label>
        <input id="email" v-model.trim="email" type="email" required autocomplete="email" />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input id="password" v-model="password" type="password" required minlength="8" autocomplete="new-password" />
      </div>

      <div class="form-group">
        <label for="confirmPassword">Confirm Password</label>
        <input id="confirmPassword" v-model="confirmPassword" type="password" required minlength="8" autocomplete="new-password" />
      </div>

      <button class="btn" type="submit" :disabled="submitting">
        {{ submitting ? 'Creating account...' : 'Register' }}
      </button>
    </form>

    <p class="auth-footer">
      Already have an account?
      <router-link to="/login">Login here</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()

const name = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const errorMessage = ref('')
const submitting = ref(false)

const handleRegister = async () => {
  errorMessage.value = ''

  if (password.value !== confirmPassword.value) {
    errorMessage.value = 'Passwords do not match.'
    return
  }

  submitting.value = true

  try {
    await auth.register(name.value, email.value, password.value)
    router.push('/tickets')
  } catch (error) {
    errorMessage.value =
      error.response?.data?.error || 'Registration failed. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>