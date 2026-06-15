<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">学期管理</h2>
      <button class="btn-primary" @click="showForm = true">添加学期</button>
    </div>
    <div class="filter-bar">
      <select v-model="filterSubjectId" @change="onLoad">
        <option :value="null">全部科目</option>
        <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>科目</th>
          <th>学期名称</th>
          <th>单元数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getSubjectName(item.subject_id) }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.units?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑学期' : '添加学期' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>科目</label>
            <select v-model="form.subject_id" required>
              <option v-for="s in subjects" :key="s.id" :value="s.id">{{ s.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>学期名称</label>
            <input v-model="form.name" required placeholder="如：上册、下册" />
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

const items = ref<any[]>([])
const subjects = ref<any[]>([])
const showForm = ref(false)
const filterSubjectId = ref<number | null>(null)
const form = reactive({ id: 0, subject_id: 1, name: '' })

async function onLoad() {
  subjects.value = await api.admin.getSubjects()
  items.value = await api.admin.getSemesters(filterSubjectId.value || undefined)
}

function getSubjectName(subjectId: number) {
  const s = subjects.value.find(x => x.id === subjectId)
  return s?.name || ''
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveSemester(form)
  showForm.value = false
  Object.assign(form, { id: 0, subject_id: 1, name: '' })
  onLoad()
}

onMounted(onLoad)
</script>

<style scoped src="./table.css"></style>
<style scoped>
.filter-bar {
  margin-bottom: 16px;
}
.filter-bar select {
  padding: 8px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  min-width: 200px;
}
</style>