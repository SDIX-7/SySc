# 质量信息系统

一个基于 Flask + Vue 的PCB缺陷检测与质量信息系统，包含图片缺陷检测、控制图分析、异常报警等功能。

本项目基于 [YOLOv8-model-improvement](https://github.com/Zwc2003/YOLOv8-model-improvement) 项目进行二次开发。

## 项目结构

```
├── back_end/      # Flask 后端
│   ├── dataset_split/  # 数据集分割
│   ├── functions/      # 功能模块
│   └── static/         # 静态文件
├── front_end/     # Vue 前端
├── email_test.py  # 邮件测试脚本
├── LICENSE
└── README.md
```

## 技术栈

### 后端 (back_end/)
- Flask - Python Web 框架
- OpenCV - 图像处理
- SQLAlchemy - 数据库管理
- Marshmallow - 数据序列化
- 深度学习框架 - 缺陷检测

### 前端 (front_end/)
- Vue.js - JavaScript 框架
- Vuex - 状态管理
- Vue Router - 路由管理

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
   - 邮件通知
   - 异常类型识别

## 界面展示

界面图片位于项目根目录的 `fig/` 文件夹中，展示了系统的主要功能界面：

### 主要功能界面

![界面1](fig/22.png)
![界面2](fig/28.png)
![界面3](fig/33.png)
![界面4](fig/37.png)
![界面5](fig/46.png)
![界面6](fig/59.png)

## 安装与运行

### 后端安装

```bash
# 进入后端目录
cd back_end

# 安装依赖
pip install -r requirements.txt

# 运行后端服务
python app.py
```

### 前端安装

```bash
# 进入前端目录
cd front_end

# 安装依赖
npm install

# 运行前端服务
npm run dev
```

## 配置说明

### 后端配置

- `app.py` - 主应用配置
- `functions/` - 业务逻辑函数
- `static/` - 静态文件目录
- `images/` - 图片存储目录

### 前端配置

- `config/` - Vue 配置文件
- `src/` - 源代码目录
- `src/components/` - Vue 组件
- `src/views/` - 页面视图

## 控制图异常检测规则

1. 点超出 3σ 控制线
2. 连续 7 点在中心线同侧
3. 连续 6 点递增或递减
4. 连续 14 点相邻点上下交替
5. 连续 3 点中有 2 点在 2σ 控制线外
6. 连续 5 点中有 4 点在 1σ 控制线外
7. 连续 15 点在 1σ 控制线内
8. 连续 8 点在中心线两侧且无 1 点在 1σ 控制线内

## 邮件报警配置

在 `back_end/functions/email_utils1.py` 中配置邮件服务器信息：

```python
# 修改以下邮件配置信息
smtp_server = 'smtp.qq.com'
smtp_port = 465
sender_email = 'your_email@qq.com'
password = 'your_email_password'  # 替换为真实授权码
```

**注意：** 修改好后请将文件名改为 `email_utils.py`

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

2. 部署后端服务（可使用 Gunicorn、uWSGI 等）
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## 许可证

GNU GPL v3 License

## 联系方式

如有问题或建议，请联系项目维护者。