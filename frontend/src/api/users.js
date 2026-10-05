import api from './client'

export const fetchUsers = (params = {}) => api.get('/users', { params })