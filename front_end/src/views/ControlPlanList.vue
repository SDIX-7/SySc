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
          <button class="btn-primary" @click="router.push('/control-plans/new')">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            创建控制计划
          </button>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ controlPlans.length }}</span>
            <span class="stat-label">控制计划总数</span>
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
            <span class="stat-value">{{ activePlans }}</span>
            <span class="stat-label">激活计划</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon warning">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ draftPlans }}</span>
            <span class="stat-label">草稿计划</span>
          </div>
        </div>
      </div>
      
      <div class="filter-section">
        <div class="filter-row">
          <el-input
            v-model="searchText"
            placeholder="搜索控制计划..."
            prefix-icon="Search"
            clearable
            class="search-input"
          />
          <el-select v-model="filterPlanType" placeholder="计划类型" clearable class="filter-select">
            <el-option label="原型样件" value="prototype" />
            <el-option label="试生产" value="pre-launch" />
            <el-option label="生产" value="production" />
          </el-select>
          <el-select v-model="filterStatus" placeholder="状态" clearable class="filter-select">
            <el-option label="草稿" value="draft" />
            <el-option label="已批准" value="approved" />
            <el-option label="激活" value="active" />
            <el-option label="已废弃" value="obsolete" />
          </el-select>
        </div>
      </div>
      
      <div class="table-container">
        <el-table
          :data="filteredPlans"
          style="width: 100%"
          v-loading="loading"
          :header-cell-style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontWeight: '600' }"
        >
          <el-table-column prop="control_plan_number" label="控制计划编号" width="180">
            <template #default="{ row }">
              <span class="plan-number">{{ row.control_plan_number || '–' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="part_number" label="零件号" width="150">
            <template #default="{ row }">
              <span class="part-number">{{ row.part_number || '–' }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="part_name" label="零件名称" min-width="200">
            <template #default="{ row }">
              <div class="part-info">
                <span class="part-name">{{ row.part_name || '–' }}</span>
                <span class="part-desc" v-if="row.part_description">{{ row.part_description }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="plan_type" label="计划类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getPlanTypeTagType(row.plan_type)" size="small">
                {{ getPlanTypeText(row.plan_type) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="version" label="版本" width="80">
            <template #default="{ row }">
              <span class="version-badge">v{{ row.version }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <span class="status-badge" :class="row.status">
                {{ getStatusText(row.status) }}
              </span>
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
                <el-button size="small" @click="editPlan(row)">编辑</el-button>
                <el-button size="small" type="success" @click="exportPlan(row)">导出</el-button>
                <el-button size="small" type="danger" @click="confirmDelete(row)">删除</el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="filteredPlans.length === 0 && !loading" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <h3>暂无控制计划</h3>
          <p>点击上方按钮创建第一个控制计划</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getControlPlans, deleteControlPlan, exportControlPlanExcel } from '@/api/controlPlan'
import { showDeleteConfirm, showMessage } from '@/utils/dialog'
import type { ControlPlan, PlanType, ControlPlanStatus } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = computed(() => route.params.lineId ? Number(route.params.lineId) : undefined)

const controlPlans = ref<ControlPlan[]>([])
const loading = ref(false)
const searchText = ref('')
const filterPlanType = ref('')
const filterStatus = ref('')

const pageTitle = computed(() => lineId.value ? '产线控制计划' : '控制计划管理')
const pageSubtitle = computed(() => lineId.value ? '管理当前产线的控制计划' : '管理所有控制计划（Control Plan）')

const activePlans = computed(() => controlPlans.value.filter(p => p.status === 'active').length)
const draftPlans = computed(() => controlPlans.value.filter(p => p.status === 'draft').length)

const filteredPlans = computed(() => {
  let result = controlPlans.value
  
  if (searchText.value) {
    const search = searchText.value.toLowerCase()
    result = result.filter(p => 
      (p.control_plan_number?.toLowerCase().includes(search)) ||
      (p.part_number?.toLowerCase().includes(search)) ||
      (p.part_name?.toLowerCase().includes(search)) ||
      (p.part_description?.toLowerCase().includes(search))
    )
  }
  
  if (filterPlanType.value) {
    result = result.filter(p => p.plan_type === filterPlanType.value)
  }
  
  if (filterStatus.value) {
    result = result.filter(p => p.status === filterStatus.value)
  }
  
  return result
})

const fetchControlPlans = async () => {
  try {
    loading.value = true
    const response = await getControlPlans(lineId.value) as ControlPlan[]
    controlPlans.value = response
  } catch (error) {
    console.error('获取控制计划失败:', error)
    ElMessage.error('获取控制计划失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (plan: ControlPlan) => {
  router.push(`/control-plans/${plan.id}`)
}

const editPlan = (plan: ControlPlan) => {
  router.push(`/control-plans/${plan.id}/edit`)
}

const exportPlan = async (plan: ControlPlan) => {
  try {
    loading.value = true
    const response = await exportControlPlanExcel(plan.id)
    const blob = new Blob([response as any], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `控制计划_${plan.part_number || plan.id}.xlsx`
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

const confirmDelete = async (plan: ControlPlan) => {
  try {
    await showDeleteConfirm(`控制计划 "${plan.part_name || plan.control_plan_number}"`)
    await executeDelete(plan.id)
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除控制计划失败:', error)
    }
  }
}

const executeDelete = async (planId: number) => {
  try {
    loading.value = true
    await deleteControlPlan(planId)
    showMessage.success('删除成功')
    fetchControlPlans()
  } catch (error: any) {
    console.error('删除控制计划失败:', error)
    showMessage.error(error.detail || '删除失败')
  } finally {
    loading.value = false
  }
}

const getPlanTypeText = (type: PlanType) => {
  const map: Record<PlanType, string> = {
    'prototype': '原型样件',
    'pre-launch': '试生产',
    'production': '生产'
  }
  return map[type] || type
}

const getPlanTypeTagType = (type: PlanType): '' | 'success' | 'warning' | 'info' | 'danger' => {
  const map: Record<PlanType, '' | 'success' | 'warning' | 'info' | 'danger'> = {
    'prototype': 'info',
    'pre-launch': 'warning',
    'production': 'success'
  }
  return map[type] || ''
}

const getStatusText = (status: ControlPlanStatus) => {
  const map: Record<ControlPlanStatus, string> = {
    'draft': '草稿',
    'approved': '已批准',
    'active': '激活',
    'obsolete': '已废弃'
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
  fetchControlPlans()
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
  grid-template-columns: repeat(3, 1fr);
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
  width: 160px;
}

.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.plan-number {
  font-family: var(--font-mono);
  font-weight: 600;
  color: var(--accent-primary);
}

.part-number {
  font-family: var(--font-mono);
  color: var(--text-secondary);
}

.part-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.part-name {
  font-weight: 600;
  color: var(--text-primary);
}

.part-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.version-badge {
  display: inline-block;
  padding: 2px 8px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
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

.status-badge.approved {
  background: rgba(0, 212, 255, 0.15);
  color: var(--accent-primary);
  border: 1px solid rgba(0, 212, 255, 0.3);
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-badge.obsolete {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
  border: 1px solid rgba(239, 68, 68, 0.3);
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

@media (max-width: 1400px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1200px) {
  .page-content {
    padding: 24px;
  }
  
  .stats-row {
    grid-template-columns: 1fr;
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
