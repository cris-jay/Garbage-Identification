<template>
  <div class="feedback-page">
    <div class="card">
      <h2>反馈纠错</h2>
      <p class="subtitle">您的反馈将帮助AI更好地学习，让环境更加美好。</p>
      <div class="image-section" v-if="imageUrl">
        <div class="label">识别错误的图片</div>
        <img :src="imageUrl" class="error-img" />
      </div>
      <div class="info-row">
        <div class="label">原识别结果</div>
        <div class="old-category">{{ originalCategory }}</div>
      </div>
      <div class="info-row">
        <div class="label">正确分类</div>
        <div class="category-select">
          <button
            v-for="cat in categories"
            :key="cat"
            :class="{ active: selectedCategory === cat }"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
      </div>
      <div class="info-row">
        <div class="label">纠错说明</div>
        <textarea v-model="description" rows="3" placeholder="例如：这是过期的纽扣电池，不应识别为可回收物..."></textarea>
      </div>
      <div class="actions">
        <button class="submit-btn" @click="submitFeedback">提交反馈</button>
        <button class="cancel-btn" @click="goBack">取消</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const route = useRoute()

const imageUrl = ref('')
const originalCategory = ref('')
const selectedCategory = ref('')
const description = ref('')
const recordId = ref(null)
const categories = ['可回收物', '有害垃圾', '厨余垃圾', '其他垃圾']

onMounted(() => {
  imageUrl.value = route.query.img || ''
  originalCategory.value = route.query.category || '可回收物'
  selectedCategory.value = originalCategory.value
  // 后端识别接口不返回record_id，从history页面跳转时可能有record_id
  recordId.value = route.query.record_id || null
})

const submitFeedback = async () => {
  if (!selectedCategory.value) {
    alert('请选择正确分类')
    return
  }
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('/api/feedback', {
      record_id: recordId.value,
      correct_category: selectedCategory.value,
      content: description.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      alert('反馈已提交，感谢您的贡献！')
      router.push('/home')
    } else {
      alert(res.data.msg || '提交失败')
    }
  } catch (err) {
    console.error(err)
    alert('提交失败，请检查后端服务')
  }
}

const goBack = () => {
  router.back()
}
</script>

<style scoped>
.feedback-page {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.card {
  background: white;
  border-radius: 24px;
  padding: 20px;
}
h2 {
  margin: 0 0 8px;
  font-size: 24px;
}
.subtitle {
  font-size: 13px;
  color: #666;
  margin-bottom: 20px;
  line-height: 1.4;
}
.image-section {
  margin-bottom: 20px;
}
.label {
  font-size: 14px;
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}
.error-img {
  width: 100%;
  max-height: 200px;
  object-fit: cover;
  border-radius: 16px;
  background: #f0f2f5;
}
.info-row {
  margin-bottom: 20px;
}
.old-category {
  background: #f0f2f5;
  padding: 10px;
  border-radius: 12px;
  font-weight: 500;
}
.category-select {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.category-select button {
  flex: 1;
  padding: 8px 0;
  border: 1px solid #ddd;
  background: white;
  border-radius: 40px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
}
.category-select button.active {
  background: #2ecc71;
  color: white;
  border-color: #2ecc71;
}
textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 16px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
}
.actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.submit-btn, .cancel-btn {
  flex: 1;
  padding: 12px;
  border-radius: 40px;
  font-size: 16px;
  border: none;
  cursor: pointer;
}
.submit-btn {
  background: #2ecc71;
  color: white;
}
.cancel-btn {
  background: #f0f2f5;
  color: #333;
}
</style>