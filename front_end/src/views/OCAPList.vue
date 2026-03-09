<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <p class="page-subtitle">{{ pageSubtitle }}</p>
        </div>
        <div class="header-right">
          <button class="btn-primary" @click="router.push('/ocaps/new')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            创建OCAP
          </button>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ ocaps.length }}</span>
            <span class="stat-label">OCAP总数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon danger">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="15" y1="9" x2="9" y2="15"/>
              <line x1="9" y1="9" x2="15" y2="15"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ criticalOcaps }}</span>
            <span class="stat-label">紧急</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon warning">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ executingOcaps }}</span>
            <span class="stat-label">执行中</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon success">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ completedOcaps }}</span>
            <span class="stat-label">已完成</span>
          </div>
        </div>
      </div>
      
      <div class="filter-section">
        <div class="filter-row">
          <el-input
            v-model="searchText"
            placeholder="搜索OCAP..."
            prefix-icon="Search"
            clearable
            class="search-input"
          />
          <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
            <el-option label="草稿" value="draft" />
            <el-option label="激活" value="active" />
            <el-option label="执行中" value="executing" />
            <el-option label="已完成" value="completed" />
            <el-option label="已关闭" value="closed" />
          </el-select>
          <el-select v-model="filterPriority" placeholder="优先级" clearable class="filter-select">
            <el-option label="紧急" value="critical" />
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </div>
      </div>
      
      <div class="table-container">
        <el-table
          :data="filteredOcaps"
          style="width: 100%"
          v-loading="loading"
          :header-cell-style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontWeight: '600' }"
        >
          <el-table-column prop="name" label="OCAP名称" min-width="200">
            <template #default="{ row }">
              <div class="ocap-name">
                <span class="name">{{ row.name }}</span>
                <span class="desc" v-if="row.description">{{ row.description }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="signal_type" label="信号类型" width="160">
            <template #default="{ row }">
              <span class="signal-type">{{ getSignalTypeText(row.signal_type) }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="priority" label="优先级" width="100">
            <template #default="{ row }">
              <span class="priority-badge" :class="row.priority">
                {{ getPriorityText(row.priority) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="overall_priority_score" label="优先级评分" width="110">
            <template #default="{ row }">
              <div class="score-display">
                <span class="score">{{ row.overall_priority_score }}</span>
                <span class="score-label">分</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <span class="status-badge" :class="row.status">
                {{ getStatusText(row.status) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="is_active" label="是否激活" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_active ? 'success' : 'info'" size="small">
                {{ row.is_active ? '是' : '否' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="{ row }">
              {{ formatTime(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button size="small" @click="viewDetail(row)">查看</el-button>
                <el-button size="small" @click="editOcap(row)">编辑</el-button>
                <el-button size="small" type="success" @click="exportOcap(row)">导出</el-button>
                <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="filteredOcaps.length === 0 && !loading" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
            <line x1="12" y1="9" x2="12" y2="13"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <h3>暂无OCAP</h3>
          <p>点击上方按钮创建第一个OCAP</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getOCAPs, deleteOCAP, exportOCAPExcel } from '@/api/ocap'
import { showDeleteConfirm, showMessage } from '@/utils/dialog'
import type { OCAP, SignalType, OCAPPriority, OCAPStatus } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = computed(() => route.params.lineId ? Number(route.params.lineId) : undefined)

const ocaps = ref<OCAP[]>([])
const loading = ref(false)
const searchText = ref('')
const filterStatus = ref('')
const filterPriority = ref('')

const pageTitle = computed(() => lineId.value ? '产线 OCAP' : 'OCAP 管理')
const pageSubtitle = computed(() => lineId.value ? '管理当前产线的失控行动计划' : '管理所有失控行动计划（OCAP）')

const criticalOcaps = computed(() => ocaps.value.filter(o => o.priority === 'critical').length)
const executingOcaps = computed(() => ocaps.value.filter(o => o.status === 'executing').length)
const completedOcaps = computed(() => ocaps.value.filter(o => o.status === 'completed').length)

const filteredOcaps = computed(() => {
  let result = ocaps.value
  
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(o => 
      (o.name?.toLowerCase().includes(search)) ||
      (o.description?.toLowerCase().includes(search))
    )
  }
  
  if (filterStatus.value) {
    result = result.filter(o => o.status === filterStatus.value)
  }
  
  if (filterPriority.value) {
    result = result.filter(o => o.priority === filterPriority.value)
  }
  
  return result
})

const fetchOCAPs = async () => {
  try {
    loading.value = true
    const response = await getOCAPs(undefined, lineId.value) as OCAP[]
    ocaps.value = response
  } catch (error) {
    console.error('获取OCAP失败:', error)
    ElMessage.error('获取OCAP失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (ocap: OCAP) => {
  router.push(`/ocaps/${ocap.id}`)
}

const editOcap = (ocap: OCAP) => {
  router.push(`/ocaps/${ocap.id}/edit`)
}

const exportOcap = async (ocap: OCAP) => {
  try {
    loading.value = true
    const response = await exportOCAPExcel(ocap.id)
    const blob = new Blob([response as any], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `OCAP_${ocap.name}.xlsx`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('导出成功')
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  } finally {
    loading.value = false
  }
}

const confirmDelete = async (ocap: OCAP) => {
  try {
    await showDeleteConfirm(`OCAP "${ocap.name}"`)
    await executeDelete(ocap.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除OCAP失败:', error)
    }
  }
}

const executeDelete = async (ocapId: number) => {
  try {
    loading.value = true
    await deleteOCAP(ocapId)
    showMessage.success('删除成功')
    fetchOCAPs()
  } catch (error: any) {
    console.error('删除OCAP失败:', error)
    showMessage.error(error.detail || '删除失败')
  } finally {
    loading.value = false
  }
}

const getSignalTypeText = (type?: SignalType) => {
  if (!type) return '–'
  const map: Record<SignalType, string> = {
    'point_beyond_3sigma': '点超出3σ',
    'run_9': '连续9点',
    'trend_6': '趋势6点',
    'zone_2of3': '2/3区域',
    'zone_4of5': '4/5区域',
    'run_8': '连续8点',
    'run_6': '连续6点',
    'run_14': '连续14点',
    'run_15': '连续15点'
  }
  return map[type] || type
}

const getPriorityText = (priority: OCAPPriority) => {
  const map: Record<OCAPPriority, string> = {
    'critical': '紧急',
    'high': '高',
    'medium': '中',
    'low': '低'
  }
  return map[priority] || priority
}

const getStatusText = (status: OCAPStatus) => {
  const map: Record<OCAPStatus, string> = {
    'draft': '草稿',
    'active': '激活',
    'executing': '执行中',
    'completed': '已完成',
    'closed': '已关闭'
  }
  return map[status] || status
}

const formatTime = (time: string) => {
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

onMounted(() => {
  fetchOCAPs()
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
  align-items: flex-start;
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
  font-size: 0.875rem;
  color: var(--text-muted);
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-primary:hover {
  background: #00b8e6;
  transform: translateY(-1px);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px 24px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-sm);
  color: var(--accent-primary);
}

.stat-icon.danger {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.stat-icon.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.filter-section {
  margin-bottom: 24px;
}

.filter-row {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 400px;
}

.filter-select {
  width: 140px;
}

.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.ocap-name {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ocap-name .name {
  font-weight: 600;
  color: var(--text-primary);
}

.ocap-name .desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.signal-type {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.priority-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.priority-badge.critical {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.priority-badge.high {
  background: rgba(245, 158, 11, 0.2);
  color: var(--warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.priority-badge.medium {
  background: rgba(0, 212, 255, 0.15);
  color: var(--accent-primary);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.priority-badge.low {
  background: rgba(107, 114, 128, 0.2);
  color: var(--text-secondary);
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.score-display {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.score {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1rem;
  color: var(--text-primary);
}

.score-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.status-badge.draft {
  background: rgba(107, 114, 128, 0.2);
  color: var(--text-secondary);
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.executing {
  background: rgba(245, 158, 11, 0.2);
  color: var(--warning);
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.status-badge.completed {
  background: rgba(0, 212, 255, 0.15);
  color: var(--accent-primary);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.status-badge.closed {
  background: rgba(107, 114, 128, 0.2);
  color: var(--text-secondary);
  border: 1px solid rgba(107, 114, 128, 0.3);
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-width: 200px;
}

.action-buttons .el-button {
  flex: 1 1 calc(50% - 3px);
  min-width: 60px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  color: var(--text-muted);
}

.empty-state svg {
  margin-bottom: 24px;
  opacity: 0.3;
}

.empty-state h3 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 0.875rem;
}

@media (max-width: 1200px) {
  .page-content {
    padding: 24px;
  }
  
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .btn-primary {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .stat-card {
    padding: 16px;
  }
  
  .stat-value {
    font-size: 1.5rem;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .action-buttons {
    flex-wrap: wrap;
  }
}
</style>
