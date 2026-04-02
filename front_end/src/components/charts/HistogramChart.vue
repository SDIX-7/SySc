<template>
  <div class="histogram-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data: number[]
  mean?: number
  std?: number
  usl?: number
  lsl?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  title: 'Histogram'
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const data = props.data.sort((a, b) => a - b)
  const mean = props.mean || (data.reduce((sum, val) => sum + val, 0) / data.length)
  const std = props.std || Math.sqrt(data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length)

  // Calculate histogram bins
  const minVal = Math.min(...data)
  const maxVal = Math.max(...data)
  const binCount = Math.min(30, Math.ceil(Math.sqrt(data.length)))
  const binWidth = (maxVal - minVal) / binCount

  const bins: number[] = []
  const counts: number[] = []

  for (let i = 0; i < binCount; i++) {
    bins.push(minVal + (i + 0.5) * binWidth)
    counts.push(0)
  }

  data.forEach(val => {
    const binIndex = Math.min(Math.floor((val - minVal) / binWidth), binCount - 1)
    counts[binIndex]++
  })

  // Normalize counts to density
  const densityCounts = counts.map(c => c / (data.length * binWidth))

  // Generate normal distribution curve
  const curvePoints: [number, number][] = []
  for (let i = 0; i <= 100; i++) {
    const x = minVal + (maxVal - minVal) * i / 100
    const y = (1 / (std * Math.sqrt(2 * Math.PI))) * Math.exp(-0.5 * Math.pow((x - mean) / std, 2))
    curvePoints.push([x, y])
  }

  const option: echarts.EChartsOption = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 14,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '60px',
      bottom: '30px'
    },
    xAxis: {
      type: 'category',
      data: bins.map(b => b.toFixed(2)),
      name: 'Value',
      nameLocation: 'center',
      nameGap: 30
    },
    yAxis: {
      type: 'value',
      name: 'Density',
      nameLocation: 'center',
      nameGap: 40
    },
    series: [
      {
        name: 'Histogram',
        type: 'bar',
        data: densityCounts,
        barWidth: '80%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#5470c6' },
            { offset: 1, color: '#91cc75' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#5470c6' },
              { offset: 1, color: '#5470c6' }
            ])
          }
        }
      },
      {
        name: 'Normal Curve',
        type: 'line',
        data: curvePoints,
        smooth: true,
        symbol: 'none',
        lineStyle: {
          color: '#ee6666',
          width: 2
        }
      }
    ],
    // Add vertical lines for specs
    markLine: {
      data: [
        ...(props.usl ? [{
          xAxis: props.usl,
          name: 'USL',
          lineStyle: { color: '#f44336', type: 'dashed' },
          label: { formatter: 'USL', position: 'end' }
        }] : []),
        ...(props.lsl ? [{
          xAxis: props.lsl,
          name: 'LSL',
          lineStyle: { color: '#f44336', type: 'dashed' },
          label: { formatter: 'LSL', position: 'end' }
        }] : []),
        {
          xAxis: mean,
          name: 'Mean',
          lineStyle: { color: '#4caf50', type: 'solid' },
          label: { formatter: 'Mean', position: 'end' }
        }
      ]
    }
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

watch(() => props.data, () => {
  initChart()
}, { deep: true })

const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}
</script>

<style scoped>
.histogram-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
