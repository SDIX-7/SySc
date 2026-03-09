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
            <h1 class="page-title">SPC控制图</h1>
            <p class="page-subtitle">{{ line?.line_name }}</p>
          </div>
        </div>
        
        <div class="header-right">
          <div class="chart-controls">
            <div class="chart-type-selector">
              <label>控制图类型：</label>
              <select v-model="selectedChartType" @change="onChartTypeChange">
                <optgroup v-if="line?.data_type === 'measurement'" label="计量型控制图">
                  <option value="XR">X-R图 (均值-极差)</option>
                  <option value="XS">X-s图 (均值-标准差)</option>
                  <option value="IMR">I-MR图 (单值-移动极差)</option>
                  <option value="MEDIAN">中位数-极差图</option>
                </optgroup>
                <optgroup v-if="line?.data_type === 'attribute'" label="计数型控制图">
                  <option value="P">P图 (不合格品率) - 样本量变化</option>
                  <option value="NP">NP图 (不合格品数) - 样本量固定</option>
                  <option value="C">C图 (缺陷数) - 检查单位固定</option>
                  <option value="U">U图 (单位缺陷数) - 检查单位不固定</option>
                </optgroup>
              </select>
            </div>
          </div>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="20" x2="12" y2="10"/>
              <line x1="18" y1="20" x2="18" y2="4"/>
              <line x1="6" y1="20" x2="6" y2="16"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ chartData.ucl?.toFixed(2) || '–' }}</span>
            <span class="stat-label">UCL (上限)</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon success">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ chartData.center?.toFixed(2) || '–' }}</span>
            <span class="stat-label">CL (中心线)</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="4" x2="12" y2="14"/>
              <line x1="18" y1="4" x2="18" y2="20"/>
              <line x1="6" y1="4" x2="6" y2="20"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ chartData.lcl?.toFixed(2) || '–' }}</span>
            <span class="stat-label">LCL (下限)</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon warning" v-if="abnormalPoints > 0">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="stat-icon success" v-else>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ abnormalPoints }}</span>
            <span class="stat-label">异常点</span>
          </div>
        </div>
      </div>
      
      <div class="analysis-section" v-if="line?.data_type === 'measurement' && hasData">
        <div class="histogram-panel">
          <div class="panel-header">
            <h3 class="panel-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18"/>
                <rect x="7" y="10" width="3" height="8"/>
                <rect x="12" y="6" width="3" height="12"/>
                <rect x="17" y="13" width="3" height="5"/>
              </svg>
              数据分布直方图
            </h3>
            <div class="histogram-controls">
              <label>组数：</label>
              <select v-model="histogramBins" @change="drawHistogram">
                <option :value="sturgesBins">Sturges规则 ({{ sturgesBins }})</option>
                <option :value="squareRootBins">平方根法则 ({{ squareRootBins }})</option>
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="15">15</option>
                <option value="20">20</option>
              </select>
            </div>
          </div>
          <div class="histogram-container">
            <canvas ref="histogramCanvas"></canvas>
          </div>
          <div class="histogram-stats">
            <div class="h-stat">
              <span class="h-stat-label">样本量</span>
              <span class="h-stat-value">{{ rawData.length }}</span>
            </div>
            <div class="h-stat">
              <span class="h-stat-label">均值</span>
              <span class="h-stat-value">{{ meanValue.toFixed(3) }}</span>
            </div>
            <div class="h-stat">
              <span class="h-stat-label">标准差</span>
              <span class="h-stat-value">{{ stdValue.toFixed(3) }}</span>
            </div>
            <div class="h-stat">
              <span class="h-stat-label">最小值</span>
              <span class="h-stat-value">{{ minValue.toFixed(3) }}</span>
            </div>
            <div class="h-stat">
              <span class="h-stat-label">最大值</span>
              <span class="h-stat-value">{{ maxValue.toFixed(3) }}</span>
            </div>
            <div class="h-stat">
              <span class="h-stat-label">偏度</span>
              <span class="h-stat-value">{{ skewness.toFixed(3) }}</span>
            </div>
          </div>
        </div>
        
        <div class="normality-panel">
          <div class="panel-header">
            <h3 class="panel-title">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              正态性检验
            </h3>
          </div>
          
          <div class="normality-content">
            <div class="test-result" :class="normalityResult.isNormal ? 'normal' : 'not-normal'">
              <div class="result-icon">
                <svg v-if="normalityResult.isNormal" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <svg v-else width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </div>
              <div class="result-text">
                <span class="result-title">{{ normalityResult.isNormal ? '符合正态分布' : '不符合正态分布' }}</span>
                <span class="result-desc">Shapiro-Wilk检验 (α=0.05)</span>
              </div>
            </div>
            
            <div class="test-details">
              <div class="detail-row">
                <span class="detail-label">W统计量</span>
                <span class="detail-value">{{ normalityResult.wStatistic.toFixed(4) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">p值</span>
                <span class="detail-value" :class="{ 'p-significant': normalityResult.pValue < 0.05 }">
                  {{ normalityResult.pValue.toFixed(4) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">显著性水平</span>
                <span class="detail-value">α = 0.05</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">判定依据</span>
                <span class="detail-value explanation">
                  {{ normalityResult.pValue >= 0.05 ? 'p ≥ 0.05，不能拒绝正态性假设' : 'p < 0.05，拒绝正态性假设' }}
                </span>
              </div>
            </div>
            
            <div class="test-interpretation">
              <div class="interpretation-header">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                结果解读
              </div>
              <p class="interpretation-text">
                <template v-if="normalityResult.isNormal">
                  数据分布符合正态性假设，可以使用基于正态分布的统计过程控制方法。X-R图和X-s图的控制限计算有效。
                </template>
                <template v-else>
                  数据分布可能偏离正态分布，建议检查数据是否存在异常值或考虑使用非参数方法。控制图结果需谨慎解读。
                </template>
              </p>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chart-section">
        <div class="chart-header">
          <h2 class="chart-title">{{ getChartTypeName(selectedChartType) }}</h2>
          <div class="chart-legend">
            <span class="legend-item">
              <span class="legend-color data-line"></span>
              数据点
            </span>
            <span class="legend-item">
              <span class="legend-color ucl-line"></span>
              UCL/LCL (3σ)
            </span>
            <span class="legend-item">
              <span class="legend-color sigma2-line"></span>
              ±2σ
            </span>
            <span class="legend-item">
              <span class="legend-color sigma1-line"></span>
              ±1σ
            </span>
            <span class="legend-item">
              <span class="legend-color cl-line"></span>
              CL
            </span>
          </div>
        </div>
        
        <div class="dual-chart-container" v-if="hasData && isDualChart">
          <div class="chart-panel">
            <h3 class="panel-title">{{ getXBarChartTitle() }}</h3>
            <div class="chart-wrapper">
              <canvas ref="xbarCanvas"></canvas>
            </div>
          </div>
          <div class="chart-panel">
            <h3 class="panel-title">{{ getVariationChartTitle() }}</h3>
            <div class="chart-wrapper">
              <canvas ref="variationCanvas"></canvas>
            </div>
          </div>
        </div>
        
        <div class="chart-container single-chart" v-else-if="hasData">
          <canvas ref="chartCanvas"></canvas>
        </div>
        
        <div class="chart-empty" v-else>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M3 3v18h18"/>
            <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
          </svg>
          <p>暂无足够数据生成控制图</p>
          <p class="hint">请先在数据采集页面添加数据</p>
        </div>
      </div>
      
      <div class="alarm-section" v-if="abnormalPoints > 0">
        <h2 class="section-title">异常报警</h2>
        <div class="alarm-list">
          <div v-for="(alarm, index) in alarms" :key="index" class="alarm-item">
            <div class="alarm-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div class="alarm-content">
              <span class="alarm-title">{{ alarm.rule }}</span>
              <span class="alarm-desc">{{ alarm.description }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getProductionLine, getAttributeData, getMeasurementData } from '@/api'
import type { ProductionLine, AttributeData, MeasurementData } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = Number(route.params.id)
const line = ref<ProductionLine | null>(null)
const chartCanvas = ref<HTMLCanvasElement | null>(null)
const xbarCanvas = ref<HTMLCanvasElement | null>(null)
const variationCanvas = ref<HTMLCanvasElement | null>(null)
const histogramCanvas = ref<HTMLCanvasElement | null>(null)
const selectedChartType = ref('U')
const subgroupSize = ref(5)
const histogramBins = ref(10)

const showSubgroupSelector = computed(() => {
  return ['XR', 'XS', 'MEDIAN'].includes(selectedChartType.value)
})

const subgroupSizeOptions = computed(() => {
  const chartType = selectedChartType.value
  if (chartType === 'XR' || chartType === 'MEDIAN') {
    return [2, 3, 4, 5, 6, 7, 8, 9]
  } else if (chartType === 'XS') {
    return [10, 11, 12, 13, 14, 15]
  }
  return []
})

const onChartTypeChange = () => {
  if (selectedChartType.value === 'XR' || selectedChartType.value === 'MEDIAN') {
    subgroupSize.value = 5
  } else if (selectedChartType.value === 'XS') {
    subgroupSize.value = 10
  }
  fetchChartData()
}

interface ChartData {
  ucl?: number
  cl?: number
  lcl?: number
  center?: number
  dataPoints?: { x: number; y: number; abnormal: boolean }[]
}

const chartData = ref<ChartData>({})
const variationChartData = ref<ChartData>({})
const abnormalPoints = ref(0)
const alarms = ref<{ rule: string; description: string }[]>([])
const rawData = ref<number[]>([])

const hasData = computed(() => chartData.value.dataPoints && chartData.value.dataPoints!.length > 0)

const isDualChart = computed(() => {
  return ['XR', 'XS', 'IMR', 'MEDIAN'].includes(selectedChartType.value)
})

const meanValue = computed(() => {
  if (rawData.value.length === 0) return 0
  return rawData.value.reduce((a, b) => a + b, 0) / rawData.value.length
})

const stdValue = computed(() => {
  if (rawData.value.length < 2) return 0
  const mean = meanValue.value
  const squaredDiffs = rawData.value.map(v => Math.pow(v - mean, 2))
  return Math.sqrt(squaredDiffs.reduce((a, b) => a + b, 0) / (rawData.value.length - 1))
})

const minValue = computed(() => rawData.value.length > 0 ? Math.min(...rawData.value) : 0)
const maxValue = computed(() => rawData.value.length > 0 ? Math.max(...rawData.value) : 0)

const skewness = computed(() => {
  if (rawData.value.length < 3) return 0
  const mean = meanValue.value
  const std = stdValue.value
  if (std === 0) return 0
  const cubedDiffs = rawData.value.map(v => Math.pow((v - mean) / std, 3))
  return cubedDiffs.reduce((a, b) => a + b, 0) / rawData.value.length
})

const sturgesBins = computed(() => Math.ceil(Math.log2(rawData.value.length) + 1) || 5)
const squareRootBins = computed(() => Math.ceil(Math.sqrt(rawData.value.length)) || 5)

interface NormalityResult {
  wStatistic: number
  pValue: number
  isNormal: boolean
}

const normalityResult = ref<NormalityResult>({
  wStatistic: 0,
  pValue: 0,
  isNormal: false
})

const shapiroWilkTest = (data: number[]): NormalityResult => {
  const n = data.length
  if (n < 3) {
    return { wStatistic: 0, pValue: 0, isNormal: false }
  }
  
  const sortedData = [...data].sort((a, b) => a - b)
  const mean = sortedData.reduce((a, b) => a + b, 0) / n
  
  let ss = 0
  for (let i = 0; i < n; i++) {
    ss += Math.pow(sortedData[i] - mean, 2)
  }
  
  if (ss === 0) {
    return { wStatistic: 1, pValue: 1, isNormal: true }
  }
  
  const m: number[] = []
  for (let i = 1; i <= n; i++) {
    m.push((n + 1) * (i - (n + 1) / 2) / n)
  }
  
  const mmSum = m.reduce((acc, mi) => acc + mi * mi, 0)
  
  let b = 0
  for (let i = 0; i < n; i++) {
    b += m[i] * (sortedData[i] - mean)
  }
  b = b * b
  
  let w = b / (ss * mmSum)
  
  if (w > 1) w = 1
  if (w < 0) w = 0
  
  let pValue: number
  
  if (n <= 50) {
    const pValueTable: {[key: number]: [number, number]} = {
      3: [0.7337, 0.0410], 4: [0.6288, 0.0884], 5: [0.5522, 0.1289],
      6: [0.4827, 0.1436], 7: [0.4348, 0.1407], 8: [0.3926, 0.1386],
      9: [0.3578, 0.1357], 10: [0.3294, 0.1330], 11: [0.3039, 0.1297],
      12: [0.2815, 0.1257], 13: [0.2616, 0.1212], 14: [0.2438, 0.1165],
      15: [0.2279, 0.1118], 16: [0.2135, 0.1071], 17: [0.2003, 0.1026],
      18: [0.1882, 0.0982], 19: [0.1771, 0.0941], 20: [0.1669, 0.0902],
      21: [0.1575, 0.0865], 22: [0.1488, 0.0830], 23: [0.1408, 0.0797],
      24: [0.1334, 0.0766], 25: [0.1266, 0.0737], 26: [0.1203, 0.0709],
      27: [0.1145, 0.0683], 28: [0.1092, 0.0658], 29: [0.1042, 0.0635],
      30: [0.0996, 0.0613], 31: [0.0954, 0.0593], 32: [0.0915, 0.0574],
      33: [0.0879, 0.0556], 34: [0.0845, 0.0540], 35: [0.0813, 0.0525],
      36: [0.0784, 0.0511], 37: [0.0756, 0.0497], 38: [0.0730, 0.0484],
      39: [0.0706, 0.0472], 40: [0.0683, 0.0461], 41: [0.0662, 0.0450],
      42: [0.0642, 0.0440], 43: [0.0623, 0.0430], 44: [0.0605, 0.0421],
      45: [0.0588, 0.0412], 46: [0.0572, 0.0404], 47: [0.0557, 0.0396],
      48: [0.0543, 0.0388], 49: [0.0529, 0.0381], 50: [0.0516, 0.0374]
    }
    
    if (pValueTable[n]) {
      const [mu, sigma] = pValueTable[n]
      const z = (w - mu) / sigma
      pValue = 1 - normalCDF(z)
    } else {
      pValue = w >= 0.95 ? 0.5 : 0.1
    }
  } else {
    if (w >= 0.99) pValue = 0.99
    else if (w >= 0.97) pValue = 0.95
    else if (w >= 0.94) pValue = 0.90
    else if (w >= 0.90) pValue = 0.80
    else if (w >= 0.85) pValue = 0.70
    else if (w >= 0.80) pValue = 0.50
    else if (w >= 0.75) pValue = 0.30
    else if (w >= 0.70) pValue = 0.20
    else if (w >= 0.65) pValue = 0.10
    else if (w >= 0.60) pValue = 0.05
    else pValue = 0.01
  }
  
  pValue = Math.max(0, Math.min(1, pValue))
  
  return {
    wStatistic: w,
    pValue: pValue,
    isNormal: pValue >= 0.05
  }
}

const normalCDF = (x: number): number => {
  const a1 =  0.254829592
  const a2 = -0.284496736
  const a3 =  1.421413741
  const a4 = -1.453152027
  const a5 =  1.061405429
  const p  =  0.3275911
  
  const sign = x < 0 ? -1 : 1
  x = Math.abs(x) / Math.sqrt(2)
  
  const t = 1.0 / (1.0 + p * x)
  const y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * Math.exp(-x * x)
  
  return 0.5 * (1.0 + sign * y)
}

watch(hasData, async (newVal) => {
  if (newVal) {
    await nextTick()
    drawChart()
    if (line.value?.data_type === 'measurement') {
      drawHistogram()
      normalityResult.value = shapiroWilkTest(rawData.value)
    }
  }
})

watch(histogramBins, () => {
  if (hasData.value && line.value?.data_type === 'measurement') {
    drawHistogram()
  }
})

const detectAbnormalities = (
  values: number[],
  cl: number,
  ucl: number,
  lcl: number
): { rule: string; description: string; points: number[] }[] => {
  const abnormalities: { rule: string; description: string; points: number[] }[] = []
  const sigma = (ucl - cl) / 3
  const sigma1Upper = cl + sigma
  const sigma1Lower = cl - sigma
  const sigma2Upper = cl + 2 * sigma
  const sigma2Lower = cl - 2 * sigma
  
  values.forEach((v, i) => {
    if (v > ucl || v < lcl) {
      const existing = abnormalities.find(a => a.rule === '超出3σ控制线')
      if (existing) {
        existing.points.push(i + 1)
      } else {
        abnormalities.push({
          rule: '超出3σ控制线',
          description: '点超出上下控制限',
          points: [i + 1]
        })
      }
    }
  })
  
  for (let i = 0; i <= values.length - 9; i++) {
    const ninePoints = values.slice(i, i + 9)
    const allAbove = ninePoints.every(v => v > cl)
    const allBelow = ninePoints.every(v => v < cl)
    if (allAbove || allBelow) {
      abnormalities.push({
        rule: '连续9点在中心线同侧',
        description: `第${i + 1}-${i + 9}点连续在中心线${allAbove ? '上方' : '下方'}`,
        points: Array.from({ length: 9 }, (_, j) => i + j + 1)
      })
      break
    }
  }
  
  for (let i = 0; i <= values.length - 6; i++) {
    const sixPoints = values.slice(i, i + 6)
    const increasing = sixPoints.every((v, j) => j === 0 || v > sixPoints[j - 1])
    const decreasing = sixPoints.every((v, j) => j === 0 || v < sixPoints[j - 1])
    if (increasing || decreasing) {
      abnormalities.push({
        rule: '连续6点递增或递减',
        description: `第${i + 1}-${i + 6}点连续${increasing ? '递增' : '递减'}`,
        points: Array.from({ length: 6 }, (_, j) => i + j + 1)
      })
      break
    }
  }
  
  for (let i = 0; i <= values.length - 3; i++) {
    const threePoints = values.slice(i, i + 3)
    const outside2Sigma = threePoints.filter(v => v > sigma2Upper || v < sigma2Lower).length
    if (outside2Sigma >= 2) {
      abnormalities.push({
        rule: '连续3点中有2点在2σ外',
        description: `第${i + 1}-${i + 3}点中有${outside2Sigma}点超出2σ控制线`,
        points: Array.from({ length: 3 }, (_, j) => i + j + 1)
      })
    }
  }
  
  for (let i = 0; i <= values.length - 5; i++) {
    const fivePoints = values.slice(i, i + 5)
    const outside1Sigma = fivePoints.filter(v => v > sigma1Upper || v < sigma1Lower).length
    if (outside1Sigma >= 4) {
      abnormalities.push({
        rule: '连续5点中有4点在1σ外',
        description: `第${i + 1}-${i + 5}点中有${outside1Sigma}点超出1σ控制线`,
        points: Array.from({ length: 5 }, (_, j) => i + j + 1)
      })
    }
  }
  
  for (let i = 0; i <= values.length - 15; i++) {
    const fifteenPoints = values.slice(i, i + 15)
    const inside1Sigma = fifteenPoints.filter(v => v >= sigma1Lower && v <= sigma1Upper).length
    if (inside1Sigma === 15) {
      abnormalities.push({
        rule: '连续15点在1σ内',
        description: `第${i + 1}-${i + 15}点全部在1σ控制线内`,
        points: Array.from({ length: 15 }, (_, j) => i + j + 1)
      })
      break
    }
  }
  
  for (let i = 0; i <= values.length - 8; i++) {
    const eightPoints = values.slice(i, i + 8)
    const outside1Sigma = eightPoints.filter(v => v > sigma1Upper || v < sigma1Lower).length
    if (outside1Sigma === 8) {
      abnormalities.push({
        rule: '连续8点在中心线两侧且无1点在1σ内',
        description: `第${i + 1}-${i + 8}点全部在1σ控制线外`,
        points: Array.from({ length: 8 }, (_, j) => i + j + 1)
      })
      break
    }
  }
  
  return abnormalities
}

const getChartTypeName = (type: string) => {
  const map: Record<string, string> = {
    U: 'U图 - 单位缺陷数控制图',
    P: 'P图 - 不合格率控制图',
    NP: 'NP图 - 不合格数控制图',
    C: 'C图 - 缺陷数控制图',
    XR: 'X-R图 - 均值-极差控制图',
    XS: 'X-s图 - 均值-标准差控制图',
    IMR: 'I-MR图 - 单值-移动极差控制图',
    MEDIAN: '中位数-极差控制图'
  }
  return map[type] || type
}

const getXBarChartTitle = () => {
  const map: Record<string, string> = {
    XR: 'X图 (均值控制图)',
    XS: 'X图 (均值控制图)',
    IMR: 'I图 (单值控制图)',
    MEDIAN: '中位数控制图'
  }
  return map[selectedChartType.value] || '均值控制图'
}

const getVariationChartTitle = () => {
  const map: Record<string, string> = {
    XR: 'R图 (极差控制图)',
    XS: 's图 (标准差控制图)',
    IMR: 'MR图 (移动极差控制图)',
    MEDIAN: 'R图 (极差控制图)'
  }
  return map[selectedChartType.value] || '变异控制图'
}

const fetchData = async () => {
  try {
    const lineRes = await getProductionLine(lineId)
    line.value = lineRes as ProductionLine
    
    const dataType = line.value?.data_type
    
    if (dataType === 'measurement') {
      if (!['XR', 'XS', 'IMR', 'MEDIAN'].includes(selectedChartType.value)) {
        selectedChartType.value = 'XR'
      }
      const measureRes = await getMeasurementData(lineId)
      const data = measureRes as MeasurementData[]
      
      if (data.length > 0) {
        const allValues: number[] = []
        data.forEach(d => {
          if (d.measurement_values) {
            allValues.push(...d.measurement_values)
          }
        })
        rawData.value = allValues
        calculateMeasurementControlChart(data)
      }
    } else {
      if (!['U', 'P', 'NP', 'C'].includes(selectedChartType.value)) {
        selectedChartType.value = 'P'
      }
      const attrRes = await getAttributeData(lineId)
      const data = attrRes as AttributeData[]
      
      if (data.length > 0) {
        rawData.value = data.map(d => d.defect_count)
        calculateAttributeControlChart(data)
      }
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const calculateMeasurementControlChart = async (data: MeasurementData[]) => {
  if (selectedChartType.value === 'IMR') {
    try {
      const response = await fetch(
        `http://localhost:5000/api/production-lines/${lineId}/control-chart/IMR`,
        {
          headers: { 'Content-Type': 'application/json' }
        }
      )
      
      if (!response.ok) {
        console.error('API请求失败:', response.status)
        return
      }
      
      const result = await response.json()
      processIMRChartData(result)
    } catch (error) {
      console.error('获取控制图数据失败:', error)
    }
    return
  }
  
  const n = subgroupSize.value
  
  try {
    const response = await fetch(
      `http://localhost:5000/api/production-lines/${lineId}/control-chart/${selectedChartType.value}?subgroup_size=${n}`,
      {
        headers: { 'Content-Type': 'application/json' }
      }
    )
    
    if (!response.ok) {
      console.error('API请求失败:', response.status)
      return
    }
    
    const result = await response.json()
    
    if (result.xbar_chart && result.r_chart) {
      const xbarData = result.xbar_chart
      const rData = result.r_chart
      
      const xbarPoints = xbarData.data_points.map((v: number, i: number) => ({
        x: i + 1,
        y: v,
        abnormal: (xbarData.abnormal_points || []).includes(i + 1)
      }))
      
      const rPoints = rData.data_points.map((v: number, i: number) => ({
        x: i + 1,
        y: v,
        abnormal: (rData.abnormal_points || []).includes(i + 1)
      }))
      
      chartData.value = {
        ucl: xbarData.ucl,
        cl: xbarData.center_line,
        lcl: xbarData.lcl,
        center: xbarData.center_line,
        dataPoints: xbarPoints
      }
      
      variationChartData.value = {
        ucl: rData.ucl,
        cl: rData.center_line,
        lcl: rData.lcl,
        center: rData.center_line,
        dataPoints: rPoints
      }
      
      abnormalPoints.value = xbarPoints.filter((p: any) => p.abnormal).length + 
                            rPoints.filter((p: any) => p.abnormal).length
      
      const allAbnormalities: any[] = []
      if (xbarData.abnormal_points && xbarData.abnormal_points.length > 0) {
        xbarData.abnormal_points.forEach((idx: number) => {
          allAbnormalities.push({
            rule: 'X图 - 超出控制限',
            description: `第${idx}点超出X图控制限`
          })
        })
      }
      if (rData.abnormal_points && rData.abnormal_points.length > 0) {
        rData.abnormal_points.forEach((idx: number) => {
          allAbnormalities.push({
            rule: 'R图 - 超出控制限',
            description: `第${idx}点超出R图控制限`
          })
        })
      }
      alarms.value = allAbnormalities
      
      await nextTick()
      drawDualCharts()
    } else if (result.median_chart && result.r_chart) {
      const medianData = result.median_chart
      const rData = result.r_chart
      
      const medianPoints = medianData.data_points.map((v: number, i: number) => ({
        x: i + 1,
        y: v,
        abnormal: (medianData.abnormal_points || []).includes(i + 1)
      }))
      
      const rPoints = rData.data_points.map((v: number, i: number) => ({
        x: i + 1,
        y: v,
        abnormal: (rData.abnormal_points || []).includes(i + 1)
      }))
      
      chartData.value = {
        ucl: medianData.ucl,
        cl: medianData.center_line,
        lcl: medianData.lcl,
        center: medianData.center_line,
        dataPoints: medianPoints
      }
      
      variationChartData.value = {
        ucl: rData.ucl,
        cl: rData.center_line,
        lcl: rData.lcl,
        center: rData.center_line,
        dataPoints: rPoints
      }
      
      abnormalPoints.value = medianPoints.filter((p: any) => p.abnormal).length + 
                            rPoints.filter((p: any) => p.abnormal).length
      
      const allAbnormalities: any[] = []
      if (medianData.abnormal_points && medianData.abnormal_points.length > 0) {
        medianData.abnormal_points.forEach((idx: number) => {
          allAbnormalities.push({
            rule: '中位数图 - 超出控制限',
            description: `第${idx}点超出中位数图控制限`
          })
        })
      }
      if (rData.abnormal_points && rData.abnormal_points.length > 0) {
        rData.abnormal_points.forEach((idx: number) => {
          allAbnormalities.push({
            rule: 'R图 - 超出控制限',
            description: `第${idx}点超出R图控制限`
          })
        })
      }
      alarms.value = allAbnormalities
      
      await nextTick()
      drawDualCharts()
    }
  } catch (error) {
    console.error('获取控制图数据失败:', error)
  }
}

const processIMRChartData = (result: any) => {
  if (result.x_chart && result.mr_chart) {
    const xData = result.x_chart
    const mrData = result.mr_chart
    
    const xPoints = xData.data_points.map((v: number, i: number) => ({
      x: i + 1,
      y: v,
      abnormal: (xData.abnormal_points || []).includes(i + 1)
    }))
    
    const mrPoints = mrData.data_points.map((v: number, i: number) => ({
      x: i + 1,
      y: v,
      abnormal: (mrData.abnormal_points || []).includes(i + 1)
    }))
    
    chartData.value = {
      ucl: xData.ucl,
      cl: xData.center_line,
      lcl: xData.lcl,
      center: xData.center_line,
      dataPoints: xPoints
    }
    
    variationChartData.value = {
      ucl: mrData.ucl,
      cl: mrData.center_line,
      lcl: mrData.lcl,
      center: mrData.center_line,
      dataPoints: mrPoints
    }
    
    abnormalPoints.value = xPoints.filter((p: any) => p.abnormal).length + 
                          mrPoints.filter((p: any) => p.abnormal).length
    
    const allAbnormalities: any[] = []
    if (xData.abnormal_points && xData.abnormal_points.length > 0) {
      xData.abnormal_points.forEach((idx: number) => {
        allAbnormalities.push({
          rule: 'I图 - 超出控制限',
          description: `第${idx}点超出I图控制限`
        })
      })
    }
    if (mrData.abnormal_points && mrData.abnormal_points.length > 0) {
      mrData.abnormal_points.forEach((idx: number) => {
        allAbnormalities.push({
          rule: 'MR图 - 超出控制限',
          description: `第${idx}点超出MR图控制限`
        })
      })
    }
    alarms.value = allAbnormalities
    
    nextTick(() => drawDualCharts())
  }
}

const fallbackCalculate = (recentGroups: number[][]) => {
  const xBars = recentGroups.map(g => g.reduce((a, b) => a + b, 0) / g.length)
  const ranges = recentGroups.map(g => Math.max(...g) - Math.min(...g))
  
  const xBar = xBars.reduce((a, b) => a + b, 0) / xBars.length
  const rBar = ranges.reduce((a, b) => a + b, 0) / ranges.length
  
  const n = 5
  const A2 = 0.577
  const D3 = 0
  const D4 = 2.114
  
  const xbarUcl = xBar + A2 * rBar
  const xbarLcl = Math.max(0, xBar - A2 * rBar)
  const xbarCl = xBar
  
  const rUcl = D4 * rBar
  const rLcl = D3 * rBar
  const rCl = rBar
  
  const xbarAbnormalities = detectAbnormalities(xBars, xbarCl, xbarUcl, xbarLcl)
  const rAbnormalities = detectAbnormalities(ranges, rCl, rUcl, rLcl)
  
  const xbarAbnormalSet = new Set<number>()
  xbarAbnormalities.forEach(a => a.points.forEach(p => xbarAbnormalSet.add(p)))
  
  const rAbnormalSet = new Set<number>()
  rAbnormalities.forEach(a => a.points.forEach(p => rAbnormalSet.add(p)))
  
  chartData.value = {
    ucl: xbarUcl,
    cl: xbarCl,
    lcl: xbarLcl,
    center: xbarCl,
    dataPoints: xBars.map((v, i) => ({
      x: i + 1,
      y: v,
      abnormal: xbarAbnormalSet.has(i + 1)
    }))
  }
  
  variationChartData.value = {
    ucl: rUcl,
    cl: rCl,
    lcl: rLcl,
    center: rCl,
    dataPoints: ranges.map((v, i) => ({
      x: i + 1,
      y: v,
      abnormal: rAbnormalSet.has(i + 1)
    }))
  }
  
  abnormalPoints.value = xbarAbnormalSet.size + rAbnormalSet.size
  alarms.value = [...xbarAbnormalities, ...rAbnormalities]
  
  nextTick(() => drawDualCharts())
}

const calculateControlChart = (data: AttributeData[]) => {
  const groupSize = 5
  const maxGroups = 25
  
  const groups: { defects: number; samples: number }[] = []
  for (let i = 0; i < data.length; i += groupSize) {
    const groupData = data.slice(i, i + groupSize)
    const totalDefects = groupData.reduce((sum, d) => sum + d.defect_count, 0)
    const totalSamples = groupData.reduce((sum, d) => sum + d.sample_size, 0)
    groups.push({ defects: totalDefects, samples: totalSamples })
  }
  
  const recentGroups = groups.slice(-maxGroups)
  if (recentGroups.length === 0) return
  
  const uValues = recentGroups.map(g => g.samples > 0 ? g.defects / g.samples : 0)
  const totalDefects = recentGroups.reduce((sum, g) => sum + g.defects, 0)
  const totalSamples = recentGroups.reduce((sum, g) => sum + g.samples, 0)
  const uBar = totalSamples > 0 ? totalDefects / totalSamples : 0
  
  let ucl: number, cl: number, lcl: number
  
  if (selectedChartType.value === 'U') {
    cl = uBar
    ucl = cl + 3 * Math.sqrt(cl)
    lcl = Math.max(0, cl - 3 * Math.sqrt(cl))
  } else {
    cl = uBar
    ucl = cl + 3 * Math.sqrt(cl)
    lcl = Math.max(0, cl - 3 * Math.sqrt(cl))
  }
  
  const detectedAbnormalities = detectAbnormalities(uValues, cl, ucl, lcl)
  const abnormalPointSet = new Set<number>()
  detectedAbnormalities.forEach(a => a.points.forEach(p => abnormalPointSet.add(p)))
  
  const dataPoints = uValues.map((v, i) => ({
    x: i + 1,
    y: v,
    abnormal: abnormalPointSet.has(i + 1)
  }))
  
  abnormalPoints.value = dataPoints.filter(p => p.abnormal).length
  alarms.value = detectedAbnormalities.map(a => ({
    rule: a.rule,
    description: a.description
  }))
  
  chartData.value = { ucl, cl, lcl, center: cl, dataPoints }
}

const drawHistogram = () => {
  if (!histogramCanvas.value || rawData.value.length === 0) return
  
  const canvas = histogramCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  
  if (rect.width === 0 || rect.height === 0) return
  
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  ctx.scale(dpr, dpr)
  
  const width = rect.width
  const height = rect.height
  const padding = { top: 30, right: 30, bottom: 50, left: 50 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  
  ctx.fillStyle = '#0a0e17'
  ctx.fillRect(0, 0, width, height)
  
  const data = rawData.value
  const min = Math.min(...data)
  const max = Math.max(...data)
  const range = max - min || 1
  const bins = Number(histogramBins.value)
  const binWidth = range / bins
  
  const histogram: number[] = new Array(bins).fill(0)
  data.forEach(v => {
    let binIndex = Math.floor((v - min) / binWidth)
    if (binIndex >= bins) binIndex = bins - 1
    if (binIndex < 0) binIndex = 0
    histogram[binIndex]++
  })
  
  const maxFreq = Math.max(...histogram)
  const mean = meanValue.value
  const std = stdValue.value
  
  const scaleX = (x: number) => padding.left + (x / bins) * chartWidth
  const scaleY = (y: number) => padding.top + chartHeight - (y / maxFreq) * chartHeight
  
  ctx.strokeStyle = '#1e293b'
  ctx.lineWidth = 1
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (i / 5) * chartHeight
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(width - padding.right, y)
    ctx.stroke()
  }
  
  const gradient = ctx.createLinearGradient(0, padding.top, 0, padding.top + chartHeight)
  gradient.addColorStop(0, 'rgba(0, 212, 255, 0.8)')
  gradient.addColorStop(1, 'rgba(0, 212, 255, 0.2)')
  
  histogram.forEach((freq, i) => {
    const x = scaleX(i)
    const barWidth = chartWidth / bins - 2
    const barHeight = (freq / maxFreq) * chartHeight
    
    ctx.fillStyle = gradient
    ctx.fillRect(x + 1, padding.top + chartHeight - barHeight, barWidth, barHeight)
    
    ctx.strokeStyle = '#00d4ff'
    ctx.lineWidth = 1
    ctx.strokeRect(x + 1, padding.top + chartHeight - barHeight, barWidth, barHeight)
  })
  
  if (std > 0) {
    const normalY = (x: number) => {
      const normalDensity = (1 / (std * Math.sqrt(2 * Math.PI))) * 
        Math.exp(-0.5 * Math.pow((x - mean) / std, 2))
      const scaledDensity = normalDensity * data.length * binWidth
      return scaledDensity / maxFreq * chartHeight
    }
    
    ctx.strokeStyle = '#f59e0b'
    ctx.lineWidth = 2
    ctx.beginPath()
    
    for (let i = 0; i <= 100; i++) {
      const x = min + (i / 100) * range
      const normalHeight = normalY(x)
      const canvasX = padding.left + ((x - min) / range) * chartWidth
      const canvasY = padding.top + chartHeight - normalHeight
      
      if (i === 0) {
        ctx.moveTo(canvasX, canvasY)
      } else {
        ctx.lineTo(canvasX, canvasY)
      }
    }
    ctx.stroke()
  }
  
  ctx.fillStyle = '#64748b'
  ctx.font = '11px "JetBrains Mono", monospace'
  ctx.textAlign = 'center'
  
  for (let i = 0; i <= bins; i += Math.ceil(bins / 5)) {
    const x = scaleX(i)
    const value = min + i * binWidth
    ctx.fillText(value.toFixed(1), x, height - padding.bottom + 20)
  }
  
  ctx.textAlign = 'right'
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (i / 5) * chartHeight
    const value = maxFreq * (1 - i / 5)
    ctx.fillText(value.toFixed(0), padding.left - 10, y + 4)
  }
  
  ctx.fillStyle = '#94a3b8'
  ctx.font = '12px "Orbitron", sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText('数据值', width / 2, height - 10)
  
  ctx.save()
  ctx.translate(15, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('频数', 0, 0)
  ctx.restore()
}

const drawChart = () => {
  if (!chartCanvas.value) return
  
  const canvas = chartCanvas.value
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  
  if (rect.width === 0 || rect.height === 0) return
  
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  ctx.scale(dpr, dpr)
  
  const width = rect.width
  const height = rect.height
  const padding = { top: 40, right: 40, bottom: 60, left: 60 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  
  ctx.fillStyle = '#0a0e17'
  ctx.fillRect(0, 0, width, height)
  
  const dataPoints = chartData.value.dataPoints || []
  if (dataPoints.length === 0) return
  
  const ucl = chartData.value.ucl || 0
  const lcl = chartData.value.lcl || 0
  const cl = chartData.value.cl || 0
  
  const dataMax = Math.max(...dataPoints.map(p => p.y))
  const dataMin = Math.min(...dataPoints.map(p => p.y))
  
  const allYValues = [...dataPoints.map(p => p.y), ucl, lcl, cl]
  const rawMin = Math.min(...allYValues)
  const rawMax = Math.max(...allYValues)
  const range = rawMax - rawMin || 1
  const margin = range * 0.15
  
  const minY = rawMin - margin
  const maxY = rawMax + margin
  const maxX = dataPoints.length
  
  const sigma = (ucl - cl) / 3
  const sigma1Upper = cl + sigma
  const sigma1Lower = cl - sigma
  const sigma2Upper = cl + 2 * sigma
  const sigma2Lower = cl - 2 * sigma
  
  const scaleX = (x: number) => padding.left + (x / maxX) * chartWidth
  const scaleY = (y: number) => padding.top + chartHeight - ((y - minY) / (maxY - minY)) * chartHeight
  
  ctx.strokeStyle = '#1e293b'
  ctx.lineWidth = 1
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (i / 5) * chartHeight
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(width - padding.right, y)
    ctx.stroke()
  }
  
  ctx.setLineDash([3, 3])
  ctx.lineWidth = 1
  
  const sigma2UpperY = scaleY(sigma2Upper)
  ctx.strokeStyle = '#f59e0b'
  ctx.beginPath()
  ctx.moveTo(padding.left, sigma2UpperY)
  ctx.lineTo(width - padding.right, sigma2UpperY)
  ctx.stroke()
  
  const sigma2LowerY = scaleY(sigma2Lower)
  ctx.beginPath()
  ctx.moveTo(padding.left, sigma2LowerY)
  ctx.lineTo(width - padding.right, sigma2LowerY)
  ctx.stroke()
  
  const sigma1UpperY = scaleY(sigma1Upper)
  ctx.strokeStyle = '#3b82f6'
  ctx.beginPath()
  ctx.moveTo(padding.left, sigma1UpperY)
  ctx.lineTo(width - padding.right, sigma1UpperY)
  ctx.stroke()
  
  const sigma1LowerY = scaleY(sigma1Lower)
  ctx.beginPath()
  ctx.moveTo(padding.left, sigma1LowerY)
  ctx.lineTo(width - padding.right, sigma1LowerY)
  ctx.stroke()
  
  ctx.setLineDash([5, 5])
  ctx.lineWidth = 2
  
  const uclY = scaleY(ucl)
  ctx.strokeStyle = '#ef4444'
  ctx.beginPath()
  ctx.moveTo(padding.left, uclY)
  ctx.lineTo(width - padding.right, uclY)
  ctx.stroke()
  
  const clY = scaleY(cl)
  ctx.strokeStyle = '#22c55e'
  ctx.beginPath()
  ctx.moveTo(padding.left, clY)
  ctx.lineTo(width - padding.right, clY)
  ctx.stroke()
  
  const lclY = scaleY(lcl)
  ctx.strokeStyle = '#ef4444'
  ctx.beginPath()
  ctx.moveTo(padding.left, lclY)
  ctx.lineTo(width - padding.right, lclY)
  ctx.stroke()
  
  ctx.setLineDash([])
  
  ctx.strokeStyle = '#00d4ff'
  ctx.lineWidth = 2
  ctx.beginPath()
  dataPoints.forEach((p, i) => {
    const x = scaleX(p.x)
    const y = scaleY(p.y)
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
  
  dataPoints.forEach((p) => {
    const x = scaleX(p.x)
    const y = scaleY(p.y)
    
    ctx.beginPath()
    if (p.abnormal) {
      ctx.fillStyle = '#ef4444'
      ctx.arc(x, y, 6, 0, Math.PI * 2)
      ctx.fill()
    } else {
      ctx.fillStyle = '#00d4ff'
      ctx.arc(x, y, 4, 0, Math.PI * 2)
      ctx.fill()
    }
  })
  
  ctx.fillStyle = '#64748b'
  ctx.font = '12px "JetBrains Mono", monospace'
  ctx.textAlign = 'center'
  
  for (let i = 0; i <= maxX; i += Math.ceil(maxX / 10)) {
    const x = scaleX(i)
    ctx.fillText(i.toString(), x, height - padding.bottom + 20)
  }
  
  ctx.textAlign = 'right'
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (i / 5) * chartHeight
    const value = maxY - (i / 5) * (maxY - minY)
    ctx.fillText(value.toFixed(1), padding.left - 10, y + 4)
  }
  
  ctx.fillStyle = '#ef4444'
  ctx.textAlign = 'left'
  ctx.font = 'bold 12px "JetBrains Mono", monospace'
  ctx.fillText(`UCL = ${ucl.toFixed(3)}`, padding.left + 10, uclY - 8)
  ctx.fillText(`LCL = ${lcl.toFixed(3)}`, padding.left + 10, lclY + 16)
  ctx.fillStyle = '#22c55e'
  ctx.fillText(`CL = ${cl.toFixed(3)}`, padding.left + 10, clY - 8)
}

const fetchChartData = () => {
  fetchData()
}

const drawDualCharts = () => {
  if (!xbarCanvas.value || !variationCanvas.value) return
  
  drawSingleChart(xbarCanvas.value, chartData.value, getXBarChartTitle())
  drawSingleChart(variationCanvas.value, variationChartData.value, getVariationChartTitle())
}

const drawSingleChart = (canvas: HTMLCanvasElement, data: ChartData, title: string) => {
  if (!canvas || !data.dataPoints || data.dataPoints.length === 0) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const dpr = window.devicePixelRatio || 1
  const rect = canvas.getBoundingClientRect()
  
  if (rect.width === 0 || rect.height === 0) return
  
  canvas.width = rect.width * dpr
  canvas.height = rect.height * dpr
  ctx.scale(dpr, dpr)
  
  const width = rect.width
  const height = rect.height
  const padding = { top: 50, right: 40, bottom: 60, left: 70 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom
  
  ctx.fillStyle = '#0a0e17'
  ctx.fillRect(0, 0, width, height)
  
  ctx.fillStyle = '#f8fafc'
  ctx.font = 'bold 14px "Orbitron", sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(title, width / 2, 25)
  
  const dataPoints = data.dataPoints
  const ucl = data.ucl || 0
  const lcl = data.lcl || 0
  const cl = data.cl || data.center || 0
  
  const allYValues = [...dataPoints.map(p => p.y), ucl, lcl, cl]
  const rawMin = Math.min(...allYValues)
  const rawMax = Math.max(...allYValues)
  const range = rawMax - rawMin || 1
  const margin = range * 0.15
  
  const minY = rawMin - margin
  const maxY = rawMax + margin
  
  const xScale = (x: number) => padding.left + (x / dataPoints.length) * chartWidth
  const yScale = (y: number) => padding.top + chartHeight - ((y - minY) / (maxY - minY)) * chartHeight
  
  ctx.strokeStyle = '#1e293b'
  ctx.lineWidth = 1
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (i / 5) * chartHeight
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(width - padding.right, y)
    ctx.stroke()
    
    const value = maxY - (i / 5) * (maxY - minY)
    ctx.fillStyle = '#64748b'
    ctx.font = '11px "JetBrains Mono", monospace'
    ctx.textAlign = 'right'
    ctx.fillText(value.toFixed(3), padding.left - 8, y + 4)
  }
  
  for (let i = 0; i < dataPoints.length; i++) {
    const x = xScale(i + 0.5)
    ctx.strokeStyle = '#1e293b'
    ctx.beginPath()
    ctx.moveTo(x, padding.top)
    ctx.lineTo(x, padding.top + chartHeight)
    ctx.stroke()
    
    if ((i + 1) % 5 === 0 || i === 0) {
      ctx.fillStyle = '#64748b'
      ctx.font = '11px "JetBrains Mono", monospace'
      ctx.textAlign = 'center'
      ctx.fillText(String(i + 1), x, padding.top + chartHeight + 20)
    }
  }
  
  const uclY = yScale(ucl)
  const lclY = yScale(lcl)
  const clY = yScale(cl)
  
  ctx.strokeStyle = '#ef4444'
  ctx.lineWidth = 2
  ctx.setLineDash([8, 4])
  ctx.beginPath()
  ctx.moveTo(padding.left, uclY)
  ctx.lineTo(width - padding.right, uclY)
  ctx.stroke()
  ctx.beginPath()
  ctx.moveTo(padding.left, lclY)
  ctx.lineTo(width - padding.right, lclY)
  ctx.stroke()
  
  ctx.strokeStyle = '#22c55e'
  ctx.setLineDash([])
  ctx.beginPath()
  ctx.moveTo(padding.left, clY)
  ctx.lineTo(width - padding.right, clY)
  ctx.stroke()
  
  ctx.fillStyle = '#ef4444'
  ctx.font = 'bold 11px "JetBrains Mono", monospace'
  ctx.textAlign = 'left'
  ctx.fillText(`UCL = ${ucl.toFixed(3)}`, padding.left + 10, uclY - 8)
  ctx.fillText(`LCL = ${lcl.toFixed(3)}`, padding.left + 10, lclY + 16)
  ctx.fillStyle = '#22c55e'
  ctx.fillText(`CL = ${cl.toFixed(3)}`, padding.left + 10, clY - 8)
  
  ctx.strokeStyle = '#0ea5e9'
  ctx.lineWidth = 2
  ctx.beginPath()
  dataPoints.forEach((point, i) => {
    const x = xScale(i + 0.5)
    const y = yScale(point.y)
    if (i === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  ctx.stroke()
  
  dataPoints.forEach((point, i) => {
    const x = xScale(i + 0.5)
    const y = yScale(point.y)
    
    ctx.beginPath()
    ctx.arc(x, y, 5, 0, Math.PI * 2)
    
    if (point.abnormal) {
      ctx.fillStyle = '#ef4444'
      ctx.fill()
      ctx.strokeStyle = '#ef4444'
      ctx.lineWidth = 2
      ctx.beginPath()
      ctx.arc(x, y, 10, 0, Math.PI * 2)
      ctx.stroke()
    } else {
      ctx.fillStyle = '#0ea5e9'
      ctx.fill()
    }
  })
  
  ctx.fillStyle = '#64748b'
  ctx.font = '12px "JetBrains Mono", monospace'
  ctx.textAlign = 'center'
  ctx.fillText('子组编号', width / 2, height - 15)
  
  ctx.save()
  ctx.translate(15, height / 2)
  ctx.rotate(-Math.PI / 2)
  ctx.fillText('测量值', 0, 0)
  ctx.restore()
}

const goBack = () => {
  router.push(`/production-lines/${lineId}`)
}

onMounted(() => {
  fetchData()
  
  window.addEventListener('resize', () => {
    drawChart()
    if (line.value?.data_type === 'measurement') {
      drawHistogram()
    }
  })
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
  font-family: 'Orbitron', sans-serif;
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.page-subtitle {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  color: var(--accent-primary);
}

.chart-type-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chart-type-selector label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.chart-type-selector select {
  padding: 10px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.875rem;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 24px;
}

.subgroup-selector {
  display: flex;
  align-items: center;
  gap: 12px;
}

.subgroup-selector label {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.subgroup-selector select {
  padding: 10px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: 'Orbitron', sans-serif;
  font-size: 0.875rem;
  min-width: 80px;
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

.stat-icon.warning {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger);
}

.stat-icon.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.analysis-section {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 24px;
  margin-bottom: 32px;
}

.histogram-panel,
.normality-panel {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.panel-title svg {
  color: var(--accent-primary);
}

.histogram-controls {
  display: flex;
  align-items: center;
  gap: 8px;
}

.histogram-controls label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.histogram-controls select {
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.75rem;
}

.histogram-container {
  width: 100%;
  height: 350px;
  margin-bottom: 16px;
  flex: 1;
}

.histogram-container canvas {
  display: block;
  width: 100% !important;
  height: 100% !important;
}

.histogram-stats {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
  flex-shrink: 0;
}

.h-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.h-stat-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.h-stat-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  color: var(--accent-primary);
  font-weight: 600;
}

.normality-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.test-result {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
}

.test-result.normal {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.test-result.not-normal {
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.result-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.test-result.normal .result-icon {
  color: var(--success);
}

.test-result.not-normal .result-icon {
  color: var(--danger);
}

.result-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.result-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1.125rem;
  font-weight: 700;
}

.test-result.normal .result-title {
  color: var(--success);
}

.test-result.not-normal .result-title {
  color: var(--danger);
}

.result-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.test-details {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.detail-label {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.detail-value {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  color: var(--text-primary);
  font-weight: 600;
}

.detail-value.p-significant {
  color: var(--danger);
}

.detail-value.explanation {
  font-family: inherit;
  font-size: 0.75rem;
  color: var(--text-secondary);
  max-width: 200px;
  text-align: right;
}

.test-interpretation {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border-left: 3px solid var(--accent-primary);
}

.interpretation-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-family: 'Orbitron', sans-serif;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.interpretation-header svg {
  color: var(--accent-primary);
}

.interpretation-text {
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
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
  font-family: 'Orbitron', sans-serif;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
}

.chart-legend {
  display: flex;
  gap: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.legend-color {
  width: 20px;
  height: 3px;
  border-radius: 2px;
}

.legend-color.data-line {
  background: #00d4ff;
}

.legend-color.ucl-line,
.legend-color.lcl-line {
  background: #ef4444;
}

.legend-color.sigma2-line {
  background: #f59e0b;
}

.legend-color.sigma1-line {
  background: #3b82f6;
}

.legend-color.cl-line {
  background: #22c55e;
}

.chart-container {
  width: 100%;
  height: 400px;
}

.chart-container.single-chart {
  height: 400px;
}

.chart-container canvas {
  width: 100%;
  height: 100%;
}

.dual-chart-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 16px;
}

.chart-panel {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  overflow: hidden;
}

.panel-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  padding: 16px 20px;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), transparent);
  border-bottom: 1px solid var(--border-color);
  margin: 0;
}

.chart-wrapper {
  height: 350px;
  padding: 16px;
}

.chart-wrapper canvas {
  width: 100%;
  height: 100%;
}

@media (max-width: 1200px) {
  .dual-chart-container {
    grid-template-columns: 1fr;
  }
}

.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 400px;
  color: var(--text-muted);
}

.chart-empty svg {
  margin-bottom: 16px;
  opacity: 0.3;
}

.chart-empty .hint {
  font-size: 0.875rem;
  margin-top: 8px;
}

.alarm-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.section-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.alarm-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alarm-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-md);
}

.alarm-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(239, 68, 68, 0.2);
  border-radius: var(--radius-sm);
  color: var(--danger);
}

.alarm-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alarm-title {
  font-family: 'Orbitron', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--danger);
}

.alarm-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .analysis-section {
    grid-template-columns: 1fr;
  }
  
  .histogram-stats {
    grid-template-columns: repeat(3, 1fr);
  }
}
</style>
