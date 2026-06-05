<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { useAuthStore } from '../store/auth'
import { useMagnetic } from '../composables/useMagnetic'
import { useGsapContext } from '../composables/useGsapContext'
import { scrambleTo } from '../composables/useScrambleText'
import MagneticButton from '../components/ui/MagneticButton.vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const titleRef = ref(null)
const { elRef: panelRef } = useMagnetic(0.12)

const { rootRef: pageRef } = useGsapContext(() => {
  const tl = gsap.timeline({ defaults: { ease: 'power3.out' } })
  tl.from('.login-mark', { autoAlpha: 0, letterSpacing: '0.4em', duration: 0.6 })
    .from('.login-panel', { autoAlpha: 0, y: 32, duration: 0.7 }, '-=0.3')
    .from('.login-field', { autoAlpha: 0, x: -16, stagger: 0.1, duration: 0.4 }, '-=0.3')
})

onMounted(() => {
  if (titleRef.value) {
    scrambleTo(titleRef.value, '登录测试平台', 0.9)
  }
})

async function handleSubmit() {
  if (!form.value.username || !form.value.password) return
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    const redirect = route.query.redirect || '/projects'
    router.push(redirect)
  } catch {
    gsap.fromTo('.login-error', { x: -8 }, { x: 0, duration: 0.3, ease: 'elastic.out(1, 0.6)' })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div ref="pageRef" class="login-page">
    <div ref="panelRef" class="login-panel">
      <div class="login-header">
        <span class="login-mark">AITS / CONTROL ROOM</span>
        <h1 ref="titleRef">登录测试平台</h1>
        <p>HTTP Basic Auth · Django 用户凭证</p>
      </div>

      <form @submit.prevent="handleSubmit">
        <div class="login-field">
          <label for="username">OPERATOR</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            placeholder="alice"
            autocomplete="username"
          />
        </div>
        <div class="login-field">
          <label for="password">PASSKEY</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            @keyup.enter="handleSubmit"
          />
        </div>

        <div v-if="authStore.loginError" class="login-error">
          {{ authStore.loginError }}
        </div>

        <MagneticButton class="login-submit" :loading="loading" @click="handleSubmit">
          接入控制台
        </MagneticButton>
      </form>
    </div>

    <p class="login-hint">先在 Django Admin 或 shell 中创建用户</p>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--aits-space-5);
}

.login-panel {
  width: 100%;
  max-width: 420px;
  padding: var(--aits-space-7) var(--aits-space-6);
  background: var(--aits-surface);
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius-lg);
  box-shadow: var(--aits-shadow);
  will-change: transform;
}

.login-header {
  margin-bottom: var(--aits-space-6);
}

.login-mark {
  display: block;
  font-family: var(--aits-mono);
  font-size: 10px;
  color: var(--aits-accent);
  letter-spacing: 0.14em;
}

h1 {
  margin: var(--aits-space-3) 0 var(--aits-space-2);
  font-family: var(--aits-display);
  font-size: 26px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.login-header p {
  margin: 0;
  font-size: 13px;
  color: var(--aits-text-muted);
}

.login-field {
  margin-bottom: var(--aits-space-4);
}

.login-field label {
  display: block;
  margin-bottom: var(--aits-space-2);
  font-family: var(--aits-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  color: var(--aits-text-muted);
}

.login-field input {
  width: 100%;
  height: 44px;
  padding: 0 var(--aits-space-4);
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius);
  background: var(--aits-surface-raised);
  color: var(--aits-text);
  font-family: var(--aits-mono);
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.login-field input:focus {
  border-color: var(--aits-accent);
  box-shadow: 0 0 0 3px var(--aits-accent-dim);
}

.login-error {
  margin-bottom: var(--aits-space-4);
  padding: var(--aits-space-3);
  border: 1px solid rgba(255, 107, 107, 0.35);
  border-radius: var(--aits-radius);
  background: rgba(255, 107, 107, 0.08);
  color: var(--aits-danger);
  font-size: 13px;
}

.login-submit {
  width: 100%;
  margin-top: var(--aits-space-2);
}

.login-hint {
  margin-top: var(--aits-space-5);
  font-family: var(--aits-mono);
  font-size: 11px;
  color: var(--aits-text-muted);
}
</style>
