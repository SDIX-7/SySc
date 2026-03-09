<template>
  <div id="app">
    <router-view :key="$route.path" />
  </div>
</template>

<script setup lang="ts">
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', '微软雅黑', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  width: 100%;
  height: 100vh;
  margin: 0;
  padding: 0;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
}

.custom-confirm-dialog {
  border-radius: 12px !important;
  overflow: hidden;
}

.custom-confirm-dialog .el-message-box__header {
  padding: 20px 20px 10px;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
}

.custom-confirm-dialog .el-message-box__title {
  font-weight: 600;
  font-size: 18px;
  color: #1e293b;
}

.custom-confirm-dialog .el-message-box__content {
  padding: 20px;
  font-size: 15px;
  color: #475569;
}

.custom-confirm-dialog .el-message-box__btns {
  padding: 10px 20px 20px;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.custom-confirm-dialog .el-button {
  min-width: 100px;
  border-radius: 8px;
}

.el-message {
  top: 20px !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
}

.el-overlay {
  background-color: rgba(0, 0, 0, 0.5) !important;
  backdrop-filter: blur(2px);
}

.el-dialog {
  border-radius: 12px !important;
  overflow: hidden;
}

.el-dialog__header {
  padding: 20px !important;
  background: linear-gradient(135deg, #f8fafc, #f1f5f9);
  border-bottom: 1px solid #e2e8f0;
}

.el-dialog__title {
  font-weight: 600 !important;
  font-size: 18px !important;
  color: #1e293b !important;
}

.el-dialog__body {
  padding: 24px !important;
}

.el-dialog__footer {
  padding: 16px 24px !important;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;
}

</style>
