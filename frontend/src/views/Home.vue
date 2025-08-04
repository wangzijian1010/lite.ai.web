<template>
  <div class="home">
    <!-- 顶部导航栏 -->
    <header class="top-navbar">
      <div class="navbar-content">
        <div class="logo">
          <span class="gradient-text">吉卜力 AI</span>
        </div>
        
        <!-- 用户区域 -->
        <div class="user-area">
          <div v-if="authStore.isAuthenticated" class="user-menu">
            <div class="user-avatar">
              {{ authStore.user?.username?.charAt(0).toUpperCase() }}
            </div>
            <div class="user-dropdown" :class="{ open: dropdownOpen }">
              <button @click="toggleDropdown" class="dropdown-trigger">
                <span class="username">{{ authStore.user?.username }}</span>
                <span class="dropdown-arrow">▼</span>
              </button>
              <div class="dropdown-content">
                <div class="dropdown-item credits-item">
                  积分: {{ authStore.user?.credits || 0 }}
                </div>
                <button @click="openSettings" class="dropdown-item settings-item">
                  <span>⚙️ 设置</span>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="auth-buttons">
            <button @click="showAuthModal('login')" class="auth-btn login-btn">
              登录
            </button>
            <button @click="showAuthModal('register')" class="auth-btn register-btn">
              注册
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Hero Section -->
    <section class="hero">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <span class="gradient-text">吉卜力 AI</span>
          </h1>
          <p class="hero-subtitle">
            AI 赋能，让您的照片秒变艺术大片。支持多种风格转换，包括独特的吉卜力梦幻风，轻松打造个性视觉作品。
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
                    <span class="credits-cost">消耗 10 积分</span>
                  </button>
                  <button 
                    @click="selectedProcessing = 'grayscale'"
                    :class="['processing-btn', { active: selectedProcessing === 'grayscale' }]"
                  >
                    ⚫ 灰度转换
                    <span class="credits-cost">消耗 10 积分</span>
                  </button>
                  <button 
                    @click="selectedProcessing = 'creative_upscale'"
                    :class="['processing-btn', { active: selectedProcessing === 'creative_upscale' }]"
                  >
                    ✨ 创意放大修复
                    <span class="credits-cost">消耗 10 积分</span>
                  </button>
                  <button 
                    @click="selectedProcessing = 'text_to_image'"
                    :class="['processing-btn', { active: selectedProcessing === 'text_to_image' }]"
                  >
                    🎯 AI文生图
                    <span class="credits-cost">消耗 10 积分</span>
                  </button>
                  <button 
                    @click="selectedProcessing = 'face_swap'"
                    :class="['processing-btn', { active: selectedProcessing === 'face_swap' }]"
                  >
                    🔄 AI换脸
                    <span class="credits-cost">消耗 15 积分</span>
                  </button>
                </div>
              </div>
              
              <!-- 文生图参数输入 -->
              <div v-if="selectedProcessing === 'text_to_image'" class="text-to-image-inputs">
                <div class="input-group">
                  <label for="prompt">正向提示词 (必填)</label>
                  <textarea 
                    id="prompt"
                    v-model="textToImageParams.prompt"
                    placeholder="描述您想要生成的图像，例如：a beautiful landscape with mountains and lake"
                    rows="3"
                    class="input-field"
                  ></textarea>
                </div>
                
                <div class="input-group">
                  <label for="negative_prompt">负向提示词</label>
                  <textarea 
                    id="negative_prompt"
                    v-model="textToImageParams.negative_prompt"
                    placeholder="描述您不想要的元素，例如：blurry, low quality, text"
                    rows="2"
                    class="input-field"
                  ></textarea>
                </div>
                
                <button 
                  @click="handleTextToImage"
                  :disabled="processing || !textToImageParams.prompt.trim()"
                  class="btn btn-primary generate-btn"
                >
                  <span v-if="!processing">🎯 生成图像</span>
                  <span v-else class="loading-content">
                    <div class="loading"></div>
                    <div class="progress-info">
                      <div v-if="ghibliStore.currentTask">
                        <div class="progress-text">{{ ghibliStore.currentTask.message }}</div>
                        <div class="progress-bar">
                          <div 
                            class="progress-fill" 
                            :style="{ width: ghibliStore.currentTask.progress + '%' }"
                          ></div>
                        </div>
                        <div class="progress-percent">{{ ghibliStore.currentTask.progress }}%</div>
                      </div>
                      <div v-else>正在生成...</div>
                    </div>
                  </span>
                </button>
              </div>
              
              <!-- Face Swap功能 -->
              <div v-if="selectedProcessing === 'face_swap'">
                <div class="face-swap-container">
                  <div class="face-swap-uploads">
                    <!-- Source Image Upload -->
                    <div class="face-swap-upload-section">
                      <h4>Source Image (源图)</h4>
                      <p>Upload the image with the face you want to use</p>
                      <div class="face-swap-upload-area" @click="triggerSourceUpload" @dragover.prevent @drop="handleSourceDrop">
                        <input 
                          ref="sourceFileInput" 
                          type="file" 
                          accept="image/*" 
                          @change="handleSourceSelect" 
                          style="display: none"
                        />
                        <div v-if="!sourceFile" class="upload-placeholder">
                          <div class="upload-icon">📷</div>
                          <div class="upload-text">Click or drag source image here</div>
                        </div>
                        <div v-else class="uploaded-preview">
                          <img :src="sourcePreviewUrl" alt="Source" class="preview-img" />
                          <div class="file-info">
                            <div class="file-name">{{ sourceFile.name }}</div>
                            <button @click.stop="clearSourceFile" class="clear-btn">✕</button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Target Image Upload -->
                    <div class="face-swap-upload-section">
                      <h4>Target Image (目标图)</h4>
                      <p>Upload the image where you want to place the face</p>
                      <div class="face-swap-upload-area" @click="triggerTargetUpload" @dragover.prevent @drop="handleTargetDrop">
                        <input 
                          ref="targetFileInput" 
                          type="file" 
                          accept="image/*" 
                          @change="handleTargetSelect" 
                          style="display: none"
                        />
                        <div v-if="!targetFile" class="upload-placeholder">
                          <div class="upload-icon">🎯</div>
                          <div class="upload-text">Click or drag target image here</div>
                        </div>
                        <div v-else class="uploaded-preview">
                          <img :src="targetPreviewUrl" alt="Target" class="preview-img" />
                          <div class="file-info">
                            <div class="file-name">{{ targetFile.name }}</div>
                            <button @click.stop="clearTargetFile" class="clear-btn">✕</button>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Face Swap Process Button -->
                  <div v-if="sourceFile && targetFile" class="face-swap-process">
                    <button 
                      @click="handleFaceSwap"
                      :disabled="processing"
                      class="btn btn-primary face-swap-btn"
                    >
                      <span v-if="!processing">🔄 Start Face Swap</span>
                      <span v-else class="loading-content">
                        <div class="loading"></div>
                        <span>Processing face swap...</span>
                      </span>
                    </button>
                  </div>
                </div>
              </div>
              
              <!-- 图片上传 (非文生图和换脸功能) -->
              <div v-else>
                <!-- 吉卜力风格和创意放大功能显示进度 -->
                <div v-if="(selectedProcessing === 'ghibli_style' || selectedProcessing === 'creative_upscale') && processing && ghibliStore.currentTask" class="upload-progress">
                  <div class="progress-container">
                    <div class="progress-text">{{ ghibliStore.currentTask.message }}</div>
                    <div class="progress-bar">
                      <div 
                        class="progress-fill" 
                        :style="{ width: ghibliStore.currentTask.progress + '%' }"
                      ></div>
                    </div>
                    <div class="progress-percent">{{ ghibliStore.currentTask.progress }}%</div>
                  </div>
                </div>
                <!-- 图片上传组件 -->
                <div v-else>
                  <ImageUpload @upload="handleFileSelect" :loading="false" />
                  
                  <!-- 运行按钮 -->
                  <div v-if="selectedFile" class="run-section">
                    <div class="file-preview-container">
                      <div class="file-preview-card">
                        <div class="preview-image-wrapper">
                          <img :src="filePreviewUrl" alt="Selected file" class="preview-image" />
                        </div>
                        <div class="file-info">
                          <div class="file-name">{{ selectedFile.name }}</div>
                          <div class="file-size">{{ formatFileSize(selectedFile.size) }}</div>
                          <div class="file-status">✅ 已准备好处理</div>
                        </div>
                      </div>
                    </div>
                    
                    <button 
                      @click="handleImageProcess"
                      :disabled="processing || !selectedFile"
                      class="btn btn-primary run-btn"
                    >
                      <span v-if="!processing">
                        <span v-if="selectedProcessing === 'ghibli_style'">🎨 开始转换吉卜力风格</span>
                        <span v-else-if="selectedProcessing === 'grayscale'">⚫ 开始灰度转换</span>
                        <span v-else-if="selectedProcessing === 'creative_upscale'">✨ 开始创意放大修复</span>
                        <span v-else>🚀 开始处理</span>
                      </span>
                      <span v-else class="loading-content">
                        <div class="loading"></div>
                        <div class="progress-info">
                          <div v-if="ghibliStore.currentTask">
                            <div class="progress-text">{{ ghibliStore.currentTask.message }}</div>
                            <div class="progress-bar">
                              <div 
                                class="progress-fill" 
                                :style="{ width: ghibliStore.currentTask.progress + '%' }"
                              ></div>
                            </div>
                            <div class="progress-percent">{{ ghibliStore.currentTask.progress }}%</div>
                          </div>
                          <div v-else>正在处理...</div>
                        </div>
                      </span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Result Section -->
          <div v-if="originalImage || resultImage" class="result-section">
            <div class="section-header">
              <h2>{{ selectedProcessing === 'text_to_image' ? '生成结果' : '艺术转换' }}</h2>
              <p>{{ selectedProcessing === 'text_to_image' ? 'AI为您创造的精美图像' : '见证您的照片华丽变身' }}</p>
            </div>
            <div class="result-card">
              <!-- 文生图只显示结果 -->
              <div v-if="selectedProcessing === 'text_to_image' && resultImage" class="text-to-image-result">
                <div class="generated-image">
                  <img :src="resultImage" alt="Generated Image" />
                </div>
              </div>
              <!-- 其他处理显示对比 -->
              <ImageComparison 
                v-else
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
    
    <!-- 认证模态框 -->
    <AuthModal
      :show-modal="authModalVisible"
      :mode="authMode"
      @close="authModalVisible = false"
      @success="handleAuthSuccess"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import ImageUpload from '@/components/ImageUpload.vue'
