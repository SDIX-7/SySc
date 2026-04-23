# 质量信息系统 (Quality Information System, QIS)

## 基于 AIAG/VDA 标准的制造业全流程质量管理平台

> **面向质量部的一站式质量管理解决方案** | 支持 IATF 16949 / ISO/TS 16949 国际标准

---

## 📋 项目简介

**质量信息系统（QIS）** 是一款面向制造业质量部的综合质量管理平台，严格遵循 **AIAG/VDA/ISO/TS 16949** 国际标准开发。系统集成了 SPC 统计过程控制、MSA 测量系统分析、控制计划、OCAP 异常应对、过程能力分析等核心质量工具，覆盖从新产品导入到量产监控的全流程质量管理。

### 系统规模

| 维度 | 规模 |
|------|------|
| 数据库表 | **23 张** |
| API 接口 | **100+ 个** RESTful 端点 |
| 前端页面 | **24 个** 功能组件 (**29 个**路由) |
| 控制图类型 | **12 种** (Xbar-R, Xbar-s, I-MR, P, C, U, np 等) |
| 能力指数 | **6 维** (Cp, Cpk, Pp, Ppk, Cm, Cmk) |

### 目标用户

- **质量经理 (QM)** — 战略决策与体系管理
- **质量工程师 (QE)** — 技术支持与问题解决
- **过程工程师 (PE)** — 过程控制与持续改进
- **质量检验员 (QI)** — 数据采集与日常监控
- **SPC 分析师** — 统计分析与报告输出
- **MSA 专员** — 测量系统评估

### 适用行业

- 🚗 汽车零部件制造（IATF 16949）
- 💻 电子组装行业
- 🏥 医疗器械生产
- ✈️ 航空航天配套
- ⚙️ 精密机械加工

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     前端 (Vue 3 + TypeScript)                │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 数据采集   │ │ SPC 监控  │ │ 能力分析  │ │ MSA 研究  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 控制计划   │ │ OCAP    │ │ AI 检测  │ │ 报告导出  │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │ RESTful API (FastAPI)
┌─────────────────────────▼───────────────────────────────────┐
│                    后端 (Python + FastAPI)                    │
│                                                             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ 控制图引擎     │ │ 能力计算引擎  │ │ MSA 分析引擎         │ │
│  │ (ccharts库)   │ │ (scipy/numpy)│ │ (Gage R&R)          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │
│  │ 报告生成引擎   │ │ AI 检测引擎  │ │ 业务逻辑层            │ │
│  │ (Jinja2)     │ │(YOLOv8/PyTorch)│ │ (Services)          │ │
│  └──────────────┘ └──────────────┘ └──────────────────────┘ │
└─────────────────────────┬───────────────────────────────────┘
                          │ SQLAlchemy ORM
┌─────────────────────────▼───────────────────────────────────┐
│                      数据库 (SQLite)                         │
│                                                             │
│  产线管理 | 测量数据 | 计数数据 | 控制图配置 | 抽样方案     │
│  能力分析 | 控制计划 | OCAP 异常 | MSA 研究 | 用户权限     │
│  AI 检测 | 邮件通知 | ... (共23张核心业务表)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 核心功能模块

### 3.1 生产线管理 (Production Line Management)

系统的核心组织单元，所有质量活动均围绕产线展开。每条产线可配置独立的数据类型、控制图类型、抽样方案及 AI 检测模型。

- 创建/编辑/删除生产线
- 配置数据采集方式（计量型 measurement / 计数型 attribute）
- 关联 YOLOv8 AI 缺陷检测模型
- 产线状态管理（active/inactive）

### 3.2 控制计划 (Control Plan)

基于 **AIAG APQP** 标准格式的控制计划管理，是连接 PFMEA 与 SPC 监控的关键桥梁。

- 符合 AIAG APQP 控制计划模板格式
- 特殊特性分类标识（CC 关键特性 / SC 安全特性）
- 控制方法与反应计划关联 OCAP
- 版本管理与审批流程（草稿 → 审核 → 发布 → 归档）
- 支持导出 Excel / HTML / PDF 格式

### 3.3 测量系统分析 (MSA)

基于 **AIAG MSA 第4版** 标准的测量系统分析工具，确保测量数据的质量和可靠性。

- **Gage R&R 研究**：X-bar/R 法和 ANOVA 法
- **偏倚研究**：测量系统准确度评估
- **线性研究**：量程内偏倚变化分析
- **稳定性研究**：随时间变化的测量漂移检测
- AIAG 接受标准判定：%GRR <10% 优秀 / <30% 可接受 / ≥30% 不可接受
- NDC（可区分类别数）评估：ndc ≥ 5 为可接受

