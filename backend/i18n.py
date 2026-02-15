# /backend/i18n.py
"""Simple i18n helpers for API responses"""

from typing import Dict

SUPPORTED_LANGS = {'en', 'zh'}

MESSAGES: Dict[str, Dict[str, str]] = {
    'en': {
        'auth.token_missing': 'Token is missing',
        'auth.user_not_found': 'User not found',
        'auth.token_expired': 'Token has expired',
        'auth.invalid_token': 'Invalid token',
        'auth.username_password_required': 'Username and password required',
        'auth.invalid_credentials': 'Invalid credentials',
        'auth.old_new_password_required': 'Both old and new passwords required',
        'auth.invalid_old_password': 'Invalid old password',
        'auth.password_too_short': 'Password must be at least 6 characters',
        'auth.password_changed': 'Password changed successfully',

        'domain.not_found_or_denied': 'Domain not found or access denied',
        'domain.name_required': 'Domain name is required',
        'domain.already_exists': 'Domain already exists',
        'domain.delete_superuser_only': 'Only superusers can delete domains',
        'domain.deleted': 'Domain deleted successfully',

        'user.superuser_required': 'Superuser access required',
        'user.username_exists': 'Username already exists',
        'user.permissions_updated': 'Permissions updated successfully'
    },
    'zh': {
        'auth.token_missing': '缺少认证令牌',
        'auth.user_not_found': '用户不存在',
        'auth.token_expired': '令牌已过期',
        'auth.invalid_token': '无效令牌',
        'auth.username_password_required': '用户名和密码不能为空',
        'auth.invalid_credentials': '用户名或密码错误',
        'auth.old_new_password_required': '旧密码和新密码均不能为空',
        'auth.invalid_old_password': '旧密码错误',
        'auth.password_too_short': '密码至少需要 6 个字符',
        'auth.password_changed': '密码修改成功',

        'domain.not_found_or_denied': '域名不存在或无权限访问',
        'domain.name_required': '域名不能为空',
        'domain.already_exists': '域名已存在',
        'domain.delete_superuser_only': '仅超级管理员可删除域名',
        'domain.deleted': '域名删除成功',

        'user.superuser_required': '需要超级管理员权限',
        'user.username_exists': '用户名已存在',
        'user.permissions_updated': '权限更新成功'
    }
}


def normalize_language(raw_lang: str) -> str:
    if not raw_lang:
        return 'en'

    lowered = raw_lang.strip().lower()
    if lowered.startswith('zh'):
        return 'zh'
    return 'en'


def get_request_lang(req) -> str:
    header = req.headers.get('Accept-Language', '')
    first = header.split(',', 1)[0].split(';', 1)[0]
    normalized = normalize_language(first)
    if normalized in SUPPORTED_LANGS:
        return normalized
    return 'en'


def t(lang: str, key: str, **kwargs) -> str:
    language = lang if lang in SUPPORTED_LANGS else 'en'
    text = MESSAGES.get(language, {}).get(key) or MESSAGES['en'].get(key) or key
    if kwargs:
        return text.format(**kwargs)
    return text
