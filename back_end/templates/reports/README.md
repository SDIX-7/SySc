# 报告导出模板说明

## 概述

本项目已创建三个专业的 HTML 报告导出模板，**完全符合 AIAG/VDA 质量标准格式**，基于项目图片中的真实表格格式设计。

## 模板文件位置

所有模板文件位于：`d:\py\质量信息系统\flask+vue\back_end\templates\reports\`

## 设计说明

所有模板均按照 `d:\py\质量信息系统\报告.md` 中提供的图片格式设计，确保与 AIAG/VDA 标准表格完全一致。

### 1. 控制计划报告模板
**文件**: `control_plan_report.html`

**用途**: 按照 AIAG/VDA 控制计划标准格式导出控制计划

**特点**:
- ✅ **与图片格式完全一致** - 严格按照 AIAG/VDA 控制计划表格格式
- ✅ 包含所有 26 个标准字段（带圆圈编号）
- ✅ Prototype/Pre-Launch/Production 选择框
- ✅ 标准的表头信息区域（Control Plan Number, Part Name, Organization 等）
- ✅ 主表格包含：CHARACTERISTICS, METHODS, REACTION PLAN
- ✅ 使用表格布局，黑色边框，灰色表头
- ✅ 打印友好的设计

**字段说明** (按照 AIAG/VDA 标准编号):
1. PROTOTYPE/PRE-LAUNCH/PRODUCTION
2. CONTROL PLAN NUMBER
3. PART NUMBER/LATEST CHANGE LEVEL
4. PART NAME/DESCRIPTION
5. ORGANIZATION/PLANT
6. ORGANIZATION CODE (SUPPLIER CODE)
7. KEY CONTACT/PHONE
8. CORE TEAM
9. ORGANIZATION/PLANT APPROVAL/DATE
10. DATE (ORIG.)
11. DATE (REV.)
12. CUSTOMER ENGINEERING APPROVAL/DATE
13. CUSTOMER QUALITY APPROVAL/DATE
14. OTHER APPROVAL/DATE
15. PART/PROCESS NUMBER
16. PROCESS NAME/OPERATION DESCRIPTION
17. MACHINE, DEVICE, JIG, TOOLS FOR MFG.
18. NUMBER (CHARACTERISTICS)
19. PRODUCT CHARACTERISTIC
20. PROCESS CHARACTERISTIC
21. SPECIAL CHARACTERISTIC CLASSIFICATION
22. PRODUCT/PROCESS SPECIFICATION/TOLERANCE
23. EVALUATION/MEASUREMENT TECHNIQUE
24. SAMPLE SIZE/FREQ.
25. CONTROL METHOD
26. REACTION PLAN

**包含的模板变量**:
```python
{
    'plan_type': 'prototype|pre_launch|production',
    'page_number': '页码',
    'total_pages': '总页数',
    'control_plan_number': '控制计划编号',
    'part_number': '零件号',
    'latest_change_level': '最新变更等级',
    'part_name': '零件名称',
    'organization_plant': '组织/工厂',
    'organization_code': '组织代码',
    'key_contact': '关键联系人',
    'core_team': '核心团队',
    'date_orig': '原始日期',
    'date_rev': '修订日期',
    'org_approval': '组织批准',
    'customer_eng_approval': '客户工程批准',
    'customer_quality_approval': '客户质量批准',
    'other_approval': '其他批准',
    'items': [控制计划项目列表]
}
```

---

### 2. SPC 过程能力分析报告模板
**文件**: `spc_capability_report.html`

**用途**: 按照 AIAG/VDA SPC 手册标准格式导出过程能力分析报告

**特点**:
- ✅ **与图片格式完全一致** - 严格按照 AIAG/VDA SPC 报告格式（20 个编号区域）
- ✅ 标准表头：Title, AIAG/VDA/QMC logos
- ✅ 过程信息区域（1-10 号字段）
- ✅ 四个图表区域：Histogram, Raw Value Chart, Probability Plot, x̄/s Chart（11-14 号）
- ✅ 统计信息区域（15-18 号）
- ✅ 能力指数和 PPM（19 号）
- ✅ 结论区域（20 号）
- ✅ 表格布局，黑色边框

**字段说明** (按照 AIAG/VDA SPC 标准编号):
1. Process Name
2. Process ID
3. Study Location / Operator Name
4. Study Date
5. Part Name & ID
6. Characteristic Name & ID
7-8. Study Remarks
9-10. Sample Size, Subgroup Size, Sampling Strategy
11. Histogram
12. Raw Value Chart
13. Probability Plot
14. x̄/s - Shewhart Chart
15. Process Location estimate (X50%)
16. Process variation estimate
17. Distribution Model
18. Performance / Capability Requirement (Cp,G, Cpk,G)
19. Calculated Performance / Capability indices (Cp, Cpk with 95% CI)
20. Conclusions / Recommendations / Corrective Actions

**包含的模板变量**:
```python
{
    'process_name': '过程名称',
    'machine_name': '机器名称',
    'study_location': '研究地点',
    'process_id': '过程 ID',
    'machine_id': '机器 ID',
    'operator_name': '操作员名称',
    'study_date': '研究日期',
    'start_time': '开始时间',
    'end_time': '结束时间',
    'part_name_id': '零件名称和 ID',
    'characteristic_name_id': '特性名称和 ID',
    'lsl': '规格下限',
    'usl': '规格上限',
    'study_remarks': '研究备注',
    'sample_size': '样本大小',
    'subgroup_size': '子组大小',
    'sampling_strategy': '抽样策略',
    'x50': '中位数',
    'variation_estimate': '变异估计',
    'distribution_model': '分布模型',
    'cp_g': 'Cp 要求值',
    'cpk_g': 'Cpk 要求值',
    'calculation_method': '计算方法',
    'cp': 'Cp 值',
    'cpk': 'Cpk 值',
    'cp_ci_lower': 'Cp 置信区间下限',
    'cp_ci_upper': 'Cp 置信区间上限',
    'cpk_ci_lower': 'Cpk 置信区间下限',
    'cpk_ci_upper': 'Cpk 置信区间上限',
    'p_usl': '超出 USL 的百分比',
    'ppm_usl': 'PPM USL',
    'p_lsl': '低于 LSL 的百分比',
    'ppm_lsl': 'PPM LSL',
    'conclusion': '结论'
}
```

---

### 3. OCAP 响应计划报告模板
**文件**: `ocap_response_report.html`

**用途**: 导出异常响应计划（Out of Control Action Plan）完整报告

**特点**:
- ✅ 红色主题，突出紧急性
- ✅ 优先级徽章（Critical/High/Medium/Low）
- ✅ 基本信息网格展示
- ✅ 统计信息卡片
- ✅ SPC 触发信号展示
- ✅ 响应时间线（检测→围堵→纠正→验证）
- ✅ 响应步骤明细表格
- ✅ 根本原因分析
- ✅ 纠正措施跟踪

**包含的模板变量**:
```python
{
    'ocap_number': 'OCAP 编号',
    'title': '标题',
    'priority_class': '优先级等级',
    'priority_text': '优先级文本',
    'production_line': '产线',
    'assigned_to': '负责人',
    'status': '状态',
    'created_time': '创建时间',
    'signals': [SPC 信号列表],
    'steps': [响应步骤列表],
    'root_causes': [根本原因列表],
    'actions': [纠正措施列表],
    'generated_time': '生成时间',
    'ocap_id': 'OCAP ID'
}
```

---

## 使用方式

### 后端集成示例

```python
from fastapi import Response
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

