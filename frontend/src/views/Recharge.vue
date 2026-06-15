<template>
  <div class="page">
    <van-nav-bar title="充值" left-arrow @click-left="$router.back()" />
    
    <van-cell-group inset style="margin: 16px">
      <van-cell title="当前积分" :value="userStore.userInfo?.points || 0" />
    </van-cell-group>

    <van-grid :column-num="3" style="margin: 16px">
      <van-grid-item v-for="item in packages" :key="item.amount" @click="recharge(item.amount)">
        <template #text>
          <div>{{ item.amount }}元</div>
          <div style="color: #ee0a24">{{ item.points }}积分</div>
        </template>
      </van-grid-item>
    </van-grid>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { api } from '@/api'
import { showSuccessToast, showConfirmDialog } from 'vant'

const userStore = useUserStore()
const packages = ref([
  { amount: 10, points: 1000 },
  { amount: 50, points: 5000 },
  { amount: 100, points: 10000 },
  { amount: 200, points: 20000 },
  { amount: 500, points: 50000 },
  { amount: 1000, points: 100000 }
])

async function recharge(amount: number) {
  await showConfirmDialog({
    title: '确认充值',
    message: `充值${amount}元，获得${amount * 100}积分`
  })
  await api.recharge(amount)
  showSuccessToast('充值成功')
  userStore.fetchUserInfo()
}

onMounted(() => {
  userStore.fetchUserInfo()
})
</script>