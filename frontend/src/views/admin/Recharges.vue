<template>
  <div>
    <h2 style="margin-bottom: 24px">充值记录</h2>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>用户名</th>
          <th>充值金额</th>
          <th>获得积分</th>
          <th>时间</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in records" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.username }}</td>
          <td>{{ item.amount }}元</td>
          <td>{{ item.points }}</td>
          <td>{{ item.created_at }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { api } from '@/api'

const records = ref<any[]>([])

async function onLoad() {
  const res = await api.admin.getRecharges()
  records.value = res
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