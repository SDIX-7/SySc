<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <button class="btn-back" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">数据采集</h1>
            <p class="page-subtitle">{{ line?.line_name }}</p>
          </div>
        </div>
      </div>
      
      <div class="upload-section">
        <div class="upload-tabs">
          <button 
            v-if="line?.data_type === 'attribute'"
            class="upload-tab" 
            :class="{ active: uploadType === 'image' }"
            @click="uploadType = 'image'"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <circle cx="8.5" cy="8.5" r="1.5"/>
              <polyline points="21 15 16 10 5 21"/>
            </svg>
            {{ line?.line_name || '产线' }}图像批量上传
          </button>
          <button 
            v-if="line?.data_type === 'measurement'"
            class="upload-tab" 
            :class="{ active: uploadType === 'excel' }"
            @click="uploadType = 'excel'"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
            </svg>
            测量数据上传
          </button>
        </div>
        
        <div class="data-type-notice" v-if="line?.data_type">
          <template v-if="line.data_type === 'attribute'">
            <span class="notice-icon">📷</span>
            <span>当前产线为<span class="highlight">计数型数据</span>采集模式，支持图像批量上传进行缺陷检测</span>
          </template>
          <template v-else-if="line.data_type === 'measurement'">
            <span class="notice-icon">📊</span>
            <span>当前产线为<span class="highlight">计量型数据</span>采集模式，支持Excel/CSV格式测量数据上传</span>
          </template>
        </div>
        
        <div v-if="uploadType === 'image'" class="upload-panel">
          <div class="upload-area" @click="triggerImageUpload" @dragover.prevent @drop.prevent="handleImageDrop">
            <input 
              type="file" 
              ref="imageInputRef" 
              accept="image/*" 
              multiple 
              style="display: none"
              @change="handleImageSelect"
            />
            <div class="upload-icon">
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <p class="upload-text">点击或拖拽上传PCB图像</p>
            <p class="upload-hint">支持 JPG, PNG, TIFF, BMP 格式，可一次性选择多个文件</p>
          </div>
          
          <div v-if="uploadQueue.length > 0" class="queue-section">
            <div class="queue-header">
              <h3 class="queue-title">
                上传队列 <span class="queue-count">({{ uploadQueue.length }} 个文件)</span>
              </h3>
              <div class="queue-actions">
                <button class="btn-clear" @click="clearQueue">清空队列</button>
                <button class="btn-upload-all" @click="startBatchUpload" :disabled="uploading">
                  {{ uploading ? '上传中...' : '开始批量检测' }}
                </button>
              </div>
            </div>
            
            <div class="progress-section" v-if="uploading">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: uploadProgress + '%' }"></div>
              </div>
              <div class="progress-info">
                <span>进度: {{ uploadProgress.toFixed(1) }}%</span>
                <span>已处理: {{ processedCount }}/{{ uploadQueue.length }}</span>
              </div>
            </div>
            
            <div class="queue-list">
              <div 
                v-for="(item, index) in uploadQueue" 
                :key="index" 
                class="queue-item"
                :class="{ 'uploading': item.status === 'uploading', 'done': item.status === 'done', 'error': item.status === 'error' }"
              >
                <div class="item-preview">
                  <img :src="item.preview" v-if="item.preview" />
                  <div class="file-icon" v-else>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                      <circle cx="8.5" cy="8.5" r="1.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                  </div>
                </div>
                <div class="item-info">
                  <span class="item-name">{{ item.name }}</span>
                  <span class="item-size">{{ formatFileSize(item.size) }}</span>
                  <span class="item-status" :class="item.status">
                    {{ getStatusText(item.status) }}
                  </span>
                </div>
                <div class="item-result" v-if="item.result">
                  <span class="defect-count" :class="{ 'has-defects': item.result.defect_count > 0 }">
                    {{ item.result.defect_count }} 个缺陷
                  </span>
                  <span class="defect-classes" v-if="item.result.classes && item.result.classes.length > 0">
                    {{ item.result.classes.join(', ') }}
                  </span>
                </div>
                <button class="btn-remove" @click="removeFromQueue(index)" :disabled="uploading">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          <div v-if="uploadResults.length > 0" class="results-section">
            <div class="results-header">
              <h3 class="results-title">检测结果汇总</h3>
              <button class="btn-clear" @click="clearResults">清除结果</button>
            </div>
            <div class="results-summary">
              <div class="summary-card">
                <span class="summary-value">{{ uploadResults.length }}</span>
                <span class="summary-label">总检测数</span>
              </div>
              <div class="summary-card success">
                <span class="summary-value">{{ resultsWithNoDefects }}</span>
                <span class="summary-label">无缺陷</span>
              </div>
              <div class="summary-card danger">
                <span class="summary-value">{{ resultsWithDefects }}</span>
                <span class="summary-label">有缺陷</span>
              </div>
              <div class="summary-card">
                <span class="summary-value">{{ totalDefects }}</span>
                <span class="summary-label">缺陷总数</span>
              </div>
            </div>
            <div class="results-grid">
              <div 
                v-for="(result, index) in uploadResults" 
                :key="index" 
                class="result-card"
                :class="{ 'has-defects': result.has_defects }"
              >
                <div class="result-image">
                  <img 
                    :src="result.image_path" 
                    v-if="result.image_path" 
                    @click="showPreview(result.image_path)"
                    class="preview-clickable"
                  />
                  <div class="no-image" v-else>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                      <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                      <circle cx="8.5" cy="8.5" r="1.5"/>
                      <polyline points="21 15 16 10 5 21"/>
                    </svg>
                  </div>
                </div>
                <div class="result-info">
                  <span class="result-filename">{{ result.filename }}</span>
                  <span class="result-defects" :class="{ 'text-danger': result.has_defects }">
                    {{ result.defect_count }} 个缺陷
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <el-dialog
          v-model="previewVisible"
          title="检测结果预览"
          width="80%"
          :before-close="closePreview"
          class="preview-dialog"
        >
          <div class="preview-container">
            <img :src="previewImage" class="preview-image" />
          </div>
        </el-dialog>
        
        <div v-if="uploadType === 'excel'" class="upload-panel">
          <div class="upload-area" @click="triggerExcelUpload">
            <input 
              type="file" 
              ref="excelInputRef" 
              accept=".xlsx,.xls,.csv" 
              style="display: none"
              @change="handleExcelSelect"
            />
            <div class="upload-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
              </svg>
            </div>
            <p class="upload-text">点击上传Excel/CSV文件</p>
            <p class="upload-hint">支持 .xlsx, .xls, .csv 格式</p>
          </div>
          
          <div v-if="excelData.length > 0" class="preview-section">
            <h3 class="preview-title">数据预览</h3>
            <div class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th v-for="col in excelHeaders" :key="col">{{ col }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in excelData.slice(0, 10)" :key="index">
                    <td v-for="col in excelHeaders" :key="col">{{ row[col] }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-if="excelData.length > 10" class="more-hint">... 还有 {{ excelData.length - 10 }} 行数据</p>
            <button class="btn-upload" @click="uploadExcelData" :loading="uploading">
              导入数据
            </button>
          </div>
        </div>
      </div>
      
      <div class="recent-section">
        <h2 class="section-title">最近采集数据</h2>
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>检测结果</th>
                <th>样本编号</th>
                <th>数据类型</th>
                <th>样本数量</th>
                <th>缺陷数量</th>
                <th>采集时间</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in recentData" :key="item.id">
                <td class="result-thumb-cell">
                  <img 
                    v-if="getRecentDataThumbnail(item)" 
                    :src="getRecentDataThumbnail(item)" 
                    class="result-thumb"
                    @click="showPreview(getRecentDataFullImage(item)!)"
                  />
                  <span v-else class="no-result">-</span>
                </td>
                <td>{{ item.sample_id }}</td>
                <td>{{ item.sample_size > 1 ? '批量数据' : '单样本' }}</td>
                <td>{{ item.sample_size }}</td>
                <td :class="{ 'text-danger': item.defect_count > 0 }">{{ item.defect_count }}</td>
                <td>{{ formatTime(item.inspection_time) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-if="recentData.length === 0" class="empty-table">
            <p>暂无采集数据</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as XLSX from 'xlsx'
import Menu from '@/components/Menu.vue'
import { getProductionLine, getAttributeData, createAttributeData } from '@/api'
import type { ProductionLine, AttributeData } from '@/types'

interface UploadItem {
  file: File
  name: string
  size: number
  preview: string
  status: 'pending' | 'uploading' | 'done' | 'error'
  result?: {
    defect_count: number
    classes: string[]
    has_defects: boolean
    image_path?: string
  }
  error?: string
}

interface UploadResult {
  filename: string
  has_defects: boolean
  defect_count: number
  classes: string[]
  image_path?: string
}

const route = useRoute()
const router = useRouter()

const lineId = Number(route.params.id)
const line = ref<ProductionLine | null>(null)
const recentData = ref<AttributeData[]>([])

const uploadType = ref<'image' | 'excel'>('image')
const imageInputRef = ref<HTMLInputElement | null>(null)
const excelInputRef = ref<HTMLInputElement | null>(null)

const uploadQueue = ref<UploadItem[]>([])
const uploadResults = ref<UploadResult[]>([])
const uploading = ref(false)
const uploadProgress = ref(0)
const processedCount = ref(0)

const previewVisible = ref(false)
const previewImage = ref('')

const excelHeaders = ref<string[]>([])
const excelData = ref<any[]>([])

const resultsWithNoDefects = computed(() => uploadResults.value.filter(r => !r.has_defects).length)
const resultsWithDefects = computed(() => uploadResults.value.filter(r => r.has_defects).length)
const totalDefects = computed(() => uploadResults.value.reduce((sum, r) => sum + r.defect_count, 0))

const fetchData = async () => {
  try {
    const [lineRes, attrRes] = await Promise.all([
      getProductionLine(lineId),
      getAttributeData(lineId)
    ])
    
    line.value = lineRes as ProductionLine
    recentData.value = (attrRes as AttributeData[]).slice(0, 10)
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const triggerImageUpload = () => {
  imageInputRef.value?.click()
}

const handleImageSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFilesToQueue(Array.from(input.files))
  }
}

const handleImageDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files) {
    addFilesToQueue(Array.from(e.dataTransfer.files))
  }
}

const addFilesToQueue = (files: File[]) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/tiff', 'image/bmp']
  
  files.forEach(file => {
    if (!allowedTypes.includes(file.type)) {
      ElMessage.warning(`不支持的文件格式: ${file.name}`)
      return
    }
    
    if (file.size > 10 * 1024 * 1024) {
      ElMessage.warning(`文件过大: ${file.name} (最大10MB)`)
      return
    }
    
    const reader = new FileReader()
    reader.onload = (e) => {
      uploadQueue.value.push({
        file,
        name: file.name,
        size: file.size,
        preview: e.target?.result as string,
        status: 'pending'
      })
    }
    reader.readAsDataURL(file)
  })
}

const removeFromQueue = (index: number) => {
  uploadQueue.value.splice(index, 1)
}

const clearQueue = () => {
  uploadQueue.value = []
}

const clearResults = () => {
  uploadResults.value = []
}

const startBatchUpload = async () => {
  if (uploadQueue.value.length === 0) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }
  
  uploading.value = true
  uploadProgress.value = 0
  processedCount.value = 0
  uploadResults.value = []
  
  const totalFiles = uploadQueue.value.length
  
  for (let i = 0; i < totalFiles; i++) {
    const item = uploadQueue.value[i]
    item.status = 'uploading'
    
    const formData = new FormData()
    formData.append('files', item.file)
    formData.append('line_id', String(lineId))
    
    try {
      const response = await fetch('/api/images/batch-detect', {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('上传失败')
      }
      
      const result = await response.json()
      
      if (result.results && result.results.length > 0) {
        const r = result.results[0]
        item.status = 'done'
        item.result = {
          defect_count: r.defect_count,
          classes: r.classes || [],
          has_defects: r.has_defects,
          image_path: r.image_path
        }
        uploadResults.value.push(r)
      }
      
      if (result.errors && result.errors.length > 0) {
        item.status = 'error'
        item.error = result.errors[0].error
      }
      
    } catch (error) {
      console.error('上传失败:', error)
      item.status = 'error'
      item.error = '上传失败'
    }
    
    processedCount.value = i + 1
    uploadProgress.value = Math.round(((i + 1) / totalFiles) * 100)
  }
  
  const summary = {
    images_with_defects: uploadResults.value.filter(r => r.has_defects).length,
    total_defects: uploadResults.value.reduce((sum, r) => sum + r.defect_count, 0)
  }
  
  ElMessage.success(`检测完成: ${summary.images_with_defects} 个有缺陷，共 ${summary.total_defects} 个缺陷`)
  
  uploading.value = false
  fetchData()
}

const formatFileSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '等待上传',
    uploading: '检测中...',
    done: '已完成',
    error: '上传失败'
  }
  return map[status] || status
}

