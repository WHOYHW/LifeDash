<template>
  <div class="todos-page">
    <header class="navbar">
      <div class="nav-left">
        <div class="logo">
          <span class="logo-icon">📊</span>
          <span class="logo-text">LifeDash</span>
        </div>
        <nav class="breadcrumb">
          <span>待办事项</span>
        </nav>
      </div>
      <div class="nav-right">
        <div class="user-info">
          <div class="avatar">{{ avatarLetter }}</div>
          <div class="user-detail">
            <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
          </div>
        </div>
        <button @click="goBack" class="btn-ghost">← 返回</button>
      </div>
    </header>

    <main class="todos-main">
      <div class="page-header">
        <div class="header-left">
          <h2>📋 待办管理</h2>
          <p class="subtitle">共 {{ todos.length }} 条 · 进行中 {{ activeTodos.length }} · 已完成 {{ completedTodos.length }}</p>
        </div>
        <button @click="showForm = !showForm" class="btn-primary">
          {{ showForm ? '✕ 取消' : '+ 添加待办' }}
        </button>
      </div>

      <div v-if="showForm" class="add-form">
        <div class="form-row">
          <input
            v-model="newTodo.title"
            type="text"
            placeholder="待办标题 (必填)"
            class="form-input title-input"
            maxlength="200"
          />
        </div>
        <div class="form-row">
          <textarea
            v-model="newTodo.description"
            placeholder="描述 (可选)"
            class="form-textarea"
            rows="2"
          ></textarea>
        </div>
        <div class="form-row form-options">
          <select v-model="newTodo.priority" class="form-select">
            <option value="high">🔴 高优先级</option>
            <option value="medium">🟡 中优先级</option>
            <option value="low">🟢 低优先级</option>
          </select>
          <input
            v-model="newTodo.due_date"
            type="datetime-local"
            class="form-input date-input"
          />
          <input
            v-model="newTodo.tag"
            type="text"
            placeholder="标签 (如: 工作)"
            class="form-input tag-input"
          />
          <button @click="handleCreate" class="btn-submit" :disabled="!newTodo.title">
            创建
          </button>
        </div>
      </div>

      <div v-if="errorMsg" class="error-banner">
        <span>⚠️ {{ errorMsg }}</span>
        <button class="btn-retry" @click="loadTodos">重试</button>
      </div>

      <div class="filter-tabs">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          @click="currentFilter = tab.key"
          :class="['tab', { active: currentFilter === tab.key }]"
        >
          {{ tab.label }}
          <span class="tab-count">{{ getCount(tab.key) }}</span>
        </button>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <div class="loading-text">加载中...</div>
      </div>

      <div class="todo-list" v-else-if="filteredTodos.length > 0">
        <div
          v-for="todo in filteredTodos"
          :key="todo.id"
          class="todo-item"
          :class="{ completed: todo.is_completed, overdue: isOverdue(todo) }"
        >
          <div
            class="todo-checkbox"
            :class="{ checked: todo.is_completed }"
            @click="handleToggle(todo.id)"
          >
            <span v-if="todo.is_completed">✓</span>
          </div>
          <div class="todo-content">
            <div class="todo-title-row">
              <span class="todo-title" :class="{ done: todo.is_completed }">{{ todo.title }}</span>
              <span v-if="todo.tag" class="tag-chip">{{ todo.tag }}</span>
            </div>
            <div v-if="todo.description" class="todo-desc">{{ todo.description }}</div>
            <div class="todo-meta">
              <span :class="['priority-tag', `priority-${todo.priority}`]">
                {{ priorityLabel(todo.priority) }}
              </span>
              <span v-if="todo.due_date" class="meta-item">
                📅 {{ formatDate(todo.due_date) }}
              </span>
              <span v-if="isOverdue(todo)" class="overdue-badge">已逾期</span>
              <span class="meta-item">🕐 {{ formatTime(todo.created_at) }}</span>
            </div>
          </div>
          <div class="todo-actions">
            <button @click="openEdit(todo)" class="action-btn edit-btn" title="编辑">✏️</button>
            <button @click="handleDelete(todo.id)" class="action-btn delete-btn" title="删除">🗑️</button>
          </div>
        </div>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📝</div>
        <div class="empty-text">暂无待办事项</div>
        <div class="empty-hint">点击右上角"+ 添加待办"创建第一条待办</div>
      </div>

      <div v-if="editingTodo" class="edit-modal" @click.self="editingTodo = null">
        <div class="modal-content">
          <h3>编辑待办</h3>
          <div class="form-row">
            <input v-model="editingTodo.title" type="text" class="form-input title-input" />
          </div>
          <div class="form-row">
            <textarea v-model="editingTodo.description" class="form-textarea" rows="2"></textarea>
          </div>
          <div class="form-row form-options">
            <select v-model="editingTodo.priority" class="form-select">
              <option value="high">🔴 高优先级</option>
              <option value="medium">🟡 中优先级</option>
              <option value="low">🟢 低优先级</option>
            </select>
            <input v-model="editingTodo.due_date" type="datetime-local" class="form-input date-input" />
            <input v-model="editingTodo.tag" type="text" placeholder="标签" class="form-input tag-input" />
          </div>
          <div class="modal-actions">
            <button @click="editingTodo = null" class="btn-cancel">取消</button>
            <button @click="handleUpdate" class="btn-submit">保存</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTodosStore } from '@/stores/todos'

