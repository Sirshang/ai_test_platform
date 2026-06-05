<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from '../../composables/useReducedMotion'

const props = defineProps({
  active: { type: Boolean, default: false },
  variant: { type: String, default: 'ready' },
})

const pulseRef = ref(null)
/** @type {gsap.core.Tween | null} */
let pulseTween = null

function startPulse() {
  pulseTween?.kill()
  if (!props.active || !pulseRef.value || prefersReducedMotion()) return
  pulseTween = gsap.to(pulseRef.value, {
    scale: 2.2,
    autoAlpha: 0,
    duration: 1.4,
    repeat: -1,
    ease: 'sine.out',
  })
}

watch(() => props.active, startPulse)

onMounted(startPulse)

onUnmounted(() => {
  pulseTween?.kill()
})
</script>

<template>
  <span class="status-pulse-wrap" :class="variant">
    <span ref="pulseRef" class="status-pulse" aria-hidden="true" />
    <span class="status-core" />
  </span>
</template>

<style scoped>
.status-pulse-wrap {
  position: relative;
  display: inline-flex;
  width: 10px;
  height: 10px;
  align-items: center;
  justify-content: center;
}

.status-core {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--pulse-color, var(--aits-text-muted));
}

.status-pulse {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: var(--pulse-color, var(--aits-text-muted));
  transform: scale(1);
  opacity: 0.55;
}

.status-pulse-wrap.ready {
  --pulse-color: var(--aits-accent);
}

.status-pulse-wrap.draft {
  --pulse-color: var(--aits-warn);
}

.status-pulse-wrap.empty {
  --pulse-color: var(--aits-border);
}
</style>
