<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">版本管理</h2>
      <button class="btn-primary" @click="showForm = true">添加版本</button>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>版本名称</th>
          <th>年级数</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ item.name }}</td>
          <td>{{ item.grades?.length || 0 }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑版本' : '添加版本' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>版本名称</label>
            <input v-model="form.name" required placeholder="如：人教版、苏教版" />
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
const showForm = ref(false)
const form = reactive({ id: 0, name: '' })

async function onLoad() {
  items.value = await api.admin.getVersions()
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveVersion(form)
  showForm.value = false
  Object.assign(form, { id: 0, name: '' })
  onLoad()
}

onMounted(onLoad)
</script>

<style scoped src="./table.css"></style>