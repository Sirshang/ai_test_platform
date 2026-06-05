import { onMounted, onUnmounted, ref } from 'vue'
import { gsap } from 'gsap'

/**
 * Scoped GSAP context with automatic cleanup (gsap-frameworks pattern).
 * @param {(ctx: gsap.Context) => void} setupFn
 * @returns {{ rootRef: import('vue').Ref<HTMLElement | null>, replay: () => void }}
 */
export function useGsapContext(setupFn) {
  const rootRef = ref(null)
  /** @type {gsap.Context | null} */
  let ctx = null

  function mountContext() {
    ctx?.revert()
    if (!rootRef.value) return
    ctx = gsap.context(() => setupFn(ctx), rootRef.value)
  }

  onMounted(() => {
    mountContext()
  })

  onUnmounted(() => {
    ctx?.revert()
    ctx = null
  })

  return {
    rootRef,
    replay: mountContext,
  }
}

/**
 * Page entrance timeline — header then content stagger.
 * @param {HTMLElement} scope
 */
export function pageEnterTimeline(scope) {
  if (!scope) return gsap.timeline()
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  const eyebrow = scope.querySelector('.page-eyebrow')
  const title = scope.querySelector('.page-title')
  const subtitle = scope.querySelector('.page-subtitle')
  const bodyItems = scope.querySelectorAll('.page-body > *')

  if (eyebrow) tl.from(eyebrow, { autoAlpha: 0, y: 12, duration: 0.4 })
  if (title) tl.from(title, { autoAlpha: 0, y: 20, duration: 0.55 }, '-=0.15')
  if (subtitle) tl.from(subtitle, { autoAlpha: 0, y: 14, duration: 0.4 }, '-=0.25')
  if (bodyItems.length) {
    tl.from(bodyItems, { autoAlpha: 0, y: 18, duration: 0.45, stagger: 0.07 }, '-=0.1')
  }
  return tl
}
