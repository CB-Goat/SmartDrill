<template>
  <div class="page">
    <van-nav-bar title="充值" left-arrow @click-left="$router.back()" />
    
    <van-cell-group inset style="margin: 16px">
      <van-cell title="当前积分" :value="userStore.userInfo?.points || 0" />
    </van-cell-group>

    <div class="recharge-guide">
      <div class="guide-title">充值步骤</div>
      
      <div class="step">
        <div class="step-number">1</div>
        <div class="step-content">
          <div class="step-text">长按下方二维码，关注公众号</div>
        </div>
      </div>

      <div class="qr-container">
        <img src="/wechat_qr.jpg" alt="公众号二维码" class="qr-img" />
        <div class="qr-tip">扫码关注"鸡娃有方"</div>
      </div>

      <div class="step">
        <div class="step-number">2</div>
        <div class="step-content">
          <div class="step-text">进入公众号，点击底部"订阅充值"菜单，获取付款二维码</div>
        </div>
      </div>

      <div class="step">
        <div class="step-number">3</div>
        <div class="step-content">
          <div class="step-text">选择订阅充值产品，完成付款</div>
        </div>
      </div>

      <div class="step">
        <div class="step-number">4</div>
        <div class="step-content">
          <div class="step-text">系统增加用户积分（1元兑换100积分）</div>
        </div>
      </div>

      <div class="tip">
        <van-icon name="info-o" />
        <span>充值问题请联系公众号客服</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  userStore.fetchUserInfo()
})
</script>

<style scoped>
.recharge-guide {
  padding: 0 16px 24px;
}

.guide-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #323233;
}

.step {
  display: flex;
  align-items: flex-start;
  margin-bottom: 16px;
}

.step-number {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ff6b6b, #ff8e8e);
  color: white;
  font-size: 14px;
  font-weight: bold;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-right: 12px;
}

.step-content {
  flex: 1;
  padding-top: 2px;
}

.step-text {
  font-size: 15px;
  color: #323233;
  line-height: 1.6;
}

.qr-container {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  margin: 16px 0 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

.qr-img {
  width: 180px;
  height: 180px;
  border-radius: 8px;
}

.qr-tip {
  margin-top: 12px;
  font-size: 14px;
  color: #646566;
}

.tip {
  margin-top: 20px;
  font-size: 13px;
  color: #969799;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
</style>