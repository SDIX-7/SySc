<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content" v-if="analysis">
      <div class="page-header">
        <div class="header-left">
          <button class="btn-back" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">{{ analysis.analysis_name || '能力分析报告' }}</h1>
            <p class="page-subtitle">{{ formatTime(analysis.analysis_time) }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="analysis-type-badge" :class="analysis.analysis_type">
            {{ getAnalysisTypeText(analysis.analysis_type) }}
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="indices-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </span>
            能力指数
          </h2>
          
          <div class="indices-grid">
            <div class="index-card" :class="getIndexClass(indices?.cpk?.value)">
              <div class="index-header">
                <span class="index-name">Cpk</span>
                <span class="index-rating" :style="{ color: indices?.cpk?.color }">
                  {{ indices?.cpk?.rating || '–' }}
                </span>
              </div>
              <div class="index-value" :style="{ color: indices?.cpk?.color }">
                {{ indices?.cpk?.value?.toFixed(3) || '–' }}
              </div>
              <div class="index-desc">过程能力指数</div>
            </div>
            
            <div class="index-card" :class="getIndexClass(indices?.cp?.value)">
              <div class="index-header">
                <span class="index-name">Cp</span>
                <span class="index-rating" :style="{ color: indices?.cp?.color }">
                  {{ indices?.cp?.rating || '–' }}
                </span>
              </div>
              <div class="index-value" :style="{ color: indices?.cp?.color }">
                {{ indices?.cp?.value?.toFixed(3) || '–' }}
              </div>
              <div class="index-desc">潜在过程能力</div>
            </div>
            
            <div class="index-card" :class="getIndexClass(indices?.ppk?.value)">
              <div class="index-header">
                <span class="index-name">Ppk</span>
                <span class="index-rating" :style="{ color: indices?.ppk?.color }">
                  {{ indices?.ppk?.rating || '–' }}
                </span>
              </div>
              <div class="index-value" :style="{ color: indices?.ppk?.color }">
                {{ indices?.ppk?.value?.toFixed(3) || '–' }}
              </div>
              <div class="index-desc">过程绩效指数</div>
            </div>
            
            <div class="index-card" :class="getIndexClass(indices?.pp?.value)">
              <div class="index-header">
                <span class="index-name">Pp</span>
                <span class="index-rating" :style="{ color: indices?.pp?.color }">
                  {{ indices?.pp?.rating || '–' }}
                </span>
              </div>
              <div class="index-value" :style="{ color: indices?.pp?.color }">
                {{ indices?.pp?.value?.toFixed(3) || '–' }}
              </div>
              <div class="index-desc">潜在过程绩效</div>
            </div>
            
            <div class="index-card" v-if="indices?.cm?.value" :class="getIndexClass(indices?.cm?.value)">
              <div class="index-header">
                <span class="index-name">Cm</span>
                <span class="index-rating" :style="{ color: indices?.cm?.color }">
                  {{ indices?.cm?.rating || '–' }}
                </span>
              </div>
              <div class="index-value" :style="{ color: indices?.cm?.color }">
                {{ indices?.cm?.value?.toFixed(3) || '–' }}
              </div>
              <div class="index-desc">机器能力</div>
            </div>
            
            <div class="index-card" v-if="indices?.cmk?.value" :class="getIndexClass(indices?.cmk?.value)">
              <div class="index-header">
                <span class="index-name">Cmk</span>
                <span class="index-rating" :style="{ color: indices?.cmk?.color }">
                  {{ indices?.cmk?.rating || '–' }}
                </span>
              </div>
              <div class="index-value" :style="{ color: indices?.cmk?.color }">
                {{ indices?.cmk?.value?.toFixed(3) || '–' }}
              </div>
              <div class="index-desc">机器能力指数</div>
            </div>
          </div>
        </div>

        <div class="chart-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18"/>
                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
              </svg>
            </span>
            分布直方图
          </h2>
          <div ref="histogramChart" class="chart-container"></div>
        </div>

        <div class="specs-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
            </span>
            规格信息
          </h2>
          
          <div class="specs-grid">
            <div class="spec-item">
              <span class="spec-label">规格上限 (USL)</span>
              <span class="spec-value">{{ parseFloat(analysis.usl).toFixed(4) }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">目标值 (Target)</span>
              <span class="spec-value">{{ analysis.target ? parseFloat(analysis.target).toFixed(4) : '–' }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">规格下限 (LSL)</span>
              <span class="spec-value">{{ parseFloat(analysis.lsl).toFixed(4) }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">过程均值 (μ)</span>
              <span class="spec-value">{{ parseFloat(analysis.mean).toFixed(4) }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">组内标准差 (σ_within)</span>
              <span class="spec-value">{{ parseFloat(analysis.sigma_within).toFixed(4) }}</span>
            </div>
            <div class="spec-item">
              <span class="spec-label">整体标准差 (σ_overall)</span>
              <span class="spec-value">{{ parseFloat(analysis.sigma_overall).toFixed(4) }}</span>
            </div>
          </div>
        </div>

        <div class="stats-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="9" y1="21" x2="9" y2="9"/>
              </svg>
            </span>
            数据统计
          </h2>
          
          <div class="stats-grid">
            <div class="stat-card">
              <span class="stat-value">{{ analysis.sample_count }}</span>
              <span class="stat-label">样本数量</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ analysis.subgroup_count }}</span>
              <span class="stat-label">子组数量</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ minValue.toFixed(4) }}</span>
              <span class="stat-label">最小值</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ maxValue.toFixed(4) }}</span>
              <span class="stat-label">最大值</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ rangeValue.toFixed(4) }}</span>
              <span class="stat-label">极差</span>
            </div>
            <div class="stat-card">
              <span class="stat-value">{{ parseFloat(analysis.mean).toFixed(4) }}</span>
              <span class="stat-label">平均值</span>
            </div>
          </div>
        </div>

        <div class="normality-section" v-if="normalityTest">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
            </span>
            正态性检验
          </h2>
          
          <div class="normality-result" :class="{ 'is-normal': normalityTest.is_normal }">
            <div class="normality-status">
              <div class="status-icon">
                <svg v-if="normalityTest.is_normal" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </div>
              <div class="status-text">
                {{ normalityTest.is_normal ? '数据服从正态分布' : '数据不服从正态分布' }}
              </div>
            </div>
            <div class="normality-details">
              <div class="detail-item">
                <span class="detail-label">检验方法</span>
                <span class="detail-value">{{ normalityTest.test_name }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">P值</span>
                <span class="detail-value">{{ normalityTest.p_value.toFixed(4) }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">统计量</span>
                <span class="detail-value">{{ normalityTest.statistic.toFixed(4) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="evaluation-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
              </svg>
            </span>
            能力评价
          </h2>
          
          <div class="evaluation-content">
            <div class="evaluation-summary" :class="overallEvaluation.class">
              <div class="summary-icon">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <path d="M8 14s1.5 2 4 2 4-2 4-2"/>
                  <line x1="9" y1="9" x2="9.01" y2="9"/>
                  <line x1="15" y1="9" x2="15.01" y2="9"/>
                </svg>
              </div>
              <div class="summary-text">
                <h3>{{ overallEvaluation.title }}</h3>
                <p>{{ overallEvaluation.description }}</p>
              </div>
            </div>
            
            <div class="evaluation-scale">
              <h4>能力等级标准</h4>
              <div class="scale-items">
                <div class="scale-item excellent">
                  <span class="scale-range">Cpk ≥ 1.67</span>
                  <span class="scale-desc">能力优秀</span>
                </div>
                <div class="scale-item good">
                  <span class="scale-range">1.33 ≤ Cpk < 1.67</span>
                  <span class="scale-desc">能力充足</span>
                </div>
                <div class="scale-item fair">
                  <span class="scale-range">1.00 ≤ Cpk < 1.33</span>
                  <span class="scale-desc">能力一般</span>
                </div>
                <div class="scale-item poor">
                  <span class="scale-range">Cpk < 1.00</span>
                  <span class="scale-desc">能力不足</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="loading-container" v-else>
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import Menu from '@/components/Menu.vue'
import { getCapabilityAnalysis } from '@/api'
import type { CapabilityAnalysisResult, CapabilityIndices } from '@/types'

const route = useRoute()
const router = useRouter()

const analysisId = Number(route.params.analysisId)
const analysis = ref<CapabilityAnalysisResult | null>(null)
const indices = ref<CapabilityIndices | null>(null)
const normalityTest = ref<{ is_normal: boolean; p_value: number; statistic: number; test_name: string } | null>(null)
const histogramChart = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const minValue = computed(() => {
  if (!analysis.value?.data_values?.length) return 0
  return Math.min(...analysis.value.data_values)
})

const maxValue = computed(() => {
  if (!analysis.value?.data_values?.length) return 0
  return Math.max(...analysis.value.data_values)
})

const rangeValue = computed(() => maxValue.value - minValue.value)

const overallEvaluation = computed(() => {
  const cpk = indices.value?.cpk?.value || 0
  
  if (cpk >= 1.67) {
    return {
      class: 'excellent',
      title: '过程能力优秀',
      description: '过程能力非常出色，产品质量稳定可靠，可以适当降低检验频率。'
    }
  } else if (cpk >= 1.33) {
    return {
      class: 'good',
      title: '过程能力充足',
      description: '过程能力良好，产品质量满足要求，建议保持当前控制水平。'
    }
  } else if (cpk >= 1.0) {
    return {
      class: 'fair',
      title: '过程能力一般',
      description: '过程能力处于临界状态，建议分析原因并采取改进措施。'
    }
  } else {
    return {
      class: 'poor',
      title: '过程能力不足',
      description: '过程能力不足，产品质量风险较高，需要立即采取纠正措施。'
    }
  }
})

const getIndexClass = (value?: number) => {
  if (!value) return ''
  if (value >= 1.67) return 'excellent'
  if (value >= 1.33) return 'good'
  if (value >= 1.0) return 'fair'
  return 'poor'
}

const getAnalysisTypeText = (type: string) => {
  const map: Record<string, string> = {
    process: '过程能力分析',
    machine: '机器能力分析',
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

const fetchAnalysis = async () => {
  try {
    const result = await getCapabilityAnalysis(analysisId)
    analysis.value = result as CapabilityAnalysisResult
    
    if ((result as any).indices) {
      indices.value = (result as any).indices
    }
    
    if ((result as any).normality_test) {
      normalityTest.value = (result as any).normality_test
    }
    
    await nextTick()
    renderHistogram()
  } catch (error) {
    console.error('获取分析数据失败:', error)
    ElMessage.error('获取分析数据失败')
  }
}

const renderHistogram = () => {
  if (!histogramChart.value || !analysis.value?.data_values?.length) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(histogramChart.value)
  
  const data = analysis.value.data_values
  const usl = parseFloat(analysis.value.usl)
  const lsl = parseFloat(analysis.value.lsl)
  const mean = parseFloat(analysis.value.mean || '0')
  const sigma = parseFloat(analysis.value.sigma_overall || '1')
  
  const binCount = Math.ceil(Math.sqrt(data.length))
  const dataMin = Math.min(...data)
  const dataMax = Math.max(...data)
  const binWidth = (dataMax - dataMin) / binCount
  
  const bins: number[] = new Array(binCount).fill(0)
  data.forEach(val => {
    const binIndex = Math.min(Math.floor((val - dataMin) / binWidth), binCount - 1)
    bins[binIndex]++
  })
  
  const xAxisData: string[] = []
  for (let i = 0; i < binCount; i++) {
    const start = dataMin + i * binWidth
    const end = start + binWidth
    xAxisData.push(`${start.toFixed(2)}-${end.toFixed(2)}`)
  }
  
  const normalCurveX: number[] = []
  const normalCurveY: number[] = []
  const step = (dataMax - dataMin) / 100
  const maxFreq = Math.max(...bins)
  
  for (let x = dataMin; x <= dataMax; x += step) {
    normalCurveX.push(x)
    const y = (1 / (sigma * Math.sqrt(2 * Math.PI))) * 
              Math.exp(-0.5 * Math.pow((x - mean) / sigma, 2))
    normalCurveY.push(y * data.length * binWidth)
  }
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: { color: '#e2e8f0' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: xAxisData,
      axisLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.3)' } },
      axisLabel: { 
        color: '#94a3b8',
        fontSize: 10,
        rotate: 45
      },
      axisTick: { lineStyle: { color: 'rgba(148, 163, 184, 0.3)' } }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisLabel: { color: '#94a3b8' },
      splitLine: { lineStyle: { color: 'rgba(148, 163, 184, 0.1)' } }
    },
    series: [
      {
        name: '频数',
        type: 'bar',
        data: bins,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(0, 212, 255, 0.8)' },
            { offset: 1, color: 'rgba(0, 212, 255, 0.2)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '60%'
      },
      {
        name: '正态分布',
        type: 'line',
        data: normalCurveY,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#10b981',
          width: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' }
          ])
        }
      }
    ],
    markLines: [
      {
        symbol: 'none',
        data: [
          {
            name: 'USL',
            xAxis: usl,
            lineStyle: { color: '#ef4444', type: 'dashed' },
            label: { formatter: 'USL', position: 'end' }
          },
          {
            name: 'LSL',
            xAxis: lsl,
            lineStyle: { color: '#ef4444', type: 'dashed' },
            label: { formatter: 'LSL', position: 'end' }
          },
          {
            name: 'Mean',
            xAxis: mean,
            lineStyle: { color: '#00d4ff', type: 'solid' },
            label: { formatter: 'Mean', position: 'end' }
          }
        ]
      }
    ]
  }
  
  chartInstance.setOption(option)
  
  window.addEventListener('resize', () => {
    chartInstance?.resize()
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchAnalysis()
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

.analysis-type-badge {
  padding: 6px 16px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  background: rgba(0, 212, 255, 0.15);
  color: var(--accent-primary);
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.indices-section,
.chart-section,
.specs-section,
.stats-section,
.normality-section,
.evaluation-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 12px;
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
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

.indices-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.index-card {
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.index-card.excellent {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.index-card.good {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.05);
}

.index-card.fair {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.05);
}

.index-card.poor {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.index-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.index-name {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.index-rating {
  font-size: 0.75rem;
  font-weight: 500;
}

.index-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 4px;
}

.index-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.chart-container {
  height: 350px;
}

.specs-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.spec-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.spec-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.spec-value {
  font-family: var(--font-mono);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.stat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.stat-value {
  font-family: var(--font-mono);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--accent-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.normality-result {
  display: flex;
  gap: 24px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.normality-result.is-normal {
  border-color: var(--success);
  background: rgba(16, 185, 129, 0.05);
}

.normality-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-icon {
  color: var(--danger);
}

.normality-result.is-normal .status-icon {
  color: var(--success);
}

.status-text {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.normality-details {
  display: flex;
  gap: 24px;
  margin-left: auto;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.detail-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.detail-value {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.evaluation-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.evaluation-summary {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 2px solid var(--border-color);
}

.evaluation-summary.excellent {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.evaluation-summary.good {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}

.evaluation-summary.fair {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.evaluation-summary.poor {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.summary-icon {
  color: var(--text-muted);
}

.evaluation-summary.excellent .summary-icon { color: #10b981; }
.evaluation-summary.good .summary-icon { color: #3b82f6; }
.evaluation-summary.fair .summary-icon { color: #f59e0b; }
.evaluation-summary.poor .summary-icon { color: #ef4444; }

.summary-text h3 {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.summary-text p {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.evaluation-scale h4 {
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.scale-items {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.scale-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border-radius: var(--radius-sm);
  text-align: center;
}

.scale-item.excellent {
  background: rgba(16, 185, 129, 0.1);
}

.scale-item.good {
  background: rgba(59, 130, 246, 0.1);
}

.scale-item.fair {
  background: rgba(245, 158, 11, 0.1);
}

.scale-item.poor {
  background: rgba(239, 68, 68, 0.1);
}

.scale-range {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-primary);
}

.scale-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
}

.loading-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid var(--border-color);
  border-top-color: var(--accent-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 1200px) {
  .dashboard-grid {
    grid-template-columns: 1fr;
  }
  
  .indices-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .specs-grid,
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .scale-items {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