import ImageComparison from '@/components/ImageComparison.vue'
import AuthModal from '@/components/AuthModal.vue'
import { useGhibliStore } from '@/stores/ghibli'
import { useAuthStore } from '@/stores/auth'

const ghibliStore = useGhibliStore()
const authStore = useAuthStore()

// 认证相关
const authModalVisible = ref(false)
const authMode = ref<'login' | 'register'>('login')
const dropdownOpen = ref(false)

// 其他现有变量
const originalImage = ref<string>('')
const resultImage = ref<string>('')
const processing = ref(false)
const selectedProcessing = ref<'ghibli_style' | 'grayscale' | 'text_to_image' | 'creative_upscale' | 'face_swap'>('ghibli_style')
const textToImageParams = ref({
  prompt: '',
  negative_prompt: 'text, watermark, blurry, low quality'
})

// 新增文件选择相关状态
const selectedFile = ref<File | null>(null)
const filePreviewUrl = ref<string>('')

// 认证相关方法
const showAuthModal = (mode: 'login' | 'register') => {
  authMode.value = mode
  authModalVisible.value = true
}

const toggleDropdown = () => {
  dropdownOpen.value = !dropdownOpen.value
}

const openSettings = () => {
  const confirmed = confirm('设置选项:\n\n1. 点击"确定"退出登录\n2. 点击"取消"返回')
  if (confirmed) {
    authStore.logout()
  }
  dropdownOpen.value = false
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: Event) => {
  const dropdown = document.querySelector('.user-dropdown')
  if (dropdown && !dropdown.contains(event.target as Node)) {
    dropdownOpen.value = false
  }
}

