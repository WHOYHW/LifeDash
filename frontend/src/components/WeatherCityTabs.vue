<template>
  <div class="city-tabs">
    <div class="tabs-container">
      <div 
        v-for="city in store.savedCities" 
        :key="city.city_code"
        class="city-tab"
        :class="{ active: city.city_code === store.currentCity }"
      >
        <span class="tab-name" @click="handleSwitch(city)">{{ city.city_name }}</span>
        <span v-if="city.is_default" class="tab-default-star" title="默认城市">⭐</span>
        <span 
          class="tab-action" 
          :title="city.is_default ? '已是默认城市' : '设为默认'"
          @click.stop="handleSetDefault(city)"
        >
          ⭐
        </span>
        <span 
          class="tab-delete" 
          title="删除"
          @click.stop="handleDelete(city)"
        >
          ×
        </span>
      </div>
      <button class="add-tab" title="添加城市到收藏" @click="showAddModal = true">＋</button>
    </div>

    <div class="current-city-info">
      <span class="info-item">📍 当前：{{ store.currentCityName }}</span>
      <span v-if="defaultCityName" class="info-item default">⭐ 默认：{{ defaultCityName }}</span>
    </div>

    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal">
          <div class="modal-header">
            <h3>添加城市到收藏</h3>
            <button class="close-btn" @click="showAddModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="current-weather-info">
              <span>当前城市：{{ store.currentCityName }}</span>
              <button 
                v-if="!isCurrentCitySaved" 
                class="save-current-btn"
                @click="saveCurrentCity"
              >
                ⭐ 收藏当前城市
              </button>
              <span v-else class="already-saved">✓ 已收藏</span>
            </div>

            <div class="divider">或搜索其他城市</div>
            
            <input 
              v-model="searchKeyword" 
              type="text" 
              placeholder="输入城市名，如：上海、广州、深圳"
              class="search-input"
              @keyup.enter="searchAndAdd"
              :disabled="searching"
            />
            <button 
              class="search-btn" 
              @click="searchAndAdd"
              :disabled="searching || !searchKeyword.trim()"
            >
              {{ searching ? '搜索中...' : '搜索' }}
            </button>

            <div v-if="searchError" class="error-msg">{{ searchError }}</div>
            
            <div v-if="searchResult" class="search-result">
              <div class="result-item">
                <span class="result-name">{{ searchResult.name }}</span>
                <span class="result-path">{{ searchResult.path }}</span>
                <button class="add-btn" @click="confirmAdd">＋ 添加</button>
              </div>
            </div>

            <div class="quick-cities">
              <div class="quick-label">🔥 热门城市</div>
              <div class="quick-list">
                <span 
                  v-for="city in quickCities" 
                  :key="city.code" 
                  class="quick-item"
                  @click="quickAdd(city)"
                >
                  {{ city.name }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="showConfirmDelete" class="modal-overlay" @click.self="showConfirmDelete = false">
        <div class="modal small-modal">
          <div class="modal-header">
            <h3>确认删除</h3>
          </div>
          <div class="modal-body">
            <p>确定要从收藏中删除"{{ cityToDelete?.city_name }}"吗？</p>
            <div class="modal-actions">
              <button class="btn-cancel" @click="showConfirmDelete = false">取消</button>
              <button class="btn-confirm" @click="confirmDelete">删除</button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWeatherStore } from '../stores/weather'
import { searchCity } from '../api/weather'

const store = useWeatherStore()

const showAddModal = ref(false)
const showConfirmDelete = ref(false)
const searchKeyword = ref('')
const searching = ref(false)
const searchError = ref(null)
const searchResult = ref(null)
const cityToDelete = ref(null)

const quickCities = [
  { code: 'beijing', name: '北京' },
  { code: 'shanghai', name: '上海' },
  { code: 'guangzhou', name: '广州' },
  { code: 'shenzhen', name: '深圳' },
  { code: 'hangzhou', name: '杭州' },
  { code: 'chengdu', name: '成都' },
  { code: 'xian', name: '西安' },
  { code: 'nanjing', name: '南京' }
]

const defaultCityName = computed(() => {
  const defaultCity = store.savedCities.find(c => c.is_default)
  return defaultCity?.city_name || ''
})

const isCurrentCitySaved = computed(() => {
  return store.savedCities.some(c => c.city_code === store.currentCity)
})

const handleSwitch = async (city) => {
  await store.switchCity(city.city_code, city.city_name)
}

const handleSetDefault = async (city) => {
  if (!city.is_default) {
    try {
      await store.markAsDefault(city.city_code)
    } catch (e) {
      alert(e.message || '设置默认城市失败')
    }
  }
}

const handleDelete = (city) => {
  cityToDelete.value = city
  showConfirmDelete.value = true
}

const confirmDelete = async () => {
  if (cityToDelete.value) {
    try {
      await store.removeCity(cityToDelete.value.city_code)
    } catch (e) {
      alert(e.message || '删除失败')
    }
    showConfirmDelete.value = false
    cityToDelete.value = null
  }
}

