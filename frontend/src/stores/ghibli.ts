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

interface AsyncTaskResponse {
  success: boolean
  message: string
  task_id: string
  prompt_id?: string
  estimated_time?: number
}

interface ProgressResponse {
  success: boolean
  task_id: string
  status: string  // 'pending', 'running', 'completed', 'failed'
  progress: number  // 0-100
  message: string
  result_url?: string
  error?: string
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
    availableProcessors: {} as Record<string, string>,
    // 新增状态用于进度跟踪
    currentTask: null as {
      taskId: string
      progress: number
      status: string
      message: string
    } | null,
    // 新增模型列表状态
    availableModels: [] as string[],
    modelsLoading: false
  }),
  
  actions: {
    async loadAvailableModels() {
      if (this.modelsLoading) return
      
      this.modelsLoading = true
      try {
        const response = await axios.get(`${API_BASE_URL}/api/comfyui-models`, {
          timeout: 15000
        })
        
        if (response.data.success) {
          this.availableModels = response.data.models || []
          console.log(`加载了 ${this.availableModels.length} 个可用模型`)
        } else {
          console.warn('获取模型列表失败:', response.data.message)
          this.availableModels = []
        }
      } catch (error) {
        console.error('获取模型列表失败:', error)
        this.availableModels = []
      } finally {
        this.modelsLoading = false
      }
    },

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

    async creativeUpscaleImage(file: File): Promise<string> {
      return this.processImage(file, 'creative_upscale')
    },

    async creativeUpscaleImageWithProgress(file: File): Promise<string> {
      this.isProcessing = true
      this.currentTask = null
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('processing_type', 'creative_upscale')
        
        // 1. 启动异步任务
        const response = await axios.post<AsyncTaskResponse>(
          `${API_BASE_URL}/api/process-async`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 10000 // 启动任务只需要很短时间
          }
        )
        
        if (!response.data.success) {
          throw new Error(response.data.message || '启动任务失败')
        }
        
        const taskId = response.data.task_id
        
        // 2. 初始化任务状态
        this.currentTask = {
          taskId,
          progress: 0,
          status: 'pending',
          message: '任务已创建...'
        }
        
        // 3. 轮询进度
        const result = await this.pollTaskProgress(taskId)
        
        // 4. 保存到历史记录
        this.processingHistory.push({
          original: URL.createObjectURL(file),
          result,
          timestamp: Date.now(),
          processingType: 'creative_upscale',
          processingTime: this.currentTask?.progress || 0
        })
        
        return result
        
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
        throw new Error('处理图像时发生未知错误')
      } finally {
        this.isProcessing = false
        this.currentTask = null
      }
    },
    
    async generateImageWithProgress(prompt: string, negativePrompt?: string, model?: string): Promise<string> {
      this.isProcessing = true
      this.currentTask = null
      
      try {
        const formData = new FormData()
        formData.append('prompt', prompt)
        if (negativePrompt) {
          formData.append('negative_prompt', negativePrompt)
        }
        if (model) {
          formData.append('model', model)
        }
        
        // 1. 启动异步任务
        const response = await axios.post<AsyncTaskResponse>(
          `${API_BASE_URL}/api/text-to-image-async`,
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data'
            },
            timeout: 10000 // 启动任务只需要很短时间
          }
        )
        
        if (!response.data.success) {
          throw new Error(response.data.message || '启动任务失败')
        }
        
        const taskId = response.data.task_id
        
        // 2. 初始化任务状态
        this.currentTask = {
          taskId,
          progress: 0,
          status: 'pending',
          message: '任务已创建...'
        }
        
        // 3. 轮询进度
        const result = await this.pollTaskProgress(taskId)
        
        // 4. 保存到历史记录
        this.processingHistory.push({
          original: '', // 文生图没有原图
          result,
          timestamp: Date.now(),
          processingType: 'text_to_image',
          processingTime: this.currentTask?.progress || 0
        })
        
        return result
        
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
        throw new Error('生成图像时发生未知错误')
      } finally {
        this.isProcessing = false
        this.currentTask = null
      }
    },

    async pollTaskProgress(taskId: string): Promise<string> {
      const maxPolls = 300 // 最多轮询5分钟 (300 * 1秒)
      let polls = 0
      
      while (polls < maxPolls) {
        try {
          const response = await axios.get<ProgressResponse>(
            `${API_BASE_URL}/api/progress/${taskId}`,
            { timeout: 5000 }
          )
          
          if (response.data.success) {
            // 更新任务状态
            if (this.currentTask && this.currentTask.taskId === taskId) {
              this.currentTask.progress = response.data.progress
              this.currentTask.status = response.data.status
              this.currentTask.message = response.data.message
            }
            
            // 检查任务状态
            if (response.data.status === 'completed' && response.data.result_url) {
              // 移除API基础URL前缀，因为我们直接使用相对路径显示图片
              const imageUrl = response.data.result_url;
              return imageUrl;
            } else if (response.data.status === 'failed') {
              throw new Error(response.data.error || '图像生成失败')
            }
          } else {
            throw new Error(response.data.message || '查询进度失败')
          }
          
        } catch (error) {
          console.warn('轮询进度出错:', error)
          // 继续轮询，除非是严重错误
          if (axios.isAxiosError(error) && error.response?.status === 404) {
            throw new Error('任务不存在或已过期')
          }
        }
        
        // 等待1秒后继续轮询
        await new Promise(resolve => setTimeout(resolve, 1000))
        polls++
      }
      
      throw new Error('图像生成超时，请重试')
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
          // 移除API基础URL前缀，因为我们直接使用相对路径显示图片
          const imageUrl = response.data.processed_image_url;
          
          this.processingHistory.push({
            original: '', // 文生图没有原图
            result: imageUrl,
            timestamp: Date.now(),
            processingType: response.data.processing_type,
            processingTime: response.data.processing_time
          })
          
          return imageUrl;
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
          // 移除API基础URL前缀，因为我们直接使用相对路径显示图片
          const imageUrl = response.data.processed_image_url;
          
          this.processingHistory.push({
            original: URL.createObjectURL(file),
            result: imageUrl,
            timestamp: Date.now(),
            processingType: response.data.processing_type,
            processingTime: response.data.processing_time
          })
          
          return imageUrl;
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