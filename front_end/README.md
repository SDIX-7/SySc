# 质量信息系统 (QIS) - 前端应用

## Introduction

质量信息系统是一个基于 Vue 3 + TypeScript 开发的企业级质量管理前端应用，为质量部门提供完整的质量管理工具集。系统实现了：

- **📊 SPC 实时监控**：多类型控制图可视化 + 异常标记 + 实时报警
- **📈 过程能力分析**：直方图、正态概率图、能力六芒星图
- **🔬 MSA 测量系统分析**：GR&R 方差分量图 + 可接受性判定
- **📋 控制计划管理**：AIAG 标准格式展示 + 版本对比
- **⚠️ OCAP 异常应对**：时间线流程图 + 根因分析 + 纠正措施跟踪
- **🤖 AI 缺陷检测**：实时检测 + 缺陷标注 + 历史查询
- **📑 报告导出**：Excel/HTML/PDF 多格式 + 自定义模板

该项目与后端 FastAPI 应用配合使用，构成完整的质量管理平台。

## Environment

+ Vue 3.x
+ TypeScript 5.x
+ Node >= 18.0.0
+ npm >= 8.0.0

**推荐使用 Node.js 18 或更高版本，以确保依赖安装和构建过程顺利进行。**

## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:5173
npm run dev

# build for production
npm run build

# preview production build
npm run preview

# type check
npm run type-check

