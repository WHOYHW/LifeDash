<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <div class="auth-header">
        <h1>📊 LifeDash</h1>
        <p>创建你的专属数字看板</p>
      </div>
      <form @submit.prevent="handleRegister" class="auth-form">
        <div class="input-group">
          <label>用户名</label>
          <input
            v-model="form.username"
            type="text"
            placeholder="3-20位，字母开头"
            required
            :disabled="loading"
          />
        </div>
        <div class="input-group">
          <label>邮箱</label>
          <input
            v-model="form.email"
            type="email"
            placeholder="example@email.com"
            required
            :disabled="loading"
          />
        </div>
        <div class="input-group">
          <label>密码</label>
          <input
            v-model="form.password"
            type="password"
            placeholder="8-32位，含字母和数字"
            required
            :disabled="loading"
          />
        </div>
        <div v-if="errorMsg" class="error-msg">{{ errorMsg }}</div>
        <div v-if="successMsg" class="success-msg">{{ successMsg }}</div>
        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          {{ loading ? '注册中...' : '注 册' }}
        </button>
        <p class="switch-link">
          已有账号？<router-link to="/login">去登录</router-link>
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

const form = ref({ username: '', email: '', password: '' })
const loading = ref(false)
const errorMsg = ref('')
const successMsg = ref('')

const handleRegister = async () => {
  errorMsg.value = ''
  successMsg.value = ''
  loading.value = true
  try {
    await authStore.register(form.value)
    successMsg.value = '🎉 注册成功！正在跳转到登录页...'
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    errorMsg.value = err.message || '注册失败，请检查输入信息'
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

.success-msg {
  background: #c6f6d5;
  color: #276749;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 16px;
  border-left: 4px solid #38a169;
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
