import axios from 'axios'

// ========== 全局加载动画管理器 ==========
class LoadingManager {
  constructor() {
    this.count = 0
    this.loadingEl = null
    this.styleEl = null
    this.initStyles()
  }

  initStyles() {
    this.styleEl = document.createElement('style')
    this.styleEl.textContent = `
      .global-loading-mask {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.2);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        transition: opacity 0.2s ease;
      }
      .global-loading-mask.hidden {
        opacity: 0;
        pointer-events: none;
      }
      .global-loading-spinner {
        width: 48px;
        height: 48px;
        border: 4px solid #e0e0e0;
        border-top-color: #409eff;
        border-radius: 50%;
        animation: loading-spin 0.8s linear infinite;
      }
      .global-loading-text {
        margin-top: 16px;
        color: #606266;
        font-size: 14px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      .global-loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
      }
      @keyframes loading-spin {
        to { transform: rotate(360deg); }
      }
    `
    document.head.appendChild(this.styleEl)
  }

  show(text = '加载中...') {
    if (this.count === 0) {
      this.loadingEl = document.createElement('div')
      this.loadingEl.className = 'global-loading-mask'
      this.loadingEl.innerHTML = `
        <div class="global-loading-container">
          <div class="global-loading-spinner"></div>
          <div class="global-loading-text">${text}</div>
        </div>
      `
      document.body.appendChild(this.loadingEl)
    }
    this.count++
  }

  hide() {
    this.count--
    if (this.count <= 0) {
      this.count = 0
      if (this.loadingEl) {
        this.loadingEl.classList.add('hidden')
        setTimeout(() => {
          if (this.loadingEl && this.loadingEl.parentNode) {
            this.loadingEl.parentNode.removeChild(this.loadingEl)
          }
        }, 200)
      }
    }
  }
}

const loadingManager = new LoadingManager()

// ========== Axios 实例封装 ==========
const request = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器：添加Token + 显示加载动画
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    if (!config.silent) {
      loadingManager.show(config.loadingText || '加载中...')
    }
    return config
  },
  (error) => {
    loadingManager.hide()
    return Promise.reject(error)
  }
)

// 响应拦截器：处理业务逻辑 + 隐藏加载动画
request.interceptors.response.use(
  (response) => {
    if (!response.config.silent) {
      loadingManager.hide()
    }
    const res = response.data
    if (res.code !== 200 && res.code !== 201) {
      const err = new Error(res.message || '请求失败')
      err.businessError = true
      return Promise.reject(err)
    }
    return res
  },
  (error) => {
    if (!error.config?.silent) {
      loadingManager.hide()
    }
    if (error.response) {
      const { status, data } = error.response
      if (status === 401) {
        const hasToken = !!localStorage.getItem('token')
        if (hasToken) {
          localStorage.removeItem('token')
          localStorage.removeItem('user')
          if (window.location.hash !== '#/login' && window.location.hash !== '#/register') {
            alert('登录已过期，请重新登录')
            window.location.href = '/#/login'
          }
        }
        const msg = data?.detail || data?.message || '用户名或密码错误'
        return Promise.reject(new Error(msg))
      }
      const msg = data?.message || (Array.isArray(data?.detail)
        ? data.detail.map(d => d.msg).join('; ')
        : data?.detail) || `请求失败 (${status})`
      return Promise.reject(new Error(msg))
    }
    if (error.code === 'ECONNABORTED') {
      return Promise.reject(new Error('请求超时，请稍后重试'))
    }
    return Promise.reject(new Error('网络错误，请检查后端服务是否启动'))
  }
)

export default request