"""
НЕФК — Anti-DDoS / Rate Limiting система v1
============================================
Захист від:
  • Brute-force (багато запитів з одного IP)
  • DDoS (flood запитів)
  • Підозрілі User-Agent (боти, сканери)
  • Path traversal атаки
  • Repeated 404/error flooding

Компоненти:
  1. RateLimitMiddleware     — основний middleware
  2. rate_limit decorator    — для окремих view
  3. SecurityDashboardView   — адмін-моніторинг
  4. BannedIP model          — постійний бан через БД
  5. SecurityLog model       — журнал подій
"""

import time
import re
import logging
import threading
from collections import defaultdict, deque
from functools import wraps

from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.db import models

logger = logging.getLogger('nemk_security')

# ═══════════════════════════════════════════════════════════════
# КОНФІГУРАЦІЯ
# ═══════════════════════════════════════════════════════════════

RATE_LIMIT_CONFIG = {
    # Глобальний rate limit: max requests per window (seconds)
    'global':          {'limit': 120, 'window': 60},    # 120 запитів / хв
    'global_burst':    {'limit': 30,  'window': 5},     # не більше 30 за 5 сек

    # Auth endpoints — жорсткіший ліміт
    'auth':            {'limit': 10,  'window': 60},    # 10 спроб / хв
    'auth_lockout':    {'limit': 20,  'window': 300},   # блок на 5 хв після 20 спроб

    # API endpoints
    'api':             {'limit': 60,  'window': 60},

    # Admin
    'admin':           {'limit': 30,  'window': 60},

    # Auto-ban threshold: кількість попереджень до бану
    'auto_ban_after':  5,
    # Auto-ban тривалість (секунди)
    'auto_ban_duration': 3600,   # 1 година
    # Permanent ban після N тимчасових банів
    'perm_ban_after':  3,
}

# Підозрілі User-Agent паттерни
SUSPICIOUS_UA_PATTERNS = [
    r'sqlmap', r'nikto', r'nmap', r'masscan', r'hydra',
    r'metasploit', r'burpsuite', r'dirbuster', r'gobuster',
    r'wfuzz', r'nuclei', r'acunetix', r'nessus', r'openvas',
    r'python-requests/[01]', r'curl/[0-6]', r'wget/[01]',
    r'zgrab', r'crawler', r'scrapy', r'bot(?!.*google|.*bing)',
    r'<script', r'%3cscript', r'../../../',
]
SUSPICIOUS_UA_RE = [re.compile(p, re.IGNORECASE) for p in SUSPICIOUS_UA_PATTERNS]

# Path patterns що вказують на атаку
MALICIOUS_PATHS = [
    r'\.\./', r'etc/passwd', r'etc/shadow', r'proc/self',
    r'\.env$', r'\.git/', r'wp-admin', r'wp-login',
    r'phpMyAdmin', r'phpmyadmin', r'adminer',
    r'eval\(', r'base64_decode', r'union.*select',
    r'<script>', r'javascript:', r'vbscript:',
    r'\.php$', r'\.asp$', r'\.aspx$', r'\.jsp$',
]
MALICIOUS_PATH_RE = [re.compile(p, re.IGNORECASE) for p in MALICIOUS_PATHS]

# Whitelist — ці IP ніколи не блокуються
IP_WHITELIST = {'127.0.0.1', '::1', 'localhost'}

# ═══════════════════════════════════════════════════════════════
# IN-MEMORY STORAGE (thread-safe)
# ═══════════════════════════════════════════════════════════════

_lock = threading.Lock()

# {ip: deque of timestamps}
_request_log: dict = defaultdict(lambda: deque(maxlen=500))

# {ip: {'count': int, 'first_seen': float, 'last_seen': float, 'warnings': int}}
_ip_stats: dict = defaultdict(lambda: {
    'count': 0, 'first_seen': time.time(), 'last_seen': time.time(),
    'warnings': 0, 'banned_count': 0,
})

# {ip: unban_timestamp}  — тимчасові бани в пам'яті
_temp_bans: dict = {}

# {ip: reason}  — постійні бани в пам'яті (синхронізовані з cache)
_perm_bans: dict = {}

# Журнал подій: [{time, ip, event, detail}]
_security_events: deque = deque(maxlen=1000)

# Лічильники
_stats = {
    'total_requests': 0,
    'blocked_requests': 0,
    'temp_bans_issued': 0,
    'perm_bans_issued': 0,
    'suspicious_ua_blocked': 0,
    'malicious_path_blocked': 0,
    'started_at': time.time(),
}