const handleAuthSuccess = () => {
  // 认证成功后的处理
  console.log('认证成功')
}

onMounted(() => {
  // 加载可用的处理器
  ghibliStore.loadAvailableProcessors()
  // 添加点击外部关闭下拉菜单的事件监听
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  // 移除事件监听
  document.removeEventListener('click', handleClickOutside)
})

// 处理文件选择（不立即处理）
const handleFileSelect = (file: File) => {
  selectedFile.value = file
  filePreviewUrl.value = URL.createObjectURL(file)
  // 清除之前的结果
  originalImage.value = ''
  resultImage.value = ''
}

// 处理图片处理（点击运行按钮时）
const handleImageProcess = async () => {
  if (!selectedFile.value) return
  
  try {
    // 检查用户是否登录
    if (!authStore.isAuthenticated) {
      alert('请先登录后再使用功能')
      showAuthModal('login')
      return
    }

    // 检查积分是否足够
    const creditCheck = await authStore.checkCredits(10)
    if (!creditCheck.success) {
      alert(`积分不足！当前积分：${creditCheck.current_credits}，需要积分：10`)
      return
    }

    processing.value = true
    originalImage.value = URL.createObjectURL(selectedFile.value)
    
    // 根据选择的处理类型调用不同的方法
    let result: string
    if (selectedProcessing.value === 'ghibli_style') {
      result = await ghibliStore.convertToGhibliStyleWithProgress(selectedFile.value)
    } else if (selectedProcessing.value === 'grayscale') {
      result = await ghibliStore.convertToGrayscale(selectedFile.value)
    } else if (selectedProcessing.value === 'creative_upscale') {
      result = await ghibliStore.creativeUpscaleImageWithProgress(selectedFile.value)
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

// 格式化文件大小的辅助函数
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 保留原有的handleImageUpload函数以防其他地方使用
const handleImageUpload = async (file: File) => {
  handleFileSelect(file)
}

const handleTextToImage = async () => {
  try {
    // 检查用户是否登录
    if (!authStore.isAuthenticated) {
      alert('请先登录后再使用功能')
      showAuthModal('login')
      return
    }

    // 检查积分是否足够
    const creditCheck = await authStore.checkCredits(10)
    if (!creditCheck.success) {
      alert(`积分不足！当前积分：${creditCheck.current_credits}，需要积分：10`)
      return
    }

    processing.value = true
    originalImage.value = '' // 文生图没有原图
    
    const result = await ghibliStore.generateImageWithProgress(
      textToImageParams.value.prompt,
      textToImageParams.value.negative_prompt || undefined
    )
    
    resultImage.value = result
  } catch (error) {
    console.error('文生图失败:', error)
    const errorMessage = error instanceof Error ? error.message : '图像生成失败，请重试'
    alert(errorMessage)
  } finally {
    processing.value = false
  }
}

// Face swap methods
const triggerSourceUpload = () => {
  const input = document.querySelector('input[ref="sourceFileInput"]') as HTMLInputElement
  if (input) input.click()
}

const triggerTargetUpload = () => {
  const input = document.querySelector('input[ref="targetFileInput"]') as HTMLInputElement
  if (input) input.click()
}

const handleSourceSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    sourceFile.value = target.files[0]
    sourcePreviewUrl.value = URL.createObjectURL(target.files[0])
  }
}

const handleTargetSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    targetFile.value = target.files[0]
    targetPreviewUrl.value = URL.createObjectURL(target.files[0])
  }
}

const handleSourceDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    sourceFile.value = event.dataTransfer.files[0]
    sourcePreviewUrl.value = URL.createObjectURL(event.dataTransfer.files[0])
  }
}

const handleTargetDrop = (event: DragEvent) => {
  event.preventDefault()
  if (event.dataTransfer?.files && event.dataTransfer.files[0]) {
    targetFile.value = event.dataTransfer.files[0]
    targetPreviewUrl.value = URL.createObjectURL(event.dataTransfer.files[0])
  }
}

const clearSourceFile = () => {
  sourceFile.value = null
  sourcePreviewUrl.value = ''
}

const clearTargetFile = () => {
  targetFile.value = null
  targetPreviewUrl.value = ''
}

const handleFaceSwap = async () => {
  if (!sourceFile.value || !targetFile.value) return
  
  try {
    // 检查用户是否登录
    if (!authStore.isAuthenticated) {
      alert('请先登录后再使用功能')
      showAuthModal('login')
      return
    }

    // 检查积分是否足够
    const creditCheck = await authStore.checkCredits(15)
    if (!creditCheck.success) {
      alert(`积分不足！当前积分：${creditCheck.current_credits}，需要积分：15`)
      return
    }

    processing.value = true
    originalImage.value = URL.createObjectURL(sourceFile.value)
    
    // Call face swap API (placeholder - returns original image for now)
    const result = await ghibliStore.faceSwap(sourceFile.value, targetFile.value)
    
    resultImage.value = result
  } catch (error) {
    console.error('换脸失败:', error)
    const errorMessage = error instanceof Error ? error.message : '换脸失败，请重试'
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

/* 顶部导航栏 */
.top-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding: 12px 0;
}

.navbar-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  font-size: 1.5rem;
  font-weight: 700;
}