# lint code
npm run lint
```

## 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 3 状态管理
- **Vue Router 4** - 路由管理（25个路由）
- **Element Plus** - Vue 3 UI 组件库
- **ECharts** - 数据可视化图表库
- **Axios** - HTTP 客户端
- **Tailwind CSS** - 原子化 CSS 框架

## 项目结构

```
front_end/
├── src/
│   ├── api/           # API 接口封装
│   ├── assets/        # 静态资源
│   ├── components/    # Vue 组件
│   │   └── charts/    # 图表组件库
│   ├── router/        # Vue Router 配置
│   ├── stores/        # Pinia 状态管理
│   ├── types/         # TypeScript 类型定义
│   ├── utils/         # 工具函数
│   ├── views/         # 页面视图
│   ├── App.vue        # 根组件
│   └── main.ts        # 入口文件
├── vite.config.ts     # Vite 配置
├── tsconfig.json      # TypeScript 配置
└── package.json       # 项目依赖
```

## 主要功能

### 1. 🏭 生产线管理

- **ProductionLines.vue** - 产线列表与概览
  - 产线创建/编辑/删除
  - 数据类型配置（计量型/计数型）
  - 绑定AI检测模型
  - 产线状态监控

- **ProductionLineDashboard.vue** - 产线仪表盘
  - 实时数据概览
  - 最近控制图状态
  - 能力指标摘要
  - 快捷操作入口

- **ProductionLineDetail.vue** - 产线详情
  - 详细配置信息
  - 关联文档列表
  - 历史数据分析

### 2. 📊 数据采集与监控

- **LineDataCollection.vue** - 数据采集
  - 计量型数据录入（单值/子组）
  - 计数型数据录入（缺陷数/不合格数）
  - 批量数据导入
  - 数据验证与校验

- **LineHistory.vue** - 历史数据查询
  - 时间范围筛选
  - 数据趋势图表
  - 异常记录追溯
  - 数据导出

- **DetectByImg.vue** - AI图像检测
  - 图片上传（支持批量）
  - 实时缺陷检测
  - 结果可视化标注
  - 检测历史管理

### 3. 📈 SPC 统计过程控制

- **LineControlChart.vue** - 控制图主界面
  - 多种控制图类型切换（Xbar-R/Xbar-s/I-MR/U/P/C/np）
  - 动态控制限计算
  - Western Electric 8大判异规则标记
  - 异常点高亮与详情
  - 控制图配置管理

- **ProcessControl.vue** - 过程控制中心
  - 多产线监控看板
  - 异常汇总视图
  - 报警通知列表
  - 快速响应入口

### 4. 📊 过程能力分析

- **CapabilityAnalysis.vue** - 能力分析列表
  - 历史分析记录
  - 筛选与搜索
  - 快速发起分析

- **CapabilityAnalysisForm.vue** - 发起能力分析
  - 规格限设置（USL/LSL/Target）
  - 数据选择（手动/自动导入）
  - 分析类型选择（过程/机器能力）
  - 正态性检验选项

- **CapabilityAnalysisDetail.vue** - 能力分析详情
  - **HistogramChart.vue** - 数据直方图（正态/偏态/混合分布拟合）
  - **CapabilityGauge.vue** - 能力仪表盘（Cp/Cpk/Pp/Ppk/Cm/Cmk）
  - **RunChart.vue** - 运行图（时间序列趋势）
  - 正态概率图（Q-Q Plot）
  - 统计参数汇总（均值、标准差、置信区间）
  - 结论与建议

- **CapabilityAnalysisHistory.vue** - 能力分析历史
  - 时间趋势对比
  - 能力指标演变
  - 改进效果追踪

### 5. 🔬 MSA 测量系统分析

- **MSAStudyList.vue** - MSA研究列表
  - 研究状态管理（草稿/进行中/完成）
  - 研究类型筛选（GR&R/偏倚/线性/稳定性）

- **MSAStudyForm.vue** - 创建MSA研究
  - 研究类型选择
  - 测量系统定义
  - 实验设计（零件数/操作员数/重复次数）
  - 随机化选项

- **MSAStudyDetail.vue** - MSA研究详情
  - 实验数据录入界面
  - GR&R 计算结果展示
  - **方差分量饼图**（重复性/再现性/零件/总变异）
  - **可接受性判定**（%GR&R <10%优秀/<30%可接受/>30%不可接受）
  - NDC（可区分类别数）评估
  - 改进建议

### 6. 📋 控制计划管理

- **ControlPlanList.vue** - 控制计划列表
  - 按产线筛选
  - 版本管理
  - 状态筛选（草稿/审核中/已发布/已归档）

- **ControlPlanForm.vue** - 编制控制计划
  - 基本信息（零件号、工序、版本）
  - 团队成员定义
  - 控制计划项编辑器
  - 特殊特性标识（CC/SC）
  - 反应计划关联OCAP

- **ControlPlanDetail.vue** - 控制计划详情
  - AIAG 标准格式展示
  - 完整表格视图
  - 版本对比功能
  - 导出（Excel/HTML/PDF）

### 7. ⚠️ OCAP 异常应对

- **OCAPList.vue** - OCAP列表
  - 按优先级排序
  - 状态筛选（开放/进行中/已关闭）
  - 按产线/信号类型筛选

- **OCAPForm.vue** - 创建/编辑OCAP
  - 失控信号定义
  - 优先级评分（严重度/频度/探测度）
  - 应对步骤设计（围堵/调查/纠正/预防）
  - 责任人指派

- **OCAPDetail.vue** - OCAP详情与执行
  - **时间线视图**：信号触发 → 围堵 → 调查 → 纠正 → 验证 → 关闭
  - **根本原因分析**：
    - 5Why 分析界面
    - 鱼骨图（人/机/料/法/环/测）
    - 因果关系记录
  - **纠正措施跟踪**：
    - 措施制定与责任人
    - 截止日期管理
    - 完成状态追踪
    - 效果验证记录
  - **证据管理**：照片/文档上传
  - **报告导出**：OCAP响应报告（HTML）

### 8. 🏠 首页仪表盘

- **HomeView.vue** - 系统首页
  - 系统概览卡片（产线数/活跃OCAP/近期能力研究）
  - 待办事项提醒
  - 最新异常警报
  - 快捷功能入口
  - 系统公告

### 9. 🧩 公共组件

- **Menu.vue** - 导航菜单
  - 模块化菜单结构
  - 权限控制显示
  - 响应式布局

- **charts/** - 图表组件库
  - **CapabilityGauge.vue** - 能力仪表盘
  - **HistogramChart.vue** - 直方图
  - **RunChart.vue** - 运行图

## 页面路由结构

```
/                           → HomeView（首页仪表盘）
/production-lines           → ProductionLines（产线列表）
/production-lines/:id       → ProductionLineDashboard（产线仪表盘）
/production-lines/:id/data-collection → LineDataCollection（数据采集）
/production-lines/:id/history         → LineHistory（历史数据）
/production-lines/:id/control-chart   → LineControlChart（控制图）
/production-lines/:id/capability-analysis → CapabilityAnalysis（能力分析列表）
/production-lines/:id/control-plans   → ControlPlanList（控制计划列表）
/production-lines/:id/ocaps           → OCAPList（OCAP列表）
/production-lines/:id/msa-studies     → MSAStudyList（MSA列表）
/control-plans               → ControlPlanList（全局控制计划）
/control-plans/new           → ControlPlanForm（新建控制计划）
/control-plans/:planId       → ControlPlanDetail（控制计划详情）
/ocaps                      → OCAPList（全局OCAP）
/ocaps/new                  → OCPForm（新建OCAP）
/ocaps/:ocapId              → OCAPDetail（OCAP详情执行）
/msa-studies                → MSAStudyList（全局MSA）
/msa-studies/new            → MSAStudyForm（新建MSA）
/msa-studies/:studyId       → MSAStudyDetail（MSA详情）
/capability-analysis/:analysisId → CapabilityAnalysisDetail（能力分析详情）
/capability-analysis/history        → CapabilityAnalysisHistory（能力分析历史）
```

## 典型用户操作流程

### 场景1：日常SPC监控（检验员/QI）

```
1. 登录系统 → 首页查看待办
2. 进入指定产线 → 数据采集页面
3. 录入本次检测数据（计量型/计数型）
4. 查看控制图更新 → 检查是否有异常标记
5. 如有异常 → 查看异常详情 → 通知质量工程师
6. 完成本次检测任务
```

### 场景2：异常处理（质量工程师/QE）

```
1. 收到异常报警通知
2. 进入OCAP列表 → 打开对应OCAP
3. 查看失控信号详情和时间线
4. 执行围堵行动（隔离可疑产品）
5. 开展根本原因分析（填写5Why或绘制鱼骨图）
6. 制定纠正措施并指派责任人
7. 跟踪措施执行情况
8. 验证措施有效性
9. 生成OCAP响应报告
10. 关闭OCAP
```

### 场景3：新产品导入（过程工程师/PE）

```
1. 创建新产线 → 配置基本参数
2. 进入MSA模块 → 发起测量系统分析
3. 设计实验方案（确定零件/操作员/重复次数）
4. 录入实验数据 → 查看GR&R结果
5. 如%GR&R>30% → 改进测量系统 → 重新分析
6. 如%GR&R≤30% → 进入下一步
7. 进入控制计划模块 → 编制控制计划
8. 依据PFMEA识别特殊特性 → 定义控制方法
9. 关联反应计划（OCAP）
10. 提交审核 → 批准发布
11. 发起初始过程能力研究
12. 收集数据 → 计算Pp/Ppk
13. 如Pp/Ppk≥1.67 → 批准量产
14. 如Pp/Ppk<1.67 → 过程改进 → 重新研究
15. 进入日常SPC监控阶段
```

### 场景4：定期管理评审（质量经理/QM）

```
1. 查看首页仪表盘 → 了解整体质量状况
2. 查看能力分析历史趋势
3. 审查未关闭的OCAP清单
4. 查看控制计划版本变更记录
5. 评审MSA系统整体表现
6. 生成月度/季度质量报告
7. 制定持续改进计划
```

## Configuration

### API 代理配置

前端通过代理服务访问后端API，需要在 `vite.config.ts` 中进行配置：

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      }
    }
  }
})
```

