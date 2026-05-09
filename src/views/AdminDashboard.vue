<template>
  <div class="admin-dashboard">
    <!-- 顶部标题和更新时间 -->
    <div class="dashboard-header">
      <h2>绿动后台</h2>
      <div class="update-time">数据大屏 · 系统状态更新于：{{ currentTime }}</div>
    </div>

    <!-- 统计卡片行 -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-title">总用户数</div>
        <div class="stat-value">{{ stats.totalUsers }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">总识别次数</div>
        <div class="stat-value">{{ stats.totalRecognitions }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">本月识别量</div>
        <div class="stat-value">{{ stats.monthCount }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">待处理反馈</div>
        <div class="stat-value">{{ stats.pendingFeedbacks }}</div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="charts-row">
      <div class="chart-card">
        <div class="chart-title">近7天识别趋势</div>
        <div class="line-chart">
          <div v-for="(item, idx) in trendData" :key="idx" class="line-item">
            <div class="line-bar" :style="{ height: item.height + '%' }"></div>
            <div class="line-label">{{ item.label }}</div>
          </div>
        </div>
      </div>
      <div class="chart-card">
        <div class="chart-title">垃圾分类占比</div>
        <div class="pie-chart">
          <div class="legend">
            <div v-for="type in categoryStats" :key="type.name" class="legend-item">
              <span class="color-dot" :style="{ background: type.color }"></span>
              <span>{{ type.name }} {{ type.percent }}%</span>
            </div>
          </div>
          <div class="simple-pie">
            <div v-for="type in categoryStats" :key="type.name" class="pie-slice" :style="{ width: type.percent + '%', background: type.color }"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- TOP10垃圾识别 -->
    <div class="top-garbage-section">
      <div class="section-title">识别最多的垃圾 TOP10</div>
      <div class="top-list">
        <div v-for="(item, idx) in topGarbage" :key="idx" class="top-item">
          <span class="top-rank">{{ idx + 1 }}</span>
          <span class="top-name">{{ item.name }}</span>
          <span class="top-count">{{ item.count }}次</span>
        </div>
      </div>
    </div>

    <!-- 管理功能卡片 -->
    <div class="manage-section">
      <div class="section-title">内容管理</div>
      <div class="manage-grid">
        <div class="manage-card" @click="goToGarbageList">
          <div class="icon">🗑️</div>
          <div>垃圾条目管理</div>
        </div>
        <div class="manage-card" @click="goToArticleManage">
          <div class="icon">📝</div>
          <div>文章管理</div>
        </div>
        <div class="manage-card" @click="goToFeedbackAudit">
          <div class="icon">✅</div>
          <div>反馈审核</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const currentTime = ref('')
const stats = ref({
  totalUsers: 0,
  totalRecognitions: 0,
  monthCount: 0,
  pendingFeedbacks: 0
})

const trendData = ref([])
const categoryStats = ref([])
const topGarbage = ref([])

const categoryColors = {
  '可回收物': '#3498db',
  '有害垃圾': '#e74c3c',
  '湿垃圾': '#f39c12',
  '干垃圾': '#95a5a6',
  '厨余垃圾': '#f39c12',
  '其他垃圾': '#95a5a6'
}

onMounted(async () => {
  // 更新时间
  const now = new Date()
  currentTime.value = `${now.getFullYear()}年${now.getMonth()+1}月${now.getDate()}日 ${now.getHours().toString().padStart(2,'0')}:${now.getMinutes().toString().padStart(2,'0')}`
  
  // 从后端获取真实数据
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/admin/dashboard/screen', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      const data = res.data.data
      
      // 更新统计卡片
      stats.value = {
        totalUsers: data.cards.total_users || 0,
        totalRecognitions: data.cards.total_recognitions || 0,
        monthCount: data.cards.month_count || 0,
        pendingFeedbacks: data.cards.pending_feedbacks || 0
      }
      
      // 更新分类统计（饼图）
      const totalCategory = data.category_stats.reduce((sum, item) => sum + item.value, 0)
      categoryStats.value = data.category_stats.map(item => ({
        name: item.name,
        percent: totalCategory > 0 ? Math.round((item.value / totalCategory) * 100) : 0,
        color: categoryColors[item.name] || '#95a5a6'
      }))
      
      // 更新7天趋势
      const maxTrend = Math.max(...data.trend_7d.map(item => item.count), 1)
      trendData.value = data.trend_7d.map(item => ({
        label: item.date.slice(5), // 显示 MM-DD
        height: (item.count / maxTrend) * 100
      }))
      
      // 更新TOP10
      topGarbage.value = data.top_garbage.map(item => ({
        name: item.garbage_name,
        count: item.count
      }))
    }
  } catch (err) {
    console.error('获取仪表盘数据失败', err)
  }
})

const goToGarbageList = () => router.push('/admin/garbage')
const goToArticleManage = () => router.push('/admin/articles')
const goToFeedbackAudit = () => router.push('/admin/feedback/audit')
</script>

<style scoped>
.admin-dashboard {
  padding: 20px;
  background: #f5f7fb;
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
}
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 24px;
}
.dashboard-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}
.update-time {
  font-size: 12px;
  color: #999;
}
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.stat-title {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
}
.charts-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}
.chart-card {
  background: white;
  border-radius: 20px;
  padding: 20px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.chart-title {
  font-weight: 600;
  margin-bottom: 16px;
}
.line-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  height: 200px;
}
.line-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 40px;
}
.line-bar {
  width: 24px;
  background: #3498db;
  border-radius: 8px 8px 4px 4px;
  transition: 0.2s;
}
.line-label {
  font-size: 10px;
  margin-top: 8px;
  color: #666;
}
.pie-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.legend-item {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.color-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}
.simple-pie {
  display: flex;
  height: 20px;
  border-radius: 20px;
  overflow: hidden;
}
.pie-slice {
  height: 100%;
}
.top-garbage-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.section-title {
  font-weight: 600;
  font-size: 18px;
  margin-bottom: 16px;
}
.top-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.top-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  background: #f8f9fc;
  border-radius: 12px;
}
.top-rank {
  width: 28px;
  height: 28px;
  background: #2ecc71;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}
.top-item:nth-child(1) .top-rank { background: #f1c40f; }
.top-item:nth-child(2) .top-rank { background: #95a5a6; }
.top-item:nth-child(3) .top-rank { background: #cd7f32; }
.top-name {
  flex: 1;
  font-weight: 500;
}
.top-count {
  color: #666;
  font-size: 14px;
}
.manage-section {
  background: white;
  border-radius: 20px;
  padding: 20px;
  margin-bottom: 24px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
}
.manage-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.manage-card {
  background: #f8f9fc;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: 0.2s;
}
.manage-card:hover {
  background: #eef2f7;
}
.manage-card .icon {
  font-size: 32px;
  margin-bottom: 8px;
}
@media (max-width: 800px) {
  .stats-row, .charts-row, .manage-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
