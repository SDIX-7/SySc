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
            <h1 class="page-title">新建能力分析</h1>
            <p class="page-subtitle">{{ line?.line_name || '加载中...' }}</p>
          </div>
        </div>
      </div>

      <div class="form-container">
        <div class="form-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
            </span>
            基本信息
          </h2>
          
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">分析名称</label>
              <el-input 
                v-model="form.analysis_name" 
                placeholder="请输入分析名称（可选）"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label">分析类型</label>
              <el-select v-model="form.analysis_type" class="form-input">
                <el-option label="过程能力分析" value="process" />
                <el-option label="机器能力分析" value="machine" />
                <el-option label="预分析" value="preliminary" />
              </el-select>
            </div>
          </div>
        </div>

        <div class="form-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </span>
            规格限设置
          </h2>
          
          <div class="spec-visual">
            <div class="spec-bar">
              <div class="spec-region lsl" :style="{ width: '20%' }">
                <span class="spec-label">LSL</span>
              </div>
              <div class="spec-region target">
                <span class="spec-label">Target</span>
              </div>
              <div class="spec-region usl" :style="{ width: '20%' }">
                <span class="spec-label">USL</span>
              </div>
            </div>
          </div>
          
          <div class="form-grid spec-grid">
            <div class="form-group">
              <label class="form-label required">规格上限 (USL)</label>
              <el-input-number 
                v-model="form.usl" 
                :precision="4" 
                :step="0.1"
                placeholder="请输入USL"
                class="form-input"
                :class="{ 'is-error': errors.usl }"
              />
              <span class="error-text" v-if="errors.usl">{{ errors.usl }}</span>
            </div>
            
            <div class="form-group">
              <label class="form-label required">目标值 (Target)</label>
              <el-input-number 
                v-model="form.target" 
                :precision="4" 
                :step="0.1"
                placeholder="请输入目标值（可选）"
                class="form-input"
              />
            </div>
            
            <div class="form-group">
              <label class="form-label required">规格下限 (LSL)</label>
              <el-input-number 
                v-model="form.lsl" 
                :precision="4" 
                :step="0.1"
                placeholder="请输入LSL"
                class="form-input"
                :class="{ 'is-error': errors.lsl }"
              />
              <span class="error-text" v-if="errors.lsl">{{ errors.lsl }}</span>
            </div>
          </div>
          
          <div class="form-group machine-sigma" v-if="form.analysis_type === 'machine'">
            <label class="form-label">机器标准差 (σ_machine)</label>
            <el-input-number 
              v-model="form.sigma_machine" 
              :precision="4" 
              :step="0.01"
              placeholder="请输入机器标准差（可选）"
              class="form-input"
            />
            <span class="form-hint">用于计算机器能力指数 Cm 和 Cmk</span>
          </div>
        </div>

        <div class="form-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </span>
            数据输入
          </h2>
          
          <div class="data-source-tabs">
            <button 
              class="source-tab" 
              :class="{ active: dataSource === 'import' }"
              @click="dataSource = 'import'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              从产线导入
            </button>
            <button 
              class="source-tab" 
              :class="{ active: dataSource === 'manual' }"
              @click="dataSource = 'manual'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 20h9"/>
                <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
              </svg>
              手动输入
            </button>
            <button 
              class="source-tab" 
              :class="{ active: dataSource === 'file' }"
              @click="dataSource = 'file'"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              文件上传
            </button>
          </div>

          <div class="data-input-area">
            <div v-if="dataSource === 'import'" class="import-panel">
              <div class="import-info">
                <p class="import-text">从产线 <strong>{{ line?.line_name }}</strong> 导入测量数据</p>
                <p class="import-count" v-if="measurementData.length > 0">
                  可用数据: <strong>{{ measurementData.length }}</strong> 条记录，
                  共 <strong>{{ totalDataPoints }}</strong> 个数据点
                </p>
              </div>
              
              <div class="import-options">
                <div class="option-group">
                  <label class="option-label">数据范围</label>
                  <el-select v-model="importRange" class="option-select">
                    <el-option label="最近 25 条" :value="25" />
                    <el-option label="最近 50 条" :value="50" />
                    <el-option label="最近 100 条" :value="100" />
                    <el-option label="全部数据" :value="0" />
                  </el-select>
                </div>
              </div>
              
              <button class="btn-import" @click="importFromLine" :disabled="measurementData.length === 0">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                导入数据
              </button>
            </div>

            <div v-if="dataSource === 'manual'" class="manual-panel">
              <el-input
                v-model="manualDataText"
                type="textarea"
                :rows="6"
                placeholder="请输入测量数据，每行一个数值或用逗号分隔&#10;例如:&#10;10.2, 10.5, 10.3, 10.4&#10;或&#10;10.2&#10;10.5&#10;10.3"
                class="manual-input"
              />
              <div class="manual-actions">
                <button class="btn-parse" @click="parseManualData">
                  解析数据
                </button>
                <span class="parsed-count" v-if="form.data_values.length > 0">
                  已解析 <strong>{{ form.data_values.length }}</strong> 个数据点
                </span>
              </div>
            </div>

            <div v-if="dataSource === 'file'" class="file-panel">
              <div class="file-drop-zone" @click="triggerFileUpload" @dragover.prevent @drop.prevent="handleFileDrop">
                <input 
                  type="file" 
                  ref="fileInputRef" 
                  accept=".txt,.csv,.xlsx,.xls" 
                  style="display: none"
                  @change="handleFileSelect"
                />
                <div class="drop-icon">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="16" y1="13" x2="8" y2="13"/>
                    <line x1="16" y1="17" x2="8" y2="17"/>
                  </svg>
                </div>
                <p class="drop-text">点击或拖拽上传数据文件</p>
                <p class="drop-hint">支持 .txt, .csv, .xlsx 格式</p>
              </div>
              <div v-if="uploadedFileName" class="file-info">
                <span class="file-name">{{ uploadedFileName }}</span>
                <span class="file-count">{{ form.data_values.length }} 个数据点</span>
              </div>
            </div>
          </div>

          <div v-if="form.data_values.length > 0" class="data-preview">
            <div class="preview-header">
              <h3 class="preview-title">数据预览</h3>
              <div class="preview-stats">
                <span class="stat-item">
                  <span class="stat-label">样本数</span>
                  <span class="stat-value">{{ form.data_values.length }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">最小值</span>
                  <span class="stat-value">{{ minValue.toFixed(4) }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">最大值</span>
                  <span class="stat-value">{{ maxValue.toFixed(4) }}</span>
                </span>
                <span class="stat-item">
                  <span class="stat-label">平均值</span>
                  <span class="stat-value">{{ meanValue.toFixed(4) }}</span>
                </span>
              </div>
            </div>
            <div class="preview-data">
              <span 
                v-for="(val, idx) in form.data_values.slice(0, 50)" 
                :key="idx" 
                class="data-point"
                :class="{ 
                  'out-of-spec': isOutOfSpec(val),
                  'near-spec': isNearSpec(val)
                }"
              >
                {{ val.toFixed(3) }}
              </span>
              <span v-if="form.data_values.length > 50" class="more-data">
                +{{ form.data_values.length - 50 }} 更多...
              </span>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button class="btn-cancel" @click="goBack">
            取消
          </button>
          <button 
            class="btn-submit" 
            @click="submitAnalysis" 
            :disabled="!isFormValid || submitting"
          >
            <svg v-if="submitting" class="loading-spinner" width="20" height="20" viewBox="0 0 24 24">
              <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.4" stroke-dashoffset="10">
                <animateTransform attributeName="transform" type="rotate" from="0 12 12" to="360 12 12" dur="1s" repeatCount="indefinite"/>
              </circle>
            </svg>
            <span v-else>开始分析</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { showMessage } from '@/utils/dialog'
import * as XLSX from 'xlsx'
import Menu from '@/components/Menu.vue'
import { getProductionLine, getMeasurementData, createCapabilityAnalysis, getCapabilityAnalyses } from '@/api'
import type { ProductionLine, MeasurementData, CapabilityAnalysisCreate, CapabilityAnalysis } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = Number(route.params.id)
const line = ref<ProductionLine | null>(null)
const measurementData = ref<MeasurementData[]>([])
const lastAnalysis = ref<CapabilityAnalysis | null>(null)

const form = ref<CapabilityAnalysisCreate>({
  line_id: lineId,
  analysis_name: '',
  usl: 0,
  lsl: 0,
  target: undefined,
  sigma_machine: undefined,
  data_values: [],
  analysis_type: 'process'
})

const errors = ref<Record<string, string>>({})
const dataSource = ref<'import' | 'manual' | 'file'>('import')
const manualDataText = ref('')
const importRange = ref(50)
const fileInputRef = ref<HTMLInputElement | null>(null)
const uploadedFileName = ref('')
const submitting = ref(false)

const totalDataPoints = computed(() => {
  return measurementData.value.reduce((sum, m) => sum + m.measurement_values.length, 0)
})

const minValue = computed(() => {
  if (form.value.data_values.length === 0) return 0
  return Math.min(...form.value.data_values)
})

const maxValue = computed(() => {
  if (form.value.data_values.length === 0) return 0
  return Math.max(...form.value.data_values)
})

const meanValue = computed(() => {
  if (form.value.data_values.length === 0) return 0
  const sum = form.value.data_values.reduce((a, b) => a + b, 0)
  return sum / form.value.data_values.length
})

const isFormValid = computed(() => {
  return (
    form.value.usl > form.value.lsl &&
    form.value.data_values.length >= 2 &&
    Object.keys(errors.value).length === 0
  )
})

const fetchData = async () => {
  try {
    const [lineRes, measureRes, analysesRes] = await Promise.all([
      getProductionLine(lineId),
      getMeasurementData(lineId),
      getCapabilityAnalyses(lineId)
    ])
    
    line.value = lineRes as ProductionLine
    
    if (line.value?.data_type === 'attribute') {
      showMessage.error('计数型数据产线不支持过程能力分析')
      router.push(`/production-lines/${lineId}`)
      return
    }
    
    measurementData.value = (measureRes as MeasurementData[]).reverse()
    
    const analyses = analysesRes as CapabilityAnalysis[]
    if (analyses && analyses.length > 0) {
      lastAnalysis.value = analyses[0]
    }
  } catch (error) {
    console.error('获取数据失败:', error)
    showMessage.error('获取产线数据失败')
  }
}

const importFromLine = () => {
  let data = measurementData.value
  if (importRange.value > 0) {
    data = data.slice(0, importRange.value)
  }
  
  const values: number[] = []
  data.forEach(m => {
    values.push(...m.measurement_values)
  })
  
  form.value.data_values = values
  
  if (lastAnalysis.value && form.value.usl === 0 && form.value.lsl === 0) {
    form.value.usl = parseFloat(lastAnalysis.value.usl)
    form.value.lsl = parseFloat(lastAnalysis.value.lsl)
    form.value.target = lastAnalysis.value.target ? parseFloat(lastAnalysis.value.target) : undefined
    showMessage.success(`已导入 ${values.length} 个数据点，已从上次分析记录获取规格限`)
  } else {
    showMessage.success(`已导入 ${values.length} 个数据点`)
  }
}

const parseManualData = () => {
  const text = manualDataText.value.trim()
  if (!text) {
    showMessage.warning('请输入数据')
    return
  }
  
  const values: number[] = []
  const lines = text.split(/[\n,;]+/)
  
  lines.forEach(line => {
    const val = parseFloat(line.trim())
    if (!isNaN(val)) {
      values.push(val)
    }
  })
  
  if (values.length === 0) {
    showMessage.error('未能解析到有效数据')
    return
  }
  
  form.value.data_values = values
  showMessage.success(`已解析 ${values.length} 个数据点`)
}

const triggerFileUpload = () => {
  fileInputRef.value?.click()
}

const handleFileSelect = (e: Event) => {
  const input = e.target as HTMLInputElement
  if (input.files && input.files[0]) {
    processFile(input.files[0])
  }
}

const handleFileDrop = (e: DragEvent) => {
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    processFile(e.dataTransfer.files[0])
  }
}

