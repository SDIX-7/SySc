<template>
  <div class="page-container">
    <Menu />
    
    <div class="hero-section">
      <div class="hero-content">
        <div class="hero-badge animate-slide-up">
          <span class="badge-dot"></span>
          <span>通用SPC采集和监测系统</span>
        </div>
        <h1 class="hero-title animate-slide-up delay-1">
          <span class="title-line">智能</span>
          <span class="title-line gradient-text">统计过程控制</span>
        </h1>
        <p class="hero-description animate-slide-up delay-2">
          支持多产线管理、多种控制图类型、GB 2828抽样方案，实时采集和分析生产质量数据。
        </p>
        <div class="hero-actions animate-slide-up delay-3">
          <router-link to="/production-lines" class="btn-primary">
            <span>产线管理</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </router-link>
        </div>
      </div>
      
      <div class="hero-visual animate-fade-in delay-2">
        <div class="visual-grid">
          <div class="grid-item" v-for="i in 9" :key="i" :style="{ animationDelay: `${i * 0.1}s` }">
            <div class="grid-inner"></div>
          </div>
        </div>
        <div class="visual-ring"></div>
        <div class="visual-ring inner"></div>
      </div>
    </div>
    
    <div class="features-section">
      <div class="section-header">
        <h2 class="section-title">核心功能</h2>
        <p class="section-subtitle">强大的质量保障工具</p>
      </div>
      
      <div class="features-grid">
        <div class="feature-card animate-slide-up" v-for="(feature, index) in features" :key="index" :style="{ animationDelay: `${index * 0.1}s` }">
          <div class="feature-icon">
            <component :is="feature.icon" />
          </div>
          <h3 class="feature-title">{{ feature.title }}</h3>
          <p class="feature-description">{{ feature.description }}</p>
          <router-link :to="feature.link" class="feature-link">
            <span>了解更多</span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </router-link>
        </div>
      </div>
    </div>
    
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card animate-slide-up" v-for="(stat, index) in stats" :key="index" :style="{ animationDelay: `${index * 0.1}s` }">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Menu from '@/components/Menu.vue'
import { Camera, TrendCharts, Setting } from '@element-plus/icons-vue'

const features = [
  {
    title: '产线管理',
    description: '管理多条生产线，配置数据类型、控制图类型和抽样方案。',
    icon: Setting,
    link: '/production-lines'
  },
  {
    title: '数据采集',
    description: '支持图片和Excel数据采集，自动数据校验和预处理。',
    icon: TrendCharts,
    link: '/production-lines'
  },
  {
    title: 'SPC控制图',
    description: '支持X-R图、X-s图、P图、NP图、C图、U图等多种控制图，实时监控生产质量。',
    icon: TrendCharts,
    link: '/production-lines'
  },
  {
    title: '过程能力分析',
    description: '计算Cp、Cpk、Pp、Ppk等能力指数，评估过程能力是否满足质量要求。',
    icon: TrendCharts,
    link: '/capability-analysis/history'
  }
]

const stats = [
  { value: '6种', label: '控制图类型' },
  { value: '100+', label: '产线支持' },
  { value: '99.5%', label: '数据准确率' },
  { value: '24/7', label: '全天候运行' }
]
</script>

<style scoped>
.hero-section {
  min-height: calc(100vh - 70px);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 60px;
  align-items: center;
  padding: 60px 80px;
  max-width: 1600px;
  margin: 0 auto;
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: rgba(0, 212, 255, 0.1);
  border: 1px solid var(--border-color);
  border-radius: 100px;
  width: fit-content;
  font-family: var(--font-mono);
  font-size: 12px;
  color: var(--accent-primary);
  letter-spacing: 0.05em;
}

.badge-dot {
  width: 6px;
  height: 6px;
  background: var(--accent-primary);
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.hero-title {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.title-line {
  font-family: var(--font-display);
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: 0.02em;
}

.gradient-text {
  background: var(--accent-gradient);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.125rem;
  color: var(--text-secondary);
  max-width: 500px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  gap: 16px;
  margin-top: 16px;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 16px 32px;
  background: var(--accent-gradient);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--bg-primary);
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
  cursor: pointer;
  transition: all var(--transition-normal);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 40px rgba(0, 212, 255, 0.3);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 16px 32px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-family: var(--font-display);
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
  transition: all var(--transition-normal);
}

.btn-secondary:hover {
  border-color: var(--accent-primary);
  color: var(--accent-primary);
}

.hero-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  height: 500px;
}

.visual-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  transform: rotate(45deg);
}

.grid-item {
  width: 100px;
  height: 100px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  animation: grid-pulse 3s ease-in-out infinite;
}

.grid-inner {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, transparent 100%);
  border-radius: inherit;
}

.visual-ring {
  position: absolute;
  width: 400px;
  height: 400px;
  border: 1px solid var(--border-color);
  border-radius: 50%;
  animation: ring-rotate 20s linear infinite;
}

.visual-ring.inner {
  width: 300px;
  height: 300px;
  animation-direction: reverse;
  animation-duration: 15s;
}

@keyframes grid-pulse {
  0%, 100% { opacity: 0.5; }
  50% { opacity: 1; }
}

@keyframes ring-rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.features-section {
  padding: 80px;
  max-width: 1600px;
  margin: 0 auto;
}

.section-header {
  text-align: center;
  margin-bottom: 60px;
}

.section-title {
  font-family: var(--font-display);
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.section-subtitle {
  font-size: 1rem;
  color: var(--text-muted);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.feature-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 32px;
  transition: all var(--transition-normal);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--accent-gradient);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform var(--transition-normal);
}

.feature-card:hover {
  border-color: var(--border-glow);
  transform: translateY(-4px);
  box-shadow: var(--shadow-glow);
}

.feature-card:hover::before {
  transform: scaleX(1);
}

.feature-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0, 212, 255, 0.1);
  border-radius: var(--radius-sm);
  margin-bottom: 20px;
  color: var(--accent-primary);
}

.feature-icon :deep(svg) {
  width: 24px;
  height: 24px;
}

.feature-title {
  font-family: var(--font-display);
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  letter-spacing: 0.05em;
}

.feature-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 20px;
}

.feature-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--accent-primary);
  font-family: var(--font-display);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  text-decoration: none;
  transition: gap var(--transition-normal);
}

.feature-link:hover {
  gap: 10px;
}

.stats-section {
  padding: 60px 80px;
  max-width: 1600px;
  margin: 0 auto;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
}

.stat-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: 32px;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 3px;
  background: var(--accent-gradient);
}

.stat-value {
  font-family: var(--font-display);
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--accent-primary);
  margin-bottom: 8px;
}

.stat-label {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

@media (max-width: 1200px) {
  .hero-section {
    grid-template-columns: 1fr;
    text-align: center;
    padding: 40px;
  }
  
  .hero-content {
    align-items: center;
  }
  
  .hero-visual {
    display: none;
  }
  
  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .features-grid,
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .btn-primary,
  .btn-secondary {
    width: 100%;
    justify-content: center;
  }
}
</style>
