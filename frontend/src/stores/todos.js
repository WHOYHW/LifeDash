import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { todoApi } from '@/api/todos'

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

export const useTodosStore = defineStore('todos', () => {
  const todos = ref([])
  const todayTodos = ref([])
  const loading = ref(false)
  const error = ref('')

  const activeTodos = computed(() =>
    todos.value.filter(t => !t.is_completed)
  )
  const completedTodos = computed(() =>
    todos.value.filter(t => t.is_completed)
  )
  const overdueTodos = computed(() => {
    const now = new Date()
    return todos.value.filter(t => {
      if (t.is_completed || !t.due_date) return false
      const due = parseDateTime(t.due_date)
      if (!due) return false
      return due < now
    })
  })

  async function fetchTodos(params = {}) {
    loading.value = true
    error.value = ''
    try {
      const res = await todoApi.list(params)
      todos.value = res.data
      return res.data
    } catch (err) {
      error.value = err.message || '加载待办失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function fetchTodayTodos() {
    try {
      const res = await todoApi.today()
      todayTodos.value = res.data
      return res.data
    } catch (err) {
      throw err
    }
  }

  async function createTodo(data) {
    const res = await todoApi.create(data)
    todos.value.unshift(res.data)
    return res.data
  }

  async function updateTodo(id, data) {
    const res = await todoApi.update(id, data)
    const idx = todos.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      todos.value[idx] = res.data
    }
    return res.data
  }

  async function toggleTodo(id) {
    const res = await todoApi.toggle(id)
    const idx = todos.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      todos.value[idx] = res.data
    }
    return res.data
  }

  async function deleteTodo(id) {
    await todoApi.delete(id)
    const idx = todos.value.findIndex(t => t.id === id)
    if (idx !== -1) {
      todos.value.splice(idx, 1)
    }
  }

  return {
    todos,
    todayTodos,
    loading,
    error,
    activeTodos,
    completedTodos,
    overdueTodos,
    fetchTodos,
    fetchTodayTodos,
    createTodo,
    updateTodo,
    toggleTodo,
    deleteTodo,
  }
})
