# System Architecture - Nginx Configerrrrrr

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
│                     (http://localhost:3000)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP Requests
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Vue.js 3 Frontend                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Components                                              │  │
│  │  ├── Login.vue (Authentication)                         │  │
│  │  ├── Dashboard.vue (Domain List)                        │  │
│  │  ├── DomainEditor.vue (Config Editor)                   │  │
│  │  ├── AdminPanel.vue (User Management)                   │  │
│  │  └── ChangePassword.vue (Password Change)               │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Router (Vue Router)                                     │  │
│  │  ├── Route Guards (Auth Check)                          │  │
│  │  └── Navigation Logic                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Client (Axios)                                      │  │
│  │  ├── Request Interceptor (Add JWT)                      │  │
│  │  ├── Response Interceptor (Handle Errors)               │  │
│  │  └── API Methods                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ /api/* requests
                             │ (with JWT token)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Python Flask Backend                         │
│                     (http://localhost:5000)                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  app.py (Main Application)                               │  │
│  │  ├── Route Handlers                                      │  │
│  │  ├── JWT Middleware                                      │  │
│  │  └── CORS Configuration                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  auth.py (Authentication Layer)                          │  │
│  │  ├── @login_required decorator                          │  │
│  │  ├── @superuser_required decorator                      │  │
│  │  └── Permission Checking                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  models.py (Database Layer)                              │  │
│  │  ├── User Model (SQLAlchemy)                            │  │
│  │  ├── Domain Model (SQLAlchemy)                          │  │
│  │  └── Relationships                                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  nginx_parser.py (Config Parser)                         │  │
│  │  ├── Parse existing configs                             │  │
│  │  ├── Extract server blocks                              │  │
│  │  └── Generate new configs                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  nginx_manager.py (File Operations)                      │  │
│  │  ├── Read/Write config files                            │  │
│  │  ├── Run nginx -t (validation)                          │  │
│  │  ├── Run nginx -s reload                                │  │
│  │  └── Backup/Restore logic                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└───────┬────────────────────────────┬────────────────────────────┘
        │                            │
        │                            │
        ▼                            ▼
┌───────────────────┐      ┌──────────────────────────┐
│   SQLite DB       │      │    Nginx System          │
│                   │      │                          │
│ ┌───────────────┐ │      │  /etc/nginx/conf.d/      │
│ │ Users Table   │ │      │  ├── domain1.conf        │
│ │ ├── id        │ │      │  ├── domain2.conf        │
│ │ ├── username  │ │      │  └── domain3.conf        │
│ │ ├── password  │ │      │                          │
│ │ └── is_super  │ │      │  nginx process           │
│ └───────────────┘ │      │  ├── Validation          │
│ ┌───────────────┐ │      │  ├── Reload              │
│ │ Domains Table │ │      │  └── Serving traffic     │
│ │ ├── id        │ │      └──────────────────────────┘
│ │ ├── name      │ │
│ │ ├── mode      │ │
│ │ ├── config    │ │
│ │ └── owner_id  │ │
│ └───────────────┘ │
│ ┌───────────────┐ │
│ │ user_domains  │ │
│ │ (Many-to-Many)│ │
│ └───────────────┘ │
└───────────────────┘
```

## Request Flow Examples

### 1. User Login Flow

```
Browser                 Frontend              Backend              Database
   │                       │                     │                    │
   │  Enter credentials    │                     │                    │
   ├──────────────────────>│                     │                    │
   │                       │  POST /api/auth/login                    │
   │                       ├────────────────────>│                    │
   │                       │                     │  Query user        │
   │                       │                     ├───────────────────>│
   │                       │                     │<───────────────────┤
   │                       │                     │  Verify password   │
   │                       │                     │  Generate JWT      │
   │                       │<────────────────────┤                    │
   │  Store token & user   │                     │                    │
   │<──────────────────────┤                     │                    │
   │  Redirect to dashboard│                     │                    │
   │                       │                     │                    │
```