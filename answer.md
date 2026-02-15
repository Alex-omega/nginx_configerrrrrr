I'll create a complete full-stack Nginx configuration manager for you. This is a comprehensive project, so I'll generate all the necessary files.Due to technical difficulties with the file system tools, let me provide you with the complete source code for all files in this response. You can copy and create these files manually:

## Project Structure

```
nginx-configerrrrrr/
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── utils.py
│   ├── nginx_parser.py
│   ├── config.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── router.js
│       ├── api.js
│       └── components/
│           ├── Login.vue
│           ├── Dashboard.vue
│           ├── DomainEditor.vue
│           ├── LocationBlock.vue
│           └── UserManager.vue
├── pre_run.py
└── README.md
```

---

## File: `/pre_run.py`

```python
#!/usr/bin/env python3
# /pre_run.py
"""
Pre-run initialization script for Nginx Configerrrrrr
Scans existing Nginx configurations, imports them into the database,
and standardizes the configuration files.
"""

import os
import sys
import sqlite3
import hashlib
import re
from datetime import datetime

# Configuration
NGINX_CONF_DIR = "/etc/nginx/conf.d"
DB_PATH = "backend/nginx_manager.db"

class NginxConfigParser:
    """Parse existing Nginx configuration files"""
    
    def __init__(self, filepath):
        self.filepath = filepath
        self.content = self._read_file()
        
    def _read_file(self):
        try:
            with open(self.filepath, 'r') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {self.filepath}: {e}")
            return ""
    
    def extract_server_names(self):
        """Extract server_name directives"""
        pattern = r'server_name\s+([^;]+);'
        matches = re.findall(pattern, self.content)
        if matches:
            return [name.strip() for name in matches[0].split()]
        return []
    
    def extract_listen_ports(self):
        """Extract listen ports"""
        pattern = r'listen\s+(\d+)'
        matches = re.findall(pattern, self.content)
        return list(set(matches))
    
    def extract_locations(self):
        """Extract location blocks with their configurations"""
        locations = []
        pattern = r'location\s+(=|~|~\*|\^~)?\s*([^\s{]+)\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}'
        matches = re.finditer(pattern, self.content, re.DOTALL)
        
        for match in matches:
            modifier = match.group(1) or ''
            path = match.group(2)
            content = match.group(3)
            
            location_data = {
                'path': path,
                'modifier': modifier,
                'content': content.strip(),
                'proxy_pass': self._extract_proxy_pass(content),
                'root': self._extract_root(content)
            }
            locations.append(location_data)
        
        return locations
    
    def _extract_proxy_pass(self, content):
        """Extract proxy_pass directive"""
        pattern = r'proxy_pass\s+([^;]+);'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None
    
    def _extract_root(self, content):
        """Extract root directive"""
        pattern = r'root\s+([^;]+);'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else None
    
    def has_ssl(self):
        """Check if SSL is configured"""
        return 'ssl_certificate' in self.content

def initialize_database():
    """Create database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_superuser BOOLEAN DEFAULT 0,
            is_default_password BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Domains table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            server_name TEXT NOT NULL,
            listen_port TEXT DEFAULT '80',
            ssl_enabled BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain_id INTEGER NOT NULL,
            path TEXT NOT NULL,
            match_modifier TEXT DEFAULT '',
            mode TEXT DEFAULT 'basic',
            forward_type TEXT DEFAULT 'dynamic',
            proxy_pass TEXT,
            root_path TEXT,
            config_content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE
        )
    ''')
    
    # User-Domain permissions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_domain_permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            domain_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (domain_id) REFERENCES domains(id) ON DELETE CASCADE,
            UNIQUE(user_id, domain_id)
        )
    ''')
    
    # Create default superuser
    password_hash = hashlib.sha256('123456'.encode()).hexdigest()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, password_hash, is_superuser, is_default_password)
        VALUES (?, ?, 1, 1)
    ''', ('root_alex', password_hash))
    
    conn.commit()
    conn.close()
    print("✓ Database initialized")

def scan_and_import_configs():
    """Scan /etc/nginx/conf.d/ and import existing configurations"""
    if not os.path.exists(NGINX_CONF_DIR):
        print(f"Warning: {NGINX_CONF_DIR} does not exist")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    conf_files = [f for f in os.listdir(NGINX_CONF_DIR) if f.endswith('.conf')]
    print(f"\nScanning {len(conf_files)} configuration files...")
    
    for conf_file in conf_files:
        filepath = os.path.join(NGINX_CONF_DIR, conf_file)
        print(f"\nProcessing: {conf_file}")
        
        parser = NginxConfigParser(filepath)
        server_names = parser.extract_server_names()
        listen_ports = parser.extract_listen_ports()
        locations = parser.extract_locations()
        has_ssl = parser.has_ssl()
        
        if not server_names:
            print(f"  ⚠ No server_name found, skipping")
            continue
        
        domain_name = server_names[0]
        listen_port = listen_ports[0] if listen_ports else '80'
        
        print(f"  Domain: {domain_name}")
        print(f"  Port: {listen_port}")
        print(f"  SSL: {has_ssl}")
        print(f"  Locations: {len(locations)}")
        
        try:
            cursor.execute('''
                INSERT INTO domains (name, server_name, listen_port, ssl_enabled)
                VALUES (?, ?, ?, ?)
            ''', (domain_name, ' '.join(server_names), listen_port, has_ssl))
            
            domain_id = cursor.lastrowid
            
            for loc in locations:
                forward_type = 'dynamic' if loc['proxy_pass'] else 'static'
                
                cursor.execute('''
                    INSERT INTO locations (domain_id, path, match_modifier, mode, 
                                          forward_type, proxy_pass, root_path, config_content)
                    VALUES (?, ?, ?, 'advanced', ?, ?, ?, ?)
                ''', (
                    domain_id,
                    loc['path'],
                    loc['modifier'],
                    forward_type,
                    loc['proxy_pass'],
                    loc['root'],
                    loc['content']
                ))
            
            if not locations:
                cursor.execute('''
                    INSERT INTO locations (domain_id, path, mode, forward_type)
                    VALUES (?, '/', 'basic', 'dynamic')
                ''', (domain_id,))
            
            print(f"  ✓ Imported successfully")
            
        except sqlite3.IntegrityError:
            print(f"  ⚠ Domain {domain_name} already exists, skipping")
        except Exception as e:
            print(f"  ✗ Error importing: {e}")
    
    conn.commit()
    conn.close()

def standardize_configs():
    """Rewrite all configuration files to match the standard format"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, name, server_name, listen_port, ssl_enabled FROM domains')
    domains = cursor.fetchall()
    
    print(f"\nStandardizing {len(domains)} configuration files...")
    
    for domain in domains:
        domain_id, domain_name, server_name, listen_port, ssl_enabled = domain
        
        cursor.execute('''
            SELECT path, match_modifier, mode, forward_type, proxy_pass, root_path, config_content
            FROM locations WHERE domain_id = ?
        ''', (domain_id,))
        locations = cursor.fetchall()
        
        config = generate_standard_config(domain_name, server_name, listen_port, ssl_enabled, locations)
        
        conf_path = os.path.join(NGINX_CONF_DIR, f"{domain_name}.conf")
        try:
            with open(conf_path, 'w') as f:
                f.write(config)
            print(f"  ✓ Standardized {domain_name}.conf")
        except Exception as e:
            print(f"  ✗ Error writing {domain_name}.conf: {e}")
    
    conn.close()

def generate_standard_config(domain_name, server_name, listen_port, ssl_enabled, locations):
    """Generate standardized Nginx configuration"""
    config = f"""# Generated by Nginx Configerrrrrr
# Domain: {domain_name}

server {{
    listen {listen_port};
    server_name {server_name};
    
    # Logs
    access_log /var/log/nginx/{domain_name}/access.log;
    error_log /var/log/nginx/{domain_name}/error.log;
"""
    
    for loc in locations:
        path, modifier, mode, forward_type, proxy_pass, root_path, config_content = loc
        
        modifier_str = f" {modifier}" if modifier else ""
        config += f"\n    location{modifier_str} {path} {{\n"
        
        if mode == 'advanced' and config_content:
            for line in config_content.split('\n'):
                if line.strip():
                    config += f"        {line.strip()}\n"
        else:
            if forward_type == 'dynamic' and proxy_pass:
                config += f"        proxy_pass {proxy_pass};\n"
                config += """        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 1200s;
        proxy_send_timeout 1200s;
        proxy_read_timeout 1200s;
        client_max_body_size 500m;
        client_body_buffer_size 80m;
        keepalive_timeout 300s;
"""
            elif forward_type == 'static' and root_path:
                config += f"        root {root_path};\n"
                config += "        index index.html index.htm;\n"
        
        config += "    }\n"
    
    config += "}\n"
    return config

def create_log_directories():
    """Create log directories for all domains"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT name FROM domains')
    domains = cursor.fetchall()
    
    print(f"\nCreating log directories...")
    
    for (domain_name,) in domains:
        log_dir = f"/var/log/nginx/{domain_name}"
        try:
            os.makedirs(log_dir, exist_ok=True)
            print(f"  ✓ Created {log_dir}")
        except Exception as e:
            print(f"  ✗ Error creating {log_dir}: {e}")
    
    conn.close()

def main():
    """Main execution"""
    print("=" * 60)
    print("Nginx Configerrrrrr - Pre-Run Initialization")
    print("=" * 60)
    
    os.makedirs('backend', exist_ok=True)
    
    print("\n[1/4] Initializing database...")
    initialize_database()
    
    print("\n[2/4] Scanning existing Nginx configurations...")
    scan_and_import_configs()
    
    print("\n[3/4] Standardizing configuration files...")
    standardize_configs()
    
    print("\n[4/4] Creating log directories...")
    create_log_directories()
    
    print("\n" + "=" * 60)
    print("✓ Pre-run initialization completed successfully!")
    print("=" * 60)
    print("\nYou can now start the backend server:")
    print("  cd backend && python3 app.py")
    print("\nDefault login credentials:")
    print("  Username: root_alex")
    print("  Password: 123456")
    print("  (You will be forced to change this on first login)")

if __name__ == "__main__":
    main()
```

