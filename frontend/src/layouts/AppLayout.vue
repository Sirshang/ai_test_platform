<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { useAuthStore } from '../store/auth'
import { useGsapContext } from '../composables/useGsapContext'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const projectId = computed(() => route.params.id)
const isProjectScope = computed(() => Boolean(projectId.value))
const navIndicator = ref(null)

const { rootRef: shellRef } = useGsapContext(() => {
  gsap.from('.topbar', { autoAlpha: 0, y: -12, duration: 0.5, ease: 'power3.out' })
})

function moveNavIndicator(activeLink) {
  if (!navIndicator.value || !activeLink) return
  gsap.to(navIndicator.value, {
    x: activeLink.offsetLeft,
    width: activeLink.offsetWidth,
    duration: 0.35,
    ease: 'power3.out',
  })
}

function syncNavIndicator() {
  requestAnimationFrame(() => {
    const active = shellRef.value?.querySelector('.nav-link.active')
    moveNavIndicator(active)
  })
}

watch(() => route.path, syncNavIndicator)

onMounted(syncNavIndicator)

function handleLogout() {
  authStore.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div ref="shellRef" class="app-shell">
    <header class="topbar">
      <router-link to="/projects" class="brand">
        <span class="brand-mark">AITS</span>
        <span class="brand-divider" aria-hidden="true" />
        <span class="brand-sub">TEST CONTROL</span>
      </router-link>

      <nav v-if="isProjectScope" class="project-nav">
        <div ref="navIndicator" class="nav-indicator" aria-hidden="true" />
        <router-link
          :to="`/projects/${projectId}`"
          class="nav-link"
          active-class="active"
          @click="syncNavIndicator"
        >
          概览
        </router-link>
        <router-link
          :to="`/projects/${projectId}/api-cases`"
          class="nav-link"
          active-class="active"
          @click="syncNavIndicator"
        >
          API 用例
        </router-link>
      </nav>

      <div class="topbar-actions">
        <span class="user-badge">
          <span class="user-dot" aria-hidden="true" />
          {{ authStore.displayName }}
        </span>
        <button type="button" class="logout-btn" @click="handleLogout">退出</button>
      </div>
    </header>

    <main class="main-content">
      <router-view v-slot="{ Component }">
        <Transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </Transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.topbar {
  display: flex;
  align-items: center;
  gap: var(--aits-space-6);
  padding: 0 var(--aits-space-6);
  height: 52px;
  border-bottom: 1px solid var(--aits-border-subtle);
  background: rgba(8, 11, 15, 0.88);
  backdrop-filter: blur(16px);
  position: sticky;
  top: 0;
  z-index: 100;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--aits-space-3);
  text-decoration: none;
  flex-shrink: 0;
}

.brand-mark {
  font-family: var(--aits-display);
  font-weight: 800;
  font-size: 16px;
  color: var(--aits-accent);
  letter-spacing: 0.04em;
}

.brand-divider {
  width: 1px;
  height: 14px;
  background: var(--aits-border);
}

.brand-sub {
  font-family: var(--aits-mono);
  font-size: 10px;
  color: var(--aits-text-muted);
  letter-spacing: 0.12em;
}

.project-nav {
  position: relative;
  display: flex;
  gap: 2px;
  flex: 1;
}

.nav-indicator {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 2px;
  width: 0;
  background: var(--aits-accent);
  box-shadow: 0 0 8px var(--aits-accent-glow);
  pointer-events: none;
}

.nav-link {
  position: relative;
  padding: 14px 16px 12px;
  font-family: var(--aits-mono);
  font-size: 12px;
  letter-spacing: 0.04em;
  color: var(--aits-text-muted);
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover,
.nav-link.active {
  color: var(--aits-accent);
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: var(--aits-space-3);
  margin-left: auto;
}

.user-badge {
  display: inline-flex;
  align-items: center;
  gap: var(--aits-space-2);
  font-family: var(--aits-mono);
  font-size: 11px;
  color: var(--aits-text-muted);
  padding: 4px 10px;
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius);
}

.user-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--aits-accent);
  box-shadow: 0 0 6px var(--aits-accent-glow);
}

.logout-btn {
  border: none;
  background: none;
  font-family: var(--aits-mono);
  font-size: 11px;
  color: var(--aits-text-muted);
  cursor: pointer;
  padding: 4px 8px;
  transition: color 0.2s;
}

.logout-btn:hover {
  color: var(--aits-danger);
}

.main-content {
  flex: 1;
  padding: var(--aits-space-6);
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (prefers-reduced-motion: reduce) {
  .page-fade-enter-active,
  .page-fade-leave-active {
    transition: opacity 0.15s;
  }

  .page-fade-enter-from,
  .page-fade-leave-to {
    transform: none;
  }
}
</style>
