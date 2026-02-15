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