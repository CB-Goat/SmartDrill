<template>
  <div>
    <h2 style="margin-bottom: 24px">订单管理</h2>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>标题</th>
          <th>消费积分</th>
          <th>时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="order in orders" :key="order.id">
          <td>{{ order.id }}</td>
          <td>{{ order.username }}</td>
          <td>{{ order.title }}</td>
          <td>{{ order.points }}</td>
          <td>{{ order.created_at }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const orders = ref<any[]>([])

async function onLoad() {
  const res = await api.admin.getOrders()
  orders.value = res
}

onMounted(onLoad)
</script>

<style scoped>
.data-table {
  width: 100%;
  background: #fff;
  border-radius: 4px;
  border-collapse: collapse;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.data-table th,
.data-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f0f0f0;
}

.data-table th {
  background: #fafafa;
  color: rgba(0, 0, 0, 0.85);
  font-weight: 500;
}

.data-table tbody tr:hover {
  background: #fafafa;
}
</style>