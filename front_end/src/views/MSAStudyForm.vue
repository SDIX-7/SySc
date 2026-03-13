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
            <h1 class="page-title">{{ isEdit ? '编辑MSA研究' : '新建MSA研究' }}</h1>
            <p class="page-subtitle">{{ isEdit ? '修改MSA研究信息和测量数据' : '创建新的测量系统分析研究' }}</p>
          </div>
        </div>
      </div>

      <div class="form-container">
        <el-form ref="formRef" :model="formData" :rules="formRules" label-position="top" class="msa-form">
          <div class="form-section">
            <h2 class="section-title">
              <span class="section-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
              </span>
              基本信息
            </h2>
            
            <div class="form-grid">
              <el-form-item label="研究名称" prop="study_name">
                <el-input v-model="formData.study_name" placeholder="请输入研究名称" />
              </el-form-item>
              
              <el-form-item label="研究类型" prop="study_type">
                <el-select v-model="formData.study_type" placeholder="请选择研究类型" style="width: 100%;">
                  <el-option label="GR&R (量具重复性和再现性)" value="grr" />
                  <el-option label="偏倚分析" value="bias" />
                  <el-option label="稳定性分析" value="stability" />
                  <el-option label="线性分析" value="linearity" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="关联产线">
                <el-select v-model="formData.line_id" placeholder="选择关联产线（可选）" clearable style="width: 100%;">
                  <el-option v-for="line in productionLines" :key="line.id" :label="line.line_name" :value="line.id" />
                </el-select>
              </el-form-item>
              
              <el-form-item label="测量系统">
                <el-input v-model="formData.measurement_system" placeholder="测量设备/量具名称" />
              </el-form-item>
              
              <el-form-item label="测量特性">
                <el-input v-model="formData.characteristic" placeholder="被测量的特性参数" />
              </el-form-item>
            </div>
          </div>

          <div class="form-section">
            <h2 class="section-title">
              <span class="section-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                </svg>
              </span>
              规格信息
            </h2>
            
            <div class="form-grid specs-grid">
              <el-form-item label="规格上限 (USL)">
                <el-input-number v-model="formData.specification_upper" :precision="4" placeholder="USL" style="width: 100%;" />
              </el-form-item>
              
              <el-form-item label="目标值 (Target)">
                <el-input-number v-model="formData.specification_target" :precision="4" placeholder="目标值" style="width: 100%;" />
              </el-form-item>
              
              <el-form-item label="规格下限 (LSL)">
                <el-input-number v-model="formData.specification_lower" :precision="4" placeholder="LSL" style="width: 100%;" />
              </el-form-item>
              
              <el-form-item label="公差">
                <el-input v-model="formData.tolerance" placeholder="自动计算或手动输入" />
              </el-form-item>
            </div>
          </div>

          <div class="form-section">
            <h2 class="section-title">
              <span class="section-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
              </span>
              研究设计
            </h2>
            
            <div class="design-info">
              <div class="design-item">
                <el-form-item label="零件数量" prop="number_of_parts">
                  <el-input-number v-model="formData.number_of_parts" :min="2" :max="20" @change="updateDesign" style="width: 100%;" />
                </el-form-item>
              </div>
              <div class="design-operator">×</div>
              <div class="design-item">
                <el-form-item label="操作员数量" prop="number_of_operators">
                  <el-input-number v-model="formData.number_of_operators" :min="2" :max="10" @change="updateDesign" style="width: 100%;" />
                </el-form-item>
              </div>
              <div class="design-operator">×</div>
              <div class="design-item">
                <el-form-item label="重复次数" prop="number_of_replicates">
                  <el-input-number v-model="formData.number_of_replicates" :min="2" :max="5" @change="updateDesign" style="width: 100%;" />
                </el-form-item>
              </div>
              <div class="design-operator">=</div>
              <div class="design-result">
                <span class="result-value">{{ totalMeasurements }}</span>
                <span class="result-label">测量次数</span>
              </div>
            </div>
            
            <el-form-item label="随机顺序">
              <el-switch v-model="formData.random_order" />
              <span class="form-hint">测量时是否随机化零件和操作员顺序</span>
            </el-form-item>
          </div>

          <div class="form-section">
            <h2 class="section-title">
              <span class="section-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="7" height="7"/>
                  <rect x="14" y="3" width="7" height="7"/>
                  <rect x="14" y="14" width="7" height="7"/>
                  <rect x="3" y="14" width="7" height="7"/>
                </svg>
              </span>
              零件管理
              <button type="button" class="btn-add" @click="addPart">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                添加零件
              </button>
            </h2>
            
            <div class="parts-table">
              <div class="table-header">
                <span class="col-number">编号</span>
                <span class="col-name">名称</span>
                <span class="col-ref">参考值</span>
                <span class="col-action">操作</span>
              </div>
              <div class="table-body">
                <div class="table-row" v-for="(part, index) in formData.parts" :key="index">
                  <span class="col-number">
                    <el-input v-model="part.part_number" placeholder="P1, P2..." size="small" />
                  </span>
                  <span class="col-name">
                    <el-input v-model="part.part_name" placeholder="零件名称" size="small" />
                  </span>
                  <span class="col-ref">
                    <el-input-number v-model="part.reference_value" :precision="4" placeholder="参考值" size="small" style="width: 100%;" />
                  </span>
                  <span class="col-action">
                    <button type="button" class="btn-remove" @click="removePart(index)" v-if="formData.parts.length > 2">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                      </svg>
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h2 class="section-title">
              <span class="section-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                  <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                  <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                </svg>
              </span>
              操作员管理
              <button type="button" class="btn-add" @click="addOperator">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="12" y1="5" x2="12" y2="19"/>
                  <line x1="5" y1="12" x2="19" y2="12"/>
                </svg>
                添加操作员
              </button>
            </h2>
            
            <div class="operators-table">
              <div class="table-header">
                <span class="col-id">工号</span>
                <span class="col-name">姓名</span>
                <span class="col-action">操作</span>
              </div>
              <div class="table-body">
                <div class="table-row" v-for="(op, index) in formData.operators" :key="index">
                  <span class="col-id">
                    <el-input v-model="op.operator_id" placeholder="OP001" size="small" />
                  </span>
                  <span class="col-name">
                    <el-input v-model="op.operator_name" placeholder="操作员姓名" size="small" />
                  </span>
                  <span class="col-action">
                    <button type="button" class="btn-remove" @click="removeOperator(index)" v-if="formData.operators.length > 2">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <polyline points="3 6 5 6 21 6"/>
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                      </svg>
                    </button>
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div class="form-section">
            <h2 class="section-title">
              <span class="section-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <line x1="3" y1="9" x2="21" y2="9"/>
                  <line x1="9" y1="21" x2="9" y2="9"/>
                </svg>
              </span>
              测量数据录入
            </h2>
            
            <div class="measurement-table-wrapper">
              <table class="measurement-table">
                <thead>
                  <tr>
                    <th rowspan="2" class="part-col">零件</th>
                    <th v-for="(op, opIndex) in formData.operators" :key="opIndex" :colspan="formData.number_of_replicates" class="operator-col">
                      {{ op.operator_name || `操作员${opIndex + 1}` }}
                    </th>
                  </tr>
                  <tr>
                    <template v-for="(op, opIndex) in formData.operators" :key="'sub-' + opIndex">
                      <th v-for="r in formData.number_of_replicates" :key="opIndex + '-' + r" class="replicate-col">
                        #{{ r }}
                      </th>
                    </template>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(part, partIndex) in formData.parts" :key="partIndex">
                    <td class="part-cell">
                      <span class="part-number">{{ part.part_number || `P${partIndex + 1}` }}</span>
                    </td>
                    <template v-for="(op, opIndex) in formData.operators" :key="partIndex + '-' + opIndex">
                      <td v-for="r in formData.number_of_replicates" :key="partIndex + '-' + opIndex + '-' + r" class="measurement-cell">
                        <el-input-number 
                          v-model="getMeasurement(partIndex, opIndex, r - 1).measurement_value"
                          :precision="4"
                          size="small"
                          placeholder="-"
                          controls-position="right"
                        />
                      </td>
                    </template>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div class="measurement-actions">
              <button type="button" class="btn-clear" @click="clearMeasurements">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"/>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                </svg>
                清空数据
              </button>
              <button type="button" class="btn-random" @click="fillRandomData">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                </svg>
                填充测试数据
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button type="button" class="btn-cancel" @click="goBack">取消</button>
            <button type="button" class="btn-save" @click="handleSave" :loading="saving">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              {{ isEdit ? '保存修改' : '创建研究' }}
            </button>
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import Menu from '@/components/Menu.vue'
import { getMSAStudy, createMSAStudy, updateMSAStudy, type MSAStudy, type MSAPart, type MSAOperator, type MSAMeasurement } from '@/api/msa'
import { getProductionLines, type ProductionLine } from '@/api'

