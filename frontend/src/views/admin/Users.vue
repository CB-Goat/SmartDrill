<template>
  <div>
    <van-nav-bar title="用户管理" left-arrow @click-left="$router.back()" />
    <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
      <van-cell-group v-for="user in users" :key="user.id" inset style="margin: 8px 16px">
        <van-cell :title="user.username" :label="user.phone" :value="`${user.points}积分`" />
      </van-cell-group>
    </van-list>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const users = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)

async function onLoad() {
  const res = await api.admin.getUsers()
  users.value = res
  loading.value = false
  finished.value = true
}

onMounted(onLoad)
</script>