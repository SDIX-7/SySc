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
            <h1 class="page-title">监测历史</h1>
            <p class="page-subtitle">{{ line?.line_name }}</p>
          </div>
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
            <span class="stat-value">{{ totalRecords }}</span>
            <span class="stat-label">总记录数</span>
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
            <span class="stat-value">{{ totalDefects }}</span>
            <span class="stat-label">异常总数</span>
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
            <span class="stat-value">{{ passRate }}%</span>
            <span class="stat-label">合格率</span>
          </div>
        </div>
      </div>
      
      <div class="query-section">
        <div class="query-form">
          <div class="query-row">
            <div class="query-item">
              <label class="query-label">开始日期</label>
              <el-date-picker
                v-model="queryParams.startDate"
                type="date"
                placeholder="选择开始日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :clearable="true"
                class="date-picker"
              />
            </div>
            <div class="query-item">
              <label class="query-label">结束日期</label>
              <el-date-picker
                v-model="queryParams.endDate"
                type="date"
                placeholder="选择结束日期"
                format="YYYY-MM-DD"
                value-format="YYYY-MM-DD"
                :clearable="true"
                class="date-picker"
              />
            </div>
            <div class="query-item">
              <label class="query-label">样本编号</label>
              <el-input
                v-model="queryParams.sampleId"
                placeholder="请输入样本编号"
                clearable
                class="search-input"
              />
            </div>
            <div class="query-item">
              <label class="query-label">检测状态</label>
              <el-select
                v-model="queryParams.status"
                placeholder="全部状态"
                clearable
                class="status-select"
              >
                <el-option label="全部" value="" />
                <el-option label="正常" value="normal" />
                <el-option label="异常" value="abnormal" />
              </el-select>
            </div>
          </div>
          <div class="query-actions">
            <el-button type="primary" @click="handleQuery" :loading="loading">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="11" cy="11" r="8"/>
                <line x1="21" y1="21" x2="16.65" y2="16.65"/>
              </svg>
              查询
            </el-button>
            <el-button @click="handleReset">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                <path d="M3 3v5h5"/>
              </svg>
              重置
            </el-button>
          </div>
        </div>
      </div>
      
      <div class="table-section">
        <div class="table-container" v-loading="loading" element-loading-text="加载中...">
          <table class="data-table">
            <thead>
              <tr>
                <th>图片预览</th>
                <th>样本编号</th>
                <th>缺陷类型</th>
                <th>缺陷数量</th>
                <th>检验时间</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in tableData" :key="item.id">
                <td>
                  <div class="table-image" @click="viewDetail(item)">
                    <img 
                      v-if="getDefectThumbnail(item)" 
                      :src="getDefectThumbnail(item)" 
                      :alt="item.sample_id"
                    />
                    <div v-else class="no-image-small">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                        <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                        <circle cx="8.5" cy="8.5" r="1.5"/>
                        <polyline points="21 15 16 10 5 21"/>
                      </svg>
                    </div>
                  </div>
                </td>
                <td class="sample-id">{{ item.sample_id }}</td>
                <td>
                  <div class="defect-types">
                    <span 
                      v-for="(cls, idx) in getDefectClasses(item)" 
                      :key="idx" 
                      class="defect-tag"
                    >
                      {{ cls }}
                    </span>
                    <span v-if="getDefectClasses(item).length === 0" class="no-defect">正常</span>
                  </div>
                </td>
                <td :class="{ 'text-danger': item.defect_count > 0, 'text-success': item.defect_count === 0 }">
                  {{ item.defect_count }}
                </td>
                <td>{{ formatTime(item.inspection_time) }}</td>
                <td>
                  <button class="btn-view" @click="viewDetail(item)">查看详情</button>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-if="tableData.length === 0 && !loading" class="empty-table">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            <p>暂无监测数据</p>
          </div>
        </div>
        
        <div class="pagination-section" v-if="total > 0">
          <div class="pagination-info">
            共 <span class="highlight">{{ total }}</span> 条记录，当前第 <span class="highlight">{{ currentPage }}</span> / <span class="highlight">{{ totalPages }}</span> 页
          </div>
          <div class="pagination-controls">
            <el-button 
              :disabled="currentPage === 1" 
              @click="handlePageChange(1)"
              size="small"
            >
              首页
            </el-button>
            <el-button 
              :disabled="currentPage === 1" 
              @click="handlePageChange(currentPage - 1)"
              size="small"
            >
              上一页
            </el-button>
            <div class="page-numbers">
              <button 
                v-for="page in visiblePages" 
                :key="page"
                :class="['page-btn', { active: page === currentPage }]"
                @click="handlePageChange(page)"
              >
                {{ page }}
              </button>
            </div>
            <el-button 
              :disabled="currentPage === totalPages" 
              @click="handlePageChange(currentPage + 1)"
              size="small"
            >
              下一页
            </el-button>
            <el-button 
              :disabled="currentPage === totalPages" 
              @click="handlePageChange(totalPages)"
              size="small"
            >
              末页
            </el-button>
            <div class="page-jump">
              <span>跳至</span>
              <el-input-number 
                v-model="jumpPage" 
                :min="1" 
                :max="totalPages" 
                size="small"
                controls-position="right"
              />
              <span>页</span>
              <el-button size="small" @click="handleJumpPage">确定</el-button>
            </div>
          </div>
        </div>
      </div>
      
      <el-dialog
        v-model="showDetailDialog"
        title="检测详情"
        width="700px"
        class="detail-dialog"
      >
        <div v-if="selectedItem" class="detail-content">
          <div class="detail-header">
            <div class="detail-image" v-if="getDefectFullImage(selectedItem)">
              <img :src="getDefectFullImage(selectedItem)" :alt="selectedItem.sample_id" />
            </div>
            <div class="detail-image empty" v-else>
              <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <polyline points="21 15 16 10 5 21"/>
              </svg>
              <p>无缺陷</p>
            </div>
          </div>
          
          <div class="detail-info">
            <div class="info-row">
              <span class="info-label">样本编号</span>
              <span class="info-value">{{ selectedItem.sample_id }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">检测状态</span>
              <span class="info-value" :class="{ 'text-danger': selectedItem.defect_count > 0, 'text-success': selectedItem.defect_count === 0 }">
                {{ selectedItem.defect_count > 0 ? '存在缺陷' : '正常' }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">缺陷数量</span>
              <span class="info-value" :class="{ 'text-danger': selectedItem.defect_count > 0 }">
                {{ selectedItem.defect_count }}
              </span>
            </div>
            <div class="info-row">
              <span class="info-label">检验时间</span>
              <span class="info-value">{{ formatTime(selectedItem.inspection_time) }}</span>
            </div>
            <div class="info-row">
              <span class="info-label">检验员</span>
              <span class="info-value">{{ selectedItem.inspector || '-' }}</span>
            </div>
          </div>
          
          <div class="detail-defects" v-if="getDefectClasses(selectedItem).length > 0">
            <h4>缺陷类型详情</h4>
            <div class="defect-list">
              <div 
                v-for="(cls, idx) in getDefectClasses(selectedItem)" 
                :key="idx" 
                class="defect-item"
              >
                <span class="defect-icon">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/>
                    <line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                </span>
                <span class="defect-name">{{ getDefectTypeName(cls) }}</span>
              </div>
            </div>
          </div>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Menu from '@/components/Menu.vue'
import { getProductionLine, getAttributeData } from '@/api'
import type { ProductionLine, AttributeData } from '@/types'

const route = useRoute()
const router = useRouter()

const lineId = Number(route.params.id)
const line = ref<ProductionLine | null>(null)
const allData = ref<AttributeData[]>([])
const loading = ref(false)
const showDetailDialog = ref(false)
const selectedItem = ref<AttributeData | null>(null)

const pageSize = 20
const currentPage = ref(1)
const jumpPage = ref(1)

const queryParams = ref({
  startDate: '',
  endDate: '',
  sampleId: '',
  status: ''
})

const filteredData = computed(() => {
  let result = [...allData.value]
  
  if (queryParams.value.startDate) {
    const startDate = new Date(queryParams.value.startDate)
    startDate.setHours(0, 0, 0, 0)
    result = result.filter(item => {
      const itemDate = new Date(item.inspection_time || '')
      return itemDate >= startDate
    })
  }
  
  if (queryParams.value.endDate) {
    const endDate = new Date(queryParams.value.endDate)
    endDate.setHours(23, 59, 59, 999)
    result = result.filter(item => {
      const itemDate = new Date(item.inspection_time || '')
      return itemDate <= endDate
    })
  }
  
  if (queryParams.value.sampleId) {
    const keyword = queryParams.value.sampleId.toLowerCase()
    result = result.filter(item => 
      item.sample_id.toLowerCase().includes(keyword)
    )
  }
  
  if (queryParams.value.status) {
    if (queryParams.value.status === 'normal') {
      result = result.filter(item => item.defect_count === 0)
    } else if (queryParams.value.status === 'abnormal') {
      result = result.filter(item => item.defect_count > 0)
    }
  }
  
  return result.sort((a, b) => 
    new Date(b.inspection_time || '').getTime() - new Date(a.inspection_time || '').getTime()
  )
})

const total = computed(() => filteredData.value.length)

const totalPages = computed(() => Math.ceil(total.value / pageSize) || 1)

const tableData = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  const end = start + pageSize
  return filteredData.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value
  
  let start = Math.max(1, current - 2)
  let end = Math.min(total, current + 2)
  
  if (end - start < 4) {
    if (start === 1) {
      end = Math.min(total, start + 4)
    } else if (end === total) {
      start = Math.max(1, end - 4)
    }
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const totalRecords = computed(() => allData.value.length)
const totalDefects = computed(() => allData.value.reduce((sum, item) => sum + item.defect_count, 0))
const passRate = computed(() => {
  if (allData.value.length === 0) return 100
  const passCount = allData.value.filter(item => item.defect_count === 0).length
  return Math.round((passCount / allData.value.length) * 100)
})

const getDefectClasses = (item: AttributeData): string[] => {
  if (!item.defect_details) return []
  if (typeof item.defect_details === 'string') {
    try {
      const details = JSON.parse(item.defect_details)
      return details.classes || []
    } catch {
      return []
    }
  }
  return item.defect_details?.classes || []
}

const getDefectThumbnail = (item: AttributeData): string | null => {
  if (!item.defect_details) return null
  let details: any = item.defect_details
  if (typeof item.defect_details === 'string') {
    try {
      details = JSON.parse(item.defect_details)
    } catch {
      return null
    }
  }
  if (details.thumbnail_path) {
    return details.thumbnail_path
  }
  if (details.image) {
    return `/results/thumbnails/${item.sample_id}.png`
  }
  return null
}

const getDefectFullImage = (item: AttributeData): string | null => {
  if (!item.defect_details) return null
  let details: any = item.defect_details
  if (typeof item.defect_details === 'string') {
    try {
      details = JSON.parse(item.defect_details)
    } catch {
      return null
    }
  }
  if (details.image_path) {
    return details.image_path
  }
  if (details.image) {
    return `/results/images/${item.sample_id}.png`
  }
  return null
}

const getDefectTypeName = (cls: string): string => {
  const map: Record<string, string> = {
    'missing_hole': '缺孔',
    'mouse_bite': '鼠咬',
    'open_circuit': '开路',
    'short': '短路',
    'spur': '毛刺',
    'spurious_copper': '多余铜'
  }
  return map[cls] || cls
}

const fetchData = async () => {
  loading.value = true
  try {
    const [lineRes, attrRes] = await Promise.all([
      getProductionLine(lineId),
      getAttributeData(lineId)
    ])
    
    line.value = lineRes as ProductionLine
    allData.value = (attrRes as AttributeData[]).sort((a, b) => 
      new Date(b.inspection_time || '').getTime() - new Date(a.inspection_time || '').getTime()
    )
  } catch (error) {
    console.error('获取数据失败:', error)
  } finally {
    loading.value = false
  }
}

const handleQuery = () => {
  loading.value = true
  currentPage.value = 1
  setTimeout(() => {
    loading.value = false
  }, 300)
}

const handleReset = () => {
  queryParams.value = {
    startDate: '',
    endDate: '',
    sampleId: '',
    status: ''
  }
  currentPage.value = 1
}

const handlePageChange = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    jumpPage.value = page
  }
}

const handleJumpPage = () => {
  if (jumpPage.value >= 1 && jumpPage.value <= totalPages.value) {
    currentPage.value = jumpPage.value
  }
}

const viewDetail = (item: AttributeData) => {
  selectedItem.value = item
  showDetailDialog.value = true
}

const formatTime = (time?: string) => {
  if (!time) return '-'
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
  router.push(`/production-lines/${lineId}`)
}

watch(currentPage, (newVal) => {
  jumpPage.value = newVal
})

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

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
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

.query-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 20px 24px;
  margin-bottom: 24px;
}