### 3.4 SPC 统计过程控制

基于 **ccharts** 专业统计库构建的 SPC 引擎，支持完整的控制图类型体系和 Western Electric 判异准则。

**支持的控制图类型：**

| 类型 | 控制图 | 适用场景 |
|------|--------|---------|
| 计量型 | Xbar-R（均值-极差） | 子组样本量 2-10 |
| 计量型 | Xbar-s（均值-标准差） | 子组样本量 >10 |
| 计量型 | I-MR（单值-移动极差） | 单件生产/样本量=1 |
| 计量型 | Median-R（中位数-极差） | 异常值较多场景 |
| 计数型 | P 图（不合格率） | 样本量不固定 |
| 计数型 | np 图（不合格数） | 样本量固定 |
| 计数型 | C 图（缺陷数） | 样本量固定 |
| 计数型 | U 图（单位缺陷数） | 样本量不固定 |
| 高级 | EWMA（指数加权移动平均） | 检测小偏移 |
| 高级 | CUSUM（累积和） | 检测持续偏移 |

**Western Electric 8 大判异准则：**
1. 1点超出3σ控制线
2. 连续9点在中心线同侧
3. 连续6点递增或递减
4. 连续14点相邻点上下交替
5. 连续3点中2点在2σ外
6. 连续5点中4点在1σ外
7. 连续15点在1σ内（层内变异过小）
8. 连续8点在中心线两侧但无1点在1σ内

### 3.5 过程能力分析 (Capability Analysis)

六维过程能力指数评估，支持正态/偏态/混合分布拟合。

| 指数 | 含义 | 评价标准 |
|------|------|---------|
| Cp | 过程潜在能力 | ≥1.33 合格 |
| Cpk | 过程实际能力 | ≥1.33 合格，≥1.67 优秀 |
| Pp | 过程性能 | ≥1.33 合格 |
| Ppk | 过程实际性能 | ≥1.33 合格 |
| Cm | 机器能力 | ≥1.67 合格 |
| Cmk | 机器实际能力 | ≥1.67 合格 |

- 正态性检验（Shapiro-Wilk 检验）
- 直方图 + 正态/偏态/混合分布拟合曲线
- 运行图（时间序列趋势分析）
- 能力仪表盘可视化

### 3.6 异常应对计划 (OCAP - Out of Control Action Plan)

完整的四阶段闭环异常管理流程，确保失控信号得到及时有效的处理。

```
信号触发 → 围堵行动 → 根本原因分析 → 纠正措施 → 效果验证 → 关闭
```

- **围堵阶段**：隔离可疑产品，防止不良流出
- **调查阶段**：根本原因分析（5Why 分析法 / 鱼骨图）
- **纠正阶段**：制定永久性纠正措施，指派责任人
- **验证阶段**：确认措施有效性，更新控制计划

### 3.7 AI 缺陷检测

基于 **YOLOv8** 深度学习模型的实时缺陷检测功能。

- 支持多种图片格式（JPG/PNG/TIF/BMP）
- 批量检测与单张检测
- 缺陷自动标注与可视化
- 检测结果自动入库与统计
- 每条产线可绑定独立检测模型

### 3.8 报告导出

符合 **AIAG-VDA SPC 手册** 标准的报告生成功能。

- **控制计划报告**：AIAG 标准格式（Excel/HTML/PDF）
- **SPC 能力分析报告**：正态/偏态/混合分布三种模板
- **OCAP 响应报告**：完整的异常处理时间线
- **MSA 分析报告**：GR&R 结果与方差分量
- **过程能力报告**：六维指数 + 直方图 + 概率图

---

## 🔄 业务流程

### 新产品导入流程 (APQP)

```
创建产线 → MSA测量系统分析 → 制定控制计划 → 过程能力研究 → 量产SPC监控
   │              │                  │               │              │
   ▼              ▼                  ▼               ▼              ▼
 配置参数     GR&R≤30%?        APQP格式编制     Pp/Ppk≥1.67?    日常监控
 数据类型     ↓否→改进         特殊特性识别      ↓否→改进       异常→OCAP
 绑定模型     ↓是→通过         关联反应计划      ↓是→通过       报告生成
```

### 日常质量监控流程

```
1. 检验员录入检测数据（计量型/计数型）
2. 系统自动更新控制图并检测异常
3. 如发现异常 → 自动触发报警邮件 + 创建OCAP
4. 质量工程师执行围堵行动（隔离可疑产品）
5. 进行根本原因分析（5Why/鱼骨图）
6. 制定纠正措施并跟踪验证
7. 生成响应报告并存档
```

