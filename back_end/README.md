# PCB缺陷检测系统 - 后端

## 项目介绍

本项目是一个基于FastAPI框架开发的PCB缺陷检测系统后端，提供图片检测、数据管理和控制图生成等功能。系统可以接收前端上传的PCB图片，使用深度学习模型进行缺陷检测，并将检测结果存储到数据库中。同时，系统还支持生成U图控制图，用于监控PCB生产质量。

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
├── main.py                # FastAPI 入口文件
├── app/                   # 应用主目录
│   ├── main.py            # FastAPI 应用配置
│   ├── config.py          # 配置管理
│   ├── database.py        # 数据库连接
│   ├── models/            # SQLAlchemy 模型
│   │   └── models.py      # 数据表定义
│   ├── routers/           # API 路由
│   │   └── api.py         # API 端点定义
│   ├── schemas/           # Pydantic 模型
│   └── services/          # 业务逻辑
├── functions/             # 功能模块
│   ├── detect_img.py      # 图片检测函数
│   ├── control_chart.py   # 控制图生成函数
│   └── email_utils.py     # 邮件发送工具
├── images/                # 临时存储上传的图片
├── static/                # 静态文件目录
│   └── results/           # 检测结果存储目录
│       ├── images/        # 检测结果图片
│       └── jsons/         # 检测结果JSON文件
└── requirements.txt       # Python依赖文件
```

## 技术栈

- **FastAPI** - 现代高性能 Python Web 框架
- **Pydantic** - 数据验证和序列化
- **SQLAlchemy 2.0** - ORM 数据库管理
- **Uvicorn** - ASGI 服务器
- **OpenCV 4.x** - 图像处理
- **YOLOv8** - 缺陷检测模型
- **SQLite** - 轻量级数据库

## API接口说明

### 1. 图片检测

- **URL**: `/api/detectByImg`
- **方法**: POST
- **参数**: 
  - `file`: 上传的图片文件
- **返回**: 检测后的结果图片
- **描述**: 接收前端上传的PCB图片，使用YOLOv8模型进行缺陷检测，并返回检测结果图片

### 2. 获取图片列表

- **URL**: `/api/images`
- **方法**: GET
- **参数**: 
  - `startDate`: 开始日期（可选，格式：YYYY-MM-DD HH:MM:SS）
  - `endDate`: 结束日期（可选，格式：YYYY-MM-DD HH:MM:SS）
- **返回**: 图片列表JSON数据
- **描述**: 获取检测历史记录，支持按时间范围筛选

### 3. 获取单个图片信息

- **URL**: `/api/images/<int:image_id>`
- **方法**: GET
- **返回**: 单个图片的详细信息JSON数据
- **描述**: 根据ID获取指定图片的详细检测信息

### 4. 添加图片记录

- **URL**: `/api/images`
- **方法**: POST
- **参数**: JSON格式的图片信息
- **返回**: 添加成功的图片信息JSON数据
- **描述**: 手动添加图片检测记录

### 5. 保存检测结果

- **URL**: `/api/images/detection_results`
- **方法**: POST
- **参数**: JSON格式的检测结果
- **返回**: 保存成功的消息
- **描述**: 保存检测结果到数据库

### 6. 获取控制图数据

- **URL**: `/api/control-chart-data`
- **方法**: GET
- **返回**: 控制图数据JSON，包含25组样本数据和异常检测结果
- **描述**: 生成U图控制图数据，每3张PCB为一个样本，返回最近25组数据

### 7. 获取邮箱设置

- **URL**: `/api/email-settings`
- **方法**: GET
- **返回**: 当前邮箱设置JSON数据
- **描述**: 获取当前用于接收报警邮件的邮箱地址

### 8. 更新邮箱设置

- **URL**: `/api/email-settings`
- **方法**: PUT
- **参数**: 
  - `email`: 新的邮箱地址
- **返回**: 更新后的邮箱设置JSON数据
- **描述**: 更新用于接收报警邮件的邮箱地址

### 9. 获取检测结果图片

- **URL**: `/results/images/<filename>`
- **方法**: GET
- **返回**: 检测结果图片
- **描述**: 获取保存的检测结果图片

### 10. 获取检测结果JSON

- **URL**: `/results/jsons/<filename>`
- **方法**: GET
- **返回**: 检测结果JSON数据
- **描述**: 获取保存的检测结果JSON文件

## 数据库模型

### Image表

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

## 控制图功能

系统支持生成U图控制图，用于监控PCB生产质量。主要特点：

1. 每3张PCB为一个样本进行计算
2. 返回最近25组数据
3. 包含所有8个异常规则的检测结果
4. 当检测到异常时自动发送报警邮件

## 注意事项

1. 确保模型文件存在且路径配置正确
2. 首次运行时会自动创建数据库
3. 检测结果会保存在`static/results`目录下
4. 控制图功能需要足够的数据量才能生成有意义的结果（建议至少75张PCB检测数据）
5. 邮件发送功能配置
   - 默认发送方邮箱：3600094151@qq.com
   - 默认接收方邮箱：2395365918@qq.com
   - 邮箱配置文件：`functions/email_utils.py`
   - 如需修改邮箱配置，请编辑`email_utils.py`文件中的相关参数
6. 可通过前端界面更新接收报警邮件的邮箱地址
7. 数据库自动初始化，首次运行时会创建`database.db`文件
8. 临时图片存储在`images`目录，检测完成后会自动处理

## 前端集成

后端提供了静态文件服务，可以直接访问前端构建后的文件。前端构建后，将`dist`目录复制到`front_end`目录下，后端将自动提供前端访问。

访问地址：`http://localhost:5000`

## 开发计划（1个月周期）

### 第1周：需求分析与架构设计

**里程碑：完成后端架构设计与技术选型**

| 任务 | 目标 |
|------|------|
| 需求调研与分析 | 明确PCB缺陷检测的业务需求和功能边界 |
| 技术选型确认 | 确定FastAPI技术栈，评估可行性 |
| 数据库设计 | 完成ER图设计，定义核心数据表结构 |
| API接口设计 | 设计RESTful API规范，编写接口文档 |

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

**里程碑：完成后端与前端的联调**

| 任务 | 目标 |
|------|------|
| API联调支持 | 配置CORS，支持前端跨域请求 |
| 接口优化 | 根据前端需求优化API响应格式 |
| 错误处理 | 完善异常处理和错误响应 |

### 第4周：测试优化与部署

**里程碑：完成后端测试与生产部署**

| 任务 | 目标 |
|------|------|
| 单元测试 | 编写核心模块的单元测试 |
| 性能优化 | 优化检测速度、数据库查询性能 |
| 异常报警功能 | 实现邮件通知与AI分析报警 |
| 部署配置 | 编写部署文档，配置生产环境 |

## 许可证

GNU GPL v3 License
