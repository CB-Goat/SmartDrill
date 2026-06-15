<template>
  <div>
    <van-nav-bar title="充值记录" left-arrow @click-left="$router.back()" />
    <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
      <van-cell-group v-for="item in records" :key="item.id" inset style="margin: 8px 16px">
        <van-cell :title="item.username" :label="item.created_at" :value="`${item.amount}元`" />
      </van-cell-group>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const records = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)

async function onLoad() {
  const res = await api.admin.getRecharges()
  records.value = res
  loading.value = false
  finished.value = true
}

onMounted(onLoad)
</script>