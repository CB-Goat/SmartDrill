<template>
  <div class="home-page">
    <div class="header-bg">
      <div class="header-content">
        <div class="welcome-text">欢迎回来</div>
        <div class="user-name">{{ userStore.userInfo?.username || '用户' }}</div>
      </div>
      <div class="points-card">
        <div class="points-label">我的积分</div>
        <div class="points-value">{{ userStore.userInfo?.points || 0 }}</div>
        <router-link to="/recharge" class="recharge-btn">立即充值</router-link>
      </div>
    </div>

    <div class="main-content">
      <div class="section-title">快捷功能</div>
      <div class="function-grid">
        <router-link to="/review" class="function-card review-card">
          <div class="card-icon">📚</div>
          <div class="card-title">复习资料</div>
          <div class="card-desc">知识点·考点·题型</div>
        </router-link>
        <router-link to="/practice" class="function-card practice-card">
          <div class="card-icon">✏️</div>
          <div class="card-title">练习题</div>
          <div class="card-desc">单元·期中·期末</div>
        </router-link>
        <router-link to="/orders" class="function-card orders-card">
          <div class="card-icon">📋</div>
          <div class="card-title">我的订单</div>
          <div class="card-desc">查看下载记录</div>
        </router-link>
        <router-link to="/recharge" class="function-card recharge-card">
          <div class="card-icon">💎</div>
          <div class="card-title">充值中心</div>
          <div class="card-desc">获取更多积分</div>
        </router-link>
      </div>
    </div>

    <van-tabbar v-model="active" active-color="#ff6b6b" inactive-color="#999">
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

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
  padding-bottom: 60px;
}

.header-bg {
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 50%, #ffa5a5 100%);
  padding: 40px 20px 80px;
  border-radius: 0 0 30px 30px;
  position: relative;
}

.header-content {
  text-align: center;
  color: #fff;
  margin-bottom: 20px;
}

.welcome-text {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.user-name {
  font-size: 24px;
  font-weight: bold;
}

.points-card {
  background: #fff;
  border-radius: 16px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 8px 20px rgba(255, 107, 107, 0.3);
  position: absolute;
  left: 20px;
  right: 20px;
  bottom: -50px;
}

.points-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 8px;
}

.points-value {
  font-size: 36px;
  font-weight: bold;
  color: #ff6b6b;
  margin-bottom: 12px;
}

.recharge-btn {
  display: inline-block;
  background: linear-gradient(135deg, #ff6b6b 0%, #ff8e8e 100%);
  color: #fff;
  padding: 8px 24px;
  border-radius: 20px;
  font-size: 14px;
  text-decoration: none;
  transition: transform 0.3s, box-shadow 0.3s;
}

.recharge-btn:active {
  transform: scale(0.95);
}

.main-content {
  padding: 70px 20px 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 16px;
  padding-left: 4px;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.function-card {
  background: #fff;
  border-radius: 16px;
  padding: 24px 16px;
  text-align: center;
  text-decoration: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transition: transform 0.3s, box-shadow 0.3s;
}

.function-card:active {
  transform: translateY(-4px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.12);
}

.card-icon {
  font-size: 40px;
  margin-bottom: 12px;
}

.card-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.card-desc {
  font-size: 12px;
  color: #999;
}

.review-card {
  background: linear-gradient(135deg, #fff 0%, #fff5f5 100%);
  border: 2px solid #ffe8e8;
}

.practice-card {
  background: linear-gradient(135deg, #fff 0%, #f0f9ff 100%);
  border: 2px solid #e0f2fe;
}

.orders-card {
  background: linear-gradient(135deg, #fff 0%, #fefce8 100%);
  border: 2px solid #fef3c7;
}

.recharge-card {
  background: linear-gradient(135deg, #fff 0%, #fdf2f8 100%);
  border: 2px solid #fce7f3;
}
</style>