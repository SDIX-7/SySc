# PCB缺陷检测系统 - 前端

## Introduction

PCB缺陷检测系统是一个基于Vue.js开发的前端可视化项目，用于展示和分析PCB（印刷电路板）的缺陷检测结果。系统可以实时显示检测结果、历史检测记录，并提供质量控制图功能，帮助用户监控PCB生产质量。

该项目与后端Flask应用配合使用，实现完整的PCB缺陷检测功能。

## Environment

+ Vue 2.x.x
+ Node >= 18.0.0
+ npm >= 8.0.0

**推荐使用 Node.js 18 或更高版本，以确保依赖安装和构建过程顺利进行。**

## Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```

## Configuration

### 代理服务配置

前端通过代理服务访问后端API，需要在 `config/index.js` 中进行配置，配置完成后请重新启动项目方可生效。

```javascript
proxyTable: {
  '/api': {
    // target需更换为后端实际运行的IP地址
    // 本地开发时默认为 http://localhost:5000
    target: 'http://localhost:5000',
    ws: true,                    // 启用WebSocket支持
    secure: false,               // 允许非HTTPS连接
    changeOrigin: true,          // 允许跨域请求
    pathRewrite: {
      '^/api': ''               // 重写URL，移除/api前缀
    }
  }
}
```

### 主要依赖说明

- **Element UI** - 基于 Vue 2.x 的桌面端组件库
- **ECharts** - 用于生成控制图和数据可视化
- **Axios** - 用于发送HTTP请求
- **Vue Router** - 路由管理
- **Vuex** - 状态管理
- **Socket.io-client** - WebSocket通信支持
- **ECharts** - 数据可视化图表库

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

## Cautions

### 启动前准备

1. 确保后端服务已启动，默认运行在 `http://localhost:5000`
2. 确保代理配置正确，指向后端实际运行的IP地址
3. 安装所有依赖包

### 启动方式

项目使用 `http://localhost:8080` 进行访问，启动命令：

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

1. **端口冲突**：如果8080端口被占用，可以在 `config/index.js` 中修改端口号
2. **代理配置错误**：确保代理配置中的target指向正确的后端地址
3. **依赖安装失败**：尝试使用 `npm install --legacy-peer-deps` 命令安装依赖
4. **构建失败**：确保Node.js版本符合要求，推荐使用Node 18+

## 许可证

GNU GPL v3 License