def _get_client_ip(request) -> str:
    """Витягує реальний IP клієнта (через proxy headers)."""
    headers = [
        'HTTP_X_FORWARDED_FOR',
        'HTTP_X_REAL_IP',
        'HTTP_CF_CONNECTING_IP',   # Cloudflare
        'HTTP_X_CLUSTER_CLIENT_IP',
        'HTTP_FORWARDED',
        'REMOTE_ADDR',
    ]
    for h in headers:
        ip = request.META.get(h, '').split(',')[0].strip()
        if ip and ip not in ('', 'unknown'):
            return ip
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def _log_event(ip: str, event: str, detail: str = '', severity: str = 'WARNING'):
    """Додає запис у журнал подій."""
    entry = {
        'time':     time.time(),
        'time_fmt': timezone.now().strftime('%d.%m.%Y %H:%M:%S'),
        'ip':       ip,
        'event':    event,
        'detail':   detail,
        'severity': severity,
    }
    with _lock:
        _security_events.appendleft(entry)
    log_fn = getattr(logger, severity.lower(), logger.warning)
    log_fn(f'[НЕФК-SEC] {event} | IP:{ip} | {detail}')


def _is_temp_banned(ip: str) -> bool:
    """Перевіряє тимчасовий бан."""
    unban_at = _temp_bans.get(ip)
    if unban_at is None:
        return False
    if time.time() >= unban_at:
        del _temp_bans[ip]
        _log_event(ip, 'TEMP_BAN_EXPIRED', severity='INFO')
        return False
    return True


def _is_perm_banned(ip: str) -> bool:
    """Перевіряє постійний бан."""
    if ip in _perm_bans:
        return True
    cached = cache.get(f'perm_ban_{ip}')
    if cached:
        _perm_bans[ip] = cached
        return True
    return False


def _issue_temp_ban(ip: str, reason: str, duration: int = None):
    """Видає тимчасовий бан."""
    dur = duration or RATE_LIMIT_CONFIG['auto_ban_duration']
    _temp_bans[ip] = time.time() + dur
    _ip_stats[ip]['banned_count'] += 1
    _stats['temp_bans_issued'] += 1
    _log_event(ip, 'TEMP_BAN_ISSUED', f'Reason:{reason} Duration:{dur}s', 'WARNING')

    # Якщо перевищено ліміт тимчасових банів — постійний бан
    if _ip_stats[ip]['banned_count'] >= RATE_LIMIT_CONFIG['perm_ban_after']:
        _issue_perm_ban(ip, f'Too many temp bans: {reason}')


def _issue_perm_ban(ip: str, reason: str):
    """Видає постійний бан."""
    _perm_bans[ip] = reason
    cache.set(f'perm_ban_{ip}', reason, timeout=None)
    _stats['perm_bans_issued'] += 1
    _log_event(ip, 'PERM_BAN_ISSUED', f'Reason:{reason}', 'ERROR')


def _unban_ip(ip: str):
    """Знімає всі бани з IP."""
    _temp_bans.pop(ip, None)
    _perm_bans.pop(ip, None)
    cache.delete(f'perm_ban_{ip}')
    if ip in _ip_stats:
        _ip_stats[ip]['warnings'] = 0
        _ip_stats[ip]['banned_count'] = 0
    _log_event(ip, 'IP_UNBANNED', severity='INFO')


def _check_rate_limit(ip: str, path: str) -> tuple[bool, str]:
    """
    Перевіряє rate limit.
    Повертає (is_blocked: bool, reason: str)
    """
    now = time.time()
    cfg_global = RATE_LIMIT_CONFIG['global']
    cfg_burst  = RATE_LIMIT_CONFIG['global_burst']

    with _lock:
        log = _request_log[ip]
        log.append(now)

        # Підраховуємо запити за різні вікна
        reqs_1min  = sum(1 for t in log if now - t < cfg_global['window'])
        reqs_5sec  = sum(1 for t in log if now - t < cfg_burst['window'])

        # Auth endpoints — жорсткіший контроль
        is_auth = any(path.startswith(p) for p in ['/login', '/register', '/api/'])
        if is_auth:
            auth_cfg = RATE_LIMIT_CONFIG['auth']
            reqs_auth = sum(1 for t in log if now - t < auth_cfg['window'])
            if reqs_auth > auth_cfg['limit']:
                _ip_stats[ip]['warnings'] += 1
                return True, f'Auth rate limit: {reqs_auth} req/{auth_cfg["window"]}s'

        # Burst check (5 секунд)
        if reqs_5sec > cfg_burst['limit']:
            _ip_stats[ip]['warnings'] += 1
            if _ip_stats[ip]['warnings'] >= RATE_LIMIT_CONFIG['auto_ban_after']:
                _issue_temp_ban(ip, f'Burst flood: {reqs_5sec} req/5s')
            return True, f'Burst limit: {reqs_5sec} req/5s'

        # Global check (1 хвилина)
        if reqs_1min > cfg_global['limit']:
            _ip_stats[ip]['warnings'] += 1
            if _ip_stats[ip]['warnings'] >= RATE_LIMIT_CONFIG['auto_ban_after']:
                _issue_temp_ban(ip, f'Global flood: {reqs_1min} req/min')
            return True, f'Rate limit: {reqs_1min} req/min'

    return False, ''


