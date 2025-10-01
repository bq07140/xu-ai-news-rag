<template>
  <div class="analysis-page">
    <!-- Statistics Cards -->
    <el-row :gutter="16">
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Total Documents" :value="stats.total_documents">
            <template #prefix>
              <el-icon color="#409EFF"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Last 7 Days" :value="stats.recent_7days">
            <template #prefix>
              <el-icon color="#67C23A"><TrendCharts /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Index Size" :value="stats.index_size">
            <template #prefix>
              <el-icon color="#E6A23C"><DataLine /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic title="Categories" :value="Object.keys(stats.category_distribution || {}).length">
            <template #prefix>
              <el-icon color="#F56C6C"><Histogram /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts Area -->
    <el-row :gutter="16" style="margin-top: 16px">
      <!-- Category Distribution -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>Category Distribution</span>
              <el-button text :icon="Refresh" @click="fetchCategoryDistribution" />
            </div>
          </template>
          <v-chart :option="categoryOption" style="height: 300px" />
        </el-card>
      </el-col>

      <!-- Source Distribution -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>Source Distribution</span>
              <el-button text :icon="Refresh" @click="fetchSourceDistribution" />
            </div>
          </template>
          <v-chart :option="sourceOption" style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Keywords and Time Trend -->
    <el-row :gutter="16" style="margin-top: 16px">
      <!-- Top 10 Keywords -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>Top 10 Keywords</span>
              <el-space>
                <el-select
                  v-model="keywordTimeRange"
                  size="small"
                  style="width: 120px"
                  @change="fetchKeywords"
                >
                  <el-option label="Last 7 days" value="7days" />
                  <el-option label="Last 30 days" value="30days" />
                  <el-option label="All" value="all" />
                </el-select>
                <el-button text :icon="Refresh" @click="fetchKeywords" />
              </el-space>
            </div>
          </template>
          <v-chart :option="keywordOption" style="height: 400px" />
        </el-card>
      </el-col>

      <!-- Time Trend -->
      <el-col :span="12">
        <el-card shadow="never">
          <template #header>
            <div class="card-header">
              <span>Time Trend</span>
              <el-space>
                <el-select
                  v-model="trendDays"
                  size="small"
                  style="width: 120px"
                  @change="fetchTimeTrend"
                >
                  <el-option label="Last 7 days" :value="7" />
                  <el-option label="Last 30 days" :value="30" />
                </el-select>
                <el-button text :icon="Refresh" @click="fetchTimeTrend" />
              </el-space>
            </div>
          </template>
          <v-chart :option="trendOption" style="height: 400px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- Comprehensive Analysis Report -->
    <el-card shadow="never" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>Comprehensive Analysis Report</span>
          <el-space>
            <el-select
              v-model="reportTimeRange"
              size="small"
              style="width: 120px"
              @change="fetchReport"
            >
              <el-option label="Last 7 days" value="7days" />
              <el-option label="Last 30 days" value="30days" />
              <el-option label="All" value="all" />
            </el-select>
            <el-button text :icon="Refresh" @click="fetchReport" />
          </el-space>
        </div>
      </template>

      <el-skeleton v-if="reportLoading" :rows="5" animated />

      <div v-else-if="report" class="report-content">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="Total Documents">
            {{ report.total_documents }}
          </el-descriptions-item>
          <el-descriptions-item label="Time Range">
            {{ reportTimeRange }}
          </el-descriptions-item>
          <el-descriptions-item label="Generated At">
            {{ formatDate(report.generated_at) }}
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="report.top_keywords" style="margin-top: 24px">
          <h4>Top 10 Keywords</h4>
          <el-table :data="report.top_keywords" style="margin-top: 12px">
            <el-table-column type="index" label="Rank" width="80" />
            <el-table-column prop="keyword" label="Keyword" />
            <el-table-column prop="count" label="Count" width="120" />
            <el-table-column label="Weight" width="150">
              <template #default="{ row }">
                <el-progress
                  :percentage="Math.round(row.weight * 1000)"
                  :show-text="false"
                />
                {{ (row.weight * 100).toFixed(2) }}%
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <el-alert
        v-else
        title="Insufficient Data"
        description="At least 100 documents are required to generate analysis report"
        type="warning"
        :closable="false"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { analysisAPI } from '@/api'