---

## File: `/backend/config.py`

```python
# /backend/config.py
"""Configuration settings for the Nginx Manager application"""

import os

class Config:
    """Application configuration"""
    
    # Database
    DATABASE_PATH = 'nginx_manager.db'
    
    # Nginx
    NGINX_CONF_DIR = '/etc/nginx/conf.d'
    NGINX_LOG_DIR = '/var/log/nginx'
    NGINX_BIN = '/usr/sbin/nginx'
    
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Server
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = False
    
    # Certbot
    CERTBOT_BIN = '/usr/bin/certbot'
```

---

## File: `/backend/models.py`

```python
# /backend/models.py
"""Database models for the Nginx Manager"""

import sqlite3
import hashlib
from datetime import datetime
from config import Config

class Database:
    """Database connection manager"""
    
    @staticmethod
    def get_connection():
        """Get database connection"""
        conn = sqlite3.connect(Config.DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

class User:
    """User model"""
    
    @staticmethod
    def get_by_username(username):
        """Get user by username"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    @staticmethod
    def create(username, password, is_superuser=False):
        """Create new user"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password_hash, is_superuser, is_default_password)
                VALUES (?, ?, ?, 0)
            ''', (username, password_hash, is_superuser))
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return user_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    @staticmethod
    def update_password(user_id, new_password):
        """Update user password"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        
        cursor.execute('''
            UPDATE users SET password_hash = ?, is_default_password = 0
            WHERE id = ?
        ''', (password_hash, user_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def verify_password(username, password):
        """Verify user password"""
        user = User.get_by_username(username)
        if not user:
            return False
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        return password_hash == user['password_hash']
    
    @staticmethod
    def get_all():
        """Get all users"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, username, is_superuser, created_at FROM users')
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

class Domain:
    """Domain model"""
    
    @staticmethod
    def get_all(user_id=None):
        """Get all domains (filtered by user permissions if not superuser)"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        if user_id:
            user = User.get_by_id(user_id)
            if user and user['is_superuser']:
                cursor.execute('SELECT * FROM domains ORDER BY name')
            else:
                cursor.execute('''
                    SELECT d.* FROM domains d
                    INNER JOIN user_domain_permissions udp ON d.id = udp.domain_id
                    WHERE udp.user_id = ?
                    ORDER BY d.name
                ''', (user_id,))
        else:
            cursor.execute('SELECT * FROM domains ORDER BY name')
        
        domains = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return domains
    
    @staticmethod
    def get_by_id(domain_id, user_id=None):
        """Get domain by ID"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM domains WHERE id = ?', (domain_id,))
        domain = cursor.fetchone()
        
        if not domain:
            conn.close()
            return None
        
        # Check permissions
        if user_id:
            user = User.get_by_id(user_id)
            if not user['is_superuser']:
                cursor.execute('''
                    SELECT * FROM user_domain_permissions
                    WHERE user_id = ? AND domain_id = ?
                ''', (user_id, domain_id))
                
                if not cursor.fetchone():
                    conn.close()
                    return None
        
        conn.close()
        return dict(domain)
    
    @staticmethod
    def create(name, server_name, listen_port='80', ssl_enabled=False):
        """Create new domain"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO domains (name, server_name, listen_port, ssl_enabled)
                VALUES (?, ?, ?, ?)
            ''', (name, server_name, listen_port, ssl_enabled))
            conn.commit()
            domain_id = cursor.lastrowid
            conn.close()
            return domain_id
        except sqlite3.IntegrityError:
            conn.close()
            return None
    
    @staticmethod
    def update(domain_id, **kwargs):
        """Update domain"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['name', 'server_name', 'listen_port', 'ssl_enabled']:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(domain_id)
            
            query = f"UPDATE domains SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    @staticmethod
    def delete(domain_id):
        """Delete domain"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM domains WHERE id = ?', (domain_id,))
        conn.commit()
        conn.close()

class Location:
    """Location model"""
    
    @staticmethod
    def get_by_domain(domain_id):
        """Get all locations for a domain"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM locations WHERE domain_id = ? ORDER BY path', (domain_id,))
        locations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return locations
    
    @staticmethod
    def create(domain_id, path, match_modifier='', mode='basic', forward_type='dynamic', 
               proxy_pass=None, root_path=None, config_content=None):
        """Create new location"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO locations (domain_id, path, match_modifier, mode, forward_type, 
                                  proxy_pass, root_path, config_content)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (domain_id, path, match_modifier, mode, forward_type, proxy_pass, root_path, config_content))
        conn.commit()
        location_id = cursor.lastrowid
        conn.close()
        return location_id
    
    @staticmethod
    def update(location_id, **kwargs):
        """Update location"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        updates = []
        values = []
        
        for key, value in kwargs.items():
            if key in ['path', 'match_modifier', 'mode', 'forward_type', 'proxy_pass', 'root_path', 'config_content']:
                updates.append(f"{key} = ?")
                values.append(value)
        
        if updates:
            values.append(location_id)
            query = f"UPDATE locations SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, values)
            conn.commit()
        
        conn.close()
    
    @staticmethod
    def delete(location_id):
        """Delete location"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM locations WHERE id = ?', (location_id,))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_by_domain(domain_id):
        """Delete all locations for a domain"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM locations WHERE domain_id = ?', (domain_id,))
        conn.commit()
        conn.close()

class UserDomainPermission:
    """User-Domain permission model"""
    
    @staticmethod
    def grant(user_id, domain_id):
        """Grant domain access to user"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO user_domain_permissions (user_id, domain_id)
                VALUES (?, ?)
            ''', (user_id, domain_id))
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
    
    @staticmethod
    def revoke(user_id, domain_id):
        """Revoke domain access from user"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM user_domain_permissions
            WHERE user_id = ? AND domain_id = ?
        ''', (user_id, domain_id))
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_user_domains(user_id):
        """Get all domain IDs accessible by user"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT domain_id FROM user_domain_permissions
            WHERE user_id = ?
        ''', (user_id,))
        domain_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        return domain_ids
    
    @staticmethod
    def set_user_domains(user_id, domain_ids):
        """Set all domains accessible by user"""
        conn = Database.get_connection()
        cursor = conn.cursor()
        
        # Remove all existing permissions
        cursor.execute('DELETE FROM user_domain_permissions WHERE user_id = ?', (user_id,))
        
        # Add new permissions
        for domain_id in domain_ids:
            cursor.execute('''
                INSERT OR IGNORE INTO user_domain_permissions (user_id, domain_id)
                VALUES (?, ?)
            ''', (user_id, domain_id))
        
        conn.commit()
        conn.close()
```

