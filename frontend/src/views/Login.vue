<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <h1>📊 LifeDash</h1>
        <p>登录您的数字生活</p>
      </div>
      <form @submit.prevent="handleLogin" class="auth-form">
        <div class="input-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            required
            :disabled="loading"
          />
        </div>
        <div class="input-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            required
            :disabled="loading"
          />
        </div>
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '登录中...' : '登 录' }}
        </button>
        <p class="switch-link">
          还没有账号？<router-link to="/register">立即注册</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')

const handleLogin = async () => {
  errorMsg.value = ''
  loading.value = true
  try {
    await authStore.login(form.value)
    router.push('/dashboard')
  } catch (err) {
    errorMsg.value = err.message || '登录失败，请检查账号和密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-family: 'Segoe UI', sans-serif;
}

.auth-card {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 24px;
  padding: 48px 40px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.2);
  transition: transform 0.3s ease;
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.auth-header h1 {
  font-size: 32px;
  color: #2d3748;
  margin-bottom: 8px;
}

.auth-header p {
  color: #718096;
  font-size: 16px;
}

.input-group {
  margin-bottom: 20px;
}

.input-group label {
  display: block;
  font-weight: 600;
  color: #2d3748;
  margin-bottom: 6px;
  font-size: 14px;
}

.input-group input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  font-size: 16px;
  transition: border-color 0.2s;
  background: white;
}

.input-group input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2);
}

.input-group input:disabled {
  background: #f7fafc;
  cursor: not-allowed;
}

.btn-primary {
  width: 100%;
  padding: 14px;
  background: #667eea;
  border: none;
  border-radius: 12px;
  color: white;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  background: #5a67d8;
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  display: inline-block;
  width: 18px;
  height: 18px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-msg {
  background: #fed7d7;
  color: #c53030;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 16px;
  border-left: 4px solid #e53e3e;
}

.switch-link {
  text-align: center;
  margin-top: 20px;
  color: #4a5568;
}

.switch-link a {
  color: #667eea;
  font-weight: 600;
  text-decoration: none;
}

.switch-link a:hover {
  text-decoration: underline;
}
</style>
