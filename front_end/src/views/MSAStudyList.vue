<template>
  <div class="msa-study-list">
    <div class="page-header">
      <h2>测量系统分析(MSA)研究</h2>
      <el-button type="primary" @click="handleCreate">新建MSA研究</el-button>
    </div>

    <el-card>
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="产线">
          <el-select v-model="queryParams.line_id" placeholder="选择产线" clearable @change="handleQuery">
            <el-option v-for="line in productionLines" :key="line.id" :label="line.line_name" :value="line.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="研究类型">
          <el-select v-model="queryParams.study_type" placeholder="选择类型" clearable @change="handleQuery">
            <el-option label="GR&R" value="grr" />
            <el-option label="偏倚" value="bias" />
            <el-option label="稳定性" value="stability" />
            <el-option label="线性" value="linearity" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="选择状态" clearable @change="handleQuery">
            <el-option label="草稿" value="draft" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="msaStudies" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="study_name" label="研究名称" min-width="180" />
        <el-table-column prop="study_type" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getStudyTypeTag(row.study_type)">{{ getStudyTypeLabel(row.study_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ getStatusLabel(row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="characteristic" label="测量特性" min-width="120" />
        <el-table-column prop="number_of_parts" label="零件数" width="80" />
        <el-table-column prop="number_of_operators" label="操作员" width="80" />
        <el-table-column prop="number_of_replicates" label="重复次数" width="90" />
        <el-table-column prop="percent_grr" label="%GR&R" width="90">
          <template #default="{ row }">
            <span v-if="row.result && row.result.percent_grr">{{ row.result.percent_grr }}%</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="ndc" label="NDC" width="80">
          <template #default="{ row }">
            <span v-if="row.result && row.result.ndc">{{ row.result.ndc }}</span>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="overall_acceptance" label="判定" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.result && row.result.overall_acceptance" :type="getAcceptanceTag(row.result.overall_acceptance)">
              {{ getAcceptanceLabel(row.result.overall_acceptance) }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleView(row)">查看</el-button>
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="success" link @click="handleCalculate(row)" v-if="row.status !== 'completed'">计算</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter from 'vue-router, useRoute }'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getMSAStudies, deleteMSAStudy, calculateMSA, type MSAStudy } from '@/api/msa'
import { getProductionLines, type ProductionLine } from '@/api'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const msaStudies = ref<MSAStudy[]>([])
const productionLines = ref<ProductionLine[]>([])

const queryParams = ref({
  line_id: undefined as number | undefined,
  study_type: undefined as string | undefined,
  status: undefined as string | undefined
})

const getStudyTypeLabel = (type: string) => {
  const map: Record<string, string> = {
    grr: 'GR&R',
    bias: '偏倚',
    stability: '稳定性',
    linearity: '线性'
  }
  return map[type] || type
}

const getStudyTypeTag = (type: string) => {
  const map: Record<string, string> = {
    grr: 'primary',
    bias: 'success',
    stability: 'warning',
    linearity: 'info'
  }
  return map[type] || 'info'
}

const getStatusLabel = (status: string) => {
  const map: Record<string, string> = {
    draft: '草稿',
    in_progress: '进行中',
    completed: '已完成'
  }
  return map[status] || status
}

const getStatusTag = (status: string) => {
  const map: Record<string, string> = {
    draft: 'info',
    in_progress: 'warning',
    completed: 'success'
  }
  return map[status] || 'info'
}

const getAcceptanceLabel = (acceptance: string) => {
  const map: Record<string, string> = {
    acceptable: '接受',
    conditional: '条件接受',
    unacceptable: '不接受'
  }
  return map[acceptance] || acceptance
}

const getAcceptanceTag = (acceptance: string) => {
  const map: Record<string, string> = {
    acceptable: 'success',
    conditional: 'warning',
    unacceptable: 'danger'
  }
  return map[acceptance] || 'info'
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const fetchMSAStudies = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (queryParams.value.line_id) params.line_id = queryParams.value.line_id
    if (queryParams.value.study_type) params.study_type = queryParams.value.study_type
    if (queryParams.value.status) params.status = queryParams.value.status
    
    const res = await getMSAStudies(params)
    msaStudies.value = res.data || []
  } catch (error) {
    console.error('获取MSA研究失败:', error)
  } finally {
    loading.value = false
  }
}

const fetchProductionLines = async () => {
  try {
    const res = await getProductionLines()
    productionLines.value = res.data || []
  } catch (error) {
    console.error('获取产线失败:', error)
  }
}

const handleQuery = () => {
  fetchMSAStudies()
}

const handleReset = () => {
  queryParams.value = {
    line_id: undefined,
    study_type: undefined,
    status: undefined
  }
  fetchMSAStudies()
}

const handleCreate = () => {
  router.push('/msa-studies/new')
}

const handleView = (row: MSAStudy) => {
  router.push(`/msa-studies/${row.id}`)
}

const handleEdit = (row: MSAStudy) => {
  router.push(`/msa-studies/${row.id}/edit`)
}

const handleCalculate = async (row: MSAStudy) => {
  try {
    await ElMessageBox.confirm('确认执行GR&R计算？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'info'
    })
    
    const res = await calculateMSA(row.id!)
    ElMessage.success(res.message || '计算完成')
    fetchMSAStudies()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '计算失败')
    }
  }
}

const handleDelete = async (row: MSAStudy) => {
  try {
    await ElMessageBox.confirm('确认删除该MSA研究？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await deleteMSAStudy(row.id!)
    ElMessage.success('删除成功')
    fetchMSAStudies()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

onMounted(() => {
  fetchProductionLines()
  
  if (route.params.lineId) {
    queryParams.value.line_id = Number(route.params.lineId)
  }
  
  fetchMSAStudies()
})
</script>

<style scoped>
.msa-study-list {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.search-form {
  margin-bottom: 20px;
}
</style>
