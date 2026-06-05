<script setup>
import { useMagnetic } from '../../composables/useMagnetic'

defineProps({
  loading: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['click'])
const { elRef } = useMagnetic(0.28)

function handleClick(event) {
  emit('click', event)
}
</script>

<template>
  <button
    ref="elRef"
    type="button"
    class="magnetic-btn"
    :class="{ 'is-loading': loading }"
    :disabled="disabled || loading"
    @click="handleClick"
  >
    <span class="magnetic-btn-glow" aria-hidden="true" />
    <span class="magnetic-btn-inner">
      <span v-if="loading" class="magnetic-btn-spinner" aria-hidden="true" />
      <slot />
    </span>
  </button>
</template>

<style scoped>
.magnetic-btn {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0 22px;
  height: 42px;
  border: 1px solid var(--aits-accent);
  border-radius: var(--aits-radius);
  background: var(--aits-accent);
  color: var(--aits-bg-deep);
  font-family: var(--aits-display);
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.04em;
  cursor: pointer;
  overflow: hidden;
  transition: box-shadow 0.25s;
  will-change: transform;
}

.magnetic-btn:hover:not(:disabled) {
  box-shadow:
    0 0 0 1px var(--aits-accent),
    0 0 24px var(--aits-accent-glow),
    0 8px 32px rgba(0, 0, 0, 0.4);
}

.magnetic-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.magnetic-btn-glow {
  position: absolute;
  inset: -50%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.25) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s;
}

.magnetic-btn:hover .magnetic-btn-glow {
  opacity: 1;
}

.magnetic-btn-inner {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.magnetic-btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(8, 11, 15, 0.25);
  border-top-color: var(--aits-bg-deep);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
