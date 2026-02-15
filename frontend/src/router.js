// /frontend/src/router.js
import { createRouter, createWebHistory } from 'vue-router'
import Login from './components/Login.vue'
import Dashboard from './components/Dashboard.vue'
import DomainEditor from './components/DomainEditor.vue'
import UserManager from './components/UserManager.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/domain/new',
    name: 'NewDomain',
    component: DomainEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/domain/:id',
    name: 'EditDomain',
    component: DomainEditor,
    meta: { requiresAuth: true }
  },
  {
    path: '/users',
    name: 'UserManager',
    component: UserManager,
    meta: { requiresAuth: true, requiresSuperuser: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else if (to.meta.requiresSuperuser && !user.is_superuser) {
    next('/')
  } else if (to.path === '/login' && token) {
    next('/')
  } else {
    next()
  }
})

export default router