<template>
  <div class="article-detail">
    <div v-if="loading">加载中...</div>
    <div v-else class="card">
      <h1>{{ article.title }}</h1>
      <div class="meta">
        <span>作者：{{ article.author }}</span>
        <span>阅读量：{{ article.view || article.view_count }}</span>
        <span>{{ article.create_time }}</span>
      </div>
      <div class="content" v-html="article.content"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const article = ref({})
const loading = ref(true)

onMounted(async () => {
  const id = route.params.id
  try {
    const res = await axios.get(`/api/article/detail/${id}`)
    if (res.data.code === 200) {
      article.value = res.data.data || {}
    } else {
      article.value = { title: '文章不存在', content: '<p>未找到该文章</p>' }
    }
  } catch (err) {
    console.error(err)
    article.value = { title: '加载失败', content: '<p>请检查后端服务</p>' }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.article-detail {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.card {
  background: white;
  border-radius: 24px;
  padding: 20px;
}
h1 {
  font-size: 24px;
  margin-bottom: 12px;
}
.meta {
  font-size: 13px;
  color: #999;
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
  padding-bottom: 12px;
}
.content {
  line-height: 1.6;
  color: #333;
}
.content p {
  margin-bottom: 12px;
}
</style>