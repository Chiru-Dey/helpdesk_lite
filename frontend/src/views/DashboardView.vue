<template>
  <div>
    <h1>Dashboard</h1>

    <div v-if="loading" class="loading">Loading dashboard...</div>
    <div v-else-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <template v-else>
      <div class="stat-grid">
        <div class="stat-card">
          <div class="stat-label">Total Tickets</div>
          <div class="stat-value">{{ data.total_tickets }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Open</div>
          <div class="stat-value text-blue">{{ data.open_tickets }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">In Progress</div>
          <div class="stat-value text-yellow">{{ data.in_progress_tickets }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Resolved Today</div>
          <div class="stat-value text-green">{{ data.resolved_today }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Closed</div>
          <div class="stat-value text-gray">{{ data.closed_tickets }}</div>
        </div>
      </div>

      <div class="dashboard-grid">
        <div class="card">
          <h2>Tickets by Status</h2>
          <div class="bar-chart">
            <div v-for="(count, status) in data.tickets_by_status" :key="status" class="bar-row">
              <div class="bar-label">{{ formatStatus(status) }}</div>
              <div class="bar-track">
                <div class="bar-fill" :class="`bar-fill-${status}`" :style="{ width: getBarWidth(count, data.total_tickets) }"></div>
              </div>
              <div class="bar-count">{{ count }}</div>
            </div>
          </div>
        </div>

        <div class="card">
          <h2>Tickets by Priority</h2>
          <div class="bar-chart">
            <div v-for="(count, priority) in data.tickets_by_priority" :key="priority" class="bar-row">
              <div class="bar-label">{{ priority }}</div>
              <div class="bar-track">
                <div class="bar-fill" :class="`bar-fill-priority-${priority}`" :style="{ width: getBarWidth(count, data.total_tickets) }"></div>
              </div>
              <div class="bar-count">{{ count }}</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h2>Recent Tickets</h2>
        <table v-if="data.recent_tickets.length" class="table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Subject</th>
              <th>Status</th>
              <th>Customer</th>
              <th>Assignee</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ticket in data.recent_tickets" :key="ticket.id" @click="router.push(`/tickets/${ticket.id}`)">
              <td>{{ ticket.id }}</td>
              <td>{{ ticket.subject }}</td>
              <td><span :class="['badge', `badge-${ticket.status}`]">{{ formatStatus(ticket.status) }}</span></td>
              <td>{{ ticket.customer ? ticket.customer.name : '-' }}</td>
              <td>{{ ticket.assignee ? ticket.assignee.name : 'Unassigned' }}</td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-state">No recent tickets.</p>
      </div>
    </template>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchDashboard } from '../api/dashboard'

const router = useRouter()

const data = ref(null)
const loading = ref(true)
const errorMessage = ref('')

const formatStatus = (status) => status.replace('_', ' ')

const getBarWidth = (count, total) => {
  if (!total || total === 0) return '0%'
  return `${Math.max((count / total) * 100, count > 0 ? 2 : 0)}%`
}

onMounted(async () => {
  try {
    const response = await fetchDashboard()
    data.value = response.data.dashboard
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to load dashboard.'
  } finally {
    loading.value = false
  }
})
</script>