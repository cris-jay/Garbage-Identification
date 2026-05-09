<template>
  <div class="home">
    <!-- 顶部欢迎卡片 -->
    <div class="welcome-card">
      <div class="greeting">绿动达人</div>
    </div>

    <!-- AI视觉识别入口 -->
    <div class="ai-card" @click="goToRecognize">
      <div class="ai-icon">📷</div>
      <div class="ai-text">
        <h3>AI视觉识别</h3>
        <p>拍照或上传图片，精准识别垃圾分类</p>
      </div>
      <button class="ai-btn">拍照识别</button>
    </div>

    <!-- 功能菜单网格 -->
    <div class="menu-grid">
      <div class="menu-item" @click="goTo('/search')">
        <span>🔍</span>
        <p>垃圾搜索</p>
      </div>
      <div class="menu-item" @click="goTo('/knowledge')">
        <span>📚</span>
        <p>分类知识</p>
      </div>
      <div class="menu-item" @click="goTo('/articles')">
        <span>📰</span>
        <p>科普文章</p>
      </div>
      <!-- 动态显示管理后台（仅管理员） -->
      <div v-if="isAdmin" class="menu-item" @click="goTo('/admin')">
        <span>⚙️</span>
        <p>管理后台</p>
      </div>
    </div>

    <!-- 识别历史 -->
    <div class="history-section">
      <div class="section-header">
        <span>识别历史</span>
        <span class="more" @click="gotoHistory">查看全部 ></span>
      </div>
      <div class="history-list">
        <div v-if="history.length === 0 && !loading" class="empty">暂无记录</div>
        <div v-for="item in history" :key="item.id" class="history-item">
          <img :src="placeholderImg" class="history-img" />
          <div>
            <div>{{ item.garbage_name }}</div>
            <div class="history-time">{{ item.create_time }}</div>
          </div>
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
const history = ref([])
const loading = ref(true)
const placeholderImg = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDAgMCAwIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMmY1Ii8+PC9zdmc+'

const isAdmin = computed(() => {
  return localStorage.getItem('role') === 'admin'
})

const gotoHistory = () => {
  router.push('/history')
}
const goTo = (path) => router.push(path)
const goToRecognize = () => router.push('/recognize')

onMounted(async () => {
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/history', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      // 只取最新的3条记录
      history.value = (res.data.data || []).slice(0, 3)
    }
  } catch (err) {
    console.error('获取历史失败', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.home {
  padding: 16px;
  background: #f5f7fa;
  padding-bottom: 70px;
}
.welcome-card {
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  border-radius: 24px;
  padding: 20px;
  color: white;
  margin-bottom: 20px;
}
.greeting {
  font-size: 20px;
  font-weight: bold;
}
.ai-card {
  background: white;
  border-radius: 24px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-bottom: 16px;
  cursor: pointer;
}
.ai-icon {
  font-size: 48px;
}
.ai-text {
  flex: 1;
}
.ai-text h3 {
  margin: 0;
  font-size: 18px;
}
.ai-text p {
  margin: 4px 0 0;
  color: #666;
  font-size: 12px;
}
.ai-btn {
  background: #2ecc71;
  border: none;
  color: white;
  padding: 8px 16px;
  border-radius: 40px;
  font-size: 14px;
  cursor: pointer;
}
.menu-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}
.menu-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.menu-item span {
  font-size: 32px;
}
.menu-item p {
  margin-top: 8px;
  font-size: 14px;
  font-weight: 500;
}
.menu-item:active {
  background: #e8f5e9;
}
.history-section .section-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-weight: bold;
}
.more {
  color: #2ecc71;
  cursor: pointer;
}
.history-list {
  display: flex;
  gap: 12px;
  overflow-x: auto;
}
.history-item {
  background: white;
  border-radius: 16px;
  padding: 12px;
  min-width: 100px;
  text-align: center;
}
.history-img {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  object-fit: cover;
  margin-bottom: 8px;
}
.history-time {
  font-size: 10px;
  color: #999;
}
.empty {
  background: white;
  border-radius: 16px;
  padding: 12px;
  min-width: 100px;
  text-align: center;
  color: #999;
}
</style>
