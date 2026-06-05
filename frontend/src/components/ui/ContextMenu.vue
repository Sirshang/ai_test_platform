<script setup>
import { ref, watch } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from '../../composables/useReducedMotion'

const props = defineProps({
  visible: { type: Boolean, default: false },
  x: { type: Number, default: 0 },
  y: { type: Number, default: 0 },
})

const menuRef = ref(null)

watch(
  () => props.visible,
  (show) => {
    if (!show || !menuRef.value || prefersReducedMotion()) return
    gsap.fromTo(
      menuRef.value,
      { autoAlpha: 0, scale: 0.92, y: -6 },
      { autoAlpha: 1, scale: 1, y: 0, duration: 0.22, ease: 'back.out(1.6)' },
    )
  },
)
</script>

<template>
  <Teleport to="body">
    <div
      v-if="visible"
      ref="menuRef"
      class="ctx-menu"
      :style="{ left: `${x}px`, top: `${y}px` }"
      @click.stop
    >
      <slot />
    </div>
  </Teleport>
</template>

<style scoped>
.ctx-menu {
  position: fixed;
  z-index: 9999;
  min-width: 156px;
  padding: 6px;
  background: var(--aits-surface-raised);
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius);
  box-shadow: var(--aits-shadow), 0 0 0 1px rgba(77, 255, 145, 0.08);
  transform-origin: top left;
}

:slotted(button) {
  display: block;
  width: 100%;
  padding: 9px 12px;
  border: none;
  background: none;
  color: var(--aits-text);
  font-family: var(--aits-sans);
  font-size: 13px;
  text-align: left;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s, color 0.15s;
}

:slotted(button:hover) {
  background: var(--aits-accent-dim);
  color: var(--aits-accent);
}
</style>
