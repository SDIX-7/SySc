<template>
  <div class="capability-gauge">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Props {
  value: number
  name?: string
  requirement?: number
  min?: number
  max?: number
}

const props = withDefaults(defineProps<Props>(), {
  value: 0,
  name: 'Cpk',
  requirement: 1.33,
  min: 0,
  max: 2
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const getColor = (value: number): string => {
  if (value >= 1.67) return '#4caf50' // Excellent - Green
  if (value >= 1.33) return '#8bc34a' // Good - Light Green
  if (value >= 1.0) return '#ff9800' // Fair - Orange
  return '#f44336' // Poor - Red
}

const getRating = (value: number): string => {
  if (value >= 1.67) return 'Excellent'
  if (value >= 1.33) return 'Good'
  if (value >= 1.0) return 'Fair'
  return 'Poor'
}

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const option: echarts.EChartsOption = {
    series: [
      {
        type: 'gauge',
        name: props.name,
        min: props.min,
        max: props.max,
        splitNumber: 10,
        radius: '90%',
        axisLine: {
          lineStyle: {
            width: 20,
            color: [
              [0.5, '#f44336'], // 0 - 1.0: Red
              [0.67, '#ff9800'], // 1.0 - 1.33: Orange
              [0.83, '#8bc34a'], // 1.33 - 1.67: Light Green
              [1, '#4caf50'] // 1.67 - 2.0: Green
            ]
          }
        },
        pointer: {
          itemStyle: {
            color: '#333'
          },
          width: 5,
          length: '60%'
        },
        axisTick: {
          distance: -20,
          length: 8,
          lineStyle: {
            color: 'auto',
            width: 2
          }
        },
        splitLine: {
          distance: -25,
          length: 20,
          lineStyle: {
            color: 'auto',
            width: 3
          }
        },
        axisLabel: {
          color: '#333',
          distance: 30,
          fontSize: 12,
          formatter: (value: number) => {
            if (value === 1.0) return '1.0'
            if (value === 1.33) return '1.33'
            if (value === 1.67) return '1.67'
            return ''
          }
        },
        title: {
          show: true,
          offsetCenter: [0, '70%'],
          fontSize: 14,
          color: '#666'
        },
        detail: {
          valueAnimation: true,
          formatter: (value: number) => {
            return value.toFixed(3)
          },
          color: '#333',
          fontSize: 28,
          fontWeight: 'bold',
          offsetCenter: [0, '30%']
        },
        data: [
          {
            value: props.value,
            name: props.name
          }
        ]
      }
    ]
  }

  chartInstance.setOption(option)
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  if (chartInstance) {
    chartInstance.dispose()
  }
})

watch(() => props.value, () => {
  initChart()
})

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}
</script>

<style scoped>
.capability-gauge {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 200px;
}
</style>
