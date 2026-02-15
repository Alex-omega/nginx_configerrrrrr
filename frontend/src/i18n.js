// /frontend/src/i18n.js
import { reactive } from 'vue'

const LANGUAGE_STORAGE_KEY = 'app_lang'
const SUPPORTED_LANGUAGES = ['en', 'zh']

const messages = {
  en: {
    app: {
      title: 'Nginx Configerrrrrr'
    },
    language: {
      label: 'Language',
      english: 'English',
      chinese: '中文'
    },
    nav: {
      dashboard: 'Dashboard',
      users: 'Users',
      logout: 'Logout'
    },
    common: {
      loading: 'Loading...',
      save: 'Save',
      cancel: 'Cancel',
      create: 'Create',
      update: 'Update',
      delete: 'Delete',
      edit: 'Edit',
      back: 'Back',
      required: 'Required',
      saveApply: 'Save & Apply'
    },
    login: {
      title: 'Login to Nginx Manager',
      username: 'Username',
      password: 'Password',
      enterUsername: 'Enter username',
      enterPassword: 'Enter password',
      login: 'Login',
      loggingIn: 'Logging in...',
      loginFailed: 'Login failed',
      changeDefaultPassword: 'Change Default Password',
      changePasswordRequired: 'You must change your password before proceeding.',
      currentPassword: 'Current Password',
      newPassword: 'New Password',
      confirmNewPassword: 'Confirm New Password',
      atLeast6: 'At least 6 characters',
      changing: 'Changing...',
      changePassword: 'Change Password',
      passwordTooShort: 'Password must be at least 6 characters',
      passwordMismatch: 'Passwords do not match',
      changePasswordFailed: 'Failed to change password'
    },
    dashboard: {
      title: 'Domain Management',
      addDomain: 'Add Domain',
      loadingDomains: 'Loading domains...',
      empty: 'No domains configured yet.',
      createFirstDomain: 'Create Your First Domain',
      ssl: 'SSL',
      serverName: 'Server Name',
      port: 'Port',
      locations: 'Locations',
      edit: 'Edit',
      delete: 'Delete',
      confirmDeletion: 'Confirm Deletion',
      deleteConfirmText: 'Are you sure you want to delete {name}?',
      deleteWarning: 'This will remove the Nginx configuration file and cannot be undone.',
      loadFailed: 'Failed to load domains',
      deleteFailed: 'Failed to delete domain'
    },
    domainEditor: {
      newDomain: 'New Domain',
      editDomain: 'Edit Domain',
      serverConfig: 'Server Configuration',
      domainName: 'Domain Name',
      serverName: 'Server Name',
      listenPort: 'Listen Port',
      configFilenameHint: 'This will be used as configuration filename',
      serverNameHint: 'Space-separated list of server names',
      enableHttps: 'Enable HTTPS (Certbot)',
      enablingSsl: 'Enabling SSL...',
      locationBlocks: 'Location Blocks',
      addLocation: 'Add Location',
      noLocations: 'No locations configured',
      domainRequired: 'Domain name and server name are required',
      needOneLocation: 'At least one location is required',
      saveFailed: 'Failed to save domain',
      loadFailed: 'Failed to load domain',
      sslEnableFailed: 'Failed to enable SSL',
      sslEnabledSuccess: 'SSL certificate obtained successfully!',
      domainCreatedSuccess: 'Domain created successfully!',
      domainUpdatedSuccess: 'Domain updated successfully!',
      saving: 'Saving...'
    },
    location: {
      title: 'Location: {path}',
      advancedMode: 'Advanced Mode',
      locationPath: 'Location Path',
      matchModifier: 'Match Modifier',
      forwardType: 'Forward Type',
      proxyPass: 'Proxy Pass',
      rootPath: 'Root Path',
      targetBackendHint: 'Target backend server (e.g., http://127.0.0.1:8080)',
      rootPathHint: 'Local directory path to serve files from',
      templateApplied: 'Standard Template Applied:',
      customConfig: 'Custom Configuration',
      customConfigPlaceholder: 'Enter custom Nginx directives...',
      customConfigHint: 'Enter raw Nginx directives (without location block wrapper)',
      commonDirectives: 'Common Nginx Directives',
      proxyDirectives: 'Proxy Directives:',
      staticDirectives: 'Static File Directives:',
      securityDirectives: 'Security:',
      proxyHeaders: 'Proxy headers (Host, X-Real-IP, X-Forwarded-For, etc.)',
      proxyTimeouts: 'Timeouts: 1200s connect/send/read',
      proxyBodySize: 'Max body size: 500m',
      proxyKeepalive: 'Keepalive: 300s',
      staticIndexes: 'Index files: index.html, index.htm',
      modifiers: {
        prefixDefault: 'Prefix (default)',
        exact: '= (Exact Match)',
        prefixNoRegex: '^~ (Prefix, no regex)',
        regexCaseSensitive: '~ (Regex, case-sensitive)',
        regexCaseInsensitive: '~* (Regex, case-insensitive)'
      },
      forwardTypes: {
        dynamic: 'Dynamic (Proxy)',
        static: 'Static (File Serving)'
      }
    },
    users: {
      title: 'User Management',
      addUser: 'Add User',
      loadingUsers: 'Loading users...',
      username: 'Username',
      type: 'Type',
      accessibleDomains: 'Accessible Domains',
      created: 'Created',
      actions: 'Actions',
      superuser: 'Superuser',
      user: 'User',
      all: 'All',
      editPermissions: 'Edit Permissions',
      addNewUser: 'Add New User',
      editPermissionsTitle: 'Edit Permissions: {username}',
      password: 'Password',
      atLeast6: 'At least 6 characters',
      enterUsername: 'Enter username',
      createUser: 'Create User',
      creating: 'Creating...',
      updatePermissions: 'Update Permissions',
      updating: 'Updating...',
      loadFailed: 'Failed to load data',
      createFailed: 'Failed to create user',
      updateFailed: 'Failed to update permissions',
      usernamePasswordRequired: 'Username and password are required',
      passwordTooShort: 'Password must be at least 6 characters'
    }
  },
  zh: {
    app: {
      title: 'Nginx 配置管理器'
    },
    language: {
      label: '语言',
      english: 'English',
      chinese: '中文'
    },
    nav: {
      dashboard: '控制台',
      users: '用户管理',
      logout: '退出登录'
    },
    common: {
      loading: '加载中...',
      save: '保存',
      cancel: '取消',
      create: '创建',
      update: '更新',
      delete: '删除',
      edit: '编辑',
      back: '返回',
      required: '必填',
      saveApply: '保存并应用'
    },
    login: {
      title: '登录 Nginx 管理器',
      username: '用户名',
      password: '密码',
      enterUsername: '请输入用户名',
      enterPassword: '请输入密码',
      login: '登录',
      loggingIn: '登录中...',
      loginFailed: '登录失败',
      changeDefaultPassword: '修改默认密码',
      changePasswordRequired: '首次登录必须先修改密码。',
      currentPassword: '当前密码',
      newPassword: '新密码',
      confirmNewPassword: '确认新密码',
      atLeast6: '至少 6 个字符',
      changing: '修改中...',
      changePassword: '修改密码',
      passwordTooShort: '密码至少需要 6 个字符',
      passwordMismatch: '两次输入的密码不一致',
      changePasswordFailed: '修改密码失败'
    },
    dashboard: {
      title: '域名管理',
      addDomain: '新增域名',
      loadingDomains: '正在加载域名...',
      empty: '还没有配置任何域名。',
      createFirstDomain: '创建第一个域名',
      ssl: 'SSL',
      serverName: 'Server Name',
      port: '端口',
      locations: 'Location 数量',
      edit: '编辑',
      delete: '删除',
      confirmDeletion: '确认删除',
      deleteConfirmText: '确定要删除 {name} 吗？',
      deleteWarning: '这会删除对应 Nginx 配置文件，且无法撤销。',
      loadFailed: '加载域名失败',
      deleteFailed: '删除域名失败'
    },
    domainEditor: {
      newDomain: '新建域名',
      editDomain: '编辑域名',
      serverConfig: 'Server 配置',
      domainName: '域名',
      serverName: 'Server Name',
      listenPort: '监听端口',
      configFilenameHint: '该值将作为配置文件名',
      serverNameHint: '多个 server_name 使用空格分隔',
      enableHttps: '启用 HTTPS（Certbot）',
      enablingSsl: '正在启用 SSL...',
      locationBlocks: 'Location 配置块',
      addLocation: '新增 Location',
      noLocations: '暂无 Location 配置',
      domainRequired: '域名和 Server Name 不能为空',
      needOneLocation: '至少需要一个 location',
      saveFailed: '保存域名失败',
      loadFailed: '加载域名失败',
      sslEnableFailed: '启用 SSL 失败',
      sslEnabledSuccess: 'SSL 证书申请成功！',
      domainCreatedSuccess: '域名创建成功！',
      domainUpdatedSuccess: '域名更新成功！',
      saving: '保存中...'
    },
    location: {
      title: 'Location: {path}',
      advancedMode: '高级模式',
      locationPath: 'Location 路径',
      matchModifier: '匹配修饰符',
      forwardType: '转发类型',
      proxyPass: 'Proxy Pass',
      rootPath: 'Root 路径',
      targetBackendHint: '目标后端地址（例如 http://127.0.0.1:8080）',
      rootPathHint: '用于提供静态文件的本地目录路径',
      templateApplied: '已应用标准模板：',
      customConfig: '自定义配置',
      customConfigPlaceholder: '输入自定义 Nginx 指令...',
      customConfigHint: '填写原生 Nginx 指令（不包含 location 包裹）',
      commonDirectives: '常用 Nginx 指令',
      proxyDirectives: '代理相关指令：',
      staticDirectives: '静态文件指令：',
      securityDirectives: '安全相关：',
      proxyHeaders: '代理头（Host、X-Real-IP、X-Forwarded-For 等）',
      proxyTimeouts: '超时：connect/send/read 1200s',
      proxyBodySize: '请求体大小：500m',
      proxyKeepalive: '长连接：300s',
      staticIndexes: '索引文件：index.html、index.htm',
      modifiers: {
        prefixDefault: '前缀匹配（默认）',
        exact: '=（精确匹配）',
        prefixNoRegex: '^~（前缀匹配，不再匹配正则）',
        regexCaseSensitive: '~（正则，区分大小写）',
        regexCaseInsensitive: '~*（正则，不区分大小写）'
      },
      forwardTypes: {
        dynamic: '动态代理（Proxy）',
        static: '静态文件（File Serving）'
      }
    },
    users: {
      title: '用户管理',
      addUser: '新增用户',
      loadingUsers: '正在加载用户...',
      username: '用户名',
      type: '类型',
      accessibleDomains: '可访问域名',
      created: '创建时间',
      actions: '操作',
      superuser: '超级管理员',
      user: '普通用户',
      all: '全部',
      editPermissions: '编辑权限',
      addNewUser: '新增用户',
      editPermissionsTitle: '编辑权限：{username}',
      password: '密码',
      atLeast6: '至少 6 个字符',
      enterUsername: '请输入用户名',
      createUser: '创建用户',
      creating: '创建中...',
      updatePermissions: '更新权限',
      updating: '更新中...',
      loadFailed: '加载数据失败',
      createFailed: '创建用户失败',
      updateFailed: '更新权限失败',
      usernamePasswordRequired: '用户名和密码不能为空',
      passwordTooShort: '密码至少需要 6 个字符'
    }
  }
}

