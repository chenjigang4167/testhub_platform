<template>
  <div class="test-report">
    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="left-filters">
        <el-select v-model="filters.project" :placeholder="$t('report.selectProject')" clearable @change="handleFilterChange" style="width: 200px">
          <el-option v-for="item in projects" :key="item.id" :label="item.name" :value="item.id"></el-option>
        </el-select>
        <el-select v-model="filters.days" :placeholder="$t('report.timeRange')" @change="handleFilterChange" style="width: 150px">
          <el-option :label="$t('report.recentDays')" :value="7"></el-option>
          <el-option :label="$t('report.recent14Days')" :value="14"></el-option>
          <el-option :label="$t('report.recent30Days')" :value="30"></el-option>
        </el-select>
      </div>
      <div class="right-actions">
        <el-button type="primary" @click="exportReport">
          <el-icon><Download /></el-icon>
          {{ $t('report.exportReport') }}
        </el-button>
      </div>
    </div>

    <!-- Dashboard cards -->
    <div class="dashboard-cards">
      <div class="card total-plans">
        <div class="card-icon">
          <el-icon><Collection /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dashboardData.active_plans || 0 }}</div>
          <div class="card-label">{{ $t('report.activePlans') }}</div>
        </div>
        <div class="card-extra">
          <el-progress type="circle" :percentage="dashboardData.plan_progress || 0" :width="40" :stroke-width="4" :show-text="false" />
          <span class="progress-text">{{ dashboardData.plan_progress || 0 }}% {{ $t('report.progress') }}</span>
        </div>
      </div>
      <div class="card total-cases">
        <div class="card-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dashboardData.total_cases || 0 }}</div>
          <div class="card-label">{{ $t('report.totalCases') }}</div>
        </div>
      </div>
      <div class="card pass-rate">
        <div class="card-icon">
          <el-icon><CircleCheck /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dashboardData.pass_rate || 0 }}%</div>
          <div class="card-label">{{ $t('report.passRate') }}</div>
        </div>
      </div>
      <div class="card defects">
        <div class="card-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-value">{{ dashboardData.total_defects || 0 }}</div>
          <div class="card-label">{{ $t('report.defectsFound') }}</div>
        </div>
      </div>
    </div>

    <!-- Charts area -->
    <div class="charts-container">
      <!-- First row: Execution status and trends -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-header">
            <h3>{{ $t('report.executionStatusDistribution') }}</h3>
          </div>
          <div class="chart-body" ref="statusChartRef"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <h3>{{ $t('report.dailyExecutionTrend') }}</h3>
          </div>
          <div class="chart-body" ref="trendChartRef"></div>
        </div>
      </div>

      <!-- Second row: Defect analysis -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-header">
            <h3>{{ $t('report.failureDistribution') }}</h3>
          </div>
          <div class="chart-body" ref="defectChartRef"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <h3>{{ $t('report.failureTop10') }}</h3>
          </div>
          <div class="chart-body table-body">
            <el-table :data="failedCasesTop" style="width: 100%" size="small">
              <el-table-column prop="testcase__title" :label="$t('report.caseTitle')" show-overflow-tooltip />
              <el-table-column prop="fail_count" :label="$t('report.failureCount')" width="100" align="center">
                <template #default="scope">
                  <el-tag type="danger">{{ scope.row.fail_count }}</el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>

      <!-- Third row: AI efficiency -->
      <div class="chart-row">
        <div class="chart-card">
          <div class="chart-header">
            <h3>{{ $t('report.aiEffectivenessAnalysis') }}</h3>
          </div>
          <div class="ai-metrics-container">
            <div class="ai-metric-item">
              <div class="metric-value">{{ aiData.adoption_rate || 0 }}%</div>
              <div class="metric-label">{{ $t('report.adoptionRate') }}</div>
              <el-progress :percentage="aiData.adoption_rate || 0" :show-text="false" status="success" />
            </div>
            <div class="ai-metric-item">
              <div class="metric-value">{{ aiData.requirement_coverage || 0 }}%</div>
              <div class="metric-label">{{ $t('report.requirementCoverage') }}</div>
              <el-progress :percentage="aiData.requirement_coverage || 0" :show-text="false" />
            </div>
            <div class="ai-metric-item">
              <div class="metric-value">{{ aiData.saved_hours || 0 }}h</div>
              <div class="metric-label">{{ $t('report.savedHours') }}</div>
            </div>
          </div>
          <div class="chart-body-small" ref="aiEfficiencyChartRef"></div>
        </div>
        <div class="chart-card">
          <div class="chart-header">
            <h3>{{ $t('report.teamWorkload') }}</h3>
          </div>
          <div class="chart-body" ref="workloadChartRef"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import { Collection, Document, CircleCheck, Warning, Download } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import api from '@/utils/api'

