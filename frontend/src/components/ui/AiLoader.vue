<script setup>
defineProps({
  active: { type: Boolean, default: false },
})
</script>

<template>
  <div class="ai-loader" :class="{ active }">
    <div class="ai-loader-scan" aria-hidden="true" />
    <slot />
  </div>
</template>

<style scoped>
.ai-loader {
  position: relative;
  border-radius: var(--aits-radius);
  overflow: hidden;
}

.ai-loader-scan {
  position: absolute;
  inset: 0;
  pointer-events: none;
  opacity: 0;
  background: linear-gradient(
    90deg,
    transparent 0%,
    rgba(77, 255, 145, 0.08) 45%,
    rgba(77, 255, 145, 0.18) 50%,
    rgba(77, 255, 145, 0.08) 55%,
    transparent 100%
  );
  transform: translateX(-100%);
}

.ai-loader.active .ai-loader-scan {
  opacity: 1;
  animation: ai-scan 1.4s ease-in-out infinite;
}

@keyframes ai-scan {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

@media (prefers-reduced-motion: reduce) {
  .ai-loader.active .ai-loader-scan {
    animation: none;
    opacity: 0.12;
    transform: none;
  }
}
</style>
