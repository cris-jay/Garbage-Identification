<template>
  <div class="knowledge">
    <div class="category-tabs">
      <div v-for="cat in categories" :key="cat.id" :class="{ active: activeCat === cat.id }" @click="activeCat = cat.id; loadItems(cat.id)">
        {{ cat.name }}
      </div>
    </div>
    <div class="content">
      <div class="guide">
        <h3>{{ currentCatName }}投放指南</h3>
        <div v-if="items.length > 0" class="tag-group">
          <span v-for="item in items" :key="item.name">{{ item.name }}</span>
        </div>
        <div v-else class="loading">加载中...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const categories = ref([])
const activeCat = ref(null)
const items = ref([])

const currentCatName = computed(() => {
  const cat = categories.value.find(c => c.id === activeCat.value)
  return cat ? cat.name : ''
})

const loadCategories = async () => {
  try {
    const res = await axios.get('/api/category')
    if (res.data.code === 200) {
      categories.value = res.data.data || []
      if (categories.value.length > 0) {
        activeCat.value = categories.value[0].id
        loadItems(activeCat.value)
      }
    }
  } catch (err) {
    console.error('获取分类失败', err)
  }
}

const loadItems = async (categoryId) => {
  if (!categoryId) return
  items.value = []
  try {
    const res = await axios.get(`/api/garbage/list?category_id=${categoryId}`)
    if (res.data.code === 200) {
      items.value = res.data.data || []
    }
  } catch (err) {
    console.error('获取垃圾列表失败', err)
  }
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.knowledge {
  padding: 16px;
}
.category-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 20px;
  background: white;
  padding: 8px;
  border-radius: 48px;
}
.category-tabs div {
  flex: 1;
  text-align: center;
  padding: 8px;
  border-radius: 40px;
  background: #f0f2f5;
  cursor: pointer;
}
.category-tabs .active {
  background: #2ecc71;
  color: white;
}
.guide {
  background: white;
  border-radius: 24px;
  padding: 20px;
}
.tag-group span {
  display: inline-block;
  background: #e8f5e9;
  padding: 6px 12px;
  border-radius: 20px;
  margin: 4px;
  font-size: 12px;
}
.item-title {
  font-weight: bold;
  margin: 16px 0 8px;
}
.loading {
  text-align: center;
  color: #999;
  padding: 20px;
}
</style>
