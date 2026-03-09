<template>
  <div class="page-container">
    <Menu />
    
    <div class="page-content">
      <div class="page-header">
        <div class="header-left">
          <div class="breadcrumb">
            <router-link to="/ocaps">OCAP</router-link>
            <span class="separator">/</span>
            <span class="current">{{ isEdit ? '编辑OCAP' : '创建OCAP' }}</span>
          </div>
          <h1 class="page-title">{{ isEdit ? '编辑OCAP' : '创建OCAP' }}</h1>
        </div>
        <div class="header-right">
          <el-button @click="router.back()">取消</el-button>
          <el-button type="primary" @click="saveOcap" :loading="loading">保存</el-button>
        </div>
      </div>
      
      <div class="form-container">
        <el-form ref="formRef" :model="formData" :rules="rules" label-position="top" class="ocap-form">
          <div class="form-section">
            <h3 class="section-title">基本信息</h3>
            <div class="form-grid">
              <el-form-item label="OCAP名称" prop="name">
                <el-input v-model="formData.name" placeholder="请输入OCAP名称" maxlength="200" show-word-limit />
              </el-form-item>
              <el-form-item label="状态">
                <el-select v-model="formData.status" style="width: 100%">
                  <el-option label="草稿" value="draft" />
                  <el-option label="激活" value="active" />
                  <el-option label="执行中" value="executing" />
                  <el-option label="已完成" value="completed" />
                  <el-option label="已关闭" value="closed" />
                </el-select>
              </el-form-item>
              <el-form-item label="描述">
                <el-input v-model="formData.description" type="textarea" :rows="3" placeholder="请输入OCAP描述" maxlength="2000" show-word-limit />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">信号信息</h3>
            <div class="form-grid">
              <el-form-item label="信号类型">
                <el-select v-model="formData.signal_type" style="width: 100%" clearable placeholder="请选择信号类型">
                  <el-option label="点超出3σ控制限" value="point_beyond_3sigma" />
                  <el-option label="连续9点在中心线一侧" value="run_9" />
                  <el-option label="连续6点递增或递减" value="trend_6" />
                  <el-option label="连续3点中有2点在A区或之外" value="zone_2of3" />
                  <el-option label="连续5点中有4点在B区或之外" value="zone_4of5" />
                  <el-option label="连续8点在中心线两侧但无一在C区" value="run_8" />
                  <el-option label="连续14点上下交替" value="run_14" />
                  <el-option label="连续15点在C区" value="run_15" />
                </el-select>
              </el-form-item>
              <el-form-item label="优先级">
                <el-select v-model="formData.priority" style="width: 100%">
                  <el-option label="紧急" value="critical">
                    <span class="priority-option">
                      <el-tag type="danger" size="small">紧急</el-tag>
                    </span>
                  </el-option>
                  <el-option label="高" value="high">
                    <span class="priority-option">
                      <el-tag type="warning" size="small">高</el-tag>
                    </span>
                  </el-option>
                  <el-option label="中" value="medium">
                    <span class="priority-option">
                      <el-tag type="info" size="small">中</el-tag>
                    </span>
                  </el-option>
                  <el-option label="低" value="low">
                    <span class="priority-option">
                      <el-tag size="small">低</el-tag>
                    </span>
                  </el-option>
                </el-select>
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">优先级评分</h3>
            <div class="priority-scores">
              <div class="score-item">
                <el-form-item label="严重性评分">
                  <div class="score-slider">
                    <el-slider v-model="formData.severity_score" :min="1" :max="10" :marks="scoreMarks" />
                    <el-tag :type="getSeverityTagType(formData.severity_score)" size="small">
                      {{ formData.severity_score }}
                    </el-tag>
                  </div>
                </el-form-item>
              </div>
              <div class="score-item">
                <el-form-item label="范围评分">
                  <div class="score-slider">
                    <el-slider v-model="formData.scope_score" :min="1" :max="10" :marks="scoreMarks" />
                    <el-tag :type="getSeverityTagType(formData.scope_score)" size="small">
                      {{ formData.scope_score }}
                    </el-tag>
                  </div>
                </el-form-item>
              </div>
              <div class="score-item">
                <el-form-item label="趋势评分">
                  <div class="score-slider">
                    <el-slider v-model="formData.trend_score" :min="1" :max="10" :marks="scoreMarks" />
                    <el-tag :type="getSeverityTagType(formData.trend_score)" size="small">
                      {{ formData.trend_score }}
                    </el-tag>
                  </div>
                </el-form-item>
              </div>
              <div class="score-item">
                <el-form-item label="综合优先级评分">
                  <div class="score-slider">
                    <el-slider v-model="formData.overall_priority_score" :min="1" :max="10" :marks="scoreMarks" />
                    <el-tag :type="getSeverityTagType(formData.overall_priority_score)" size="small">
                      {{ formData.overall_priority_score }}
                    </el-tag>
                  </div>
                </el-form-item>
              </div>
            </div>
          </div>
          
          <div class="form-section">
            <h3 class="section-title">关联信息</h3>
            <div class="form-grid">
              <el-form-item label="产线">
                <el-select v-model="formData.line_id" placeholder="请选择产线" style="width: 100%" clearable :loading="linesLoading">
                  <el-option 
                    v-for="line in productionLines" 
                    :key="line.id" 
                    :label="`${line.line_name} (${line.line_code})`" 
                    :value="line.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="控制图配置">
                <el-select v-model="formData.control_chart_config_id" placeholder="请选择控制图配置" style="width: 100%" clearable :loading="configsLoading">
                  <el-option 
                    v-for="config in controlChartConfigs" 
                    :key="config.id" 
                    :label="`配置 #${config.id} - ${config.chart_type}`" 
                    :value="config.id"
                  />
                </el-select>
              </el-form-item>
              <el-form-item label="是否激活">
                <el-switch v-model="formData.is_active" active-text="激活" inactive-text="停用" />
              </el-form-item>
              <el-form-item label="创建人">
                <el-input v-model="formData.created_by" placeholder="请输入创建人" />
              </el-form-item>
            </div>
          </div>
          
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">OCAP步骤</h3>
              <el-button type="primary" size="small" @click="addStep">添加步骤</el-button>
            </div>
            
            <div v-if="formData.steps && formData.steps.length > 0" class="steps-list">
              <div v-for="(step, index) in formData.steps" :key="index" class="step-item">
                <div class="step-header">
                  <el-tag :type="getPhaseTagType(step.phase)" size="small">
                    {{ getPhaseLabel(step.phase) }}
                  </el-tag>
                  <span class="step-number">步骤 {{ step.step_number }}</span>
                  <el-button type="danger" size="small" link @click="removeStep(index)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
                <div class="step-content">
                  <div class="step-row">
                    <el-form-item label="阶段">
                      <el-select v-model="step.phase" style="width: 150px">
                        <el-option label="围堵" value="containment" />
                        <el-option label="调查" value="investigation" />
                        <el-option label="纠正" value="correction" />
                        <el-option label="验证" value="verification" />
                      </el-select>
                    </el-form-item>
                    <el-form-item label="动作类型">
                      <el-select v-model="step.action_type" style="width: 150px">
                        <el-option label="立即行动" value="immediate" />
                        <el-option label="短期行动" value="short_term" />
                        <el-option label="长期行动" value="long_term" />
                      </el-select>
                    </el-form-item>
                  </div>
                  <el-form-item label="动作描述">
                    <el-input v-model="step.action_description" type="textarea" :rows="2" placeholder="请输入动作描述" />
                  </el-form-item>
                  <div class="step-row">
                    <el-form-item label="负责人角色">
                      <el-input v-model="step.responsible_role" placeholder="如：质量工程师" />
                    </el-form-item>
                    <el-form-item label="负责人">
                      <el-input v-model="step.responsible_person" placeholder="具体负责人姓名" />
                    </el-form-item>
                    <el-form-item label="预计时长(分钟)">
                      <el-input-number v-model="step.expected_duration_minutes" :min="1" style="width: 120px" />
                    </el-form-item>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无OCAP步骤，点击上方按钮添加" />
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
import { getOCAP, createOCAP, updateOCAP } from '@/api/ocap'
import { getProductionLines, getControlChartConfigs } from '@/api'
import type { OCAPCreate, OCAPStepCreate, ProductionLine, ControlChartConfig } from '@/types'

