import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import api from './api'
import 'vant/lib/index.css'
import { Tabbar, TabbarItem } from 'vant'

const app = createApp(App)
app.use(router)
app.use(Tabbar)
app.use(TabbarItem)

// 全局挂载api
app.config.globalProperties.$api = api

app.mount('#app')