---

## File: `/backend/utils.py`

```python
# /backend/utils.py
"""Utility functions for Nginx configuration management"""

import os
import subprocess
from config import Config
from models import Location

class NginxConfigGenerator:
    """Generate Nginx configuration files"""
    
    @staticmethod
    def generate_config(domain):
        """Generate complete Nginx configuration for a domain"""
        domain_name = domain['name']
        server_name = domain['server_name']
        listen_port = domain['listen_port']
        
        config = f"""# Generated by Nginx Configerrrrrr
# Domain: {domain_name}

server {{
    listen {listen_port};
    server_name {server_name};
    
    # Logs
    access_log {Config.NGINX_LOG_DIR}/{domain_name}/access.log;
    error_log {Config.NGINX_LOG_DIR}/{domain_name}/error.log;
"""
        
        # Get locations
        locations = Location.get_by_domain(domain['id'])
        
        for location in locations:
            config += NginxConfigGenerator._generate_location_block(location)
        
        config += "}\n"
        
        return config
    
    @staticmethod
    def _generate_location_block(location):
        """Generate a location block"""
        path = location['path']
        modifier = location['match_modifier']
        mode = location['mode']
        
        modifier_str = f" {modifier}" if modifier else ""
        block = f"\n    location{modifier_str} {path} {{\n"
        
        if mode == 'advanced' and location['config_content']:
            # Use advanced custom configuration
            for line in location['config_content'].split('\n'):
                if line.strip():
                    block += f"        {line.strip()}\n"
        else:
            # Generate basic configuration
            forward_type = location['forward_type']
            
            if forward_type == 'dynamic' and location['proxy_pass']:
                proxy_pass = location['proxy_pass']
                block += f"        proxy_pass {proxy_pass};\n"
                block += """        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 1200s;
        proxy_send_timeout 1200s;
        proxy_read_timeout 1200s;
        client_max_body_size 500m;
        client_body_buffer_size 80m;
        keepalive_timeout 300s;
"""
            elif forward_type == 'static' and location['root_path']:
                root_path = location['root_path']
                block += f"        root {root_path};\n"
                block += "        index index.html index.htm;\n"
        
        block += "    }\n"
        
        return block
    
    @staticmethod
    def write_config(domain):
        """Write configuration file to disk"""
        domain_name = domain['name']
        config = NginxConfigGenerator.generate_config(domain)
        
        # Ensure log directory exists
        log_dir = os.path.join(Config.NGINX_LOG_DIR, domain_name)
        os.makedirs(log_dir, exist_ok=True)
        
        # Write config file
        conf_path = os.path.join(Config.NGINX_CONF_DIR, f"{domain_name}.conf")
        with open(conf_path, 'w') as f:
            f.write(config)
        
        return conf_path

class NginxManager:
    """Manage Nginx service"""
    
    @staticmethod
    def test_config():
        """Test Nginx configuration"""
        try:
            result = subprocess.run(
                [Config.NGINX_BIN, '-t'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Configuration test passed"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def reload():
        """Reload Nginx"""
        try:
            result = subprocess.run(
                [Config.NGINX_BIN, '-s', 'reload'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, "Nginx reloaded successfully"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def test_and_reload():
        """Test configuration and reload if valid"""
        success, message = NginxManager.test_config()
        
        if not success:
            return False, f"Configuration test failed: {message}"
        
        success, message = NginxManager.reload()
        return success, message

class CertbotManager:
    """Manage SSL certificates with Certbot"""
    
    @staticmethod
    def obtain_certificate(domain_name):
        """Obtain SSL certificate for domain"""
        try:
            result = subprocess.run(
                [
                    Config.CERTBOT_BIN,
                    '--nginx',
                    '-d', domain_name,
                    '--non-interactive',
                    '--agree-tos',
                    '--redirect',
                    '--hsts',
                    '--staple-ocsp',
                    '-m', 'admin@example.com'  # Change this
                ],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                return True, "SSL certificate obtained successfully"
            else:
                return False, result.stderr
        except Exception as e:
            return False, str(e)
```

