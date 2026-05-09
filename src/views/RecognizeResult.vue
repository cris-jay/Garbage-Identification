<template>
  <div class="result-page">
    <div class="result-card">
      <div class="image-area">
        <img :src="imageUrl" alt="识别图片" />
      </div>
      <div class="recog-info">
        <div class="category-badge" :class="categoryClass">
          {{ result.category }}
        </div>
        <div class="confidence">匹配度 {{ result.confidence }}%</div>
        <div class="name">{{ result.name }}</div>
        <div class="description">{{ result.desc }}</div>
      </div>
      <div class="actions">
        <button class="feedback-btn" @click="goFeedback">结果有误？纠错上报</button>
        <button class="retake-btn" @click="retake">再扫一扫</button>
      </div>
    </div>
    <div class="history-quick" @click="goHistory">
      <span>识别历史</span>
      <span>查看全部 &gt;</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const imageUrl = ref('')
const result = ref({
  name: '',
  category: '',
  category_id: 4,
  confidence: 0,
  desc: ''
})

const categoryClass = computed(() => {
  const map = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other'
  }
  return map[result.value.category] || ''
})

onMounted(() => {
  imageUrl.value = route.query.img || ''
  result.value = {
    name: route.query.name || '未知',
    category: route.query.category || '其他垃圾',
    category_id: route.query.category_id || 4,
    confidence: route.query.confidence || 0,
    desc: route.query.desc || ''
  }
})

const goFeedback = () => {
  // 后端识别接口不返回record_id，反馈时传null
  router.push({
    path: '/feedback',
    query: {
      name: result.value.name,
      category: result.value.category,
      img: imageUrl.value
    }
  })
}

const retake = () => {
  router.push('/recognize')
}

const goHistory = () => {
  router.push('/history')
}
</script>

<style scoped>
.result-page {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.result-card {
  background: white;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 20px;
}
.image-area {
  width: 100%;
  background: #f0f2f5;
  display: flex;
  justify-content: center;
  align-items: center;
}
.image-area img {
  width: 100%;
  max-height: 300px;
  object-fit: cover;
}
.recog-info {
  padding: 20px;
}
.category-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: bold;
  color: white;
  margin-bottom: 12px;
}
.recyclable { background: #3498db; }
.harmful { background: #e74c3c; }
.kitchen { background: #f39c12; }
.other { background: #95a5a6; }
.confidence {
  font-size: 14px;
  color: #2ecc71;
  font-weight: bold;
  margin-bottom: 8px;
}
.name {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 12px;
}
.description {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin-bottom: 16px;
}
.actions {
  padding: 0 20px 20px;
  display: flex;
  gap: 12px;
}
.feedback-btn, .retake-btn {
  flex: 1;
  padding: 12px;
  border-radius: 40px;
  font-size: 14px;
  border: none;
  cursor: pointer;
}
.feedback-btn {
  background: #fff3e0;
  color: #e67e22;
}
.retake-btn {
  background: #2ecc71;
  color: white;
}
.history-quick {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  cursor: pointer;
  font-weight: 500;
}
</style>
