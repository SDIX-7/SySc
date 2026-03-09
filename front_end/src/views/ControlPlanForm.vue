<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <div class="breadcrumb">
            <router-link to="/control-plans">控制计划</router-link>
            <span class="separator">/</span>
            <span class="current">{{ isEdit ? '编辑控制计划' : '创建控制计划' }}</span>
          </div>
          <h1 class="page-title">{{ isEdit ? '编辑控制计划' : '创建控制计划' }}</h1>
        </div>
        <div class="header-right">
          <el-button @click="router.back()">取消</el-button>
          <el-button type="primary" @click="savePlan" :loading="loading">保存</el-button>
        </div>
      </div>
      
      <div class="form-container">
        <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" class="plan-form">
          <div class="form-section">
            <h3 class="section-title">基本信息</h3>
            <div class="form-grid">
              <el-form-item label="产线" prop="line_id">
                <el-select v-model="formData.line_id" placeholder="请选择产线" style="width: 100%" :loading="linesLoading">
                  <el-option 
                    v-for="line in productionLines" 
                    :key="line.id" 
                    :label="`${line.line_name} (${line.line_code})`" 
                    :value="line.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="计划类型" prop="plan_type">
                <el-select v-model="formData.plan_type" style="width: 100%">
                  <el-option label="原型样件" value="prototype" />
                  <el-option label="试生产" value="pre-launch" />
                  <el-option label="生产" value="production" />
                </el-select>
              </el-form-item>
              <el-form-item label="控制计划编号" prop="control_plan_number">
                <el-input v-model="formData.control_plan_number" placeholder="请输入控制计划编号" />
              </el-form-item>
              <el-form-item label="零件号" prop="part_number">
                <el-input v-model="formData.part_number" placeholder="请输入零件号" />
              </el-form-item>
              <el-form-item label="零件名称" prop="part_name">
                <el-input v-model="formData.part_name" placeholder="请输入零件名称" />
              </el-form-item>
              <el-form-item label="零件描述">
                <el-input v-model="formData.part_description" type="textarea" :rows="2" placeholder="请输入零件描述" />
              </el-form-item>
              <el-form-item label="最新变更级别">
                <el-input v-model="formData.latest_change_level" placeholder="请输入最新变更级别" />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">组织信息</h3>
            <div class="form-grid">
              <el-form-item label="组织/工厂">
                <el-input v-model="formData.organization_plant" placeholder="请输入组织/工厂" />
              </el-form-item>
              <el-form-item label="组织代码">
                <el-input v-model="formData.organization_code" placeholder="请输入组织代码" />
              </el-form-item>
              <el-form-item label="关键联系人">
                <el-input v-model="formData.key_contact" placeholder="请输入关键联系人" />
              </el-form-item>
              <el-form-item label="联系电话">
                <el-input v-model="formData.key_contact_phone" placeholder="请输入联系电话" />
              </el-form-item>
              <el-form-item label="核心团队">
                <el-input v-model="formData.core_team" type="textarea" :rows="2" placeholder="请输入核心团队成员" />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">审批信息</h3>
            <div class="form-grid">
              <el-form-item label="组织批准日期">
                <el-date-picker v-model="formData.org_approval_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="组织批准人">
                <el-input v-model="formData.org_approval_by" placeholder="请输入组织批准人" />
              </el-form-item>
              <el-form-item label="其他批准日期">
                <el-date-picker v-model="formData.other_approval_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="其他批准人">
                <el-input v-model="formData.other_approval_by" placeholder="请输入其他批准人" />
              </el-form-item>
              <el-form-item label="客户工程批准日期">
                <el-date-picker v-model="formData.customer_eng_approval_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="客户工程批准人">
                <el-input v-model="formData.customer_eng_approval_by" placeholder="请输入客户工程批准人" />
              </el-form-item>
              <el-form-item label="客户质量批准日期">
                <el-date-picker v-model="formData.customer_quality_approval_date" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="客户质量批准人">
                <el-input v-model="formData.customer_quality_approval_by" placeholder="请输入客户质量批准人" />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">版本信息</h3>
            <div class="form-grid">
              <el-form-item label="原始日期">
                <el-date-picker v-model="formData.date_orig" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="修订日期">
                <el-date-picker v-model="formData.date_rev" type="date" style="width: 100%" value-format="YYYY-MM-DD" />
              </el-form-item>
              <el-form-item label="页码">
                <el-input-number v-model="formData.page_number" :min="1" style="width: 100%" />
              </el-form-item>
              <el-form-item label="总页数">
                <el-input-number v-model="formData.total_pages" :min="1" style="width: 100%" />
              </el-form-item>
              <el-form-item label="版本">
                <el-input v-model="formData.version" placeholder="如 1.0" />
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="formData.status" style="width: 100%">
                  <el-option label="草稿" value="draft" />
                  <el-option label="已批准" value="approved" />
                  <el-option label="激活" value="active" />
                  <el-option label="已废弃" value="obsolete" />
                </el-select>
              </el-form-item>
              <el-form-item label="创建人">
                <el-input v-model="formData.created_by" placeholder="请输入创建人" />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">控制计划项目</h3>
              <el-button type="primary" size="small" @click="addItem">添加项目</el-button>
            </div>
            
            <div v-if="formData.items && formData.items.length > 0" class="items-table">
              <el-table :data="formData.items" border stripe>
                <el-table-column type="index" label="序号" width="60" />
                <el-table-column prop="part_process_number" label="过程编号" width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.part_process_number" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="process_name" label="过程名称" width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.process_name" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="operation_description" label="作业描述" min-width="150">
                  <template #default="{ row }">
                    <el-input v-model="row.operation_description" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="characteristic_no" label="特性编号" width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.characteristic_no" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="product_characteristic" label="产品特性" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.product_characteristic" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="specification_tolerance" label="规格/公差" width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.specification_tolerance" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="sample_size" label="样本容量" width="90">
                  <template #default="{ row }">
                    <el-input v-model="row.sample_size" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="sample_frequency" label="样本频率" width="100">
                  <template #default="{ row }">
                    <el-input v-model="row.sample_frequency" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="control_method" label="控制方法" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.control_method" size="small" />
                  </template>
                </el-table-column>
                <el-table-column prop="reaction_plan" label="反应计划" min-width="120">
                  <template #default="{ row }">
                    <el-input v-model="row.reaction_plan" size="small" />
                  </template>
                </el-table-column>
                <el-table-column label="操作" width="80" fixed="right">
                  <template #default="{ $index }">
                    <el-button type="danger" size="small" link @click="removeItem($index)">
                      <el-icon><Delete /></el-icon>
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
            <el-empty v-else description="暂无控制计划项目，点击上方按钮添加" />
          </div>
        </el-form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Delete } from '@element-plus/icons-vue'