const triggerExcelUpload = () => {
  excelInputRef.value?.click()
}

const handleExcelSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    const file = input.files[0]
    const reader = new FileReader()
    
    reader.onload = (e) => {
      try {
        const data = e.target?.result
        const workbook = XLSX.read(data, { type: 'binary' })
        const sheetName = workbook.SheetNames[0]
        const sheet = workbook.Sheets[sheetName]
        const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as any[][]
        
        if (jsonData.length > 0) {
          excelHeaders.value = jsonData[0].map((h: any) => String(h))
          const rows = jsonData.slice(1).map(row => {
            const obj: any = {}
            excelHeaders.value.forEach((header, i) => {
              obj[header] = row[i]
            })
            return obj
          })
          excelData.value = rows
        }
      } catch (error) {
        console.error('解析Excel失败:', error)
        ElMessage.error('文件格式错误')
      }
    }
    
    reader.onerror = () => {
      ElMessage.error('读取文件失败')
    }
    
    reader.readAsBinaryString(file)
  }
}

const uploadExcelData = async () => {
  if (excelData.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }
  
  uploading.value = true
  
  try {
    const sampleId = `MEASURE-${Date.now()}`
    const values: number[] = []
    
    const valueColumn = excelHeaders.value.find(h => 
      h.toLowerCase().includes('value') || 
      h.toLowerCase().includes('测量') ||
      h.toLowerCase().includes('数据')
    ) || excelHeaders.value[1]
    
    excelData.value.forEach(row => {
      const val = parseFloat(row[valueColumn])
      if (!isNaN(val)) {
        values.push(val)
      }
    })
    
    await createAttributeData({
      line_id: lineId,
      sample_id: sampleId,
      sample_size: values.length,
      defect_count: 0,
      inspector: 'Excel导入'
    })
    
    ElMessage.success('数据导入成功')
    excelData.value = []
    excelHeaders.value = []
    fetchData()
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  } finally {
    uploading.value = false
  }
}