const processFile = (file: File) => {
  uploadedFileName.value = file.name
  
  const ext = file.name.split('.').pop()?.toLowerCase()
  
  if (ext === 'txt' || ext === 'csv') {
    const reader = new FileReader()
    reader.onload = (e) => {
      const text = e.target?.result as string
      const values: number[] = []
      text.split(/[\n,;]+/).forEach(line => {
        const val = parseFloat(line.trim())
        if (!isNaN(val)) values.push(val)
      })
      form.value.data_values = values
      showMessage.success(`已解析 ${values.length} 个数据点`)
    }
    reader.readAsText(file)
  } else if (ext === 'xlsx' || ext === 'xls') {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = e.target?.result
        const workbook = XLSX.read(data, { type: 'binary' })
        const sheet = workbook.Sheets[workbook.SheetNames[0]]
        const jsonData = XLSX.utils.sheet_to_json(sheet, { header: 1 }) as any[][]
        
        const values: number[] = []
        jsonData.forEach((row, rowIdx) => {
          row.forEach(cell => {
            const val = parseFloat(cell)
            if (!isNaN(val)) values.push(val)
          })
        })
        
        form.value.data_values = values
        showMessage.success(`已解析 ${values.length} 个数据点`)
      } catch (error) {
        showMessage.error('文件解析失败')
      }
    }
    reader.readAsBinaryString(file)
  }
}