const router = useRouter()
const authStore = useAuthStore()
const todosStore = useTodosStore()

const showForm = ref(false)
const editingTodo = ref(null)
const currentFilter = ref('all')
const errorMsg = ref('')

const newTodo = ref({
  title: '',
  description: '',
  priority: 'medium',
  due_date: '',
  tag: '',
})

const tabs = [
  { key: 'all', label: '全部' },
  { key: 'active', label: '进行中' },
  { key: 'completed', label: '已完成' },
  { key: 'overdue', label: '已逾期' },
]

const todos = computed(() => todosStore.todos)
const loading = computed(() => todosStore.loading)

const avatarLetter = computed(() => {
  const name = authStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const activeTodos = computed(() => todosStore.activeTodos)
const completedTodos = computed(() => todosStore.completedTodos)
const overdueTodos = computed(() => todosStore.overdueTodos)

const filteredTodos = computed(() => {
  switch (currentFilter.value) {
    case 'active': return activeTodos.value
    case 'completed': return completedTodos.value
    case 'overdue': return overdueTodos.value
    default: return todos.value
  }
})

function getCount(key) {
  switch (key) {
    case 'active': return activeTodos.value.length
    case 'completed': return completedTodos.value.length
    case 'overdue': return overdueTodos.value.length
    default: return todos.value.length
  }
}

function parseDateTime(str) {
  if (!str) return null
  const s = String(str)
  const m = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})[ T](\d{1,2}):(\d{1,2})(?::(\d{1,2}))?/)
  if (m) {
    return new Date(
      parseInt(m[1]), parseInt(m[2]) - 1, parseInt(m[3]),
      parseInt(m[4]), parseInt(m[5]), parseInt(m[6] || '0')
    )
  }
  const d = new Date(str)
  return isNaN(d.getTime()) ? null : d
}

function isOverdue(todo) {
  if (!todo.due_date || todo.is_completed) return false
  const now = new Date()
  const due = parseDateTime(todo.due_date)
  if (!due) return false
  return due < now
}

function priorityLabel(p) {
  return { high: '高', medium: '中', low: '低' }[p] || '中'
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const s = String(dateStr)
  const m = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})[ T](\d{1,2}):(\d{1,2})/)
  if (m) {
    return `${m[1]}-${m[2].padStart(2,'0')}-${m[3].padStart(2,'0')} ${m[4].padStart(2,'0')}:${m[5].padStart(2,'0')}`
  }
  const d = new Date(dateStr)
  if (isNaN(d.getTime())) return s
  const y = d.getFullYear()
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${mm}-${day} ${h}:${min}`
}

function formatTime(dtStr) {
  if (!dtStr) return ''
  const d = new Date(dtStr)
  const now = new Date()
  const diff = now - d
  const minutes = Math.floor(diff / 60000)
  if (minutes < 60) return `${minutes}分钟前`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `${hours}小时前`
  const days = Math.floor(hours / 24)
  if (days < 7) return `${days}天前`
  return d.toLocaleDateString('zh-CN')
}

async function loadTodos() {
  errorMsg.value = ''
  try {
    await todosStore.fetchTodos()
  } catch (err) {
    errorMsg.value = err.message || '未知错误'
  }
}

async function handleCreate() {
  if (!newTodo.value.title.trim()) return
  try {
    const data = {
      title: newTodo.value.title.trim(),
      description: newTodo.value.description.trim() || null,
      priority: newTodo.value.priority,
      due_date: newTodo.value.due_date ? newTodo.value.due_date.replace('T', ' ') + ':00' : null,
      tag: newTodo.value.tag.trim() || null,
    }
    await todosStore.createTodo(data)
    newTodo.value = { title: '', description: '', priority: 'medium', due_date: '', tag: '' }
    showForm.value = false
    errorMsg.value = ''
  } catch (err) {
    errorMsg.value = '创建失败: ' + (err.message || '未知错误')
  }
}

async function handleToggle(id) {
  try {
    await todosStore.toggleTodo(id)
    errorMsg.value = ''
  } catch (err) {
    errorMsg.value = '操作失败: ' + (err.message || '未知错误')
  }
}

async function handleDelete(id) {
  if (!confirm('确定删除这条待办吗？')) return
  try {
    await todosStore.deleteTodo(id)
    errorMsg.value = ''
  } catch (err) {
    errorMsg.value = '删除失败: ' + (err.message || '未知错误')
  }
}

function openEdit(todo) {
  editingTodo.value = { ...todo }
}

async function handleUpdate() {
  if (!editingTodo.value || !editingTodo.value.title.trim()) return
  try {
    const data = {
      title: editingTodo.value.title.trim(),
      description: editingTodo.value.description?.trim() || null,
      priority: editingTodo.value.priority,
      due_date: editingTodo.value.due_date ? (() => {
        const d = new Date(editingTodo.value.due_date)
        const pad = (n) => String(n).padStart(2, '0')
        return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`
      })() : null,
      tag: editingTodo.value.tag?.trim() || null,
    }
    await todosStore.updateTodo(editingTodo.value.id, data)
    editingTodo.value = null
  } catch (err) {
    alert('更新失败: ' + (err.message || '未知错误'))
  }
}