const route = useRoute()
const router = useRouter()

const studyId = computed(() => Number(route.params.studyId))
const isEdit = computed(() => !!studyId.value && route.name === 'EditMSAStudy')

const formRef = ref<FormInstance>()
const saving = ref(false)
const productionLines = ref<ProductionLine[]>([])

interface MeasurementData {
  part_index: number
  operator_index: number
  replicate: number
  measurement_value: number | undefined
}

const formData = ref({
  study_name: '',
  study_type: 'grr',
  line_id: undefined as number | undefined,
  measurement_system: '',
  characteristic: '',
  specification_upper: undefined as number | undefined,
  specification_lower: undefined as number | undefined,
  specification_target: undefined as number | undefined,
  tolerance: '',
  number_of_parts: 10,
  number_of_operators: 3,
  number_of_replicates: 2,
  random_order: true,
  parts: [] as MSAPart[],
  operators: [] as MSAOperator[],
  measurements: [] as MeasurementData[]
})

const formRules: FormRules = {
  study_name: [
    { required: true, message: '请输入研究名称', trigger: 'blur' }
  ],
  study_type: [
    { required: true, message: '请选择研究类型', trigger: 'change' }
  ],
  number_of_parts: [
    { required: true, message: '请设置零件数量', trigger: 'change' }
  ],
  number_of_operators: [
    { required: true, message: '请设置操作员数量', trigger: 'change' }
  ],
  number_of_replicates: [
    { required: true, message: '请设置重复次数', trigger: 'change' }
  ]
}