const saveCurrentCity = async () => {
  try {
    const res = await searchCity(store.currentCityName)
    if (res.data) {
      await store.addCity(res.data.code, res.data.name)
      alert(`已收藏 ${res.data.name}！`)
    }
  } catch (e) {
    alert(e.message || '收藏失败')
  }
}

const searchAndAdd = async () => {
  if (!searchKeyword.value.trim()) return
  
  searching.value = true
  searchError.value = null
  searchResult.value = null
  
  try {
    const res = await searchCity(searchKeyword.value.trim())
    searchResult.value = res.data
  } catch (e) {
    searchError.value = '未找到该城市'
  } finally {
    searching.value = false
  }
}

const confirmAdd = async () => {
  if (searchResult.value) {
    try {
      await store.addCity(searchResult.value.code, searchResult.value.name)
      showAddModal.value = false
      searchKeyword.value = ''
      searchResult.value = null
      searchError.value = null
    } catch (e) {
      alert(e.message || '添加失败')
    }
  }
}

const quickAdd = async (city) => {
  try {
    const res = await searchCity(city.name)
    if (res.data) {
      await store.addCity(res.data.code, res.data.name)
    }
  } catch (e) {
    alert(e.message || '添加失败')
  }
}

onMounted(async () => {
  await store.loadSavedCities()
})
</script>

<style scoped>
.city-tabs {
  width: 100%;
}

.tabs-container {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 10px;
}

.city-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px 6px 12px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  transition: all 0.2s;
  font-size: 13px;
  color: white;
}

.city-tab:hover {
  background: rgba(255, 255, 255, 0.3);
}

.city-tab.active {
  background: white;
  color: #667eea;
  font-weight: 600;
}

.tab-name {
  font-weight: 500;
  cursor: pointer;
}

.tab-default-star {
  font-size: 12px;
  filter: drop-shadow(0 0 2px rgba(255, 200, 0, 0.8));
}

.tab-action {
  opacity: 0.7;
  cursor: pointer;
  font-size: 12px;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.tab-action:hover {
  opacity: 1;
  background: rgba(255, 255, 255, 0.3);
}

.city-tab.active .tab-action:hover {
  background: rgba(102, 126, 234, 0.15);
}

.tab-delete {
  opacity: 0.6;
  font-size: 14px;
  margin-left: 2px;
  line-height: 1;
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.2s;
}

.tab-delete:hover {
  opacity: 1;
  background: rgba(255, 0, 0, 0.2);
}

.add-tab {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  background: rgba(255, 255, 255, 0.2);
  border: 2px dashed rgba(255, 255, 255, 0.5);
  border-radius: 50%;
  color: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
}

.add-tab:hover {
  background: rgba(255, 255, 255, 0.35);
  transform: scale(1.1);
}

.current-city-info {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.info-item {
  background: rgba(255, 255, 255, 0.15);
  padding: 4px 10px;
  border-radius: 12px;
}

.info-item.default {
  background: rgba(255, 193, 7, 0.3);
  color: white;
}

.current-weather-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 10px;
  margin-bottom: 16px;
}

.save-current-btn {
  padding: 6px 14px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 8px;
  color: white;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.save-current-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.already-saved {
  color: #38a169;
  font-weight: 600;
}

.divider {
  text-align: center;
  color: #999;
  font-size: 13px;
  margin: 16px 0;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 30%;
  height: 1px;
  background: #e0e0e0;
}

.divider::before { left: 0; }
.divider::after { right: 0; }

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 400px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal.small-modal {
  max-width: 320px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0 8px;
  line-height: 1;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.search-input {
  width: calc(100% - 100px);
  padding: 10px 14px;
  border: 2px solid #e8e8e8;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #667eea;
}

.search-btn {
  width: 90px;
  padding: 10px;
  margin-left: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 10px;
  color: white;
  font-size: 14px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.search-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.search-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-msg {
  margin-top: 10px;
  padding: 10px;
  background: #fff2f0;
  color: #f5222d;
  border-radius: 8px;
  font-size: 14px;
}

.search-result {
  margin-top: 15px;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 10px;
}

.result-name {
  flex: 1;
  font-size: 15px;
  color: #333;
  font-weight: 500;
}

.result-path {
  font-size: 12px;
  color: #999;
  margin-right: 10px;
}

.add-btn {
  padding: 6px 14px;
  background: #667eea;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 13px;
  cursor: pointer;
}

.add-btn:hover {
  background: #5a67d8;
}

.quick-cities {
  margin-top: 20px;
  padding-top: 15px;
  border-top: 1px solid #f0f0f0;
}

.quick-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.quick-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-item {
  padding: 6px 14px;
  background: #f5f5f5;
  border-radius: 16px;
  cursor: pointer;
  font-size: 14px;
  color: #333;
  transition: all 0.2s;
}

.quick-item:hover {
  background: #667eea;
  color: white;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 20px;
}

.btn-cancel {
  padding: 8px 20px;
  background: #f0f0f0;
  border: none;
  border-radius: 8px;
  color: #333;
  cursor: pointer;
  font-size: 14px;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-confirm {
  padding: 8px 20px;
  background: #e53e3e;
  border: none;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  font-size: 14px;
}

.btn-confirm:hover {
  background: #c53030;
}
</style>
