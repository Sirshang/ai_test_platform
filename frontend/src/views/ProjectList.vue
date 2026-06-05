<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { gsap } from 'gsap'
import { ElMessage } from 'element-plus'
import { createProject, fetchProjects } from '../api/projects'
import { getErrorMessage } from '../api/client'
import { useGsapContext, pageEnterTimeline } from '../composables/useGsapContext'
import { useSpotlight } from '../composables/useSpotlight'
import PageHeader from '../components/ui/PageHeader.vue'
import MagneticButton from '../components/ui/MagneticButton.vue'

const router = useRouter()
const projects = ref([])
const loading = ref(false)
const showCreate = ref(false)
const creating = ref(false)
const createForm = ref({ name: '', description: '' })
const { containerRef: gridRef } = useSpotlight()

const { rootRef: pageRef, replay } = useGsapContext(() => {
  pageEnterTimeline(pageRef.value)
})

async function loadProjects() {
  loading.value = true
  try {
    const { data } = await fetchProjects()
    projects.value = data
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loading.value = false
    await nextTick()
    animateCards()
    replay()
  }
}

function animateCards() {
  if (!pageRef.value) return
  gsap.from(pageRef.value.querySelectorAll('.project-card'), {
    autoAlpha: 0,
    y: 28,
    duration: 0.55,
    stagger: { amount: 0.35, from: 'start' },
    ease: 'power3.out',
    clearProps: 'transform',
  })
}

watch(showCreate, (open) => {
  if (open) {
    nextTick(() => {
      gsap.from('.create-dialog-inner', {
        autoAlpha: 0,
        scale: 0.96,
        duration: 0.3,
        ease: 'back.out(1.4)',
      })
    })
  }
})

async function handleCreate() {
  if (!createForm.value.name.trim()) {
    ElMessage.warning('请输入项目名称')
    return
  }
  creating.value = true
  try {
    const { data } = await createProject({
      name: createForm.value.name.trim(),
      description: createForm.value.description.trim(),
    })
    ElMessage.success('项目创建成功')
    showCreate.value = false
    createForm.value = { name: '', description: '' }
    router.push(`/projects/${data.id}`)
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    creating.value = false
  }
}

function formatDate(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('zh-CN')
}

onMounted(loadProjects)
</script>

<template>
  <div ref="pageRef" class="project-list-page">
    <PageHeader
      eyebrow="WORKSPACE / 01"
      title="我的项目"
      subtitle="选择项目进入 API 用例管理与 AI 脚本生成控制台"
    >
      <template #actions>
        <MagneticButton @click="showCreate = true">新建项目</MagneticButton>
      </template>
    </PageHeader>

    <div class="page-body">
      <el-skeleton v-if="loading" :rows="4" animated />

      <div v-else-if="projects.length === 0" class="empty-state">
        <span class="empty-code">NO_PROJECTS</span>
        <p>暂无项目，创建第一个测试项目开始</p>
        <MagneticButton @click="showCreate = true">创建项目</MagneticButton>
      </div>

      <div v-else ref="gridRef" class="project-grid">
        <router-link
          v-for="project in projects"
          :key="project.id"
          :to="`/projects/${project.id}`"
          class="project-card spotlight-card"
        >
          <span class="ghost-index">{{ String(project.id).padStart(2, '0') }}</span>
          <div class="card-top">
            <span class="card-id">PRJ-{{ String(project.id).padStart(3, '0') }}</span>
            <span class="card-date">{{ formatDate(project.created_at) }}</span>
          </div>
          <h2>{{ project.name }}</h2>
          <p class="card-desc">{{ project.description || '暂无描述' }}</p>
          <div class="card-footer">
            <span class="owner-tag">{{ project.owner }}</span>
            <span class="enter-hint">OPEN →</span>
          </div>
        </router-link>
      </div>
    </div>

    <el-dialog v-model="showCreate" title="新建项目" width="440px" destroy-on-close>
      <div class="create-dialog-inner">
        <el-form label-position="top">
          <el-form-item label="项目名称" required>
            <el-input v-model="createForm.name" placeholder="用户中心 API 测试" maxlength="100" />
          </el-form-item>
          <el-form-item label="描述">
            <el-input
              v-model="createForm.description"
              type="textarea"
              :rows="3"
              placeholder="项目用途说明（可选）"
            />
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <button type="button" class="aits-btn-ghost" @click="showCreate = false">取消</button>
        <MagneticButton :loading="creating" @click="handleCreate">创建</MagneticButton>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--aits-space-4);
  padding: var(--aits-space-7) var(--aits-space-5);
  border: 1px dashed var(--aits-border);
  border-radius: var(--aits-radius-lg);
  text-align: center;
}

.empty-code {
  font-family: var(--aits-mono);
  font-size: 11px;
  color: var(--aits-accent);
  letter-spacing: 0.14em;
}

.empty-state p {
  margin: 0;
  color: var(--aits-text-muted);
}

.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: var(--aits-space-4);
}

.project-card {
  display: flex;
  flex-direction: column;
  padding: var(--aits-space-5);
  border-radius: var(--aits-radius-lg);
  text-decoration: none;
  color: inherit;
  transition: border-color 0.3s, box-shadow 0.3s;
}

.project-card:hover {
  border-color: rgba(77, 255, 145, 0.35);
  box-shadow: 0 0 0 1px rgba(77, 255, 145, 0.12), var(--aits-shadow);
}

.card-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--aits-space-3);
}

.card-id {
  font-family: var(--aits-mono);
  font-size: 10px;
  color: var(--aits-accent);
  letter-spacing: 0.08em;
}

.card-date {
  font-family: var(--aits-mono);
  font-size: 10px;
  color: var(--aits-text-muted);
}

.project-card h2 {
  margin: 0 0 var(--aits-space-2);
  font-family: var(--aits-display);
  font-size: 18px;
  font-weight: 700;
}

.card-desc {
  margin: 0 0 var(--aits-space-4);
  font-size: 13px;
  color: var(--aits-text-muted);
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.55;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.owner-tag {
  font-family: var(--aits-mono);
  font-size: 10px;
  padding: 3px 8px;
  border: 1px solid var(--aits-border);
  border-radius: var(--aits-radius);
  color: var(--aits-text-muted);
}

.enter-hint {
  font-family: var(--aits-mono);
  font-size: 10px;
  color: var(--aits-accent);
  opacity: 0;
  letter-spacing: 0.08em;
  transition: opacity 0.25s;
}

.project-card:hover .enter-hint {
  opacity: 1;
}
</style>
