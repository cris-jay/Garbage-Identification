<template>
  <div class="app-container">
    <!-- 主要内容区域 -->
    <router-view />
    <!-- 底部导航栏（只在部分页面显示，如首页/搜索/知识库/科普/个人中心） -->
    <van-tabbar v-model="active" fixed v-if="showTabBar" @change="onTabChange">
      <van-tabbar-item icon="wap-home-o">首页</van-tabbar-item>
      <van-tabbar-item icon="search">搜索</van-tabbar-item>
      <van-tabbar-item icon="bookmark-o">知识库</van-tabbar-item>
      <van-tabbar-item icon="newspaper-o">科普</van-tabbar-item>
      <van-tabbar-item icon="user-o">个人中心</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const active = ref(0)

const showTabBar = computed(() => {
  // 需要显示底部导航的页面路由名称列表
  const tabBarPages = ['Home', 'Search', 'Knowledge', 'ArticleList', 'Profile']
  return tabBarPages.includes(route.name)
})

const onTabChange = (index) => {
  const routes = ['Home', 'Search', 'Knowledge', 'ArticleList', 'Profile']
  router.push({ name: routes[index] })
}

// 监听路由变化，同步选中状态
watch(() => route.name, (newName) => {
  const map = {
    'Home': 0,
    'Search': 1,
    'Knowledge': 2,
    'ArticleList': 3,
    'Profile': 4
  }
  if (map[newName] !== undefined) active.value = map[newName]
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: #f8f8f8;
}
.app-container {
  padding-bottom: 50px; /* 给底部tab预留空间 */
}
</style>