import { Refresh, Document, TrendCharts, DataLine, Histogram } from '@element-plus/icons-vue'
import dayjs from 'dayjs'

use([
  CanvasRenderer,
  PieChart,
  BarChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const stats = ref({
  total_documents: 0,
  recent_7days: 0,
  index_size: 0,
  category_distribution: {},
  source_distribution: {}
})

const keywordTimeRange = ref('7days')
const trendDays = ref(7)
const reportTimeRange = ref('7days')
const reportLoading = ref(false)
const report = ref(null)

// 图表配置
const categoryOption = ref({})
const sourceOption = ref({})
const keywordOption = ref({})
const trendOption = ref({})

// 格式化日期
const formatDate = (date) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 获取统计信息
const fetchStatistics = async () => {
  try {
    const res = await analysisAPI.getStatistics()
    stats.value = res
  } catch (error) {
    console.error('Failed to fetch statistics:', error)
  }
}

// 获取分类分布
const fetchCategoryDistribution = async () => {
  try {
    const res = await analysisAPI.getCategoryDistribution()
    const data = Object.entries(res.distribution).map(([name, value]) => ({
      name,
      value
    }))

    categoryOption.value = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'right'
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  } catch (error) {
    console.error('Failed to fetch category distribution:', error)
  }
}

// 获取来源分布
const fetchSourceDistribution = async () => {
  try {
    const res = await analysisAPI.getSourceDistribution()
    const data = Object.entries(res.distribution).map(([name, value]) => ({
      name,
      value
    }))

    sourceOption.value = {
      tooltip: {
        trigger: 'item',
        formatter: '{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'vertical',
        left: 'right'
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data,
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    }
  } catch (error) {
    console.error('Failed to fetch source distribution:', error)
  }
}

// 获取关键词
const fetchKeywords = async () => {
  try {
    const res = await analysisAPI.extractKeywords({
      time_range: keywordTimeRange.value,
      topK: 10
    })

    const data = res.keywords.map((item) => ({
      name: item.keyword,
      value: item.count
    }))

    keywordOption.value = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'value'
      },
      yAxis: {
        type: 'category',
        data: data.map((item) => item.name)
      },
      series: [
        {
          type: 'bar',
          data: data.map((item) => item.value),
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    }
  } catch (error) {
    console.error('Failed to fetch keywords:', error)
  }
}

// 获取时间趋势
const fetchTimeTrend = async () => {
  try {
    const res = await analysisAPI.getTimeTrend({ days: trendDays.value })
    const dates = Object.keys(res.trend).sort()
    const values = dates.map((date) => res.trend[date])

    trendOption.value = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: dates,
        axisLabel: {
          rotate: 45
        }
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: values,
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#67C23A'
          },
          areaStyle: {
            color: 'rgba(103, 194, 58, 0.2)'
          }
        }
      ],
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        containLabel: true
      }
    }
  } catch (error) {
    console.error('Failed to fetch time trend:', error)
  }
}

// 获取综合报告
const fetchReport = async () => {
  reportLoading.value = true
  try {
    const res = await analysisAPI.getReport({
      time_range: reportTimeRange.value
    })
    report.value = res.report
  } catch (error) {
    console.error('Failed to fetch report:', error)
    report.value = null
  } finally {
    reportLoading.value = false
  }
}

onMounted(() => {
  fetchStatistics()
  fetchCategoryDistribution()
  fetchSourceDistribution()
  fetchKeywords()
  fetchTimeTrend()
  fetchReport()
})
</script>

<style scoped>
.analysis-page {
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-content {
  padding: 16px 0;
}

.report-content h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}
</style>


