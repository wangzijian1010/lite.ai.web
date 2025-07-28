import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'

const API_BASE_URL = `${import.meta.env.VITE_API_BASE_URL}/api/auth`

export interface User {
  id: number
  username: string
  email: string
  is_active: boolean
  email_verified: boolean
  credits: number
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

  const registerSimple = async (username: string, email: string, password: string) => {
    console.log('🔵 [FRONTEND] Starting simple registration...')
    console.log('🔵 [FRONTEND] API_BASE_URL:', API_BASE_URL)
    console.log('🔵 [FRONTEND] Registration data:', { username, email, password: '***' })
    
    try {
      console.log('🔵 [FRONTEND] Sending registration request...')
      const response = await axios.post(`${API_BASE_URL}/register-simple`, {
        username,
        email,
        password
      })
      
      console.log('🟢 [FRONTEND] Registration successful:', response.data)
      
      // 注册成功后自动登录
      console.log('🔵 [FRONTEND] Auto-login after registration...')
      const loginResponse = await axios.post(`${API_BASE_URL}/login`, {
        username,
        password
      })
      
      console.log('🟢 [FRONTEND] Auto-login successful')
      setToken(loginResponse.data.access_token)
      await fetchUserInfo()
      
      return response.data
    } catch (error: any) {
      console.error('🔴 [FRONTEND] Registration failed:', error)
      console.error('🔴 [FRONTEND] Error response:', error.response?.data)
      console.error('🔴 [FRONTEND] Error status:', error.response?.status)
      console.error('🔴 [FRONTEND] Error headers:', error.response?.headers)
      console.error('🔴 [FRONTEND] Full error object:', error)
      throw error
    }
  }

  const sendVerificationCode = async (email: string) => {
    console.log('Sending verification code to:', email);
    try {
      const response = await axios.post(`${API_BASE_URL}/send-verification-code`, {
        email
      })
      console.log('Verification code response:', response.data);
      return response.data
    } catch (error: any) {
      console.error('Error sending verification code:', error);
      console.error('Error response:', error.response?.data);
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
    console.log('🔵 [FRONTEND] Starting login...')
    console.log('🔵 [FRONTEND] API_BASE_URL:', API_BASE_URL)
    console.log('🔵 [FRONTEND] Login data:', { username, password: '***' })
    
    try {
      console.log('🔵 [FRONTEND] Sending login request...')
      const response = await axios.post(`${API_BASE_URL}/login`, {
        username,
        password
      })
      
      console.log('🟢 [FRONTEND] Login successful:', response.data)
      setToken(response.data.access_token)
      await fetchUserInfo()
      
      return response.data
    } catch (error: any) {
      console.error('🔴 [FRONTEND] Login failed:', error)
      console.error('🔴 [FRONTEND] Error response:', error.response?.data)
      console.error('🔴 [FRONTEND] Error status:', error.response?.status)
      console.error('🔴 [FRONTEND] Error headers:', error.response?.headers)
      console.error('🔴 [FRONTEND] Full error object:', error)
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

  const getCredits = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/credits`)
      return response.data
    } catch (error) {
      throw error
    }
  }

  const checkCredits = async (cost: number = 10) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/credits/check`, { cost })
      return response.data
    } catch (error) {
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
    registerSimple,
    sendVerificationCode,
    verifyCode,
    login,
    logout,
    fetchUserInfo,
    getCredits,
    checkCredits
  }
})