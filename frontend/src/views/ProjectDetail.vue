<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { ElMessage } from 'element-plus'
import { fetchProject } from '../api/projects'
import { getErrorMessage } from '../api/client'
import { useGsapContext, pageEnterTimeline } from '../composables/useGsapContext'
import { useSpotlight } from '../composables/useSpotlight'
import PageHeader from '../components/ui/PageHeader.vue'
import MagneticButton from '../components/ui/MagneticButton.vue'

const route = useRoute()
const router = useRouter()
const project = ref(null)
const loading = ref(true)
const { containerRef: actionsRef } = useSpotlight()

const { rootRef: pageRef, replay } = useGsapContext(() => {
  pageEnterTimeline(pageRef.value)
})

async function loadProject() {
  loading.value = true
  try {
    const { data } = await fetchProject(route.params.id)
    project.value = data
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
    router.push('/projects')
  } finally {
    loading.value = false
    await nextTick()
    replay()
    gsap.from(pageRef.value?.querySelectorAll('.meta-card, .action-card') ?? [], {
      autoAlpha: 0,
      y: 20,
      duration: 0.45,
      stagger: 0.08,
      ease: 'power3.out',
    })
  }
}

onMounted(loadProject)
</script>

<template>
  <div ref="pageRef" class="project-detail">
    <template v-if="loading">
      <el-skeleton :rows="5" animated />
    </template>

    <template v-else-if="project">
      <PageHeader
        :eyebrow="`PROJECT / ${String(project.id).padStart(3, '0')}`"
        :title="project.name"
        :subtitle="project.description || '暂无描述'"
      >
        <template #actions>
          <router-link :to="`/projects/${project.id}/api-cases`">
            <MagneticButton>管理 API 用例</MagneticButton>
          </router-link>
        </template>
      </PageHeader>

      <div class="page-body">
        <div class="meta-grid">
          <div class="meta-card spotlight-card">
            <span class="meta-label">负责人</span>
            <span class="meta-value">{{ project.owner }}</span>
          </div>
          <div class="meta-card spotlight-card">
            <span class="meta-label">创建时间</span>
            <span class="meta-value mono">{{ new Date(project.created_at).toLocaleString('zh-CN') }}</span>
          </div>
          <div class="meta-card spotlight-card">
            <span class="meta-label">最近更新</span>
            <span class="meta-value mono">{{ new Date(project.updated_at).toLocaleString('zh-CN') }}</span>
          </div>
        </div>

        <section class="quick-actions">
          <h2 class="section-label">QUICK ACCESS</h2>
          <div ref="actionsRef" class="action-cards">
            <router-link :to="`/projects/${project.id}/api-cases`" class="action-card spotlight-card">
              <span class="action-icon">API</span>
              <div>
                <strong>API 用例</strong>
                <p>创建、编辑、AI 生成 pytest 脚本</p>
              </div>
              <span class="action-arrow">→</span>
            </router-link>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--aits-space-3);
  margin-bottom: var(--aits-space-7);
}

.meta-card {
  padding: var(--aits-space-4) var(--aits-space-5);
  border-radius: var(--aits-radius);
  display: flex;
  flex-direction: column;
  gap: var(--aits-space-2);
}

.meta-label {
  font-family: var(--aits-mono);
  font-size: 10px;
  color: var(--aits-text-muted);
  letter-spacing: 0.1em;
}

.meta-value {
  font-size: 14px;
  font-weight: 500;
}

.meta-value.mono {
  font-family: var(--aits-mono);
  font-size: 12px;
}

.section-label {
  margin: 0 0 var(--aits-space-4);
  font-family: var(--aits-mono);
  font-size: 10px;
  letter-spacing: 0.14em;
  color: var(--aits-text-muted);
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--aits-space-3);
}

.action-card {
  display: flex;
  align-items: center;
  gap: var(--aits-space-4);
  padding: var(--aits-space-5);
  border-radius: var(--aits-radius-lg);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.25s;
}

.action-card:hover {
  border-color: rgba(77, 255, 145, 0.35);
}

.action-icon {
  font-family: var(--aits-mono);
  font-size: 12px;
  font-weight: 600;
  color: var(--aits-accent);
  padding: 10px 12px;
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius);
}

.action-card strong {
  display: block;
  font-family: var(--aits-display);
  font-size: 15px;
  margin-bottom: 4px;
}

.action-card p {
  margin: 0;
  font-size: 12px;
  color: var(--aits-text-muted);
}

.action-arrow {
  margin-left: auto;
  font-family: var(--aits-mono);
  color: var(--aits-accent);
  opacity: 0;
  transition: opacity 0.25s;
}

.action-card:hover .action-arrow {
  opacity: 1;
}
</style>
