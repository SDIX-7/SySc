<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">测量系统分析 (MSA)</h1>
          <p class="page-subtitle">Measurement System Analysis</p>
        </div>
        <div class="header-right">
          <button class="btn-create" @click="handleCreate">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            新建MSA研究
          </button>
        </div>
      </div>

      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon total">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">总研究数</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon draft">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.draft }}</span>
            <span class="stat-label">草稿</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon progress">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.inProgress }}</span>
            <span class="stat-label">进行中</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon completed">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ stats.completed }}</span>
            <span class="stat-label">已完成</span>
          </div>
        </div>
      </div>

      <div class="filter-section">
        <div class="filter-row">
          <div class="filter-item">
            <label>产线</label>
            <el-select v-model="queryParams.line_id" placeholder="全部产线" clearable @change="handleQuery" style="width: 180px;">
              <el-option v-for="line in productionLines" :key="line.id" :label="line.line_name" :value="line.id" />
            </el-select>
          </div>
          <div class="filter-item">
            <label>研究类型</label>
            <el-select v-model="queryParams.study_type" placeholder="全部类型" clearable @change="handleQuery" style="width: 140px;">
              <el-option label="GR&R" value="grr" />
              <el-option label="偏倚" value="bias" />
              <el-option label="稳定性" value="stability" />
              <el-option label="线性" value="linearity" />
            </el-select>
          </div>
          <div class="filter-item">
            <label>状态</label>
            <el-select v-model="queryParams.status" placeholder="全部状态" clearable @change="handleQuery" style="width: 120px;">
              <el-option label="草稿" value="draft" />
              <el-option label="进行中" value="in_progress" />
              <el-option label="已完成" value="completed" />
            </el-select>
          </div>
          <div class="filter-item">
            <label>判定结果</label>
            <el-select v-model="queryParams.acceptance" placeholder="全部" clearable @change="handleQuery" style="width: 120px;">
              <el-option label="接受" value="acceptable" />
              <el-option label="条件接受" value="conditional" />
              <el-option label="不接受" value="unacceptable" />
            </el-select>
          </div>
          <div class="filter-actions">
            <button class="btn-filter" @click="handleQuery">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              查询
            </button>
            <button class="btn-reset" @click="handleReset">重置</button>
          </div>
        </div>
      </div>

      <div class="table-section">
        <el-table :data="msaStudies" v-loading="loading" stripe class="data-table">
          <el-table-column prop="id" label="ID" width="70" align="center" />
          <el-table-column prop="study_name" label="研究名称" min-width="200">
            <template #default="{ row }">
              <div class="study-name-cell">
                <span class="study-name">{{ row.study_name }}</span>
                <span class="study-desc" v-if="row.measurement_system">{{ row.measurement_system }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="study_type" label="类型" width="100" align="center">
            <template #default="{ row }">
              <span class="type-tag" :class="row.study_type">{{ getStudyTypeLabel(row.study_type) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100" align="center">
            <template #default="{ row }">
              <span class="status-tag" :class="row.status">{{ getStatusLabel(row.status) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="characteristic" label="测量特性" min-width="120" />
          <el-table-column label="研究设计" width="140" align="center">
            <template #default="{ row }">
              <span class="design-info">{{ row.number_of_parts }}件 × {{ row.number_of_operators }}人 × {{ row.number_of_replicates }}次</span>
            </template>
          </el-table-column>
          <el-table-column prop="percent_grr" label="%GR&R" width="100" align="center">
            <template #default="{ row }">
              <div v-if="row.result && row.result.percent_grr" class="grr-cell">
                <span class="grr-value" :class="getGRRClass(parseFloat(row.result.percent_grr))">
                  {{ parseFloat(row.result.percent_grr).toFixed(2) }}%
                </span>
              </div>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="ndc" label="NDC" width="80" align="center">
            <template #default="{ row }">
              <span v-if="row.result && row.result.ndc" :class="{ 'ndc-good': parseFloat(row.result.ndc) >= 5 }">
                {{ row.result.ndc }}
              </span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="overall_acceptance" label="判定" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.result && row.result.overall_acceptance" class="acceptance-tag" :class="row.result.overall_acceptance">
                {{ getAcceptanceLabel(row.result.overall_acceptance) }}
              </span>
              <span v-else class="no-data">-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160" align="center">
            <template #default="{ row }">
              <span class="time-text">{{ formatDate(row.created_at) }}</span>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <div class="action-buttons">
                <button class="btn-action view" @click="handleView(row)" title="查看详情">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                </button>
                <button class="btn-action edit" @click="handleEdit(row)" title="编辑">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                  </svg>
                </button>
                <button class="btn-action calculate" @click="handleCalculate(row)" v-if="row.status !== 'completed'" title="计算GR&R">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="4" y="2" width="16" height="20" rx="2"/>
                    <line x1="8" y1="6" x2="16" y2="6"/>
                    <line x1="8" y1="10" x2="16" y2="10"/>
                    <line x1="8" y1="14" x2="12" y2="14"/>
                  </svg>
                </button>
                <button class="btn-action delete" @click="handleDelete(row)" title="删除">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMSAStudies, deleteMSAStudy, calculateMSA, type MSAStudy } from '@/api/msa'
import { getProductionLines, type ProductionLine } from '@/api'
import Menu from '@/components/Menu.vue'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const msaStudies = ref<MSAStudy[]>([])
const productionLines = ref<ProductionLine[]>([])

const queryParams = ref({
  line_id: undefined as number | undefined,
  study_type: undefined as string | undefined,
  status: undefined as string | undefined,
  acceptance: undefined as string | undefined
})

const stats = computed(() => {
  const total = msaStudies.value.length
  const draft = msaStudies.value.filter(s => s.status === 'draft').length
  const inProgress = msaStudies.value.filter(s => s.status === 'in_progress').length
  const completed = msaStudies.value.filter(s => s.status === 'completed').length
  return { total, draft, inProgress, completed }
})

const getStudyTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    grr: 'GR&R',
    bias: '偏倚',
    stability: '稳定性',
    linearity: '线性'
  }
  return map[type] || type
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
}

const getAcceptanceLabel = (acceptance: string) => {
  const map: Record<string, string> = {
    acceptable: '接受',
    conditional: '条件接受',
    unacceptable: '不接受'
  }
  return map[acceptance] || acceptance
}

const getGRRClass = (grr: number) => {
  if (grr < 10) return 'good'
  if (grr < 30) return 'warning'
  return 'danger'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchMSAStudies = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (queryParams.value.line_id) params.line_id = queryParams.value.line_id
    if (queryParams.value.study_type) params.study_type = queryParams.value.study_type
    if (queryParams.value.status) params.status = queryParams.value.status
    
    const res = await getMSAStudies(params)
    let studies = res.data || []
    
    if (queryParams.value.acceptance) {
      studies = studies.filter((s: MSAStudy) => s.result?.overall_acceptance === queryParams.value.acceptance)
    }
    
    msaStudies.value = studies
  } catch (error) {
    console.error('获取MSA研究失败:', error)
    ElMessage.error('获取MSA研究失败')
  } finally {
    loading.value = false
  }
}

const fetchProductionLines = async () => {
  try {
    const res = await getProductionLines()
    productionLines.value = res.data || []
  } catch (error) {
    console.error('获取产线失败:', error)
  }
}

const handleQuery = () => {
  fetchMSAStudies()
}

const handleReset = () => {
  queryParams.value = {
    line_id: undefined,
    study_type: undefined,
    status: undefined,
    acceptance: undefined
  }
  fetchMSAStudies()
}

const handleCreate = () => {
  router.push('/msa-studies/new')
}

const handleView = (row: MSAStudy) => {
  router.push(`/msa-studies/${row.id}`)
}

const handleEdit = (row: MSAStudy) => {
  router.push(`/msa-studies/${row.id}/edit`)
}

const handleCalculate = async (row: MSAStudy) => {
  try {
    await ElMessageBox.confirm('确认执行GR&R计算？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    const res = await calculateMSA(row.id!)
    ElMessage.success(res.message || '计算完成')
    fetchMSAStudies()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '计算失败')
    }
  }
}

