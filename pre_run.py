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