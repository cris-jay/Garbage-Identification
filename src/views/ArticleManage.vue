<template>
  <div class="article-manage">
    <div class="header">
      <h2>文章管理</h2>
      <button class="add-btn" @click="goToPublish">发布文章</button>
    </div>

    <div class="article-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="articles.length === 0" class="empty">暂无文章</div>
      <div v-else>
        <div v-for="article in articles" :key="article.id" class="article-item">
          <div class="article-info">
            <div class="article-title">{{ article.title }}</div>
            <div class="article-meta">
              <span>阅读量：{{ article.view || 0 }}</span>
              <span>{{ formatTime(article.create_time) }}</span>
            </div>
          </div>
          <div class="article-actions">
            <button class="view-btn" @click="viewArticle(article.id)">查看</button>
            <button class="delete-btn" @click="deleteArticle(article.id)">删除</button>
          </div>
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
const articles = ref([])
const loading = ref(true)

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')}`
}

const loadArticles = async () => {
  loading.value = true
  try {
    const res = await axios.get('/api/article/list')
    if (res.data.code === 200) {
      articles.value = res.data.data || []
    }
  } catch (err) {
    console.error('获取文章列表失败', err)
    alert('获取文章列表失败')
  } finally {
    loading.value = false
  }
}

const goToPublish = () => {
  router.push('/admin/article/publish')
}

const viewArticle = (id) => {
  router.push(`/article/${id}`)
}

const deleteArticle = async (id) => {
  if (!confirm('确定要删除这篇文章吗？此操作不可恢复。')) return
  
  try {
    const token = localStorage.getItem('token')
    const res = await axios.delete(`/api/admin/article/delete/${id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      alert('删除成功')
      loadArticles()
    } else {
      alert(res.data.msg || '删除失败')
    }
  } catch (err) {
    console.error(err)
    alert('删除失败，请检查后端服务')
  }
}

onMounted(() => {
  loadArticles()
})
</script>

<style scoped>
.article-manage {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header h2 {
  margin: 0;
  font-size: 20px;
}
.add-btn {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 40px;
  cursor: pointer;
  font-size: 14px;
}
.article-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
  background: white;
  border-radius: 16px;
}
.article-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.article-info {
  flex: 1;
}
.article-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}
.article-meta {
  font-size: 12px;
  color: #999;
  display: flex;
  gap: 16px;
}
.article-actions {
  display: flex;
  gap: 8px;
}
.view-btn, .delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}
.view-btn {
  background: #3498db;
  color: white;
}
.delete-btn {
  background: #e74c3c;
  color: white;
}
</style>
