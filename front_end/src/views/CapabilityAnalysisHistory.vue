<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">能力分析历史</h1>
          <p class="page-subtitle">所有产线的能力分析记录</p>
        </div>
      </div>

      <div class="filters-section">
        <div class="filter-group">
          <label class="filter-label">产线筛选</label>
          <el-select v-model="filterLine" placeholder="全部产线" clearable class="filter-select">
            <el-option 
              v-for="line in productionLines" 
              :key="line.id" 
              :label="line.line_name" 
              :value="line.id" 
            />
          </el-select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">分析类型</label>
          <el-select v-model="filterType" placeholder="全部类型" clearable class="filter-select">
            <el-option label="过程能力分析" value="process" />
            <el-option label="机器能力分析" value="machine" />
            <el-option label="预分析" value="preliminary" />
          </el-select>
        </div>
        
        <div class="filter-group">
          <label class="filter-label">能力等级</label>
          <el-select v-model="filterRating" placeholder="全部等级" clearable class="filter-select">
            <el-option label="能力优秀 (Cpk ≥ 1.67)" value="excellent" />
            <el-option label="能力充足 (Cpk ≥ 1.33)" value="good" />
            <el-option label="能力一般 (Cpk ≥ 1.0)" value="fair" />
            <el-option label="能力不足 (Cpk < 1.0)" value="poor" />
          </el-select>
        </div>
      </div>

      <div class="table-section">
        <el-table 
          :data="filteredAnalyses" 
          style="width: 100%"
          class="analysis-table"
          @row-click="viewDetail"
        >
          <el-table-column label="分析名称" min-width="200">
            <template #default="{ row }">
              <div class="name-cell">
                <span class="analysis-name">{{ row.analysis_name || `分析 #${row.id}` }}</span>
                <span class="analysis-type" :class="row.analysis_type">
                  {{ getAnalysisTypeText(row.analysis_type) }}
                </span>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="产线" prop="line_name" width="150" />
          
          <el-table-column label="Cpk" width="100" align="center">
            <template #default="{ row }">
              <span class="index-value" :class="getIndexClass(parseFloat(row.cpk || '0'))">
                {{ parseFloat(row.cpk || '0').toFixed(3) }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="Cp" width="100" align="center">
            <template #default="{ row }">
              <span class="index-value" :class="getIndexClass(parseFloat(row.cp || '0'))">
                {{ parseFloat(row.cp || '0').toFixed(3) }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="Ppk" width="100" align="center">
            <template #default="{ row }">
              <span class="index-value" :class="getIndexClass(parseFloat(row.ppk || '0'))">
                {{ parseFloat(row.ppk || '0').toFixed(3) }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="样本数" prop="sample_count" width="100" align="center" />
          
          <el-table-column label="分析时间" width="160">
            <template #default="{ row }">
              {{ formatTime(row.analysis_time) }}
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="120" align="center">
            <template #default="{ row }">
              <span class="status-badge" :class="getStatusClass(parseFloat(row.cpk || '0'))">
                {{ getStatusText(parseFloat(row.cpk || '0')) }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <button class="btn-view" @click.stop="viewDetail(row)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              </button>
            </template>
          </el-table-column>
        </el-table>
        
        <div class="empty-state" v-if="filteredAnalyses.length === 0">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
          </div>
          <h3>暂无分析记录</h3>
          <p>请先在产线页面创建能力分析</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getProductionLines, getCapabilityAnalyses } from '@/api'
import type { ProductionLine, CapabilityAnalysis } from '@/types'

const router = useRouter()

const productionLines = ref<ProductionLine[]>([])
const analyses = ref<CapabilityAnalysis[]>([])

const filterLine = ref<number | null>(null)
const filterType = ref('')
const filterRating = ref('')

const filteredAnalyses = computed(() => {
  let result = analyses.value
  
  if (filterLine.value) {
    result = result.filter(a => a.line_id === filterLine.value)
  }
  
  if (filterType.value) {
    result = result.filter(a => a.analysis_type === filterType.value)
  }
  
  if (filterRating.value) {
    result = result.filter(a => {
      const cpk = parseFloat(a.cpk || '0')
      switch (filterRating.value) {
        case 'excellent': return cpk >= 1.67
        case 'good': return cpk >= 1.33 && cpk < 1.67
        case 'fair': return cpk >= 1.0 && cpk < 1.33
        case 'poor': return cpk < 1.0
        default: return true
      }
    })
  }
  
  return result
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
  if (value >= 1.67) return '优秀'
  if (value >= 1.33) return '充足'
  if (value >= 1.0) return '一般'
  return '不足'
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
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const fetchData = async () => {
  try {
    const [linesRes, analysesRes] = await Promise.all([
      getProductionLines(),
      getCapabilityAnalyses()
    ])
    
    productionLines.value = linesRes as ProductionLine[]
    const allAnalyses = analysesRes as CapabilityAnalysis[]
    
    const lineMap = new Map(productionLines.value.map(l => [l.id, l.line_name]))
    analyses.value = allAnalyses.map(a => ({
      ...a,
      line_name: lineMap.get(a.line_id) || '未知产线'
    }))
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const viewDetail = (row: CapabilityAnalysis) => {
  router.push(`/capability-analysis/${row.id}`)
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

.filters-section {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  padding: 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.filter-select {
  width: 200px;
}

.table-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.analysis-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: transparent;
  --el-table-header-bg-color: var(--bg-secondary);
  --el-table-row-hover-bg-color: rgba(0, 212, 255, 0.05);
  --el-table-border-color: var(--border-color);
  --el-table-text-color: var(--text-primary);
  --el-table-header-text-color: var(--text-muted);
}

.name-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.analysis-name {
  font-weight: 500;
  color: var(--text-primary);
}

.analysis-type {
  font-size: 0.625rem;
  padding: 2px 8px;
  border-radius: 100px;
  width: fit-content;
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

.index-value {
  font-family: var(--font-mono);
  font-weight: 600;
}

.index-value.excellent { color: #10b981; }
.index-value.good { color: #3b82f6; }
.index-value.fair { color: #f59e0b; }
.index-value.poor { color: #ef4444; }

.status-badge {
  padding: 4px 10px;
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

.btn-view {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-view:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
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
</style>
