<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">过程控制</h1>
          <p class="page-subtitle">实时U图监控和异常模式检测</p>
        </div>
        <div class="header-right">
          <button class="btn-secondary" @click="loadChartData">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M23 4v6h-6"/>
              <path d="M1 20v-6h6"/>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
            </svg>
            刷新
          </button>
          <div class="auto-refresh" :class="{ active: autoRefresh }" @click="toggleAutoRefresh">
            <span class="refresh-dot"></span>
            <span>{{ autoRefresh ? '自动刷新' : '已暂停' }}</span>
          </div>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-value">{{ statistics.totalSamples }}</div>
          <div class="stat-label">样本总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.meanU.toFixed(4) }}</div>
          <div class="stat-label">平均U值</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ statistics.ucl.toFixed(4) }}</div>
          <div class="stat-label">控制上限</div>
        </div>
        <div class="stat-card" :class="{ danger: statistics.totalAbnormal > 0 }">
          <div class="stat-value">{{ statistics.totalAbnormal }}</div>
          <div class="stat-label">异常点数</div>
        </div>
      </div>
      
      <div class="chart-section">
        <div class="chart-header">
          <h3 class="chart-title">U图控制图</h3>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-dot normal"></span>
              <span>正常</span>
            </div>
            <div class="legend-item">
              <span class="legend-dot abnormal"></span>
              <span>异常</span>
            </div>
          </div>
        </div>
        <div ref="chartRef" class="chart-container"></div>
      </div>
      
      <div class="rules-section">
        <h3 class="section-title">异常规则检测</h3>
        <div class="rules-grid">
          <div 
            v-for="rule in ruleResults" 
            :key="rule.rule" 
            class="rule-card"
            :class="{ danger: rule.abnormalCount > 0, success: rule.abnormalCount === 0 }"
          >
            <div class="rule-header">
              <span class="rule-number">{{ rule.rule }}</span>
              <span class="rule-status" :class="rule.abnormalCount > 0 ? 'danger' : 'success'">
                {{ rule.abnormalCount > 0 ? '!' : '✓' }}
              </span>
            </div>
            <p class="rule-description">{{ rule.description }}</p>
            <div class="rule-count">
              <span class="count-value">{{ rule.abnormalCount }}</span>
              <span class="count-label">次违规</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import Menu from '@/components/Menu.vue'
import { getControlChartData } from '@/api'
import type { ControlChartData } from '@/types'

const chartRef = ref<HTMLElement>()
let chart: echarts.ECharts | null = null

const chartData = ref<ControlChartData | null>(null)
const statistics = reactive({
  totalSamples: 0,
  totalDefects: 0,
  meanU: 0,
  ucl: 0,
  totalAbnormal: 0
})

const ruleResults = ref([
  { rule: '规则1', description: '点超出3σ控制界限', abnormalCount: 0 },
  { rule: '规则2', description: '连续9点在中心线同侧', abnormalCount: 0 },
  { rule: '规则3', description: '连续6点递增或递减', abnormalCount: 0 },
  { rule: '规则4', description: '连续14点上下交替', abnormalCount: 0 },
  { rule: '规则5', description: '连续3点中有2点在2σ区外', abnormalCount: 0 },
  { rule: '规则6', description: '连续5点中有4点在1σ区外', abnormalCount: 0 },
  { rule: '规则7', description: '连续15点在1σ区内', abnormalCount: 0 },
  { rule: '规则8', description: '连续8点无1点在1σ区内', abnormalCount: 0 }
])

const autoRefresh = ref(true)
let refreshTimer: ReturnType<typeof setInterval> | null = null

const initChart = () => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value, 'dark')
  }
}

const loadChartData = async () => {
  try {
    const response = await getControlChartData() as ControlChartData
    chartData.value = response
    updateStatistics()
    updateRuleResults()
    renderChart()
  } catch (error) {
    console.error('加载控制图数据失败:', error)
  }
}

const updateStatistics = () => {
  if (!chartData.value) return
  statistics.totalSamples = chartData.value.u_list.length
  statistics.meanU = chartData.value.center_line
  statistics.ucl = chartData.value.ucl_list[0] || 0
  
  const uniqueAbnormal = new Set<number>()
  Object.values(chartData.value.abnormal_rules).forEach(indices => {
    indices.forEach(i => uniqueAbnormal.add(i))
  })
  statistics.totalAbnormal = uniqueAbnormal.size
}

