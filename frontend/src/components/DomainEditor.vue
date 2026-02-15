<!-- /frontend/src/components/DomainEditor.vue -->
<template>
  <div class="editor-container">
    <div class="editor">
      <div class="editor-header">
        <button @click="goBack" class="btn-back">← Back</button>
        <h2>{{ isNew ? '➕ New Domain' : '✏️ Edit Domain' }}</h2>
      </div>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-if="success" class="success-message">
        {{ success }}
      </div>
      
      <div class="form-section">
        <h3>🌐 Server Configuration</h3>
        
        <div class="form-group">
          <label>Domain Name *</label>
          <input 
            v-model="domain.name" 
            type="text" 
            placeholder="example.com"
            :disabled="!isNew"
            required
          />
          <small>This will be used as configuration filename</small>
        </div>
        
        <div class="form-group">
          <label>Server Name *</label>
          <input 
            v-model="domain.server_name" 
            type="text" 
            placeholder="example.com www.example.com"
            required
          />
          <small>Space-separated list of server names</small>
        </div>
        
        <div class="form-group">
          <label>Listen Port</label>
          <input 
            v-model="domain.listen_port" 
            type="text" 
            placeholder="80"
          />
        </div>
        
        <div v-if="!isNew && !domain.ssl_enabled" class="form-group">
          <button @click="enableSSL" class="btn btn-success" :disabled="sslLoading">
            🔒 {{ sslLoading ? 'Enabling SSL...' : 'Enable HTTPS (Certbot)' }}
          </button>
        </div>
      </div>
      
      <div class="form-section">
        <div class="section-header">
          <h3>📍 Location Blocks</h3>
          <button @click="addLocation" class="btn btn-small btn-primary">
            ➕ Add Location
          </button>
        </div>
        
        <div v-if="domain.locations.length === 0" class="empty-state">
          No locations configured
        </div>
        
        <location-block
          v-for="(location, index) in domain.locations"
          :key="index"
          :location="location"
          :index="index"
          @update="updateLocation(index, $event)"
          @remove="removeLocation(index)"
        />
      </div>
      
      <div class="editor-actions">
        <button @click="goBack" class="btn btn-secondary">
          Cancel
        </button>
        <button @click="save" class="btn btn-primary" :disabled="saving">
          {{ saving ? 'Saving...' : 'Save & Apply' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'
import LocationBlock from './LocationBlock.vue'

export default {
  name: 'DomainEditor',
  components: {
    LocationBlock
  },
  data() {
    return {
      domain: {
        name: '',
        server_name: '',
        listen_port: '80',
        ssl_enabled: false,
        locations: []
      },
      isNew: true,
      loading: true,
      saving: false,
      sslLoading: false,
      error: '',
      success: ''
    }
  },
  mounted() {
    const id = this.$route.params.id
    
    if (id && id !== 'new') {
      this.isNew = false
      this.loadDomain(id)
    } else {
      this.isNew = true
      this.addLocation()
      this.loading = false
    }
  },
  methods: {
    async loadDomain(id) {
      try {
        const response = await api.getDomain(id)
        this.domain = response.data
        
        if (this.domain.locations.length === 0) {
          this.addLocation()
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to load domain'
      } finally {
        this.loading = false
      }
    },
    
    addLocation() {
      this.domain.locations.push({
        path: this.domain.locations.length === 0 ? '/' : '/api',
        match_modifier: '',
        mode: 'basic',
        forward_type: 'dynamic',
        proxy_pass: '',
        root_path: '',
        config_content: ''
      })
    },
    
    updateLocation(index, data) {
      this.domain.locations[index] = { ...this.domain.locations[index], ...data }
    },
    
    removeLocation(index) {
      if (this.domain.locations.length > 1) {
        this.domain.locations.splice(index, 1)
      } else {
        this.error = 'At least one location is required'
      }
    },
    
    async save() {
      this.error = ''
      this.success = ''
      
      if (!this.domain.name || !this.domain.server_name) {
        this.error = 'Domain name and server name are required'
        return
      }
      
      this.saving = true
      
      try {
        if (this.isNew) {
          await api.createDomain(this.domain)
          this.success = 'Domain created successfully!'
          setTimeout(() => this.$router.push('/'), 1500)
        } else {
          await api.updateDomain(this.$route.params.id, this.domain)
          this.success = 'Domain updated successfully!'
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to save domain'
      } finally {
        this.saving = false
      }
    },
    
    async enableSSL() {
      this.error = ''
      this.sslLoading = true
      
      try {
        await api.enableSSL(this.$route.params.id)
        this.success = 'SSL certificate obtained successfully!'
        this.domain.ssl_enabled = true
        this.domain.listen_port = '443'
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to enable SSL'
      } finally {
        this.sslLoading = false
      }
    },
    
    goBack() {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.editor-container {
  padding: 2rem;
  min-height: calc(100vh - 70px);
}

.editor {
  max-width: 900px;
  margin: 0 auto;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.editor-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.btn-back {
  background: #e0e0e0;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.btn-back:hover {
  background: #d0d0d0;
}

.form-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.form-section h3 {
  color: #333;
  margin-bottom: 1rem;
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

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-group input:disabled {
  background: #f0f0f0;
  cursor: not-allowed;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #888;
  font-size: 0.85rem;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.editor-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 2px solid #e0e0e0;
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

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background: #45a049;
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

.success-message {
  background: #e0ffe0;
  color: #2f7d32;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  border-left: 4px solid #4caf50;
}
</style>