const formatTime = (time?: string) => {
  if (!time) return '–'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getRecentDataThumbnail = (item: AttributeData): string | null => {
  if (item.defect_details?.thumbnail_path) {
    return item.defect_details.thumbnail_path
  }
  if (item.defect_count > 0) {
    return `/results/thumbnails/${item.sample_id}.png`
  }
  return null
}

const getRecentDataFullImage = (item: AttributeData): string | null => {
  if (item.defect_details?.image_path) {
    return item.defect_details.image_path
  }
  if (item.defect_count > 0) {
    return `/results/images/${item.sample_id}.png`
  }
  return null
}

const goBack = () => {
  router.push(`/production-lines/${lineId}`)
}

const showPreview = (imagePath: string) => {
  previewImage.value = imagePath
  previewVisible.value = true
}

const closePreview = () => {
  previewVisible.value = false
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-content {
  padding: 40px;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-back {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-back:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.page-subtitle {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--accent-primary);
}

.upload-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 32px;
}

.upload-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.upload-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.upload-tab:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.upload-tab.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: var(--bg-primary);
}

.upload-panel {
  min-height: 300px;
}

.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px;
  background: var(--bg-secondary);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.upload-area:hover {
  border-color: var(--accent-primary);
  background: rgba(0, 212, 255, 0.05);
}

.upload-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
}

