// /frontend/src/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Handle auth errors
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default {
  // Auth
  login(username, password) {
    return api.post('/login', { username, password })
  },
  
  changePassword(oldPassword, newPassword) {
    return api.post('/change-password', {
      old_password: oldPassword,
      new_password: newPassword
    })
  },
  
  // Domains
  getDomains() {
    return api.get('/domains')
  },
  
  getDomain(id) {
    return api.get(`/domains/${id}`)
  },
  
  createDomain(data) {
    return api.post('/domains', data)
  },
  
  updateDomain(id, data) {
    return api.put(`/domains/${id}`, data)
  },
  
  deleteDomain(id) {
    return api.delete(`/domains/${id}`)
  },
  
  enableSSL(id) {
    return api.post(`/domains/${id}/ssl`)
  },
  
  // Users
  getUsers() {
    return api.get('/users')
  },
  
  createUser(data) {
    return api.post('/users', data)
  },
  
  updateUserPermissions(id, domainIds) {
    return api.put(`/users/${id}`, { domain_ids: domainIds })
  }
}