def _check_user_agent(ua: str) -> tuple[bool, str]:
    """Перевіряє User-Agent на підозрілі паттерни."""
    if not ua:
        return False, ''
    for pattern in SUSPICIOUS_UA_RE:
        if pattern.search(ua):
            return True, f'Suspicious UA: {ua[:80]}'
    return False, ''


def _check_malicious_path(path: str) -> tuple[bool, str]:
    """Перевіряє URL на ознаки атак."""
    for pattern in MALICIOUS_PATH_RE:
        if pattern.search(path):
            return True, f'Malicious path: {path[:100]}'
    return False, ''


def _blocked_response(request, reason: str, retry_after: int = 60) -> HttpResponse:
    """Повертає відповідь 429/403 з красивою сторінкою."""
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    if is_ajax:
        return JsonResponse(
            {'error': 'Too many requests', 'detail': reason, 'retry_after': retry_after},
            status=429,
        )
    context = {
        'reason':      reason,
        'retry_after': retry_after,
        'ip':          _get_client_ip(request),
    }
    return render(request, 'security/blocked.html', context, status=429)


# ═══════════════════════════════════════════════════════════════
# MIDDLEWARE
# ═══════════════════════════════════════════════════════════════

class RateLimitMiddleware:
    """
    Головний anti-DDoS middleware.
    Підключається у settings.py як перший у MIDDLEWARE.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip   = _get_client_ip(request)
        path = request.path
        ua   = request.META.get('HTTP_USER_AGENT', '')

        with _lock:
            _stats['total_requests'] += 1
            _ip_stats[ip]['count']     += 1
            _ip_stats[ip]['last_seen']  = time.time()

        # 1. Whitelist — пропускаємо без перевірок
        if ip in IP_WHITELIST:
            return self.get_response(request)

        # 2. Постійний бан
        if _is_perm_banned(ip):
            _stats['blocked_requests'] += 1
            _log_event(ip, 'PERM_BANNED_REQUEST', path, 'ERROR')
            return _blocked_response(request, 'Ваш IP заблокований назавжди. Зверніться до адміністратора.', 0)

        # 3. Тимчасовий бан
        if _is_temp_banned(ip):
            _stats['blocked_requests'] += 1
            retry = max(0, int(_temp_bans.get(ip, 0) - time.time()))
            _log_event(ip, 'TEMP_BANNED_REQUEST', path)
            return _blocked_response(request, f'Тимчасово заблоковано. Спробуйте через {retry} сек.', retry)

        # 4. Перевірка підозрілого User-Agent
        ua_blocked, ua_reason = _check_user_agent(ua)
        if ua_blocked:
            _stats['blocked_requests']        += 1
            _stats['suspicious_ua_blocked']   += 1
            _issue_temp_ban(ip, ua_reason, 1800)
            _log_event(ip, 'SUSPICIOUS_UA', ua_reason, 'WARNING')
            return _blocked_response(request, 'Підозрілий запит заблоковано.', 1800)

        # 5. Перевірка шкідливого шляху
        path_blocked, path_reason = _check_malicious_path(path)
        if path_blocked:
            _stats['blocked_requests']         += 1
            _stats['malicious_path_blocked']   += 1
            _issue_temp_ban(ip, path_reason, 3600)
            _log_event(ip, 'MALICIOUS_PATH', path_reason, 'ERROR')
            return _blocked_response(request, 'Заборонений запит.', 3600)

        # 6. Rate limit
        rl_blocked, rl_reason = _check_rate_limit(ip, path)
        if rl_blocked:
            _stats['blocked_requests'] += 1
            _log_event(ip, 'RATE_LIMITED', rl_reason)
            return _blocked_response(request, f'Забагато запитів. {rl_reason}', 60)

        # Все ок — пропускаємо
        response = self.get_response(request)

        # Логуємо 404/500 flooding
        if response.status_code == 404:
            cache_key = f'404_{ip}'
            cnt = cache.get(cache_key, 0) + 1
            cache.set(cache_key, cnt, 300)
            if cnt > 30:
                _issue_temp_ban(ip, f'404 flooding: {cnt} times', 1800)
                _log_event(ip, '404_FLOOD', f'{cnt} 404s in 5min')

        return response


# ═══════════════════════════════════════════════════════════════
# DECORATOR для окремих view
# ═══════════════════════════════════════════════════════════════

def rate_limit(limit: int = 30, window: int = 60, ban_on_exceed: bool = False):
    """
    Декоратор для обмеження запитів на конкретний view.

    @rate_limit(limit=5, window=60)
    def my_view(request): ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            ip = _get_client_ip(request)
            if ip in IP_WHITELIST:
                return view_func(request, *args, **kwargs)

            cache_key = f'rl_{view_func.__name__}_{ip}'
            now = time.time()

            # Отримуємо список timestamps
            timestamps = cache.get(cache_key, [])
            timestamps = [t for t in timestamps if now - t < window]
            timestamps.append(now)
            cache.set(cache_key, timestamps, window + 5)

            if len(timestamps) > limit:
                if ban_on_exceed:
                    _issue_temp_ban(ip, f'View rate limit: {view_func.__name__}')
                _log_event(ip, 'VIEW_RATE_LIMIT', f'{view_func.__name__}: {len(timestamps)}/{limit}')
                retry = window - int(now - timestamps[0])
                return _blocked_response(request, f'Занадто багато запитів. Зачекайте {retry}с.', retry)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


