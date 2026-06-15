<template>
  <div class="page">
    <van-nav-bar title="练习题" left-arrow @click-left="$router.back()" />
    
    <van-cell-group inset style="margin: 16px">
      <van-field v-model="form.subject" is-link readonly label="学科" placeholder="选择学科" @click="showSubject = true" />
      <van-field v-model="form.semester" is-link readonly label="学期" placeholder="选择学期" @click="showSemester = true" />
      <van-field v-model="form.unit" is-link readonly label="单元" placeholder="选择单元" @click="showUnit = true" />
      <van-field v-model="form.examType" is-link readonly label="考试类型" placeholder="选择类型" @click="showExamType = true" />
      <van-field v-model="form.difficulty" is-link readonly label="难度" placeholder="选择难度" @click="showDifficulty = true" />
      <van-field v-model="form.questionCount" type="number" label="题数" placeholder="输入题数" />
    </van-cell-group>

    <div style="margin: 16px">
      <van-button round block type="primary" class="btn-primary" @click="getQuestions">获取练习题（{{ form.questionCount || 0 }}积分）</van-button>
    </div>

    <van-action-sheet v-model:show="showSubject" :actions="subjects" @select="onSubjectSelect" />
    <van-action-sheet v-model:show="showSemester" :actions="semesters" @select="onSemesterSelect" />
    <van-action-sheet v-model:show="showUnit" :actions="units" @select="onUnitSelect" />
    <van-action-sheet v-model:show="showExamType" :actions="examTypes" @select="onExamTypeSelect" />
    <van-action-sheet v-model:show="showDifficulty" :actions="difficulties" @select="onDifficultySelect" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/api'
import { showSuccessToast } from 'vant'

const router = useRouter()
const form = reactive({
  subject: '', semester: '', unit: '', examType: '', difficulty: '',
  subjectId: 0, semesterId: 0, unitId: 0, questionCount: 10
})
const showSubject = ref(false)
const showSemester = ref(false)
const showUnit = ref(false)
const showExamType = ref(false)
const showDifficulty = ref(false)
const subjects = ref<any[]>([])
const semesters = ref<any[]>([])
const units = ref<any[]>([])
const examTypes = ref([{ name: '单元测试', value: 'unit' }, { name: '期中考试', value: 'midterm' }, { name: '期末考试', value: 'final' }])
const difficulties = ref([{ name: '简单', value: 'easy' }, { name: '中等', value: 'medium' }, { name: '困难', value: 'hard' }])

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

function onUnitSelect(action: any) { form.unit = action.name; form.unitId = action.value }
function onExamTypeSelect(action: any) { form.examType = action.name }
function onDifficultySelect(action: any) { form.difficulty = action.name }

async function getQuestions() {
  await api.getPracticeQuestions({
    subjectId: form.subjectId,
    semesterId: form.semesterId,
    unitId: form.unitId,
    examType: form.examType,
    difficulty: form.difficulty,
    questionCount: form.questionCount
  })
  showSuccessToast('订单已创建，请在订单列表下载')
  router.push('/orders')
}
</script>