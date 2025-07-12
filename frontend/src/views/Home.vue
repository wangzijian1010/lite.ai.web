<template>
  <div class="home">
    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="gradient-text">吉卜力 AI</span>
          </h1>
          <p class="hero-subtitle">
            用 AI 的魔法，将普通照片转换为充满想象力的吉卜力工作室风格艺术作品
          </p>
        </div>
        
        <div class="hero-visual">
          <div class="floating-elements">
            <div class="element element-1">✨</div>
            <div class="element element-2">🎨</div>
            <div class="element element-3">🌟</div>
            <div class="element element-4">🎭</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <section class="main-content">
      <div class="container">
        <div class="content-grid">
          <!-- Upload Section -->
          <div class="upload-section">
            <div class="section-header">
              <h2>上传您的照片</h2>
              <p>支持 JPG、PNG、WebP 格式，AI 将为您创造奇迹</p>
            </div>
            <div class="upload-card">
              <!-- Processing Type Selector -->
              <div class="processing-selector">
                <h3>选择处理类型</h3>
                <div class="processing-options">
                  <button 
                    @click="selectedProcessing = 'ghibli_style'"
                    :class="['processing-btn', { active: selectedProcessing === 'ghibli_style' }]"
                  >
                    🎨 吉卜力风格
                  </button>
                  <button 
                    @click="selectedProcessing = 'grayscale'"
                    :class="['processing-btn', { active: selectedProcessing === 'grayscale' }]"
                  >
                    ⚫ 灰度转换
                  </button>
                  <button 
                    @click="selectedProcessing = 'upscale'"
                    :class="['processing-btn', { active: selectedProcessing === 'upscale' }]"
                  >
                    🔍 AI超分放大
                  </button>
                </div>
              </div>
              
              <ImageUpload @upload="handleImageUpload" :loading="processing" />
            </div>
          </div>

          <!-- Result Section -->
          <div v-if="originalImage || resultImage" class="result-section">
            <div class="section-header">
              <h2>艺术转换</h2>
              <p>见证您的照片华丽变身</p>
            </div>
            <div class="result-card">
              <ImageComparison 
                :original="originalImage" 
                :result="resultImage" 
                :loading="processing"
              />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features Section -->
    <section class="features">
      <div class="container">
        <div class="features-grid">
          <div class="feature-item">
            <div class="feature-icon">⚡</div>
            <h3>瞬间转换</h3>
            <p>AI 技术，秒级处理</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">🎨</div>
            <h3>完美风格</h3>
            <p>还原经典吉卜力美学</p>
          </div>
          <div class="feature-item">
            <div class="feature-icon">💫</div>
            <h3>免费使用</h3>
            <p>无限制创作体验</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import ImageUpload from '@/components/ImageUpload.vue'
import ImageComparison from '@/components/ImageComparison.vue'
import { useGhibliStore } from '@/stores/ghibli'

const ghibliStore = useGhibliStore()

const originalImage = ref<string>('')
const resultImage = ref<string>('')
const processing = ref(false)
const selectedProcessing = ref<'ghibli_style' | 'grayscale' | 'upscale'>('ghibli_style')

onMounted(() => {
  // 加载可用的处理器
  ghibliStore.loadAvailableProcessors()
})

const handleImageUpload = async (file: File) => {
  try {
    processing.value = true
    originalImage.value = URL.createObjectURL(file)
    
    // 根据选择的处理类型调用不同的方法
    let result: string
    if (selectedProcessing.value === 'ghibli_style') {
      result = await ghibliStore.convertToGhibliStyle(file)
    } else if (selectedProcessing.value === 'grayscale') {
      result = await ghibliStore.convertToGrayscale(file)
    } else if (selectedProcessing.value === 'upscale') {
      result = await ghibliStore.upscaleImage(file, 2) // 默认2倍放大
    } else {
      throw new Error('未知的处理类型')
    }
    
    resultImage.value = result
  } catch (error) {
    console.error('转换失败:', error)
    const errorMessage = error instanceof Error ? error.message : '图片转换失败，请重试'
    alert(errorMessage)
  } finally {
    processing.value = false
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
}

/* Hero Section */
.hero {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
}

.hero-text {
  z-index: 2;
}

.hero-title {
  font-size: clamp(3rem, 8vw, 6rem);
  font-weight: 800;
  line-height: 1.1;
  margin-bottom: 24px;
}

.gradient-text {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.6;
  font-weight: 300;
}

.hero-visual {
  position: relative;
  height: 400px;
}

.floating-elements {
  position: relative;
  width: 100%;
  height: 100%;
}

.element {
  position: absolute;
  font-size: 3rem;
  animation: float 6s ease-in-out infinite;
}

.element-1 {
  top: 20%;
  left: 20%;
  animation-delay: 0s;
}

.element-2 {
  top: 60%;
  right: 30%;
  animation-delay: 1.5s;
}

.element-3 {
  bottom: 30%;
  left: 10%;
  animation-delay: 3s;
}

.element-4 {
  top: 10%;
  right: 10%;
  animation-delay: 4.5s;
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px) rotate(0deg);
  }
  50% {
    transform: translateY(-20px) rotate(10deg);
  }
}

/* Main Content */
.main-content {
  padding: 80px 0;
}

.content-grid {
  display: grid;
  gap: 60px;
}

.section-header {
  text-align: center;
  margin-bottom: 40px;
}

.section-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: white;
  margin-bottom: 16px;
}

.section-header p {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.7);
}

.upload-card,
.result-card {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 32px;
  padding: 40px;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Processing Selector */
.processing-selector {
  margin-bottom: 32px;
  text-align: center;
}

.processing-selector h3 {
  color: white;
  margin-bottom: 20px;
  font-size: 1.3rem;
  font-weight: 600;
}

.processing-options {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.processing-btn {
  padding: 12px 24px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  color: rgba(255, 255, 255, 0.7);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  min-width: 140px;
}

.processing-btn:hover {
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(120, 119, 198, 0.1);
  color: white;
  transform: translateY(-2px);
}

.processing-btn.active {
  border-color: #7877c6;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

/* Features Section */
.features {
  padding: 80px 0;
  background: rgba(255, 255, 255, 0.02);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 40px;
}

.feature-item {
  text-align: center;
  padding: 40px 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  transition: transform 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-8px);
}

.feature-icon {
  font-size: 3rem;
  margin-bottom: 20px;
}

.feature-item h3 {
  font-size: 1.5rem;
  color: white;
  margin-bottom: 12px;
  font-weight: 600;
}

.feature-item p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
}

@media (max-width: 768px) {
  .hero-content {
    grid-template-columns: 1fr;
    gap: 40px;
    text-align: center;
  }
  
  .hero-visual {
    height: 200px;
  }
  
  .element {
    font-size: 2rem;
  }
}
</style>