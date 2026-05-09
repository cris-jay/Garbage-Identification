<template>
  <div class="profile">
    <div class="user-info">
      <img src="https://picsum.photos/80/80?random=100" class="avatar">
      <div class="info">
        <div class="name">绿动达人</div>
        <div class="points">已识别：{{ identifiedCount }}件</div>
      </div>
    </div>
    <div class="stats-grid">
      <div class="stat-card" @click="gotoHistory">
        <div class="num">{{ identifiedCount }}</div>
        <div>识别总数</div>
      </div>
    </div>
    <div class="menu-list">
      <div class="menu-item" @click="showReportDialog = true">
        <span>📄</span>
        <span>生成月度报告</span>
      </div>
      <div class="menu-item" @click="logout">
        <span>🚪</span>
        <span>退出登录</span>
      </div>
    </div>

    <!-- 月度报告生成对话框 -->
    <div v-if="showReportDialog" class="dialog-overlay" @click="showReportDialog = false">
      <div class="dialog-content" @click.stop>
        <h3>生成月度报告</h3>
        <div class="form-item">
          <label>选择月份</label>
          <input type="month" v-model="reportMonth" :max="currentMonth">
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="showReportDialog = false">取消</button>
          <button class="submit-btn" @click="generateReport" :disabled="generating">
            {{ generating ? '生成中...' : '生成报告' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const points = ref(0)
const identifiedCount = ref(0)
const showReportDialog = ref(false)
const reportMonth = ref('')
const generating = ref(false)

const currentMonth = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
})

const gotoHistory = () => {
  router.push('/history')
}

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  router.push('/login')
}

const generateReport = async () => {
  if (!reportMonth.value) {
    alert('请选择月份')
    return
  }
  generating.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('/api/report/generate', { month: reportMonth.value }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      const reportData = res.data.data
      alert(`报告生成成功！\n识别总次数：${reportData.total_count}\n平均置信度：${reportData.avg_confidence}\n正在打开PDF报告...`)
      window.open(reportData.download_url, '_blank')
      showReportDialog.value = false
    } else {
      alert(res.data.msg || '生成失败')
    }
  } catch (err) {
    console.error(err)
    alert('生成报告失败，请检查后端服务')
  } finally {
    generating.value = false
  }
}

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/history', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      identifiedCount.value = res.data.data ? res.data.data.length : 0
    }
  } catch (err) {
    console.error(err)
  }
})
</script>

<style scoped>
.profile {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.user-info {
  background: white;
  border-radius: 24px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}
.avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
}
.name {
  font-size: 18px;
  font-weight: bold;
}
.level {
  background: #2ecc71;
  display: inline-block;
  padding: 2px 12px;
  border-radius: 20px;
  font-size: 12px;
  color: white;
  margin: 6px 0;
}
.points {
  font-size: 12px;
  color: #666;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 12px;
  margin-bottom: 24px;
}
.stat-card {
  background: white;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
}
.stat-card .num {
  font-size: 24px;
  font-weight: bold;
  color: #2ecc71;
}
.menu-list {
  background: white;
  border-radius: 16px;
}
.menu-item {
  padding: 16px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  font-weight: 500;
}
.menu-item:last-child {
  border-bottom: none;
}
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog-content {
  background: white;
  border-radius: 24px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
}
.dialog-content h3 {
  margin: 0 0 20px;
  font-size: 20px;
}
.form-item {
  margin-bottom: 20px;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}
.form-item input {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 16px;
  box-sizing: border-box;
}
.dialog-actions {
  display: flex;
  gap: 12px;
}
.submit-btn, .cancel-btn {
  flex: 1;
  padding: 12px;
  border: none;
  border-radius: 40px;
  font-size: 16px;
  cursor: pointer;
}
.submit-btn {
  background: #2ecc71;
  color: white;
}
.submit-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
.cancel-btn {
  background: #f0f2f5;
  color: #333;
}
</style>