const router = useRouter()
const route = useRoute()

const formRef = ref<FormInstance>()
const ocapId = computed(() => Number(route.params.ocapId))
const isEdit = computed(() => !!ocapId.value && route.name === 'EditOCAP')
const loading = ref(false)
const linesLoading = ref(false)
const configsLoading = ref(false)
const productionLines = ref<ProductionLine[]>([])
const controlChartConfigs = ref<ControlChartConfig[]>([])

const scoreMarks = {
  1: '1',
  5: '5',
  10: '10'
}

const formData = reactive<OCAPCreate & { steps: OCAPStepCreate[] }>({
  name: '',
  description: '',
  signal_type: undefined,
  priority: 'medium',
  severity_score: 1,
  scope_score: 1,
  trend_score: 1,
  overall_priority_score: 1,
  status: 'draft',
  is_active: true,
  created_by: '',
  control_chart_config_id: undefined,
  line_id: undefined,
  steps: []
})

const rules = reactive<FormRules>({
  name: [
    { required: true, message: '请输入OCAP名称', trigger: 'blur' },
    { min: 2, max: 200, message: '名称长度在2到200个字符之间', trigger: 'blur' }
  ]
})

const getSeverityTagType = (score: number) => {
  if (score >= 8) return 'danger'
  if (score >= 5) return 'warning'
  return 'success'
}

