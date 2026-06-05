import { onMounted, onUnmounted, ref } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from './useReducedMotion'

/**
 * Cursor-following spotlight on card surfaces (design-spells).
 */
export function useSpotlight() {
  const containerRef = ref(null)

  /** @param {PointerEvent} event */
  function handleMove(event) {
    const container = containerRef.value
    if (!container || prefersReducedMotion()) return
    const cards = container.querySelectorAll('.spotlight-card')
    cards.forEach((card) => {
      const rect = card.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      gsap.to(card, {
        '--spot-x': `${x}px`,
        '--spot-y': `${y}px`,
        duration: 0.4,
        ease: 'power2.out',
        overwrite: 'auto',
      })
    })
  }

  onMounted(() => {
    containerRef.value?.addEventListener('pointermove', handleMove)
  })

  onUnmounted(() => {
    containerRef.value?.removeEventListener('pointermove', handleMove)
  })

  return { containerRef }
}
