import request from './request'

export const todoApi = {
  create: (data) => request.post('/todos', data),
  list: (params) => request.get('/todos', { params }),
  get: (id) => request.get(`/todos/${id}`),
  update: (id, data) => request.put(`/todos/${id}`, data),
  toggle: (id) => request.patch(`/todos/${id}/toggle`),
  delete: (id) => request.delete(`/todos/${id}`),
  today: () => request.get('/todos/today'),
}
