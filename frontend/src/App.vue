<!-- /frontend/src/App.vue -->
<template>
  <div id="app">
    <nav v-if="isLoggedIn" class="navbar">
      <div class="navbar-brand">
        <h1>{{ $t('app.title') }}</h1>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="nav-item">{{ $t('nav.dashboard') }}</router-link>
        <router-link v-if="user.is_superuser" to="/users" class="nav-item">{{ $t('nav.users') }}</router-link>

        <div class="lang-switch">
          <label for="global-lang">{{ $t('language.label') }}</label>
          <select id="global-lang" :value="$i18nState.language" @change="changeLanguage($event.target.value)">
            <option value="en">{{ $t('language.english') }}</option>
            <option value="zh">{{ $t('language.chinese') }}</option>
          </select>
        </div>

        <div class="nav-item user-info">
          {{ user.username }}
        </div>
        <button @click="logout" class="nav-item logout-btn">{{ $t('nav.logout') }}</button>
      </div>
    </nav>

    <router-view />
  </div>
</template>

<script>
export default {
  name: 'App',
  computed: {
    isLoggedIn() {
      return !!localStorage.getItem('token') && this.$route.path !== '/login'
    },
    user() {
      return JSON.parse(localStorage.getItem('user') || '{}')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.$router.push('/login')
    },
    changeLanguage(language) {
      this.$setLanguage(language)
    }
  }
}
</script>

<style>
.navbar {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.navbar-brand h1 {
  font-size: 1.5rem;
  color: #667eea;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.nav-item {
  text-decoration: none;
  color: #333;
  font-weight: 500;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  transition: all 0.3s;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.nav-item:hover {
  background: #f0f0f0;
}

.nav-item.router-link-active {
  background: #667eea;
  color: white;
}

.lang-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #666;
  font-size: 0.9rem;
}

.lang-switch select {
  border: 1px solid #d8d8d8;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  background: white;
  color: #333;
}

.user-info {
  color: #666;
  cursor: default;
}

.user-info:hover {
  background: none;
}

.logout-btn {
  background: #ff6b6b;
  color: white;
}

.logout-btn:hover {
  background: #ee5555;
}
</style>
