<!-- /frontend/src/components/UserManager.vue -->
<template>
  <div class="user-manager">
    <div class="container">
      <div class="header">
        <h2>{{ $t('users.title') }}</h2>
        <button @click="showAddUser = true" class="btn btn-primary">
          {{ $t('users.addUser') }}
        </button>
      </div>

      <div v-if="loading" class="loading">
        {{ $t('users.loadingUsers') }}
      </div>

      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>

      <div v-else class="users-table">
        <table>
          <thead>
            <tr>
              <th>{{ $t('users.username') }}</th>
              <th>{{ $t('users.type') }}</th>
              <th>{{ $t('users.accessibleDomains') }}</th>
              <th>{{ $t('users.created') }}</th>
              <th>{{ $t('users.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.username }}</td>
              <td>
                <span :class="['badge', user.is_superuser ? 'badge-admin' : 'badge-user']">
                  {{ user.is_superuser ? $t('users.superuser') : $t('users.user') }}
                </span>
              </td>
              <td>
                {{ user.is_superuser ? $t('users.all') : user.domain_ids.length }}
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button
                  v-if="!user.is_superuser"
                  @click="editUser(user)"
                  class="btn btn-small btn-secondary"
                >
                  {{ $t('users.editPermissions') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showAddUser" class="modal">
      <div class="modal-content">
        <h3>{{ $t('users.addNewUser') }}</h3>

        <div v-if="modalError" class="error-message">
          {{ modalError }}
        </div>

        <form @submit.prevent="createUser">
          <div class="form-group">
            <label>{{ $t('users.username') }} *</label>
            <input
              v-model="newUser.username"
              type="text"
              required
              :placeholder="$t('users.enterUsername')"
            />
          </div>

          <div class="form-group">
            <label>{{ $t('users.password') }} *</label>
            <input
              v-model="newUser.password"
              type="password"
              required
              :placeholder="$t('users.atLeast6')"
            />
          </div>

          <div class="form-group">
            <label>{{ $t('users.accessibleDomains') }}</label>
            <div class="domain-checklist">
              <label
                v-for="domain in domains"
                :key="domain.id"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="domain.id"
                  v-model="newUser.domain_ids"
                />
                <span>{{ domain.name }}</span>
              </label>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="showAddUser = false" class="btn btn-secondary">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? $t('users.creating') : $t('users.createUser') }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="editingUser" class="modal">
      <div class="modal-content">
        <h3>{{ $t('users.editPermissionsTitle', { username: editingUser.username }) }}</h3>

        <div v-if="modalError" class="error-message">
          {{ modalError }}
        </div>

        <form @submit.prevent="updateUserPermissions">
          <div class="form-group">
            <label>{{ $t('users.accessibleDomains') }}</label>
            <div class="domain-checklist">
              <label
                v-for="domain in domains"
                :key="domain.id"
                class="checkbox-label"
              >
                <input
                  type="checkbox"
                  :value="domain.id"
                  v-model="editingUser.domain_ids"
                />
                <span>{{ domain.name }}</span>
              </label>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="editingUser = null" class="btn btn-secondary">
              {{ $t('common.cancel') }}
            </button>
            <button type="submit" class="btn btn-primary" :disabled="updating">
              {{ updating ? $t('users.updating') : $t('users.updatePermissions') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'UserManager',
  data() {
    return {
      users: [],
      domains: [],
      loading: true,
      error: '',
      showAddUser: false,
      editingUser: null,
      newUser: {
        username: '',
        password: '',
        domain_ids: []
      },
      modalError: '',
      creating: false,
      updating: false
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''

      try {
        const [usersRes, domainsRes] = await Promise.all([
          api.getUsers(),
          api.getDomains()
        ])

        this.users = usersRes.data
        this.domains = domainsRes.data
      } catch (error) {
        this.error = error.response?.data?.error || this.$t('users.loadFailed')
      } finally {
        this.loading = false
      }
    },

    async createUser() {
      this.modalError = ''

      if (!this.newUser.username || !this.newUser.password) {
        this.modalError = this.$t('users.usernamePasswordRequired')
        return
      }

      if (this.newUser.password.length < 6) {
        this.modalError = this.$t('users.passwordTooShort')
        return
      }

      this.creating = true

      try {
        await api.createUser(this.newUser)
        await this.loadData()
        this.showAddUser = false
        this.newUser = { username: '', password: '', domain_ids: [] }
      } catch (error) {
        this.modalError = error.response?.data?.error || this.$t('users.createFailed')
      } finally {
        this.creating = false
      }
    },

    editUser(user) {
      this.editingUser = { ...user }
      this.modalError = ''
    },

    async updateUserPermissions() {
      this.modalError = ''
      this.updating = true

      try {
        await api.updateUserPermissions(this.editingUser.id, this.editingUser.domain_ids)
        await this.loadData()
        this.editingUser = null
      } catch (error) {
        this.modalError = error.response?.data?.error || this.$t('users.updateFailed')
      } finally {
        this.updating = false
      }
    },

    formatDate(dateString) {
      const locale = this.$i18nState.language === 'zh' ? 'zh-CN' : 'en-US'
      return new Date(dateString).toLocaleDateString(locale)
    }
  }
}
</script>

<style scoped>
.user-manager {
  padding: 2rem;
  min-height: calc(100vh - 70px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.users-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-admin {
  background: #ff6b6b;
  color: white;
}

.badge-user {
  background: #667eea;
  color: white;
}

.btn {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  background: #ffe0e0;
  color: #d32f2f;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #d32f2f;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #333;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #555;
  font-weight: 500;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.domain-checklist {
  max-height: 300px;
  overflow-y: auto;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: background 0.3s;
}

.checkbox-label:hover {
  background: #f8f9fa;
}

.checkbox-label input {
  cursor: pointer;
  width: auto;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.modal-actions .btn {
  flex: 1;
}
</style>
