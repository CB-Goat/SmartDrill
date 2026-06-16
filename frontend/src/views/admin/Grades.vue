<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">年级管理</h2>
      <button class="btn-primary" @click="showForm = true">添加年级</button>
    </div>
    <div class="filter-bar">
      <select v-model="filterVersionId" @change="onLoad">
        <option :value="null">全部版本</option>
        <option v-for="v in versions" :key="v.id" :value="v.id">{{ v.name }}</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>版本</th>
          <th>年级名称</th>
          <th>科目数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getVersionName(item.version_id) }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.subjects?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
            <button class="btn-link" style="color: #f56c6c; margin-left: 8px" @click="deleteItem(item)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑年级' : '添加年级' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>版本</label>
            <select v-model="form.version_id" required>
              <option v-for="v in versions" :key="v.id" :value="v.id">{{ v.name }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>年级名称</label>
            <input v-model="form.name" required placeholder="如：三年级、七年级" />
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
const versions = ref<any[]>([])
const showForm = ref(false)
const filterVersionId = ref<number | null>(null)
const form = reactive({ id: 0, version_id: 1, name: '' })

async function onLoad() {
  versions.value = await api.admin.getVersions()
  items.value = await api.admin.getGrades(filterVersionId.value || undefined)
}

function getVersionName(versionId: number) {
  const v = versions.value.find(x => x.id === versionId)
  return v?.name || ''
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveGrade(form)
  showForm.value = false
  Object.assign(form, { id: 0, version_id: 1, name: '' })
  onLoad()
}

async function deleteItem(item: any) {
  if (!confirm(`确定删除年级"${item.name}"吗？`)) return
  await api.admin.deleteGrade(item.id)
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