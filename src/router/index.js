import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Home from '../views/Home.vue'
import Search from '../views/Search.vue'
import Knowledge from '../views/Knowledge.vue'
import ArticleList from '../views/ArticleList.vue'
import Profile from '../views/Profile.vue'
import Recognize from '../views/Recognize.vue'
import RecognizeResult from '../views/RecognizeResult.vue'
import Feedback from '../views/Feedback.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import History from '../views/History.vue'
import ArticleDetail from '../views/ArticleDetail.vue'
import GarbageManage from '../views/GarbageManage.vue'
import ArticlePublish from '../views/ArticlePublish.vue'
import FeedbackAudit from '../views/FeedbackAudit.vue'
import ArticleManage from '../views/ArticleManage.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/home', name: 'Home', component: Home, meta: { requiresAuth: true } },
  { path: '/search', name: 'Search', component: Search, meta: { requiresAuth: true } },
  { path: '/knowledge', name: 'Knowledge', component: Knowledge, meta: { requiresAuth: true } },
  { path: '/articles', name: 'ArticleList', component: ArticleList, meta: { requiresAuth: true } },
  { path: '/profile', name: 'Profile', component: Profile, meta: { requiresAuth: true } },
  { path: '/recognize', name: 'Recognize', component: Recognize, meta: { requiresAuth: true } },
  { path: '/recognize-result', name: 'RecognizeResult', component: RecognizeResult, meta: { requiresAuth: true } },
  { path: '/feedback', name: 'Feedback', component: Feedback, meta: { requiresAuth: true } },
  { path: '/history', name: 'History', component: History, meta: { requiresAuth: true } },
  { path: '/article/:id', name: 'ArticleDetail', component: ArticleDetail, meta: { requiresAuth: true } },
  { path: '/admin', name: 'AdminDashboard', component: AdminDashboard, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/garbage', name: 'GarbageManage', component: GarbageManage, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/article/publish', name: 'ArticlePublish', component: ArticlePublish, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/feedback/audit', name: 'FeedbackAudit', component: FeedbackAudit, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/admin/articles', name: 'ArticleManage', component: ArticleManage, meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresAdmin) {
    const role = localStorage.getItem('role')
    if (role !== 'admin') {
      alert('无管理员权限')
      next('/home')
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router