const handleDelete = async (row: MSAStudy) => {
  try {
    await ElMessageBox.confirm('确认删除该MSA研究？此操作不可恢复。', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMSAStudy(row.id!)
    ElMessage.success('删除成功')
    fetchMSAStudies()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  fetchProductionLines()
  
  if (route.params.lineId) {
    queryParams.value.line_id = Number(route.params.lineId)
  }
  
  fetchMSAStudies()
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
  flex-direction: column;
  gap: 4px;
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

.btn-create {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-primary), #0284c7);
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-create:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}

.stat-icon.total {
  background: rgba(0, 212, 255, 0.1);
  color: var(--accent-primary);
}

.stat-icon.draft {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.stat-icon.progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.stat-icon.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.filter-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 20px;
  margin-bottom: 24px;
}

.filter-row {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-item label {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.filter-actions {
  display: flex;
  gap: 12px;
  margin-left: auto;
}

.btn-filter {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  background: var(--accent-primary);
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-filter:hover {
  background: #0284c7;
}

.btn-reset {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-reset:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.table-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.data-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-row-hover-bg-color: rgba(0, 212, 255, 0.05);
  --el-table-border-color: var(--border-color);
}

.study-name-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.study-name {
  font-weight: 500;
  color: var(--text-primary);
}

.study-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.type-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 500;
}

.type-tag.grr {
  background: rgba(0, 212, 255, 0.1);
  color: var(--accent-primary);
}

.type-tag.bias {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.type-tag.stability {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.type-tag.linearity {
  background: rgba(139, 92, 246, 0.1);
  color: #8b5cf6;
}

.status-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-tag.draft {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.status-tag.in_progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-tag.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.design-info {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.grr-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.grr-value {
  font-family: var(--font-mono);
  font-weight: 600;
}

.grr-value.good {
  color: #10b981;
}

.grr-value.warning {
  color: #f59e0b;
}

.grr-value.danger {
  color: #ef4444;
}

.ndc-good {
  color: #10b981;
  font-weight: 600;
}

.no-data {
  color: var(--text-muted);
}

.acceptance-tag {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 500;
}

.acceptance-tag.acceptable {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.acceptance-tag.conditional {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.acceptance-tag.unacceptable {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.time-text {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.action-buttons {
  display: flex;
  justify-content: center;
  gap: 8px;
}

.btn-action {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-action:hover {
  transform: translateY(-1px);
}

.btn-action.view:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
  background: rgba(0, 212, 255, 0.1);
}

.btn-action.edit:hover {
  border-color: #8b5cf6;
  color: #8b5cf6;
  background: rgba(139, 92, 246, 0.1);
}

.btn-action.calculate:hover {
  border-color: #10b981;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.btn-action.delete:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

@media (max-width: 1200px) {
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
    margin-top: 12px;
  }
}
</style>
