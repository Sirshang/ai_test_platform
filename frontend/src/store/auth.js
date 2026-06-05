import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import { setAuthCredentials } from '../api/client'
import { fetchProjects } from '../api/projects'

const STORAGE_KEY = 'aits_auth'

export const useAuthStore = defineStore('auth', () => {
  const username = ref('')
  const password = ref('')
  const isAuthenticated = ref(false)
  const loginError = ref('')

  function restoreSession() {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return
    try {
      const data = JSON.parse(raw)
      if (data.username && data.password) {
        username.value = data.username
        password.value = data.password
        setAuthCredentials(data.username, data.password)
        isAuthenticated.value = true
      }
    } catch {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  }

  async function login(user, pass) {
    loginError.value = ''
    setAuthCredentials(user, pass)
    try {
      await fetchProjects()
      username.value = user
      password.value = pass
      isAuthenticated.value = true
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ username: user, password: pass }))
    } catch (error) {
      setAuthCredentials(null, null)
      isAuthenticated.value = false
      loginError.value = error?.response?.status === 401 ? '用户名或密码错误' : '无法连接后端服务'
      throw error
    }
  }

  function logout() {
    username.value = ''
    password.value = ''
    isAuthenticated.value = false
    loginError.value = ''
    setAuthCredentials(null, null)
    sessionStorage.removeItem(STORAGE_KEY)
  }

  const displayName = computed(() => username.value || '未登录')

  restoreSession()

  return {
    username,
    isAuthenticated,
    loginError,
    displayName,
    login,
    logout,
    restoreSession,
  }
})
