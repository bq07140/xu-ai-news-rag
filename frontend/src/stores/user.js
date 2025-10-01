import { defineStore } from 'pinia'
import { ref } from 'vue'
import { authAPI } from '@/api'
import router from '@/router'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('access_token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('user_info') || 'null'))

  // Login
  async function login(username, password) {
    try {
      const res = await authAPI.login({ username, password })
      
      // Update reactive state
      token.value = res.access_token
      userInfo.value = res.user
      
      // Save to localStorage
      localStorage.setItem('access_token', res.access_token)
      localStorage.setItem('user_info', JSON.stringify(res.user))
      
      ElMessage.success('Login successful')
      
      // Wait 200ms to ensure state is updated before navigation
      await new Promise(resolve => setTimeout(resolve, 200))
      router.push('/documents')
      
      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    }
  }

  // Register
  async function register(userData) {
    try {
      await authAPI.register(userData)
      ElMessage.success('Registration successful, please login')
      return true
    } catch (error) {
      console.error('Register error:', error)
      return false
    }
  }

  // Logout
  async function logout() {
    try {
      await authAPI.logout()
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      token.value = ''
      userInfo.value = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('user_info')
      router.push('/login')
    }
  }

  // Fetch user information
  async function fetchUserInfo() {
    try {
      const res = await authAPI.getUserInfo()
      userInfo.value = res.user
      localStorage.setItem('user_info', JSON.stringify(res.user))
      return true
    } catch (error) {
      console.error('Fetch user info error:', error)
      return false
    }
  }

  return {
    token,
    userInfo,
    login,
    register,
    logout,
    fetchUserInfo
  }
})