### PDCA 持续改进循环

```
Plan(计划) → Do(执行) → Check(检查) → Act(改进)
    │            │            │            │
    ▼            ▼            ▼            ▼
 识别改进机会  实施纠正措施  验证措施效果  标准化与推广
 制定改进计划  执行OCAP步骤  SPC监控确认  更新控制计划
```

---

## 👥 质量部组织架构

### 组织结构

```
                    ┌─────────────┐
                    │  质量经理(QM) │
                    └──────┬──────┘
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │  技术支持组    │ │ 过程控制组 │ │  数据分析组   │
    │              │ │          │ │              │
    │ • QE         │ │ • PE     │ │ • SPC分析师  │
    │ • MSA专员    │ │ • QI     │ │              │
    └──────────────┘ └──────────┘ └──────────────┘
```

### 岗位职责矩阵

| 岗位 | 主要职责 | 系统权限 | 关键操作 |
|------|---------|---------|---------|
| **QM 质量经理** | 体系管理、审批决策、管理评审 | 全部查看 + 审批 | 审批控制计划、评审OCAP、导出报告 |
| **QE 质量工程师** | 技术支持、异常处理、根因分析 | 查看 + 录入 + 导出 | 执行OCAP、根因分析、纠正措施 |
| **PE 过程工程师** | 过程控制、控制计划、持续改进 | 查看 + 录入 + 编辑 | 编制控制计划、发起能力研究 |
| **QI 质量检验员** | 数据采集、日常监控、产品检验 | 查看 + 录入 | 录入检测数据、查看控制图 |
| **SPC 分析师** | 统计分析、报告输出、趋势预测 | 查看 + 分析 + 导出 | 控制图分析、能力计算、报告生成 |
| **MSA 专员** | 测量系统评估、GR&R研究 | 查看 + 录入 + 分析 | 发起MSA研究、录入数据、判定结果 |

### 权限分配

| 功能模块 | QM | QE | PE | QI | SPC | MSA |
|---------|----|----|----|----|----|----|
| 生产线管理 | 👁✏🗑 | 👁✏ | 👁✏ | 👁 | 👁 | 👁 |
| 控制计划 | 👁✏📋 | 👁✏ | 👁✏ | 👁 | 👁📤 | 👁 |
| MSA研究 | 👁📋 | 👁 | 👁 | 👁 | 👁 | 👁✏📋 |
| 数据采集 | 👁 | 👁 | 👁 | 👁✏ | 👁 | 👁✏ |
| SPC监控 | 👁 | 👁 | 👁 | 👁 | 👁✏📤 | 👁 |
| 能力分析 | 👁📋 | 👁 | 👁✏ | 👁 | 👁✏📤 | 👁 |
| OCAP | 👁📋 | 👁✏📋 | 👁✏ | 👁 | 👁📤 | 👁 |
| 报告导出 | 👁📤 | 👁📤 | 👁📤 | 👁 | 👁📤 | 👁📤 |

> 👁 查看 | ✏ 录入/编辑 | 📋 审批 | 📤 导出 | 🗑 删除

---

## 🚀 快速开始

### 环境要求

| 依赖 | 版本要求 | 用途 |
|------|---------|------|
| Python | ≥ 3.11 | 后端运行环境 |
| Node.js | ≥ 18.0 | 前端构建工具 |
| npm | ≥ 8.0 | 前端包管理 |

### 后端安装与运行

```bash
cd back_end

# 安装 Python 依赖
pip install -r requirements.txt

# 配置环境变量（如需AI检测功能）
# 在 .env 文件中添加：DEEPSEEK_API_KEY=xxxxxxx

# 启动后端服务
python main.py
```

后端服务将在 `http://localhost:5000` 上运行。
API 文档地址：`http://localhost:5000/docs`

### 前端安装与运行

```bash
cd front_end

# 安装前端依赖
npm install

# 启动开发服务
npm run dev
```

前端服务将在 `http://localhost:5173` 上运行。

### 生产部署

```bash
# 构建前端
cd front_end
npm run build

# 部署后端
cd back_end
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 app.main:app
```

---