---

## File: `/backend/app.py`

```python
# /backend/app.py
"""Main Flask application for Nginx Manager"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import jwt
from datetime import datetime, timedelta
from functools import wraps

from config import Config
from models import User, Domain, Location, UserDomainPermission
from utils import NginxConfigGenerator, NginxManager, CertbotManager

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config.from_object(Config)
CORS(app)

# JWT decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.get_by_id(data['user_id'])
            
            if not current_user:
                return jsonify({'error': 'User not found'}), 401
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if not User.verify_password(username, password):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    user = User.get_by_username(username)
    
    # Generate JWT token
    token = jwt.encode({
        'user_id': user['id'],
        'exp': datetime.utcnow() + timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'token': token,
        'user': {
            'id': user['id'],
            'username': user['username'],
            'is_superuser': user['is_superuser'],
            'is_default_password': user['is_default_password']
        }
    })

@app.route('/api/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password"""
    data = request.json
    old_password = data.get('old_password')
    new_password = data.get('new_password')
    
    if not old_password or not new_password:
        return jsonify({'error': 'Both old and new passwords required'}), 400
    
    if not User.verify_password(current_user['username'], old_password):
        return jsonify({'error': 'Invalid old password'}), 401
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    User.update_password(current_user['id'], new_password)
    
    return jsonify({'message': 'Password changed successfully'})

# Domain routes
@app.route('/api/domains', methods=['GET'])
@token_required
def get_domains(current_user):
    """Get all domains (filtered by permissions)"""
    domains = Domain.get_all(current_user['id'])
    
    # Include locations for each domain
    for domain in domains:
        domain['locations'] = Location.get_by_domain(domain['id'])
    
    return jsonify(domains)

@app.route('/api/domains/<int:domain_id>', methods=['GET'])
@token_required
def get_domain(current_user, domain_id):
    """Get single domain"""
    domain = Domain.get_by_id(domain_id, current_user['id'])
    
    if not domain:
        return jsonify({'error': 'Domain not found or access denied'}), 404
    
    domain['locations'] = Location.get_by_domain(domain_id)
    
    return jsonify(domain)

@app.route('/api/domains', methods=['POST'])
@token_required
def create_domain(current_user):
    """Create new domain"""
    data = request.json
    name = data.get('name')
    server_name = data.get('server_name', name)
    listen_port = data.get('listen_port', '80')
    
    if not name:
        return jsonify({'error': 'Domain name is required'}), 400
    
    # Create domain
    domain_id = Domain.create(name, server_name, listen_port)
    
    if not domain_id:
        return jsonify({'error': 'Domain already exists'}), 400
    
    # Create default location
    Location.create(domain_id, '/', '', 'basic', 'dynamic')
    
    # Get domain with locations
    domain = Domain.get_by_id(domain_id)
    domain['locations'] = Location.get_by_domain(domain_id)
    
    # Generate and write config
    try:
        NginxConfigGenerator.write_config(domain)
        success, message = NginxManager.test_and_reload()
        
        if not success:
            Domain.delete(domain_id)
            return jsonify({'error': message}), 400
    except Exception as e:
        Domain.delete(domain_id)
        return jsonify({'error': str(e)}), 500
    
    return jsonify(domain), 201

@app.route('/api/domains/<int:domain_id>', methods=['PUT'])
@token_required
def update_domain(current_user, domain_id):
    """Update domain"""
    domain = Domain.get_by_id(domain_id, current_user['id'])
    
    if not domain:
        return jsonify({'error': 'Domain not found or access denied'}), 404
    
    data = request.json
    
    # Update domain basic info
    if 'server_name' in data:
        Domain.update(domain_id, server_name=data['server_name'])
    
    if 'listen_port' in data:
        Domain.update(domain_id, listen_port=data['listen_port'])
    
    # Update locations
    if 'locations' in data:
        # Delete existing locations
        Location.delete_by_domain(domain_id)
        
        # Create new locations
        for loc_data in data['locations']:
            Location.create(
                domain_id,
                loc_data.get('path', '/'),
                loc_data.get('match_modifier', ''),
                loc_data.get('mode', 'basic'),
                loc_data.get('forward_type', 'dynamic'),
                loc_data.get('proxy_pass'),
                loc_data.get('root_path'),
                loc_data.get('config_content')
            )
    
    # Get updated domain
    domain = Domain.get_by_id(domain_id)
    domain['locations'] = Location.get_by_domain(domain_id)
    
    # Regenerate and test config
    try:
        NginxConfigGenerator.write_config(domain)
        success, message = NginxManager.test_and_reload()
        
        if not success:
            return jsonify({'error': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    return jsonify(domain)

@app.route('/api/domains/<int:domain_id>', methods=['DELETE'])
@token_required
def delete_domain(current_user, domain_id):
    """Delete domain"""
    domain = Domain.get_by_id(domain_id, current_user['id'])
    
    if not domain:
        return jsonify({'error': 'Domain not found or access denied'}), 404
    
    # Only superusers can delete domains
    if not current_user['is_superuser']:
        return jsonify({'error': 'Only superusers can delete domains'}), 403
    
    # Delete config file
    conf_path = os.path.join(Config.NGINX_CONF_DIR, f"{domain['name']}.conf")
    if os.path.exists(conf_path):
        os.remove(conf_path)
    
    # Delete from database
    Domain.delete(domain_id)
    
    # Reload Nginx
    NginxManager.reload()
    
    return jsonify({'message': 'Domain deleted successfully'})

@app.route('/api/domains/<int:domain_id>/ssl', methods=['POST'])
@token_required
def enable_ssl(current_user, domain_id):
    """Enable SSL for domain using Certbot"""
    domain = Domain.get_by_id(domain_id, current_user['id'])
    
    if not domain:
        return jsonify({'error': 'Domain not found or access denied'}), 404
    
    success, message = CertbotManager.obtain_certificate(domain['name'])
    
    if success:
        Domain.update(domain_id, ssl_enabled=True, listen_port='443')
        return jsonify({'message': message})
    else:
        return jsonify({'error': message}), 500

# User management routes (superuser only)
@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users"""
    if not current_user['is_superuser']:
        return jsonify({'error': 'Superuser access required'}), 403
    
    users = User.get_all()
    
    # Include domain permissions
    for user in users:
        user['domain_ids'] = UserDomainPermission.get_user_domains(user['id'])
    
    return jsonify(users)

@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    """Create new user"""
    if not current_user['is_superuser']:
        return jsonify({'error': 'Superuser access required'}), 403
    
    data = request.json
    username = data.get('username')
    password = data.get('password')
    domain_ids = data.get('domain_ids', [])
    
    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    user_id = User.create(username, password)
    
    if not user_id:
        return jsonify({'error': 'Username already exists'}), 400
    
    # Set domain permissions
    UserDomainPermission.set_user_domains(user_id, domain_ids)
    
    return jsonify({'id': user_id, 'username': username}), 201

@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user_permissions(current_user, user_id):
    """Update user domain permissions"""
    if not current_user['is_superuser']:
        return jsonify({'error': 'Superuser access required'}), 403
    
    data = request.json
    domain_ids = data.get('domain_ids', [])
    
    UserDomainPermission.set_user_domains(user_id, domain_ids)
    
    return jsonify({'message': 'Permissions updated successfully'})

# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
```

