<template>
  <div>
    <van-nav-bar title="题库管理" left-arrow @click-left="$router.back()" />
    <van-button round block type="primary" class="btn-primary" style="margin: 16px" @click="showForm = true">添加题目</van-button>
    <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
      <van-cell-group v-for="q in questions" :key="q.id" inset style="margin: 8px 16px">
        <van-cell :title="q.question" :label="q.subject" />
      </van-cell-group>
    </van-list>
    <van-popup v-model:show="showForm" position="bottom" style="height: 70%">
      <van-form @submit="onSubmit">
        <van-field v-model="form.question" label="题目" type="textarea" rows="3" />
        <van-field v-model="form.answer" label="答案" type="textarea" rows="3" />
        <van-field v-model="form.difficulty" label="难度" />
        <van-button round block type="primary" native-type="submit" class="btn-primary">保存</van-button>
      </van-form>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/api'

const questions = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)
const showForm = ref(false)
const form = reactive({ question: '', answer: '', difficulty: 'medium', subject: '' })

async function onLoad() {
  const res = await api.admin.getQuestions()
  questions.value = res
  loading.value = false
  finished.value = true
}

async function onSubmit() {
  await api.admin.saveQuestion(form)
  showForm.value = false
  onLoad()
}

onMounted(onLoad)
</script>