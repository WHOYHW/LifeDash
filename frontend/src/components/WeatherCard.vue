<template>
  <div class="weather-card" :class="{ 'weather-hot': store.isHot, 'weather-cold': store.isCold }">
    <div v-if="store.loading && !store.nowWeather" class="weather-loading">
      <div class="spinner"></div>
      <span>加载天气中...</span>
    </div>
    
    <div v-else-if="store.error" class="weather-error">
      <span class="error-icon">⚠️</span>
      <span>{{ store.error }}</span>
      <button class="retry-btn" @click="retry">重试</button>
    </div>
    
    <template v-else-if="store.nowWeather">
      <div class="weather-header">
        <WeatherCityTabs />
      </div>
      
      <div class="weather-main">
        <div class="weather-icon">
          {{ weatherIcon }}
        </div>
        <div class="weather-info">
          <div class="temp">{{ store.nowWeather.temp }}°<span class="temp-unit">C</span></div>
          <div class="weather-text">{{ store.nowWeather.text }}</div>
        </div>
        <div class="weather-details">
          <div class="detail-item">
            <span class="detail-icon">💧</span>
            <span class="detail-value">{{ store.nowWeather.humidity || '--' }}%</span>
            <span class="detail-label">湿度</span>
          </div>
          <div class="detail-item">
            <span class="detail-icon">🌬️</span>
            <span class="detail-value">{{ store.nowWeather.wind_scale || '--' }}</span>
            <span class="detail-label">风力</span>
          </div>
        </div>
      </div>
      
      <div v-if="store.forecast.length > 0" class="weather-forecast">
        <div 
          v-for="(day, index) in store.forecast" 
          :key="index" 
          class="forecast-item"
          :class="{ 'today': index === 0 }"
        >
          <div class="forecast-date">{{ formatDate(day.date, index) }}</div>
          <div class="forecast-icon">{{ getForecastIcon(day.text_day) }}</div>
          <div class="forecast-text">{{ day.text_day }}</div>
          <div class="forecast-temp">
            <span class="temp-max">{{ day.temp_max }}°</span>
            <span class="temp-sep">/</span>
            <span class="temp-min">{{ day.temp_min }}°</span>
          </div>
        </div>
      </div>
    </template>
    
    <div v-else class="weather-empty">
      <span>暂无天气数据</span>
      <button class="retry-btn" @click="retry">加载</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useWeatherStore } from '../stores/weather'
import WeatherCityTabs from './WeatherCityTabs.vue'

const store = useWeatherStore()

const weatherIcon = computed(() => {
  const text = store.nowWeather.value?.text || ''
  if (text.includes('晴')) return '☀️'
  if (text.includes('多云')) return '⛅'
  if (text.includes('阴')) return '☁️'
  if (text.includes('雷阵雨')) return '⛈️'
  if (text.includes('雨')) return '🌧️'
  if (text.includes('雪')) return '❄️'
  if (text.includes('雾')) return '🌫️'
  if (text.includes('风')) return '🌬️'
  return '🌤️'
})

const getForecastIcon = (text) => {
  if (!text) return '🌤️'
  if (text.includes('晴')) return '☀️'
  if (text.includes('多云')) return '⛅'
  if (text.includes('阴')) return '☁️'
  if (text.includes('雷阵雨')) return '⛈️'
  if (text.includes('雨')) return '🌧️'
  if (text.includes('雪')) return '❄️'
  return '🌤️'
}

const formatDate = (dateStr, index) => {
  if (index === 0) return '今天'
  if (index === 1) return '明天'
  if (index === 2) return '后天'
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return `${d.getMonth() + 1}/${d.getDate()}`
}

const retry = () => {
  store.clearError()
  store.fetchWeather()
}

onMounted(() => {
  if (!store.nowWeather) {
    store.fetchWeather()
  }
})
</script>

<style scoped>
.weather-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 20px;
  color: white;
  position: relative;
  overflow: hidden;
  transition: all 0.3s ease;
}

.weather-card.weather-hot {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.weather-card.weather-cold {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.weather-header {
  margin-bottom: 15px;
}

.weather-main {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.weather-icon {
  font-size: 60px;
  line-height: 1;
}

.weather-info {
  flex: 1;
}

.temp {
  font-size: 48px;
  font-weight: 700;
  line-height: 1;
}

.temp-unit {
  font-size: 24px;
  font-weight: 400;
}

.weather-text {
  font-size: 16px;
  margin-top: 5px;
  opacity: 0.9;
}

.weather-details {
  display: flex;
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 12px;
  border-radius: 10px;
  min-width: 55px;
}

.detail-icon {
  font-size: 16px;
  margin-bottom: 2px;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
}

.detail-label {
  font-size: 11px;
  opacity: 0.7;
}

.weather-forecast {
  display: flex;
  gap: 10px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 12px;
}

.forecast-item {
  flex: 1;
  text-align: center;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.forecast-item.today {
  background: rgba(255, 255, 255, 0.25);
}

.forecast-date {
  font-size: 12px;
  opacity: 0.8;
  margin-bottom: 5px;
}

.forecast-icon {
  font-size: 28px;
  margin-bottom: 5px;
}

.forecast-text {
  font-size: 12px;
  margin-bottom: 5px;
  opacity: 0.9;
}

.forecast-temp {
  font-size: 12px;
}

.temp-max {
  font-weight: 600;
}

.temp-sep {
  margin: 0 2px;
  opacity: 0.6;
}

.temp-min {
  opacity: 0.7;
}

.weather-loading,
.weather-error,
.weather-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 10px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 20px;
  background: rgba(255, 255, 255, 0.25);
  border: none;
  border-radius: 20px;
  color: white;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.2s;
}

.retry-btn:hover {
  background: rgba(255, 255, 255, 0.35);
}

.error-icon {
  font-size: 32px;
}
</style>