.upload-text {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.upload-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.queue-section {
  margin-top: 24px;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.queue-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.queue-count {
  font-weight: 400;
  color: var(--text-muted);
}

.queue-actions {
  display: flex;
  gap: 12px;
}

.btn-clear {
  padding: 8px 16px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-clear:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.btn-upload-all {
  padding: 8px 24px;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-upload-all:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.btn-upload-all:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.progress-section {
  margin-bottom: 16px;
}

.progress-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--accent-gradient);
  transition: width 0.3s ease;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.queue-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
}

.queue-item.uploading {
  border-color: var(--accent-primary);
}

.queue-item.done {
  border-color: var(--success);
}

.queue-item.error {
  border-color: var(--danger);
}

.item-preview {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-card);
}

.item-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.file-icon {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.item-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.item-name {
  font-size: 0.875rem;
  color: var(--text-primary);
  font-family: var(--font-mono);
}

.item-size {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.item-status {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.item-status.done {
  color: var(--success);
}

.item-status.error {
  color: var(--danger);
}

.item-result {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.defect-count {
  font-size: 0.875rem;
  color: var(--success);
}

.defect-count.has-defects {
  color: var(--danger);
}

.defect-classes {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.btn-remove {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  border-radius: var(--radius-sm);
}

.btn-remove:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.btn-remove:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.results-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.results-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.results-summary {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.summary-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.summary-card.success .summary-value {
  color: var(--success);
}

.summary-card.danger .summary-value {
  color: var(--danger);
}

.summary-value {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.summary-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 12px;
}

.result-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.result-card.has-defects {
  border-color: var(--danger);
}

.result-image {
  width: 100%;
  aspect-ratio: 1;
  background: var(--bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image {
  color: var(--text-muted);
}

.result-info {
  padding: 8px;
}

.result-filename {
  display: block;
  font-size: 0.75rem;
  color: var(--text-primary);
  font-family: var(--font-mono);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-defects {
  font-size: 0.75rem;
  color: var(--success);
}

.text-danger {
  color: var(--danger);
}

.preview-clickable {
  cursor: pointer;
  transition: transform 0.2s ease;
}

.preview-clickable:hover {
  transform: scale(1.05);
}

.preview-container {
  display: flex;
  justify-content: center;
  align-items: center;
  background: var(--bg-dark);
  border-radius: var(--radius-md);
  padding: 20px;
}

.preview-image {
  max-width: 100%;
  max-height: 80vh;
  object-fit: contain;
  border-radius: var(--radius-sm);
}

.preview-section {
  margin-top: 24px;
}

.preview-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.table-container {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 12px 16px;
  font-size: 0.875rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.empty-table {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.result-thumb-cell {
  padding: 8px !important;
}

.result-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: transform 0.2s ease;
  border: 1px solid var(--border-color);
}

.result-thumb:hover {
  transform: scale(1.1);
}

.no-result {
  color: var(--text-muted);
  font-size: 0.875rem;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.recent-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.btn-upload {
  padding: 12px 32px;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
  margin-top: 16px;
}

.btn-upload:hover {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.more-hint {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
  padding: 12px;
}

@media (max-width: 1200px) {
  .results-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
