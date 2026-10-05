<template>
  <div>
    <div class="page-header">
      <h1>User Management</h1>
      <button class="btn" @click="openCreateModal">Create User</button>
    </div>

    <div v-if="loading" class="loading">Loading users...</div>
    <div v-if="errorMessage" class="alert-error">{{ errorMessage }}</div>
    <div v-if="successMessage" class="alert-success">{{ successMessage }}</div>

    <table v-if="users.length && !loading" class="table">
      <thead>
        <tr>
          <th>ID</th>
          <th>Name</th>
          <th>Email</th>
          <th>Roles</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td>{{ user.id }}</td>
          <td>{{ user.name }}</td>
          <td>{{ user.email }}</td>
          <td>
            <span v-for="role in user.roles" :key="role.id" class="badge badge-role">{{ role.name }}</span>
          </td>
          <td>
            <span :class="['badge', user.active ? 'badge-active' : 'badge-inactive']">
              {{ user.active ? 'Active' : 'Inactive' }}
            </span>
          </td>
          <td>
            <button class="btn btn-secondary btn-sm" @click="openEditModal(user)">Edit</button>
            <button class="btn btn-danger btn-sm" @click="handleDelete(user.id)">Delete</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Create Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-card">
        <h2>Create User</h2>
        <div v-if="modalError" class="alert-error">{{ modalError }}</div>
        <form @submit.prevent="handleCreate">
          <div class="form-group">
            <label>Name</label>
            <input v-model.trim="createForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Email</label>
            <input v-model.trim="createForm.email" type="email" required />
          </div>
          <div class="form-group">
            <label>Password (min 8 chars)</label>
            <input v-model="createForm.password" type="password" required minlength="8" />
          </div>
          <div class="form-group">
            <label>Roles</label>
            <div class="checkbox-group">
              <label v-for="role in availableRoles" :key="role">
                <input type="checkbox" :value="role" v-model="createForm.roles" />
                {{ role }}
              </label>
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn" :disabled="modalLoading">Create</button>
            <button type="button" class="btn btn-secondary" @click="closeModals" :disabled="modalLoading">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Edit Modal -->
    <div v-if="editingUser" class="modal-overlay" @click.self="closeModals">
      <div class="modal-card">
        <h2>Edit User: {{ editingUser.email }}</h2>
        <div v-if="modalError" class="alert-error">{{ modalError }}</div>
        <form @submit.prevent="handleUpdate">
          <div class="form-group">
            <label>Name</label>
            <input v-model.trim="editForm.name" type="text" required />
          </div>
          <div class="form-group">
            <label>Status</label>
            <select v-model="editForm.active">
              <option :value="true">Active</option>
              <option :value="false">Inactive</option>
            </select>
          </div>
          <div class="form-group">
            <label>Roles</label>
            <div class="checkbox-group">
              <label v-for="role in availableRoles" :key="role">
                <input type="checkbox" :value="role" v-model="editForm.roles" />
                {{ role }}
              </label>
            </div>
          </div>
          <div class="modal-actions">
            <button type="submit" class="btn" :disabled="modalLoading">Save</button>
            <button type="button" class="btn btn-secondary" @click="closeModals" :disabled="modalLoading">Cancel</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { fetchUsers, createUser, updateUser, deleteUser } from '../api/users'

const users = ref([])
const loading = ref(true)
const errorMessage = ref('')
const successMessage = ref('')

const availableRoles = ['admin', 'agent', 'customer']

const showCreateModal = ref(false)
const editingUser = ref(null)
const modalError = ref('')
const modalLoading = ref(false)

const createForm = ref({ name: '', email: '', password: '', roles: ['customer'] })
const editForm = ref({ name: '', active: true, roles: [] })

const loadUsers = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const { data } = await fetchUsers()
    users.value = data.users
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to load users.'
  } finally {
    loading.value = false
  }
}

onMounted(loadUsers)

const openCreateModal = () => {
  createForm.value = { name: '', email: '', password: '', roles: ['customer'] }
  modalError.value = ''
  showCreateModal.value = true
}

const openEditModal = (user) => {
  editingUser.value = user
  editForm.value = {
    name: user.name,
    active: user.active,
    roles: user.roles.map(r => r.name)
  }
  modalError.value = ''
}

const closeModals = () => {
  showCreateModal.value = false
  editingUser.value = null
}

const handleCreate = async () => {
  modalError.value = ''
  if (createForm.value.roles.length === 0) {
    modalError.value = 'Please select at least one role.'
    return
  }
  modalLoading.value = true
  try {
    await createUser(createForm.value)
    showCreateModal.value = false
    successMessage.value = 'User created successfully.'
    setTimeout(() => successMessage.value = '', 3000)
    await loadUsers()
  } catch (error) {
    modalError.value = error.response?.data?.error || 'Failed to create user.'
  } finally {
    modalLoading.value = false
  }
}

const handleUpdate = async () => {
  modalError.value = ''
  if (editForm.value.roles.length === 0) {
    modalError.value = 'Please select at least one role.'
    return
  }
  modalLoading.value = true
  try {
    await updateUser(editingUser.value.id, editForm.value)
    editingUser.value = null
    successMessage.value = 'User updated successfully.'
    setTimeout(() => successMessage.value = '', 3000)
    await loadUsers()
  } catch (error) {
    modalError.value = error.response?.data?.error || 'Failed to update user.'
  } finally {
    modalLoading.value = false
  }
}

const handleDelete = async (id) => {
  if (!confirm('Are you sure you want to delete this user? This cannot be undone.')) return
  
  errorMessage.value = ''
  successMessage.value = ''
  try {
    await deleteUser(id)
    successMessage.value = 'User deleted successfully.'
    setTimeout(() => successMessage.value = '', 3000)
    await loadUsers()
  } catch (error) {
    errorMessage.value = error.response?.data?.error || 'Failed to delete user.'
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-card {
  background: #fff;
  padding: 2rem;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.checkbox-group {
  display: flex;
  gap: 1rem;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: normal;
  text-transform: capitalize;
}

.badge-role {
  background: #e0edff;
  color: #1d4ed8;
  margin-right: 0.25rem;
}

.badge-active {
  background: #ddf5e4;
  color: #177245;
}

.badge-inactive {
  background: #fdecec;
  color: #d64545;
}

.btn-sm {
  padding: 0.3rem 0.6rem;
  font-size: 0.85rem;
}
</style>