### 环境变量配置

在项目根目录创建 `.env` 文件配置环境变量：

```env
# API 基础地址
VITE_API_BASE_URL=http://localhost:5000/api

# 应用标题
VITE_APP_TITLE=质量信息系统 (QIS)
```

### Element Plus 主题定制

在 `src/styles/element-theme.scss` 中自定义主题变量：

```scss
$--color-primary: #409EFF;
$--color-success: #67C23A;
$--color-warning: #E6A23C;
$--color-danger: #F56C6C;
$--color-info: #909399;
```

### ECharts 全局配置

在 `src/utils/echarts-config.ts` 中统一配置 ECharts 全局选项：

```typescript
import * as echarts from 'echarts'

// 设置默认主题色和字体
echarts.registerTheme('qis', {
  color: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C'],
  textStyle: { fontFamily: 'Microsoft YaHei, sans-serif' }
})
```

### Pinia 状态持久化配置

使用 `pinia-plugin-persistedstate` 实现状态持久化：

```typescript
// src/stores/index.ts
import { createPinia } from 'pinia'
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate'

const pinia = createPinia()
pinia.use(piniaPluginPersistedstate)

// 在 store 中启用持久化
defineStore('user', {
  state: () => ({ ... }),
  persist: {
    key: 'qis-user',
    storage: localStorage,
    paths: ['token', 'userInfo']
  }
})
```

