<template>
  <div class="page">
    <van-nav-bar title="我的订单" />
    
    <van-pull-refresh v-model="refreshing" @refresh="onRefresh">
      <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
        <van-cell-group v-for="order in orders" :key="order.id" inset style="margin: 8px 16px">
          <van-cell :title="order.title" :label="order.created_at" :value="`${order.points}积分`" />
          <van-cell>
            <template #default>
              <van-button size="small" type="primary" class="btn-primary" @click="download(order.id)">下载</van-button>
            </template>
          </van-cell>
        </van-cell-group>
      </van-list>
    </van-pull-refresh>
    
    <van-tabbar v-model="active" active-color="#ff6b6b" inactive-color="#999">
      <van-tabbar-item icon="home-o" to="/">首页</van-tabbar-item>
      <van-tabbar-item icon="description" to="/orders">订单</van-tabbar-item>
      <van-tabbar-item icon="user-o" to="/profile">我的</van-tabbar-item>
    </van-tabbar>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const active = ref(1)
const orders = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)
const refreshing = ref(false)

async function onLoad() {
  const res = await api.getOrders()
  orders.value = res
  loading.value = false
  finished.value = true
}

async function onRefresh() {
  await onLoad()
  refreshing.value = false
}

async function download(orderId: number) {
  const blob = await api.downloadOrder(orderId)
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `order_${orderId}.docx`
  a.click()
  window.URL.revokeObjectURL(url)
}

onMounted(onLoad)
</script>