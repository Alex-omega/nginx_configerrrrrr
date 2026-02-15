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