# 加载模板
env = Environment(loader=FileSystemLoader('templates/reports'))
template = env.get_template('control_plan_report.html')

# 准备数据
data = {
    'plan_type': 'production',
    'page_number': 1,
    'total_pages': 1,
    'control_plan_number': 'CP-2026-001',
    'part_number': 'PN-001',
    'part_name': '示例零件',
    # ... 其他字段
    'items': [...]
}

# 渲染模板
html_content = template.render(**data)

# 返回响应
return Response(
    content=html_content,
    media_type="text/html",
    headers={
        "Content-Disposition": f"attachment; filename*=UTF-8''ControlPlan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    }
)
```

---

## 设计特点

### 1. 符合标准
- ✅ **完全匹配图片格式** - 所有模板均基于 AIAG/VDA 标准表格
- ✅ 使用正确的字段编号（圆圈数字）
- ✅ 标准的表格布局和边框样式

### 2. 专业设计
- 📊 使用表格布局，确保打印效果
- 📊 黑色边框，灰色表头
- 📊 合适的字体大小（9-11px）
- 📊 清晰的字段分组

### 3. 打印优化
- 🖨️ 专门的打印样式
- 🖨️ 白色背景
- 🖨️ 移除不必要的装饰

### 4. 国际化
- 🌐 英文标签（符合 AIAG/VDA 标准）
- 🌐 支持中文字符

---

## 与现有代码的集成

### 现有报告服务
项目已有报告导出功能在 `report_service.py` 中：
- `export_control_plan_detailed_report()` - 控制计划 HTML 报告
- `export_capability_analysis_report()` - SPC 能力 HTML 报告

### 建议的集成方式
1. **替换现有模板**: 将现有的内联 HTML 模板替换为使用这些模板文件
2. **使用 Jinja2 渲染**: 使用 Jinja2 模板引擎渲染 HTML
3. **添加 OCAP 导出**: 新增 `export_ocap_response_report()` 函数

### 安装 Jinja2
```bash
pip install jinja2
```

---

## 文件结构

```
flask+vue/
└── back_end/
    ├── templates/
    │   └── reports/
    │       ├── control_plan_report.html      # 控制计划报告模板（AIAG/VDA 标准格式）
    │       ├── spc_capability_report.html    # SPC 能力分析报告模板（AIAG/VDA 标准格式）
    │       ├── ocap_response_report.html     # OCAP 响应计划报告模板
    │       └── README.md                     # 本说明文档
    ├── app/
    │   └── services/
    │       └── report_service.py             # 报告服务（需更新以使用模板）
    └── routers/
        └── api.py                            # API 路由
```

---

## 下一步建议

1. ✅ **模板已创建** - 三个 HTML 报告模板已完成，与图片格式完全一致
2. ⏳ **安装 Jinja2** - 在 requirements.txt 中添加 `jinja2`
3. ⏳ **更新 report_service.py** - 使用模板文件替换内联 HTML
4. ⏳ **添加 OCAP 导出 API** - 在 api.py 中添加 OCAP 报告导出端点
5. ⏳ **前端集成** - 在前端添加报告导出按钮
6. ⏳ **测试验证** - 测试所有报告导出功能

---

## 参考

- AIAG/VDA Control Plan Standard (控制计划标准格式)
- AIAG/VDA SPC Harmonized Standard (SPC 研究报告标准格式)
- 项目文档：`d:\py\质量信息系统\报告.md`
- 参考图片：
  - `FILES/ControlPlan.md/img-20260306210125.png` - Control Plan 空白表格
  - `FILES/ControlPlan.md/img-20260306210129.png` - 控制计划字段说明 (1-9)
  - `FILES/ControlPlan.md/img-20260306210133.png` - 控制计划字段说明 (10-18)
  - `FILES/ControlPlan.md/屏幕截图 2026-03-11 231934.png` - SPC 研究报告格式
