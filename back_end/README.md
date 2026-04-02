# 质量信息系统 (QIS) - 后端服务

## 项目介绍

本项目是基于 FastAPI 框架开发的质量信息系统后端，提供完整的质量管理功能，包括：

- **SPC 统计过程控制**：8种控制图类型 + Western Electric 8大判异准则
- **MSA 测量系统分析**：Gage R&R (X-bar/R & ANOVA) + 偏倚/线性/稳定性
- **控制计划管理**：AIAG APQP 标准格式 + 版本控制
- **过程能力分析**：Cp/Cpk/Pp/Ppk/Cm/Cmk 六维指数
- **异常应对 (OCAP)**：四阶段闭环流程 + 根因分析
- **AI 缺陷检测**：YOLOv8 深度学习 + 自动标注
- **报告生成**：Excel/HTML/PDF 多格式导出

系统严格遵循 **AIAG/VDA/ISO/TS16949** 国际标准，适用于汽车零部件、电子组装、医疗器械等制造行业的质量管理部门。

## Quick Start

### 1. 安装依赖

```bash
# 进入后端目录
cd back_end

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

创建.env文件并配置DEEPSEEK_API_KEY：

```bash
# 在back_end目录下创建.env文件
# 在.env文件中添加以下内容：
# DEEPSEEK_API_KEY=xxxxxxx
```

### 3. 初始化数据库

系统使用SQLite数据库，首次运行时会自动创建数据库文件。

### 4. 运行应用

```bash
# 启动FastAPI应用
python main.py
```

应用将在 `http://localhost:5000` 上运行。

## 项目结构

```
back_end/
├── main.py                     # FastAPI 入口文件
├── app/
│   ├── main.py                 # FastAPI 应用配置
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy 模型（23张表）
│   │   └── models.py           # 数据表定义
│   │       ├── ProductionLine  # 生产线
│   │       ├── MeasurementData # 测量数据
│   │       ├── AttributeData   # 属性数据
│   │       ├── ControlChartConfig  # 控制图配置
│   │       ├── CapabilityAnalysis  # 能力分析
│   │       ├── ControlPlan     # 控制计划
│   │       ├── ControlPlanItem # 控制计划项
│   │       ├── OCAP            # 失控行动计划
│   │       ├── OCAPSignal/Step/Execution/RootCause/CorrectiveAction
│   │       ├── MSAStudy        # MSA研究
│   │       └── MSAPart/Operator/Measurement/Result
│   ├── routers/                # API 路由（100个端点）
│   │   └── api.py              # API 端点定义
│   ├── schemas/                # Pydantic 模型
│   └── services/               # 业务逻辑
│       ├── control_chart_service.py   # SPC控制图计算
│       ├── capability_service.py      # 过程能力分析
│       ├── msa_service.py             # MSA分析
│       ├── detection_service.py       # AI缺陷检测
│       ├── report_service.py          # Excel报告导出
│       ├── report_service_new.py      # HTML报告导出
│       └── email_service.py           # 邮件报警
├── ccharts/                    # SPC控制图算法库
│   ├── xbar_rbar.py            # Xbar-R 图
│   ├── xbar_sbar.py            # Xbar-s 图
│   ├── imr.py                  # I-MR 图
│   ├── p.py / u.py / c.py / np.py  # 计数型控制图
│   └── ewma.py / cusum.py      # 高级控制图
├── templates/reports/          # 报告模板
│   ├── control_plan_report.html
│   ├── spc_normal_distribution.html
│   ├── spc_skewed_distribution.html
│   ├── spc_mixed_distribution.html
│   └── ocap_response_report.html
├── static/results/             # 检测结果存储
└── requirements.txt            # Python依赖
```

## 技术栈

