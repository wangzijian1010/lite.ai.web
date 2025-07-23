<template>
  <div class="image-upload">
    <div 
      class="upload-area"
      :class="{ dragover: isDragging }"
      @click="triggerFileInput"
      @drop="handleDrop"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
    >
      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        @change="handleFileSelect"
        style="display: none"
      />
      
      <div v-if="!loading" class="upload-content">
        <div class="upload-icon">📸</div>
        <h3>点击或拖拽上传图片</h3>
        <p>支持 JPG、PNG、WebP 格式，最大 10MB</p>
      </div>
      
      <div v-else class="loading-content">
        <div class="loading"></div>
        <p>处理中...</p>
      </div>
    </div>
    
    <div v-if="selectedFile" class="file-info">
      <p><strong>已选择:</strong> {{ selectedFile.name }}</p>
      <p><strong>大小:</strong> {{ formatFileSize(selectedFile.size) }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  loading: false
})

const emit = defineEmits<{
  upload: [file: File]
}>()

const fileInput = ref<HTMLInputElement>()
const isDragging = ref(false)
const selectedFile = ref<File | null>(null)

const triggerFileInput = () => {
  if (!props.loading) {
    fileInput.value?.click()
  }
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    processFile(file)
  }
}

const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragging.value = false
  
  if (props.loading) return
  
  const file = event.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  if (!props.loading) {
    isDragging.value = true
  }
}

const handleDragLeave = () => {
  isDragging.value = false
}

const processFile = (file: File) => {
  if (file.size > 10 * 1024 * 1024) {
    alert('文件大小不能超过 10MB')
    return
  }
  
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }
  
  selectedFile.value = file
  emit('upload', file)
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.upload-area {
  min-height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 24px;
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.upload-area::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.1), rgba(139, 92, 246, 0.1));
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: -1;
}

.upload-area:hover {
  border-color: rgba(96, 165, 250, 0.5);
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.upload-area:hover::before {
  opacity: 1;
}

.upload-area.dragover {
  border-color: #60a5fa;
  background: rgba(96, 165, 250, 0.1);
  box-shadow: 0 10px 30px rgba(96, 165, 250, 0.2);
}

.upload-content {
  text-align: center;
  padding: 20px;
  z-index: 1;
}

.upload-icon {
  font-size: 5rem;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
  background: linear-gradient(135deg, #60a5fa, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
}

.upload-content h3 {
  font-size: 1.75rem;
  color: white;
  margin-bottom: 16px;
  font-weight: 700;
}

.upload-content p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 1.1rem;
  max-width: 400px;
  line-height: 1.6;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
  color: white;
  font-size: 1.25rem;
  padding: 40px;
}

.loading-text {
  font-weight: 500;
}

.file-info {
  margin-top: 30px;
  padding: 20px;
  background: rgba(30, 41, 59, 0.6);
  border-radius: 16px;
  font-size: 1rem;
  border: 1px solid rgba(96, 165, 250, 0.3);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
  animation: slideUp 0.4s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.file-info p {
  margin: 8px 0;
  color: rgba(255, 255, 255, 0.85);
}

.file-info strong {
  color: white;
  font-weight: 600;
}
</style>