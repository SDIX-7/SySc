<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content" v-loading="loading">
      <div class="page-header">
        <div class="header-left">
          <div class="breadcrumb">
            <router-link to="/ocaps">OCAP</router-link>
            <span class="separator">/</span>
            <span class="current">{{ ocap?.name || '详情' }}</span>
          </div>
          <h1 class="page-title">OCAP详情</h1>
        </div>
        <div class="header-right">
          <el-button @click="router.push(`/ocaps/${ocapId}/edit`)">编辑</el-button>
          <el-button type="success" @click="exportOcap">导出Excel</el-button>
          <el-button @click="router.back()">返回</el-button>
        </div>
      </div>
      
      <div v-if="ocap" class="detail-content">
        <div class="info-section">
          <div class="section-header">
            <h2 class="section-title">基本信息</h2>
            <div class="status-info">
              <span class="priority-badge" :class="ocap.priority">
                {{ getPriorityText(ocap.priority) }}
              </span>
              <span class="status-badge" :class="ocap.status">
                {{ getStatusText(ocap.status) }}
              </span>
              <el-tag :type="ocap.is_active ? 'success' : 'info'" size="small">
                {{ ocap.is_active ? '已激活' : '未激活' }}
              </el-tag>
            </div>
          </div>
          
          <div class="info-grid">
            <div class="info-card">
              <h3 class="card-title">OCAP信息</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">OCAP名称</span>
                  <span class="value">{{ ocap.name }}</span>
                </div>
                <div class="info-item">
                  <span class="label">描述</span>
                  <span class="value">{{ ocap.description || '–' }}</span>
                </div>
                <div class="info-item">
                  <span class="label">信号类型</span>
                  <span class="value">{{ getSignalTypeText(ocap.signal_type) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">创建人</span>
                  <span class="value">{{ ocap.created_by || '–' }}</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <h3 class="card-title">优先级评分</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">严重性评分</span>
                  <span class="value score">{{ ocap.severity_score }}/10</span>
                </div>
                <div class="info-item">
                  <span class="label">范围评分</span>
                  <span class="value score">{{ ocap.scope_score }}/10</span>
                </div>
                <div class="info-item">
                  <span class="label">趋势评分</span>
                  <span class="value score">{{ ocap.trend_score }}/10</span>
                </div>
                <div class="info-item">
                  <span class="label">综合优先级评分</span>
                  <span class="value score highlight">{{ ocap.overall_priority_score }}/10</span>
                </div>
              </div>
            </div>
            
            <div class="info-card">
              <h3 class="card-title">时间信息</h3>
              <div class="info-list">
                <div class="info-item">
                  <span class="label">创建时间</span>
                  <span class="value">{{ formatDateTime(ocap.created_at) }}</span>
                </div>
                <div class="info-item">
                  <span class="label">更新时间</span>
                  <span class="value">{{ formatDateTime(ocap.updated_at) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div class="tabs-section">
          <el-tabs v-model="activeTab">
            <el-tab-pane label="步骤" name="steps">
              <div class="tab-content">
                <div v-if="ocap.steps && ocap.steps.length > 0" class="steps-progress">
                  <div class="progress-header">
                    <div class="progress-title">
                      <span>步骤进度</span>
                      <el-tag type="danger">{{ stepProgress.completed }}/{{ stepProgress.total }}</el-tag>
                    </div>
                    <div class="progress-percentage">{{ stepProgress.percentage }}%</div>
                  </div>
                  <el-progress
                    :percentage="stepProgress.percentage"
                    :color="stepProgressColors"
                    :stroke-width="20"
                  />
                  <div class="progress-stats">
                    <div class="stat-item">
                      <el-icon class="stat-icon completed"><SuccessFilled /></el-icon>
                      <span class="stat-value">{{ stepProgress.completed }}</span>
                      <span class="stat-label">已完成</span>
                    </div>
                    <div class="stat-item">
                      <el-icon class="stat-icon in-progress"><Clock /></el-icon>
                      <span class="stat-value">{{ stepProgress.inProgress }}</span>
                      <span class="stat-label">进行中</span>
                    </div>
                    <div class="stat-item">
                      <el-icon class="stat-icon pending"><More /></el-icon>
                      <span class="stat-value">{{ stepProgress.pending }}</span>
                      <span class="stat-label">待处理</span>
                    </div>
                    <div class="stat-item">
                      <el-icon class="stat-icon overdue"><WarningFilled /></el-icon>
                      <span class="stat-value">{{ stepProgress.overdue }}</span>
                      <span class="stat-label">已逾期</span>
                    </div>
                  </div>
                </div>

                <div v-if="ocap.steps && ocap.steps.length > 0" class="steps-list">
                  <div v-for="step in groupedSteps.containment" :key="step.id" class="step-group">
                    <div class="step-phase">遏制阶段</div>
                    <div class="step-item">
                      <div class="step-header">
                        <span class="step-number">步骤 {{ step.step_number }}</span>
                        <el-tag :type="getActionTypeTag(step.action_type)" size="small">
                          {{ getActionTypeText(step.action_type) }}
                        </el-tag>
                        <span class="step-mandatory" v-if="step.is_mandatory">必须</span>
                      </div>
                      <div class="step-content">
                        <p class="step-desc">{{ step.action_description }}</p>
                        <div class="step-meta">
                          <span v-if="step.responsible_person">负责人: {{ step.responsible_person }}</span>
                          <span v-if="step.expected_duration_minutes">预计时长: {{ step.expected_duration_minutes }}分钟</span>
                          <span v-if="step.deadline">截止时间: {{ formatDateTime(step.deadline) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-for="step in groupedSteps.investigation" :key="step.id" class="step-group">
                    <div class="step-phase">调查阶段</div>
                    <div class="step-item">
                      <div class="step-header">
                        <span class="step-number">步骤 {{ step.step_number }}</span>
                        <el-tag :type="getActionTypeTag(step.action_type)" size="small">
                          {{ getActionTypeText(step.action_type) }}
                        </el-tag>
                        <span class="step-mandatory" v-if="step.is_mandatory">必须</span>
                      </div>
                      <div class="step-content">
                        <p class="step-desc">{{ step.action_description }}</p>
                        <div class="step-meta">
                          <span v-if="step.responsible_person">负责人: {{ step.responsible_person }}</span>
                          <span v-if="step.expected_duration_minutes">预计时长: {{ step.expected_duration_minutes }}分钟</span>
                          <span v-if="step.deadline">截止时间: {{ formatDateTime(step.deadline) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-for="step in groupedSteps.correction" :key="step.id" class="step-group">
                    <div class="step-phase">纠正阶段</div>
                    <div class="step-item">
                      <div class="step-header">
                        <span class="step-number">步骤 {{ step.step_number }}</span>
                        <el-tag :type="getActionTypeTag(step.action_type)" size="small">
                          {{ getActionTypeText(step.action_type) }}
                        </el-tag>
                        <span class="step-mandatory" v-if="step.is_mandatory">必须</span>
                      </div>
                      <div class="step-content">
                        <p class="step-desc">{{ step.action_description }}</p>
                        <div class="step-meta">
                          <span v-if="step.responsible_person">负责人: {{ step.responsible_person }}</span>
                          <span v-if="step.expected_duration_minutes">预计时长: {{ step.expected_duration_minutes }}分钟</span>
                          <span v-if="step.deadline">截止时间: {{ formatDateTime(step.deadline) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div v-for="step in groupedSteps.verification" :key="step.id" class="step-group">
                    <div class="step-phase">验证阶段</div>
                    <div class="step-item">
                      <div class="step-header">
                        <span class="step-number">步骤 {{ step.step_number }}</span>
                        <el-tag :type="getActionTypeTag(step.action_type)" size="small">
                          {{ getActionTypeText(step.action_type) }}
                        </el-tag>
                        <span class="step-mandatory" v-if="step.is_mandatory">必须</span>
                      </div>
                      <div class="step-content">
                        <p class="step-desc">{{ step.action_description }}</p>
                        <div class="step-meta">
                          <span v-if="step.responsible_person">负责人: {{ step.responsible_person }}</span>
                          <span v-if="step.expected_duration_minutes">预计时长: {{ step.expected_duration_minutes }}分钟</span>
                          <span v-if="step.deadline">截止时间: {{ formatDateTime(step.deadline) }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                <div v-else class="empty-tab">
                  <p>暂无步骤信息</p>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="信号" name="signals">
              <div class="tab-content">
                <el-table
                  v-if="ocap.signals && ocap.signals.length > 0"
                  :data="ocap.signals"
                  style="width: 100%"
                >
                  <el-table-column prop="signal_time" label="信号时间" width="180">
                    <template #default="{ row }">
                      {{ formatDateTime(row.signal_time) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="signal_type" label="信号类型" width="140">
                    <template #default="{ row }">
                      {{ getSignalTypeText(row.signal_type) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="signal_value" label="信号值" width="120" />
                  <el-table-column prop="control_limit_value" label="控制限值" width="120" />
                  <el-table-column prop="subgroup_index" label="子组索引" width="100" />
                  <el-table-column prop="detected_by" label="检测方式" width="100">
                    <template #default="{ row }">
                      {{ row.detected_by === 'auto' ? '自动' : '手动' }}
                    </template>
                  </el-table-column>
                </el-table>
                <div v-else class="empty-tab">
                  <p>暂无信号信息</p>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="执行记录" name="executions">
              <div class="tab-content">
                <el-table
                  v-if="ocap.executions && ocap.executions.length > 0"
                  :data="ocap.executions"
                  style="width: 100%"
                >
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                      <span class="exec-status" :class="row.status">
                        {{ getExecutionStatusText(row.status) }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="executed_by" label="执行人" width="120" />
                  <el-table-column prop="started_at" label="开始时间" width="180">
                    <template #default="{ row }">
                      {{ formatDateTime(row.started_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="completed_at" label="完成时间" width="180">
                    <template #default="{ row }">
                      {{ formatDateTime(row.completed_at) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="notes" label="备注" min-width="200" />
                  <el-table-column prop="product_disposition" label="产品处置" width="120">
                    <template #default="{ row }">
                      {{ getProductDispositionText(row.product_disposition) }}
                    </template>
                  </el-table-column>
                </el-table>
                <div v-else class="empty-tab">
                  <p>暂无执行记录</p>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="根本原因" name="rootCauses">
              <div class="tab-content">
                <div v-if="ocap.root_causes && ocap.root_causes.length > 0" class="root-causes-list">
                  <div v-for="rc in ocap.root_causes" :key="rc.id" class="root-cause-card">
                    <div class="rc-header">
                      <span class="rc-method">{{ getAnalysisMethodText(rc.analysis_method) }}</span>
                      <el-tag v-if="rc.verified" type="success" size="small">已验证</el-tag>
                    </div>
                    <div v-if="rc.analysis_method === '5whys'" class="five-whys">
                      <div class="why-item" v-if="rc.why_1">
                        <span class="why-label">为什么1:</span>
                        <span>{{ rc.why_1 }}</span>
                      </div>
                      <div class="why-item" v-if="rc.why_2">
                        <span class="why-label">为什么2:</span>
                        <span>{{ rc.why_2 }}</span>
                      </div>
                      <div class="why-item" v-if="rc.why_3">
                        <span class="why-label">为什么3:</span>
                        <span>{{ rc.why_3 }}</span>
                      </div>
                      <div class="why-item" v-if="rc.why_4">
                        <span class="why-label">为什么4:</span>
                        <span>{{ rc.why_4 }}</span>
                      </div>
                      <div class="why-item" v-if="rc.why_5">
                        <span class="why-label">为什么5:</span>
                        <span>{{ rc.why_5 }}</span>
                      </div>
                    </div>
                    <div class="rc-result" v-if="rc.root_cause_description">
                      <strong>根本原因:</strong> {{ rc.root_cause_description }}
                    </div>
                  </div>
                </div>
                <div v-else class="empty-tab">
                  <p>暂无根本原因分析</p>
                </div>
              </div>
            </el-tab-pane>
            
            <el-tab-pane label="纠正措施" name="correctiveActions">
              <div class="tab-content">
                <el-table
                  v-if="ocap.corrective_actions && ocap.corrective_actions.length > 0"
                  :data="ocap.corrective_actions"
                  style="width: 100%"
                >
                  <el-table-column prop="action_description" label="措施描述" min-width="200" />
                  <el-table-column prop="action_type" label="类型" width="100">
                    <template #default="{ row }">
                      {{ row.action_type === 'temporary' ? '临时' : '永久' }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="responsible_person" label="负责人" width="120" />
                  <el-table-column prop="target_date" label="目标日期" width="120">
                    <template #default="{ row }">
                      {{ formatDate(row.target_date) }}
                    </template>
                  </el-table-column>
                  <el-table-column prop="status" label="状态" width="100">
                    <template #default="{ row }">
                      <span class="ca-status" :class="row.status">
                        {{ getCorrectiveActionStatusText(row.status) }}
                      </span>
                    </template>
                  </el-table-column>
                  <el-table-column prop="effectiveness_verified" label="有效性验证" width="100">
                    <template #default="{ row }">
                      <el-tag :type="row.effectiveness_verified ? 'success' : 'info'" size="small">
                        {{ row.effectiveness_verified ? '已验证' : '未验证' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
                <div v-else class="empty-tab">
                  <p>暂无纠正措施</p>
                </div>
              </div>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import Menu from '@/components/Menu.vue'
import { getOCAP, exportOCAPExcel } from '@/api/ocap'
import { SuccessFilled, Clock, More, WarningFilled } from '@element-plus/icons-vue'
import type { 
  OCAP, 
  OCAPStep, 
  SignalType, 
  OCAPPriority, 
  OCAPStatus, 
  OCAPPhase,
  ActionType,
  ExecutionStatus,
  AnalysisMethod,
  CorrectiveActionStatus,
  ProductDisposition
} from '@/types'

const router = useRouter()
const route = useRoute()

const ocapId = Number(route.params.ocapId)
const ocap = ref<OCAP | null>(null)
const loading = ref(false)
const activeTab = ref('steps')

const stepProgress = computed(() => {
  if (!ocap.value?.steps || ocap.value.steps.length === 0) {
    return {
      total: 0,
      completed: 0,
      inProgress: 0,
      pending: 0,
      overdue: 0,
      percentage: 0
    }
  }

  const steps = ocap.value.steps
  const total = steps.length
  const completed = steps.filter(s => s.status === 'completed' || s.status === 'verified').length
  const inProgress = steps.filter(s => s.status === 'in_progress' || s.status === 'executing').length
  const pending = steps.filter(s => s.status === 'pending' || s.status === 'not_started').length

  // Count overdue steps (have deadline and are not completed)
  const now = new Date()
  const overdue = steps.filter(s => {
    if (s.status === 'completed' || s.status === 'verified') return false
    if (!s.deadline) return false
    return new Date(s.deadline) < now
  }).length

  return {
    total,
    completed,
    inProgress,
    pending,
    overdue,
    percentage: total > 0 ? Math.round((completed / total) * 100) : 0
  }
})

const stepProgressColors = [
  { color: '#67c23a', percentage: 25 },
  { color: '#e6a23c', percentage: 50 },
  { color: '#f56c6c', percentage: 75 },
  { color: '#909399', percentage: 100 }
]

const groupedSteps = computed(() => {
  const groups: Record<OCAPPhase, OCAPStep[]> = {
    containment: [],
    investigation: [],
    correction: [],
    verification: []
  }
  
  if (ocap.value?.steps) {
    ocap.value.steps.forEach(step => {
      groups[step.phase].push(step)
    })
  }
  
  return groups
})

const fetchOCAP = async () => {
  try {
    loading.value = true
    const response = await getOCAP(ocapId) as OCAP
    ocap.value = response
  } catch (error) {
    console.error('获取OCAP失败:', error)
    ElMessage.error('获取OCAP失败')
  } finally {
    loading.value = false
  }
}

const exportOcap = async () => {
  try {
    loading.value = true
    const response = await exportOCAPExcel(ocapId)
    const blob = new Blob([response as any], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `OCAP_${ocap.value?.name || ocapId}.xlsx`
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

const getActionTypeText = (type: ActionType) => {
  const map: Record<ActionType, string> = {
    'immediate': '立即',
    'short_term': '短期',
    'long_term': '长期'
  }
  return map[type] || type
}

const getActionTypeTag = (type: ActionType): '' | 'success' | 'warning' | 'info' | 'danger' => {
  const map: Record<ActionType, '' | 'success' | 'warning' | 'info' | 'danger'> = {
    'immediate': 'danger',
    'short_term': 'warning',
    'long_term': 'info'
  }
  return map[type] || ''
}

const getExecutionStatusText = (status: ExecutionStatus) => {
  const map: Record<ExecutionStatus, string> = {
    'pending': '待处理',
    'in_progress': '进行中',
    'completed': '已完成',
    'skipped': '已跳过',
    'failed': '失败'
  }
  return map[status] || status
}

const getAnalysisMethodText = (method: AnalysisMethod) => {
  const map: Record<AnalysisMethod, string> = {
    '5whys': '5个为什么',
    'fishbone': '鱼骨图',
    'pareto': '帕累托',
    'fta': '故障树分析'
  }
  return map[method] || method
}

const getCorrectiveActionStatusText = (status: CorrectiveActionStatus) => {
  const map: Record<CorrectiveActionStatus, string> = {
    'planned': '计划中',
    'in_progress': '进行中',
    'completed': '已完成',
    'verified': '已验证'
  }
  return map[status] || status
}

const getProductDispositionText = (disposition?: ProductDisposition) => {
  if (!disposition) return '–'
  const map: Record<ProductDisposition, string> = {
    'release': '放行',
    'rework': '返工',
    'scrap': '报废',
    'concession': '让步接收'
  }
  return map[disposition] || disposition
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
  fetchOCAP()
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
.tabs-section {
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
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.priority-badge.high {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.priority-badge.medium {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.priority-badge.low {
  background: rgba(107, 114, 128, 0.15);
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
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.status-badge.executing {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.status-badge.completed {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-badge.closed {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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
  min-width: 100px;
}

.info-item .value {
  font-size: 0.875rem;
  color: var(--text-primary);
  text-align: right;
  word-break: break-word;
}

.info-item .value.score {
  font-family: var(--font-display);
  font-weight: 700;
  font-size: 1rem;
}

.info-item .value.score.highlight {
  color: var(--accent-primary);
  font-size: 1.125rem;
}

.tabs-section {
  padding: 0;
}

.tab-content {
  padding: 24px;
  min-height: 300px;
}

.empty-tab {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px;
  color: var(--text-muted);
}

.steps-progress {
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
  border: 2px solid #cbd5e1;
  border-radius: var(--radius-md);
  padding: 20px;
  margin-bottom: 24px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.progress-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.progress-percentage {
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--accent-primary);
}

.progress-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px;
  background: white;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-color);
}

.stat-icon {
  font-size: 1.5rem;
}

.stat-icon.completed {
  color: #67c23a;
}

.stat-icon.in-progress {
  color: #e6a23c;
}

.stat-icon.pending {
  color: #909399;
}

.stat-icon.overdue {
  color: #f56c6c;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.step-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-phase {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--accent-primary);
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-sm);
}

.step-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
  margin-left: 24px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.step-number {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--text-primary);
}

.step-mandatory {
  font-size: 0.75rem;
  color: var(--danger);
  padding: 2px 8px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: var(--radius-sm);
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.step-desc {
  color: var(--text-primary);
  line-height: 1.6;
}

.step-meta {
  display: flex;
  gap: 16px;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.exec-status,
.ca-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.7rem;
  font-weight: 600;
}

.exec-status.pending,
.ca-status.planned {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.exec-status.in_progress,
.ca-status.in_progress {
  background: rgba(245, 158, 11, 0.15);
  color: var(--warning);
}

.exec-status.completed,
.ca-status.completed {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.exec-status.skipped {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.exec-status.failed {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.ca-status.verified {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.root-causes-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.root-cause-card {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
}

.rc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.rc-method {
  font-family: var(--font-display);
  font-weight: 700;
  color: var(--accent-primary);
}

.five-whys {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
}

.why-item {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
}

.why-label {
  font-weight: 600;
  color: var(--text-muted);
  min-width: 80px;
}

.rc-result {
  padding: 12px;
  background: rgba(16, 185, 129, 0.1);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
}

@media (max-width: 1200px) {
  .page-content {
    padding: 24px;
  }
  
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
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
  
  .info-grid {
    grid-template-columns: 1fr;
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
  
  .tab-content {
    padding: 16px;
  }
  
  .step-item {
    margin-left: 16px;
  }
  
  .step-header {
    flex-wrap: wrap;
  }
  
  .step-meta {
    flex-wrap: wrap;
  }
}
</style>