- **FastAPI** - 现代高性能 Python Web 框架
- **Pydantic** - 数据验证和序列化
- **SQLAlchemy 2.0** - ORM 数据库管理
- **Uvicorn** - ASGI 服务器
- **OpenCV 4.x** - 图像处理
- **YOLOv8** - 缺陷检测模型
- **SQLite** - 轻量级数据库
- **ccharts** - Python SPC控制图计算库
- **scipy/numpy** - 科学计算与统计分析
- **Jinja2** - HTML报告模板渲染
- **PyTorch** - 深度学习框架（YOLOv8）

## API接口说明

### 图片检测相关接口

#### 1. 图片检测

- **URL**: `/api/detectByImg`
- **方法**: POST
- **参数**:
  - `file`: 上传的图片文件
- **返回**: 检测后的结果图片
- **描述**: 接收前端上传的图片，使用YOLOv8模型进行缺陷检测，并返回检测结果图片

#### 2. 批量图片检测

- **URL**: `/api/images/batch-detect`
- **方法**: POST
- **参数**: 多个图片文件
- **返回**: 批量检测结果
- **描述**: 支持批量上传并检测多张图片

#### 3. 获取图片列表

- **URL**: `/api/images`
- **方法**: GET
- **参数**:
  - `startDate`: 开始日期（可选，格式：YYYY-MM-DD HH:MM:SS）
  - `endDate`: 结束日期（可选，格式：YYYY-MM-DD HH:MM:SS）
- **返回**: 图片列表JSON数据
- **描述**: 获取检测历史记录，支持按时间范围筛选

#### 4. 获取单个图片信息

- **URL**: `/api/images/<int:image_id>`
- **方法**: GET
- **返回**: 单个图片的详细信息JSON数据
- **描述**: 根据ID获取指定图片的详细检测信息

#### 5. 添加图片记录

- **URL**: `/api/images`
- **方法**: POST
- **参数**: JSON格式的图片信息
- **返回**: 添加成功的图片信息JSON数据
- **描述**: 手动添加图片检测记录

#### 6. 获取检测结果图片

- **URL**: `/results/images/<filename>`
- **方法**: GET
- **返回**: 检测结果图片
- **描述**: 获取保存的检测结果图片

#### 7. 获取检测结果JSON

- **URL**: `/results/jsons/<filename>`
- **方法**: GET
- **返回**: 检测结果JSON数据
- **描述**: 获取保存的检测结果JSON文件

### 控制图与监控接口

#### 8. 获取控制图数据

- **URL**: `/api/control-chart-data`
- **方法**: GET
- **返回**: 控制图数据JSON，包含样本数据和异常检测结果
- **描述**: 生成控制图数据，支持多种图表类型（Xbar-R, Xbar-s, I-MR, P, U, C, NP, EWMA, CUSUM）

### 邮箱设置接口

#### 9. 获取邮箱设置

- **URL**: `/api/email-settings`
- **方法**: GET
- **返回**: 当前邮箱设置JSON数据
- **描述**: 获取当前用于接收报警邮件的邮箱地址

#### 10. 更新邮箱设置

- **URL**: `/api/email-settings`
- **方法**: PUT
- **参数**:
  - `email`: 新的邮箱地址
- **返回**: 更新后的邮箱设置JSON数据
- **描述**: 更新用于接收报警邮件的邮箱地址

---

### 生产线管理 API

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/production-lines` | 获取产线列表 |
| POST | `/api/production-lines` | 创建产线 |
| PUT | `/api/production-lines/{id}` | 更新产线 |
| DELETE | `/api/production-lines/{id}` | 删除产线 |

### 控制计划 API

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/control-plans` | 获取控制计划列表 |
| POST | `/api/control-plans` | 创建控制计划 |
| GET | `/api/control-plans/{id}` | 获取控制计划详情 |
| PUT | `/api/control-plans/{id}` | 更新控制计划 |
| POST | `/api/control-plans/{id}/items` | 添加控制计划项 |
| GET | `/api/control-plans/{id}/export/excel` | 导出Excel格式 |
| GET | `/api/control-plans/{id}/export/html` | 导出HTML格式 |

