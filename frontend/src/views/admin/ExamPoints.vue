<template>
  <div>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px">
      <h2 style="margin: 0">考点管理</h2>
      <button class="btn-primary" @click="showForm = true">添加考点</button>
    </div>
    <div class="filter-bar">
      <select v-model="filterKnowledgePointId" @change="onLoad">
        <option :value="null">全部知识点</option>
        <option v-for="k in knowledgePoints" :key="k.id" :value="k.id">{{ k.title }}</option>
      </select>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th>
          <th>知识点</th>
          <th>考点标题</th>
          <th>考试题型</th>
          <th>考试频率</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td>{{ getKnowledgePointTitle(item.knowledge_point_id) }}</td>
          <td>{{ item.title }}</td>
          <td>{{ item.exam_types }}</td>
          <td>{{ item.exam_frequency }}</td>
          <td>
            <button class="btn-link" @click="editItem(item)">编辑</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="showForm" class="modal-overlay" @click="showForm = false">
      <div class="modal-content" @click.stop>
        <h3>{{ form.id ? '编辑考点' : '添加考点' }}</h3>
        <form @submit.prevent="onSubmit">
          <div class="form-item">
            <label>知识点</label>
            <select v-model="form.knowledge_point_id" required>
              <option v-for="k in knowledgePoints" :key="k.id" :value="k.id">{{ k.title }}</option>
            </select>
          </div>
          <div class="form-item">
            <label>考点标题</label>
            <input v-model="form.title" required />
          </div>
          <div class="form-item">
            <label>考点内容</label>
            <textarea v-model="form.content" rows="3"></textarea>
          </div>
          <div class="form-item">
            <label>考试题型</label>
            <input v-model="form.exam_types" placeholder="如：单选题,判断题" />
          </div>
          <div class="form-item">
            <label>考试频率</label>
            <select v-model="form.exam_frequency">
              <option value="少考">少考</option>
              <option value="常考">常考</option>
              <option value="必考">必考</option>
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

const items = ref<any[]>([])
const knowledgePoints = ref<any[]>([])
const showForm = ref(false)
const filterKnowledgePointId = ref<number | null>(null)
const form = reactive({ id: 0, knowledge_point_id: 1, title: '', content: '', exam_types: '', exam_frequency: '常考' })

async function onLoad() {
  knowledgePoints.value = await api.admin.getKnowledge()
  items.value = await api.admin.getExamPoints(filterKnowledgePointId.value || undefined)
}

function getKnowledgePointTitle(knowledgePointId: number) {
  const k = knowledgePoints.value.find(x => x.id === knowledgePointId)
  return k?.title || ''
}

function editItem(item: any) {
  Object.assign(form, item)
  showForm.value = true
}

async function onSubmit() {
  await api.admin.saveExamPoint(form)
  showForm.value = false
  Object.assign(form, { id: 0, knowledge_point_id: 1, title: '', content: '', exam_types: '', exam_frequency: '常考' })
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