const { t } = useI18n()

// 状态
const projects = ref([])
const filters = reactive({
  project: null,
  days: 7
})
const dashboardData = ref({})
const failedCasesTop = ref([])
const aiData = ref({})

// 图表实例
let statusChart = null
let trendChart = null
let defectChart = null
let aiEfficiencyChart = null
let workloadChart = null

// DOM引用
const statusChartRef = ref(null)
const trendChartRef = ref(null)
const defectChartRef = ref(null)
const aiEfficiencyChartRef = ref(null)
const workloadChartRef = ref(null)

// Fetch projects
const fetchProjects = async () => {
  try {
    const response = await api.get('/projects/')
    projects.value = response.data.results || []
  } catch (error) {
    console.error(t('report.fetchProjectsFailed'), error)
  }
}

// Fetch dashboard data
const fetchDashboardData = async () => {
  try {
    const params = { project: filters.project }
    const response = await api.get('/reports/reports/dashboard/', { params })
    dashboardData.value = response.data
  } catch (error) {
    console.error(t('report.fetchDashboardFailed'), error)
  }
}

// 初始化图表
const initCharts = () => {
  if (statusChartRef.value) statusChart = echarts.init(statusChartRef.value)
  if (trendChartRef.value) trendChart = echarts.init(trendChartRef.value)
  if (defectChartRef.value) defectChart = echarts.init(defectChartRef.value)
  if (aiEfficiencyChartRef.value) aiEfficiencyChart = echarts.init(aiEfficiencyChartRef.value)
  if (workloadChartRef.value) workloadChart = echarts.init(workloadChartRef.value)
  
  window.addEventListener('resize', handleResize)
}

const handleResize = () => {
  statusChart?.resize()
  trendChart?.resize()
  defectChart?.resize()
  aiEfficiencyChart?.resize()
  workloadChart?.resize()
}

