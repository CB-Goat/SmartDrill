<template>
  <div>
    <h2 style="margin-bottom: 24px">仪表盘</h2>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px">
      <div class="stat-card">
        <div class="stat-title">总用户数</div>
        <div class="stat-value">{{ stats.users }}</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">总充值</div>
        <div class="stat-value">{{ stats.recharge }}元</div>
      </div>
      <div class="stat-card">
        <div class="stat-title">总消费</div>
        <div class="stat-value">{{ stats.consumption }}积分</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const stats = ref({ users: 0, recharge: 0, consumption: 0 })
</script>

<style scoped>
.stat-card {
  background: #fff;
  padding: 24px;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.stat-title {
  color: rgba(0, 0, 0, 0.45);
  font-size: 14px;
  margin-bottom: 8px;
}

.stat-value {
  color: rgba(0, 0, 0, 0.85);
  font-size: 30px;
  font-weight: 500;
}
</style>