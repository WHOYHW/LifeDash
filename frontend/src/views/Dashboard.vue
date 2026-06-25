<template>
  <div class="dashboard">
    <header class="navbar">
      <div class="nav-left">
        <div class="logo">
          <span class="logo-icon">📊</span>
          <span class="logo-text">LifeDash</span>
        </div>
      </div>
      <div class="nav-right">
        <div class="user-info">
          <div class="avatar">{{ avatarLetter }}</div>
          <div class="user-detail">
            <span class="user-name">{{ authStore.user?.username || '用户' }}</span>
            <span class="user-role">在线</span>
          </div>
        </div>
        <button @click="handleLogout" class="logout-btn">
          <span>退出</span>
        </button>
      </div>
    </header>

    <div class="main-layout">
      <aside class="sidebar">
        <nav class="side-nav">
          <div class="nav-section">主菜单</div>
          <ul>
            <li :class="{active: activeMenu === 'dashboard'}" @click="activeMenu = 'dashboard'">
              <span class="nav-icon">🏠</span>
              <span class="nav-label">仪表盘</span>
            </li>
            <li :class="{active: activeMenu === 'todos'}" @click="activeMenu = 'todos'; goToTodos()">
              <span class="nav-icon">📋</span>
              <span class="nav-label">待办事项</span>
              <span v-if="activeCount > 0" class="nav-badge">{{ activeCount }}</span>
            </li>
            <li @click="activeMenu = 'habits'">
              <span class="nav-icon">✅</span>
              <span class="nav-label">习惯养成</span>
            </li>
            <li @click="activeMenu = 'notes'">
              <span class="nav-icon">📝</span>
              <span class="nav-label">快速笔记</span>
            </li>
            <li @click="activeMenu = 'expenses'">
              <span class="nav-icon">💰</span>
              <span class="nav-label">财务记账</span>
            </li>
          </ul>
          <div class="nav-section">其他</div>
          <ul>
            <li @click="activeMenu = 'stats'">
              <span class="nav-icon">📈</span>
              <span class="nav-label">数据统计</span>
            </li>
            <li @click="activeMenu = 'settings'">
              <span class="nav-icon">⚙️</span>
              <span class="nav-label">系统设置</span>
            </li>
          </ul>
        </nav>
      </aside>

      <main class="content">
        <div class="page-header">
          <div class="page-title">
            <h2>欢迎回来，{{ authStore.user?.username || '用户' }} 👋</h2>
            <p class="page-subtitle">{{ currentDate }}</p>
          </div>
          <div class="page-actions">
            <button class="btn-ghost">🔔</button>
            <button class="btn-ghost">🔍</button>
          </div>
        </div>

        <div v-if="loadError" class="load-error-banner">
          <span>⚠️ {{ loadError }}</span>
          <button class="btn-retry" @click="reloadTodos">重试</button>
        </div>

        <div class="stats-row">
          <div class="stat-card">
            <div class="stat-icon-wrap stat-icon-1">📋</div>
            <div class="stat-info">
              <span class="stat-value">{{ activeCount }}</span>
              <span class="stat-label">进行中待办</span>
            </div>
            <div class="stat-trend up">今日</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap stat-icon-2">✅</div>
            <div class="stat-info">
              <span class="stat-value">85%</span>
              <span class="stat-label">习惯完成</span>
            </div>
            <div class="stat-trend up">↑ 12%</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap stat-icon-3">💰</div>
            <div class="stat-info">
              <span class="stat-value">¥ 2,380</span>
              <span class="stat-label">本月支出</span>
            </div>
            <div class="stat-trend down">↓ 8%</div>
          </div>
          <div class="stat-card">
            <div class="stat-icon-wrap stat-icon-4">📝</div>
            <div class="stat-info">
              <span class="stat-value">24</span>
              <span class="stat-label">笔记数量</span>
            </div>
            <div class="stat-trend up">↑ 5</div>
          </div>
        </div>

        <div class="content-row">
          <div class="panel">
            <div class="panel-header">
              <h3>⏰ 实时时钟</h3>
              <span class="panel-action">详情</span>
            </div>
            <div class="clock-display">
              <span class="clock-time">{{ currentTime }}</span>
              <span class="clock-date">{{ currentDate }}</span>
              <span class="clock-greeting">{{ greeting }}</span>
            </div>
          </div>

          <div class="panel weather-panel">
            <WeatherCard />
          </div>
        </div>

        <div class="content-row">
          <div class="panel">
            <div class="panel-header">
              <h3>📋 今日待办</h3>
              <span class="panel-action" @click="goToTodos">查看全部 →</span>
            </div>
            <div class="todo-list" v-if="todayTodos.length > 0">
              <div
                v-for="todo in todayTodos"
                :key="todo.id"
                class="todo-item"
                :class="{ completed: todo.is_completed }"
              >
                <div
                  class="todo-checkbox"
                  :class="{ checked: todo.is_completed }"
                  @click="toggleTodo(todo.id)"
                >
                  <span v-if="todo.is_completed">✓</span>
                </div>
                <div class="todo-content">
                  <span class="todo-title" :class="{ done: todo.is_completed }">{{ todo.title }}</span>
                  <span class="todo-meta">
                    <span :class="['priority-tag', `priority-${todo.priority}`]">{{ formatPriority(todo.priority) }}</span>
                    <span v-if="todo.due_date" class="todo-time">{{ formatDate(todo.due_date) }}</span>
                  </span>
                </div>
              </div>
            </div>
            <div v-else class="empty-tip">暂无待办，添加第一条吧 →</div>
          </div>

          <div class="panel">
            <div class="panel-header">
              <h3>✅ 习惯打卡</h3>
              <span class="panel-action">全部</span>
            </div>
            <div class="habit-ring">
              <svg class="ring-progress" viewBox="0 0 120 120">
                <circle class="ring-bg" cx="60" cy="60" r="50" />
                <circle class="ring-fg" cx="60" cy="60" r="50"
                  stroke-dasharray="314.16"
                  stroke-dashoffset="47.12" />
              </svg>
              <div class="ring-text">
                <span class="ring-value">85%</span>
                <span class="ring-label">完成率</span>
              </div>
            </div>
            <div class="habit-list">
              <div class="habit-item">
                <span class="habit-dot habit-done"></span>
                <span class="habit-name">早起</span>
                <span class="habit-status">已完成</span>
              </div>
              <div class="habit-item">
                <span class="habit-dot habit-done"></span>
                <span class="habit-name">喝水</span>
                <span class="habit-status">3/8 杯</span>
              </div>
              <div class="habit-item">
                <span class="habit-dot"></span>
                <span class="habit-name">阅读</span>
                <span class="habit-status">未开始</span>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useTodosStore } from '@/stores/todos'
