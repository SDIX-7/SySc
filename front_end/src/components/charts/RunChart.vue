<template>
  <div class="run-chart">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onUnmounted } from 'vue'
import * as echarts from 'echarts'

interface Props {
  data: number[]
  mean?: number
  ucl?: number
  lcl?: number
  title?: string
}

const props = withDefaults(defineProps<Props>(), {
  data: () => [],
  title: 'Run Chart'
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const data = props.data
  const mean = props.mean || (data.reduce((sum, val) => sum + val, 0) / data.length)

  // Calculate control limits if not provided
  let ucl = props.ucl
  let lcl = props.lcl

  if (!ucl || !lcl) {
    const movingRange = data.slice(1).map((val, idx) => Math.abs(val - data[idx]))
    const mrBar = movingRange.reduce((sum, val) => sum + val, 0) / movingRange.length
    const d2 = 1.128 // for n=2

    if (!ucl) ucl = mean + 3 * (mrBar / d2)
    if (!lcl) lcl = mean - 3 * (mrBar / d2)
  }

  // Prepare data points
  const seriesData: [number, number][] = data.map((val, idx) => [idx + 1, val])

  // Identify out-of-control points
  const outOfControlIndices: number[] = []
  data.forEach((val, idx) => {
    if (val > ucl || val < lcl) {
      outOfControlIndices.push(idx + 1)
    }
  })

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
      formatter: (params: any) => {
        const param = params[0]
        const value = param.value[1]
        const index = param.value[0]
        let result = `Sample ${index}<br/>`
        result += `Value: ${value.toFixed(4)}<br/>`

        if (value > ucl) {
          result += '<span style="color: #f44336;">⚠ Above UCL</span>'
        } else if (value < lcl) {
          result += '<span style="color: #f44336;">⚠ Below LCL</span>'
        } else {
          result += '<span style="color: #4caf50;">✓ Within limits</span>'
        }

        return result
      }
    },
    grid: {
      left: '10%',
      right: '10%',
      top: '60px',
      bottom: '30px'
    },
    xAxis: {
      type: 'value',
      name: 'Sample Number',
      nameLocation: 'center',
      nameGap: 30,
      min: 1,
      max: data.length
    },
    yAxis: {
      type: 'value',
      name: 'Value',
      nameLocation: 'center',
      nameGap: 40
    },
    series: [
      {
        name: 'Data',
        type: 'line',
        data: seriesData,
        smooth: false,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#2196f3',
          width: 2
        },
        itemStyle: {
          color: (params: any) => {
            const value = params.value[1]
            if (value > ucl || value < lcl) {
              return '#f44336'
            }
            return '#2196f3'
          }
        },
        markLine: {
          silent: true,
          data: [
            {
              yAxis: mean,
              name: 'CL',
              lineStyle: {
                color: '#4caf50',
                width: 2,
                type: 'solid'
              },
              label: {
                formatter: 'CL',
                position: 'end'
              }
            },
            {
              yAxis: ucl,
              name: 'UCL',
              lineStyle: {
                color: '#f44336',
                width: 2,
                type: 'dashed'
              },
              label: {
                formatter: 'UCL',
                position: 'end'
              }
            },
            {
              yAxis: lcl,
              name: 'LCL',
              lineStyle: {
                color: '#f44336',
                width: 2,
                type: 'dashed'
              },
              label: {
                formatter: 'LCL',
                position: 'end'
              }
            }
          ]
        }
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
.run-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 300px;
}
</style>