const i18nState = reactive({
  language: 'en'
})

function detectLanguage() {
  const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY)
  if (SUPPORTED_LANGUAGES.includes(stored)) {
    return stored
  }

  const browser = (navigator.language || 'en').toLowerCase()
  return browser.startsWith('zh') ? 'zh' : 'en'
}

function resolveKey(obj, path) {
  return path.split('.').reduce((acc, key) => {
    if (acc && Object.prototype.hasOwnProperty.call(acc, key)) {
      return acc[key]
    }
    return undefined
  }, obj)
}

function interpolate(template, params) {
  return template.replace(/\{(\w+)\}/g, (_, key) => {
    if (Object.prototype.hasOwnProperty.call(params, key)) {
      return String(params[key])
    }
    return `{${key}}`
  })
}

export function getLanguage() {
  return i18nState.language
}

export function setLanguage(language) {
  const normalized = SUPPORTED_LANGUAGES.includes(language) ? language : 'en'
  i18nState.language = normalized
  localStorage.setItem(LANGUAGE_STORAGE_KEY, normalized)
}

export function t(key, params = {}) {
  const current = messages[i18nState.language] || messages.en
  const fallback = messages.en
  const value = resolveKey(current, key) ?? resolveKey(fallback, key)

  if (typeof value !== 'string') {
    return key
  }

  return interpolate(value, params)
}

setLanguage(detectLanguage())

export default {
  install(app) {
    app.config.globalProperties.$t = t
    app.config.globalProperties.$setLanguage = setLanguage
    app.config.globalProperties.$getLanguage = getLanguage
    app.config.globalProperties.$i18nState = i18nState
  }
}