const updateRuleResults = () => {
  if (!chartData.value) return
  const { abnormal_rules } = chartData.value
  
  ruleResults.value = ruleResults.value.map((rule, index) => {
    const ruleNum = index + 1
    const indices = abnormal_rules[ruleNum] || []
    return {
      ...rule,
      abnormalCount: indices.length
    }
  })
}

const renderChart = () => {
  if (!chart || !chartData.value) return
  
  const { u_list, center_line, abnormal_points, ucl_list, lcl_list } = chartData.value
  const sampleLabels = u_list.map((_, i) => `#${i + 1}`)
  
  const option: echarts.EChartsOption = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(17, 24, 39, 0.95)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: { color: '#f1f5f9' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: sampleLabels,
      axisLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.2)' } },
      axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono' }
    },
    yAxis: {
      type: 'value',
      name: 'U值',
      nameTextStyle: { color: '#94a3b8' },
      axisLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.2)' } },
      splitLine: { lineStyle: { color: 'rgba(0, 212, 255, 0.1)' } },
      axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono' }
    },
    series: [
      {
        name: 'U值',
        type: 'line',
        data: u_list.map((value, index) => ({
          value,
          itemStyle: {
            color: abnormal_points.includes(index) ? '#ef4444' : '#00d4ff'
          }
        })),
        symbol: 'circle',
        symbolSize: 8,
        lineStyle: { color: '#00d4ff', width: 2 },
        emphasis: { scale: true }
      },
      {
        name: '中心线',
        type: 'line',
        data: Array(u_list.length).fill(center_line),
        lineStyle: { color: '#10b981', type: 'dashed', width: 1 },
        symbol: 'none'
      },
      {
        name: '控制上限',
        type: 'line',
        data: ucl_list,
        lineStyle: { color: '#ef4444', type: 'dashed', width: 1 },
        symbol: 'none'
      },
      {
        name: '控制下限',
        type: 'line',
        data: lcl_list,
        lineStyle: { color: '#ef4444', type: 'dashed', width: 1 },
        symbol: 'none'
      }
    ]
  }
  
  chart.setOption(option)
}

const toggleAutoRefresh = () => {
  autoRefresh.value = !autoRefresh.value
  if (autoRefresh.value) {
    startAutoRefresh()
  } else {
    stopAutoRefresh()
  }
}

const startAutoRefresh = () => {
  stopAutoRefresh()
  refreshTimer = setInterval(loadChartData, 30000)
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

onMounted(() => {
  initChart()
  loadChartData()
  if (autoRefresh.value) startAutoRefresh()
})

onBeforeUnmount(() => {
  if (chart) chart.dispose()
  stopAutoRefresh()
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

.header-right {
  display: flex;
  gap: 12px;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.auto-refresh {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-family: var(--font-mono);
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.auto-refresh.active {
  border-color: var(--success);
  color: var(--success);
}

.refresh-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.auto-refresh.active .refresh-dot {
  animation: pulse 2s ease-in-out infinite;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 24px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--accent-gradient);
}

.stat-card.danger::before {
  background: var(--danger);
}

.stat-value {
  font-family: var(--font-display);
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin-bottom: 4px;
}

.stat-card.danger .stat-value {
  color: var(--danger);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.chart-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 32px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.chart-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.normal {
  background: var(--accent-primary);
}

.legend-dot.abnormal {
  background: var(--danger);
}

.chart-container {
  height: 400px;
}

.rules-section {
  margin-top: 32px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  letter-spacing: 0.05em;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.rule-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px;
  transition: all var(--transition-normal);
}

.rule-card.danger {
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.05);
}

.rule-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.rule-number {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--accent-primary);
}

.rule-status {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
}

.rule-status.success {
  background: rgba(16, 185, 129, 0.2);
  color: var(--success);
}

.rule-status.danger {
  background: rgba(239, 68, 68, 0.2);
  color: var(--danger);
}

.rule-description {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 12px;
}

.rule-count {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.count-value {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
}

.rule-card.danger .count-value {
  color: var(--danger);
}

.count-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .rules-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .stats-row,
  .rules-grid {
    grid-template-columns: 1fr;
  }
}
</style>
