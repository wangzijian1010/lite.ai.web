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
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 20px;
}

.upload-content {
  text-align: center;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 20px;
  animation: pulse 2s infinite;
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
  font-size: 1.4rem;
  color: white;
  margin-bottom: 12px;
  font-weight: 600;
}

.upload-content p {
  color: rgba(255, 255, 255, 0.6);
  font-size: 1rem;
}

.loading-content {
  display: flex;
  align-items: center;
  gap: 20px;
  color: white;
  font-size: 1.1rem;
}

.file-info {
  margin-top: 20px;
  padding: 16px;
  background: rgba(120, 119, 198, 0.1);
  border-radius: 12px;
  font-size: 0.95rem;
  border: 1px solid rgba(120, 119, 198, 0.2);
}

.file-info p {
  margin: 6px 0;
  color: rgba(255, 255, 255, 0.8);
}

.file-info strong {
  color: white;
}
</style>