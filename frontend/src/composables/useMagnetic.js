import { onMounted, onUnmounted, ref } from 'vue'
import { gsap } from 'gsap'
import { prefersReducedMotion } from './useReducedMotion'

/**
 * Magnetic hover spell — button follows cursor within radius.
 * @param {number} [strength=0.35]
 */
export function useMagnetic(strength = 0.35) {
  const elRef = ref(null)
  /** @type {((e: PointerEvent) => void) | null} */
  let moveHandler = null
  /** @type {((e: PointerEvent) => void) | null} */
  let leaveHandler = null

  onMounted(() => {
    const el = elRef.value
    if (!el || prefersReducedMotion()) return

    moveHandler = (event) => {
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2
      const dx = (event.clientX - cx) * strength
      const dy = (event.clientY - cy) * strength
      gsap.to(el, { x: dx, y: dy, duration: 0.35, ease: 'power2.out', overwrite: 'auto' })
    }

    leaveHandler = () => {
      gsap.to(el, { x: 0, y: 0, duration: 0.6, ease: 'elastic.out(1, 0.5)' })
    }

    el.addEventListener('pointermove', moveHandler)
    el.addEventListener('pointerleave', leaveHandler)
  })

  onUnmounted(() => {
    const el = elRef.value
    if (!el) return
    if (moveHandler) el.removeEventListener('pointermove', moveHandler)
    if (leaveHandler) el.removeEventListener('pointerleave', leaveHandler)
    gsap.set(el, { clearProps: 'transform' })
  })

  return { elRef }
}