import Menu from '@/components/Menu.vue'
import { getControlPlan, createControlPlan, updateControlPlan } from '@/api/controlPlan'
import { getProductionLines } from '@/api'
import type { ControlPlanCreate, ControlPlanItemCreate, ProductionLine } from '@/types'

const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const planId = computed(() => Number(route.params.planId))
const isEdit = computed(() => !!planId.value && route.name === 'EditControlPlan')
const loading = ref(false)
const linesLoading = ref(false)
const productionLines = ref<ProductionLine[]>([])

const formData = reactive<ControlPlanCreate & { items: ControlPlanItemCreate[] }>({
  line_id: undefined as unknown as number,
  plan_type: 'production',
  control_plan_number: '',
  part_number: '',
  part_name: '',
  part_description: '',
  latest_change_level: '',
  organization_plant: '',
  organization_code: '',
  key_contact: '',
  key_contact_phone: '',
  core_team: '',
  org_approval_date: '',
  org_approval_by: '',
  other_approval_date: '',
  other_approval_by: '',
  customer_eng_approval_date: '',
  customer_eng_approval_by: '',
  customer_quality_approval_date: '',
  customer_quality_approval_by: '',
  date_orig: '',
  date_rev: '',
  page_number: 1,
  total_pages: 1,
  version: '1.0',
  status: 'draft',
  created_by: '',
  items: []
})

const rules = reactive<FormRules>({
  line_id: [
    { required: true, message: '请选择产线', trigger: 'change' }
  ],
  plan_type: [
    { required: true, message: '请选择计划类型', trigger: 'change' }
  ],
  control_plan_number: [
    { required: true, message: '请输入控制计划编号', trigger: 'blur' }
  ],
  part_number: [
    { required: true, message: '请输入零件号', trigger: 'blur' }
  ],
  part_name: [
    { required: true, message: '请输入零件名称', trigger: 'blur' }
  ]
})

const fetchProductionLines = async () => {
  try {
    linesLoading.value = true
    const response = await getProductionLines() as any
    productionLines.value = response || []
  } catch (error) {
    console.error('获取产线列表失败:', error)
  } finally {
    linesLoading.value = false
  }
}