import WeatherCard from '@/components/WeatherCard.vue'

const router = useRouter()
const authStore = useAuthStore()
const todosStore = useTodosStore()

const activeMenu = ref('dashboard')
const currentTime = ref('')
const currentDate = ref('')
const greeting = ref('')
const loadError = ref('')

let timer = null

const avatarLetter = computed(() => {
  const name = authStore.user?.username || 'U'
  return name.charAt(0).toUpperCase()
})

const todayTodos = computed(() => todosStore.todayTodos)
const activeCount = computed(() => todosStore.activeTodos.length)

const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { hour12: false })
  currentDate.value = now.toLocaleDateString('zh-CN', {
    year: 'numeric', month: 'long', day: 'numeric', weekday: 'long'
  })
  const hour = now.getHours()
  if (hour >= 6 && hour < 12) greeting.value = '🌅 早上好，新的一天开始了'
  else if (hour >= 12 && hour < 14) greeting.value = '☀️ 中午好，记得午休'
  else if (hour >= 14 && hour < 18) greeting.value = '📚 下午好，加油完成任务'
  else if (hour >= 18 && hour < 22) greeting.value = '🌇 晚上好，放松一下吧'
  else greeting.value = '🌙 夜深了，早点休息'
}

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}

const goToTodos = () => {
  router.push('/todos')
}

const toggleTodo = async (id) => {
  try {
    await todosStore.toggleTodo(id)
  } catch (e) {
    alert('操作失败: ' + (e.message || '未知错误'))
  }
}

