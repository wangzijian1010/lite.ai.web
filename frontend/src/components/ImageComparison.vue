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

const downloadImage = () => {
  if (!props.result) return
  
  const link = document.createElement('a')
  link.href = props.result
  link.download = `ghibli-style-${Date.now()}.png`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
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
  gap: 30px;
  align-items: center;
  margin-bottom: 32px;
}

.image-panel h3 {
  text-align: center;
  color: white;
  margin-bottom: 20px;
  font-weight: 600;
  font-size: 1.3rem;
}

.image-wrapper {
  aspect-ratio: 1;
  border-radius: 20px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
}

.image-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.05), transparent);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.image-wrapper:hover::before {
  opacity: 1;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-wrapper:hover img {
  transform: scale(1.02);
}

.placeholder {
  text-align: center;
  color: rgba(255, 255, 255, 0.5);
}

.placeholder-icon {
  font-size: 4rem;
  margin-bottom: 16px;
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-10px);
  }
}

.processing {
  text-align: center;
  color: white;
}

.processing .loading {
  margin: 0 auto 20px auto;
}

.processing p {
  font-size: 1.1rem;
  animation: glow 2s ease-in-out infinite alternate;
}

@keyframes glow {
  from {
    text-shadow: 0 0 5px rgba(120, 119, 198, 0.5);
  }
  to {
    text-shadow: 0 0 20px rgba(120, 119, 198, 0.8);
  }
}

.divider {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.6);
}

.arrow {
  font-size: 2.5rem;
  font-weight: bold;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateX(0);
  }
  40% {
    transform: translateX(5px);
  }
  60% {
    transform: translateX(-5px);
  }
}

.action-buttons {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 32px;
}

@media (max-width: 768px) {
  .comparison-container {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .divider {
    transform: rotate(90deg);
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .action-buttons .btn {
    width: 200px;
  }
}
</style>