const totalMeasurements = computed(() => {
  return formData.value.number_of_parts * formData.value.number_of_operators * formData.value.number_of_replicates
})

const getMeasurement = (partIndex: number, operatorIndex: number, replicate: number) => {
  let meas = formData.value.measurements.find(m => 
    m.part_index === partIndex && 
    m.operator_index === operatorIndex && 
    m.replicate === replicate
  )
  
  if (!meas) {
    meas = {
      part_index: partIndex,
      operator_index: operatorIndex,
      replicate: replicate,
      measurement_value: undefined
    }
    formData.value.measurements.push(meas)
  }
  
  return meas
}

const updateDesign = () => {
  const partsCount = formData.value.number_of_parts
  const operatorsCount = formData.value.number_of_operators
  
  while (formData.value.parts.length < partsCount) {
    formData.value.parts.push({
      part_number: `P${formData.value.parts.length + 1}`,
      part_name: '',
      reference_value: undefined
    })
  }
  while (formData.value.parts.length > partsCount) {
    formData.value.parts.pop()
  }
  
  while (formData.value.operators.length < operatorsCount) {
    formData.value.operators.push({
      operator_id: `OP${String(formData.value.operators.length + 1).padStart(3, '0')}`,
      operator_name: `操作员${formData.value.operators.length + 1}`
    })
  }
  while (formData.value.operators.length > operatorsCount) {
    formData.value.operators.pop()
  }
}

const addPart = () => {
  formData.value.number_of_parts++
  formData.value.parts.push({
    part_number: `P${formData.value.parts.length + 1}`,
    part_name: '',
    reference_value: undefined
  })
}

