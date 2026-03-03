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
            <h1 class="page-title">{{ line?.line_name || '产线详情' }}</h1>
            <p class="page-subtitle">{{ line?.line_code }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="status-badge" :class="line?.status">
            {{ line?.status === 'active' ? '运行中' : '已停用' }}
          </div>
        </div>
      </div>
      
      <div class="info-section">
        <h2 class="section-title">基本信息</h2>
        <div class="info-grid">
          <div class="info-card">
            <span class="info-label">产线编号</span>
            <span class="info-value">{{ line?.line_code }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">数据类型</span>
            <span class="info-value">{{ getDataTypeText(line?.data_type) }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ formatTime(line?.created_at) }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">更新时间</span>
            <span class="info-value">{{ formatTime(line?.updated_at) }}</span>
          </div>
        </div>
        <div class="info-desc" v-if="line?.line_description">
          <span class="info-label">描述</span>
          <p class="desc-text">{{ line.line_description }}</p>
        </div>
      </div>
      
      <div class="tabs-section">
        <div class="tabs-header">
          <button 
            v-for="tab in tabs" 
            :key="tab.value" 
            class="tab-btn"
            :class="{ active: activeTab === tab.value }"
            @click="activeTab = tab.value"
          >
            {{ tab.label }}
          </button>
        </div>
        
        <div class="tab-content">
          <div v-if="activeTab === 'data'" class="tab-panel">
            <div class="panel-header">
              <h3 class="panel-title">数据记录</h3>
              <div class="panel-actions class="btn-secondary">
                <button" @click="showDataForm = true">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="12" y1="5" x2="12" y2="19"/>
                    <line x1="5" y1="12" x2="19" y2="12"/>
                  </svg>
                  添加数据
                </button>
              </div>
            </div>
            
            <div class="data-tabs">
              <button 
                class="data-tab" 
                :class="{ active: dataType === 'attribute' }"
                @click="dataType = 'attribute'"
              >
                计数型数据
              </button>
              <button 
                class="data-tab" 
                :class="{ active: dataType === 'measurement' }"
                @click="dataType = 'measurement'"
              >
                计量型数据
              </button>
            </div>
            
            <div v-if="dataType === 'attribute'" class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>样本编号</th>
                    <th>样本数量</th>
                    <th>缺陷数量</th>
                    <th>检验时间</th>
                    <th>检验员</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in attributeData" :key="item.id">
                    <td>{{ item.sample_id }}</td>
                    <td>{{ item.sample_size }}</td>
                    <td :class="{ 'text-danger': item.defect_count > 0 }">{{ item.defect_count }}</td>
                    <td>{{ formatTime(item.inspection_time) }}</td>
                    <td>{{ item.inspector || '–' }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="attributeData.length === 0" class="empty-table">
                <p>暂无计数型数据</p>
              </div>
            </div>
            
            <div v-if="dataType === 'measurement'" class="table-container">
              <table class="data-table">
                <thead>
                  <tr>
                    <th>样本编号</th>
                    <th>测量值</th>
                    <th>测量时间</th>
                    <th>操作员</th>
                    <th>设备</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="item in measurementData" :key="item.id">
                    <td>{{ item.sample_id }}</td>
                    <td>{{ item.measurement_values?.join(', ') || '–' }}</td>
                    <td>{{ formatTime(item.measurement_time) }}</td>
                    <td>{{ item.operator || '–' }}</td>
                    <td>{{ item.equipment || '–' }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-if="measurementData.length === 0" class="empty-table">
                <p>暂无计量型数据</p>
              </div>
            </div>
          </div>
          
          <div v-if="activeTab === 'chart'" class="tab-panel">
            <div class="panel-header">
              <h3 class="panel-title">控制图</h3>
              <div class="chart-types">
                <select v-model="chartType" class="chart-select">
                  <option value="U">U图 (单位缺陷数)</option>
                  <option value="P">P图 (不合格率)</option>
                  <option value="NP">NP图 (不合格数)</option>
                  <option value="C">C图 (缺陷数)</option>
                </select>
              </div>
            </div>
            <div class="chart-container">
              <div v-if="attributeData.length > 0" class="chart-placeholder">
                <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                  <path d="M3 3v18h18"/>
                  <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
                </svg>
                <p>控制图展示区域</p>
                <p class="hint">基于 {{ attributeData.length }} 条数据点</p>
              </div>
              <div v-else class="empty-chart">
                <p>暂无足够数据生成控制图</p>
              </div>
            </div>
          </div>
          
          <div v-if="activeTab === 'sampling'" class="tab-panel">
            <div class="panel-header">
              <h3 class="panel-title">抽样方案</h3>
              <button class="btn-secondary" @click="showSamplingForm = true">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                创建方案
              </button>
            </div>
            
            <div class="sampling-list">
              <div v-for="plan in samplingPlans" :key="plan.id" class="sampling-card">
                <div class="sampling-header">
                  <h4>{{ plan.plan_name }}</h4>
                  <span class="sampling-type">{{ plan.sampling_type }}</span>
                </div>
                <div class="sampling-body">
                  <div class="sampling-info">
                    <span class="label">批量大小</span>
                    <span class="value">{{ plan.batch_size }}</span>
                  </div>
                  <div class="sampling-info">
                    <span class="label">AQL</span>
                    <span class="value">{{ plan.aql_value }}</span>
                  </div>
                  <div class="sampling-info">
                    <span class="label">检验水平</span>
                    <span class="value">{{ plan.inspection_level }}</span>
                  </div>
                </div>
              </div>
              
              <div v-if="samplingPlans.length === 0" class="empty-list">
                <p>暂无抽样方案</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <el-dialog
      v-model="showDataForm"
      :title="dataType === 'attribute' ? '添加计数型数据' : '添加计量型数据'"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form v-if="dataType === 'attribute'" :model="attrForm" label-position="top">
        <el-form-item label="样本编号" required>
          <el-input v-model="attrForm.sample_id" placeholder="请输入样本编号" />
        </el-form-item>
        <el-form-item label="样本数量" required>
          <el-input-number v-model="attrForm.sample_size" :min="1" />
        </el-form-item>
        <el-form-item label="缺陷数量">
          <el-input-number v-model="attrForm.defect_count" :min="0" />
        </el-form-item>
        <el-form-item label="检验员">
          <el-input v-model="attrForm.inspector" placeholder="请输入检验员姓名" />
        </el-form-item>
      </el-form>
      
      <el-form v-else :model="measureForm" label-position="top">
        <el-form-item label="样本编号" required>
          <el-input v-model="measureForm.sample_id" placeholder="请输入样本编号" />
        </el-form-item>
        <el-form-item label="测量值 (逗号分隔)" required>
          <el-input v-model="measureValuesInput" placeholder="例如: 10.5, 11.2, 10.8" />
        </el-form-item>
        <el-form-item label="操作员">
          <el-input v-model="measureForm.operator" placeholder="请输入操作员姓名" />
        </el-form-item>
        <el-form-item label="测量设备">
          <el-input v-model="measureForm.equipment" placeholder="请输入设备编号" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showDataForm = false">取消</el-button>
        <el-button type="primary" @click="submitData" :loading="loading">提交</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showSamplingForm"
      title="创建抽样方案"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="samplingForm" label-position="top">
        <el-form-item label="方案名称" required>
          <el-input v-model="samplingForm.plan_name" placeholder="请输入方案名称" />
        </el-form-item>
        <el-form-item label="批量大小 (N)" required>
          <el-input-number v-model="samplingForm.batch_size" :min="1" />
        </el-form-item>
        <el-form-item label="AQL值">
          <el-select v-model="samplingForm.aql_value">
            <el-option label="0.65" value="0.65" />
            <el-option label="1.0" value="1.0" />
            <el-option label="1.5" value="1.5" />
            <el-option label="2.5" value="2.5" />
          </el-select>
        </el-form-item>
        <el-form-item label="检验水平">
          <el-select v-model="samplingForm.inspection_level">
            <el-option label="S-1" value="S-1" />
            <el-option label="S-2" value="S-2" />
            <el-option label="S-3" value="S-3" />
            <el-option label="S-4" value="S-4" />
            <el-option label="I" value="I" />
            <el-option label="II" value="II" />
            <el-option label="III" value="III" />
          </el-select>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showSamplingForm = false">取消</el-button>
        <el-button type="primary" @click="createSamplingPlan" :loading="loading">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Menu from '@/components/Menu.vue'
import { 
  getProductionLine, 
  getAttributeData, 
  getMeasurementData,
  getSamplingPlans,
  createAttributeData,
  createMeasurementData,
  createSamplingPlan 
} from '@/api'
import type { ProductionLine, AttributeData, MeasurementData, SamplingPlan } from '@/types'

const route = useRoute()
const router = useRouter()

const line = ref<ProductionLine | null>(null)
const attributeData = ref<AttributeData[]>([])
const measurementData = ref<MeasurementData[]>([])
const samplingPlans = ref<SamplingPlan[]>([])
const loading = ref(false)

const activeTab = ref('data')
const dataType = ref('attribute')
const chartType = ref('U')

const showDataForm = ref(false)
const showSamplingForm = ref(false)

const measureValuesInput = ref('')

const attrForm = ref({
  sample_id: '',
  sample_size: 1,
  defect_count: 0,
  inspector: ''
})

const measureForm = ref({
  sample_id: '',
  operator: '',
  equipment: ''
})

const samplingForm = ref({
  plan_name: '',
  batch_size: 100,
  aql_value: '1.0',
  inspection_level: 'II'
})

const tabs = [
  { label: '数据记录', value: 'data' },
  { label: '控制图', value: 'chart' },
  { label: '抽样方案', value: 'sampling' }
]

const lineId = Number(route.params.id)

const fetchLine = async () => {
  try {
    const response = await getProductionLine(lineId) as ProductionLine
    line.value = response
  } catch (error) {
    console.error('获取产线失败:', error)
    ElMessage.error('获取产线失败')
  }
}

const fetchData = async () => {
  try {
    const [attrRes, measureRes] = await Promise.all([
      getAttributeData(lineId),
      getMeasurementData(lineId)
    ])
    attributeData.value = attrRes as AttributeData[]
    measurementData.value = measureRes as MeasurementData[]
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const fetchSamplingPlans = async () => {
  try {
    const response = await getSamplingPlans(lineId) as SamplingPlan[]
    samplingPlans.value = response
  } catch (error) {
    console.error('获取抽样方案失败:', error)
  }
}

const submitData = async () => {
  if (dataType.value === 'attribute') {
    if (!attrForm.value.sample_id) {
      ElMessage.warning('请填写样本编号')
      return
    }
    
    try {
      loading.value = true
      await createAttributeData({
        line_id: lineId,
        sample_id: attrForm.value.sample_id,
        sample_size: attrForm.value.sample_size,
        defect_count: attrForm.value.defect_count,
        inspector: attrForm.value.inspector
      })
      ElMessage.success('添加成功')
      showDataForm.value = false
      attrForm.value = { sample_id: '', sample_size: 1, defect_count: 0, inspector: '' }
      fetchData()
    } catch (error) {
      console.error('添加数据失败:', error)
      ElMessage.error('添加失败')
    } finally {
      loading.value = false
    }
  } else {
    if (!measureForm.value.sample_id || !measureValuesInput.value) {
      ElMessage.warning('请填写样本编号和测量值')
      return
    }
    
    try {
      const values = measureValuesInput.value.split(',').map(v => parseFloat(v.trim())).filter(v => !isNaN(v))
      if (values.length === 0) {
        ElMessage.warning('请输入有效的测量值')
        return
      }
      
      loading.value = true
      await createMeasurementData({
        line_id: lineId,
        sample_id: measureForm.value.sample_id,
        measurement_values: values,
        operator: measureForm.value.operator,
        equipment: measureForm.value.equipment
      })
      ElMessage.success('添加成功')
      showDataForm.value = false
      measureForm.value = { sample_id: '', operator: '', equipment: '' }
      measureValuesInput.value = ''
      fetchData()
    } catch (error) {
      console.error('添加数据失败:', error)
      ElMessage.error('添加失败')
    } finally {
      loading.value = false
    }
  }
}

const createSamplingPlan = async () => {
  if (!samplingForm.value.plan_name) {
    ElMessage.warning('请填写方案名称')
    return
  }
  
  try {
    loading.value = true
    await createSamplingPlan({
      line_id: lineId,
      plan_name: samplingForm.value.plan_name,
      batch_size: samplingForm.value.batch_size,
      aql_value: samplingForm.value.aql_value,
      inspection_level: samplingForm.value.inspection_level,
      sampling_type: 'single'
    })
    ElMessage.success('创建成功')
    showSamplingForm.value = false
    samplingForm.value = { plan_name: '', batch_size: 100, aql_value: '1.0', inspection_level: 'II' }
    fetchSamplingPlans()
  } catch (error) {
    console.error('创建抽样方案失败:', error)
    ElMessage.error('创建失败')
  } finally {
    loading.value = false
  }
}

const getDataTypeText = (type?: string) => {
  const map: Record<string, string> = {
    measurement: '计量型数据',
    attribute: '计数型数据',
    mixed: '混合类型'
  }
  return type ? map[type] || type : '–'
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

const goBack = () => {
  router.push('/production-lines')
}

watch(activeTab, (val) => {
  if (val === 'sampling') {
    fetchSamplingPlans()
  }
})

onMounted(() => {
  fetchLine()
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

.status-badge {
  padding: 6px 16px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.status-badge.inactive {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.info-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 32px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.info-desc {
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.desc-text {
  margin-top: 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.tabs-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.tabs-header {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.tab-btn {
  padding: 16px 24px;
  background: none;
  border: none;
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  border-bottom: 2px solid transparent;
}

.tab-btn:hover {
  color: var(--text-primary);
}

.tab-btn.active {
  color: var(--accent-primary);
  border-bottom-color: var(--accent-primary);
}

.tab-content {
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.data-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}

.data-tab {
  padding: 8px 16px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.data-tab.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: white;
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

.text-danger {
  color: var(--danger);
}

.empty-table, .empty-chart, .empty-list {
  padding: 40px;
  text-align: center;
  color: var(--text-muted);
}

.chart-container {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-muted);
}

.chart-placeholder svg {
  margin-bottom: 16px;
  opacity: 0.3;
}

.chart-placeholder .hint {
  font-size: 0.75rem;
  margin-top: 8px;
}

.chart-select {
  padding: 8px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
}

.sampling-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.sampling-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
}

.sampling-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sampling-header h4 {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sampling-type {
  padding: 2px 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--accent-primary);
  text-transform: uppercase;
}

.sampling-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sampling-info {
  display: flex;
  justify-content: space-between;
}

.sampling-info .label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.sampling-info .value {
  font-size: 0.875rem;
  color: var(--text-primary);
}

@media (max-width: 1200px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