const isOutOfSpec = (val: number) => {
  return val > form.value.usl || val < form.value.lsl
}

const isNearSpec = (val: number) => {
  const range = form.value.usl - form.value.lsl
  const margin = range * 0.1
  return val > form.value.usl - margin || val < form.value.lsl + margin
}

const validateForm = () => {
  errors.value = {}
  
  if (form.value.usl <= form.value.lsl) {
    errors.value.usl = 'USL 必须大于 LSL'
    errors.value.lsl = 'LSL 必须小于 USL'
  }
  
  if (form.value.data_values.length < 2) {
    errors.value.data = '至少需要 2 个数据点'
  }
  
  return Object.keys(errors.value).length === 0
}

const submitAnalysis = async () => {
  if (!validateForm()) {
    showMessage.error('请检查表单填写是否正确')
    return
  }
  
  submitting.value = true
  
  try {
    const result = await createCapabilityAnalysis(form.value)
    showMessage.success('能力分析完成')
    router.push(`/capability-analysis/${(result as any).id}`)
  } catch (error: any) {
    console.error('分析失败:', error)
    showMessage.error(error.response?.data?.detail || '分析失败，请重试')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.push(`/production-lines/${lineId}/capability-analysis`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-content {
  padding: 40px;
  max-width: 1200px;
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

.form-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.form-section {
  margin-bottom: 40px;
}

.form-section:last-of-type {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.section-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-sm);
  color: var(--accent-primary);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.spec-grid {
  grid-template-columns: repeat(3, 1fr);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-label.required::after {
  content: '*';
  color: var(--danger);
  margin-left: 4px;
}

.form-input {
  width: 100%;
}

.form-input.is-error :deep(.el-input__wrapper) {
  border-color: var(--danger);
}

.error-text {
  font-size: 0.75rem;
  color: var(--danger);
}

.form-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.spec-visual {
  margin-bottom: 24px;
}

.spec-bar {
  display: flex;
  height: 40px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.spec-region {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.spec-region.lsl {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
}

.spec-region.target {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.1));
}

.spec-region.usl {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2), rgba(239, 68, 68, 0.1));
}

.spec-label {
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.machine-sigma {
  margin-top: 16px;
}

.data-source-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.source-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.source-tab:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.source-tab.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: var(--bg-primary);
}

.data-input-area {
  min-height: 200px;
}

.import-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.import-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.import-text {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.import-count {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.import-options {
  display: flex;
  gap: 16px;
}

.option-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.option-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.option-select {
  width: 200px;
}

.btn-import {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 24px;
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

.btn-import:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.btn-import:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.manual-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.manual-input {
  width: 100%;
}

.manual-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-parse {
  padding: 10px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-parse:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.parsed-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.file-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.file-drop-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px;
  background: var(--bg-secondary);
  border: 2px dashed var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.file-drop-zone:hover {
  border-color: var(--accent-primary);
  background: rgba(0, 212, 255, 0.05);
}

.drop-icon {
  color: var(--text-muted);
  margin-bottom: 12px;
}

.drop-text {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.drop-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.file-name {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--text-primary);
}

.file-count {
  font-size: 0.75rem;
  color: var(--success);
}

.data-preview {
  margin-top: 24px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.preview-title {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.stat-label {
  font-size: 0.625rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--accent-primary);
}

.preview-data {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.data-point {
  padding: 4px 8px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-primary);
}

.data-point.out-of-spec {
  background: rgba(239, 68, 68, 0.1);
  border-color: var(--danger);
  color: var(--danger);
}

.data-point.near-spec {
  background: rgba(245, 158, 11, 0.1);
  border-color: #f59e0b;
  color: #f59e0b;
}

.more-data {
  padding: 4px 8px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  padding: 12px 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  border-color: var(--text-primary);
  color: var(--text-primary);
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
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
}

.btn-submit:hover:not(:disabled) {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .form-grid, .spec-grid {
    grid-template-columns: 1fr;
  }
  
  .preview-stats {
    flex-wrap: wrap;
    gap: 12px;
  }
}
</style>
