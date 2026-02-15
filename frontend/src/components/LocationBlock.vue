<!-- /frontend/src/components/LocationBlock.vue -->
<template>
  <div class="location-block">
    <div class="location-header">
      <h4>Location: {{ localLocation.path }}</h4>
      <div class="header-actions">
        <label class="mode-toggle">
          <input 
            type="checkbox" 
            :checked="localLocation.mode === 'advanced'"
            @change="toggleMode"
          />
          <span>Advanced Mode</span>
        </label>
        <button @click="$emit('remove')" class="btn-remove">🗑️</button>
      </div>
    </div>
    
    <div class="location-content">
      <div class="form-row">
        <div class="form-group">
          <label>Location Path *</label>
          <input 
            v-model="localLocation.path" 
            type="text" 
            placeholder="/"
            @input="updateLocation"
          />
        </div>
        
        <div class="form-group">
          <label>Match Modifier</label>
          <select v-model="localLocation.match_modifier" @change="updateLocation">
            <option value="">Prefix (default)</option>
            <option value="=">= (Exact Match)</option>
            <option value="^~">^~ (Prefix, no regex)</option>
            <option value="~">~ (Regex, case-sensitive)</option>
            <option value="~*">~* (Regex, case-insensitive)</option>
          </select>
        </div>
      </div>
      
      <!-- Basic Mode -->
      <div v-if="localLocation.mode === 'basic'" class="basic-mode">
        <div class="form-group">
          <label>Forward Type</label>
          <select v-model="localLocation.forward_type" @change="updateLocation">
            <option value="dynamic">Dynamic (Proxy)</option>
            <option value="static">Static (File Serving)</option>
          </select>
        </div>
        
        <div v-if="localLocation.forward_type === 'dynamic'" class="form-group">
          <label>Proxy Pass *</label>
          <input 
            v-model="localLocation.proxy_pass" 
            type="text" 
            placeholder="http://127.0.0.1:8080"
            @input="updateLocation"
          />
          <small>Target backend server (e.g., http://127.0.0.1:8080)</small>
        </div>
        
        <div v-else class="form-group">
          <label>Root Path *</label>
          <input 
            v-model="localLocation.root_path" 
            type="text" 
            placeholder="/var/www/html"
            @input="updateLocation"
          />
          <small>Local directory path to serve files from</small>
        </div>
        
        <div class="info-box">
          <strong>📋 Standard Template Applied:</strong>
          <ul>
            <li v-if="localLocation.forward_type === 'dynamic'">Proxy headers (Host, X-Real-IP, X-Forwarded-For, etc.)</li>
            <li v-if="localLocation.forward_type === 'dynamic'">Timeouts: 1200s connect/send/read</li>
            <li v-if="localLocation.forward_type === 'dynamic'">Max body size: 500m</li>
            <li v-if="localLocation.forward_type === 'dynamic'">Keepalive: 300s</li>
            <li v-if="localLocation.forward_type === 'static'">Index files: index.html, index.htm</li>
          </ul>
        </div>
      </div>
      
      <!-- Advanced Mode -->
      <div v-else class="advanced-mode">
        <div class="form-group">
          <label>Custom Configuration</label>
          <textarea 
            v-model="localLocation.config_content" 
            rows="15"
            placeholder="Enter custom Nginx directives..."
            @input="updateLocation"
          ></textarea>
          <small>Enter raw Nginx directives (without location block wrapper)</small>
        </div>
        
        <details class="help-section">
          <summary>📚 Common Nginx Directives</summary>
          <div class="help-content">
            <h5>Proxy Directives:</h5>
            <code>proxy_pass http://backend;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_connect_timeout 60s;</code>
            
            <h5>Static File Directives:</h5>
            <code>root /var/www/html;
index index.html;
try_files $uri $uri/ =404;</code>
            
            <h5>Security:</h5>
            <code>add_header X-Frame-Options "SAMEORIGIN";
add_header X-Content-Type-Options "nosniff";</code>
          </div>
        </details>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LocationBlock',
  props: {
    location: {
      type: Object,
      required: true
    },
    index: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      localLocation: { ...this.location }
    }
  },
  watch: {
    location: {
      handler(newVal) {
        this.localLocation = { ...newVal }
      },
      deep: true
    }
  },
  methods: {
    updateLocation() {
      this.$emit('update', this.localLocation)
    },
    
    toggleMode(event) {
      this.localLocation.mode = event.target.checked ? 'advanced' : 'basic'
      
      // When switching to advanced, populate with basic template
      if (this.localLocation.mode === 'advanced' && !this.localLocation.config_content) {
        if (this.localLocation.forward_type === 'dynamic' && this.localLocation.proxy_pass) {
          this.localLocation.config_content = `proxy_pass ${this.localLocation.proxy_pass};
proxy_redirect off;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
proxy_connect_timeout 1200s;
proxy_send_timeout 1200s;
proxy_read_timeout 1200s;
client_max_body_size 500m;
client_body_buffer_size 80m;
keepalive_timeout 300s;`
        } else if (this.localLocation.forward_type === 'static' && this.localLocation.root_path) {
          this.localLocation.config_content = `root ${this.localLocation.root_path};
index index.html index.htm;`
        }
      }
      
      this.updateLocation()
    }
  }
}
</script>

<style scoped>
.location-block {
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  margin-bottom: 1rem;
  overflow: hidden;
}

.location-header {
  background: #667eea;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.location-header h4 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.mode-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.mode-toggle input {
  cursor: pointer;
}

.btn-remove {
  background: #ff6b6b;
  border: none;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background 0.3s;
}

.btn-remove:hover {
  background: #ee5555;
}

.location-content {
  padding: 1.5rem;
}

.form-row {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
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
  font-family: inherit;
}

.form-group textarea {
  font-family: 'Courier New', monospace;
  resize: vertical;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
}

.form-group small {
  display: block;
  margin-top: 0.25rem;
  color: #888;
  font-size: 0.85rem;
}

.info-box {
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  padding: 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
}

.info-box strong {
  display: block;
  margin-bottom: 0.5rem;
  color: #1976d2;
}

.info-box ul {
  margin-left: 1.5rem;
}

.info-box li {
  margin-bottom: 0.25rem;
}

.help-section {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
  margin-top: 1rem;
}

.help-section summary {
  cursor: pointer;
  font-weight: 600;
  color: #667eea;
  user-select: none;
}

.help-content {
  margin-top: 1rem;
}

.help-content h5 {
  margin: 1rem 0 0.5rem 0;
  color: #333;
}

.help-content code {
  display: block;
  background: white;
  padding: 0.75rem;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  white-space: pre;
  overflow-x: auto;
  border: 1px solid #e0e0e0;
}
</style>