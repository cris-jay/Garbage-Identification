<template>
  <div class="article-list">
    <h2>环保科普文章</h2>
    <div v-if="articles.length === 0 && !loading" class="empty">暂无文章</div>
    <div v-for="article in articles" :key="article.id" class="article-item" @click="gotoDetail(article.id)">
      <div class="article-header">
        <h3>{{ article.title }}</h3>
        <small>阅读量：{{ article.view || 0 }}</small>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const articles = ref([])
const loading = ref(true)

onMounted(async () => {
  try {
    const res = await axios.get('/api/article/list')
    if (res.data.code === 200) {
      articles.value = res.data.data || []
    }
  } catch (err) {
    console.error('获取文章列表失败', err)
  } finally {
    loading.value = false
  }
})

const gotoDetail = (id) => {
  router.push(`/article/${id}`)
}
</script>

<style scoped>
.article-list {
  padding: 20px;
}
.article-item {
  background: white;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.article-header h3 {
  margin: 0 0 8px;
}
.article-header small {
  color: #999;
}
.empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
</style>
