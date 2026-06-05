import { gsap } from 'gsap'
import { prefersReducedMotion } from './useReducedMotion'

const CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_'

/**
 * Scramble-decode text reveal (design-spells).
 * @param {HTMLElement} el
 * @param {string} finalText
 * @param {number} [duration=0.8]
 */
export function scrambleTo(el, finalText, duration = 0.8) {
  if (!el) return
  if (prefersReducedMotion()) {
    el.textContent = finalText
    return
  }

  const proxy = { progress: 0 }
  gsap.to(proxy, {
    progress: 1,
    duration,
    ease: 'power2.out',
    onUpdate: () => {
      const p = proxy.progress
      const revealed = Math.floor(p * finalText.length)
      let out = finalText.slice(0, revealed)
      for (let i = revealed; i < finalText.length; i += 1) {
        out += CHARS[Math.floor(Math.random() * CHARS.length)]
      }
      el.textContent = out
    },
    onComplete: () => {
      el.textContent = finalText
    },
  })
}