const getPhaseTagType = (phase: string) => {
  const types: Record<string, string> = {
    containment: 'danger',
    investigation: 'warning',
    correction: 'primary',
    verification: 'success'
  }
  return types[phase] || 'info'
}

const getPhaseLabel = (phase: string) => {
  const labels: Record<string, string> = {
    containment: '围堵',
    investigation: '调查',
    correction: '纠正',
    verification: '验证'
  }
  return labels[phase] || phase
}

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

const fetchControlChartConfigs = async () => {
  try {
    configsLoading.value = true
    const response = await getControlChartConfigs() as any
    controlChartConfigs.value = response || []
  } catch (error) {
    console.error('获取控制图配置失败:', error)
  } finally {
    configsLoading.value = false
  }
}

const fetchOCAP = async () => {
  if (!isEdit.value) return
  
  try {
    loading.value = true
    const response = await getOCAP(ocapId.value) as any
    
    Object.assign(formData, {
      name: response.name,
      description: response.description,
      signal_type: response.signal_type,
      priority: response.priority,
      severity_score: response.severity_score || 1,
      scope_score: response.scope_score || 1,
      trend_score: response.trend_score || 1,
      overall_priority_score: response.overall_priority_score || 1,
      status: response.status,
      is_active: response.is_active,
      created_by: response.created_by,
      control_chart_config_id: response.control_chart_config_id,
      line_id: response.line_id,
      steps: (response.steps || []).map((step: any) => ({
        phase: step.phase,
        step_number: step.step_number,
        action_type: step.action_type,
        action_description: step.action_description,
        responsible_role: step.responsible_role,
        responsible_person: step.responsible_person,
        expected_duration_minutes: step.expected_duration_minutes,
        deadline: step.deadline,
        is_mandatory: step.is_mandatory,
        sort_order: step.sort_order
      }))
    })
  } catch (error) {
    console.error('获取OCAP失败:', error)
    ElMessage.error('获取OCAP失败')
  } finally {
    loading.value = false
  }
}

const addStep = () => {
  formData.steps.push({
    phase: 'containment',
    step_number: formData.steps.length + 1,
    action_type: 'immediate',
    action_description: '',
    responsible_role: '',
    responsible_person: '',
    expected_duration_minutes: 30,
    is_mandatory: true,
    sort_order: formData.steps.length + 1
  })
}

const removeStep = (index: number) => {
  formData.steps.splice(index, 1)
  formData.steps.forEach((step, i) => {
    step.step_number = i + 1
    step.sort_order = i + 1
  })
}

const saveOcap = async () => {
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
      await updateOCAP(ocapId.value, submitData)
      ElMessage.success('更新成功')
    } else {
      await createOCAP(submitData)
      ElMessage.success('创建成功')
    }
    
    router.push('/ocaps')
  } catch (error: any) {
    console.error('保存OCAP失败:', error)
    ElMessage.error(error.detail || '保存失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProductionLines()
  fetchControlChartConfigs()
  fetchOCAP()
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
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
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

.priority-scores {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

.score-item {
  background: var(--bg-secondary);
  padding: 16px;
  border-radius: var(--radius-md);
}

.score-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.score-slider .el-slider {
  flex: 0 0 80%;
  max-width: 80%;
}

.score-slider .el-tag {
  flex-shrink: 0;
}

.steps-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.step-item {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 16px;
}

.step-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.step-number {
  font-weight: 600;
  color: var(--text-primary);
}

.step-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.step-row {
  display: flex;
  gap: 16px;
}

.step-row .el-form-item {
  flex: 1;
  margin-bottom: 0;
}

.ocap-form :deep(.el-form-item__label) {
  font-family: var(--font-display);
  font-weight: 600;
  color: var(--text-primary);
}

.ocap-form :deep(.el-input__wrapper),
.ocap-form :deep(.el-textarea__inner) {
  background: var(--bg-secondary);
  border-color: var(--border-color);
}

.priority-option {
  display: flex;
  align-items: center;
}

@media (max-width: 1200px) {
  .form-container {
    padding: 24px;
  }
  
  .header-right {
    flex-wrap: wrap;
  }
  
  .priority-scores {
    grid-template-columns: 1fr;
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
  
  .form-grid,
  .priority-scores {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .step-row {
    flex-direction: column;
  }
  
  .score-slider {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
