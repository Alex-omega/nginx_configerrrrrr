# Nginx Configerrrrrr

A comprehensive web-based Nginx configuration manager built with Python Flask and Vue.js.

## 📋 Features

- 🔐 **Secure Authentication** - Role-based access with forced password change on first login
- 🌐 **Visual Config Editor** - Intuitive interface for managing Nginx configurations
- 📝 **Config Import** - Parse and import existing Nginx configurations automatically
- 🔒 **SSL Automation** - Integrated Certbot for automatic SSL certificate management
- 👥 **Multi-User Support** - Granular permissions per domain
- ✅ **Live Validation** - Real-time Nginx configuration testing
- 📊 **Log Management** - Per-domain access and error logs

## 🎯 System Requirements

- **OS**: Linux (Ubuntu 20.04+, Debian 10+, CentOS 8+)
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Nginx**: Installed and running
- **Certbot**: Optional, for SSL automation
- **Permissions**: Must run as root

## 🚀 Installation

### Step 1: Prepare the System

```bash
# Install system dependencies
sudo apt update
sudo apt install -y python3 python3-pip nginx certbot python3-certbot-nginx

# Install Node.js (if not already installed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

### Step 2: Setup the Project

```bash
# Navigate to installation directory
cd /opt
sudo mkdir nginx-configerrrrrr
cd nginx-configerrrrrr

