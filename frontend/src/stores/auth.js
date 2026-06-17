import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(credentials) {
    const res = await authApi.login(credentials)
    token.value = res.data.access_token
    user.value = res.data.user
    localStorage.setItem('token', res.data.access_token)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    return res
  }

  async function register(userData) {
    const res = await authApi.register(userData)
    return res
  }

  async function fetchUser() {
    const res = await authApi.getMe()
    user.value = res.data
    localStorage.setItem('user', JSON.stringify(res.data))
    return res
  }

  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  function loadUserFromStorage() {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        user.value = JSON.parse(userStr)
      } catch (e) {
        user.value = null
      }
    }
  }

  return {
    token,
    user,
    isLoggedIn,
    login,
    register,
    fetchUser,
    logout,
    loadUserFromStorage,
  }
})
