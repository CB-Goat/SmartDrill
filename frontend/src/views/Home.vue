<template>
  <div class="page">
    <van-nav-bar title="智练通" />
    
    <van-cell-group inset style="margin: 16px">
      <van-cell title="积分余额" :value="userStore.userInfo?.points || 0" />
    </van-cell-group>

    <van-grid :column-num="2" style="margin: 16px">
      <van-grid-item icon="points" text="充值" to="/recharge" />
      <van-grid-item icon="description" text="复习资料" to="/review" />
      <van-grid-item icon="edit" text="练习题" to="/practice" />
      <van-grid-item icon="orders-o" text="我的订单" to="/orders" />
    </van-grid>

    <van-tabbar v-model="active">
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="description" to="/review">复习</van-tabbar-item>
      <van-tabbar-item icon="edit" to="/practice">练习</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/orders">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()
const active = ref(0)

onMounted(() => {
  userStore.fetchUserInfo()
})
</script>