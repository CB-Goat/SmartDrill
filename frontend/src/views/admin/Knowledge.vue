<template>
  <div>
    <van-nav-bar title="知识点管理" left-arrow @click-left="$router.back()" />
    <van-button round block type="primary" class="btn-primary" style="margin: 16px" @click="showForm = true">添加知识点</van-button>
    <van-list v-model:loading="loading" :finished="finished" @load="onLoad">
      <van-cell-group v-for="item in knowledge" :key="item.id" inset style="margin: 8px 16px">
        <van-cell :title="item.title" :label="item.subject" />
      </van-cell-group>
    </van-list>
    <van-popup v-model:show="showForm" position="bottom" style="height: 60%">
      <van-form @submit="onSubmit">
        <van-field v-model="form.title" label="标题" />
        <van-field v-model="form.content" label="内容" type="textarea" rows="5" />
        <van-button round block type="primary" native-type="submit" class="btn-primary">保存</van-button>
      </van-form>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { api } from '@/api'

const knowledge = ref<any[]>([])
const loading = ref(false)
const finished = ref(false)
const showForm = ref(false)
const form = reactive({ title: '', content: '', subject: '' })

async function onLoad() {
  const res = await api.admin.getKnowledge()
  knowledge.value = res
  loading.value = false
  finished.value = true
}

async function onSubmit() {
  await api.admin.saveKnowledge(form)
  showForm.value = false
  onLoad()
}

onMounted(onLoad)
</script>