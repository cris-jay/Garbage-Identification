<template>
  <div class="recognize-page">
    <h2>垃圾拍照识别</h2>
    <div class="upload-area" @click="triggerFileInput">
      <input type="file" accept="image/*" ref="fileInput" style="display: none" @change="onFileSelected">
      <div v-if="!previewUrl" class="placeholder">
        <div class="icon">📷</div>
        <p>点击上传或拍照</p>
      </div>
      <img v-else :src="previewUrl" class="preview">
    </div>
    <button @click="recognize" :disabled="!previewUrl || loading" class="recognize-btn">
      {{ loading ? '识别中...' : '开始识别' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const fileInput = ref(null)
const previewUrl = ref('')
const loading = ref(false)

const triggerFileInput = () => {
  fileInput.value.click()
}

const onFileSelected = (e) => {
  const file = e.target.files[0]
  if (file) {
    const url = URL.createObjectURL(file)
    previewUrl.value = url
  }
}

const recognize = async () => {
  if (!previewUrl.value) return
  loading.value = true

  try {
    // 读取图片文件并转换为 base64
    const file = fileInput.value.files[0]
    if (!file) throw new Error('请先选择图片')

    const base64 = await new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        // 去除 data:image/...;base64, 前缀，只保留纯 base64
        let result = reader.result
        const commaIndex = result.indexOf(',')
        if (commaIndex !== -1) result = result.substring(commaIndex + 1)
        resolve(result)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })

    const token = localStorage.getItem('token')
    const res = await axios.post('/api/recognize/image', { image_base64: base64 }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.code === 200) {
      const resultData = res.data.data
      // 跳转到结果页，并传递识别结果和图片URL
      router.push({
        path: '/recognize-result',
        query: {
          img: previewUrl.value,
          name: resultData.name,
          category: resultData.category,
          category_id: resultData.category_id,
          confidence: resultData.confidence,
          desc: resultData.desc
        }
      })
    } else {
      alert(res.data.msg || '识别失败')
    }
  } catch (err) {
    console.error(err)
    alert('识别失败，请检查网络或后端服务')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.recognize-page {
  padding: 20px;
  text-align: center;
}
.upload-area {
  width: 100%;
  height: 250px;
  border: 2px dashed #ccc;
  border-radius: 16px;
  display: flex;
  justify-content: center;
  align-items: center;
  margin: 20px 0;
  cursor: pointer;
  background: #fafafa;
}
.placeholder {
  text-align: center;
}
.placeholder .icon {
  font-size: 48px;
  margin-bottom: 8px;
}
.preview {
  max-width: 100%;
  max-height: 250px;
  object-fit: contain;
}
.recognize-btn {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 40px;
  font-size: 16px;
  width: 80%;
  cursor: pointer;
}
.recognize-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}
</style>