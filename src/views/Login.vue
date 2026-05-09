<template>
  <div class="login-container">
    <div class="card">
      <h2>垃圾分类智能识别系统</h2>
      <div class="tab-buttons">
        <button 
          :class="{ active: isLogin }" 
          @click="isLogin = true"
          type="button"
        >登录</button>
        <button 
          :class="{ active: !isLogin }" 
          @click="isLogin = false"
          type="button"
        >注册</button>
      </div>
      
      <div v-if="isLogin">
        <input type="text" placeholder="手机号" v-model="loginForm.phone">
        <input type="password" placeholder="密码" v-model="loginForm.password">
        <button class="submit-btn" @click="handleLogin">登录</button>
      </div>
      
      <div v-else>
        <input type="text" placeholder="手机号" v-model="registerForm.phone">
        <input type="password" placeholder="密码" v-model="registerForm.password">
        <input type="text" placeholder="昵称" v-model="registerForm.nickname">
        <button class="submit-btn" @click="handleRegister">注册</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const isLogin = ref(true)
const router = useRouter()
const loginForm = ref({ phone: '', password: '' })
const registerForm = ref({ phone: '', password: '', nickname: '' })

const handleLogin = async () => {
  if (!loginForm.value.phone || !loginForm.value.password) {
    alert('请填写手机号和密码')
    return
  }
  try {
    const res = await axios.post('/api/login', {
      phone: loginForm.value.phone,
      password: loginForm.value.password
    })
    if (res.data.code === 200) {
      const token = res.data.data.token
      localStorage.setItem('token', token)
      // 后端登录接口不返回role，需要调用其他接口获取用户信息
      // 暂时使用手机号判断管理员（13800000000为管理员）
      const role = loginForm.value.phone === '13800000000' ? 'admin' : 'user'
      localStorage.setItem('role', role)
      router.push('/home')
    } else {
      alert(res.data.msg || '登录失败')
    }
  } catch (err) {
    alert('网络错误，请确保后端已启动')
  }
}

const handleRegister = async () => {
  if (!registerForm.value.phone || !registerForm.value.password) {
    alert('请填写完整信息')
    return
  }
  try {
    const res = await axios.post('/api/register', {
      phone: registerForm.value.phone,
      password: registerForm.value.password,
      nickname: registerForm.value.nickname || '用户'
    })
    if (res.data.code === 200) {
      alert('注册成功，请登录')
      isLogin.value = true
    } else {
      alert(res.data.msg || '注册失败')
    }
  } catch (err) {
    alert('注册失败，请检查后端')
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #f0f2f5;
}
.card {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 300px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
h2 {
  text-align: center;
  margin-top: 0;
  margin-bottom: 1.5rem;
}
.tab-buttons {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-bottom: 1.5rem;
}
.tab-buttons button {
  background: none;
  border: none;
  font-size: 1.2rem;
  padding: 0.25rem 0;
  cursor: pointer;
  color: #888;
  border-bottom: 2px solid transparent;
}
.tab-buttons button.active {
  color: #42b983;
  border-bottom-color: #42b983;
}
input {
  width: 100%;
  padding: 10px;
  margin: 8px 0;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
}
.submit-btn {
  width: 100%;
  padding: 10px;
  background: #42b983;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  margin-top: 12px;
  font-size: 1rem;
}
.submit-btn:hover {
  background: #35a06e;
}
</style>