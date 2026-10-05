import api from './client'

export const fetchTickets = (params = {}) => api.get('/tickets', { params })

export const fetchTicket = (id) => api.get(`/tickets/${id}`)

export const createTicket = (payload) => api.post('/tickets', payload)

export const updateTicket = (id, payload) => api.patch(`/tickets/${id}`, payload)

export const updateTicketStatus = (id, status) =>
  api.post(`/tickets/${id}/status`, { status })

export const assignTicket = (id, assigneeId) =>
  api.post(`/tickets/${id}/assign`, { assignee_id: assigneeId })

export const fetchComments = (ticketId) => api.get(`/tickets/${ticketId}/comments`)

export const addComment = (ticketId, body) =>
  api.post(`/tickets/${ticketId}/comments`, { body })