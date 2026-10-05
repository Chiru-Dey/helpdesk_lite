import api from './client'

export const fetchUsers = (params = {}) => api.get('/users', { params })
export const createUser = (payload) => api.post('/users', payload)
export const updateUser = (id, payload) => api.patch(`/users/${id}`, payload)
export const deleteUser = (id) => api.delete(`/users/${id}`)