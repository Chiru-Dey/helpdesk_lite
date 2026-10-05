import { defineStore } from 'pinia'
import api from '../api/client'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: false,
  }),
  actions: {
    async fetchUser() {
      try {
        const { data } = await api.get('/auth/me')
        this.user = data.user
      } catch {
        this.user = null
      }
    },
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this.user = data.user
    },
    async register(name, email, password) {
      const { data } = await api.post('/auth/register', { name, email, password })
      this.user = data.user
    },
    async logout() {
      await api.post('/auth/logout')
      this.user = null
    }
  }
})