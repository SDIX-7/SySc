<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content" v-if="study">
      <div class="page-header">
        <div class="header-left">
          <button class="btn-back" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">{{ study.study_name }}</h1>
            <p class="page-subtitle">{{ study.measurement_system || 'MSA研究详情' }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="action-buttons">
            <button class="btn-export" @click="exportReport" v-if="study.result">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              导出报告
            </button>
            <button class="btn-calculate" @click="handleCalculate" v-if="study.status !== 'completed'">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="4" y="2" width="16" height="20" rx="2"/>
                <line x1="8" y1="6" x2="16" y2="6"/>
                <line x1="8" y1="10" x2="16" y2="10"/>
                <line x1="8" y1="14" x2="12" y2="14"/>
              </svg>
              计算GR&R
            </button>
            <button class="btn-edit" @click="handleEdit">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              编辑
            </button>
            <span class="status-badge" :class="study.status">{{ getStatusLabel(study.status) }}</span>
          </div>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="info-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="16" x2="12" y2="12"/>
                <line x1="12" y1="8" x2="12.01" y2="8"/>
              </svg>
            </span>
            研究信息
          </h2>
          
          <div class="info-grid">
            <div class="info-item">
              <span class="info-label">研究类型</span>
              <span class="info-value">
                <span class="type-tag" :class="study.study_type">{{ getStudyTypeLabel(study.study_type) }}</span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">测量特性</span>
              <span class="info-value">{{ study.characteristic || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">测量系统</span>
              <span class="info-value">{{ study.measurement_system || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">研究设计</span>
              <span class="info-value design">{{ study.number_of_parts }}件 × {{ study.number_of_operators }}人 × {{ study.number_of_replicates }}次</span>
            </div>
            <div class="info-item">
              <span class="info-label">规格上限</span>
              <span class="info-value">{{ study.specification_upper || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">规格下限</span>
              <span class="info-value">{{ study.specification_lower || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">目标值</span>
              <span class="info-value">{{ study.specification_target || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">公差</span>
              <span class="info-value">{{ study.tolerance || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatDate(study.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="result-section" v-if="study.result">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </span>
            GR&R分析结果
          </h2>
          
          <div class="result-cards">
            <div class="result-card main" :class="getGRRClass(parseFloat(study.result.percent_grr || '0'))">
              <div class="result-header">
                <span class="result-name">%GR&R</span>
                <span class="result-status">{{ getGRRAcceptance(study.result.grr_acceptance) }}</span>
              </div>
              <div class="result-value">{{ parseFloat(study.result.percent_grr || '0').toFixed(2) }}%</div>
              <div class="result-bar">
                <div class="bar-fill" :style="{ width: Math.min(parseFloat(study.result.percent_grr || '0'), 100) + '%' }"></div>
              </div>
              <div class="result-scale">
                <span class="scale-item good">&lt;10%</span>
                <span class="scale-item warning">10-30%</span>
                <span class="scale-item danger">&gt;30%</span>
              </div>
            </div>
            
            <div class="result-card" :class="parseFloat(study.result.ndc || '0') >= 5 ? 'good' : 'warning'">
              <div class="result-header">
                <span class="result-name">NDC</span>
                <span class="result-status">{{ getNDCAcceptance(study.result.ndc_acceptance) }}</span>
              </div>
              <div class="result-value">{{ parseFloat(study.result.ndc || '0').toFixed(1) }}</div>
              <div class="result-desc">可分辨类别数</div>
              <div class="result-hint">≥5 为可接受</div>
            </div>
            
            <div class="result-card">
              <div class="result-header">
                <span class="result-name">%P/T</span>
                <span class="result-status">公差百分比</span>
              </div>
              <div class="result-value">{{ parseFloat(study.result.percent_tolerance || '0').toFixed(2) }}%</div>
              <div class="result-desc">精度/公差比</div>
            </div>
            
            <div class="result-card overall" :class="study.result.overall_acceptance">
              <div class="result-header">
                <span class="result-name">综合判定</span>
              </div>
              <div class="result-value">{{ getAcceptanceLabel(study.result.overall_acceptance) }}</div>
              <div class="result-icon">
                <svg v-if="study.result.overall_acceptance === 'acceptable'" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                  <polyline points="22 4 12 14.01 9 11.01"/>
                </svg>
                <svg v-else-if="study.result.overall_acceptance === 'conditional'" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
                <svg v-else width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="15" y1="9" x2="9" y2="15"/>
                  <line x1="9" y1="9" x2="15" y2="15"/>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <div class="variance-section" v-if="study.result">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>
                <path d="M22 12A10 10 0 0 0 12 2v10z"/>
              </svg>
            </span>
            方差分量
          </h2>
          
          <div class="variance-content">
            <div class="variance-chart" ref="varianceChart"></div>
            <div class="variance-table">
              <div class="variance-row header">
                <span class="col">来源</span>
                <span class="col">方差</span>
                <span class="col">标准差</span>
                <span class="col">贡献%</span>
              </div>
              <div class="variance-row">
                <span class="col">重复性</span>
                <span class="col mono">{{ parseFloat(study.result.variance_repeatability || '0').toFixed(6) }}</span>
                <span class="col mono">{{ parseFloat(study.result.stddev_repeatability || '0').toFixed(4) }}</span>
                <span class="col mono">{{ getVariancePercent('repeatability') }}%</span>
              </div>
              <div class="variance-row">
                <span class="col">再现性</span>
                <span class="col mono">{{ parseFloat(study.result.variance_reproducibility || '0').toFixed(6) }}</span>
                <span class="col mono">{{ parseFloat(study.result.stddev_reproducibility || '0').toFixed(4) }}</span>
                <span class="col mono">{{ getVariancePercent('reproducibility') }}%</span>
              </div>
              <div class="variance-row grr">
                <span class="col">GR&R</span>
                <span class="col mono">{{ parseFloat(study.result.variance_grr || '0').toFixed(6) }}</span>
                <span class="col mono">{{ parseFloat(study.result.stddev_grr || '0').toFixed(4) }}</span>
                <span class="col mono">{{ getVariancePercent('grr') }}%</span>
              </div>
              <div class="variance-row">
                <span class="col">零件</span>
                <span class="col mono">{{ parseFloat(study.result.variance_part || '0').toFixed(6) }}</span>
                <span class="col mono">{{ parseFloat(study.result.stddev_part || '0').toFixed(4) }}</span>
                <span class="col mono">{{ getVariancePercent('part') }}%</span>
              </div>
              <div class="variance-row total">
                <span class="col">总变异</span>
                <span class="col mono">{{ parseFloat(study.result.variance_total || '0').toFixed(6) }}</span>
                <span class="col mono">{{ parseFloat(study.result.stddev_total || '0').toFixed(4) }}</span>
                <span class="col mono">100%</span>
              </div>
            </div>
          </div>
        </div>

        <div class="measurement-section">
          <h2 class="section-title">
            <span class="section-icon">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <line x1="3" y1="9" x2="21" y2="9"/>
                <line x1="9" y1="21" x2="9" y2="9"/>
              </svg>
            </span>
            测量数据
          </h2>
          
          <div class="measurement-table-wrapper">
            <table class="measurement-table">
              <thead>
                <tr>
                  <th rowspan="2" class="part-col">零件</th>
                  <th v-for="op in operators" :key="op.id" :colspan="study.number_of_replicates" class="operator-col">
                    {{ op.operator_name }}
                  </th>
                </tr>
                <tr>
                  <template v-for="op in operators" :key="'sub-' + op.id">
                    <th v-for="r in study.number_of_replicates" :key="op.id + '-' + r" class="replicate-col">
                      #{{ r }}
                    </th>
                  </template>
                </tr>
              </thead>
              <tbody>
                <tr v-for="part in parts" :key="part.id">
                  <td class="part-cell">
                    <span class="part-name">{{ part.part_number }}</span>
                    <span class="part-ref" v-if="part.reference_value">({{ part.reference_value }})</span>
                  </td>
                  <template v-for="op in operators" :key="part.id + '-' + op.id">
                    <td v-for="r in study.number_of_replicates" :key="part.id + '-' + op.id + '-' + r" class="measurement-cell">
                      {{ getMeasurementValue(part.id!, op.id!, r) }}
                    </td>
                  </template>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="parts-operators-section">
          <div class="subsection">
            <h3 class="subsection-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="3" width="7" height="7"/>
                <rect x="14" y="3" width="7" height="7"/>
                <rect x="14" y="14" width="7" height="7"/>
                <rect x="3" y="14" width="7" height="7"/>
              </svg>
              零件列表 ({{ parts.length }})
            </h3>
            <div class="list-items">
              <div class="list-item" v-for="part in parts" :key="part.id">
                <span class="item-number">{{ part.part_number }}</span>
                <span class="item-name">{{ part.part_name || '-' }}</span>
                <span class="item-ref" v-if="part.reference_value">参考值: {{ part.reference_value }}</span>
              </div>
            </div>
          </div>
          
          <div class="subsection">
            <h3 class="subsection-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
              操作员列表 ({{ operators.length }})
            </h3>
            <div class="list-items">
              <div class="list-item" v-for="op in operators" :key="op.id">
                <span class="item-number">{{ op.operator_id || '-' }}</span>
                <span class="item-name">{{ op.operator_name }}</span>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import * as echarts from 'echarts'
import Menu from '@/components/Menu.vue'
import { getMSAStudy, calculateMSA, type MSAStudy, type MSAPart, type MSAOperator, type MSAMeasurement } from '@/api/msa'

const route = useRoute()
const router = useRouter()

const studyId = Number(route.params.studyId)
const study = ref<MSAStudy | null>(null)
const parts = ref<MSAPart[]>([])
const operators = ref<MSAOperator[]>([])
const measurements = ref<MSAMeasurement[]>([])
const varianceChart = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

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

const getGRRAcceptance = (acceptance: string) => {
  const map: Record<string, string> = {
    acceptable: '可接受',
    conditional: '条件接受',
    unacceptable: '不可接受'
  }
  return map[acceptance] || '-'
}

const getNDCAcceptance = (acceptance: string) => {
  const map: Record<string, string> = {
    acceptable: '可接受',
    unacceptable: '不可接受'
  }
  return map[acceptance] || '-'
}

const getGRRClass = (grr: number) => {
  if (grr < 10) return 'good'
  if (grr < 30) return 'warning'
  return 'danger'
}

const getVariancePercent = (type: string) => {
  if (!study.value?.result) return '0.00'
  const total = parseFloat(study.value.result.variance_total || '0')
  if (total === 0) return '0.00'
  
  let variance = 0
  switch (type) {
    case 'repeatability':
      variance = parseFloat(study.value.result.variance_repeatability || '0')
      break
    case 'reproducibility':
      variance = parseFloat(study.value.result.variance_reproducibility || '0')
      break
    case 'grr':
      variance = parseFloat(study.value.result.variance_grr || '0')
      break
    case 'part':
      variance = parseFloat(study.value.result.variance_part || '0')
      break
  }
  return ((variance / total) * 100).toFixed(2)
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

const getMeasurementValue = (partId: number, operatorId: number, replicate: number) => {
  const meas = measurements.value.find(m => 
    m.part_id === partId && 
    m.operator_id === operatorId && 
    m.replicate === replicate
  )
  return meas?.measurement_value || '-'
}

const fetchStudy = async () => {
  try {
    const res = await getMSAStudy(studyId)
    study.value = res.data || res
    parts.value = study.value?.parts || []
    operators.value = study.value?.operators || []
    measurements.value = study.value?.measurements || []
    
    await nextTick()
    if (study.value?.result) {
      renderVarianceChart()
    }
  } catch (error) {
    console.error('获取MSA研究失败:', error)
    ElMessage.error('获取MSA研究失败')
  }
}

const renderVarianceChart = () => {
  if (!varianceChart.value || !study.value?.result) return
  
  if (chartInstance) {
    chartInstance.dispose()
  }
  
  chartInstance = echarts.init(varianceChart.value)
  
  const data = [
    { name: '重复性', value: parseFloat(study.value.result.variance_repeatability || '0') },
    { name: '再现性', value: parseFloat(study.value.result.variance_reproducibility || '0') },
    { name: '零件', value: parseFloat(study.value.result.variance_part || '0') }
  ]
  
  const total = data.reduce((sum, item) => sum + item.value, 0)
  
  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      backgroundColor: 'rgba(15, 23, 42, 0.9)',
      borderColor: 'rgba(0, 212, 255, 0.3)',
      textStyle: { color: '#e2e8f0' },
      formatter: (params: any) => {
        const percent = ((params.value / total) * 100).toFixed(2)
        return `${params.name}<br/>方差: ${params.value.toFixed(6)}<br/>占比: ${percent}%`
      }
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center',
      textStyle: { color: '#94a3b8' }
    },
    series: [
      {
        name: '方差分量',
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['35%', '50%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 8,
          borderColor: 'var(--bg-card)',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold',
            color: '#e2e8f0'
          }
        },
        data: [
          { value: data[0].value, name: '重复性', itemStyle: { color: '#00d4ff' } },
          { value: data[1].value, name: '再现性', itemStyle: { color: '#8b5cf6' } },
          { value: data[2].value, name: '零件', itemStyle: { color: '#10b981' } }
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

const handleEdit = () => {
  router.push(`/msa-studies/${studyId}/edit`)
}

const handleCalculate = async () => {
  try {
    await ElMessageBox.confirm('确认执行GR&R计算？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    const res = await calculateMSA(studyId)
    ElMessage.success(res.message || '计算完成')
    fetchStudy()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '计算失败')
    }
  }
}

const exportReport = () => {
  if (!study.value) return
  
  const reportContent = generateReportContent()
  const blob = new Blob([reportContent], { type: 'text/html;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `MSA报告_${study.value.study_name}_${new Date().toISOString().split('T')[0]}.html`
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  ElMessage.success('报告已导出')
}

const generateReportContent = () => {
  if (!study.value) return ''
  
  const s = study.value
  const r = s.result
  
  return `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>MSA报告 - ${s.study_name}</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body { font-family: 'Microsoft YaHei', sans-serif; background: #f8fafc; color: #1e293b; padding: 40px; }
    .report-container { max-width: 900px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); overflow: hidden; }
    .report-header { background: linear-gradient(135deg, #0ea5e9, #0284c7); color: white; padding: 32px; }
    .report-header h1 { font-size: 24px; margin-bottom: 8px; }
    .report-header p { opacity: 0.9; font-size: 14px; }
    .report-body { padding: 32px; }
    .section { margin-bottom: 32px; }
    .section-title { font-size: 18px; font-weight: 600; color: #0f172a; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 2px solid #e2e8f0; }
    .info-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .info-item { display: flex; flex-direction: column; gap: 4px; }
    .info-label { font-size: 12px; color: #64748b; }
    .info-value { font-weight: 600; }
    .result-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
    .result-card { padding: 20px; background: #f8fafc; border-radius: 8px; text-align: center; border: 1px solid #e2e8f0; }
    .result-card.good { border-color: #10b981; background: #ecfdf5; }
    .result-card.warning { border-color: #f59e0b; background: #fffbeb; }
    .result-card.danger { border-color: #ef4444; background: #fef2f2; }
    .result-name { font-size: 12px; color: #64748b; }
    .result-value { font-size: 24px; font-weight: 700; margin: 8px 0; }
    .result-card.good .result-value { color: #10b981; }
    .result-card.warning .result-value { color: #f59e0b; }
    .result-card.danger .result-value { color: #ef4444; }
    .variance-table { width: 100%; border-collapse: collapse; }
    .variance-table th, .variance-table td { padding: 12px; border-bottom: 1px solid #e2e8f0; text-align: left; }
    .variance-table th { background: #f8fafc; font-weight: 600; }
    .report-footer { padding: 24px 32px; background: #f8fafc; text-align: center; color: #64748b; font-size: 12px; }
  </style>
</head>
<body>
  <div class="report-container">
    <div class="report-header">
      <h1>${s.study_name}</h1>
      <p>MSA研究报告 | ${getStudyTypeLabel(s.study_type)} | ${formatDate(s.created_at)}</p>
    </div>
    <div class="report-body">
      <div class="section">
        <h2 class="section-title">研究信息</h2>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">研究类型</span>
            <span class="info-value">${getStudyTypeLabel(s.study_type)}</span>
          </div>
          <div class="info-item">
            <span class="info-label">测量特性</span>
            <span class="info-value">${s.characteristic || '-'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">测量系统</span>
            <span class="info-value">${s.measurement_system || '-'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">研究设计</span>
            <span class="info-value">${s.number_of_parts}件 × ${s.number_of_operators}人 × ${s.number_of_replicates}次</span>
          </div>
          <div class="info-item">
            <span class="info-label">规格上限</span>
            <span class="info-value">${s.specification_upper || '-'}</span>
          </div>
          <div class="info-item">
            <span class="info-label">规格下限</span>
            <span class="info-value">${s.specification_lower || '-'}</span>
          </div>
        </div>
      </div>
      ${r ? `
      <div class="section">
        <h2 class="section-title">GR&R分析结果</h2>
        <div class="result-cards">
          <div class="result-card ${getGRRClass(parseFloat(r.percent_grr || '0'))}">
            <div class="result-name">%GR&R</div>
            <div class="result-value">${parseFloat(r.percent_grr || '0').toFixed(2)}%</div>
            <div>${getGRRAcceptance(r.grr_acceptance)}</div>
          </div>
          <div class="result-card ${parseFloat(r.ndc || '0') >= 5 ? 'good' : 'warning'}">
            <div class="result-name">NDC</div>
            <div class="result-value">${parseFloat(r.ndc || '0').toFixed(1)}</div>
            <div>${getNDCAcceptance(r.ndc_acceptance)}</div>
          </div>
          <div class="result-card">
            <div class="result-name">%P/T</div>
            <div class="result-value">${parseFloat(r.percent_tolerance || '0').toFixed(2)}%</div>
          </div>
          <div class="result-card ${r.overall_acceptance}">
            <div class="result-name">综合判定</div>
            <div class="result-value">${getAcceptanceLabel(r.overall_acceptance)}</div>
          </div>
        </div>
      </div>
      <div class="section">
        <h2 class="section-title">方差分量</h2>
        <table class="variance-table">
          <thead>
            <tr>
              <th>来源</th>
              <th>方差</th>
              <th>标准差</th>
              <th>贡献%</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>重复性</td>
              <td>${parseFloat(r.variance_repeatability || '0').toFixed(6)}</td>
              <td>${parseFloat(r.stddev_repeatability || '0').toFixed(4)}</td>
              <td>${getVariancePercent('repeatability')}%</td>
            </tr>
            <tr>
              <td>再现性</td>
              <td>${parseFloat(r.variance_reproducibility || '0').toFixed(6)}</td>
              <td>${parseFloat(r.stddev_reproducibility || '0').toFixed(4)}</td>
              <td>${getVariancePercent('reproducibility')}%</td>
            </tr>
            <tr style="background: #f0f9ff;">
              <td><strong>GR&R</strong></td>
              <td>${parseFloat(r.variance_grr || '0').toFixed(6)}</td>
              <td>${parseFloat(r.stddev_grr || '0').toFixed(4)}</td>
              <td>${getVariancePercent('grr')}%</td>
            </tr>
            <tr>
              <td>零件</td>
              <td>${parseFloat(r.variance_part || '0').toFixed(6)}</td>
              <td>${parseFloat(r.stddev_part || '0').toFixed(4)}</td>
              <td>${getVariancePercent('part')}%</td>
            </tr>
            <tr style="background: #f8fafc;">
              <td><strong>总变异</strong></td>
              <td>${parseFloat(r.variance_total || '0').toFixed(6)}</td>
              <td>${parseFloat(r.stddev_total || '0').toFixed(4)}</td>
              <td>100%</td>
            </tr>
          </tbody>
        </table>
      </div>
      ` : ''}
    </div>
    <div class="report-footer">
      报告生成时间: ${new Date().toLocaleString('zh-CN')}
    </div>
  </div>
</body>
</html>
  `
}

onMounted(() => {
  fetchStudy()
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

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.btn-export, .btn-calculate, .btn-edit {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-export {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-export:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.btn-calculate {
  background: linear-gradient(135deg, #10b981, #059669);
  border: none;
  color: white;
}

.btn-calculate:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.btn-edit {
  background: linear-gradient(135deg, var(--accent-primary), #0284c7);
  border: none;
  color: white;
}

.btn-edit:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

.status-badge {
  padding: 6px 16px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.draft {
  background: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
}

.status-badge.in_progress {
  background: rgba(245, 158, 11, 0.1);
  color: #f59e0b;
}

.status-badge.completed {
  background: rgba(16, 185, 129, 0.1);
  color: #10b981;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.info-section,
.result-section,
.variance-section,
.measurement-section,
.parts-operators-section {
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

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.info-value {
  font-weight: 500;
  color: var(--text-primary);
}

.info-value.design {
  font-family: var(--font-mono);
  color: var(--accent-primary);
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

.result-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.result-card {
  padding: 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  text-align: center;
}

.result-card.main {
  grid-column: span 2;
}

.result-card.good {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.05);
}

.result-card.warning {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.05);
}

.result-card.danger {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
}

.result-card.overall {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.result-card.overall.acceptable {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.1);
}

.result-card.overall.conditional {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
}

.result-card.overall.unacceptable {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
}

.result-status {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.result-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.result-card.good .result-value { color: #10b981; }
.result-card.warning .result-value { color: #f59e0b; }
.result-card.danger .result-value { color: #ef4444; }

.result-desc {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.result-hint {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 4px;
}

.result-bar {
  height: 8px;
  background: var(--bg-secondary);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
}

.bar-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.result-card.good .bar-fill { background: #10b981; }
.result-card.warning .bar-fill { background: #f59e0b; }
.result-card.danger .bar-fill { background: #ef4444; }

.result-scale {
  display: flex;
  justify-content: space-between;
  font-size: 0.625rem;
}

.scale-item.good { color: #10b981; }
.scale-item.warning { color: #f59e0b; }
.scale-item.danger { color: #ef4444; }

.result-icon {
  margin-top: 8px;
}

.result-card.overall.acceptable .result-icon { color: #10b981; }
.result-card.overall.conditional .result-icon { color: #f59e0b; }
.result-card.overall.unacceptable .result-icon { color: #ef4444; }

.variance-content {
  display: flex;
  gap: 24px;
}

.variance-chart {
  width: 200px;
  height: 200px;
  flex-shrink: 0;
}

.variance-table {
  flex: 1;
}

.variance-row {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr 80px;
  padding: 10px 0;
  border-bottom: 1px solid var(--border-color);
}

.variance-row.header {
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  border-bottom: 2px solid var(--border-color);
}

.variance-row.grr {
  background: rgba(0, 212, 255, 0.05);
}

.variance-row.total {
  font-weight: 600;
  background: var(--bg-secondary);
}

.col {
  padding: 0 8px;
}

.col.mono {
  font-family: var(--font-mono);
  font-size: 0.875rem;
}

.measurement-table-wrapper {
  overflow-x: auto;
}

.measurement-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.measurement-table th,
.measurement-table td {
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  text-align: center;
}

.measurement-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  color: var(--text-secondary);
}

.measurement-table .part-col {
  background: var(--bg-secondary);
  text-align: left;
  min-width: 120px;
}

.measurement-table .operator-col {
  background: rgba(0, 212, 255, 0.05);
}

.measurement-table .replicate-col {
  font-weight: 400;
  font-size: 0.75rem;
}

.measurement-table .part-cell {
  text-align: left;
}

.part-name {
  font-weight: 500;
}

.part-ref {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-left: 4px;
}

.measurement-cell {
  font-family: var(--font-mono);
}

.parts-operators-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.subsection {
  flex: 1;
}

.subsection-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-color);
}

.list-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.list-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--bg-secondary);
  border-radius: var(--radius-sm);
}

.item-number {
  font-family: var(--font-mono);
  font-size: 0.75rem;
  color: var(--accent-primary);
  background: rgba(0, 212, 255, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
}

.item-name {
  font-weight: 500;
  color: var(--text-primary);
}

.item-ref {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-left: auto;
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
  
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .result-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .result-card.main {
    grid-column: span 1;
  }
  
  .variance-content {
    flex-direction: column;
  }
  
  .variance-chart {
    width: 100%;
    height: 250px;
  }
  
  .parts-operators-section {
    grid-template-columns: 1fr;
  }
}
</style>
