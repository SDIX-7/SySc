# PCB缺陷检测系统 - 前端

## Introduction

PCB缺陷检测系统是一个基于Vue.js开发的前端可视化项目，用于展示和分析PCB（印刷电路板）的缺陷检测结果。系统可以实时显示检测结果、历史检测记录，并提供质量控制图功能，帮助用户监控PCB生产质量。

该项目与后端Flask应用配合使用，实现完整的PCB缺陷检测功能。

## Environment

+ Vue 2.x.x
+ Node >= 6.0.0
+ Npm >= 3.0.0

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

## configuration

### 代理服务

需在config/index.js中进行配置，在配置完成后请重新启动项目方可生效

```javascript
proxyTable: {
  '/api' : {
    // target需更换为后端实际局域网内IP
    target: 'http://localhost:5000',
    ws: true,
    secure: false,
    changeOrigin: true,
    pathRewrite: {
      '^/api': ''
    }
  }
},
```

## 主要功能

1. **图片检测**：支持上传PCB图片进行缺陷检测
2. **检测结果展示**：实时显示检测后的图片和缺陷信息
3. **历史记录查询**：支持按时间范围查询历史检测记录
4. **质量控制图**：生成U图控制图，监控PCB生产质量
5. **异常报警**：当检测到异常时，后端会自动发送报警邮件

## Cautions

### 启动

项目使用 http://localhost:8080 进行访问，确保后端服务已启动。

### 构建与部署

```bash
# 构建生产版本
npm run build

# 将构建后的文件复制到后端static目录
# 后端将自动提供前端访问
cp -r dist ../back_end/front_end/
```

访问地址：`http://localhost:5000`

## 许可证

MIT License
