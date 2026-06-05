<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'

const props = defineProps({
  modelValue: {
    type: String,
    default: '',
  },
  language: {
    type: String,
    default: 'python',
  },
  height: {
    type: String,
    default: '240px',
  },
})

const emit = defineEmits(['update:modelValue'])

self.MonacoEnvironment = {
  getWorker() {
    return new editorWorker()
  },
}

const containerRef = ref(null)
let editor = null

onMounted(() => {
  editor = monaco.editor.create(containerRef.value, {
    value: props.modelValue,
    language: props.language,
    theme: 'vs-dark',
    automaticLayout: true,
    minimap: { enabled: false },
    fontSize: 14,
    scrollBeyondLastLine: false,
  })

  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue())
  })
})

watch(
  () => props.modelValue,
  (value) => {
    if (editor && value !== editor.getValue()) {
      editor.setValue(value)
    }
  },
)

onBeforeUnmount(() => {
  editor?.dispose()
})
</script>

<template>
  <div ref="containerRef" class="monaco-editor" :style="{ height }" />
</template>

<style scoped>
.monaco-editor {
  width: 100%;
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  overflow: hidden;
}
</style>