.user-area {
  display: flex;
  align-items: center;
  gap: 16px;
}

/* 用户菜单 */
.user-menu {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.user-dropdown {
  position: relative;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: all 0.2s ease;
}

.dropdown-trigger:hover {
  background: rgba(255, 255, 255, 0.1);
}

.username {
  font-weight: 500;
}

.dropdown-arrow {
  font-size: 0.8rem;
  transition: transform 0.2s ease;
}

.user-dropdown.open .dropdown-arrow {
  transform: rotate(180deg);
}

.dropdown-content {
  position: absolute;
  top: 100%;
  right: 0;
  background: rgba(26, 32, 44, 0.95);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 8px;
  min-width: 200px;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.2s ease;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.user-dropdown.open .dropdown-content {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.dropdown-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 8px;
  transition: all 0.2s ease;
  border: none;
  background: none;
  color: white;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.dropdown-item:hover {
  background: rgba(255, 255, 255, 0.1);
}

.credits-item {
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.2);
  cursor: default;
  color: #34d399;
  font-weight: 600;
  justify-content: center;
}

.credits-item:hover {
  background: rgba(74, 222, 128, 0.15);
}

.settings-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

/* 认证按钮 */
.auth-buttons {
  display: flex;
  gap: 12px;
}

.auth-btn {
  padding: 8px 20px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.login-btn:hover {
  border-color: rgba(59, 130, 246, 0.6);
  background: rgba(59, 130, 246, 0.1);
}

.register-btn:hover {
  border-color: rgba(147, 51, 234, 0.6);
  background: rgba(147, 51, 234, 0.1);
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
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.credits-cost {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.5);
  font-weight: 400;
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

/* Text to Image Inputs */
.text-to-image-inputs {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.input-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-group label {
  color: white;
  font-weight: 600;
  font-size: 1rem;
}

.input-field {
  padding: 12px 16px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  font-size: 1rem;
  resize: vertical;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.select-field {
  cursor: pointer;
  resize: none;
}

.select-field option {
  background: rgba(40, 40, 60, 0.95);
  color: white;
  padding: 8px;
}

.loading-hint, .warning-hint {
  font-size: 0.85rem;
  margin-top: 4px;
  padding: 4px 8px;
  border-radius: 6px;
}

.loading-hint {
  color: rgba(255, 255, 255, 0.7);
  background: rgba(120, 119, 198, 0.1);
}

.warning-hint {
  color: rgba(255, 200, 100, 0.9);
  background: rgba(255, 200, 100, 0.1);
}

.input-field:focus {
  outline: none;
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(120, 119, 198, 0.1);
  box-shadow: 0 0 0 3px rgba(120, 119, 198, 0.2);
}

.input-field::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.generate-btn {
  margin-top: 16px;
  min-height: 52px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.generate-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 200px;
}

.progress-text {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.progress-percent {
  font-size: 0.8rem;
  color: rgba(255, 255, 255, 0.8);
  text-align: center;
}

/* Upload Progress */
.upload-progress {
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.progress-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-width: 300px;
  text-align: center;
}

.progress-container .progress-text {
  font-size: 1.1rem;
  color: rgba(255, 255, 255, 0.9);
  font-weight: 500;
}

.progress-container .progress-bar {
  width: 100%;
  height: 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  overflow: hidden;
}

.progress-container .progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-container .progress-percent {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  font-weight: 600;
}

/* Text to Image Result */
.text-to-image-result {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.generated-image {
  max-width: 100%;
  border-radius: 20px;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.generated-image img {
  width: 100%;
  height: auto;
  display: block;
  max-width: 512px;
  max-height: 512px;
  object-fit: contain;
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

/* File Preview Styles */
.file-preview-container {
  margin: 24px 0;
  display: flex;
  justify-content: center;
}

.file-preview-card {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  max-width: 500px;
  width: 100%;
}

.file-preview-card:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(120, 119, 198, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
}

.preview-image-wrapper {
  width: 80px;
  height: 80px;
  border-radius: 12px;
  overflow: hidden;
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.1);
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}

.file-name {
  color: white;
  font-weight: 600;
  font-size: 1rem;
  word-break: break-word;
  line-height: 1.3;
}

.file-size {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.85rem;
}

.file-status {
  color: #4ade80;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.run-section {
  margin-top: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  align-items: center;
}

.run-btn {
  min-height: 52px;
  font-size: 1.1rem;
  padding: 16px 32px;
  width: 100%;
  max-width: 500px;
}

@media (max-width: 768px) {
  .file-preview-card {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .preview-image-wrapper {
    width: 120px;
    height: 120px;
    margin: 0 auto;
  }
  
  .run-btn {
    max-width: none;
  }
}

/* 认证相关样式 */
.auth-section {
  margin-top: 32px;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 16px;
  align-items: flex-start;
}

.user-welcome {
  color: white;
  font-size: 1.1rem;
  font-weight: 500;
  padding: 12px 20px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  backdrop-filter: blur(10px);
}

.user-credits {
  color: #4ade80;
  font-size: 1rem;
  font-weight: 600;
  padding: 8px 16px;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: 8px;
  backdrop-filter: blur(10px);
}

.auth-buttons {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.auth-btn {
  padding: 12px 24px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50px;
  background: rgba(255, 255, 255, 0.05);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 1rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.login-btn:hover {
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(120, 119, 198, 0.2);
  transform: translateY(-2px);
}

.register-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
}

.register-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
}

.logout-btn {
  border-color: rgba(255, 107, 107, 0.5);
  color: rgba(255, 107, 107, 0.9);
}

.logout-btn:hover {
  border-color: rgba(255, 107, 107, 0.8);
  background: rgba(255, 107, 107, 0.1);
  transform: translateY(-2px);
}

/* Face Swap Styles */
.face-swap-container {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.face-swap-uploads {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.face-swap-upload-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.face-swap-upload-section h4 {
  color: white;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.face-swap-upload-section p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  margin: 0;
}

.face-swap-upload-area {
  border: 2px dashed rgba(255, 255, 255, 0.3);
  border-radius: 16px;
  padding: 24px;
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.02);
}

.face-swap-upload-area:hover {
  border-color: rgba(120, 119, 198, 0.6);
  background: rgba(120, 119, 198, 0.05);
  transform: translateY(-2px);
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
}

.upload-icon {
  font-size: 3rem;
  opacity: 0.7;
}

.upload-text {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1rem;
}

.uploaded-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.preview-img {
  max-width: 100%;
  max-height: 150px;
  border-radius: 12px;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.file-name {
  color: white;
  font-size: 0.9rem;
  font-weight: 500;
  flex: 1;
  text-align: center;
  word-break: break-word;
}

.clear-btn {
  background: rgba(255, 107, 107, 0.2);
  border: 1px solid rgba(255, 107, 107, 0.4);
  color: rgba(255, 107, 107, 0.9);
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.8rem;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: rgba(255, 107, 107, 0.3);
  border-color: rgba(255, 107, 107, 0.6);
  transform: scale(1.1);
}

.face-swap-process {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}

.face-swap-btn {
  min-height: 52px;
  font-size: 1.1rem;
  padding: 16px 32px;
  width: 100%;
  max-width: 400px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 50px;
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.face-swap-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.face-swap-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none !important;
}

@media (max-width: 768px) {
  .face-swap-uploads {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .face-swap-upload-area {
    min-height: 160px;
    padding: 20px;
  }
  
  .upload-icon {
    font-size: 2.5rem;
  }
  
  .face-swap-btn {
    max-width: none;
  }
}
</style>
