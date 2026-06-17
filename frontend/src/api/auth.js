import request from './request'

export const authApi = {
  register: (data) => request.post('/auth/register', data),
  login: (data) => request.post('/auth/login', data),
  getMe: () => request.get('/auth/me'),
  logout: () => request.post('/auth/logout'),
}
