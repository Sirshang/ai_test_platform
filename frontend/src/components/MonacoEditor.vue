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
  monaco.editor.defineTheme('aits-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: 'comment', foreground: '6b7d96', fontStyle: 'italic' },
      { token: 'string', foreground: '4dff91' },
      { token: 'keyword', foreground: 'ff9f1c' },
      { token: 'number', foreground: '7ec8ff' },
    ],
    colors: {
      'editor.background': '#0e1218',
      'editor.foreground': '#e8eef6',
      'editor.lineHighlightBackground': '#141a24',
      'editorCursor.foreground': '#4dff91',
      'editor.selectionBackground': '#4dff9125',
      'editorLineNumber.foreground': '#3a4a60',
      'editorLineNumber.activeForeground': '#4dff91',
    },
  })

  editor = monaco.editor.create(containerRef.value, {
    value: props.modelValue,
    language: props.language,
    theme: 'aits-dark',
    automaticLayout: true,
    minimap: { enabled: false },
    fontSize: 13,
    fontFamily: "'JetBrains Mono', monospace",
    lineHeight: 20,
    padding: { top: 12 },
    scrollBeyondLastLine: false,
    renderLineHighlight: 'line',
    cursorBlinking: 'phase',
    smoothScrolling: true,
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
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius);
  overflow: hidden;
}
</style>
