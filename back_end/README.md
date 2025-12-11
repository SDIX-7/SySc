# PCB缺陷检测系统 - 后端

## 项目介绍

本项目是一个基于Flask框架开发的PCB缺陷检测系统后端，提供图片检测、数据管理和控制图生成等功能。系统可以接收前端上传的PCB图片，使用深度学习模型进行缺陷检测，并将检测结果存储到数据库中。同时，系统还支持生成U图控制图，用于监控PCB生产质量。

## Quick Start

### 1. 安装依赖

```bash
# 进入后端目录
cd back_end

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 初始化数据库

系统使用SQLite数据库，首次运行时会自动创建数据库文件。

### 3. 运行应用

```bash
# 启动Flask应用
python app.py
```

应用将在 `http://localhost:5000` 上运行。

## 项目结构

```
back_end/
├── app.py                 # 主应用文件，包含API路由和数据库配置
├── database.db            # SQLite数据库文件（自动生成）
├── dataset_split/         # 数据集分割目录
│   ├── train/             # 训练集
│   └── PCB.yaml           # 数据集配置文件
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

## API接口说明

### 1. 图片检测

- **URL**: `/detectByImg`
- **方法**: POST
- **参数**: 
  - `file`: 上传的图片文件
- **返回**: 检测后的结果图片

### 2. 获取图片列表

- **URL**: `/images`
- **方法**: GET
- **参数**: 
  - `startDate`: 开始日期（可选）
  - `endDate`: 结束日期（可选）
- **返回**: 图片列表JSON数据

### 3. 获取单个图片信息

- **URL**: `/images/<int:image_id>`
- **方法**: GET
- **返回**: 单个图片的详细信息JSON数据

### 4. 添加图片记录

- **URL**: `/images`
- **方法**: POST
- **参数**: JSON格式的图片信息
- **返回**: 添加成功的图片信息JSON数据

### 5. 保存检测结果

- **URL**: `/images/detection_results`
- **方法**: POST
- **参数**: JSON格式的检测结果
- **返回**: 保存成功的消息

### 6. 获取控制图数据

- **URL**: `/control-chart-data`
- **方法**: GET
- **返回**: 控制图数据JSON，包含25组样本数据和异常检测结果

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
4. 控制图功能需要足够的数据量才能生成有意义的结果
5. 邮件发送功能需要在`email_utils.py`中配置正确的SMTP服务器信息

## 前端集成

后端提供了静态文件服务，可以直接访问前端构建后的文件。前端构建后，将`dist`目录复制到`front_end`目录下，后端将自动提供前端访问。

访问地址：`http://localhost:5000`

## 许可证

GNU GPL v3 License
