<template>
  <div class="search-page">
    <div class="search-bar">
      <input type="text" placeholder="搜索如：奶茶杯、旧衣服..." v-model="keyword" @keyup.enter="doSearch">
      <button @click="doSearch">搜索</button>
    </div>
    <div v-if="!searched" class="hot-search">
      <div class="label">热门搜索</div>
      <div class="tags">
        <span v-for="tag in hotList" :key="tag" @click="keyword = tag; doSearch()">{{ tag }}</span>
      </div>
    </div>
    <div v-else>
      <div v-if="results.length === 0" class="no-result">未找到相关垃圾</div>
      <div v-for="item in results" :key="item.name" class="result-item">
        <h4>{{ item.name }}</h4>
        <p class="category" :class="categoryClass(item.category)">{{ item.category }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const keyword = ref('')
const results = ref([])
const searched = ref(false)
const hotList = ['过期药品', '快递纸箱', '茶叶渣', '碎玻璃', '旧衣服', '奶茶杯']

const categoryClass = (category) => {
  const map = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other'
  }
  return map[category] || ''
}

const doSearch = async () => {
  if (!keyword.value.trim()) {
    alert('请输入搜索内容')
    return
  }
  searched.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get(`/api/search?q=${encodeURIComponent(keyword.value)}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      results.value = res.data.data || []
    } else {
      results.value = []
      alert(res.data.msg || '搜索失败')
    }
  } catch (err) {
    console.error(err)
    alert('网络错误，请确保后端已启动')
    results.value = []
  }
}
</script>

<style scoped>
.search-page {
  padding: 16px;
}
.search-bar {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
}
.search-bar input {
  flex: 1;
  padding: 12px;
  border: 1px solid #e0e0e0;
  border-radius: 40px;
  font-size: 14px;
}
.search-bar button {
  background: #2ecc71;
  border: none;
  border-radius: 40px;
  padding: 0 20px;
  color: white;
}
.label {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.tags span {
  background: #f0f2f5;
  padding: 8px 16px;
  border-radius: 40px;
  font-size: 14px;
  cursor: pointer;
}
.result-item {
  background: white;
  border-radius: 16px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.category {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}
.recyclable { background: #3498db; }
.kitchen { background: #f39c12; }
.harmful { background: #e74c3c; }
.other { background: #95a5a6; }
.desc { font-size: 12px; color: #666; margin-top: 8px; }
</style>