function goBack() {
  router.push('/dashboard')
}

onMounted(() => {
  loadTodos()
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
}

.todos-page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 14px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
}
.nav-left { display: flex; align-items: center; gap: 20px; }
.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon { font-size: 26px; }
.logo-text { font-size: 20px; font-weight: 700; color: white; }
.breadcrumb { color: rgba(255,255,255,0.85); font-size: 14px; }

.nav-right { display: flex; align-items: center; gap: 16px; }
.user-info {
  display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.15);
  padding: 6px 14px 6px 6px;
  border-radius: 30px;
}
.avatar {
  width: 34px; height: 34px; border-radius: 50%;
  background: linear-gradient(135deg, #ffecd2, #fcb69f);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #8b5a2b; font-size: 15px;
}
.user-name { color: white; font-weight: 600; font-size: 14px; }

.btn-ghost {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white; padding: 8px 18px;
  border-radius: 20px; font-weight: 500;
  cursor: pointer; transition: all 0.2s; font-size: 13px;
}
.btn-ghost:hover { background: rgba(255,255,255,0.3); }

.todos-main {
  flex: 1;
  padding: 28px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
}
.header-left h2 { font-size: 24px; color: #2d3748; font-weight: 700; margin-bottom: 4px; }
.subtitle { color: #718096; font-size: 14px; }

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white; border: none; padding: 10px 22px;
  border-radius: 10px; font-weight: 600;
  cursor: pointer; transition: all 0.2s; font-size: 14px;
}
.btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(102,126,234,0.4); }

.add-form {
  background: white; border-radius: 16px; padding: 20px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  margin-bottom: 20px;
}
.form-row { margin-bottom: 12px; }
.form-input {
  width: 100%; padding: 10px 14px; border: 1px solid #e2e8f0;
  border-radius: 10px; font-size: 14px; transition: border-color 0.2s;
}
.form-input:focus { outline: none; border-color: #667eea; }
.title-input { font-size: 15px; font-weight: 500; }
.form-textarea {
  width: 100%; padding: 10px 14px; border: 1px solid #e2e8f0;
  border-radius: 10px; font-size: 14px; resize: vertical;
  font-family: inherit;
}
.form-textarea:focus { outline: none; border-color: #667eea; }
.form-options {
  display: flex; gap: 12px; align-items: center; flex-wrap: wrap;
}
.form-select {
  padding: 8px 12px; border: 1px solid #e2e8f0;
  border-radius: 8px; font-size: 13px; background: white; cursor: pointer;
}
.date-input { width: 160px; }
.tag-input { width: 160px; }
.btn-submit {
  background: #38a169; color: white; border: none; padding: 8px 20px;
  border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px;
}
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-submit:hover:not(:disabled) { background: #2f855a; }

.filter-tabs {
  display: flex; gap: 8px; margin-bottom: 20px;
  border-bottom: 1px solid #e2e8f0; padding-bottom: 0;
}
.tab {
  padding: 10px 18px; border: none; background: none;
  font-size: 14px; font-weight: 500; color: #718096;
  cursor: pointer; border-bottom: 2px solid transparent;
  display: flex; align-items: center; gap: 6px;
  transition: all 0.2s;
}
.tab:hover { color: #2d3748; }
.tab.active { color: #667eea; border-bottom-color: #667eea; }
.tab-count {
  background: #edf2f7; color: #4a5568; font-size: 12px;
  padding: 2px 8px; border-radius: 10px; font-weight: 600;
}
.tab.active .tab-count { background: #e6f4ff; color: #667eea; }

.loading-state {
  text-align: center; padding: 60px 20px;
}
.loading-spinner {
  width: 36px; height: 36px; border: 3px solid #e2e8f0;
  border-top-color: #667eea; border-radius: 50%;
  margin: 0 auto 12px; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.loading-text { color: #a0aec0; font-size: 14px; }

.error-banner {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  background: #fff5f5; border: 1px solid #feb2b2;
  color: #c53030; padding: 12px 16px;
  border-radius: 10px; font-size: 14px; font-weight: 500;
  margin-bottom: 16px;
}
.btn-retry {
  background: #c53030; color: white; border: none;
  padding: 6px 14px; border-radius: 6px;
  font-weight: 600; cursor: pointer; font-size: 12px;
}
.btn-retry:hover { background: #9b2c2c; }

.todo-list { display: flex; flex-direction: column; gap: 10px; }

.todo-item {
  display: flex; align-items: flex-start; gap: 14px;
  padding: 16px 18px; background: white;
  border-radius: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  transition: all 0.2s;
  border-left: 4px solid #e2e8f0;
}
.todo-item:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); transform: translateY(-1px); }
.todo-item.completed { opacity: 0.65; border-left-color: #38a169; }
.todo-item.overdue { border-left-color: #e53e3e; }

.todo-checkbox {
  width: 24px; height: 24px; border: 2px solid #cbd5e0;
  border-radius: 7px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 13px; color: white; transition: all 0.2s;
  cursor: pointer; margin-top: 2px;
}
.todo-checkbox:hover { border-color: #667eea; }
.todo-checkbox.checked { background: #38a169; border-color: #38a169; }

.todo-content { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.todo-title-row { display: flex; align-items: center; gap: 8px; }
.todo-title { font-size: 15px; color: #2d3748; font-weight: 500; }
.todo-title.done { text-decoration: line-through; color: #a0aec0; }
.tag-chip {
  background: #edf2f7; color: #4a5568; font-size: 11px;
  padding: 2px 8px; border-radius: 10px; font-weight: 500;
}
.todo-desc { font-size: 13px; color: #718096; line-height: 1.5; }

.todo-meta { display: flex; align-items: center; gap: 10px; margin-top: 6px; flex-wrap: wrap; }
.meta-item { font-size: 12px; color: #a0aec0; }
.priority-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.priority-high { background: #fed7d7; color: #c53030; }
.priority-medium { background: #feebc8; color: #dd6b20; }
.priority-low { background: #c6f6d5; color: #38a169; }
.overdue-badge {
  background: #fed7d7; color: #c53030; font-size: 11px;
  padding: 2px 8px; border-radius: 4px; font-weight: 600;
}

.todo-actions { display: flex; gap: 6px; flex-shrink: 0; }
.action-btn {
  width: 32px; height: 32px; border: none; background: #f7fafc;
  border-radius: 8px; cursor: pointer; font-size: 14px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s;
}
.action-btn:hover { background: #edf2f7; }
.delete-btn:hover { background: #fed7d7; }

.empty-state {
  text-align: center; padding: 60px 20px;
}
.empty-icon { font-size: 64px; margin-bottom: 16px; }
.empty-text { font-size: 18px; color: #4a5568; font-weight: 500; }
.empty-hint { font-size: 14px; color: #a0aec0; margin-top: 8px; }

.edit-modal {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex;
  align-items: center; justify-content: center; z-index: 100;
}
.modal-content {
  background: white; border-radius: 16px; padding: 24px;
  width: 90%; max-width: 500px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}
.modal-content h3 { font-size: 18px; color: #2d3748; font-weight: 700; margin-bottom: 16px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 16px; }
.btn-cancel {
  background: #edf2f7; color: #4a5568; border: none; padding: 8px 20px;
  border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px;
}
.btn-cancel:hover { background: #e2e8f0; }

@media (max-width: 640px) {
  .todos-main { padding: 16px; }
  .page-header { flex-direction: column; gap: 12px; }
  .form-options { flex-direction: column; align-items: stretch; }
  .date-input, .tag-input { width: 100%; }
  .filter-tabs { overflow-x: auto; }
}
</style>