### 主要依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| vue | ^3.4.0 | 核心框架 |
| vue-router | ^4.2.0 | 路由管理（29个路由） |
| pinia | ^2.1.0 | 状态管理（用户/全局状态） |
| element-plus | ^2.5.0 | UI组件库（表单/表格/对话框） |
| echarts | ^5.5.0 | 数据可视化（控制图/直方图/仪表盘） |
| axios | ^1.6.0 | HTTP请求（API调用） |
| typescript | ^5.3.0 | 类型安全 |
| vite | ^5.0.0 | 构建工具 |
| @element-plus/icons-vue | ^2.3.0 | 图标库 |

## Cautions

### 启动前准备

1. 确保后端所有API服务正常运行（SPC/MSA/OCAP等模块）
2. 确保后端服务已启动，默认运行在 `http://localhost:5000`
3. 确保API代理配置正确，指向后端实际运行的IP地址
4. 安装所有依赖包

### 启动方式

项目使用 `http://localhost:5173` 进行访问，启动命令：

```bash
# 开发模式启动
npm run dev
```

### 构建与部署

```bash
# 构建生产版本
npm run build

# 将构建后的文件复制到后端目录
# 后端将自动提供前端访问
cp -r dist ../back_end/front_end/
```

部署后访问地址：`http://localhost:5000`

### 使用注意事项

1. **SPC 控制图**：需要足够的历史数据才能正常显示（建议至少25个子组）
2. **MSA 分析**：需要完整的实验数据（零件×操作员×重复次数）
3. **能力分析**：建议至少100个数据点以获得可靠的统计结论
4. **OCAP 执行**：需要按照规定的四阶段流程顺序进行（围堵→调查→纠正→验证）
5. **报告导出**：需要后端 report_service_new 服务支持

### 常见问题

1. **端口冲突**：如果5173端口被占用，Vite会自动使用下一个可用端口
2. **代理配置错误**：确保代理配置中的target指向正确的后端地址
3. **依赖安装失败**：尝试使用 `npm install --legacy-peer-deps` 命令安装依赖
4. **构建失败**：确保Node.js版本符合要求，推荐使用Node 18+
5. **类型检查错误**：运行 `npm run type-check` 查看详细错误信息
6. **控制图无数据**：检查是否已完成数据采集，确保有足够的历史数据
7. **MSA计算失败**：确认实验数据完整，所有单元格都已填写
8. **报告生成失败**：检查后端 report_service_new 服务是否正常运行

## 许可证

GNU GPL v3 License
