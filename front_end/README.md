# PCB缺陷检测系统 - 前端

## Introduction

PCB缺陷检测系统是一个基于Vue 3 + TypeScript开发的前端可视化项目，用于展示和分析PCB（印刷电路板）的缺陷检测结果。系统可以实时显示检测结果、历史检测记录，并提供质量控制图功能，帮助用户监控PCB生产质量。

该项目与后端FastAPI应用配合使用，实现完整的PCB缺陷检测功能。

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
- **Vue Router 4** - 路由管理
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

1. **图片检测**：
   - 支持上传PCB图片进行缺陷检测
   - 支持批量上传和检测
   - 实时显示检测进度和结果

2. **检测结果展示**：
   - 实时显示检测后的图片和缺陷信息
   - 标记缺陷位置和类型
   - 显示缺陷置信度和数量统计

3. **历史记录查询**：
   - 支持按时间范围查询历史检测记录
   - 支持按缺陷类型筛选
   - 详细展示每张PCB的检测信息

4. **质量控制图**：
   - 生成U图控制图，监控PCB生产质量
   - 实时显示25组样本数据
   - 标记异常点和异常规则
   - 支持查看异常详情

5. **异常报警**：
   - 当控制图检测到异常时，后端自动发送报警邮件
   - 支持自定义报警邮箱
   - 显示报警历史记录

6. **系统设置**：
   - 配置邮箱接收地址
   - 查看系统状态和版本信息

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

### 主要依赖说明

| 依赖 | 版本 | 用途 |
|------|------|------|
| vue | ^3.4.0 | 核心框架 |
| vue-router | ^4.2.0 | 路由管理 |
| pinia | ^2.1.0 | 状态管理 |
| element-plus | ^2.5.0 | UI组件库 |
| echarts | ^5.5.0 | 数据可视化 |
| axios | ^1.6.0 | HTTP请求 |
| typescript | ^5.3.0 | 类型支持 |
| vite | ^5.0.0 | 构建工具 |

## Cautions

### 启动前准备

1. 确保后端服务已启动，默认运行在 `http://localhost:5000`
2. 确保API代理配置正确，指向后端实际运行的IP地址
3. 安装所有依赖包

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

### 常见问题

1. **端口冲突**：如果5173端口被占用，Vite会自动使用下一个可用端口
2. **代理配置错误**：确保代理配置中的target指向正确的后端地址
3. **依赖安装失败**：尝试使用 `npm install --legacy-peer-deps` 命令安装依赖
4. **构建失败**：确保Node.js版本符合要求，推荐使用Node 18+
5. **类型检查错误**：运行 `npm run type-check` 查看详细错误信息

## 开发计划（1个月周期）

### 第1周：需求分析与架构设计

**里程碑：完成前端架构设计与技术选型**

| 任务 | 目标 |
|------|------|
| 需求调研与分析 | 明确PCB缺陷检测的业务需求和功能边界 |
| 技术选型确认 | 确定Vue 3 + TypeScript技术栈，评估可行性 |
| 组件架构设计 | 确定组件划分、路由结构、状态管理方案 |
| UI/UX设计 | 设计页面布局、交互流程、视觉规范 |

### 第2周：后端核心功能开发

**里程碑：完成后端核心API开发与测试**

此阶段主要为后端开发，前端配合接口联调。

### 第3周：前端开发与集成

**里程碑：完成前端页面开发与后端联调**

| 任务 | 目标 |
|------|------|
| 前端项目搭建 | 完成Vue 3项目初始化、路由配置、状态管理 |
| 图片检测页面 | 实现图片上传、检测结果展示、历史记录查询 |
| 控制图页面 | 使用ECharts实现U图可视化、异常标记展示 |
| 系统设置页面 | 实现邮箱配置、用户管理功能 |
| 前后端联调 | 完成API对接，修复集成问题 |

### 第4周：测试优化与部署

**里程碑：完成前端测试与生产部署**

| 任务 | 目标 |
|------|------|
| 功能测试 | 完成全部功能模块的测试用例编写与执行 |
| 性能优化 | 优化前端加载性能、组件渲染效率 |
| 响应式适配 | 确保页面在不同设备上的显示效果 |
| 构建部署 | 完成生产环境构建与部署配置 |

## 许可证

GNU GPL v3 License
