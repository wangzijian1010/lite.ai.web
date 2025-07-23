<template>
  <div v-if="showModal" class="auth-modal-overlay" @click="closeModal">
    <div class="auth-modal" @click.stop>
      <div class="auth-header">
        <h2>{{ isLogin ? '登录' : '注册' }}</h2>
        <button class="close-btn" @click="closeModal">×</button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="auth-form">
        <!-- 邮箱 -->
        <div class="input-group">
          <label for="email">邮箱</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            required
            placeholder="请输入您的邮箱"
            class="auth-input"
            :disabled="isLogin || emailVerified"
          />
          <!-- 邮箱验证状态 -->
          <div v-if="!isLogin && emailVerified" class="verification-status verified">
            ✓ 邮箱已验证
          </div>
        </div>
        
        <!-- 验证码（注册时显示） -->
        <div v-if="!isLogin" class="input-group">
          <label for="verification_code">邮箱验证码</label>
          <div class="verification-input-group">
            <input
              id="verification_code"
              v-model="form.verification_code"
              type="text"
              :required="!isLogin"
              placeholder="请输入6位验证码"
              class="auth-input verification-input"
              maxlength="6"
              :disabled="!form.email"
            />
            <button
              type="button"
              @click="sendVerificationCode"
              :disabled="!form.email || sendingCode || countdown > 0"
              class="send-code-btn"
            >
              <span v-if="!sendingCode && countdown === 0">发送验证码</span>
              <span v-else-if="sendingCode">发送中...</span>
              <span v-else>{{ countdown }}s后重试</span>
            </button>
          </div>
          <div v-if="codeStatus" class="code-status" :class="codeStatus.type">
            {{ codeStatus.message }}
          </div>
        </div>
        
        <!-- 用户名 -->
        <div class="input-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            placeholder="请输入用户名"
            class="auth-input"
          />
        </div>
        
        <!-- 密码 -->
        <div class="input-group">
          <label for="password">密码</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            required
            placeholder="请输入密码"
            class="auth-input"
          />
        </div>
        
        <!-- 提交按钮 -->
        <button
          type="submit"
          :disabled="loading"
          class="auth-submit-btn"
        >
          <span v-if="!loading">{{ isLogin ? '登录' : '注册' }}</span>
          <span v-else class="loading">{{ isLogin ? '登录中...' : '注册中...' }}</span>
        </button>
        
        <!-- 错误信息 -->
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        
        <!-- 切换登录/注册 -->
        <div class="switch-auth">
          <span v-if="isLogin">
            还没有账户？
            <button type="button" @click="switchMode" class="switch-btn">立即注册</button>
          </span>
          <span v-else>
            已有账户？
            <button type="button" @click="switchMode" class="switch-btn">立即登录</button>
          </span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'

const props = defineProps<{
  showModal: boolean
  mode: 'login' | 'register'
}>()

const emit = defineEmits<{
  close: []
  success: []
}>()

const authStore = useAuthStore()

const isLogin = ref(props.mode === 'login')
const loading = ref(false)
const error = ref('')

// 验证码相关状态
const sendingCode = ref(false)
const countdown = ref(0)
const emailVerified = ref(false)
const codeStatus = ref<{type: 'success' | 'error' | 'info', message: string} | null>(null)

const form = reactive({
  username: '',
  email: '',
  password: '',
  verification_code: ''
})

// 监听模式变化
watch(() => props.mode, (newMode) => {
  isLogin.value = newMode === 'login'
  resetForm()
})

const resetForm = () => {
  form.username = ''
  form.email = ''
  form.password = ''
  form.verification_code = ''
  error.value = ''
  emailVerified.value = false
  codeStatus.value = null
  countdown.value = 0
}

const closeModal = () => {
  emit('close')
  resetForm()
}

const switchMode = () => {
  isLogin.value = !isLogin.value
  resetForm()
}

