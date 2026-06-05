<script setup>
import { onMounted, ref } from 'vue'
import MonacoEditor from './components/MonacoEditor.vue'
import { useAppStore } from './store/app'

const appStore = useAppStore()
const scriptContent = ref(`def test_example():\n    assert True\n`)

onMounted(() => {
  appStore.loadTestApi()
})
</script>

<template>
  <main class="page">
    <header class="hero">
      <p class="eyebrow">AITS MVP</p>
      <h1>AI 自动化测试平台</h1>
      <p class="subtitle">Vue3 + Element Plus + Monaco Editor 前端骨架已就绪</p>
    </header>

    <el-card class="panel" shadow="never">
      <template #header>
        <div class="panel-header">
          <span>API 连通性</span>
          <el-button type="primary" :loading="appStore.apiStatus === 'loading'" @click="appStore.loadTestApi()">
            重新检测 /api/test
          </el-button>
        </div>
      </template>

      <el-alert
        v-if="appStore.apiStatus === 'ok'"
        type="success"
        :title="appStore.apiMessage"
        show-icon
        :closable="false"
      />
      <el-alert
        v-else-if="appStore.apiStatus === 'error'"
        type="error"
        :title="appStore.apiError"
        show-icon
        :closable="false"
      />
      <el-skeleton v-else :rows="2" animated />
    </el-card>

    <el-card class="panel" shadow="never">
      <template #header>Monaco Editor 预览</template>
      <MonacoEditor v-model="scriptContent" language="python" height="280px" />
    </el-card>
  </main>
</template>

<style scoped>
.page {
  max-width: 960px;
  margin: 0 auto;
  padding: 48px 24px 64px;
}

.hero {
  margin-bottom: 32px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #409eff;
  font-size: 13px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 0 0 12px;
  font-size: 32px;
  color: #1f2937;
}

.subtitle {
  margin: 0;
  color: #6b7280;
}

.panel {
  margin-bottom: 24px;
}

.panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
</style>