const reloadTodos = async () => {
  try {
    await todosStore.fetchTodos()
    await todosStore.fetchTodayTodos()
    loadError.value = ''
  } catch (e) {
    loadError.value = e.message || '加载失败'
  }
}

const formatPriority = (p) => ({ high: '高', medium: '中', low: '低' })[p] || '中'
const formatDate = (d) => {
  if (!d) return ''
  const s = String(d)
  const m = s.match(/(\d{4})-(\d{1,2})-(\d{1,2})[ T](\d{1,2}):(\d{1,2}):(\d{1,2})/)
  if (m) {
    const year = m[1], month = m[2], day = m[3], hour = m[4], minute = m[5]
    const hh = hour.padStart(2, '0')
    const mm = minute.padStart(2, '0')
    const today = new Date()
    const isToday = String(today.getFullYear()) === year
      && String(today.getMonth()+1).padStart(2,'0') === month
      && String(today.getDate()).padStart(2,'0') === day
    if (isToday) return `今天 ${hh}:${mm}`
    return `${year}-${month.padStart(2,'0')}-${day.padStart(2,'0')} ${hh}:${mm}`
  }
  const dt = new Date(d)
  if (isNaN(dt.getTime())) return s
  const now = new Date()
  const isToday = dt.toDateString() === now.toDateString()
  if (isToday) {
    const hh = String(dt.getHours()).padStart(2, '0')
    const mm = String(dt.getMinutes()).padStart(2, '0')
    return `今天 ${hh}:${mm}`
  }
  const y = dt.getFullYear()
  const m2 = String(dt.getMonth() + 1).padStart(2, '0')
  const day2 = String(dt.getDate()).padStart(2, '0')
  const hh = String(dt.getHours()).padStart(2, '0')
  const mm = String(dt.getMinutes()).padStart(2, '0')
  return `${y}-${m2}-${day2} ${hh}:${mm}`
}

onMounted(async () => {
  authStore.loadUserFromStorage()
  updateTime()
  timer = setInterval(updateTime, 1000)
  try {
    await todosStore.fetchTodos()
    await todosStore.fetchTodayTodos()
    loadError.value = ''
  } catch (e) {
    loadError.value = e.message || '加载待办失败，请检查后端服务'
  }
})

onUnmounted(() => {
  if (timer) clearInterval(timer)
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  background: #f0f2f5;
  color: #1a1a2e;
  overflow: hidden;
}

.dashboard {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.navbar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px 28px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
  flex-shrink: 0;
  z-index: 10;
}

.logo { display: flex; align-items: center; gap: 12px; }
.logo-icon { font-size: 28px; }
.logo-text { font-size: 22px; font-weight: 700; color: white; letter-spacing: 1px; }

.nav-right { display: flex; align-items: center; gap: 16px; }
.user-info {
  display: flex; align-items: center; gap: 12px;
  background: rgba(255,255,255,0.15);
  padding: 8px 16px 8px 8px;
  border-radius: 40px;
  backdrop-filter: blur(10px);
}
.avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #8b5a2b; font-size: 16px;
}
.user-detail { display: flex; flex-direction: column; }
.user-name { color: white; font-weight: 600; font-size: 14px; line-height: 1.2; }
.user-role { color: rgba(255,255,255,0.8); font-size: 12px; }

.logout-btn {
  background: rgba(255,255,255,0.2);
  border: 1px solid rgba(255,255,255,0.3);
  color: white; padding: 8px 20px;
  border-radius: 20px; font-weight: 500;
  cursor: pointer; transition: all 0.2s; font-size: 13px;
}
.logout-btn:hover { background: rgba(255,255,255,0.3); transform: translateY(-1px); }

.main-layout { display: flex; flex: 1; overflow: hidden; }

