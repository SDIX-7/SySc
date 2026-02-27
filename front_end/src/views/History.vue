<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">检测历史</h1>
          <p class="page-subtitle">查看和分析历史检测记录</p>
        </div>
        <div class="header-right">
          <div class="filter-group">
            <div class="date-picker">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/>
                <line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
                @change="fetchData"
              />
            </div>
            <button class="btn-icon" @click="fetchData">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6"/>
                <path d="M1 20v-6h6"/>
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/>
              </svg>
            </button>
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
            <span class="stat-value">{{ tableData.length }}</span>
            <span class="stat-label">总记录数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon danger">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/>
              <line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ defectCount }}</span>
            <span class="stat-label">缺陷数量</span>
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
            <span class="stat-value">{{ normalCount }}</span>
            <span class="stat-label">正常数量</span>
          </div>
        </div>
      </div>
      
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>图片</th>
              <th>名称</th>
              <th>状态</th>
              <th>缺陷数</th>
              <th>类型</th>
              <th>时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in paginatedData" :key="item.id" class="table-row">
              <td class="td-id">{{ item.id }}</td>
              <td class="td-image">
                <div class="thumbnail" :class="{ 'has-defect': item.hasDefects }">
                  <img 
                    v-if="item.hasDefects"
                    :src="`/results/images/${item.name}.png`" 
                    alt=""
                  />
                  <div v-else class="thumbnail-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <polyline points="20 6 9 17 4 12"/>
                    </svg>
                  </div>
                </div>
              </td>
              <td class="td-name">{{ item.name }}</td>
              <td class="td-status">
                <span class="status-badge" :class="item.hasDefects ? 'danger' : 'success'">
                  {{ item.hasDefects ? '缺陷' : '正常' }}
                </span>
              </td>
              <td class="td-count">{{ item.detection_total_cnts }}</td>
              <td class="td-types">
                <div class="type-tags" v-if="item.detection_classes?.length">
                  <span v-for="(type, i) in getUniqueTypes(item.detection_classes)" :key="i" class="type-tag">
                    {{ type }}
                  </span>
                </div>
                <span v-else class="no-data">–</span>
              </td>
              <td class="td-time">{{ formatTime(item.captureTime) }}</td>
            </tr>
          </tbody>
        </table>
        
        <div v-if="tableData.length === 0" class="empty-table">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
          </svg>
          <p>暂无检测记录</p>
        </div>
      </div>
      
      <div class="pagination" v-if="tableData.length > pageSize">
        <button 
          class="page-btn" 
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15 18 9 12 15 6"/>
          </svg>
        </button>
        <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
        <button 
          class="page-btn" 
          :disabled="currentPage === totalPages"
          @click="currentPage++"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import Menu from '@/components/Menu.vue'
import { getImages } from '@/api'
import type { ImageItem } from '@/types'

const dateRange = ref<string[]>([])
const tableData = ref<ImageItem[]>([])
const currentPage = ref(1)
const pageSize = ref(10)

const defectCount = computed(() => tableData.value.filter(item => item.hasDefects).length)
const normalCount = computed(() => tableData.value.filter(item => !item.hasDefects).length)
const totalPages = computed(() => Math.ceil(tableData.value.length / pageSize.value))
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return tableData.value.slice(start, start + pageSize.value)
})

const fetchData = async () => {
  try {
    const [startDate, endDate] = dateRange.value
    const response = await getImages(startDate, endDate) as ImageItem[]
    tableData.value = response
    currentPage.value = 1
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

const getUniqueTypes = (types: string[]) => {
  return [...new Set(types)]
}

const formatTime = (time: string) => {
  if (!time) return '–'
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
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

.filter-group {
  display: flex;
  gap: 12px;
}

.date-picker {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
}

.date-picker :deep(.el-date-editor) {
  --el-date-editor-width: 220px;
}

.date-picker :deep(.el-input__wrapper) {
  background: transparent;
  box-shadow: none;
  padding: 0;
}

.date-picker :deep(.el-input__inner) {
  color: var(--text-primary);
  font-family: var(--font-body);
}

.btn-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-icon:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
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

.stat-icon.danger {
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

.table-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 16px 20px;
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

.table-row {
  transition: background var(--transition-fast);
}

.table-row:hover {
  background: rgba(0, 212, 255, 0.03);
}

.data-table td {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  font-size: 0.875rem;
  color: var(--text-primary);
}

.td-id {
  font-family: var(--font-mono);
  color: var(--text-muted);
}

.thumbnail {
  width: 60px;
  height: 40px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: var(--bg-secondary);
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--success);
}

.status-badge {
  display: inline-flex;
  padding: 4px 12px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.status-badge.danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--danger);
}

.td-count {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--accent-primary);
}

.type-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.type-tag {
  padding: 2px 8px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: 4px;
  font-size: 0.75rem;
  color: var(--accent-primary);
}

.no-data {
  color: var(--text-muted);
}

.td-time {
  font-family: var(--font-mono);
  font-size: 0.8rem;
  color: var(--text-muted);
}

.empty-table {
  padding: 60px;
  text-align: center;
  color: var(--text-muted);
}

.empty-table svg {
  margin-bottom: 16px;
  opacity: 0.5;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.page-btn:hover:not(:disabled) {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.page-info {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--text-secondary);
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 20px;
  }
}
</style>