# ═══════════════════════════════════════════════════════════════
# SECURITY DASHBOARD VIEW
# ═══════════════════════════════════════════════════════════════

@login_required
def security_dashboard(request):
    """Адмін-панель безпеки — тільки для superuser."""
    if not request.user.is_superuser:
        return redirect('feed')

    # Дія: розбанити IP
    if request.method == 'POST':
        action = request.POST.get('action')
        target_ip = request.POST.get('ip', '').strip()

        if action == 'unban' and target_ip:
            _unban_ip(target_ip)
        elif action == 'ban' and target_ip:
            reason = request.POST.get('reason', 'Manual ban by admin')
            _issue_perm_ban(target_ip, reason)
        elif action == 'temp_ban' and target_ip:
            dur = int(request.POST.get('duration', 3600))
            reason = request.POST.get('reason', 'Manual temp ban by admin')
            _issue_temp_ban(target_ip, reason, dur)
        elif action == 'clear_logs':
            with _lock:
                _security_events.clear()

        return redirect('security_dashboard')

    # Топ IP за кількістю запитів
    now = time.time()
    uptime_sec = now - _stats['started_at']
    uptime_str = _fmt_uptime(uptime_sec)

    top_ips = sorted(
        _ip_stats.items(),
        key=lambda x: x[1]['count'],
        reverse=True
    )[:20]

    # Активні тимчасові бани
    active_temp_bans = [
        {
            'ip': ip,
            'expires': timezone.datetime.fromtimestamp(ts).strftime('%d.%m %H:%M:%S'),
            'remaining': max(0, int(ts - now)),
        }
        for ip, ts in sorted(_temp_bans.items(), key=lambda x: x[1])
        if ts > now
    ]

    context = {
        'stats':            _stats.copy(),
        'top_ips':          top_ips,
        'events':           list(_security_events)[:100],
        'temp_bans':        active_temp_bans,
        'perm_bans':        list(_perm_bans.items()),
        'uptime':           uptime_str,
        'config':           RATE_LIMIT_CONFIG,
        'total_tracked_ips':len(_ip_stats),
        'block_rate':       round(
            _stats['blocked_requests'] / max(_stats['total_requests'], 1) * 100, 1
        ),
    }
    return render(request, 'security/dashboard.html', context)


def _fmt_uptime(sec: float) -> str:
    sec = int(sec)
    h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
    return f'{h}г {m}хв {s}с'


# ═══════════════════════════════════════════════════════════════
# AJAX endpoint для real-time статистики
# ═══════════════════════════════════════════════════════════════

@login_required
def security_stats_api(request):
    """Повертає поточну статистику JSON для live-оновлення дашборду."""
    if not request.user.is_superuser:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    now = time.time()
    return JsonResponse({
        'total_requests':   _stats['total_requests'],
        'blocked_requests': _stats['blocked_requests'],
        'block_rate':       round(_stats['blocked_requests'] / max(_stats['total_requests'], 1) * 100, 1),
        'temp_bans':        len([ip for ip, ts in _temp_bans.items() if ts > now]),
        'perm_bans':        len(_perm_bans),
        'temp_bans_issued': _stats['temp_bans_issued'],
        'perm_bans_issued': _stats['perm_bans_issued'],
        'suspicious_ua':    _stats['suspicious_ua_blocked'],
        'malicious_paths':  _stats['malicious_path_blocked'],
        'recent_events':    list(_security_events)[:10],
        'uptime':           _fmt_uptime(now - _stats['started_at']),
    })