## 💻 技术栈

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.100+ | 高性能 Web 框架 |
| SQLAlchemy | 2.0 | ORM 数据库管理 |
| Pydantic | 2.0 | 数据验证与序列化 |
| Uvicorn | 0.23+ | ASGI 服务器 |
| PyTorch | 2.0+ | 深度学习框架 |
| YOLOv8 | 8.0+ | 目标检测模型 |
| ccharts | - | SPC 控制图计算库 |
| scipy/numpy | - | 科学计算与统计分析 |
| Jinja2 | 3.0+ | HTML 报告模板引擎 |
| SQLite | - | 轻量级数据库 |
| OpenCV | 4.x | 图像处理 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | ^3.4 | 渐进式 JavaScript 框架 |
| TypeScript | ^5.3 | 类型安全 |
| Vite | ^5.0 | 下一代构建工具 |
| Pinia | ^2.1 | Vue 3 状态管理 |
| Vue Router | ^4.2 | 路由管理（29个路由） |
| Element Plus | ^2.5 | Vue 3 UI 组件库 |
| ECharts | ^5.5 | 数据可视化图表库 |
| Axios | ^1.6 | HTTP 客户端 |

---

## 📂 项目结构

```
flask+vue/
├── back_end/                        # ★ 后端服务 (FastAPI)
│   ├── main.py                      # FastAPI 入口文件
│   ├── app/
│   │   ├── main.py                  # FastAPI 应用配置
│   │   ├── config.py                # 配置管理
│   │   ├── database.py              # 数据库连接与会话管理
│   │   ├── models/                  # ★ 数据模型层 (23张表)
│   │   │   └── models.py            # 所有 SQLAlchemy ORM 模型定义
│   │   ├── routers/                 # API 路由层 (100+端点)
│   │   │   └── api.py               # RESTful API 端点定义
│   │   ├── schemas/                 # Pydantic 数据校验模型
│   │   │   └── schemas.py           # 请求/响应数据结构定义
│   │   └── services/                # ★ 核心业务逻辑层
│   │       ├── control_chart_service.py  # SPC控制图计算引擎
│   │       ├── capability_service.py     # 过程能力分析引擎
│   │       ├── msa_service.py            # MSA测量系统分析引擎
│   │       ├── detection_service.py      # AI缺陷检测服务
│   │       ├── report_service.py         # Excel报告导出
│   │       ├── report_service_new.py     # HTML报告导出
│   │       ├── chart_generator.py        # 图表生成服务
│   │       ├── email_service.py          # 邮件报警服务
│   │       └── auth_service.py           # 用户认证服务
│   ├── templates/reports/           # ★ 报告模板 (Jinja2)
│   │   ├── control_plan_report.html      # 控制计划报告
│   │   ├── spc_normal_distribution.html  # SPC正态分布报告
│   │   ├── spc_skewed_distribution.html  # SPC偏态分布报告
│   │   ├── spc_mixed_distribution.html   # SPC混合分布报告
│   │   └── ocap_response_report.html     # OCAP响应报告
│   ├── static/results/              # 检测结果存储目录
│   └── requirements.txt             # Python 依赖清单
│
├── ccharts/                         # ★ SPC 专业控制图算法库
│   ├── ccharts.py                   # 主模块（统一接口）
│   ├── xbar_rbar.py                 # Xbar-R 控制图
│   ├── xbar_sbar.py                 # Xbar-s 控制图
│   ├── imr.py / imrx.py / imrmr.py # I-MR 系列控制图
│   ├── p.py / u.py / c.py / np.py  # 计数型控制图
│   ├── ewma.py / cusum.py          # 高级控制图
│   └── tables.py                    # SPC 统计查表数据
│
├── front_end/                       # ★ 前端应用 (Vue 3)
│   ├── src/
│   │   ├── views/                   # ★ 页面组件 (24个)
│   │   │   ├── HomeView.vue             # 首页仪表盘
│   │   │   ├── ProductionLines.vue      # 产线列表
│   │   │   ├── ProductionLineDashboard.vue  # 产线仪表盘
│   │   │   ├── LineDataCollection.vue   # 数据采集
│   │   │   ├── LineControlChart.vue     # SPC控制图
│   │   │   ├── CapabilityAnalysis.vue   # 能力分析
│   │   │   ├── CapabilityAnalysisDetail.vue  # 能力分析详情
│   │   │   ├── ControlPlanList.vue      # 控制计划列表
│   │   │   ├── ControlPlanForm.vue      # 控制计划编制
│   │   │   ├── ControlPlanDetail.vue    # 控制计划详情
│   │   │   ├── MSAStudyList.vue         # MSA研究列表
│   │   │   ├── MSAStudyForm.vue         # MSA研究创建
│   │   │   ├── MSAStudyDetail.vue       # MSA研究详情
│   │   │   ├── OCAPList.vue             # OCAP列表
│   │   │   ├── OCAPForm.vue             # OCAP创建
│   │   │   ├── OCAPDetail.vue           # OCAP详情与执行
│   │   │   └── DetectByImg.vue          # AI图像检测
│   │   ├── components/              # 公共组件
│   │   │   ├── Menu.vue                 # 导航菜单
│   │   │   └── charts/                  # 图表组件
│   │   │       ├── CapabilityGauge.vue  # 能力仪表盘
│   │   │       ├── HistogramChart.vue   # 直方图
│   │   │       └── RunChart.vue         # 运行图
│   │   ├── api/                     # API 接口封装
│   │   ├── router/                  # Vue Router 配置
│   │   ├── stores/                  # Pinia 状态管理
│   │   ├── types/                   # TypeScript 类型定义
│   │   └── utils/                   # 工具函数
│   ├── vite.config.ts               # Vite 配置
│   └── package.json                 # 前端依赖清单
│
├── daily/                           # 开发日志
├── fig/                             # 参考图片
├── LICENSE                          # GNU GPL v3 许可证
└── README.md                        # 本文件
```

