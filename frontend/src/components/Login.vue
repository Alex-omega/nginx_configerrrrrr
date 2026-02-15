<!-- /frontend/src/components/Login.vue -->
<template>
  <div class="login-container">
    <div class="lang-switch standalone-lang">
      <label for="login-lang">{{ $t('language.label') }}</label>
      <select id="login-lang" :value="$i18nState.language" @change="changeLanguage($event.target.value)">
        <option value="en">{{ $t('language.english') }}</option>
        <option value="zh">{{ $t('language.chinese') }}</option>
      </select>
    </div>

    <div class="login-box">
      <h2>{{ $t('login.title') }}</h2>

      <div v-if="error" class="error-message">
        {{ error }}
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>{{ $t('login.username') }}</label>
          <input
            v-model="username"
            type="text"
            :placeholder="$t('login.enterUsername')"
            required
          />
        </div>

        <div class="form-group">
          <label>{{ $t('login.password') }}</label>
          <input
            v-model="password"
            type="password"
            :placeholder="$t('login.enterPassword')"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? $t('login.loggingIn') : $t('login.login') }}
        </button>
      </form>
    </div>

    <div v-if="showPasswordChange" class="modal">
      <div class="modal-content">
        <h3>{{ $t('login.changeDefaultPassword') }}</h3>
        <p>{{ $t('login.changePasswordRequired') }}</p>

        <div v-if="passwordError" class="error-message">
          {{ passwordError }}
        </div>

        <form @submit.prevent="handlePasswordChange">
          <div class="form-group">
            <label>{{ $t('login.currentPassword') }}</label>
            <input
              v-model="oldPassword"
              type="password"
              required
            />
          </div>

          <div class="form-group">
            <label>{{ $t('login.newPassword') }}</label>
            <input
              v-model="newPassword"
              type="password"
              :placeholder="$t('login.atLeast6')"
              required
            />
          </div>

          <div class="form-group">
            <label>{{ $t('login.confirmNewPassword') }}</label>
            <input
              v-model="confirmPassword"
              type="password"
              required
            />
          </div>

          <button type="submit" class="btn btn-primary" :disabled="changingPassword">
            {{ changingPassword ? $t('login.changing') : $t('login.changePassword') }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      error: '',
      loading: false,
      showPasswordChange: false,
      oldPassword: '',
      newPassword: '',
      confirmPassword: '',
      passwordError: '',
      changingPassword: false
    }
  },
  methods: {
    changeLanguage(language) {
      this.$setLanguage(language)
    },

    async handleLogin() {
      this.error = ''
      this.loading = true

      try {
        const response = await api.login(this.username, this.password)
        const { token, user } = response.data

        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))

        if (user.is_default_password) {
          this.showPasswordChange = true
          this.oldPassword = this.password
        } else {
          this.$router.push('/')
        }
      } catch (error) {
        this.error = error.response?.data?.error || this.$t('login.loginFailed')
      } finally {
        this.loading = false
      }
    },

    async handlePasswordChange() {
      this.passwordError = ''

      if (this.newPassword.length < 6) {
        this.passwordError = this.$t('login.passwordTooShort')
        return
      }

      if (this.newPassword !== this.confirmPassword) {
        this.passwordError = this.$t('login.passwordMismatch')
        return
      }

      this.changingPassword = true

      try {
        await api.changePassword(this.oldPassword, this.newPassword)

        const user = JSON.parse(localStorage.getItem('user'))
        user.is_default_password = false
        localStorage.setItem('user', JSON.stringify(user))

        this.$router.push('/')
      } catch (error) {
        this.passwordError = error.response?.data?.error || this.$t('login.changePasswordFailed')
      } finally {
        this.changingPassword = false
      }
    }
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
  position: relative;
}

.standalone-lang {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.lang-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #555;
}

.lang-switch select {
  border: 1px solid #d8d8d8;
  border-radius: 4px;
  padding: 0.25rem 0.5rem;
  background: white;
  color: #333;
}

.login-box {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 400px;
}

.login-box h2 {
  margin-bottom: 2rem;
  color: #333;
  text-align: center;
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
  transition: border-color 0.3s;
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.btn {
  width: 100%;
  padding: 1rem;
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

.btn-primary:hover:not(:disabled) {
  background: #5568d3;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
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
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-bottom: 1rem;
  color: #ff6b6b;
}

.modal-content p {
  margin-bottom: 1.5rem;
  color: #666;
}
</style>
