import { defineStore } from 'pinia'
import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

interface ProcessingResult {
  success: boolean
  message: string
  processed_image_url?: string
  processing_type: string
  processing_time: number
}

export const useGhibliStore = defineStore('ghibli', {
  state: () => ({
    isProcessing: false,
    processingHistory: [] as Array<{
      original: string
      result: string
      timestamp: number
      processingType: string
      processingTime: number
    }>,
    availableProcessors: {} as Record<string, string>
  }),
  
  actions: {
    async loadAvailableProcessors() {
      try {
        const response = await axios.get(`${API_BASE_URL}/api/processors`)
        if (response.data.success) {
          this.availableProcessors = response.data.processors
        }
      } catch (error) {
        console.error('获取处理器列表失败:', error)
      }
    },
    
    async convertToGhibliStyle(file: File): Promise<string> {
      return this.processImage(file, 'ghibli_style')
    },
    
    async convertToGrayscale(file: File): Promise<string> {
      return this.processImage(file, 'grayscale')
    },
    
    async upscaleImage(file: File, scaleFactor: number = 2): Promise<string> {
      return this.processImage(file, 'upscale', { scale_factor: scaleFactor })
    },
    
    async generateImage(prompt: string, negativePrompt?: string, model?: string): Promise<string> {
      this.isProcessing = true
      
      try {
        const formData = new FormData()
        formData.append('prompt', prompt)
        if (negativePrompt) {
          formData.append('negative_prompt', negativePrompt)
        }
        if (model) {
          formData.append('model', model)
        }
        
        const response = await axios.post<ProcessingResult>(
          `${API_BASE_URL}/api/text-to-image`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 120000 // 2分钟超时，因为文生图可能较慢
          }
        )
        
        if (response.data.success && response.data.processed_image_url) {
          const fullImageUrl = `${API_BASE_URL}${response.data.processed_image_url}`
          
          this.processingHistory.push({
            original: '', // 文生图没有原图
            result: fullImageUrl,
            timestamp: Date.now(),
            processingType: response.data.processing_type,
            processingTime: response.data.processing_time
          })
          
          return fullImageUrl
        } else {
          throw new Error(response.data.message || '文生图失败')
        }
      } catch (error) {
        if (axios.isAxiosError(error)) {
          if (error.code === 'ECONNABORTED') {
            throw new Error('请求超时，图像生成可能需要更长时间')
          } else if (error.response) {
            throw new Error(error.response.data?.detail || '服务器错误')
          } else if (error.request) {
            throw new Error('无法连接到服务器，请检查网络连接')
          }
        }
        throw new Error('生成图像时发生未知错误')
      } finally {
        this.isProcessing = false
      }
    },
    
    async processImage(file: File, processingType: string, parameters?: Record<string, any>): Promise<string> {
      this.isProcessing = true
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('processing_type', processingType)
        
        if (parameters) {
          formData.append('parameters', JSON.stringify(parameters))
        }
        
        const response = await axios.post<ProcessingResult>(
          `${API_BASE_URL}/api/process`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 30000
          }
        )
        
        if (response.data.success && response.data.processed_image_url) {
          const fullImageUrl = `${API_BASE_URL}${response.data.processed_image_url}`
          
          this.processingHistory.push({
            original: URL.createObjectURL(file),
            result: fullImageUrl,
            timestamp: Date.now(),
            processingType: response.data.processing_type,
            processingTime: response.data.processing_time
          })
          
          return fullImageUrl
        } else {
          throw new Error(response.data.message || '处理失败')
        }
      } catch (error) {
        if (axios.isAxiosError(error)) {
          if (error.code === 'ECONNABORTED') {
            throw new Error('请求超时，请重试')
          } else if (error.response) {
            throw new Error(error.response.data?.detail || '服务器错误')
          } else if (error.request) {
            throw new Error('无法连接到服务器，请检查网络连接')
          }
        }
        throw new Error('处理图片时发生未知错误')
      } finally {
        this.isProcessing = false
      }
    },
    
    getProcessingHistory() {
      return this.processingHistory
    },
    
    clearHistory() {
      this.processingHistory = []
    }
  }
})