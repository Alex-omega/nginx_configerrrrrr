<!-- /frontend/src/components/Dashboard.vue -->
<template>
  <div class="dashboard">
    <div class="container">
      <div class="header">
        <h2>📋 Domain Management</h2>
        <button @click="createDomain" class="btn btn-primary">
          ➕ Add Domain
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        Loading domains...
      </div>
      
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-else-if="domains.length === 0" class="empty-state">
        <p>No domains configured yet.</p>
        <button @click="createDomain" class="btn btn-primary">
          Create Your First Domain
        </button>
      </div>
      
      <div v-else class="domains-grid">
        <div 
          v-for="domain in domains" 
          :key="domain.id" 
          class="domain-card"
          @click="editDomain(domain.id)"
        >
          <div class="domain-header">
            <h3>{{ domain.name }}</h3>
            <span v-if="domain.ssl_enabled" class="ssl-badge">🔒 SSL</span>
          </div>
          
          <div class="domain-info">
            <div class="info-item">
              <strong>Server Name:</strong> {{ domain.server_name }}
            </div>
            <div class="info-item">
              <strong>Port:</strong> {{ domain.listen_port }}
            </div>
            <div class="info-item">
              <strong>Locations:</strong> {{ domain.locations?.length || 0 }}
            </div>
          </div>
          
          <div class="domain-actions">
            <button 
              @click.stop="editDomain(domain.id)" 
              class="btn btn-small btn-secondary"
            >
              ✏️ Edit
            </button>
            <button 
              v-if="user.is_superuser"
              @click.stop="confirmDelete(domain)" 
              class="btn btn-small btn-danger"
            >
              🗑️ Delete
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Delete Confirmation Modal -->
    <div v-if="deleteModal" class="modal">
      <div class="modal-content">
        <h3>⚠️ Confirm Deletion</h3>
        <p>Are you sure you want to delete <strong>{{ deleteModal.name }}</strong>?</p>
        <p class="warning">This will remove the Nginx configuration file and cannot be undone.</p>
        
        <div class="modal-actions">
          <button @click="deleteModal = null" class="btn btn-secondary">
            Cancel
          </button>
          <button @click="deleteDomain" class="btn btn-danger">
            Delete
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Dashboard',
  data() {
    return {
      domains: [],
      loading: true,
      error: '',
      deleteModal: null
    }
  },
  computed: {
    user() {
      return JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  mounted() {
    this.loadDomains()
  },
  methods: {
    async loadDomains() {
      this.loading = true
      this.error = ''
      
      try {
        const response = await api.getDomains()
        this.domains = response.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to load domains'
      } finally {
        this.loading = false
      }
    },
    
    createDomain() {
      this.$router.push('/domain/new')
    },
    
    editDomain(id) {
      this.$router.push(`/domain/${id}`)
    },
    
    confirmDelete(domain) {
      this.deleteModal = domain
    },
    
    async deleteDomain() {
      const domainId = this.deleteModal.id
      this.deleteModal = null
      
      try {
        await api.deleteDomain(domainId)
        this.domains = this.domains.filter(d => d.id !== domainId)
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to delete domain'
      }
    }
  }
}
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  min-height: calc(100vh - 70px);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.header h2 {
  color: #333;
}

.loading, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.empty-state p {
  margin-bottom: 1.5rem;
  font-size: 1.1rem;
}

.domains-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.domain-card {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.domain-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #667eea;
}

.domain-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.domain-header h3 {
  color: #333;
  font-size: 1.2rem;
  word-break: break-all;
}

.ssl-badge {
  background: #4caf50;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.domain-info {
  margin-bottom: 1rem;
}

.info-item {
  margin-bottom: 0.5rem;
  color: #555;
  font-size: 0.9rem;
}

.info-item strong {
  color: #333;
}

.domain-actions {
  display: flex;
  gap: 0.5rem;
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

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-danger {
  background: #ff6b6b;
  color: white;
}

.btn-danger:hover {
  background: #ee5555;
}

.btn-small {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
  flex: 1;
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
  background: rgba(0,0,0,0.7);
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
  max-width: 500px;
}

.modal-content h3 {
  margin-bottom: 1rem;
  color: #ff6b6b;
}

.modal-content p {
  margin-bottom: 1rem;
  color: #666;
}

.modal-content .warning {
  color: #ff6b6b;
  font-size: 0.9rem;
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