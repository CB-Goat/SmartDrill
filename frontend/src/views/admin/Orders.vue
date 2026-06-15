<template>
  <div>
    <van-nav-bar title="订单管理" left-arrow @click-left="$router.back()" />
    <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
      <van-cell-group v-for="order in orders" :key="order.id" inset style="margin: 8px 16px">
        <van-cell :title="order.title" :label="order.created_at" :value="`${order.points}积分`" />
      </van-cell-group>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const orders = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)

async function onLoad() {
  const res = await api.admin.getOrders()
  orders.value = res
  loading.value = false
  finished.value = true
}

onMounted(onLoad)
</script>