### MSA 测量系统分析 API

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/msa-studies` | 获取MSA研究列表 |
| POST | `/api/msa-studies` | 创建MSA研究 |
| POST | `/api/msa-studies/{id}/calculate` | 计算GR&R结果 |
| GET | `/api/msa-studies/{id}/result` | 获取分析结果 |

### 过程能力分析 API

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/capability-analyses` | 获取能力分析列表 |
| POST | `/api/capability-analyses` | 创建能力分析 |
| POST | `/api/capability-analyses/calculate` | 计算能力指数 |
| GET | `/api/capability-analyses/{id}` | 获取分析详情 |
| GET | `/api/capability-analyses/{id}/export/html` | 导出HTML报告 |

### OCAP 失控行动计划 API

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/ocaps` | 获取OCAP列表 |
| POST | `/api/ocaps` | 创建OCAP |
| GET | `/api/ocaps/{id}` | 获取OCAP详情（含步骤/执行记录/根因/纠正措施） |
| POST | `/api/ocaps/{id}/signals` | 触发失控信号 |
| POST | `/api/ocaps/{id}/execute` | 执行OCAP步骤 |
| POST | `/api/ocaps/{id}/root-cause` | 提交根本原因分析 |
| POST | `/api/ocaps/{id}/corrective-actions` | 添加纠正措施 |
| GET | `/api/ocaps/{id}/export/excel` | 导出Excel |
| GET | `/api/ocaps/{id}/export/html` | 导出HTML报告 |

### 数据采集 API

| 方法 | URL | 描述 |
|------|-----|------|
| POST | `/api/measurement-data` | 录入计量型数据 |
| POST | `/api/attribute-data` | 录入计数型数据 |
| GET | `/api/production-lines/{id}/data` | 获取产线数据历史 |

### 控制图配置 API

| 方法 | URL | 描述 |
|------|-----|------|
| GET | `/api/control-chart-configs` | 获取控制图配置 |
| POST | `/api/control-chart-configs` | 创建控制图配置 |
| PUT | `/api/control-chart-configs/{id}` | 更新配置 |

## 数据库模型

### 原有基础表

#### Image 表（缺陷检测结果）

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | Integer | 主键，自增 |
| name | String | 图片名称，唯一 |
| hasDefects | Boolean | 是否有缺陷 |
| detection_total_cnts | Integer | 缺陷总数 |
| detection_classes | Text | 缺陷类别列表（JSON字符串） |
| detection_boxes | Text | 检测框坐标（JSON字符串） |
| detection_scores | Text | 置信度分数（JSON字符串） |
| captureTime | DateTime | 捕获时间 |

#### EmailSettings 表（邮箱配置）

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | Integer | 主键 |
| email | String | 邮箱地址 |

#### User 表（用户信息）

| 字段名 | 类型 | 描述 |
| --- | --- | --- |
| id | Integer | 主键 |
| username | String | 用户名 |
| password_hash | String | 密码哈希 |

---

### 新增核心业务表

#### 生产线与数据采集（4张表）

| 表名 | 主要字段 | 描述 |
| ---- | -------- | ---- |
| ProductionLine | line_code, line_name, data_type, model_path | 生产线定义与参数配置 |
| MeasurementData | line_id, measurement_values | 计量型测量数据存储 |
| AttributeData | line_id, defect_count, defect_details | 计数型属性数据存储 |
| SamplingPlan/SamplingRecord | plan_name, sample_size, frequency | 抽样计划与抽样记录 |

#### 控制图与分析（3张表）

| 表名 | 主要字段 | 描述 |
| ---- | -------- | ---- |
| ControlChartConfig | chart_type, alarm_rules, ucl/lcl/cl | 控制图配置与判异规则 |
| CapabilityAnalysis | usl/lsl, cp/cpk/pp/ppk/cm/cmk | 过程能力分析结果 |

#### 控制计划（2张表）

| 表名 | 主要字段 | 描述 |
| ---- | -------- | ---- |
| ControlPlan | part_number, version, status, revision_date | 控制计划主表 |
| ControlPlanItem | product_characteristic, spec_limits, reaction_plan | 控制计划明细项 |

#### OCAP 异常应对（6张表）

| 表名 | 主要字段 | 描述 |
| ---- | -------- | ---- |
| OCAP | signal_type, priority, status, created_at | 失控计划主表 |
| OCAPSignal | signal_time, signal_value, rule_violated | 失控信号记录 |
| OCAPStep | phase, step_number, action_description | 应对步骤定义 |
| OCAPExecution | status, notes, evidence_urls, executed_by | 执行记录 |
| OCAPRootCause | analysis_method (5Why/fishbone), category, description | 根本原因分析 |
| OCAPCorrectiveAction | action_type, effectiveness_verified, due_date | 纠正措施跟踪 |

#### MSA 测量系统分析（5张表）

| 表名 | 主要字段 | 描述 |
| ---- | -------- | ---- |
| MSAStudy | study_type (GR&R/Bias/Linearity/Stability), number_of_parts/operators/replicates | MSA研究主表 |
| MSAPart | part_number, reference_value, tolerance | 零件样本信息 |
| MSAOperator | operator_name, experience_level | 操作员信息 |
| MSAMeasurement | measurement_value, trial_number | 测量原始数据 |
| MSAResult | %GRR, %EV, %AV, ndc, acceptance结论 | 分析结果汇总 |

## 业务流程指引

### 日常质量监控流程

```
1. 检验员通过前端录入检测数据（计量型/计数型）
2. 系统自动更新控制图并检测异常（Western Electric 8大准则）
3. 如发现异常 → 自动触发报警邮件 + 创建OCAP
4. 质量工程师执行围堵行动（Containment）
5. 进行根本原因分析（5Why / 鱼骨图）
6. 制定纠正措施并跟踪验证（Corrective Action）
7. 生成响应报告并存档（Excel/HTML/PDF）
```

### 新产品导入流程（APQP）

```
1. 创建生产线并配置参数（USL/LSL, 控制图类型）
2. 执行MSA测量系统分析（确保GR&R < 10% 或 < 30%）
3. 制定控制计划（依据PFMEA识别特殊特性SC/CC）
4. 进行初始过程能力研究（Pp/Ppk ≥ 1.67）
5. 发布控制计划并培训操作员
6. 进入量产SPC监控阶段（Cp/Cpk ≥ 1.33）
```

## 注意事项

### 基础配置

1. 确保模型文件存在且路径配置正确
2. 首次运行时会自动创建数据库（database.db）
3. 检测结果会保存在 `static/results` 目录下
4. 控制图功能需要足够的数据量才能生成有意义的结果
5. 临时图片存储在 `images` 目录，检测完成后会自动处理

### 邮件报警功能

6. 默认发送方邮箱：3600094151@qq.com
7. 默认接收方邮箱：2395365918@qq.com
8. 邮箱配置文件：`services/email_service.py`
9. 可通过前端界面更新接收报警邮件的邮箱地址

### 标准合规性

10. 系统遵循 **AIAG/VDA SPC、MSA、APQP** 国际标准
11. 控制图计算基于 **ccharts** 库实现 Western Electric 8大判异准则
12. MSA 分析支持 **X-bar/R** 和 **ANOVA** 两种方法
13. 报告模板符合 **AIAG-VDA SPC 手册 22 项元素** 要求
14. OCAP 流程包含完整的 **PDCA 闭环管理**

## 前端集成

后端提供了静态文件服务，可以直接访问前端构建后的文件。前端构建后，将 `dist` 目录复制到 `front_end` 目录下，后端将自动提供前端访问。

访问地址：`http://localhost:5000`

## 许可证

GNU GPL v3 License
