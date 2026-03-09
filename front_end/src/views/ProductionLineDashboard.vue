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
            <h1 class="page-title">{{ line?.line_name || '产线详情' }}</h1>
            <p class="page-subtitle">{{ line?.line_code }}</p>
          </div>
        </div>
        <div class="header-right">
          <div class="status-badge" :class="line?.status">
            {{ line?.status === 'active' ? '运行中' : '已停用' }}
          </div>
        </div>
      </div>
      
      <div class="info-section">
        <h2 class="section-title">产线信息</h2>
        <div class="info-grid">
          <div class="info-card">
            <span class="info-label">产线编号</span>
            <span class="info-value">{{ line?.line_code }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">数据类型</span>
            <span class="info-value">{{ getDataTypeText(line?.data_type) }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">创建时间</span>
            <span class="info-value">{{ formatTime(line?.created_at) }}</span>
          </div>
          <div class="info-card">
            <span class="info-label">数据总量</span>
            <span class="info-value">{{ totalDataCount }} 条</span>
          </div>
        </div>
        <div class="info-desc" v-if="line?.line_description">
          <span class="info-label">描述</span>
          <p class="desc-text">{{ line.line_description }}</p>
        </div>
      </div>
      
      <div class="modules-section">
        <h2 class="section-title">功能模块</h2>
        <div class="modules-grid">
          <router-link :to="`/production-lines/${lineId}/data-collection`" class="module-card">
            <div class="module-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="17 8 12 3 7 8"/>
                <line x1="12" y1="3" x2="12" y2="15"/>
              </svg>
            </div>
            <h3 class="module-title">数据采集</h3>
            <p class="module-desc">上传检测样本数据，支持图片和Excel格式</p>
          </router-link>
          
          <router-link :to="`/production-lines/${lineId}/history`" class="module-card">
            <div class="module-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
            </div>
            <h3 class="module-title">监测历史</h3>
            <p class="module-desc">查看历史监测记录和统计报表</p>
          </router-link>
          
          <router-link :to="`/production-lines/${lineId}/control-chart`" class="module-card">
            <div class="module-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v18h18"/>
                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
              </svg>
            </div>
            <h3 class="module-title">SPC控制图</h3>
            <p class="module-desc">实时监控生产过程质量状态</p>
          </router-link>
          
          <router-link 
            v-if="line?.data_type === 'measurement'" 
            :to="`/production-lines/${lineId}/capability-analysis`" 
            class="module-card"
          >
            <div class="module-icon capability">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            <h3 class="module-title">能力分析</h3>
            <p class="module-desc">过程能力指数计算与评价（仅计量型数据）</p>
          </router-link>
          
          <div v-else class="module-card disabled">
            <div class="module-icon capability">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
            </div>
            <h3 class="module-title">能力分析</h3>
            <p class="module-desc">仅适用于计量型数据产线</p>
            <span class="module-tag">当前产线为计数型</span>
          </div>
          
          <router-link :to="`/production-lines/${lineId}/control-plans`" class="module-card">
            <div class="module-icon">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
                <line x1="16" y1="13" x2="8" y2="13"/>
                <line x1="16" y1="17" x2="8" y2="17"/>
                <polyline points="10 9 9 9 8 9"/>
              </svg>
            </div>
            <h3 class="module-title">控制计划</h3>
            <p class="module-desc">AIAG-VDA标准质量控制计划</p>
          </router-link>
          
          <router-link :to="`/production-lines/${lineId}/ocaps`" class="module-card">
            <div class="module-icon warning">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                <line x1="12" y1="9" x2="12" y2="13"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <h3 class="module-title">OCAP</h3>
            <p class="module-desc">失控行动计划与异常处理流程</p>
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getProductionLine, getAttributeData, getMeasurementData } from '@/api'
import type { ProductionLine, AttributeData, MeasurementData } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = Number(route.params.id)
const line = ref<ProductionLine | null>(null)
const attributeData = ref<AttributeData[]>([])
const measurementData = ref<MeasurementData[]>([])

const totalDataCount = ref(0)

const fetchData = async () => {
  try {
    const [lineRes, attrRes, measureRes] = await Promise.all([
      getProductionLine(lineId),
      getAttributeData(lineId),
      getMeasurementData(lineId)
    ])
    
    line.value = lineRes as ProductionLine
    attributeData.value = attrRes as AttributeData[]
    measurementData.value = measureRes as MeasurementData[]
    totalDataCount.value = attributeData.value.length + measurementData.value.length
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const getDataTypeText = (type?: string) => {
  const map: Record<string, string> = {
    measurement: '计量型数据',
    attribute: '计数型数据',
    mixed: '混合类型'
  }
  return type ? map[type] || type : '–'
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

const goBack = () => {
  router.push('/production-lines')
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

.status-badge {
  padding: 6px 16px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.status-badge.inactive {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.info-section, .modules-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 32px;
}

.section-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.info-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.info-value {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.info-desc {
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.desc-text {
  margin-top: 8px;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
}

.modules-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.module-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  text-decoration: none;
  transition: all var(--transition-normal);
}

.module-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-4px);
  box-shadow: 0 10px 40px rgba(0, 212, 255, 0.15);
}

.module-icon {
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--accent-primary);
  margin-bottom: 16px;
}

.module-icon.capability {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.module-title {
  font-family: var(--font-display);
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.module-desc {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-align: center;
}

.module-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.module-card.disabled .module-icon {
  background: rgba(107, 114, 128, 0.1);
  color: var(--text-muted);
}

.module-tag {
  margin-top: 8px;
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 100px;
  font-size: 0.75rem;
  color: var(--danger);
}

@media (max-width: 1200px) {
  .info-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .modules-grid {
    grid-template-columns: 1fr;
  }
}
</style>
