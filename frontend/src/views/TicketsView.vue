<template>
  <div>
    <div class="page-header">
      <h1>Tickets</h1>
      <button class="btn" @click="router.push('/tickets/new')">New Ticket</button>
    </div>

    <div class="filters">
      <label for="statusFilter">Status</label>
      <select id="statusFilter" v-model="statusFilter" @change="loadTickets">
        <option value="">All</option>
        <option value="open">Open</option>
        <option value="in_progress">In Progress</option>
        <option value="resolved">Resolved</option>
        <option value="closed">Closed</option>
      </select>
    </div>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <p v-if="loading">Loading tickets...</p>

    <table v-else-if="tickets.length" class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Subject</th>
          <th>Status</th>
          <th>Priority</th>
          <th>Category</th>
          <th>Assignee</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="ticket in tickets"
          :key="ticket.id"
          @click="router.push(`/tickets/${ticket.id}`)"
        >
          <td>{{ ticket.id }}</td>
          <td>{{ ticket.subject }}</td>
          <td>
            <span :class="['badge', `badge-${ticket.status}`]">{{ formatStatus(ticket.status) }}</span>
          </td>
          <td>
            <span :class="['badge', `badge-priority-${ticket.priority}`]">{{ ticket.priority }}</span>
          </td>
          <td>{{ ticket.category ? ticket.category.name : '-' }}</td>
          <td>{{ ticket.assignee ? ticket.assignee.name : 'Unassigned' }}</td>
        </tr>
      </tbody>
    </table>

    <p v-else class="empty-state">No tickets found.</p>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchTickets } from '../api/tickets'

const router = useRouter()

const tickets = ref([])
const loading = ref(true)
const errorMessage = ref('')
const statusFilter = ref('')

const formatStatus = (status) => status.replace('_', ' ')

const loadTickets = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const params = {}
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    const { data } = await fetchTickets(params)
    tickets.value = data.tickets
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to load tickets.'
  } finally {
    loading.value = false
  }
}

onMounted(loadTickets)
</script>