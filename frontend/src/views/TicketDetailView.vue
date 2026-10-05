<template>
  <div v-if="loading">Loading ticket...</div>

  <div v-else-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

  <div v-else-if="ticket">
    <div class="page-header">
      <h1>#{{ ticket.id }} {{ ticket.subject }}</h1>
      <button class="btn btn-secondary" @click="router.push('/tickets')">Back to Tickets</button>
    </div>

    <div class="detail-grid">
      <div class="card">
        <h2>Details</h2>
        <p>
          <strong>Status:</strong>
          <span :class="['badge', `badge-${ticket.status}`]">{{ formatStatus(ticket.status) }}</span>
        </p>
        <p>
          <strong>Priority:</strong>
          <span :class="['badge', `badge-priority-${ticket.priority}`]">{{ ticket.priority }}</span>
        </p>
        <p><strong>Category:</strong> {{ ticket.category ? ticket.category.name : '-' }}</p>
        <p><strong>Customer:</strong> {{ ticket.customer ? ticket.customer.name : '-' }}</p>
        <p><strong>Assignee:</strong> {{ ticket.assignee ? ticket.assignee.name : 'Unassigned' }}</p>
        <p><strong>Created:</strong> {{ formatDate(ticket.created_at) }}</p>
        <h3>Description</h3>
        <p class="ticket-description">{{ ticket.description }}</p>
      </div>

      <div v-if="isStaff" class="card">
        <h2>Manage Ticket</h2>

        <div class="form-group">
          <label for="statusSelect">Status</label>
          <select id="statusSelect" v-model="statusForm">
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
            <option value="closed">Closed</option>
          </select>
        </div>
        <button class="btn" :disabled="saving" @click="handleStatusUpdate">Update Status</button>

        <div class="form-group">
          <label for="prioritySelect">Priority</label>
          <select id="prioritySelect" v-model="priorityForm">
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        <button class="btn" :disabled="saving" @click="handlePriorityUpdate">Update Priority</button>

        <template v-if="isAdmin">
          <div class="form-group">
            <label for="assigneeSelect">Assignee</label>
            <select id="assigneeSelect" v-model="assigneeForm">
              <option value="">Unassigned</option>
              <option v-for="agent in agents" :key="agent.id" :value="agent.id">
                {{ agent.name }}
              </option>
            </select>
          </div>
          <button class="btn" :disabled="saving" @click="handleAssign">Assign</button>
        </template>

        <div v-if="manageMessage" class="alert-success">{{ manageMessage }}</div>
        <div v-if="manageError" class="alert-error">{{ manageError }}</div>
      </div>
    </div>

    <div class="card">
      <h2>Comments ({{ comments.length }})</h2>

      <div v-if="comments.length" class="comment-list">
        <div v-for="comment in comments" :key="comment.id" class="comment">
          <div class="comment-meta">
            <strong>{{ comment.author ? comment.author.name : 'Unknown' }}</strong>
            <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
          </div>
          <p>{{ comment.body }}</p>
        </div>
      </div>
      <p v-else class="empty-state">No comments yet.</p>

      <h3>Add a comment</h3>
      <form @submit.prevent="handleComment">
        <div class="form-group">
          <textarea v-model="commentBody" rows="3" placeholder="Write a comment..." required></textarea>
        </div>
        <button class="btn" type="submit" :disabled="commentSubmitting">
          {{ commentSubmitting ? 'Posting...' : 'Post Comment' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  addComment,
  assignTicket,
  fetchComments,
  fetchTicket,
  updateTicket,
  updateTicketStatus,
} from '../api/tickets'
import { fetchUsers } from '../api/users'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const ticket = ref(null)
const comments = ref([])
const agents = ref([])
const loading = ref(true)
const saving = ref(false)
const errorMessage = ref('')
const manageMessage = ref('')
const manageError = ref('')

const statusForm = ref('')
const priorityForm = ref('')
const assigneeForm = ref('')

const commentBody = ref('')
const commentSubmitting = ref(false)

const userRoles = computed(() => (auth.user ? auth.user.roles.map((r) => r.name) : []))
const isAdmin = computed(() => userRoles.value.includes('admin'))
const isStaff = computed(() => userRoles.value.includes('admin') || userRoles.value.includes('agent'))

const formatStatus = (status) => status.replace('_', ' ')

const formatDate = (value) => {
  if (!value) return '-'
  return new Date(value).toLocaleString()
}

const loadTicket = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const { data } = await fetchTicket(route.params.id)
    ticket.value = data.ticket
    statusForm.value = ticket.value.status
    priorityForm.value = ticket.value.priority
    assigneeForm.value = ticket.value.assignee ? String(ticket.value.assignee.id) : ''

    const commentsResponse = await fetchComments(route.params.id)
    comments.value = commentsResponse.data.comments

    if (isAdmin.value) {
      const agentsResponse = await fetchUsers({ role: 'agent' })
      agents.value = agentsResponse.data.users
    }
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to load ticket.'
  } finally {
    loading.value = false
  }
}

onMounted(loadTicket)

const handleStatusUpdate = async () => {
  saving.value = true
  manageMessage.value = ''
  manageError.value = ''

  try {
    const { data } = await updateTicketStatus(ticket.value.id, statusForm.value)
    ticket.value = data.ticket
    manageMessage.value = 'Status updated.'
  } catch (error) {
    manageError.value = error.response?.data?.error || 'Failed to update status.'
  } finally {
    saving.value = false
  }
}

const handlePriorityUpdate = async () => {
  saving.value = true
  manageMessage.value = ''
  manageError.value = ''

  try {
    const { data } = await updateTicket(ticket.value.id, { priority: priorityForm.value })
    ticket.value = data.ticket
    manageMessage.value = 'Priority updated.'
  } catch (error) {
    manageError.value = error.response?.data?.error || 'Failed to update priority.'
  } finally {
    saving.value = false
  }
}

const handleAssign = async () => {
  saving.value = true
  manageMessage.value = ''
  manageError.value = ''

  try {
    const payload = assigneeForm.value ? Number(assigneeForm.value) : null
    const { data } = await assignTicket(ticket.value.id, payload)
    ticket.value = data.ticket
    manageMessage.value = 'Assignee updated.'
  } catch (error) {
    manageError.value = error.response?.data?.error || 'Failed to assign ticket.'
  } finally {
    saving.value = false
  }
}

const handleComment = async () => {
  commentSubmitting.value = true
  errorMessage.value = ''

  try {
    const { data } = await addComment(ticket.value.id, commentBody.value)
    comments.value.push(data.comment)
    commentBody.value = ''
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to add comment.'
  } finally {
    commentSubmitting.value = false
  }
}
</script>