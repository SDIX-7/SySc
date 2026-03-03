<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <h1 class="page-title">产线管理</h1>
          <p class="page-subtitle">管理和监控所有生产线</p>
        </div>
        <div class="header-right">
          <button class="btn-primary" @click="showCreateDialog = true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="5" x2="12" y2="19"/>
              <line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            创建产线
          </button>
        </div>
      </div>
      
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ lines.length }}</span>
            <span class="stat-label">产线总数</span>
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
            <span class="stat-value">{{ activeLines }}</span>
            <span class="stat-label">启用产线</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon warning">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ inactiveLines }}</span>
            <span class="stat-label">停用产线</span>
          </div>
        </div>
      </div>
      
      <div class="cards-grid">
        <div 
          v-for="line in lines" 
          :key="line.id" 
          class="line-card"
          :class="{ inactive: line.status === 'inactive' }"
        >
          <div class="card-header">
            <div class="line-status" :class="line.status">
              {{ line.status === 'active' ? '运行中' : '已停用' }}
            </div>
            <div class="card-actions">
              <button class="btn-icon-small" @click="editLine(line)" title="编辑">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button class="btn-icon-small danger" @click="confirmDelete(line)" title="删除">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
          
          <div class="card-body" @click="viewDetail(line)">
            <h3 class="line-name">{{ line.line_name }}</h3>
            <p class="line-code">{{ line.line_code }}</p>
            <p class="line-desc" v-if="line.line_description">{{ line.line_description }}</p>
            
            <div class="line-info">
              <div class="info-item">
                <span class="info-label">数据类型</span>
                <span class="info-value">{{ getDataTypeText(line.data_type) }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">创建时间</span>
                <span class="info-value">{{ formatTime(line.created_at) }}</span>
              </div>
            </div>
          </div>
          
          <div class="card-footer">
            <button class="btn-link" @click="viewDetail(line)">
              查看详情
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="9 18 15 12 9 6"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div v-if="lines.length === 0" class="empty-state">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
          </svg>
          <h3>暂无产线</h3>
          <p>点击上方按钮创建第一条产线</p>
        </div>
      </div>
    </div>
    
    <el-dialog
      v-model="showCreateDialog"
      title="创建产线"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-position="top" class="line-form">
            <el-form-item label="产线编号" required>
              <el-input v-model="formData.line_code" placeholder="请输入产线编号" />
            </el-form-item>
            <el-form-item label="产线名称" required>
              <el-input v-model="formData.line_name" placeholder="请输入产线名称" />
            </el-form-item>
            <el-form-item label="产线描述">
              <el-input v-model="formData.line_description" type="textarea" :rows="3" placeholder="请输入产线描述（可选）" />
            </el-form-item>
            <el-form-item label="数据类型">
              <el-select v-model="formData.data_type" placeholder="请选择数据类型" @change="handleDataTypeChange">
                <el-option label="计数型数据（属性数据）" value="attribute" />
                <el-option label="计量型数据（测量数据）" value="measurement" />
              </el-select>
              <div class="data-type-hint">
                <template v-if="formData.data_type === 'attribute'">
                  <span class="hint-icon">💡</span> 计数型数据：通过图像检测统计缺陷数量，需要选择模型文件
                </template>
                <template v-else-if="formData.data_type === 'measurement'">
                  <span class="hint-icon">💡</span> 计量型数据：通过测量仪器采集连续数值，无需模型文件
                </template>
              </div>
            </el-form-item>
            <el-form-item label="模型文件" v-if="formData.data_type === 'attribute'">
              <el-select v-model="formData.model_path" placeholder="请选择模型文件" clearable filterable>
                <el-option 
                  v-for="file in modelFiles" 
                  :key="file.filename" 
                  :label="file.filename + ' (' + file.size_formatted + ')'"
                  :value="file.filename"
                />
              </el-select>
              <div class="form-hint">选择用于图像缺陷检测的AI模型文件</div>
            </el-form-item>
            <el-form-item label="状态">
              <el-radio-group v-model="formData.status">
                <el-radio label="active">启用</el-radio>
                <el-radio label="inactive">停用</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="createLine" :loading="loading">创建</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showEditDialog"
      title="编辑产线"
      width="500px"
      :close-on-click-modal="false"
    >
      <el-form :model="editData" label-position="top" class="line-form">
        <el-form-item label="产线编号">
          <el-input v-model="editData.line_code" disabled />
        </el-form-item>
        <el-form-item label="产线名称" required>
          <el-input v-model="editData.line_name" placeholder="请输入产线名称" />
        </el-form-item>
        <el-form-item label="产线描述">
          <el-input v-model="editData.line_description" type="textarea" :rows="3" placeholder="请输入产线描述（可选）" />
        </el-form-item>
        <el-form-item label="数据类型">
          <el-select v-model="editData.data_type" placeholder="请选择数据类型" @change="handleEditDataTypeChange">
            <el-option label="计数型数据（属性数据）" value="attribute" />
            <el-option label="计量型数据（测量数据）" value="measurement" />
          </el-select>
          <div class="data-type-hint">
            <template v-if="editData.data_type === 'attribute'">
              <span class="hint-icon">💡</span> 计数型数据：通过图像检测统计缺陷数量，需要选择模型文件
            </template>
            <template v-else-if="editData.data_type === 'measurement'">
              <span class="hint-icon">💡</span> 计量型数据：通过测量仪器采集连续数值，无需模型文件
            </template>
          </div>
        </el-form-item>
        <el-form-item label="模型文件" v-if="editData.data_type === 'attribute'">
          <el-select v-model="editData.model_path" placeholder="请选择模型文件" clearable filterable>
            <el-option 
              v-for="file in modelFiles" 
              :key="file.filename" 
              :label="file.filename + ' (' + file.size_formatted + ')'" 
              :value="file.filename"
            />
          </el-select>
          <div class="form-hint">选择用于图像缺陷检测的AI模型文件</div>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="editData.status">
            <el-radio label="active">启用</el-radio>
            <el-radio label="inactive">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateLine" :loading="loading">保存</el-button>
      </template>
    </el-dialog>
    
    <el-dialog
      v-model="showDeleteDialog"
      title="确认删除"
      width="400px"
    >
      <p>确定要删除产线 <strong>{{ deleteTarget?.line_name }}</strong> 吗？</p>
      <p class="warning-text">此操作不可恢复，产线下的所有数据将被删除。</p>
      <template #footer>
        <el-button @click="showDeleteDialog = false">取消</el-button>
        <el-button type="danger" @click="deleteLine" :loading="loading">删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import Menu from '@/components/Menu.vue'
import { getProductionLines, createProductionLine, updateProductionLine, deleteProductionLine, getModelFiles } from '@/api'
import type { ProductionLine, ProductionLineCreate, ProductionLineUpdate } from '@/types'

const router = useRouter()

const lines = ref<ProductionLine[]>([])
const loading = ref(false)
const showCreateDialog = ref(false)
const showEditDialog = ref(false)
const showDeleteDialog = ref(false)
const deleteTarget = ref<ProductionLine | null>(null)

const formData = ref<ProductionLineCreate>({
  line_code: '',
  line_name: '',
  line_description: '',
  data_type: 'attribute',
  model_path: '',
  status: 'active'
})

const editData = ref<{
  id: number
  line_code: string
  line_name: string
  line_description: string
  data_type: 'measurement' | 'attribute'
  model_path?: string
  status: 'active' | 'inactive'
}>({
  id: 0,
  line_code: '',
    line_name: '',
    line_description: '',
    data_type: 'attribute',
    model_path: '',
    status: 'active'
})

const activeLines = computed(() => lines.value.filter(l => l.status === 'active').length)
const inactiveLines = computed(() => lines.value.filter(l => l.status === 'inactive').length)

const fetchLines = async () => {
  try {
    loading.value = true
    const response = await getProductionLines() as ProductionLine[]
    lines.value = response
  } catch (error) {
    console.error('获取产线失败:', error)
    ElMessage.error('获取产线失败')
  } finally {
    loading.value = false
  }
}

const modelFiles = ref<{ filename: string; path: string; size: number; size_formatted: string }[]>([])

const fetchModelFiles = async () => {
  try {
    const response = await getModelFiles()
    modelFiles.value = response.files
  } catch (error) {
    console.error('获取模型文件失败:', error)
  }
}

const handleDataTypeChange = (value: string) => {
  if (value === 'measurement') {
    formData.value.model_path = ''
  }
}

const handleEditDataTypeChange = (value: string) => {
  if (value === 'measurement') {
    editData.value.model_path = ''
  }
}

const createLine = async () => {
  if (!formData.value.line_code || !formData.value.line_name) {
    ElMessage.warning('请填写产线编号和名称')
    return
  }
  
  try {
    loading.value = true
    await createProductionLine(formData.value)
    ElMessage.success('创建成功')
    showCreateDialog.value = false
    formData.value = {
      line_code: '',
      line_name: '',
      line_description: '',
      data_type: 'attribute',
      model_path: '',
      status: 'active'
    }
    fetchLines()
  } catch (error: any) {
    console.error('创建产线失败:', error)
    ElMessage.error(error.detail || '创建失败')
  } finally {
    loading.value = false
  }
}

const editLine = (line: ProductionLine) => {
  editData.value = {
    id: line.id,
    line_code: line.line_code,
    line_name: line.line_name,
    line_description: line.line_description || '',
    data_type: line.data_type as 'measurement' | 'attribute',
    model_path: line.model_path || '',
    status: line.status as 'active' | 'inactive'
  }
  showEditDialog.value = true
}

const updateLine = async () => {
  if (!editData.value.line_name) {
    ElMessage.warning('请填写产线名称')
    return
  }
  
  try {
    loading.value = true
    const updateData: ProductionLineUpdate = {
      line_name: editData.value.line_name,
      line_description: editData.value.line_description,
      data_type: editData.value.data_type,
      model_path: editData.value.model_path,
      status: editData.value.status
    }
    await updateProductionLine(editData.value.id, updateData)
    ElMessage.success('更新成功')
    showEditDialog.value = false
    fetchLines()
  } catch (error: any) {
    console.error('更新产线失败:', error)
    ElMessage.error(error.detail || '更新失败')
  } finally {
    loading.value = false
  }
}

const confirmDelete = (line: ProductionLine) => {
  deleteTarget.value = line
  showDeleteDialog.value = true
}

const deleteLine = async () => {
  if (!deleteTarget.value) return
  
  try {
    loading.value = true
    await deleteProductionLine(deleteTarget.value.id)
    ElMessage.success('删除成功')
    showDeleteDialog.value = false
    deleteTarget.value = null
    fetchLines()
  } catch (error: any) {
    console.error('删除产线失败:', error)
    ElMessage.error(error.detail || '删除失败')
  } finally {
    loading.value = false
  }
}

const viewDetail = (line: ProductionLine) => {
  router.push(`/production-lines/${line.id}`)
}

const getDataTypeText = (type: string) => {
  const map: Record<string, string> = {
    measurement: '计量型数据',
    attribute: '计数型数据'
  }
  return map[type] || type
}

const formatTime = (time: string) => {
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

onMounted(() => {
  fetchLines()
  fetchModelFiles()
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

.btn-primary {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: var(--radius-sm);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-primary:hover {
  background: #00b8e6;
  transform: translateY(-1px);
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

.stat-icon.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success);
}

.stat-icon.warning {
  background: rgba(245, 158, 11, 0.1);
  color: var(--warning);
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

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 24px;
}

.line-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);
}

.line-card:hover {
  border-color: var(--accent-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.line-card.inactive {
  opacity: 0.7;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
}

.line-status {
  padding: 4px 12px;
  border-radius: 100px;
  font-family: var(--font-display);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}

.line-status.active {
  background: rgba(16, 185, 129, 0.15);
  color: var(--success);
}

.line-status.inactive {
  background: rgba(107, 114, 128, 0.15);
  color: var(--text-muted);
}

.card-actions {
  display: flex;
  gap: 8px;
}

.btn-icon-small {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-icon-small:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.btn-icon-small.danger:hover {
  border-color: var(--danger);
  color: var(--danger);
}

.card-body {
  padding: 20px;
  cursor: pointer;
}

.line-name {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.line-code {
  font-family: var(--font-mono);
  font-size: 0.875rem;
  color: var(--accent-primary);
  margin-bottom: 8px;
}

.line-desc {
  font-size: 0.875rem;
  color: var(--text-muted);
  margin-bottom: 16px;
  line-height: 1.5;
}

.line-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.card-footer {
  padding: 12px 20px;
  border-top: 1px solid var(--border-color);
}

.btn-link {
  display: flex;
  align-items: center;
  gap: 6px;
  background: none;
  border: none;
  color: var(--accent-primary);
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-link:hover {
  gap: 10px;
}

.empty-state {
  grid-column: 1 / -1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 40px;
  background: var(--bg-card);
  border: 1px dashed var(--border-color);
  border-radius: var(--radius-lg);
  color: var(--text-muted);
}

.empty-state svg {
  margin-bottom: 24px;
  opacity: 0.3;
}

.empty-state h3 {
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-state p {
  font-size: 0.875rem;
}

.warning-text {
  color: var(--danger);
  font-size: 0.875rem;
  margin-top: 8px;
}

.line-form :deep(.el-form-item__label) {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text-primary);
}

.line-form :deep(.el-input__wrapper),
.line-form :deep(.el-textarea__inner) {
  background: var(--bg-secondary);
  border-color: var(--border-color);
}

.line-form :deep(.el-select) {
  width: 100%;
}

.data-type-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background: rgba(0, 212, 255, 0.05);
  border: 1px solid rgba(0, 212, 255, 0.2);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: var(--text-secondary);
  line-height: 1.5;
}

.hint-icon {
  margin-right: 4px;
}

.form-hint {
  margin-top: 4px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

@media (max-width: 1200px) {
  .stats-row {
    grid-template-columns: 1fr;
  }
  
  .cards-grid {
    grid-template-columns: 1fr;
  }
}
</style>
