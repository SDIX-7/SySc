# SPC信息系统

一个基于 FastAPI + Vue 3 的PCB缺陷检测与质量信息系统，包含图片缺陷检测、控制图分析、异常报警等功能。


## 项目结构

```
├── back_end/          # FastAPI 后端
│   ├── app/           # 应用主目录
│   │   ├── config.py  # 配置文件
│   │   ├── database.py # 数据库连接
│   │   ├── main.py    # FastAPI 入口
│   │   ├── models/    # SQLAlchemy 模型
│   │   ├── routers/   # API 路由
│   │   ├── schemas/   # Pydantic 模型
│   │   └── services/  # 业务逻辑
│   ├── functions/     # 功能模块
│   └── static/        # 静态文件
├── front_end/         # Vue 3 前端
│   ├── src/
│   │   ├── api/       # API 接口
│   │   ├── assets/    # 静态资源
│   │   ├── components/# Vue 组件
│   │   ├── router/    # Vue Router
│   │   ├── stores/    # Pinia 状态管理
│   │   ├── types/     # TypeScript 类型
│   │   ├── utils/     # 工具函数
│   │   └── views/     # 页面视图
│   └── vite.config.ts # Vite 配置
├── LICENSE
└── README.md
```

## 技术栈

### 后端 (back_end/)
- **FastAPI** - 现代高性能 Python Web 框架
- **Pydantic** - 数据验证和序列化
- **SQLAlchemy 2.0** - ORM 数据库管理
- **Uvicorn** - ASGI 服务器
- **OpenCV 4.x** - 图像处理
- **YOLOv8** - 缺陷检测模型
- **SQLite** - 轻量级数据库

### 前端 (front_end/)
- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全
- **Vite** - 下一代前端构建工具
- **Pinia** - Vue 3 状态管理
- **Vue Router 4** - 路由管理
- **Element Plus** - Vue 3 UI 组件库
- **ECharts** - 数据可视化
- **Axios** - HTTP 客户端

## 功能特性

1. **PCB缺陷检测**
   - 图片上传与检测
   - 缺陷类型识别
   - 检测结果可视化
   - 历史检测记录查询

2. **数据采集与管理**
   - 质量数据录入
   - 历史数据查询

3. **控制图分析**
   - U图控制图绘制
   - 实时数据监控
   - 8种异常检测规则
   - 异常自动报警

4. **异常报警**
   - 邮件通知（AI分析）
   - 异常类型识别

## 安装与运行

### 系统要求

- Python 3.8+
- Node.js 18+
- npm 8+

### 后端安装与运行

```bash
# 进入后端目录
cd back_end

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建.env文件并配置环境变量
# 在.env文件中添加以下内容：
# DEEPSEEK_API_KEY=xxxxxxx

# 运行后端服务
python main.py
```

后端服务将在 `http://localhost:5000` 上运行。
API 文档地址：`http://localhost:5000/docs`

### 前端安装与运行

```bash
# 进入前端目录
cd front_end

# 安装依赖
npm install

# 运行前端开发服务
npm run dev
```

前端服务将在 `http://localhost:5173` 上运行。

## API 文档

FastAPI 自动生成 API 文档：

- Swagger UI: `http://localhost:5000/docs`
- ReDoc: `http://localhost:5000/redoc`

## 主要 API 端点

| 方法 | 路径 | 描述 |
|------|------|------|
| POST | /api/detectByImg | 上传图片进行缺陷检测 |
| GET | /api/images | 获取检测历史记录 |
| GET | /api/control-chart-data | 获取控制图数据 |
| GET | /api/email-settings | 获取邮箱设置 |
| PUT | /api/email-settings | 更新邮箱设置 |
| POST | /api/login | 用户登录 |
| POST | /api/logout | 用户登出 |

## 控制图异常检测规则

1. 点超出 3σ 控制线
2. 连续 9 点在中心线同侧
3. 连续 6 点递增或递减
4. 连续 14 点相邻点上下交替
5. 连续 3 点中有 2 点在 2σ 控制线外
6. 连续 5 点中有 4 点在 1σ 控制线外
7. 连续 15 点在 1σ 控制线内
8. 连续 8 点在中心线两侧且无 1 点在 1σ 控制线内

## 开发计划（1个月周期）

### 第1周：需求分析与架构设计

**里程碑：完成系统架构设计与技术选型**

| 任务 | 目标 |
|------|------|
| 需求调研与分析 | 明确PCB缺陷检测的业务需求和功能边界 |
| 技术选型确认 | 确定FastAPI + Vue 3技术栈，评估可行性 |
| 数据库设计 | 完成ER图设计，定义核心数据表结构 |
| API接口设计 | 设计RESTful API规范，编写接口文档 |
| 前端架构设计 | 确定组件划分、路由结构、状态管理方案 |

### 第2周：后端核心功能开发

**里程碑：完成后端核心API开发与测试**

| 任务 | 目标 |
|------|------|
| 项目框架搭建 | 完成FastAPI项目结构、数据库连接、配置管理 |
| 用户认证模块 | 实现JWT登录认证、用户权限管理 |
| 图片检测接口 | 对接YOLOv8模型，实现图片上传与缺陷检测 |
| 数据存储模块 | 实现检测结果的数据库存储与查询 |
| 控制图计算模块 | 实现U图控制图数据计算与异常检测算法 |

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

**里程碑：完成系统测试与生产部署**

| 任务 | 目标 |
|------|------|
| 功能测试 | 完成全部功能模块的测试用例编写与执行 |
| 性能优化 | 优化检测速度、前端加载性能 |
| 异常报警功能 | 实现邮件通知与AI分析报警 |
| 部署配置 | 编写部署文档，配置生产环境 |
| 项目交付 | 整理文档、代码审查、最终演示 |

## 开发与部署

### 开发环境

- Python 3.8+
- Node.js 18+
- npm 8+

### 生产部署

1. 构建前端项目
   ```bash
   cd front_end
   npm run build
   ```

2. 部署后端服务
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 app.main:app
   ```

## 许可证

GNU GPL v3 License

## 联系方式

自己去发现
