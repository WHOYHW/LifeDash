import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  getNowWeather, 
  getForecast, 
  searchCity, 
  saveUserCity,
  getUserCities,
  addUserCity,
  deleteUserCity,
  setDefaultCity
} from '../api/weather'

export const useWeatherStore = defineStore('weather', () => {
  const currentCity = ref(localStorage.getItem('weather_city') || 'beijing')
  const currentCityName = ref(localStorage.getItem('weather_city_name') || '北京')
  const nowWeather = ref(null)
  const forecast = ref([])
  const loading = ref(false)
  const error = ref(null)
  const savedCities = ref([])

  const isHot = computed(() => nowWeather.value && nowWeather.value.temp >= 30)
  const isCold = computed(() => nowWeather.value && nowWeather.value.temp <= 5)

  const fetchWeather = async (location = null) => {
    const loc = location || currentCity.value
    loading.value = true
    error.value = null
    try {
      const [nowRes, forecastRes] = await Promise.all([
        getNowWeather(loc),
        getForecast(loc, 3)
      ])
      nowWeather.value = nowRes.data
      forecast.value = forecastRes.data
    } catch (e) {
      error.value = e.message || '获取天气失败'
    } finally {
      loading.value = false
    }
  }

  const loadSavedCities = async () => {
    try {
      const res = await getUserCities()
      savedCities.value = res.data || []
      if (savedCities.value.length > 0) {
        const defaultCity = savedCities.value.find(c => c.is_default)
        if (defaultCity && defaultCity.city_code !== currentCity.value) {
          await switchCity(defaultCity.city_code, defaultCity.city_name)
        }
      }
    } catch (e) {
      console.error('加载收藏城市失败:', e)
      savedCities.value = []
    }
  }

  const addCity = async (cityCode, cityName) => {
    try {
      const res = await addUserCity(cityCode, cityName)
      await loadSavedCities()
      return res.data
    } catch (e) {
      throw e
    }
  }

  const removeCity = async (cityCode) => {
    try {
      await deleteUserCity(cityCode)
      await loadSavedCities()
      if (currentCity.value === cityCode) {
        if (savedCities.value.length > 0) {
          const defaultCity = savedCities.value.find(c => c.is_default) || savedCities.value[0]
          await switchCity(defaultCity.city_code, defaultCity.city_name)
        }
      }
    } catch (e) {
      throw e
    }
  }

  const markAsDefault = async (cityCode) => {
    try {
      const res = await setDefaultCity(cityCode)
      await loadSavedCities()
      return res.data
    } catch (e) {
      throw e
    }
  }

  const switchCity = async (cityCode, cityName) => {
    currentCity.value = cityCode
    currentCityName.value = cityName
    localStorage.setItem('weather_city', cityCode)
    localStorage.setItem('weather_city_name', cityName)
    await fetchWeather(cityCode)
  }

  const searchAndSetCity = async (keyword) => {
    loading.value = true
    error.value = null
    try {
      const res = await searchCity(keyword)
      const cityData = res.data
      currentCity.value = cityData.code
      currentCityName.value = cityData.name
      localStorage.setItem('weather_city', cityData.code)
      localStorage.setItem('weather_city_name', cityData.name)
      await fetchWeather(cityData.code)
      return cityData
    } catch (e) {
      error.value = e.message || '城市搜索失败'
      return null
    } finally {
      loading.value = false
    }
  }

  const setCity = async (cityCode, cityName) => {
    currentCity.value = cityCode
    currentCityName.value = cityName
    localStorage.setItem('weather_city', cityCode)
    localStorage.setItem('weather_city_name', cityName)
    await fetchWeather(cityCode)
  }

  const clearError = () => {
    error.value = null
  }

  return {
    currentCity,
    currentCityName,
    nowWeather,
    forecast,
    loading,
    error,
    savedCities,
    isHot,
    isCold,
    fetchWeather,
    loadSavedCities,
    addCity,
    removeCity,
    markAsDefault,
    switchCity,
    searchAndSetCity,
    setCity,
    clearError
  }
})
