<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">题库管理</h2>
      <button class="btn-primary" @click="showForm = true">添加题目</button>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>题目</th>
          <th>题型</th>
          <th>难度</th>
          <th>考试类型</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in questions" :key="q.id">
          <td>{{ q.id }}</td>
          <td>{{ q.question?.substring(0, 30) }}...</td>
          <td>{{ q.question_type }}</td>
          <td>{{ q.difficulty }}</td>
          <td>{{ q.exam_type }}</td>
          <td>
            <button class="btn-link" @click="editItem(q)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑题目' : '添加题目' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>单元ID</label>
            <input v-model="form.unit_id" type="number" required />
          </div>
          <div class="form-item">
            <label>题目</label>
            <textarea v-model="form.question" rows="3" required></textarea>
          </div>
          <div class="form-item">
            <label>答案</label>
            <textarea v-model="form.answer" rows="3" required></textarea>
          </div>
          <div class="form-item">
            <label>题型</label>
            <select v-model="form.question_type">
              <option value="choice">选择题</option>
              <option value="fill">填空题</option>
              <option value="answer">简答题</option>
            </select>
          </div>
          <div class="form-item">
            <label>难度</label>
            <select v-model="form.difficulty">
              <option value="easy">简单</option>
              <option value="medium">中等</option>
              <option value="hard">困难</option>
            </select>
          </div>
          <div class="form-item">
            <label>考试类型</label>
            <select v-model="form.exam_type">
              <option value="unit">单元测试</option>
              <option value="midterm">期中考试</option>
              <option value="final">期末考试</option>
            </select>
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

const questions = ref<any[]>([])
const showForm = ref(false)
const form = reactive({ id: 0, unit_id: 1, question: '', answer: '', question_type: 'choice', difficulty: 'medium', exam_type: 'unit' })

async function onLoad() {
  const res = await api.admin.getQuestions()
  questions.value = res
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveQuestion(form)
  showForm.value = false
  Object.assign(form, { id: 0, unit_id: 1, question: '', answer: '', question_type: 'choice', difficulty: 'medium', exam_type: 'unit' })
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
.form-item textarea,
.form-item select {
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