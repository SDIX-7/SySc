<template>
  <header class="navbar">
    <div class="navbar-container">
      <div class="navbar-brand">
        <div class="logo-container">
          <div class="logo-ring"></div>
          <div class="logo-core">
            <span class="logo-text">PCB</span>
          </div>
        </div>
        <div class="brand-text">
          <span class="brand-title">缺陷检测系统</span>
          <span class="brand-subtitle">质量控制平台</span>
        </div>
      </div>
      
      <nav class="navbar-menu">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="menu-item"
          :class="{ active: isActive(item.path) }"
        >
          <span class="menu-icon">
            <component :is="item.icon" />
          </span>
          <span class="menu-text">{{ item.name }}</span>
          <span class="menu-indicator"></span>
        </router-link>
      </nav>
      
      <div class="navbar-status">
        <div class="status-dot"></div>
        <span class="status-text">系统运行中</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import { 
  Camera, 
  Clock, 
  TrendCharts
} from '@element-plus/icons-vue'

const route = useRoute()

const menuItems = [
  { name: '图像检测', path: '/detect-by-img', icon: Camera },
  { name: '历史记录', path: '/history', icon: Clock },
  { name: '过程控制', path: '/process-control', icon: TrendCharts },
]

const isActive = (path: string) => {
  return route.path === path
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 70px;
  background: rgba(10, 14, 23, 0.95);
  border-bottom: 1px solid var(--border-color);
  backdrop-filter: blur(20px);
  z-index: 1000;
}

.navbar-container {
  max-width: 1600px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 40px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 16px;
}

.logo-container {
  position: relative;
  width: 45px;
  height: 45px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-ring {
  position: absolute;
  width: 100%;
  height: 100%;
  border: 2px solid var(--accent-primary);
  border-radius: 50%;
  animation: pulse-glow 2s ease-in-out infinite;
}

.logo-core {
  width: 35px;
  height: 35px;
  background: var(--accent-gradient);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-text {
  font-family: var(--font-display);
  font-size: 10px;
  font-weight: 700;
  color: var(--bg-primary);
  letter-spacing: 0.05em;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.brand-title {
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: 0.15em;
}

.brand-subtitle {
  font-family: var(--font-body);
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 8px;
}

.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  color: var(--text-secondary);
  text-decoration: none;
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  border-radius: var(--radius-sm);
  transition: all var(--transition-normal);
  overflow: hidden;
}

.menu-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.menu-item:hover {
  color: var(--text-primary);
}

.menu-item:hover::before {
  opacity: 1;
}

.menu-item.active {
  color: var(--accent-primary);
}

.menu-item.active::before {
  opacity: 1;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, transparent 100%);
}

.menu-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
}

.menu-icon :deep(svg) {
  width: 16px;
  height: 16px;
}

.menu-indicator {
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%) scaleX(0);
  width: 30px;
  height: 2px;
  background: var(--accent-gradient);
  border-radius: 1px;
  transition: transform var(--transition-normal);
}

.menu-item.active .menu-indicator {
  transform: translateX(-50%) scaleX(1);
}

.navbar-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.3);
  border-radius: var(--radius-sm);
}

.status-dot {
  width: 8px;
  height: 8px;
  background: var(--success);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.4);
  }
  50% {
    opacity: 0.8;
    box-shadow: 0 0 0 8px rgba(16, 185, 129, 0);
  }
}

.status-text {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--success);
  letter-spacing: 0.1em;
}

@media (max-width: 1200px) {
  .navbar-container {
    padding: 0 20px;
  }
  
  .menu-text {
    display: none;
  }
  
  .menu-item {
    padding: 10px 14px;
  }
}

@media (max-width: 768px) {
  .brand-text {
    display: none;
  }
  
  .navbar-status {
    display: none;
  }
}
</style>