const removePart = (index: number) => {
  formData.value.parts.splice(index, 1)
  formData.value.number_of_parts--
  formData.value.parts.forEach((p, i) => {
    p.part_number = `P${i + 1}`
  })
}

const addOperator = () => {
  formData.value.number_of_operators++
  formData.value.operators.push({
    operator_id: `OP${String(formData.value.operators.length + 1).padStart(3, '0')}`,
    operator_name: `操作员${formData.value.operators.length + 1}`
  })
}

const removeOperator = (index: number) => {
  formData.value.operators.splice(index, 1)
  formData.value.number_of_operators--
}

const clearMeasurements = () => {
  formData.value.measurements = []
}

const fillRandomData = () => {
  const baseValue = formData.value.specification_target || 50
  const variation = 2
  
  formData.value.measurements = []
  
  for (let p = 0; p < formData.value.number_of_parts; p++) {
    const partValue = baseValue + (Math.random() - 0.5) * 10
    for (let o = 0; o < formData.value.number_of_operators; o++) {
      for (let r = 0; r < formData.value.number_of_replicates; r++) {
        const noise = (Math.random() - 0.5) * variation
        formData.value.measurements.push({
          part_index: p,
          operator_index: o,
          replicate: r,
          measurement_value: parseFloat((partValue + noise).toFixed(4))
        })
      }
    }
  }
  
  ElMessage.success('已填充测试数据')
}

const fetchStudy = async () => {
  if (!isEdit.value) return
  
  try {
    const res = await getMSAStudy(studyId.value)
    const study = res.data || res
    
    formData.value = {
      study_name: study.study_name,
      study_type: study.study_type,
      line_id: study.line_id,
      measurement_system: study.measurement_system || '',
      characteristic: study.characteristic || '',
      specification_upper: study.specification_upper ? parseFloat(study.specification_upper) : undefined,
      specification_lower: study.specification_lower ? parseFloat(study.specification_lower) : undefined,
      specification_target: study.specification_target ? parseFloat(study.specification_target) : undefined,
      tolerance: study.tolerance || '',
      number_of_parts: study.number_of_parts,
      number_of_operators: study.number_of_operators,
      number_of_replicates: study.number_of_replicates,
      random_order: study.random_order,
      parts: study.parts || [],
      operators: study.operators || [],
      measurements: []
    }
    
    if (study.measurements) {
      study.measurements.forEach((m: MSAMeasurement) => {
        const partIndex = formData.value.parts.findIndex(p => p.id === m.part_id)
        const opIndex = formData.value.operators.findIndex(o => o.id === m.operator_id)
        if (partIndex >= 0 && opIndex >= 0) {
          formData.value.measurements.push({
            part_index: partIndex,
            operator_index: opIndex,
            replicate: m.replicate - 1,
            measurement_value: parseFloat(m.measurement_value)
          })
        }
      })
    }
  } catch (error) {
    console.error('获取MSA研究失败:', error)
    ElMessage.error('获取MSA研究失败')
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

const handleSave = async () => {
  if (!formRef.value) return
  
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    
    saving.value = true
    
    try {
      const measurements: MSAMeasurement[] = formData.value.measurements
        .filter(m => m.measurement_value !== undefined)
        .map(m => ({
          part_id: formData.value.parts[m.part_index].id || 0,
          operator_id: formData.value.operators[m.operator_index].id || 0,
          replicate: m.replicate + 1,
          measurement_value: String(m.measurement_value)
        }))
      
      const data: any = {
        study_name: formData.value.study_name,
        study_type: formData.value.study_type,
        line_id: formData.value.line_id,
        measurement_system: formData.value.measurement_system,
        characteristic: formData.value.characteristic,
        specification_upper: formData.value.specification_upper ? String(formData.value.specification_upper) : undefined,
        specification_lower: formData.value.specification_lower ? String(formData.value.specification_lower) : undefined,
        specification_target: formData.value.specification_target ? String(formData.value.specification_target) : undefined,
        tolerance: formData.value.tolerance,
        number_of_parts: formData.value.number_of_parts,
        number_of_operators: formData.value.number_of_operators,
        number_of_replicates: formData.value.number_of_replicates,
        random_order: formData.value.random_order,
        parts: formData.value.parts,
        operators: formData.value.operators,
        measurements: measurements
      }
      
      if (isEdit.value) {
        await updateMSAStudy(studyId.value, data)
        ElMessage.success('保存成功')
      } else {
        await createMSAStudy(data)
        ElMessage.success('创建成功')
      }
      
      router.push('/msa-studies')
    } catch (error: any) {
      console.error('保存失败:', error)
      ElMessage.error(error.message || '保存失败')
    } finally {
      saving.value = false
    }
  })
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  fetchProductionLines()
  updateDesign()
  
  if (isEdit.value) {
    fetchStudy()
  }
})