const fetchControlPlan = async () => {
  if (!isEdit.value) return
  
  try {
    loading.value = true
    const response = await getControlPlan(planId.value) as any
    
    Object.assign(formData, {
      line_id: response.line_id,
      plan_type: response.plan_type,
      control_plan_number: response.control_plan_number,
      part_number: response.part_number,
      part_name: response.part_name,
      part_description: response.part_description,
      latest_change_level: response.latest_change_level,
      organization_plant: response.organization_plant,
      organization_code: response.organization_code,
      key_contact: response.key_contact,
      key_contact_phone: response.key_contact_phone,
      core_team: response.core_team,
      org_approval_date: response.org_approval_date,
      org_approval_by: response.org_approval_by,
      other_approval_date: response.other_approval_date,
      other_approval_by: response.other_approval_by,
      customer_eng_approval_date: response.customer_eng_approval_date,
      customer_eng_approval_by: response.customer_eng_approval_by,
      customer_quality_approval_date: response.customer_quality_approval_date,
      customer_quality_approval_by: response.customer_quality_approval_by,
      date_orig: response.date_orig,
      date_rev: response.date_rev,
      page_number: response.page_number || 1,
      total_pages: response.total_pages || 1,
      version: response.version,
      status: response.status,
      created_by: response.created_by,
      items: (response.items || []).map((item: any) => ({
        part_process_number: item.part_process_number,
        process_name: item.process_name,
        operation_description: item.operation_description,
        machine_device_jig_tools: item.machine_device_jig_tools,
        characteristic_no: item.characteristic_no,
        product_characteristic: item.product_characteristic,
        process_characteristic: item.process_characteristic,
        special_characteristics_class: item.special_characteristics_class,
        specification_tolerance: item.specification_tolerance,
        evaluation_measurement_technique: item.evaluation_measurement_technique,
        sample_size: item.sample_size,
        sample_frequency: item.sample_frequency,
        control_method: item.control_method,
        reaction_plan: item.reaction_plan,
        sort_order: item.sort_order
      }))
    })
  } catch (error) {
    console.error('获取控制计划失败:', error)
    ElMessage.error('获取控制计划失败')
  } finally {
    loading.value = false
  }
}

const addItem = () => {
  formData.items.push({
    part_process_number: '',
    process_name: '',
    operation_description: '',
    machine_device_jig_tools: '',
    characteristic_no: '',
    product_characteristic: '',
    process_characteristic: '',
    special_characteristics_class: '',
    specification_tolerance: '',
    evaluation_measurement_technique: '',
    sample_size: '',
    sample_frequency: '',
    control_method: '',
    reaction_plan: '',
    sort_order: formData.items.length + 1
  })
}

const removeItem = (index: number) => {
  formData.items.splice(index, 1)
  formData.items.forEach((item, i) => {
    item.sort_order = i + 1
  })
}

const savePlan = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
  } catch (error) {
    return
  }
  
  try {
    loading.value = true
    
    const submitData = { ...formData }
    
    if (isEdit.value) {
      await updateControlPlan(planId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await createControlPlan(submitData)
      ElMessage.success('创建成功')
    }
    
    router.push('/control-plans')
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error.detail || '保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProductionLines()
  fetchControlPlan()
})
</script>

<style scoped>
.page-content {
  padding: 40px;
  max-width: 1400px;
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
  gap: 8px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
}

.breadcrumb a {
  color: var(--accent-primary);
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.breadcrumb .separator {
  color: var(--text-muted);
}

.breadcrumb .current {
  color: var(--text-primary);
}

.page-title {
  font-family: var(--font-display);
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.05em;
}

.header-right {
  display: flex;
  gap: 12px;
}

.form-container {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 32px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section:last-child {
  margin-bottom: 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.section-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.section-header .section-title {
  margin: 0;
  padding: 0;
  border: none;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.items-table {
  margin-top: 16px;
}

.plan-form :deep(.el-form-item__label) {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text-primary);
}

.plan-form :deep(.el-input__wrapper),
.plan-form :deep(.el-textarea__inner) {
  background: var(--bg-secondary);
  border-color: var(--border-color);
}

.plan-form :deep(.el-table) {
  --el-table-bg-color: var(--bg-secondary);
  --el-table-tr-bg-color: var(--bg-secondary);
  --el-table-header-bg-color: var(--bg-card);
}

@media (max-width: 1200px) {
  .form-container {
    padding: 24px;
  }
  
  .header-right {
    flex-wrap: wrap;
  }
}

@media (max-width: 768px) {
  .page-content {
    padding: 16px;
  }
  
  .page-title {
    font-size: 1.5rem;
  }
  
  .form-container {
    padding: 16px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .form-actions button {
    width: 100%;
  }
}
</style>
