<template>
  <div>
    <van-nav-bar title="仪表盘" left-arrow @click-left="$router.back()" />
    <van-cell-group inset style="margin: 16px">
      <van-cell title="总用户数" :value="stats.users" />
      <van-cell title="总充值" :value="`${stats.recharge}元`" />
      <van-cell title="总消费" :value="`${stats.consumption}积分`" />
    </van-cell-group>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const stats = ref({ users: 0, recharge: 0, consumption: 0 })
</script>