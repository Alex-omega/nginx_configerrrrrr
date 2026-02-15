# /backend/app.py
"""Main Flask application for Nginx Manager"""

import os
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from config import Config
from i18n import get_request_lang, t
from models import Domain, Location, User, UserDomainPermission
from utils import CertbotManager, NginxConfigGenerator, NginxManager

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
app.config.from_object(Config)
CORS(app)


def _lang():
    return get_request_lang(request)


def _msg(key, lang=None, **kwargs):
    return t(lang or _lang(), key, **kwargs)


# JWT decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        lang = _lang()
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'error': _msg('auth.token_missing', lang)}), 401

        try:
            if token.startswith('Bearer '):
                token = token[7:]

            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user = User.get_by_id(data['user_id'])

            if not current_user:
                return jsonify({'error': _msg('auth.user_not_found', lang)}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({'error': _msg('auth.token_expired', lang)}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': _msg('auth.invalid_token', lang)}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Authentication routes
@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    lang = _lang()
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': _msg('auth.username_password_required', lang)}), 400

    if not User.verify_password(username, password):
        return jsonify({'error': _msg('auth.invalid_credentials', lang)}), 401

    user = User.get_by_username(username)

    token = jwt.encode(
        {
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(days=7)
        },
        app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify(
        {
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'is_superuser': user['is_superuser'],
                'is_default_password': user['is_default_password']
            }
        }
    )


@app.route('/api/change-password', methods=['POST'])
@token_required
def change_password(current_user):
    """Change user password"""
    lang = _lang()
    data = request.json or {}
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({'error': _msg('auth.old_new_password_required', lang)}), 400

    if not User.verify_password(current_user['username'], old_password):
        return jsonify({'error': _msg('auth.invalid_old_password', lang)}), 401

    if len(new_password) < 6:
        return jsonify({'error': _msg('auth.password_too_short', lang)}), 400

    User.update_password(current_user['id'], new_password)

    return jsonify({'message': _msg('auth.password_changed', lang)})


# Domain routes
@app.route('/api/domains', methods=['GET'])
@token_required
def get_domains(current_user):
    """Get all domains (filtered by permissions)"""
    domains = Domain.get_all(current_user['id'])

    for domain in domains:
        domain['locations'] = Location.get_by_domain(domain['id'])

    return jsonify(domains)


@app.route('/api/domains/<int:domain_id>', methods=['GET'])
@token_required
def get_domain(current_user, domain_id):
    """Get single domain"""
    lang = _lang()
    domain = Domain.get_by_id(domain_id, current_user['id'])

    if not domain:
        return jsonify({'error': _msg('domain.not_found_or_denied', lang)}), 404

    domain['locations'] = Location.get_by_domain(domain_id)

    return jsonify(domain)


@app.route('/api/domains', methods=['POST'])
@token_required
def create_domain(current_user):
    """Create new domain"""
    lang = _lang()
    data = request.json or {}
    name = data.get('name')
    server_name = data.get('server_name', name)
    listen_port = data.get('listen_port', '80')

    if not name:
        return jsonify({'error': _msg('domain.name_required', lang)}), 400

    domain_id = Domain.create(name, server_name, listen_port)

    if not domain_id:
        return jsonify({'error': _msg('domain.already_exists', lang)}), 400

    Location.create(domain_id, '/', '', 'basic', 'dynamic')

    domain = Domain.get_by_id(domain_id)
    domain['locations'] = Location.get_by_domain(domain_id)

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
    lang = _lang()
    domain = Domain.get_by_id(domain_id, current_user['id'])

    if not domain:
        return jsonify({'error': _msg('domain.not_found_or_denied', lang)}), 404

    data = request.json or {}

    if 'server_name' in data:
        Domain.update(domain_id, server_name=data['server_name'])

    if 'listen_port' in data:
        Domain.update(domain_id, listen_port=data['listen_port'])

    if 'locations' in data:
        Location.delete_by_domain(domain_id)

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

    domain = Domain.get_by_id(domain_id)
    domain['locations'] = Location.get_by_domain(domain_id)

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
    lang = _lang()
    domain = Domain.get_by_id(domain_id, current_user['id'])

    if not domain:
        return jsonify({'error': _msg('domain.not_found_or_denied', lang)}), 404

    if not current_user['is_superuser']:
        return jsonify({'error': _msg('domain.delete_superuser_only', lang)}), 403

    conf_path = os.path.join(Config.NGINX_CONF_DIR, f"{domain['name']}.conf")
    if os.path.exists(conf_path):
        os.remove(conf_path)

    Domain.delete(domain_id)
    NginxManager.reload()

    return jsonify({'message': _msg('domain.deleted', lang)})


@app.route('/api/domains/<int:domain_id>/ssl', methods=['POST'])
@token_required
def enable_ssl(current_user, domain_id):
    """Enable SSL for domain using Certbot"""
    lang = _lang()
    domain = Domain.get_by_id(domain_id, current_user['id'])

    if not domain:
        return jsonify({'error': _msg('domain.not_found_or_denied', lang)}), 404

    success, message = CertbotManager.obtain_certificate(domain['name'])

    if success:
        Domain.update(domain_id, ssl_enabled=True, listen_port='443')
        return jsonify({'message': message})

    return jsonify({'error': message}), 500


# User management routes (superuser only)
@app.route('/api/users', methods=['GET'])
@token_required
def get_users(current_user):
    """Get all users"""
    lang = _lang()
    if not current_user['is_superuser']:
        return jsonify({'error': _msg('user.superuser_required', lang)}), 403

    users = User.get_all()

    for user in users:
        user['domain_ids'] = UserDomainPermission.get_user_domains(user['id'])

    return jsonify(users)


@app.route('/api/users', methods=['POST'])
@token_required
def create_user(current_user):
    """Create new user"""
    lang = _lang()
    if not current_user['is_superuser']:
        return jsonify({'error': _msg('user.superuser_required', lang)}), 403

    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    domain_ids = data.get('domain_ids', [])

    if not username or not password:
        return jsonify({'error': _msg('auth.username_password_required', lang)}), 400

    if len(password) < 6:
        return jsonify({'error': _msg('auth.password_too_short', lang)}), 400

    user_id = User.create(username, password)

    if not user_id:
        return jsonify({'error': _msg('user.username_exists', lang)}), 400

    UserDomainPermission.set_user_domains(user_id, domain_ids)

    return jsonify({'id': user_id, 'username': username}), 201


@app.route('/api/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user_permissions(current_user, user_id):
    """Update user domain permissions"""
    lang = _lang()
    if not current_user['is_superuser']:
        return jsonify({'error': _msg('user.superuser_required', lang)}), 403

    data = request.json or {}
    domain_ids = data.get('domain_ids', [])

    UserDomainPermission.set_user_domains(user_id, domain_ids)

    return jsonify({'message': _msg('user.permissions_updated', lang)})


# Serve frontend
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Serve frontend files"""
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