watch(() => formData.value.specification_upper, (val) => {
  if (val && formData.value.specification_lower) {
    formData.value.tolerance = String(val - formData.value.specification_lower)
  }
})

watch(() => formData.value.specification_lower, (val) => {
  if (val && formData.value.specification_upper) {
    formData.value.tolerance = String(formData.value.specification_upper - val)
  }
})
</script>

<style scoped>
.page-content {
  padding: 40px;
  max-width: 1200px;
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

.form-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.form-section:last-of-type {
  border-bottom: none;
  margin-bottom: 0;
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

.btn-add {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-left: auto;
  padding: 6px 12px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-sm);
  color: #10b981;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-add:hover {
  background: rgba(16, 185, 129, 0.2);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.specs-grid {
  grid-template-columns: repeat(4, 1fr);
}

.design-info {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  margin-bottom: 20px;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
}

.design-item {
  flex: 1;
}

.design-operator {
  font-family: var(--font-display);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 20px;
}

.design-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16px 24px;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-md);
}

.result-value {
  font-family: var(--font-mono);
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent-primary);
}

.result-label {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.form-hint {
  margin-left: 12px;
  font-size: 0.75rem;
  color: var(--text-muted);
}

.parts-table,
.operators-table {
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 100px 1fr 150px 60px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.operators-table .table-header {
  grid-template-columns: 120px 1fr 60px;
}

.table-body {
  max-height: 300px;
  overflow-y: auto;
}

.table-row {
  display: grid;
  grid-template-columns: 100px 1fr 150px 60px;
  padding: 8px 16px;
  border-top: 1px solid var(--border-color);
  align-items: center;
}

.operators-table .table-row {
  grid-template-columns: 120px 1fr 60px;
}

.col-action {
  text-align: center;
}

.btn-remove {
  width: 28px;
  height: 28px;
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

.btn-remove:hover {
  border-color: #ef4444;
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

.measurement-table-wrapper {
  overflow-x: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
}

.measurement-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.measurement-table th,
.measurement-table td {
  padding: 8px;
  border: 1px solid var(--border-color);
  text-align: center;
}

.measurement-table th {
  background: var(--bg-secondary);
  font-weight: 600;
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.measurement-table .part-col {
  background: var(--bg-secondary);
  text-align: left;
  min-width: 80px;
}

.measurement-table .operator-col {
  background: rgba(0, 212, 255, 0.05);
}

.measurement-table .replicate-col {
  font-weight: 400;
  font-size: 0.7rem;
}

.measurement-table .part-cell {
  text-align: left;
}

.part-number {
  font-weight: 500;
  font-family: var(--font-mono);
}

.measurement-cell {
  min-width: 100px;
}

.measurement-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-clear, .btn-random {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-clear {
  background: transparent;
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

.btn-clear:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.btn-random {
  background: rgba(139, 92, 246, 0.1);
  border: 1px solid rgba(139, 92, 246, 0.3);
  color: #8b5cf6;
}

.btn-random:hover {
  background: rgba(139, 92, 246, 0.2);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  padding: 12px 24px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-cancel:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.btn-save {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  background: linear-gradient(135deg, var(--accent-primary), #0284c7);
  border: none;
  border-radius: var(--radius-sm);
  color: white;
  font-family: var(--font-display);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 212, 255, 0.3);
}

@media (max-width: 900px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .specs-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .design-info {
    flex-wrap: wrap;
  }
}
</style>
