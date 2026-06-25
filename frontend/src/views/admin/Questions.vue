<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">题库管理</h2>
      <div style="display: flex; gap: 12px">
        <button class="btn-default" @click="triggerImport">
          <input ref="fileInput" type="file" accept=".xlsx,.xls" @change="handleImport" style="display: none" />
          导入题库
        </button>
        <button class="btn-primary" @click="showForm = true">添加题目</button>
      </div>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>题目</th>
          <th>题型</th>
          <th>难度</th>
          <th>考点</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="q in questions" :key="q.id">
          <td>{{ q.id }}</td>
          <td>{{ q.content?.substring(0, 30) }}...</td>
          <td>{{ q.question_type }}</td>
          <td>{{ q.difficulty }}</td>
          <td>{{ q.exam_point_title || '-' }}</td>
          <td>
            <button class="btn-link" @click="editItem(q)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <!-- 分页控件 -->
    <div v-if="total > 0" class="pagination">
      <div class="pagination-info">共 {{ total }} 条，第 {{ currentPage }}/{{ totalPages }} 页</div>
      <div class="pagination-controls">
        <button class="btn-default" :disabled="currentPage <= 1" @click="onPageChange(1)">首页</button>
        <button class="btn-default" :disabled="currentPage <= 1" @click="onPageChange(currentPage - 1)">上一页</button>
        <button class="btn-default" :disabled="currentPage >= totalPages" @click="onPageChange(currentPage + 1)">下一页</button>
        <button class="btn-default" :disabled="currentPage >= totalPages" @click="onPageChange(totalPages)">末页</button>
      </div>
    </div>
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
import axios from 'axios'

const questions = ref<any[]>([])
const showForm = ref(false)
const form = reactive({ id: 0, unit_id: 1, question: '', answer: '', question_type: 'choice', difficulty: 'medium', exam_type: 'unit' })
const fileInput = ref<HTMLInputElement | null>(null)
const importing = ref(false)

// 分页状态
const currentPage = ref(1)
const pageSize = ref(50)
const total = ref(0)
const totalPages = ref(0)

async function onLoad() {
  const res: any = await api.admin.getQuestions(currentPage.value, pageSize.value)
  questions.value = res.items || []
  total.value = res.total || 0
  totalPages.value = res.total_pages || 0
}

function onPageChange(page: number) {
  currentPage.value = page
  onLoad()
  window.scrollTo({ top: 0, behavior: 'smooth' })
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

function triggerImport() {
  fileInput.value?.click()
}

async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  importing.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)

    const adminToken = localStorage.getItem('admin_token')
    const response = await axios.post('/api/admin/import-questions', formData, {
      headers: {
        'Authorization': `Bearer ${adminToken}`,
        'Content-Type': 'multipart/form-data'
      },
      timeout: 120000 // 120秒超时，导入大文件需要更长时间
    })

    const result = response.data

    if (result) {
      let msg = `导入完成！\n成功: ${result.imported}\n跳过: ${result.skipped}`
      if (result.skip_reasons) {
        msg += '\n\n跳过原因统计:'
        for (const [reason, count] of Object.entries(result.skip_reasons)) {
          if (count && (count as number) > 0) {
            msg += `\n  ${reason}: ${count}`
          }
        }
      }
      if (result.skip_details && result.skip_details.length > 0) {
        msg += `\n\n部分跳过详情(前${result.skip_details.length}条):\n`
        msg += result.skip_details.slice(0, 10).join('\n')
      }
      alert(msg)
      onLoad()
    }
  } catch (error: any) {
    if (error.code === 'ECONNABORTED') {
      alert('导入超时，请尝试分批导入或联系管理员')
    } else {
      alert('导入失败: ' + (error.response?.data?.detail || error.message))
    }
  } finally {
    importing.value = false
    if (target) target.value = ''
  }
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

.btn-default:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 16px;
  background: #fff;
  border-radius: 4px;
}

.pagination-info {
  color: rgba(0, 0, 0, 0.65);
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 8px;
}

.pagination-controls button {
  padding: 8px 12px;
  min-width: 60px;
}

.pagination-controls button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>