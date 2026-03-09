<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content" v-loading="loading">
      <div class="page-header">
        <div class="header-left">
          <div class="breadcrumb">
            <router-link to="/control-plans">控制计划</router-link>
            <span class="separator">/</span>
            <span class="current">{{ controlPlan?.part_name || controlPlan?.control_plan_number || '详情' }}</span>
          </div>
          <h1 class="page-title">控制计划详情</h1>
        </div>
        <div class="header-right">
          <el-button @click="router.push(`/control-plans/${planId}/edit`)">编辑</el-button>
          <el-button type="success" @click="exportPlan">导出Excel</el-button>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </div>
      
      <div v-if="controlPlan" class="detail-content">
        <div class="info-section">
          <div class="section-header">
            <h2 class="section-title">基本信息</h2>
            <div class="status-info">
              <el-tag :type="getPlanTypeTagType(controlPlan.plan_type)">
                {{ getPlanTypeText(controlPlan.plan_type) }}
              </el-tag>
              <span class="status-badge" :class="controlPlan.status">
                {{ getStatusText(controlPlan.status) }}
              </span>
              <span class="version-badge">v{{ controlPlan.version }}</span>
            </div>
          </div>
          
          <div class="info-grid">
            <div class="info-card">
              <h3 class="card-title">零件信息</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">零件号</span>
                  <span class="value">{{ controlPlan.part_number || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">零件名称</span>
                  <span class="value">{{ controlPlan.part_name || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">零件描述</span>
                  <span class="value">{{ controlPlan.part_description || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">最新变更级别</span>
                  <span class="value">{{ controlPlan.latest_change_level || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">控制计划编号</span>
                  <span class="value mono">{{ controlPlan.control_plan_number || '–' }}</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <h3 class="card-title">组织信息</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">组织/工厂</span>
                  <span class="value">{{ controlPlan.organization_plant || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">组织代码</span>
                  <span class="value mono">{{ controlPlan.organization_code || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">关键联系人</span>
                  <span class="value">{{ controlPlan.key_contact || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">联系电话</span>
                  <span class="value mono">{{ controlPlan.key_contact_phone || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">核心团队</span>
                  <span class="value">{{ controlPlan.core_team || '–' }}</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <h3 class="card-title">审批信息</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">组织批准日期</span>
                  <span class="value">{{ formatDate(controlPlan.org_approval_date) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">组织批准人</span>
                  <span class="value">{{ controlPlan.org_approval_by || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">客户工程批准日期</span>
                  <span class="value">{{ formatDate(controlPlan.customer_eng_approval_date) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">客户工程批准人</span>
                  <span class="value">{{ controlPlan.customer_eng_approval_by || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">客户质量批准日期</span>
                  <span class="value">{{ formatDate(controlPlan.customer_quality_approval_date) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">客户质量批准人</span>
                  <span class="value">{{ controlPlan.customer_quality_approval_by || '–' }}</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <h3 class="card-title">日期信息</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">原始日期</span>
                  <span class="value">{{ formatDate(controlPlan.date_orig) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">修订日期</span>
                  <span class="value">{{ formatDate(controlPlan.date_rev) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建时间</span>
                  <span class="value">{{ formatDateTime(controlPlan.created_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">更新时间</span>
                  <span class="value">{{ formatDateTime(controlPlan.updated_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建人</span>
                  <span class="value">{{ controlPlan.created_by || '–' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="items-section">
          <div class="section-header">
            <h2 class="section-title">控制计划项目</h2>
            <span class="item-count">共 {{ controlPlan.items?.length || 0 }} 项</span>
          </div>
          
          <div class="table-container">
            <el-table
              :data="controlPlan.items || []"
              style="width: 100%"
              :header-cell-style="{ background: 'var(--bg-secondary)', color: 'var(--text-primary)', fontWeight: '600' }"
              max-height="600"
            >
              <el-table-column type="index" label="序号" width="60" />
              <el-table-column prop="part_process_number" label="零件/过程编号" width="140" />
              <el-table-column prop="process_name" label="过程名称" width="150" />
              <el-table-column prop="operation_description" label="操作描述" min-width="180" />
              <el-table-column prop="characteristic_no" label="特性编号" width="100" />
              <el-table-column prop="product_characteristic" label="产品特性" width="150" />
              <el-table-column prop="process_characteristic" label="过程特性" width="150" />
              <el-table-column prop="special_characteristic_class" label="特殊特性分类" width="120" />
              <el-table-column prop="specification_tolerance" label="规范/公差" width="140" />
              <el-table-column prop="evaluation_measurement_technique" label="评价/测量技术" width="160" />
              <el-table-column prop="sample_size" label="样本容量" width="100" />
              <el-table-column prop="sample_frequency" label="抽样频率" width="100" />
              <el-table-column prop="control_method" label="控制方法" width="150" />
              <el-table-column prop="reaction_plan" label="反应计划" min-width="200" />
            </el-table>
            
            <div v-if="!controlPlan.items || controlPlan.items.length === 0" class="empty-state">
              <p>暂无控制计划项目</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getControlPlan, exportControlPlanExcel } from '@/api/controlPlan'
import type { ControlPlan, PlanType, ControlPlanStatus } from '@/types'

const router = useRouter()
const route = useRoute()

const planId = Number(route.params.planId)
const controlPlan = ref<ControlPlan | null>(null)
const loading = ref(false)

const fetchControlPlan = async () => {
  try {
    loading.value = true
    const response = await getControlPlan(planId) as ControlPlan
    controlPlan.value = response
  } catch (error) {
    console.error('获取控制计划失败:', error)
    ElMessage.error('获取控制计划失败')
  } finally {
    loading.value = false
  }
}

const exportPlan = async () => {
  try {
    loading.value = true
    const response = await exportControlPlanExcel(planId)
    const blob = new Blob([response as any], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `控制计划_${controlPlan.value?.part_number || planId}.xlsx`
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

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '–'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatDateTime = (dateStr?: string) => {
  if (!dateStr) return '–'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  fetchControlPlan()
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
  gap: 8px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.breadcrumb a {
  color: var(--accent-primary);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb .separator {
  color: var(--text-muted);
}

.breadcrumb .current {
  color: var(--text-primary);
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.header-right {
  display: flex;
  gap: 12px;
}

.detail-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.info-section,
.items-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--text-primary);
}

.status-info {
  display: flex;
  align-items: center;
  gap: 12px;
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
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.status-badge.approved {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.status-badge.obsolete {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.version-badge {
  display: inline-block;
  padding: 4px 12px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.item-count {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  padding: 24px;
}

.info-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
}

.card-title {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.info-item .label {
  font-size: 0.875rem;
  color: var(--text-muted);
  flex-shrink: 0;
  min-width: 120px;
}

.info-item .value {
  font-size: 0.875rem;
  color: var(--text-primary);
  text-align: right;
  word-break: break-word;
}

.info-item .value.mono {
  font-family: var(--font-mono);
}

.table-container {
  padding: 24px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  color: var(--text-muted);
}

.empty-state p {
  font-size: 0.875rem;
}

@media (max-width: 1200px) {
  .page-content {
    padding: 24px;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .header-right {
    flex-wrap: wrap;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .info-card {
    padding: 16px;
  }
  
  .info-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .info-item .value {
    text-align: left;
  }
  
  .table-container {
    overflow-x: auto;
  }
}

@media print {
  .page-header {
    print-color-adjust: exact;
  }
  
  .header-right {
    display: none;
  }
  
  .page-container {
    padding: 0;
  }
  
  .page-content {
    max-width: 100%;
  }
}
</style>