# Copy all project files here
# (Make sure all files from this project are in this directory)
```

### Step 3: Backend Setup

```bash
cd backend
sudo pip3 install -r requirements.txt
```

### Step 4: Frontend Setup

```bash
cd ../frontend
npm install
npm run build
```

### Step 5: Initialize Database

```bash
cd ..
sudo python3 pre_run.py
```

This script will:
- Scan `/etc/nginx/conf.d/*.conf` for existing configurations
- Parse and import them into the database
- Standardize configuration file formatting
- Create necessary log directories

### Step 6: Start the Application

```bash
cd backend
sudo python3 app.py
```

The application will start on `http://0.0.0.0:5000`

## 🔑 First Login

Access the application at `http://your-server-ip:5000`

**Default Credentials:**
- Username: `root_alex`
- Password: `123456`

⚠️ **You will be forced to change the password immediately after the first login.**

## 📁 Project Structure

```
nginx-configerrrrrr/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models (User, Domain, Location)
│   ├── utils.py            # Config generation, Nginx/Certbot management
│   ├── config.py           # Application configuration
│   ├── nginx_parser.py     # Nginx configuration parser
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── main.js         # Vue application entry
│   │   ├── App.vue         # Root component with navigation
│   │   ├── router.js       # Vue Router configuration
│   │   ├── api.js          # API client with Axios
│   │   └── components/
│   │       ├── Login.vue           # Login & password change
│   │       ├── Dashboard.vue       # Domain list view
│   │       ├── DomainEditor.vue    # Domain configuration editor
│   │       ├── LocationBlock.vue   # Location block component
│   │       └── UserManager.vue     # User management (superuser only)
│   ├── index.html          # HTML template
│   ├── package.json        # Node dependencies
│   └── vite.config.js      # Vite build configuration
├── pre_run.py              # Database initialization script
└── README.md               # This file
```

## 💡 Usage Guide

### Managing Domains

#### Create a New Domain

1. Click "Add Domain" on the dashboard
2. Enter domain name (e.g., `example.com`)
3. Configure server name (can include multiple: `example.com www.example.com`)
4. Set listen port (default: 80)
5. Configure location blocks:
   - **Path**: URL path (e.g., `/`, `/api`, `/static`)
   - **Match Modifier**: Choose matching type (Exact, Prefix, Regex, etc.)
   - **Mode**: Basic or Advanced
6. Save & Apply

#### Basic vs Advanced Mode

**Basic Mode** (Recommended for most users):
- Simple form-based configuration
- Choose between:
  - **Dynamic (Proxy)**: Forward to backend server (e.g., `http://127.0.0.1:3000`)
  - **Static (Files)**: Serve files from directory (e.g., `/var/www/html`)
- Pre-configured optimal settings:
  - Proxy headers
  - Timeouts (1200s)
  - Max body size (500MB)
  - Keep-alive (300s)

**Advanced Mode** (For experts):
- Full control over all Nginx directives
- Write raw configuration
- Access to all Nginx parameters
- Helpful documentation included

#### Enable SSL/HTTPS

1. Open a domain in the editor
2. Click "Enable HTTPS (Certbot)" button
3. Certbot will automatically:
   - Obtain an SSL certificate from Let's Encrypt
   - Configure Nginx for HTTPS
   - Set up automatic renewal

### User Management (Superuser Only)

1. Navigate to "Users" in the navigation menu
2. Click "Add User"
3. Enter username and password
4. Select which domains the user can access
5. Save

**Permission Levels:**
- **Superuser**: Full access to all domains and user management
- **Regular User**: Can only see and edit assigned domains

## 🔧 Configuration Modes Explained

### Location Match Modifiers

- **Prefix (default)**: Matches URLs starting with the path
- **= (Exact)**: Only exact matches
- **^~ (Prefix, no regex)**: Prefix match, stops regex searching
- **~ (Regex)**: Regular expression, case-sensitive
- **~* (Regex, case-insensitive)**: Regular expression, case-insensitive

### Forward Types

**Dynamic (Proxy Pass)**:
```nginx
location / {
    proxy_pass http://127.0.0.1:8080;
    proxy_set_header Host $host;
    # ... (standard template applied)
}
```

**Static (File Serving)**:
```nginx
location / {
    root /var/www/html;
    index index.html index.htm;
}
```

## 🗂️ File Locations

- **Nginx Configs**: `/etc/nginx/conf.d/<domain>.conf`
- **Logs**: `/var/log/nginx/<domain>/access.log` and `error.log`
- **Database**: `backend/nginx_manager.db`

## 🛠️ Troubleshooting

### Nginx Configuration Test Fails

```bash
# Check Nginx error log
sudo tail -f /var/log/nginx/error.log

# Test configuration manually
sudo nginx -t
```

### Permission Denied Errors

Ensure the application is running as root:
```bash
sudo python3 backend/app.py
```

### SSL Certificate Issues

```bash
# Check Certbot logs
sudo tail -f /var/log/letsencrypt/letsencrypt.log

# Test certificate renewal
sudo certbot renew --dry-run
```

### Database Issues

Reset the database (⚠️ This will delete all data):
```bash
sudo rm backend/nginx_manager.db
sudo python3 pre_run.py
```

## 🔒 Security Recommendations

1. **Change Default Password**: Always change `root_alex` password immediately
2. **Use Strong Passwords**: Minimum 12 characters with mixed case, numbers, symbols
3. **Firewall**: Limit access to port 5000 to trusted IPs
4. **HTTPS**: Run the management interface behind HTTPS
5. **Regular Backups**: Backup `nginx_manager.db` regularly
6. **Review Logs**: Monitor `/var/log/nginx/` for suspicious activity

## 📊 API Endpoints

### Authentication
- `POST /api/login` - User login
- `POST /api/change-password` - Change password

### Domains
- `GET /api/domains` - List all accessible domains
- `GET /api/domains/<id>` - Get a single domain
- `POST /api/domains` - Create a new domain
- `PUT /api/domains/<id>` - Update a domain
- `DELETE /api/domains/<id>` - Delete a domain
- `POST /api/domains/<id>/ssl` - Enable SSL with Certbot

### Users (Superuser Only)
- `GET /api/users` - List all users
- `POST /api/users` - Create a new user
- `PUT /api/users/<id>` - Update user permissions

## 🚀 Production Deployment

For production use:

1. **Use a Process Manager** (systemd, supervisor)
2. **Run Behind a Reverse Proxy** (Nginx with SSL)
3. **Set a Strong Secret Key** in `backend/config.py`
4. **Enable Firewall** (UFW, iptables)
5. **Regular Backups** of database and configs
6. **Monitor Logs** for errors and security issues

### Example Systemd Service

```ini
[Unit]
Description=Nginx Configerrrrrr
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/nginx-configerrrrrr/backend
ExecStart=/usr/bin/python3 /opt/nginx-configerrrrrr/backend/app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Save to `/etc/systemd/system/nginx-manager.service`, then:
```bash
sudo systemctl enable nginx-manager
sudo systemctl start nginx-manager
```

## 📝 License

MIT License - Use at your own risk

## ⚠️ Disclaimer

This tool modifies Nginx configuration files and reloads the Nginx service. Test thoroughly in a development environment before using in production. Always maintain backups of your configurations.

## 🤝 Support

For issues, questions, or contributions:
- Check Nginx logs: `/var/log/nginx/`
- Check application logs
- Review configuration test output

---

**Built with ❤️ for simplified Nginx management**