.query-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.query-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.query-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 180px;
}

.query-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.date-picker,
.search-input,
.status-select {
  width: 100%;
}

.query-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.query-actions .el-button {
  display: flex;
  align-items: center;
  gap: 6px;
}

.table-section {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.table-container {
  overflow-x: auto;
  min-height: 200px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 12px 16px;
  text-align: left;
  font-family: var(--font-display);
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.data-table td {
  padding: 12px 16px;
  font-size: 0.875rem;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
}

.table-image {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.no-image-small {
  color: var(--text-muted);
}

.sample-id {
  font-family: var(--font-mono);
  color: var(--accent-primary);
}

.defect-types {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.defect-tag {
  padding: 2px 8px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--danger);
}

.no-defect {
  padding: 2px 8px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: 4px;
  font-size: 0.7rem;
  color: var(--success);
}

.text-danger {
  color: var(--danger);
}

.text-success {
  color: var(--success);
}

.btn-view {
  padding: 6px 12px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-view:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.empty-table {
  padding: 60px 40px;
  text-align: center;
  color: var(--text-muted);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.empty-table svg {
  opacity: 0.5;
}

.empty-table p {
  font-size: 0.875rem;
}

.pagination-section {
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination-info {
  font-size: 0.875rem;
  color: var(--text-muted);
}

.pagination-info .highlight {
  color: var(--accent-primary);
  font-weight: 600;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.page-numbers {
  display: flex;
  gap: 4px;
}

.page-btn {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.page-btn:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-btn.active {
  background: var(--accent-primary);
  border-color: var(--accent-primary);
  color: #000;
}

.page-jump {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: 16px;
  font-size: 0.875rem;
  color: var(--text-muted);
}

.page-jump .el-input-number {
  width: 80px;
}

.detail-content {
  padding: 0;
}

.detail-header {
  margin-bottom: 24px;
}

.detail-image {
  width: 100%;
  max-height: 300px;
  border-radius: var(--radius-md);
  overflow: hidden;
  background: var(--bg-secondary);
}

.detail-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}

.detail-image.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: var(--text-muted);
}

.detail-image.empty p {
  margin-top: 12px;
  font-size: 0.875rem;
}

.detail-info {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  padding: 0 24px;
}

.info-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-transform: uppercase;
}

.info-value {
  font-size: 0.875rem;
  color: var(--text-primary);
}

.detail-defects {
  margin-top: 24px;
  padding: 24px;
  background: rgba(239, 68, 68, 0.05);
  border-top: 1px solid var(--border-color);
}

.detail-defects h4 {
  font-family: var(--font-display);
  font-size: 0.875rem;
  color: var(--text-primary);
  margin-bottom: 16px;
}

.defect-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.defect-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: var(--radius-sm);
}

.defect-icon {
  color: var(--danger);
}

.defect-name {
  font-size: 0.875rem;
  color: var(--danger);
  font-weight: 600;
}

:deep(.detail-dialog .el-dialog__body) {
  padding: 0;
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .detail-info {
    grid-template-columns: 1fr;
  }
  
  .query-row {
    flex-direction: column;
  }
  
  .query-item {
    min-width: 100%;
  }
  
  .pagination-controls {
    justify-content: center;
  }
  
  .page-jump {
    margin-left: 0;
    margin-top: 8px;
    width: 100%;
    justify-content: center;
  }
}
</style>