// 加载图表数据
const loadChartsData = async () => {
  const params = { 
    project: filters.project,
    days: filters.days
  }

  // 1. Status distribution
  try {
    const res = await api.get('/reports/reports/status_distribution/', { params })
    const data = [
      { value: res.data.passed, name: t('report.passed'), itemStyle: { color: '#67C23A' } },
      { value: res.data.failed, name: t('report.failed'), itemStyle: { color: '#F56C6C' } },
      { value: res.data.blocked, name: t('report.blocked'), itemStyle: { color: '#E6A23C' } },
      { value: res.data.retest, name: t('report.retest'), itemStyle: { color: '#409EFF' } },
      { value: res.data.untested, name: t('report.untested'), itemStyle: { color: '#909399' } }
    ]

    statusChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%', left: 'center' },
      series: [{
        name: t('report.executionStatus'),
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: false,
        itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
        label: { show: false, position: 'center' },
        emphasis: { label: { show: true, fontSize: 20, fontWeight: 'bold' } },
        labelLine: { show: false },
        data: data
      }]
    })
  } catch (e) { console.error(e) }

  // 2. Execution trend
  try {
    const res = await api.get('/reports/reports/execution_trend/', { params })
    const dates = res.data.map(item => item.date)
    const counts = res.data.map(item => item.count)

    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'category', boundaryGap: false, data: dates },
      yAxis: { type: 'value' },
      series: [{
        name: t('report.executionCount'),
        type: 'line',
        stack: 'Total',
        smooth: true,
        areaStyle: { opacity: 0.3, color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [{ offset: 0, color: '#409EFF' }, { offset: 1, color: '#fff' }]) },
        itemStyle: { color: '#409EFF' },
        data: counts
      }]
    })
  } catch (e) { console.error(e) }

  // 3. Defect distribution
  try {
    const res = await api.get('/reports/reports/defect_distribution/', { params })
    defectChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%', left: 'center' },
      series: [{
        name: t('report.priorityDistribution'),
        type: 'pie',
        radius: '60%',
        center: ['50%', '45%'],
        data: res.data,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }]
    })
  } catch (e) { console.error(e) }

  // 4. 失败用例TOP榜
  try {
    const res = await api.get('/reports/reports/failed_cases_top/', { params })
    failedCasesTop.value = res.data
  } catch (e) { console.error(e) }

  // 5. AI efficiency
  try {
    const res = await api.get('/reports/reports/ai_efficiency/', { params })
    aiData.value = res.data
    const aiCounts = res.data.ai_vs_manual

    aiEfficiencyChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      grid: { left: '3%', right: '4%', bottom: '3%', top: '10%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: [t('report.caseSource')] },
      series: [
        { name: t('report.aiGenerated'), type: 'bar', stack: 'total', label: { show: true }, itemStyle: { color: '#8e44ad' }, data: [aiCounts.ai] },
        { name: t('report.manualCreated'), type: 'bar', stack: 'total', label: { show: true }, itemStyle: { color: '#3498db' }, data: [aiCounts.manual] }
      ]
    })
  } catch (e) { console.error(e) }

  // 6. Team workload
  try {
    const res = await api.get('/reports/reports/team_workload/', { params })
    const users = res.data.map(item => item.username)
    const execCounts = res.data.map(item => item.execution_count)
    const defectCounts = res.data.map(item => item.defect_count)

    workloadChart.setOption({
      tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
      legend: { data: [t('report.executedCases'), t('report.defectsFound')], bottom: '0%' },
      grid: { left: '3%', right: '4%', bottom: '10%', top: '5%', containLabel: true },
      xAxis: { type: 'value' },
      yAxis: { type: 'category', data: users },
      series: [
        {
          name: t('report.executedCases'),
          type: 'bar',
          stack: 'total',
          label: { show: true },
          itemStyle: { color: '#409EFF' },
          data: execCounts
        },
        {
          name: t('report.defectsFound'),
          type: 'bar',
          stack: 'total',
          label: { show: true },
          itemStyle: { color: '#F56C6C' },
          data: defectCounts
        }
      ]
    })
  } catch (e) { console.error(e) }
}

const handleFilterChange = () => {
  fetchDashboardData()
  loadChartsData()
}

const exportReport = () => {
  ElMessage.success(t('report.exportInDevelopment'))
}

onMounted(async () => {
  await fetchProjects()
  await nextTick()
  initCharts()
  handleFilterChange()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  statusChart?.dispose()
  trendChart?.dispose()
  defectChart?.dispose()
  aiEfficiencyChart?.dispose()
  workloadChart?.dispose()
})
</script>

<style scoped>
.test-report {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.left-filters {
  display: flex;
  gap: 16px;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.3s;
  position: relative;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px 0 rgba(0, 0, 0, 0.1);
}

.card-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 16px;
  font-size: 24px;
}

.total-plans .card-icon { background: #e8f3ff; color: #409EFF; }
.total-cases .card-icon { background: #f0f9eb; color: #67C23A; }
.pass-rate .card-icon { background: #fdf6ec; color: #E6A23C; }
.defects .card-icon { background: #fef0f0; color: #F56C6C; }

.card-content {
  flex: 1;
}

.card-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
  line-height: 1.2;
}

.card-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-extra {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-size: 12px;
  color: #909399;
}

.charts-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.chart-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.chart-header {
  margin-bottom: 20px;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
  font-weight: 600;
}

.chart-body {
  height: 300px;
  width: 100%;
}

.chart-body-small {
  height: 150px;
  width: 100%;
}

.table-body {
  overflow-y: auto;
}

.ai-metrics-container {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
}

.ai-metric-item {
  text-align: center;
  width: 30%;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 12px;
  color: #909399;
  margin-bottom: 5px;
}
</style>
