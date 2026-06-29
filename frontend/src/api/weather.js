import request from './request'

export const getNowWeather = (location = 'beijing') => {
  return request.get('/weather/now', { params: { location } })
}

export const getForecast = (location = 'beijing', days = 3) => {
  return request.get('/weather/forecast', { params: { location, days } })
}

export const searchCity = (keyword) => {
  return request.get('/weather/city', { params: { keyword } })
}

export const saveUserCity = (cityCode, cityName) => {
  return request.post('/weather/city', null, {
    params: { city_code: cityCode, city_name: cityName }
  })
}

export const getUserCities = () => {
  return request.get('/weather/cities')
}

export const addUserCity = (cityCode, cityName) => {
  return request.post('/weather/cities', null, {
    params: { city_code: cityCode, city_name: cityName }
  })
}

export const deleteUserCity = (cityCode) => {
  return request.delete(`/weather/cities/${cityCode}`)
}

export const setDefaultCity = (cityCode) => {
  return request.put(`/weather/cities/${cityCode}/default`)
}