.sidebar {
  width: 240px; background: white;
  border-right: 1px solid #eef0f5;
  display: flex; flex-direction: column;
  overflow-y: auto; flex-shrink: 0;
}
.side-nav { padding: 20px 0; }
.nav-section {
  padding: 16px 28px 8px;
  font-size: 11px; font-weight: 600;
  color: #a0aec0; text-transform: uppercase; letter-spacing: 1.5px;
}
.side-nav ul { list-style: none; }
.side-nav li {
  display: flex; align-items: center;
  padding: 12px 28px; cursor: pointer;
  color: #4a5568; transition: all 0.2s;
  position: relative; gap: 12px;
}
.side-nav li::before {
  content: ''; position: absolute; left: 0; top: 0; bottom: 0;
  width: 3px; background: transparent; transition: background 0.2s;
}
.side-nav li:hover { background: #f7fafc; color: #2d3748; }
.side-nav li.active {
  background: linear-gradient(90deg, #ebf4ff 0%, transparent 100%);
  color: #667eea; font-weight: 600;
}
.side-nav li.active::before { background: #667eea; }
.nav-icon { font-size: 18px; width: 24px; text-align: center; }
.nav-label { flex: 1; font-size: 14px; }
.nav-badge {
  background: #e53e3e; color: white;
  font-size: 11px; padding: 2px 8px;
  border-radius: 10px; font-weight: 600;
}

.content {
  flex: 1; padding: 28px;
  overflow-y: auto; background: #f5f7fa;
}
.page-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 24px;
}
.page-title h2 { font-size: 24px; color: #2d3748; font-weight: 700; margin-bottom: 4px; }
.page-subtitle { color: #718096; font-size: 14px; }
.page-actions { display: flex; gap: 12px; }

.load-error-banner {
  display: flex; align-items: center; justify-content: space-between;
  gap: 12px;
  background: #fff5f5; border: 1px solid #feb2b2;
  color: #c53030; padding: 12px 16px;
  border-radius: 10px; font-size: 14px; font-weight: 500;
  margin-bottom: 20px;
}
.btn-retry {
  background: #c53030; color: white; border: none;
  padding: 6px 14px; border-radius: 6px;
  font-weight: 600; cursor: pointer; font-size: 12px;
}
.btn-retry:hover { background: #9b2c2c; }
.btn-ghost {
  width: 40px; height: 40px; border: none;
  background: white; border-radius: 10px;
  cursor: pointer; font-size: 18px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  transition: all 0.2s;
}
.btn-ghost:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

.stats-row {
  display: grid; grid-template-columns: repeat(4, 1fr);
  gap: 20px; margin-bottom: 24px;
}
.stat-card {
  background: white; border-radius: 16px; padding: 20px;
  display: flex; align-items: center; gap: 16px;
  position: relative; overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: transform 0.2s, box-shadow 0.2s;
}
.stat-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }

.stat-icon-wrap {
  width: 52px; height: 52px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  font-size: 24px;
}
.stat-icon-1 { background: linear-gradient(135deg, #667eea, #764ba2); }
.stat-icon-2 { background: linear-gradient(135deg, #11998e, #38ef7d); }
.stat-icon-3 { background: linear-gradient(135deg, #f093fb, #f5576c); }
.stat-icon-4 { background: linear-gradient(135deg, #4facfe, #00f2fe); }

.stat-info { display: flex; flex-direction: column; flex: 1; }
.stat-value { font-size: 26px; font-weight: 700; color: #2d3748; line-height: 1.1; }
.stat-label { font-size: 13px; color: #718096; margin-top: 2px; }
.stat-trend { font-size: 12px; font-weight: 600; padding: 4px 8px; border-radius: 8px; }
.stat-trend.up { color: #38a169; background: #c6f6d5; }
.stat-trend.down { color: #e53e3e; background: #fed7d7; }

.content-row {
  display: grid; grid-template-columns: 1fr 1fr;
  gap: 20px; margin-bottom: 24px;
}
.panel {
  background: white; border-radius: 16px; padding: 24px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
}
.panel-header {
  display: flex; justify-content: space-between;
  align-items: center; margin-bottom: 20px;
}
.panel-header h3 { font-size: 16px; color: #2d3748; font-weight: 600; }
.panel-action { font-size: 13px; color: #667eea; cursor: pointer; font-weight: 500; }
.panel-action:hover { text-decoration: underline; }

.clock-display { display: flex; flex-direction: column; align-items: center; padding: 20px 0; }
.clock-time {
  font-size: 48px; font-weight: 700; color: #2d3748;
  font-variant-numeric: tabular-nums; letter-spacing: 2px;
}
.clock-date { font-size: 15px; color: #718096; margin-top: 4px; }
.clock-greeting { font-size: 14px; color: #667eea; margin-top: 12px; font-weight: 500; }

.weather-display { display: flex; flex-direction: column; gap: 12px; }
.weather-main { display: flex; align-items: center; gap: 16px; }
.weather-icon { font-size: 48px; }
.weather-temp { font-size: 36px; font-weight: 700; color: #2d3748; }
.weather-detail { display: flex; justify-content: space-between; align-items: center; }
.weather-city { font-size: 16px; font-weight: 600; color: #2d3748; }
.weather-desc { font-size: 14px; color: #718096; }
.weather-extra { display: flex; gap: 24px; padding-top: 12px; border-top: 1px solid #edf2f7; }
.weather-item { display: flex; flex-direction: column; gap: 2px; }
.wi-label { font-size: 12px; color: #a0aec0; }
.wi-value { font-size: 14px; font-weight: 600; color: #4a5568; }

.todo-list { display: flex; flex-direction: column; gap: 12px; }
.todo-item {
  display: flex; align-items: center; gap: 14px;
  padding: 14px 16px; background: #f7fafc;
  border-radius: 12px; transition: background 0.2s;
}
.todo-item:hover { background: #edf2f7; }
.todo-checkbox {
  width: 22px; height: 22px; border: 2px solid #cbd5e0;
  border-radius: 6px; display: flex; align-items: center; justify-content: center;
  flex-shrink: 0; font-size: 12px; color: white; transition: all 0.2s;
}
.todo-checkbox.checked { background: #38a169; border-color: #38a169; }
.todo-content { flex: 1; display: flex; flex-direction: column; gap: 4px; }
.todo-title { font-size: 14px; color: #2d3748; font-weight: 500; }
.todo-title.done { text-decoration: line-through; color: #a0aec0; }
.todo-meta { display: flex; align-items: center; gap: 10px; }
.priority-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 600; }
.priority-high { background: #fed7d7; color: #c53030; }
.priority-medium { background: #feebc8; color: #dd6b20; }
.priority-low { background: #c6f6d5; color: #38a169; }
.todo-time { font-size: 12px; color: #a0aec0; }

.empty-tip {
  text-align: center; padding: 30px 0;
  font-size: 14px; color: #a0aec0;
}

.habit-ring { position: relative; display: flex; align-items: center; justify-content: center; margin: 16px 0; }
.ring-progress { width: 140px; height: 140px; transform: rotate(-90deg); }
.ring-bg { fill: none; stroke: #edf2f7; stroke-width: 10; }
.ring-fg { fill: none; stroke: #667eea; stroke-width: 10; stroke-linecap: round; }
.ring-text { position: absolute; text-align: center; }
.ring-value { display: block; font-size: 32px; font-weight: 700; color: #2d3748; }
.ring-label { font-size: 12px; color: #a0aec0; }

.habit-list { display: flex; flex-direction: column; gap: 10px; padding-top: 12px; border-top: 1px solid #edf2f7; }
.habit-item { display: flex; align-items: center; gap: 12px; padding: 8px 0; }
.habit-dot { width: 10px; height: 10px; border-radius: 50%; background: #e2e8f0; }
.habit-dot.habit-done { background: #38a169; }
.habit-name { flex: 1; font-size: 14px; color: #2d3748; font-weight: 500; }
.habit-status { font-size: 12px; color: #a0aec0; }

.weather-panel {
  padding: 0;
  overflow: hidden;
  background: transparent;
  box-shadow: none;
}

.weather-panel > :deep(.weather-card) {
  border-radius: 16px;
}

@media (max-width: 1024px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .content-row { grid-template-columns: 1fr; }
}
@media (max-width: 768px) {
  .sidebar { width: 64px; }
  .nav-label, .nav-section, .nav-badge { display: none; }
  .side-nav li { padding: 16px 0; justify-content: center; }
}
</style>
