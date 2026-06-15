<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">知识点管理</h2>
      <button class="btn-primary" @click="showForm = true">添加知识点</button>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>标题</th>
          <th>单元ID</th>
          <th>考试频率</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in knowledge" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.title }}</td>
          <td>{{ item.unit_id }}</td>
          <td>{{ item.exam_frequency }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑知识点' : '添加知识点' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>单元ID</label>
            <input v-model="form.unit_id" type="number" required />
          </div>
          <div class="form-item">
            <label>标题</label>
            <input v-model="form.title" required />
          </div>
          <div class="form-item">
            <label>内容</label>
            <textarea v-model="form.content" rows="5" required></textarea>
          </div>
          <div class="form-item">
            <label>考试频率</label>
            <input v-model="form.exam_frequency" />
          </div>
          <div class="form-item">
            <label>考试题型</label>
            <input v-model="form.exam_types" />
          </div>
          <div class="form-actions">
            <button type="button" class="btn-default" @click="showForm = false">取消</button>
            <button type="submit" class="btn-primary">保存</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/api'

const knowledge = ref<any[]>([])
const showForm = ref(false)
const form = reactive({ id: 0, unit_id: 1, title: '', content: '', exam_frequency: '', exam_types: '' })

async function onLoad() {
  const res = await api.admin.getKnowledge()
  knowledge.value = res
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveKnowledge(form)
  showForm.value = false
  Object.assign(form, { id: 0, unit_id: 1, title: '', content: '', exam_frequency: '', exam_types: '' })
  onLoad()
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

.btn-primary {
  background: #1890ff;
  color: #fff;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-default {
  background: #fff;
  color: rgba(0, 0, 0, 0.65);
  border: 1px solid #d9d9d9;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}

.btn-link {
  background: none;
  color: #1890ff;
  border: none;
  cursor: pointer;
  padding: 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 24px;
  border-radius: 4px;
  width: 600px;
  max-height: 80vh;
  overflow: auto;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.85);
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
  margin-top: 24px;
}
</style>