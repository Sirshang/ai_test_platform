import { gsap } from 'gsap'

/** @returns {boolean} */
export function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

/**
 * Run GSAP animation or skip when user prefers reduced motion.
 * @param {() => void} animateFn
 * @param {() => void} [fallbackFn]
 */
export function runMotion(animateFn, fallbackFn) {
  if (prefersReducedMotion()) {
    fallbackFn?.()
    return
  }
  animateFn()
}

/**
 * @param {import('gsap').TweenVars} vars
 * @returns {import('gsap').TweenVars}
 */
export function motionVars(vars) {
  if (prefersReducedMotion()) {
    return { ...vars, duration: 0, delay: 0, stagger: 0 }
  }
  return vars
}

/** Register gsap.matchMedia once at app level. */
export function initMotionMedia() {
  gsap.matchMedia().add('(prefers-reduced-motion: reduce)', () => {
    gsap.globalTimeline.timeScale(1000)
  })
}
