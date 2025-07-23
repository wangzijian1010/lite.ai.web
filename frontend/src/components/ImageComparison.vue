<template>
  <div class="image-comparison">
    <div class="comparison-container">
      <div class="image-panel">
        <h3>原图</h3>
        <div class="image-wrapper">
          <img v-if="original" :src="original" alt="原图" />
          <div v-else class="placeholder">
            <div class="placeholder-icon">🖼️</div>
            <p>上传图片后显示</p>
          </div>
        </div>
      </div>
      
      <div class="divider">
        <div class="arrow">→</div>
      </div>
      
      <div class="image-panel">
        <h3>吉卜力风格</h3>
        <div class="image-wrapper">
          <div v-if="loading" class="processing">
            <div class="loading"></div>
            <p>AI 正在施展魔法...</p>
          </div>
          <img v-else-if="result" :src="result" alt="吉卜力风格" />
          <div v-else class="placeholder">
            <div class="placeholder-icon">✨</div>
            <p>转换后的图片将在这里显示</p>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="result && !loading" class="action-buttons">
      <button @click="downloadImage" class="btn btn-primary">
        📥 下载图片
      </button>
      <button @click="shareImage" class="btn btn-secondary">
        🔗 分享
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface Props {
  original?: string
  result?: string
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  original: '',
  result: '',
  loading: false
})

const authStore = useAuthStore()

const downloadImage = async () => {
  if (!props.result) return
  
  try {
    // 检查用户是否登录
    if (!authStore.isAuthenticated) {
      alert('请先登录后再下载图片')
      return
    }

    // 从result URL中提取文件名
    const filename = props.result.split('/').pop()
    
    if (!filename) {
      alert('无法获取文件名')
      return
    }

    // 调用后端的下载接口（这会扣除积分）
    const response = await axios.get(`${API_BASE_URL}/api/files/${filename}?download=true`, {
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })

    // 创建下载链接
    const blob = new Blob([response.data])
    const downloadUrl = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(downloadUrl)

    // 刷新用户信息以更新积分显示
    await authStore.fetchUserInfo()
    
    alert('下载成功！已扣除10积分')
  } catch (error: any) {
    console.error('下载失败:', error)
    const errorMessage = error.response?.data?.detail || error.message || '下载失败，请重试'
    alert(errorMessage)
  }
}

const shareImage = async () => {
  if (!props.result) return
  
  try {
    if (navigator.share) {
      await navigator.share({
        title: '我的吉卜力风格图片',
        text: '看看我用吉卜力 AI 创作的图片！',
        url: props.result
      })
    } else {
      await navigator.clipboard.writeText(window.location.href)
      alert('链接已复制到剪贴板')
    }
  } catch (error) {
    console.error('分享失败:', error)
  }
}
</script>

<style scoped>
.image-comparison {
  width: 100%;
}

.comparison-container {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 40px;
  align-items: center;
  margin-bottom: 40px;
  padding: 20px;
}

.image-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.image-panel h3 {
  text-align: center;
  color: white;
  margin-bottom: 0;
  font-weight: 700;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.image-wrapper {
  aspect-ratio: 1;
  border-radius: 24px;
  overflow: hidden;
  background: rgba(30, 41, 59, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 350px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  position: relative;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
  transition: all 0.4s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.image-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent, rgba(96, 165, 250, 0.1), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 1;
}

.image-wrapper:hover::before {
  opacity: 1;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  z-index: 0;
}

.image-wrapper:hover img {
  transform: scale(1.03);
}

.placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.6);
  padding: 30px;
}

.placeholder-icon {
  font-size: 5rem;
  margin-bottom: 20px;
  animation: float 3s ease-in-out infinite;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
}

.processing {
  text-align: center;
  color: white;
  padding: 40px;
}

.processing .loading {
  margin: 0 auto 24px auto;
  width: 40px;
  height: 40px;
  border-width: 4px;
}

.processing p {
  font-size: 1.25rem;
  font-weight: 500;
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    text-shadow: 0 0 10px rgba(96, 165, 250, 0.5);
  }
  to {
    text-shadow: 0 0 25px rgba(96, 165, 250, 0.8);
  }
}

.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.7);
}

.arrow {
  font-size: 3rem;
  font-weight: bold;
  animation: bounce 2s infinite;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(0);
  }
  40% {
    transform: translateX(8px);
  }
  60% {
    transform: translateX(-8px);
  }
}

.action-buttons {
  display: flex;
  gap: 24px;
  justify-content: center;
  margin-top: 40px;
}

.btn {
  padding: 16px 32px;
  border: none;
  border-radius: 16px;
  font-weight: 600;
  font-size: 1.1rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.btn-primary {
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(96, 165, 250, 0.4);
}

.btn-secondary {
  background: rgba(255, 255, 255, 0.1);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-3px);
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
}

@media (max-width: 768px) {
  .comparison-container {
    grid-template-columns: 1fr;
    gap: 30px;
  }
  
  .divider {
    transform: rotate(90deg);
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 300px;
  }
  
  .image-wrapper {
    min-height: 250px;
  }
}
</style>