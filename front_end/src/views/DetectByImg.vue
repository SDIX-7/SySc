<template>
  <div class="page-container">
    <Menu />
    
    <div class="detection-layout">
      <div class="upload-section">
        <div class="section-header">
          <h2 class="section-title">数据采集</h2>
          <p class="section-subtitle">上传检测样本数据进行质量分析</p>
        </div>
        
        <div 
          class="upload-zone"
          :class="{ 'drag-over': isDragOver, 'has-file': uploadedFile }"
          @dragover.prevent="isDragOver = true"
          @dragleave.prevent="isDragOver = false"
          @drop.prevent="handleDrop"
          @click="triggerFileInput"
        >
          <input 
            type="file" 
            ref="fileInput" 
            accept="image/*" 
            @change="handleFileSelect"
            hidden 
          />
          
          <template v-if="!uploadedFile">
            <div class="upload-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <div class="upload-text">
              <span class="upload-title">拖拽图片到此处或点击上传</span>
              <span class="upload-hint">支持: JPG, PNG, BMP (最大 10MB)</span>
            </div>
          </template>
          
          <template v-else>
            <img :src="previewUrl" alt="Preview" class="preview-image" />
            <div class="file-info">
              <span class="file-name">{{ uploadedFile.name }}</span>
              <span class="file-size">{{ formatFileSize(uploadedFile.size) }}</span>
            </div>
          </template>
        </div>
        
        <div class="action-buttons">
          <button 
            v-if="uploadedFile" 
            class="btn-secondary"
            @click="clearFile"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M18 6L6 18M6 6l12 12"/>
            </svg>
            清除
          </button>
          <button 
            class="btn-primary"
            :disabled="!uploadedFile || isDetecting"
            @click="startDetection"
          >
            <template v-if="isDetecting">
              <span class="spinner"></span>
              检测中...
            </template>
            <template v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.35-4.35"/>
              </svg>
              开始检测
            </template>
          </button>
        </div>
      </div>
      
      <div class="result-section">
        <div class="section-header">
          <h2 class="section-title">检测结果</h2>
          <div v-if="detectionResult" class="result-status" :class="detectionResult.hasDefects ? 'danger' : 'success'">
            <span class="status-dot"></span>
            {{ detectionResult.hasDefects ? '发现缺陷' : '正常' }}
          </div>
        </div>
        
        <div class="result-container">
          <template v-if="!detectionResult">
            <div class="empty-state">
              <div class="empty-icon">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
              </div>
              <p class="empty-text">上传图片后查看检测结果</p>
            </div>
          </template>
          
          <template v-else>
            <div class="result-image-container">
              <img :src="resultImageUrl" alt="Detection Result" class="result-image" />
              <button class="download-btn" @click="downloadResult">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
              </button>
            </div>
            
            <div class="result-details">
              <div class="detail-item">
                <span class="detail-label">缺陷总数</span>
                <span class="detail-value">{{ detectionResult.detection_total_cnts }}</span>
              </div>
              <div class="detail-item" v-if="detectionResult.detection_classes?.length">
                <span class="detail-label">缺陷类型</span>
                <div class="defect-tags">
                  <span 
                    v-for="(type, index) in uniqueDefectTypes" 
                    :key="index" 
                    class="defect-tag"
                  >
                    {{ type }}
                  </span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import Menu from '@/components/Menu.vue'
import { detectByImg } from '@/api'

const fileInput = ref<HTMLInputElement>()
const uploadedFile = ref<File | null>(null)
const previewUrl = ref('')
const isDragOver = ref(false)
const isDetecting = ref(false)
const detectionResult = ref<any>(null)
const resultImageUrl = ref('')

const uniqueDefectTypes = computed(() => {
  if (!detectionResult.value?.detection_classes) return []
  return [...new Set(detectionResult.value.detection_classes)]
})

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) processFile(file)
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  const file = event.dataTransfer?.files[0]
  if (file && file.type.startsWith('image/')) {
    processFile(file)
  } else {
    ElMessage.warning('请上传图片文件')
  }
}

const processFile = (file: File) => {
  if (file.size > 10 * 1024 * 1024) {
    ElMessage.error('文件大小超过10MB限制')
    return
  }
  
  uploadedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  detectionResult.value = null
  resultImageUrl.value = ''
}

const clearFile = () => {
  uploadedFile.value = null
  previewUrl.value = ''
  detectionResult.value = null
  resultImageUrl.value = ''
  if (fileInput.value) fileInput.value.value = ''
}

const startDetection = async () => {
  if (!uploadedFile.value) return
  
  isDetecting.value = true
  
  try {
    const formData = new FormData()
    formData.append('file', uploadedFile.value)
    
    const response = await detectByImg(formData) as Blob
    resultImageUrl.value = URL.createObjectURL(response)
    
    detectionResult.value = {
      hasDefects: true,
      detection_total_cnts: 1,
      detection_classes: ['缺陷']
    }
    
    ElMessage.success('检测完成')
  } catch (error) {
    console.error('检测失败:', error)
    ElMessage.error('检测失败，请重试')
  } finally {
    isDetecting.value = false
  }
}

const downloadResult = () => {
  if (!resultImageUrl.value) return
  
  const link = document.createElement('a')
  link.href = resultImageUrl.value
  link.download = `检测结果_${Date.now()}.png`
  link.click()
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}
</script>

<style scoped>
.detection-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.section-subtitle {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.upload-section,
.result-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.upload-zone {
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  padding: 60px 40px;
  text-align: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.upload-zone::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.05) 0%, transparent 100%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.upload-zone:hover::before,
.upload-zone.drag-over::before {
  opacity: 1;
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: var(--accent-primary);
}

.upload-zone.has-file {
  padding: 20px;
}

.upload-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
  color: var(--accent-primary);
}

.upload-text {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-primary);
}

.upload-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: var(--radius-sm);
  object-fit: contain;
}

.file-info {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 16px;
  font-size: 0.875rem;
}

.file-name {
  color: var(--text-primary);
  font-weight: 500;
}

.file-size {
  color: var(--text-muted);
}

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 28px;
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-primary {
  flex: 1;
  background: var(--accent-gradient);
  border: none;
  color: var(--bg-primary);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 30px rgba(0, 212, 255, 0.3);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 100px;
  font-family: var(--font-mono);
  font-size: 11px;
  letter-spacing: 0.05em;
}

.result-status.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.result-status.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.result-container {
  min-height: 400px;
}

.empty-state {
  height: 400px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-text {
  font-size: 0.875rem;
}

.result-image-container {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-secondary);
}

.result-image {
  width: 100%;
  max-height: 400px;
  object-fit: contain;
}

.download-btn {
  position: absolute;
  bottom: 16px;
  right: 16px;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.download-btn:hover {
  background: var(--accent-primary);
  color: var(--bg-primary);
  border-color: var(--accent-primary);
}

.result-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-top: 24px;
}

.detail-item {
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  padding: 16px;
}

.detail-label {
  display: block;
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 8px;
}

.detail-value {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--accent-primary);
}

.defect-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.defect-tag {
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 100px;
  font-size: 0.75rem;
  color: var(--danger);
}

@media (max-width: 1200px) {
  .detection-layout {
    grid-template-columns: 1fr;
  }
}
</style>