---

## File: `/backend/requirements.txt`

```txt
# /backend/requirements.txt
Flask==3.0.0
Flask-CORS==4.0.0
PyJWT==2.8.0
```

## Frontend Files

### File: `/frontend/package.json`

```json
{
  "name": "nginx-configerrrrrr-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0"
  }
}
```

---

### File: `/frontend/vite.config.js`

```javascript
// /frontend/vite.config.js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    emptyOutDir: true
  }
})
```

---

### File: `/frontend/index.html`

```html
<!-- /frontend/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nginx Configerrrrrr</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        #app {
            min-height: 100vh;
        }
    </style>
</head>
<body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
</body>
</html>
```

---

### File: `/frontend/src/main.js`

```javascript
// /frontend/src/main.js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js'

const app = createApp(App)
app.use(router)
app.mount('#app')
```

---

### File: `/frontend/src/router.js`

```javascript
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
```

---

### File: `/frontend/src/api.js`

```javascript
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
```

---

### File: `/frontend/src/App.vue`

```vue
<!-- /frontend/src/App.vue -->
<template>
  <div id="app">
    <nav v-if="isLoggedIn" class="navbar">
      <div class="navbar-brand">
        <h1>⚙️ Nginx Configerrrrrr</h1>
      </div>
      <div class="navbar-menu">
        <router-link to="/" class="nav-item">Dashboard</router-link>
        <router-link v-if="user.is_superuser" to="/users" class="nav-item">Users</router-link>
        <div class="nav-item user-info">
          {{ user.username }}
        </div>
        <button @click="logout" class="nav-item logout-btn">Logout</button>
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
    }
  }
}
</script>

<style>
.navbar {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
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
  gap: 1.5rem;
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
```