---

## 📡 主要 API 端点

### 生产线管理

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/production-lines | 获取产线列表 |
| POST | /api/production-lines | 创建产线 |
| GET | /api/production-lines/{id} | 获取产线详情 |
| PUT | /api/production-lines/{id} | 更新产线 |
| DELETE | /api/production-lines/{id} | 删除产线 |

### 控制计划

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/control-plans | 获取控制计划列表 |
| POST | /api/control-plans | 创建控制计划 |
| GET | /api/control-plans/{id} | 获取控制计划详情 |
| PUT | /api/control-plans/{id} | 更新控制计划 |
| POST | /api/control-plans/{id}/items | 添加控制计划项 |
| GET | /api/control-plans/{id}/export/excel | 导出Excel |
| GET | /api/control-plans/{id}/export/html | 导出HTML |

### MSA 测量系统分析

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/msa-studies | 获取MSA研究列表 |
| POST | /api/msa-studies | 创建MSA研究 |
| GET | /api/msa-studies/{id} | 获取研究详情 |
| POST | /api/msa-studies/{id}/calculate | 计算GR&R结果 |
| GET | /api/msa-studies/{id}/result | 获取分析结果 |

### 过程能力分析

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/capability-analyses | 获取能力分析列表 |
| POST | /api/capability-analyses | 创建能力分析 |
| POST | /api/capability-analyses/calculate | 计算能力指数 |
| GET | /api/capability-analyses/{id} | 获取分析详情 |
| GET | /api/capability-analyses/{id}/export/html | 导出HTML报告 |

### OCAP 异常应对

| 方法 | 路径 | 描述 |
|------|------|------|
| GET | /api/ocaps | 获取OCAP列表 |
| POST | /api/ocaps | 创建OCAP |
| GET | /api/ocaps/{id} | 获取OCAP详情 |
| POST | /api/ocaps/{id}/signals | 触发失控信号 |
| POST | /api/ocaps/{id}/execute | 执行OCAP步骤 |
| POST | /api/ocaps/{id}/root-cause | 提交根本原因分析 |
| POST | /api/ocaps/{id}/corrective-actions | 添加纠正措施 |
| GET | /api/ocaps/{id}/export/excel | 导出Excel |
| GET | /api/ocaps/{id}/export/html | 导出HTML报告 |

### 数据采集与控制图

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/measurement-data | 录入计量型数据 |
| POST | /api/attribute-data | 录入计数型数据 |
| GET | /api/production-lines/{id}/data | 获取产线数据历史 |
| GET | /api/control-chart-configs | 获取控制图配置 |
| POST | /api/control-chart-configs | 创建控制图配置 |
| GET | /api/control-chart-data | 获取控制图数据 |

### AI 缺陷检测

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/detectByImg | 单张图片检测 |
| POST | /api/images/batch-detect | 批量图片检测 |
| GET | /api/images | 获取检测历史记录 |
| GET | /api/images/{id} | 获取单条检测记录 |

---

## 📜 开源许可证

本项目采用 **GNU General Public License v3.0** 许可证开源。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

- **AIAG (Automotive Industry Action Group)** — APQP/PPAP/SPC/MSA/FMEA 参考手册
- **VDA (Verband der Automobilindustrie)** — 德国汽车工业协会质量管理标准
- **ISO/TS 16949 / IATF 16949** — 国际汽车行业质量管理体系标准
- **ccharts** 社区 — Python SPC 控制图计算库
- **Ultralytics** — YOLOv8 深度学习框架
- **Element Plus & ECharts** — 优秀的前端 UI 与可视化库

---

<p align="center">
  <strong>质量信息系统 (QIS)</strong><br>
  让质量管理更智能 · 让数据驱动决策<br>
  <em>Empowering Quality Management with Intelligence & Data</em>
</p>
