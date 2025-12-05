<template>
  <div class="container">
    <Menu></Menu>
    <div class="content">
      <h1>过程控制</h1>
      <div class="chart-container">
        <div class="chart-header">
          <div class="chart-title">
            <h3>U图控制图 - 单位缺陷数控制</h3>
            <div class="update-info" v-if="lastUpdateTime">
              最后更新: {{ formatUpdateTime(lastUpdateTime) }}
            </div>
          </div>
          <div class="chart-actions">
            <el-button type="primary" @click="loadChartData" size="small">
              <i class="el-icon-refresh"></i> 刷新数据
            </el-button>
            <el-button @click="toggleAutoRefresh" size="small" :type="autoRefreshEnabled ? 'success' : 'info'">
              <i :class="autoRefreshEnabled ? 'el-icon-video-play' : 'el-icon-video-pause'"></i>
              {{ autoRefreshEnabled ? '自动刷新(30s)' : '暂停刷新' }}
            </el-button>
          </div>
        </div>
        <div id="controlChart" class="chart"></div>
        <div class="chart-legend">
          <div class="legend-item">
            <span class="legend-dot normal"></span>
            <span>正常点 (蓝色)</span>
          </div>
          <div class="legend-item">
            <span class="legend-dot abnormal"></span>
            <span>异常点 (红色)</span>
          </div>
        </div>
        <div>end-placeholder</div>
        <div class="stat-info">
          <el-row :gutter="20">
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-label">样本总数</div>
                <div class="stat-value">{{ statistics.totalSamples || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-label">平均u值</div>
                <div class="stat-value">{{ statistics.meanU.toFixed(4) || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-label">控制上限(UCL)</div>
                <div class="stat-value">{{ statistics.ucl.toFixed(4) || 0 }}</div>
              </div>
            </el-col>
            <el-col :span="6">
              <div class="stat-card">
                <div class="stat-label">异常点数量</div>
                <div class="stat-value" :class="{ 'abnormal-count': statistics.totalAbnormal > 0 }">
                  {{ statistics.totalAbnormal || 0 }}
                </div>
              </div>
            </el-col>
          </el-row>
        </div>
        <div class="rules-container">
          <h4>异常规则检测结果</h4>
          <el-table :data="ruleResults" style="width: 100%">
            <el-table-column prop="rule" label="规则" width="80"></el-table-column>
            <el-table-column prop="description" label="描述"></el-table-column>
            <el-table-column prop="abnormalCount" label="异常点数" width="100"></el-table-column>
            <el-table-column prop="status" label="状态" width="80">
              <template slot-scope="scope">
                <el-tag :type="scope.row.abnormalCount > 0 ? 'danger' : 'success'" size="small">
                  {{ scope.row.abnormalCount > 0 ? '异常' : '正常' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Menu from '@/components/Menu.vue'
import * as echarts from 'echarts'
import { getControlChartData } from '@/api/api.js'

export default {
  name: 'ProcessControl',
  components: {
    Menu
  },
  data () {
    return {
      chart: null,
      chartData: null,
      statistics: {
        totalSamples: 0,
        totalDefects: 0,
        meanU: 0,
        ucl: 0,
        totalAbnormal: 0
      },
      ruleResults: [
        { rule: '规则1', description: '1个点落在A区以外', abnormalCount: 0, status: 'normal' },
        { rule: '规则2', description: '9个点在中心线一侧', abnormalCount: 0, status: 'normal' },
        { rule: '规则3', description: '6点连续递增或递减', abnormalCount: 0, status: 'normal' },
        { rule: '规则4', description: '14点上下交替', abnormalCount: 0, status: 'normal' },
        { rule: '规则5', description: '2/3点落在A区', abnormalCount: 0, status: 'normal' },
        { rule: '规则6', description: '4/5点落在C区以外', abnormalCount: 0, status: 'normal' },
        { rule: '规则7', description: '15点连续在C区以内', abnormalCount: 0, status: 'normal' },
        { rule: '规则8', description: '8点落在中心线两侧但无C区点', abnormalCount: 0, status: 'normal' }
      ],
      refreshTimer: null,
      autoRefreshEnabled: true,
      refreshInterval: 30000, // 默认30秒刷新一次
      lastUpdateTime: null
    }
  },
  mounted () {
    this.initChart()
    this.loadChartData()
    this.startAutoRefresh()
    // 监听页面可见性变化，当页面重新可见时刷新数据
    document.addEventListener('visibilitychange', this.handleVisibilityChange)
    // 监听窗口聚焦事件
    window.addEventListener('focus', this.handleWindowFocus)
  },
  beforeDestroy () {
    if (this.chart) {
      this.chart.dispose()
    }
    this.stopAutoRefresh()
    document.removeEventListener('visibilitychange', this.handleVisibilityChange)
    window.removeEventListener('focus', this.handleWindowFocus)
  },
  activated () {
    // 当组件从缓存中激活时刷新数据
    this.loadChartData()
    this.startAutoRefresh()
  },
  deactivated () {
    // 当组件被缓存时停止自动刷新
    this.stopAutoRefresh()
  },
  methods: {
    formatUpdateTime (date) {
      const now = new Date(date)
      const hours = now.getHours().toString().padStart(2, '0')
      const minutes = now.getMinutes().toString().padStart(2, '0')
      const seconds = now.getSeconds().toString().padStart(2, '0')
      return `${hours}:${minutes}:${seconds}`
    },
    initChart () {
      this.chart = echarts.init(document.getElementById('controlChart'))
    },
    loadChartData () {
      getControlChartData().then(response => {
        this.chartData = response.data
        this.lastUpdateTime = new Date()
        this.updateStatistics()
        this.updateRuleResults()
        this.renderChart()
      }).catch(error => {
        console.error('Failed to load control chart data:', error)
      })
    },
    updateStatistics () {
      const { u_list: uValues, abnormal_rules: abnormalRules } = this.chartData
      this.statistics.totalSamples = uValues.length
      this.statistics.meanU = this.chartData.center_line
      this.statistics.ucl = this.chartData.approx_ucl

      // 计算abnormal_rules中所有异常点的并集（避免重复计数）
      const uniqueAbnormalPoints = new Set()
      if (abnormalRules) {
        for (const sampleIndices of Object.values(abnormalRules)) {
          if (sampleIndices && sampleIndices.length > 0) {
            // 添加到Set中会自动去重
            sampleIndices.forEach(index => uniqueAbnormalPoints.add(index))
          }
        }
      }

      // 确保异常点总数不超过样本总数
      const totalAbnormalCount = Math.min(uniqueAbnormalPoints.size, uValues.length)
      this.statistics.totalAbnormal = totalAbnormalCount
    },
    updateRuleResults () {
      const { abnormal_rules: abnormalRules } = this.chartData
      // 确保ruleResults有初始的8个规则配置
      const ruleDescriptions = [
        '1个点落在A区以外',
        '9个点在中心线一侧',
        '6点连续递增或递减',
        '14点上下交替',
        '2/3点落在A区',
        '4/5点落在C区以外',
        '15点连续在C区以内',
        '8点落在中心线两侧但无C区点'
      ]

      this.ruleResults = ruleDescriptions.map((desc, index) => {
        const ruleNum = index + 1
        const sampleIndices = abnormalRules && abnormalRules[ruleNum] ? abnormalRules[ruleNum] : []
        return {
          rule: `规则${ruleNum}`,
          description: desc,
          abnormalCount: sampleIndices ? sampleIndices.length : 0,
          status: sampleIndices && sampleIndices.length > 0 ? 'abnormal' : 'normal'
        }
      })
    },
    renderChart () {
      if (!this.chart || !this.chartData) return
      const { u_list: uValues, approx_ucl: upperControlLimit, center_line: meanU, abnormal_points: allAbnormalIndices } = this.chartData
      const sampleLabels = Array.from({ length: uValues.length }, (_, i) => `样本 ${i + 1}`)
      const uData = uValues.map((value, index) => ({
        value: value,
        itemStyle: {
          color: allAbnormalIndices.includes(index) ? '#ff4d4f' : '#1890ff'
        }
      }))
      const option = {
        tooltip: {
          trigger: 'axis',
          formatter: function (params) {
            let result = params[0].name + '<br/>'
            params.forEach(param => {
              result += `${param.marker}${param.seriesName}: ${param.value}<br/>`
            })
            return result
          }
        },
        legend: {
          data: ['u值', '中心线', '控制上限', '控制下限']
        },
        grid: {
          left: '3%',
          right: '4%',
          bottom: '10%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: sampleLabels
        },
        yAxis: {
          type: 'value',
          name: '缺陷数'
        },
        series: [
          {
            name: 'u值',
            type: 'line',
            data: uData,
            symbol: 'circle',
            symbolSize: 8,
            emphasis: {
              focus: 'series'
            }
          },
          {
            name: '中心线',
            type: 'line',
            data: Array(uValues.length).fill(meanU),
            lineStyle: {
              color: '#52c41a',
              type: 'dashed'
            },
            symbol: 'none'
          },
          {
            name: '控制上限',
            type: 'line',
            data: Array(uValues.length).fill(upperControlLimit),
            lineStyle: {
              color: '#ff4d4f',
              type: 'dashed'
            },
            symbol: 'none'
          },
          {
            name: '控制下限',
            type: 'line',
            data: Array(uValues.length).fill(0),
            lineStyle: {
              color: '#ff4d4f',
              type: 'dashed'
            },
            symbol: 'none'
          }
        ]
      }

      this.chart.setOption(option)
    },
    startAutoRefresh () {
      if (this.autoRefreshEnabled) {
        this.stopAutoRefresh() // 先停止现有的定时器
        this.refreshTimer = setInterval(() => {
          this.loadChartData()
        }, this.refreshInterval)
      }
    },
    stopAutoRefresh () {
      if (this.refreshTimer) {
        clearInterval(this.refreshTimer)
        this.refreshTimer = null
      }
    },
    handleVisibilityChange () {
      if (!document.hidden) {
        this.loadChartData() // 当页面重新可见时刷新数据
      }
    },
    handleWindowFocus () {
      this.loadChartData() // 当窗口获得焦点时刷新数据
    },
    toggleAutoRefresh () {
      this.autoRefreshEnabled = !this.autoRefreshEnabled
      if (this.autoRefreshEnabled) {
        this.startAutoRefresh()
      } else {
        this.stopAutoRefresh()
      }
    },
    refreshNow () {
      this.loadChartData()
    }
  }
}
</script>

<style scoped>
.chart-legend {
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 10px 0 0 0;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  position: relative;
  top: 20px;
}

.legend-item {
  display: flex;
  align-items: center;
  margin: 0 15px;
  font-size: 14px;
}

.legend-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 6px;
  border: 1px solid #ccc;
}

.legend-dot.normal {
  background-color: #1890ff;
}

.legend-dot.abnormal {
  background-color: #ff4d4f;
}
</style>

<style scoped>
.container {
  background: url("../assets/bg5.jpg") no-repeat center;
  background-size: 100% 100%;
  min-height: 100vh;
  padding: 20px;
}

.content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

h1 {
  color: #303133;
  font-size: 24px;
  margin-bottom: 20px;
}

.chart-container {
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 15px;
  margin-bottom: 20px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.chart-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.chart-action {
  display: flex;
  gap: 10px;
}

.chart {
  width: 100%;
  height: 400px;
}

.statistics {
  background: #f0f2f5;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 20px;
}

.statistics-item {
  display: inline-block;
  margin-right: 20px;
  margin-bottom: 10px;
}

.statistics-label {
  font-size: 14px;
  color: #666;
  margin-right: 5px;
}

.statistics-value {
  font-size: 18px;
  font-weight: 500;
  color: #1890ff;
}

.abnormal-table {
  background: #fff;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.abnormal-header {
  background: #f0f2f5;
  padding: 15px;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  border-bottom: 1px solid #e8e8e8;
}

.abnormal-content {
  padding: 15px;
}

.empty-message {
  text-align: center;
  color: #999;
  padding: 20px;
}

.update-time {
  text-align: right;
  font-size: 12px;
  color: #999;
  margin-top: 10px;
}

.button {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.button:hover {
  background-color: #40a9ff;
}

.button:active {
  background-color: #096dd9;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #1890ff;
}

input:checked + .slider:before {
  transform: translateX(20px);
}

.refresh-control {
  display: flex;
  align-items: center;
  gap: 10px;
}

.refresh-label {
  font-size: 14px;
  color: #666;
}
</style>
