<template>
  <div class="feedback-audit">
    <div class="header">
      <h2>反馈审核</h2>
    </div>

    <div class="stats-card">
      <div class="stats-item">
        <div class="stats-num">{{ pendingCount }}</div>
        <div class="stats-label">待审核反馈</div>
      </div>
    </div>

    <div class="feedback-list">
      <h3>反馈列表</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="feedbackList.length === 0" class="empty">暂无反馈记录</div>
      <div v-else>
        <div v-for="item in feedbackList" :key="item.id" class="feedback-item">
          <div class="feedback-header">
            <div class="feedback-id">反馈 #{{ item.id }}</div>
            <div class="feedback-status" :class="item.status">{{ statusText(item.status) }}</div>
          </div>
          <div class="feedback-content">
            <div class="content-row">
              <span class="label">用户：</span>
              <span>{{ item.nickname || item.phone || '未知用户' }}</span>
            </div>
            <div class="content-row">
              <span class="label">建议分类：</span>
              <span class="category-badge" :class="categoryClass(item.correct_category)">{{ item.correct_category }}</span>
            </div>
            <div class="content-row">
              <span class="label">反馈内容：</span>
              <span>{{ item.content || '无' }}</span>
            </div>
            <div class="content-row">
              <span class="label">提交时间：</span>
              <span>{{ formatTime(item.create_time) }}</span>
            </div>
            <div v-if="item.status !== 'pending'" class="content-row">
              <span class="label">审核结果：</span>
              <span>{{ item.audit_result || '无' }}</span>
            </div>
          </div>
          <div v-if="item.status === 'pending'" class="feedback-actions">
            <button class="approve-btn" @click="openAuditDialog(item, 'resolved')">通过</button>
            <button class="reject-btn" @click="openAuditDialog(item, 'rejected')">驳回</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 审核对话框 -->
    <div v-if="showAuditDialog" class="dialog-overlay" @click="closeAuditDialog">
      <div class="dialog-content" @click.stop>
        <h3>{{ auditForm.status === 'resolved' ? '通过反馈' : '驳回反馈' }}</h3>
        <div class="form-item">
          <label>反馈ID</label>
          <input type="text" :value="auditForm.id" disabled>
        </div>
        <div class="form-item">
          <label>审核意见</label>
          <textarea v-model="auditForm.audit_result" rows="3" placeholder="请输入审核意见"></textarea>
        </div>
        <div class="dialog-actions">
          <button class="cancel-btn" @click="closeAuditDialog">取消</button>
          <button class="submit-btn" @click="handleAudit" :disabled="auditing">
            {{ auditing ? '提交中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'

const feedbackList = ref([])
const loading = ref(true)
const auditing = ref(false)
const showAuditDialog = ref(false)
const auditForm = ref({
  id: '',
  status: 'resolved',
  audit_result: ''
})

const pendingCount = computed(() => {
  return feedbackList.value.filter(item => item.status === 'pending').length
})

const statusText = (status) => {
  const map = {
    'pending': '待审核',
    'resolved': '已通过',
    'rejected': '已驳回'
  }
  return map[status] || status
}

const categoryClass = (category) => {
  const map = {
    '可回收物': 'recyclable',
    '有害垃圾': 'harmful',
    '厨余垃圾': 'kitchen',
    '湿垃圾': 'kitchen',
    '干垃圾': 'other',
    '其他垃圾': 'other'
  }
  return map[category] || ''
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getFullYear()}-${String(date.getMonth()+1).padStart(2,'0')}-${String(date.getDate()).padStart(2,'0')} ${String(date.getHours()).padStart(2,'0')}:${String(date.getMinutes()).padStart(2,'0')}`
}

const loadFeedbackList = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.get('/api/admin/feedback/list', {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      feedbackList.value = res.data.data || []
    }
  } catch (err) {
    console.error('获取反馈列表失败', err)
    alert('获取反馈列表失败')
  } finally {
    loading.value = false
  }
}

const openAuditDialog = (item, status) => {
  auditForm.value = {
    id: item.id,
    status: status,
    audit_result: ''
  }
  showAuditDialog.value = true
}

const closeAuditDialog = () => {
  showAuditDialog.value = false
  auditForm.value = { id: '', status: 'resolved', audit_result: '' }
}

const handleAudit = async () => {
  if (auditForm.value.status === 'rejected' && !auditForm.value.audit_result.trim()) {
    alert('驳回时必须填写审核意见')
    return
  }
  
  auditing.value = true
  try {
    const token = localStorage.getItem('token')
    const res = await axios.put(`/api/admin/feedback/${auditForm.value.id}/audit`, {
      status: auditForm.value.status,
      audit_result: auditForm.value.audit_result
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      alert('审核成功')
      closeAuditDialog()
      loadFeedbackList()
    } else {
      alert(res.data.msg || '审核失败')
    }
  } catch (err) {
    console.error(err)
    alert('审核失败，请检查后端服务')
  } finally {
    auditing.value = false
  }
}

onMounted(() => {
  loadFeedbackList()
})
</script>

<style scoped>
.feedback-audit {
  padding: 16px;
  background: #f5f7fa;
  min-height: 100vh;
}
.header {
  margin-bottom: 20px;
}
.header h2 {
  margin: 0;
  font-size: 20px;
}
.stats-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  margin-bottom: 20px;
}
.stats-num {
  font-size: 48px;
  font-weight: bold;
  color: #f39c12;
}
.stats-label {
  font-size: 14px;
  color: #666;
  margin-top: 8px;
}
.feedback-list {
  background: white;
  border-radius: 16px;
  padding: 20px;
}
.feedback-list h3 {
  margin: 0 0 16px;
  font-size: 16px;
}
.loading, .empty {
  text-align: center;
  padding: 40px;
  color: #999;
}
.feedback-item {
  border: 1px solid #eee;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
}
.feedback-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.feedback-id {
  font-size: 14px;
  font-weight: bold;
  color: #333;
}
.feedback-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}
.feedback-status.pending { background: #f39c12; }
.feedback-status.resolved { background: #2ecc71; }
.feedback-status.rejected { background: #e74c3c; }
.feedback-content {
  margin-bottom: 12px;
}
.content-row {
  margin-bottom: 8px;
  font-size: 14px;
}
.content-row .label {
  color: #666;
  margin-right: 8px;
}
.category-badge {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}
.recyclable { background: #3498db; }
.harmful { background: #e74c3c; }
.kitchen { background: #f39c12; }
.other { background: #95a5a6; }
.feedback-actions {
  display: flex;
  gap: 8px;
}
.approve-btn, .reject-btn {
  flex: 1;
  padding: 10px;
  border: none;
  border-radius: 40px;
  font-size: 14px;
  cursor: pointer;
}
.approve-btn {
  background: #2ecc71;
  color: white;
}
.reject-btn {
  background: #e74c3c;
  color: white;
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
  margin-bottom: 16px;
}
.form-item label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
  font-size: 14px;
}
.form-item input,
.form-item textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 12px;
  font-size: 14px;
  box-sizing: border-box;
  font-family: inherit;
}
.form-item input:disabled {
  background: #f0f2f5;
}
.dialog-actions {
  display: flex;
  gap: 12px;
  margin-top: 20px;
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
