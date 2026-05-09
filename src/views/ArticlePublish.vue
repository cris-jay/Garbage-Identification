<template>
  <div class="article-publish">
    <div class="header">
      <h2>发布科普文章</h2>
    </div>

    <div class="form-container">
      <div class="form-item">
        <label>文章标题 *</label>
        <input type="text" v-model="articleForm.title" placeholder="请输入文章标题">
      </div>

      <div class="form-item">
        <label>作者</label>
        <input type="text" v-model="articleForm.author" placeholder="请输入作者名称">
      </div>

      <div class="form-item">
        <label>封面图片URL</label>
        <input type="text" v-model="articleForm.cover" placeholder="请输入封面图片URL（可选）">
      </div>

      <div class="form-item">
        <label>文章内容 *</label>
        <textarea v-model="articleForm.content" rows="15" placeholder="请输入文章内容，支持HTML格式"></textarea>
      </div>

      <div class="form-actions">
        <button class="cancel-btn" @click="goBack">取消</button>
        <button class="submit-btn" @click="publishArticle" :disabled="publishing">
          {{ publishing ? '发布中...' : '发布文章' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const publishing = ref(false)
const articleForm = ref({
  title: '',
  author: '管理员',
  cover: '',
  content: ''
})

const goBack = () => {
  router.back()
}

const publishArticle = async () => {
  if (!articleForm.value.title.trim()) {
    alert('请输入文章标题')
    return
  }
  if (!articleForm.value.content.trim()) {
    alert('请输入文章内容')
    return
  }

  publishing.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.post('/api/admin/article/publish', articleForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    if (res.data.code === 200) {
      alert('文章发布成功')
      router.push('/articles')
    } else {
      alert(res.data.msg || '发布失败')
    }
  } catch (err) {
    console.error(err)
    alert('发布失败，请检查后端服务')
  } finally {
    publishing.value = false
  }
}
</script>

<style scoped>
.article-publish {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.header {
  margin-bottom: 24px;
}
.header h2 {
  margin: 0;
  font-size: 20px;
}
.form-container {
  background: white;
  border-radius: 24px;
  padding: 24px;
}
.form-item {
  margin-bottom: 20px;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}
.form-item input[type="text"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
}
.form-item textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 14px;
  resize: vertical;
  font-family: inherit;
  box-sizing: border-box;
  line-height: 1.6;
}
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
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
