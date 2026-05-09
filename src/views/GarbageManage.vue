<template>
  <div class="garbage-manage">
    <div class="header">
      <h2>垃圾条目管理</h2>
      <button class="add-btn" @click="showAddDialog = true">添加条目</button>
    </div>

    <div class="search-bar">
      <input type="text" v-model="searchKeyword" placeholder="搜索垃圾名称..." @keyup.enter="loadGarbageList">
      <button @click="loadGarbageList">搜索</button>
    </div>

    <div class="garbage-list">
      <div v-if="garbageList.length === 0 && !loading" class="empty">
        暂无垃圾条目
      </div>
      <div v-for="item in garbageList" :key="item.id" class="garbage-item">
        <div class="item-info">
          <div class="item-name">{{ item.name }}</div>
          <div class="item-category" :class="categoryClass(item.category)">
            {{ item.category }}
          </div>
        </div>
        <div class="item-actions">
          <button class="edit-btn" @click="editItem(item)">编辑</button>
          <button class="delete-btn" @click="deleteItem(item.id)">删除</button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="showAddDialog || showEditDialog" class="dialog-overlay" @click="closeDialog">
      <div class="dialog-content" @click.stop>
        <h3>{{ showAddDialog ? '添加垃圾条目' : '编辑垃圾条目' }}</h3>
        <div class="form-item">
          <label>垃圾名称</label>
          <input type="text" v-model="formData.name" placeholder="例如：塑料瓶">
        </div>
        <div class="form-item">
          <label>所属分类</label>
          <div class="category-select">
            <button
              v-for="cat in categories"
              :key="cat"
              :class="{ active: formData.category === cat }"
              @click="formData.category = cat"
            >
              {{ cat }}
            </button>
          </div>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="closeDialog">取消</button>
          <button class="submit-btn" @click="submitForm" :disabled="submitting">
            {{ submitting ? '提交中...' : '提交' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const garbageList = ref([])
const loading = ref(true)
const searchKeyword = ref('')
const showAddDialog = ref(false)
const showEditDialog = ref(false)
const submitting = ref(false)
const categories = ['可回收物', '有害垃圾', '厨余垃圾', '其他垃圾']
const formData = ref({
  id: '',
  name: '',
  category: '可回收物'
})

const categoryClass = (category) => {
  const map = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '其他垃圾': 'other'
  }
  return map[category] || ''
}

const loadGarbageList = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/admin/garbage/list', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      let data = res.data.data || []
      if (searchKeyword.value) {
        data = data.filter(item => item.name.includes(searchKeyword.value))
      }
      garbageList.value = data
    } else {
      alert(res.data.msg || '获取列表失败')
    }
  } catch (err) {
    console.error(err)
    alert('获取垃圾列表失败，请检查后端服务')
  } finally {
    loading.value = false
  }
}

const editItem = (item) => {
  formData.value = {
    id: item.id,
    name: item.name,
    category: item.category
  }
  showEditDialog.value = true
}

const deleteItem = async (id) => {
  if (!confirm('确定要删除这个垃圾条目吗？')) return
  try {
    const token = localStorage.getItem('token')
    const res = await axios.delete(`/api/admin/garbage/${id}/delete`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      alert('删除成功')
      loadGarbageList()
    } else {
      alert(res.data.msg || '删除失败')
    }
  } catch (err) {
    console.error(err)
    alert('删除失败，请检查后端服务')
  }
}

const submitForm = async () => {
  if (!formData.value.name || !formData.value.category) {
    alert('请填写完整信息')
    return
  }
  submitting.value = true
  try {
    const token = localStorage.getItem('token')
    let res
    if (showAddDialog.value) {
      res = await axios.post('/api/admin/garbage/add', {
        name: formData.value.name,
        category: formData.value.category
      }, { headers: { Authorization: `Bearer ${token}` } })
    } else {
      res = await axios.put(`/api/admin/garbage/${formData.value.id}/edit`, {
        name: formData.value.name,
        category: formData.value.category
      }, { headers: { Authorization: `Bearer ${token}` } })
    }

    if (res.data.code === 200) {
      alert(showAddDialog.value ? '添加成功' : '修改成功')
      closeDialog()
      loadGarbageList()
    } else {
      alert(res.data.msg || '操作失败')
    }
  } catch (err) {
    console.error(err)
    alert('操作失败，请检查后端服务')
  } finally {
    submitting.value = false
  }
}

const closeDialog = () => {
  showAddDialog.value = false
  showEditDialog.value = false
  formData.value = {
    id: '',
    name: '',
    category: '可回收物'
  }
}

onMounted(() => {
  loadGarbageList()
})
</script>

<style scoped>
.garbage-manage {
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
  cursor: pointer;
}
.garbage-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.garbage-item {
  background: white;
  border-radius: 16px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.item-info {
  flex: 1;
}
.item-name {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 8px;
}
.item-category {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}
.recyclable { background: #3498db; }
.harmful { background: #e74c3c; }
.kitchen { background: #f39c12; }
.other { background: #95a5a6; }
.item-actions {
  display: flex;
  gap: 8px;
}
.edit-btn, .delete-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}
.edit-btn {
  background: #3498db;
  color: white;
}
.delete-btn {
  background: #e74c3c;
  color: white;
}
.empty {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  background: white;
  border-radius: 16px;
}
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog-content {
  background: white;
  border-radius: 24px;
  padding: 24px;
  width: 90%;
  max-width: 400px;
}
.dialog-content h3 {
  margin: 0 0 20px;
  font-size: 20px;
}
.form-item {
  margin-bottom: 20px;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}
.form-item input[type="text"] {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 16px;
  box-sizing: border-box;
}
.category-select {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.category-select button {
  flex: 1;
  padding: 10px 0;
  border: 1px solid #ddd;
  background: white;
  border-radius: 40px;
  font-size: 14px;
  cursor: pointer;
  transition: 0.2s;
  min-width: 70px;
}
.category-select button.active {
  background: #2ecc71;
  color: white;
  border-color: #2ecc71;
}
.dialog-actions {
  display: flex;
  gap: 12px;
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