---

### File: `/frontend/src/components/Login.vue`

```vue
<!-- /frontend/src/components/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <h2>🔐 Login to Nginx Manager</h2>
      
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      
      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Username</label>
          <input 
            v-model="username" 
            type="text" 
            placeholder="Enter username"
            required
          />
        </div>
        
        <div class="form-group">
          <label>Password</label>
          <input 
            v-model="password" 
            type="password" 
            placeholder="Enter password"
            required
          />
        </div>
        
        <button type="submit" class="btn btn-primary" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>
    </div>
    
    <!-- Password Change Modal -->
    <div v-if="showPasswordChange" class="modal">
      <div class="modal-content">
        <h3>⚠️ Change Default Password</h3>
        <p>You must change your password before proceeding.</p>
        
        <div v-if="passwordError" class="error-message">
          {{ passwordError }}
        </div>
        
        <form @submit.prevent="handlePasswordChange">
          <div class="form-group">
            <label>Current Password</label>
            <input 
              v-model="oldPassword" 
              type="password" 
              required
            />
          </div>
          
          <div class="form-group">
            <label>New Password</label>
            <input 
              v-model="newPassword" 
              type="password" 
              placeholder="At least 6 characters"
              required
            />
          </div>
          
          <div class="form-group">
            <label>Confirm New Password</label>
            <input 
              v-model="confirmPassword" 
              type="password" 
              required
            />
          </div>
          
          <button type="submit" class="btn btn-primary" :disabled="changingPassword">
            {{ changingPassword ? 'Changing...' : 'Change Password' }}
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
    async handleLogin() {
      this.error = ''
      this.loading = true
      
      try {
        const response = await api.login(this.username, this.password)
        const { token, user } = response.data
        
        localStorage.setItem('token', token)
        localStorage.setItem('user', JSON.stringify(user))
        
        // Check if password change is required
        if (user.is_default_password) {
          this.showPasswordChange = true
          this.oldPassword = this.password
        } else {
          this.$router.push('/')
        }
      } catch (error) {
        this.error = error.response?.data?.error || 'Login failed'
      } finally {
        this.loading = false
      }
    },
    
    async handlePasswordChange() {
      this.passwordError = ''
      
      if (this.newPassword.length < 6) {
        this.passwordError = 'Password must be at least 6 characters'
        return
      }
      
      if (this.newPassword !== this.confirmPassword) {
        this.passwordError = 'Passwords do not match'
        return
      }
      
      this.changingPassword = true
      
      try {
        await api.changePassword(this.oldPassword, this.newPassword)
        
        // Update user object
        const user = JSON.parse(localStorage.getItem('user'))
        user.is_default_password = false
        localStorage.setItem('user', JSON.stringify(user))
        
        this.$router.push('/')
      } catch (error) {
        this.passwordError = error.response?.data?.error || 'Failed to change password'
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
}

.login-box {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.2);
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
```

