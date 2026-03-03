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
            <h1 class="page-title">能力分析</h1>
            <p class="page-subtitle">{{ line?.line_name }}</p>
          </div>
        </div>
        <div class="header-right">
          <router-link :to="`/production-lines/${lineId}/capability-analysis/new`" class="btn-new">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            新建分析
          </router-link>
        </div>
      </div>

      <div class="stats-section">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ analyses.length }}</span>
            <span class="stat-label">分析记录</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon excellent">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ excellentCount }}</span>
            <span class="stat-label">能力优秀</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon warning">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ poorCount }}</span>
            <span class="stat-label">能力不足</span>
          </div>
        </div>
        
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ latestCpk }}</span>
            <span class="stat-label">最新 Cpk</span>
          </div>
        </div>
      </div>

      <div class="list-section">
        <div class="list-header">
          <h2 class="section-title">分析记录</h2>
          <div class="list-filters">
            <el-select v-model="filterType" placeholder="分析类型" clearable class="filter-select">
              <el-option label="过程能力分析" value="process" />
              <el-option label="机器能力分析" value="machine" />
              <el-option label="预分析" value="preliminary" />
            </el-select>
          </div>
        </div>

        <div class="analysis-list" v-if="filteredAnalyses.length > 0">
          <div 
            v-for="item in filteredAnalyses" 
            :key="item.id" 
            class="analysis-card"
            @click="viewDetail(item.id)"
          >
            <div class="card-header">
              <div class="card-title">
                <h3>{{ item.analysis_name || `分析 #${item.id}` }}</h3>
                <span class="analysis-type" :class="item.analysis_type">
                  {{ getAnalysisTypeText(item.analysis_type) }}
                </span>
              </div>
              <div class="card-time">
                {{ formatTime(item.analysis_time) }}
              </div>
            </div>
            
            <div class="card-body">
              <div class="indices-row">
                <div class="index-item" :class="getIndexClass(parseFloat(item.cpk || '0'))">
                  <span class="index-name">Cpk</span>
                  <span class="index-value">{{ parseFloat(item.cpk || '0').toFixed(3) }}</span>
                </div>
                <div class="index-item" :class="getIndexClass(parseFloat(item.cp || '0'))">
                  <span class="index-name">Cp</span>
                  <span class="index-value">{{ parseFloat(item.cp || '0').toFixed(3) }}</span>
                </div>
                <div class="index-item" :class="getIndexClass(parseFloat(item.ppk || '0'))">
                  <span class="index-name">Ppk</span>
                  <span class="index-value">{{ parseFloat(item.ppk || '0').toFixed(3) }}</span>
                </div>
                <div class="index-item" :class="getIndexClass(parseFloat(item.pp || '0'))">
                  <span class="index-name">Pp</span>
                  <span class="index-value">{{ parseFloat(item.pp || '0').toFixed(3) }}</span>
                </div>
              </div>
              
              <div class="specs-row">
                <div class="spec-item">
                  <span class="spec-label">USL</span>
                  <span class="spec-value">{{ parseFloat(item.usl).toFixed(2) }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">LSL</span>
                  <span class="spec-value">{{ parseFloat(item.lsl).toFixed(2) }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">样本数</span>
                  <span class="spec-value">{{ item.sample_count }}</span>
                </div>
                <div class="spec-item">
                  <span class="spec-label">均值</span>
                  <span class="spec-value">{{ parseFloat(item.mean || '0').toFixed(4) }}</span>
                </div>
              </div>
            </div>
            
            <div class="card-footer">
              <span class="status-badge" :class="getStatusClass(parseFloat(item.cpk || '0'))">
                {{ getStatusText(parseFloat(item.cpk || '0')) }}
              </span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </div>
          </div>
        </div>

        <div class="empty-state" v-else>
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <h3>暂无分析记录</h3>
          <p>点击上方"新建分析"按钮开始第一次能力分析</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getProductionLine, getCapabilityAnalyses } from '@/api'
import type { ProductionLine, CapabilityAnalysis } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = Number(route.params.id)
const line = ref<ProductionLine | null>(null)
const analyses = ref<CapabilityAnalysis[]>([])
const filterType = ref('')

const filteredAnalyses = computed(() => {
  if (!filterType.value) return analyses.value
  return analyses.value.filter(a => a.analysis_type === filterType.value)
})

const excellentCount = computed(() => {
  return analyses.value.filter(a => parseFloat(a.cpk || '0') >= 1.33).length
})

const poorCount = computed(() => {
  return analyses.value.filter(a => parseFloat(a.cpk || '0') < 1.0).length
})

const latestCpk = computed(() => {
  if (analyses.value.length === 0) return '–'
  return parseFloat(analyses.value[0].cpk || '0').toFixed(3)
})

const getIndexClass = (value: number) => {
  if (value >= 1.67) return 'excellent'
  if (value >= 1.33) return 'good'
  if (value >= 1.0) return 'fair'
  return 'poor'
}

const getStatusClass = (value: number) => {
  if (value >= 1.67) return 'excellent'
  if (value >= 1.33) return 'good'
  if (value >= 1.0) return 'fair'
  return 'poor'
}

const getStatusText = (value: number) => {
  if (value >= 1.67) return '能力优秀'
  if (value >= 1.33) return '能力充足'
  if (value >= 1.0) return '能力一般'
  return '能力不足'
}

const getAnalysisTypeText = (type: string) => {
  const map: Record<string, string> = {
    process: '过程能力',
    machine: '机器能力',
    preliminary: '预分析'
  }
  return map[type] || type
}

const formatTime = (time?: string) => {
  if (!time) return '–'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchData = async () => {
  try {
    const [lineRes, analysesRes] = await Promise.all([
      getProductionLine(lineId),
      getCapabilityAnalyses(lineId)
    ])
    
    line.value = lineRes as ProductionLine
    analyses.value = analysesRes as CapabilityAnalysis[]
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const viewDetail = (id: number) => {
  router.push(`/capability-analysis/${id}`)
}

const goBack = () => {
  router.push(`/production-lines/${lineId}`)
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.page-content {
  padding: 40px;
  max-width: 1400px;
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

.btn-new {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-new:hover {
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.4);
}

.stats-section {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.stat-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--accent-primary);
}

.stat-icon.excellent {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.stat-icon.warning {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.list-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.filter-select {
  width: 160px;
}

.analysis-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.analysis-card {
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.analysis-card:hover {
  border-color: var(--accent-primary);
  transform: translateX(4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 12px;
}

.card-title h3 {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.analysis-type {
  padding: 4px 10px;
  border-radius: 100px;
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  background: rgba(0, 212, 255, 0.1);
  color: var(--accent-primary);
}

.analysis-type.machine {
  background: rgba(168, 85, 247, 0.1);
  color: #a855f7;
}

.analysis-type.preliminary {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.card-time {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.card-body {
  margin-bottom: 16px;
}

.indices-row {
  display: flex;
  gap: 16px;
  margin-bottom: 12px;
}

.index-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 20px;
  background: var(--bg-card);
  border-radius: var(--radius-sm);
  min-width: 80px;
}

.index-item.excellent {
  border: 1px solid #10b981;
}

.index-item.good {
  border: 1px solid #3b82f6;
}

.index-item.fair {
  border: 1px solid #f59e0b;
}

.index-item.poor {
  border: 1px solid #ef4444;
}

.index-name {
  font-size: 0.625rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.index-value {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.specs-row {
  display: flex;
  gap: 24px;
}

.spec-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.spec-label {
  font-size: 0.625rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.spec-value {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--text-primary);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 100px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.excellent {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.status-badge.good {
  background: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.status-badge.fair {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.status-badge.poor {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  color: var(--text-muted);
  margin-bottom: 16px;
}

.empty-state h3 {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 0.875rem;
  color: var(--text-muted);
}

@media (max-width: 1200px) {
  .stats-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .indices-row {
    flex-wrap: wrap;
  }
}
</style>