// 发送验证码
const sendVerificationCode = async () => {
  console.log('Sending verification code for email:', form.email)
  try {
    sendingCode.value = true
    codeStatus.value = null
    
    const response = await authStore.sendVerificationCode(form.email)
    console.log('Received response:', response)
    
    if (response.success) {
      codeStatus.value = { type: 'success', message: response.message }
      startCountdown(60) // 开始60秒倒计时
    } else {
      codeStatus.value = { type: 'error', message: response.message }
      if (response.cooldown_seconds) {
        startCountdown(response.cooldown_seconds)
      }
    }
  } catch (err: any) {
    console.error('Error in sendVerificationCode:', err)
    console.error('Error response:', err.response)
    const errorMsg = err.response?.data?.detail || err.message || '发送失败'
    codeStatus.value = { type: 'error', message: errorMsg }
  } finally {
    sendingCode.value = false
  }
}

// 开始倒计时
const startCountdown = (seconds: number) => {
  countdown.value = seconds
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
    }
  }, 1000)
}

// 验证验证码
const verifyCode = async () => {
  try {
    const response = await authStore.verifyCode(form.email, form.verification_code)
    if (response.success) {
      emailVerified.value = true
      codeStatus.value = { type: 'success', message: '验证码验证成功' }
      return true
    }
  } catch (err: any) {
    const errorMsg = err.response?.data?.detail || err.message || '验证码验证失败'
    codeStatus.value = { type: 'error', message: errorMsg }
    return false
  }
}

const handleSubmit = async () => {
  try {
    loading.value = true
    error.value = ''
    
    if (isLogin.value) {
      await authStore.login(form.username, form.password)
    } else {
      // 注册前先验证验证码
      if (!emailVerified.value) {
        const verified = await verifyCode()
        if (!verified) {
          return
        }
      }
      
      await authStore.register(form.username, form.email, form.password, form.verification_code)
    }
    
    emit('success')
    closeModal()
  } catch (err: any) {
    error.value = err.response?.data?.detail || err.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.auth-modal {
  background: rgba(30, 41, 59, 0.9);
  backdrop-filter: blur(30px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 24px;
  padding: 40px;
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
  animation: slideIn 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.auth-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: white;
  font-size: 2rem;
  font-weight: 700;
  margin: 0;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.15);
  transform: rotate(90deg);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input-group label {
  color: white;
  font-weight: 500;
  font-size: 1.05rem;
}

.auth-input {
  padding: 16px 20px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1.05rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
}

.auth-input:focus {
  outline: none;
  border-color: #60a5fa;
  background: rgba(96, 165, 250, 0.1);
  box-shadow: 0 0 0 4px rgba(96, 165, 250, 0.2);
}

.auth-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.auth-submit-btn {
  padding: 18px 28px;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  border: none;
  border-radius: 16px;
  color: white;
  font-size: 1.15rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  margin-top: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.auth-submit-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(96, 165, 250, 0.4);
}

.auth-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-message {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: 12px;
  padding: 16px;
  font-size: 1rem;
  text-align: center;
  font-weight: 500;
}

.switch-auth {
  text-align: center;
  margin-top: 20px;
  color: rgba(255, 255, 255, 0.8);
  font-size: 1.05rem;
}

.switch-btn {
  background: none;
  border: none;
  color: #60a5fa;
  cursor: pointer;
  font-weight: 600;
  text-decoration: underline;
  font-size: inherit;
  transition: color 0.2s ease;
}

.switch-btn:hover {
  color: #93c5fd;
}

@media (max-width: 480px) {
  .auth-modal {
    padding: 30px 20px;
  }
  
  .auth-header h2 {
    font-size: 1.75rem;
  }
  
  .verification-input-group {
    flex-direction: column;
    gap: 12px;
  }
  
  .verification-input {
    margin-right: 0;
  }
  
  .send-code-btn {
    width: 100%;
  }
}

/* 验证码相关样式 */
.verification-input-group {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.verification-input {
  flex: 1;
  margin-right: 0;
}

.send-code-btn {
  padding: 16px 20px;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  border: none;
  border-radius: 16px;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  white-space: nowrap;
  min-width: 120px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.send-code-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 15px rgba(96, 165, 250, 0.3);
}

.send-code-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.verification-status {
  margin-top: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.95rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

.verification-status.verified {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.code-status {
  margin-top: 10px;
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.code-status.success {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.code-status.error {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.code-status.info {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}
</style>