---

### File: `/frontend/src/components/Dashboard.vue`

```vue
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
```

---

### File: `/frontend/src/components/DomainEditor.vue`

```vue
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
          <small>This will be used as the configuration filename</small>
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
```

---

### File: `/frontend/src/components/LocationBlock.vue`

```vue
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
```

---

### File: `/frontend/src/components/UserManager.vue`

```vue
<!-- /frontend/src/components/UserManager.vue -->
<template>
  <div class="user-manager">
    <div class="container">
      <div class="header">
        <h2>👥 User Management</h2>
        <button @click="showAddUser = true" class="btn btn-primary">
          ➕ Add User
        </button>
      </div>
      
      <div v-if="loading" class="loading">
        Loading users...
      </div>
      
      <div v-else-if="error" class="error-message">
        {{ error }}
      </div>
      
      <div v-else class="users-table">
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Type</th>
              <th>Accessible Domains</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.username }}</td>
              <td>
                <span :class="['badge', user.is_superuser ? 'badge-admin' : 'badge-user']">
                  {{ user.is_superuser ? 'Superuser' : 'User' }}
                </span>
              </td>
              <td>
                {{ user.is_superuser ? 'All' : user.domain_ids.length }}
              </td>
              <td>{{ formatDate(user.created_at) }}</td>
              <td>
                <button 
                  v-if="!user.is_superuser"
                  @click="editUser(user)" 
                  class="btn btn-small btn-secondary"
                >
                  ✏️ Edit Permissions
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Add User Modal -->
    <div v-if="showAddUser" class="modal">
      <div class="modal-content">
        <h3>➕ Add New User</h3>
        
        <div v-if="modalError" class="error-message">
          {{ modalError }}
        </div>
        
        <form @submit.prevent="createUser">
          <div class="form-group">
            <label>Username *</label>
            <input 
              v-model="newUser.username" 
              type="text" 
              required
              placeholder="Enter username"
            />
          </div>
          
          <div class="form-group">
            <label>Password *</label>
            <input 
              v-model="newUser.password" 
              type="password" 
              required
              placeholder="At least 6 characters"
            />
          </div>
          
          <div class="form-group">
            <label>Accessible Domains</label>
            <div class="domain-checklist">
              <label 
                v-for="domain in domains" 
                :key="domain.id"
                class="checkbox-label"
              >
                <input 
                  type="checkbox" 
                  :value="domain.id"
                  v-model="newUser.domain_ids"
                />
                <span>{{ domain.name }}</span>
              </label>
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="showAddUser = false" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? 'Creating...' : 'Create User' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <!-- Edit User Permissions Modal -->
    <div v-if="editingUser" class="modal">
      <div class="modal-content">
        <h3>✏️ Edit Permissions: {{ editingUser.username }}</h3>
        
        <div v-if="modalError" class="error-message">
          {{ modalError }}
        </div>
        
        <form @submit.prevent="updateUserPermissions">
          <div class="form-group">
            <label>Accessible Domains</label>
            <div class="domain-checklist">
              <label 
                v-for="domain in domains" 
                :key="domain.id"
                class="checkbox-label"
              >
                <input 
                  type="checkbox" 
                  :value="domain.id"
                  v-model="editingUser.domain_ids"
                />
                <span>{{ domain.name }}</span>
              </label>
            </div>
          </div>
          
          <div class="modal-actions">
            <button type="button" @click="editingUser = null" class="btn btn-secondary">
              Cancel
            </button>
            <button type="submit" class="btn btn-primary" :disabled="updating">
              {{ updating ? 'Updating...' : 'Update Permissions' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api.js'

export default {
  name: 'UserManager',
  data() {
    return {
      users: [],
      domains: [],
      loading: true,
      error: '',
      showAddUser: false,
      editingUser: null,
      newUser: {
        username: '',
        password: '',
        domain_ids: []
      },
      modalError: '',
      creating: false,
      updating: false
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      this.error = ''
      
      try {
        const [usersRes, domainsRes] = await Promise.all([
          api.getUsers(),
          api.getDomains()
        ])
        
        this.users = usersRes.data
        this.domains = domainsRes.data
      } catch (error) {
        this.error = error.response?.data?.error || 'Failed to load data'
      } finally {
        this.loading = false
      }
    },
    
    async createUser() {
      this.modalError = ''
      
      if (!this.newUser.username || !this.newUser.password) {
        this.modalError = 'Username and password are required'
        return
      }
      
      if (this.newUser.password.length < 6) {
        this.modalError = 'Password must be at least 6 characters'
        return
      }
      
      this.creating = true
      
      try {
        await api.createUser(this.newUser)
        await this.loadData()
        this.showAddUser = false
        this.newUser = { username: '', password: '', domain_ids: [] }
      } catch (error) {
        this.modalError = error.response?.data?.error || 'Failed to create user'
      } finally {
        this.creating = false
      }
    },
    
    editUser(user) {
      this.editingUser = { ...user }
      this.modalError = ''
    },
    
    async updateUserPermissions() {
      this.modalError = ''
      this.updating = true
      
      try {
        await api.updateUserPermissions(this.editingUser.id, this.editingUser.domain_ids)
        await this.loadData()
        this.editingUser = null
      } catch (error) {
        this.modalError = error.response?.data?.error || 'Failed to update permissions'
      } finally {
        this.updating = false
      }
    },
    
    formatDate(dateString) {
      return new Date(dateString).toLocaleDateString()
    }
  }
}
</script>

<style scoped>
.user-manager {
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

.loading {
  text-align: center;
  padding: 3rem;
  color: #666;
}

.users-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background: #f8f9fa;
}

th {
  text-align: left;
  padding: 1rem;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

td {
  padding: 1rem;
  border-bottom: 1px solid #e0e0e0;
}

.badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.badge-admin {
  background: #ff6b6b;
  color: white;
}

.badge-user {
  background: #667eea;
  color: white;
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
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-content h3 {
  margin-bottom: 1.5rem;
  color: #333;
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
}

.form-group input:focus {
  outline: none;
  border-color: #667eea;
}

.domain-checklist {
  max-height: 300px;
  overflow-y: auto;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  padding: 1rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  cursor: pointer;
  transition: background 0.3s;
}

.checkbox-label:hover {
  background: #f8f9fa;
}

.checkbox-label input {
  cursor: pointer;
  width: auto;
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
```

---

That completes all the frontend files! Now let me create a comprehensive README with the final project structure:

## Complete README.md

```markdown
# /README.md

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

⚠️ **You will be forced to change the password immediately after first login.**

## 📁 Project Structure

```
nginx-configerrrrrr/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── models.py           # Database models (User, Domain, Location)
│   ├── utils.py            # Config generation, Nginx/Certbot management
│   ├── config.py           # Application configuration
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
   - Obtain SSL certificate from Let's Encrypt
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
- `GET /api/domains/<id>` - Get single domain
- `POST /api/domains` - Create new domain
- `PUT /api/domains/<id>` - Update domain
- `DELETE /api/domains/<id>` - Delete domain
- `POST /api/domains/<id>/ssl` - Enable SSL with Certbot

### Users (Superuser Only)
- `GET /api/users` - List all users
- `POST /api/users` - Create new user
- `PUT /api/users/<id>` - Update user permissions

## 🚀 Production Deployment

For production use:

1. **Use a Process Manager** (systemd, supervisor)
2. **Run Behind Reverse Proxy** (Nginx with SSL)
3. **Set Strong Secret Key** in `backend/config.py`
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
```