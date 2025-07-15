import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/auth'

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  created_at: string
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('token'))
  const isAuthenticated = ref(!!token.value)

  // 设置axios默认header
  if (token.value) {
    axios.defaults.headers.common['Authorization'] = `Bearer ${token.value}`
  }

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    axios.defaults.headers.common['Authorization'] = `Bearer ${newToken}`
    isAuthenticated.value = true
  }

  const clearToken = () => {
    token.value = null
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
    isAuthenticated.value = false
    user.value = null
  }

  const register = async (username: string, email: string, password: string, verification_code: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/register`, {
        username,
        email,
        password,
        verification_code
      })
      
      // 注册成功后自动登录
      const loginResponse = await axios.post(`${API_BASE_URL}/login`, {
        username,
        password
      })
      
      setToken(loginResponse.data.access_token)
      await fetchUserInfo()
      
      return response.data
    } catch (error) {
      throw error
    }
  }

  const sendVerificationCode = async (email: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/send-verification-code`, {
        email
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  const verifyCode = async (email: string, code: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/verify-code`, {
        email,
        code
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  const login = async (username: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/login`, {
        username,
        password
      })
      
      setToken(response.data.access_token)
      await fetchUserInfo()
      
      return response.data
    } catch (error) {
      throw error
    }
  }

  const logout = () => {
    clearToken()
  }

  const fetchUserInfo = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/me`)
      user.value = response.data
      return response.data
    } catch (error) {
      clearToken()
      throw error
    }
  }

  // 初始化时如果有token，尝试获取用户信息
  if (token.value) {
    fetchUserInfo().catch(() => {
      clearToken()
    })
  }

  return {
    user,
    token,
    isAuthenticated,
    register,
    sendVerificationCode,
    verifyCode,
    login,
    logout,
    fetchUserInfo
  }
})