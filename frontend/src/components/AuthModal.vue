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
  try {
    sendingCode.value = true
    codeStatus.value = null
    
    const response = await authStore.sendVerificationCode(form.email)
    
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
  backdrop-filter: blur(5px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.auth-modal {
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 40px;
  width: 100%;
  max-width: 400px;
  max-height: 90vh;
  overflow-y: auto;
}

.auth-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: white;
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.7);
  font-size: 2rem;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.close-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  color: white;
  font-weight: 500;
  font-size: 0.95rem;
}

.auth-input {
  padding: 12px 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.auth-input:focus {
  outline: none;
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(120, 119, 198, 0.1);
  box-shadow: 0 0 0 3px rgba(120, 119, 198, 0.2);
}

.auth-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.auth-submit-btn {
  padding: 14px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-top: 10px;
}

.auth-submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.auth-submit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-message {
  color: #ff6b6b;
  background: rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.3);
  border-radius: 8px;
  padding: 12px;
  font-size: 0.9rem;
  text-align: center;
}

.switch-auth {
  text-align: center;
  margin-top: 20px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
}

.switch-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-weight: 600;
  text-decoration: underline;
  font-size: inherit;
}

.switch-btn:hover {
  color: #7877c6;
}

@media (max-width: 480px) {
  .auth-modal {
    padding: 30px 20px;
  }
  
  .auth-header h2 {
    font-size: 1.5rem;
  }
  
  .verification-input-group {
    flex-direction: column;
    gap: 10px;
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
  gap: 8px;
  align-items: flex-start;
}

.verification-input {
  flex: 1;
  margin-right: 0;
}

.send-code-btn {
  padding: 12px 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  min-width: 100px;
}

.send-code-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.send-code-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.verification-status {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
}

.verification-status.verified {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.code-status {
  margin-top: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.9rem;
}

.code-status.success {
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.code-status.error {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.code-status.info {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.3);
}
</style>