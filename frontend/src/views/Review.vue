<template>
  <div class="page">
    <van-nav-bar title="复习资料" left-arrow @click-left="$router.back()" />
    
    <van-cell-group inset style="margin: 16px">
      <van-field v-model="form.subject" is-link readonly label="学科" placeholder="选择学科" @click="showSubject = true" />
      <van-field v-model="form.semester" is-link readonly label="学期" placeholder="选择学期" @click="showSemester = true" />
      <van-field v-model="form.unit" is-link readonly label="单元" placeholder="选择单元" @click="showUnit = true" />
    </van-cell-group>

    <div style="margin: 16px">
      <van-button round block type="primary" class="btn-primary" @click="getMaterials">获取复习资料（10积分）</van-button>
    </div>

    <van-action-sheet v-model:show="showSubject" :actions="subjects" @select="onSubjectSelect" />
    <van-action-sheet v-model:show="showSemester" :actions="semesters" @select="onSemesterSelect" />
    <van-action-sheet v-model:show="showUnit" :actions="units" @select="onUnitSelect" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { showSuccessToast } from 'vant'

const router = useRouter()
const form = reactive({ subject: '', semester: '', unit: '', subjectId: 0, semesterId: 0, unitId: 0 })
const showSubject = ref(false)
const showSemester = ref(false)
const showUnit = ref(false)
const subjects = ref<any[]>([])
const semesters = ref<any[]>([])
const units = ref<any[]>([])

onMounted(async () => {
  const res = await api.getSubjects()
  subjects.value = res.map((s: any) => ({ name: s.name, value: s.id }))
})

async function onSubjectSelect(action: any) {
  form.subject = action.name
  form.subjectId = action.value
  const res = await api.getSemesters(action.value)
  semesters.value = res.map((s: any) => ({ name: s.name, value: s.id }))
}

async function onSemesterSelect(action: any) {
  form.semester = action.name
  form.semesterId = action.value
  const res = await api.getUnits(form.subjectId, action.value)
  units.value = res.map((u: any) => ({ name: u.name, value: u.id }))
}

function onUnitSelect(action: any) {
  form.unit = action.name
  form.unitId = action.value
}

async function getMaterials() {
  await api.getReviewMaterials({
    subjectId: form.subjectId,
    semesterId: form.semesterId,
    unitId: form.unitId
  })
  showSuccessToast('订单已创建，请在订单列表下载')
  router.push('/orders')
}
</script>