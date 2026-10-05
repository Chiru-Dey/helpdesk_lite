<template>
  <div class="auth-card wide-card">
    <h1>Create Ticket</h1>

    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>

    <form @submit.prevent="handleSubmit">
      <div class="form-group">
        <label for="subject">Subject</label>
        <input id="subject" v-model.trim="subject" type="text" required />
      </div>

      <div class="form-group">
        <label for="category">Category</label>
        <select id="category" v-model="categoryId" required>
          <option value="" disabled>Select a category</option>
          <option v-for="category in categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>

      <div class="form-group">
        <label for="priority">Priority</label>
        <select id="priority" v-model="priority">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="urgent">Urgent</option>
        </select>
      </div>

      <div class="form-group">
        <label for="description">Description</label>
        <textarea id="description" v-model="description" rows="5" required></textarea>
      </div>

      <button class="btn" type="submit" :disabled="submitting">
        {{ submitting ? 'Creating...' : 'Create Ticket' }}
      </button>
      <button class="btn btn-secondary" type="button" @click="router.push('/tickets')">
        Cancel
      </button>
    </form>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createTicket } from '../api/tickets'
import { fetchCategories } from '../api/categories'

const router = useRouter()

const subject = ref('')
const description = ref('')
const categoryId = ref('')
const priority = ref('medium')
const categories = ref([])
const errorMessage = ref('')
const submitting = ref(false)

onMounted(async () => {
  try {
    const { data } = await fetchCategories()
    categories.value = data.categories
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to load categories.'
  }
})

const handleSubmit = async () => {
  errorMessage.value = ''
  submitting.value = true

  try {
    const { data } = await createTicket({
      subject: subject.value,
      description: description.value,
      category_id: categoryId.value,
      priority: priority.value,
    })
    router.push(`/tickets/${data.ticket.id}`)
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to create ticket.'
  } finally {
    submitting.value = false
  }
}
</script>