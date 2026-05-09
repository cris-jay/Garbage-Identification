<template>
  <div class="history-page">
    <div class="header">
      <h2>识别历史</h2>
      <span class="count">共 {{ historyList.length }} 条记录</span>
    </div>

    <div class="history-list">
      <div v-for="item in historyList" :key="item.id" class="history-item" @click="goToFeedback(item)">
        <img :src="item.image_base64 ? 'data:image/jpeg;base64,' + item.image_base64 : placeholderImg" class="item-img" />
        <div class="item-info">
          <div class="item-name">{{ item.garbage_name }}</div>
          <div class="item-category" :class="categoryClass(item.category_name)">{{ item.category_name }}</div>
          <div class="item-time">{{ item.create_time }}</div>
        </div>
        <div class="item-confidence">{{ item.confidence * 100 }}%</div>
      </div>
    </div>

    <div v-if="historyList.length === 0 && !loading" class="empty">
      暂无识别记录，快去拍照识别吧~
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const historyList = ref([])
const loading = ref(true)
const placeholderImg = 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgdmlld0JveD0iMCAwIDAgMCAwIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMmY1Ii8+PC9zdmc+'

const categoryClass = (category) => {
  const map = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other'
  }
  return map[category] || ''
}

const goToFeedback = (item) => {
  router.push({
    path: '/feedback',
    query: {
      name: item.garbage_name,
      category: item.category_name,
      record_id: item.id,
      img: item.image_base64 ? 'data:image/jpeg;base64,' + item.image_base64 : placeholderImg
    }
  })
}

onMounted(async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/history', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      historyList.value = res.data.data || []
    }
  } catch (err) {
    console.error('获取历史记录失败', err)
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.history-page {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 16px;
}
.header h2 {
  font-size: 20px;
  margin: 0;
}
.count {
  font-size: 13px;
  color: #999;
}
.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.history-item {
  background: white;
  border-radius: 16px;
  padding: 12px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: 0.2s;
  cursor: pointer;
}
.history-item:active {
  background: #f0f2f5;
}
.item-img {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  object-fit: cover;
  background: #f0f2f5;
}
.item-info {
  flex: 1;
}
.item-name {
  font-weight: bold;
  font-size: 16px;
  margin-bottom: 4px;
}
.item-category {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  margin-bottom: 6px;
}
.recyclable { background: #3498db; }
.harmful { background: #e74c3c; }
.kitchen { background: #f39c12; }
.other { background: #95a5a6; }
.item-time {
  font-size: 11px;
  color: #999;
}
.item-confidence {
  font-size: 14px;
  color: #2ecc71;
  font-weight: bold;
}
.empty {
  text-align: center;
  padding: 60px 20px;
  color: #999;
}
</style>
