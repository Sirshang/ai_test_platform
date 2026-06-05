<script setup>
import { computed, nextTick, onMounted, onUnmounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { gsap } from 'gsap'
import { ElMessage, ElMessageBox } from 'element-plus'
import MonacoEditor from '../components/MonacoEditor.vue'
import PageHeader from '../components/ui/PageHeader.vue'
import MagneticButton from '../components/ui/MagneticButton.vue'
import StatusPulse from '../components/ui/StatusPulse.vue'
import AiLoader from '../components/ui/AiLoader.vue'
import ContextMenu from '../components/ui/ContextMenu.vue'
import {
  createApiCase,
  deleteApiCase,
  fetchApiCases,
  generateApiScript,
  importSwagger,
  updateApiCase,
} from '../api/apitest'
import { fetchProject } from '../api/projects'
import { getErrorMessage } from '../api/client'
import { useGsapContext, pageEnterTimeline } from '../composables/useGsapContext'
import { scrambleTo } from '../composables/useScrambleText'

const route = useRoute()
const projectId = computed(() => Number(route.params.id))

const project = ref(null)
const cases = ref([])
const loading = ref(false)
const saving = ref(false)
const generating = ref(false)
const importing = ref(false)
const importToastText = ref('')
const showImportToast = ref(false)

const showCreate = ref(false)
const showEditor = ref(false)
const showImport = ref(false)

const contextMenu = reactive({ visible: false, x: 0, y: 0, row: null })
const tableRef = ref(null)

const createForm = ref({
  title: '',
  method: 'GET',
  path: '/',
  description: '',
  status: 'draft',
})

const editForm = ref({
  id: null,
  title: '',
  description: '',
  method: 'GET',
  path: '',
  status: 'draft',
  script: '',
  headers: {},
  query_params: {},
  body: '',
})

const importForm = ref({ content: '', format: 'json' })

const methodOptions = ['GET', 'POST', 'PUT', 'PATCH', 'DELETE']
const statusMap = { draft: '草稿', ready: '就绪' }
const statusTagType = { draft: 'info', ready: 'success' }

const { rootRef: pageRef, replay } = useGsapContext(() => {
  pageEnterTimeline(pageRef.value)
})

async function loadData() {
  loading.value = true
  try {
    const [projectRes, casesRes] = await Promise.all([
      fetchProject(projectId.value),
      fetchApiCases(projectId.value),
    ])
    project.value = projectRes.data
    cases.value = casesRes.data
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    loading.value = false
    await nextTick()
    replay()
    gsap.from(tableRef.value?.$el ?? [], { autoAlpha: 0, y: 16, duration: 0.45, ease: 'power3.out' })
  }
}

watch(showEditor, (open) => {
  if (open) {
    nextTick(() => {
      gsap.from('.editor-form > *', {
        autoAlpha: 0,
        x: 20,
        duration: 0.35,
        stagger: 0.06,
        ease: 'power2.out',
      })
    })
  }
})

async function handleCreate() {
  if (!createForm.value.title.trim() || !createForm.value.path.trim()) {
    ElMessage.warning('请填写标题和路径')
    return
  }
  saving.value = true
  try {
    await createApiCase({
      project: projectId.value,
      title: createForm.value.title.trim(),
      method: createForm.value.method,
      path: createForm.value.path.trim(),
      description: createForm.value.description.trim(),
      status: createForm.value.status,
      headers: {},
      query_params: {},
      body: '',
      script: '',
    })
    ElMessage.success('用例创建成功')
    showCreate.value = false
    createForm.value = { title: '', method: 'GET', path: '/', description: '', status: 'draft' }
    await loadData()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

function openEditor(row) {
  editForm.value = {
    id: row.id,
    title: row.title,
    description: row.description || '',
    method: row.method,
    path: row.path,
    status: row.status,
    script: row.script || '',
    headers: row.headers || {},
    query_params: row.query_params || {},
    body: row.body || '',
  }
  showEditor.value = true
}

async function handleSave() {
  saving.value = true
  try {
    await updateApiCase(editForm.value.id, {
      title: editForm.value.title,
      description: editForm.value.description,
      method: editForm.value.method,
      path: editForm.value.path,
      status: editForm.value.status,
      script: editForm.value.script,
      headers: editForm.value.headers,
      query_params: editForm.value.query_params,
      body: editForm.value.body,
    })
    ElMessage.success('保存成功')
    showEditor.value = false
    await loadData()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    saving.value = false
  }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定删除用例「${row.title}」？`, '删除确认', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteApiCase(row.id)
    ElMessage.success('已删除')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(getErrorMessage(error))
    }
  }
}

function handleRowContextMenu(row, _column, event) {
  event.preventDefault()
  contextMenu.row = row
  contextMenu.x = event.clientX
  contextMenu.y = event.clientY
  contextMenu.visible = true
}

function closeContextMenu() {
  contextMenu.visible = false
  contextMenu.row = null
}

async function changeStatus(status) {
  const row = contextMenu.row
  closeContextMenu()
  if (!row || row.status === status) return
  try {
    await updateApiCase(row.id, { status })
    ElMessage.success(`状态已更新为「${statusMap[status]}」`)
    await loadData()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  }
}

function buildInterfacePayload(caseRow) {
  return {
    title: caseRow.title,
    method: caseRow.method,
    path: caseRow.path,
    description: caseRow.description || '',
    headers: caseRow.headers || {},
    query_params: caseRow.query_params || {},
    body: caseRow.body || '',
  }
}

async function handleGenerate(row) {
  generating.value = true
  try {
    const { data } = await generateApiScript({
      interfaces: [buildInterfacePayload(row)],
      case_id: row.id,
    })
    if (showEditor.value && editForm.value.id === row.id) {
      editForm.value.script = data.script
    }
    ElMessage.success('AI 脚本生成成功')
    await loadData()
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    generating.value = false
  }
}

async function handleGenerateInEditor() {
  const row = {
    id: editForm.value.id,
    title: editForm.value.title,
    method: editForm.value.method,
    path: editForm.value.path,
    description: editForm.value.description,
    headers: editForm.value.headers,
    query_params: editForm.value.query_params,
    body: editForm.value.body,
  }
  generating.value = true
  try {
    const { data } = await generateApiScript({
      interfaces: [buildInterfacePayload(row)],
      case_id: row.id,
    })
    editForm.value.script = data.script
    ElMessage.success('AI 脚本已填入编辑器')
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    generating.value = false
  }
}

async function handleImport() {
  if (!importForm.value.content.trim()) {
    ElMessage.warning('请粘贴 Swagger JSON/YAML 内容')
    return
  }
  importing.value = true
  try {
    const { data } = await importSwagger(projectId.value, {
      content: importForm.value.content,
      format: importForm.value.format,
    })
    showImport.value = false
    importForm.value.content = ''
    await loadData()
    await nextTick()
    showImportToast.value = true
    importToastText.value = ''
    const toastEl = document.querySelector('.import-toast')
    if (toastEl) {
      scrambleTo(toastEl, `+${data.created_count} CASES IMPORTED`, 0.7)
    }
    setTimeout(() => {
      showImportToast.value = false
    }, 3200)
    ElMessage.success(`成功导入 ${data.created_count} 条用例`)
  } catch (error) {
    ElMessage.error(getErrorMessage(error))
  } finally {
    importing.value = false
  }
}

onMounted(() => {
  loadData()
  document.addEventListener('click', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
})
</script>

<template>
  <div ref="pageRef" class="api-case-page" @click="closeContextMenu">
    <PageHeader
      :eyebrow="project?.name?.toUpperCase() || 'LOADING'"
      title="API 用例"
      subtitle="管理接口用例、导入 Swagger、AI 生成 pytest 脚本"
    >
      <template #actions>
        <button type="button" class="aits-btn-ghost" @click="showImport = true">导入 Swagger</button>
        <MagneticButton @click="showCreate = true">新建用例</MagneticButton>
      </template>
    </PageHeader>

    <p v-if="showImportToast" class="import-toast" aria-live="polite">{{ importToastText }}</p>

    <div class="page-body">
      <el-table
        ref="tableRef"
        v-loading="loading"
        :data="cases"
        class="case-table"
        @row-contextmenu="handleRowContextMenu"
        @row-dblclick="openEditor"
      >
        <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
        <el-table-column label="请求" min-width="180">
          <template #default="{ row }">
            <span class="method-badge" :data-method="row.method">{{ row.method }}</span>
            <span class="path-text">{{ row.path }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <span class="status-cell">
              <StatusPulse
                :active="row.status === 'ready'"
                :variant="row.status === 'ready' ? 'ready' : 'draft'"
              />
              <el-tag :type="statusTagType[row.status]" size="small">{{ statusMap[row.status] }}</el-tag>
            </span>
          </template>
        </el-table-column>
        <el-table-column label="脚本" width="80" align="center">
          <template #default="{ row }">
            <StatusPulse
              :active="Boolean(row.script)"
              :variant="row.script ? 'ready' : 'empty'"
            />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="210" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openEditor(row)">编辑</el-button>
            <el-button link size="small" :loading="generating" @click="handleGenerate(row)">AI 生成</el-button>
            <el-button link type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <p class="table-hint">双击行打开编辑器 · 右键切换状态</p>
    </div>

    <ContextMenu
      :visible="contextMenu.visible"
      :x="contextMenu.x"
      :y="contextMenu.y"
    >
      <button type="button" @click="changeStatus('draft')">设为草稿</button>
      <button type="button" @click="changeStatus('ready')">设为就绪</button>
    </ContextMenu>

    <el-dialog v-model="showCreate" title="新建 API 用例" width="480px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="标题" required>
          <el-input v-model="createForm.title" placeholder="获取用户列表" />
        </el-form-item>
        <el-form-item label="HTTP 方法">
          <el-select v-model="createForm.method" style="width: 100%">
            <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="路径" required>
          <el-input v-model="createForm.path" placeholder="/api/users" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="createForm.description" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <button type="button" class="aits-btn-ghost" @click="showCreate = false">取消</button>
        <MagneticButton :loading="saving" @click="handleCreate">创建</MagneticButton>
      </template>
    </el-dialog>

    <el-dialog v-model="showImport" title="导入 Swagger" width="560px" destroy-on-close>
      <el-form label-position="top">
        <el-form-item label="格式">
          <el-radio-group v-model="importForm.format">
            <el-radio label="json">JSON</el-radio>
            <el-radio label="yaml">YAML</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="Swagger 内容">
          <el-input
            v-model="importForm.content"
            type="textarea"
            :rows="12"
            placeholder="粘贴 OpenAPI 2.0 / 3.x 规范内容"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <button type="button" class="aits-btn-ghost" @click="showImport = false">取消</button>
        <MagneticButton :loading="importing" @click="handleImport">导入</MagneticButton>
      </template>
    </el-dialog>

    <el-drawer v-model="showEditor" title="编辑用例" size="62%" destroy-on-close>
      <div class="editor-form">
        <div class="form-row">
          <el-form-item label="标题" class="flex-2">
            <el-input v-model="editForm.title" />
          </el-form-item>
          <el-form-item label="状态" class="flex-1">
            <el-select v-model="editForm.status" style="width: 100%">
              <el-option label="草稿" value="draft" />
              <el-option label="就绪" value="ready" />
            </el-select>
          </el-form-item>
        </div>
        <div class="form-row">
          <el-form-item label="方法" class="flex-1">
            <el-select v-model="editForm.method" style="width: 100%">
              <el-option v-for="m in methodOptions" :key="m" :label="m" :value="m" />
            </el-select>
          </el-form-item>
          <el-form-item label="路径" class="flex-3">
            <el-input v-model="editForm.path" />
          </el-form-item>
        </div>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="2" />
        </el-form-item>

        <div class="script-header">
          <span>PYTEST SCRIPT</span>
          <MagneticButton :loading="generating" @click="handleGenerateInEditor">
            AI 生成
          </MagneticButton>
        </div>
        <AiLoader :active="generating">
          <MonacoEditor v-model="editForm.script" language="python" height="380px" />
        </AiLoader>
      </div>

      <template #footer>
        <button type="button" class="aits-btn-ghost" @click="showEditor = false">取消</button>
        <MagneticButton :loading="saving" @click="handleSave">保存</MagneticButton>
      </template>
    </el-drawer>
  </div>
</template>

<style scoped>
.import-toast {
  position: fixed;
  bottom: var(--aits-space-6);
  right: var(--aits-space-6);
  margin: 0;
  padding: var(--aits-space-3) var(--aits-space-4);
  font-family: var(--aits-mono);
  font-size: 12px;
  color: var(--aits-accent);
  background: var(--aits-surface);
  border: 1px solid rgba(77, 255, 145, 0.3);
  border-radius: var(--aits-radius);
  box-shadow: var(--aits-shadow);
  z-index: 200;
  min-height: 0;
}

.import-toast:empty {
  display: none;
}

.case-table {
  border: 1px solid var(--aits-border-subtle);
  border-radius: var(--aits-radius-lg);
  overflow: hidden;
}

.method-badge {
  font-family: var(--aits-mono);
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border: 1px solid var(--aits-border);
  border-radius: 3px;
  margin-right: var(--aits-space-2);
  color: var(--aits-accent);
}

.method-badge[data-method='POST'],
.method-badge[data-method='PUT'],
.method-badge[data-method='PATCH'] {
  color: var(--aits-warn);
  border-color: rgba(255, 159, 28, 0.3);
}

.method-badge[data-method='DELETE'] {
  color: var(--aits-danger);
  border-color: rgba(255, 107, 107, 0.3);
}

.path-text {
  font-family: var(--aits-mono);
  font-size: 12px;
  color: var(--aits-text-muted);
}

.status-cell {
  display: inline-flex;
  align-items: center;
  gap: var(--aits-space-2);
}

.table-hint {
  margin: var(--aits-space-3) 0 0;
  font-family: var(--aits-mono);
  font-size: 10px;
  letter-spacing: 0.06em;
  color: var(--aits-text-muted);
}

.editor-form {
  padding: 0 var(--aits-space-1);
}

.form-row {
  display: flex;
  gap: var(--aits-space-3);
}

.flex-1 { flex: 1; }
.flex-2 { flex: 2; }
.flex-3 { flex: 3; }

.script-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--aits-space-3);
  font-family: var(--aits-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  color: var(--aits-text-muted);
}

.script-header .magnetic-btn {
  height: 34px;
  padding: 0 14px;
  font-size: 11px;
}
</style>
