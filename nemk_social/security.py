"""
НЕФК — Anti-DDoS / Rate Limiting / Anti-VPN v2
"""
import time
import re
import logging
import threading
from collections import defaultdict, deque
from functools import wraps

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required

logger = logging.getLogger('nemk_security')

# ── Ліміти ────────────────────────────────────────────────────
RATE_LIMIT_CONFIG = {
    'global':          {'limit': 300, 'window': 60},  # 300 req/хв
    'global_burst':    {'limit': 80,  'window': 5},   # 80 req/5сек
    'auth':            {'limit': 20,  'window': 60},  # 20 спроб/хв на логін
    'auto_ban_after':    15,    # 15 попереджень до бану
    'auto_ban_duration': 300,   # 5 хвилин
    'perm_ban_after':    20,    # постійний бан після 20 тимчасових
}

# ── Підозрілі UA ──────────────────────────────────────────────
SUSPICIOUS_UA_RE = [re.compile(p, re.IGNORECASE) for p in [
    r'sqlmap', r'nikto', r'nmap', r'masscan', r'hydra',
    r'metasploit', r'burpsuite', r'dirbuster', r'gobuster',
    r'wfuzz', r'nuclei', r'acunetix', r'nessus',
    r'zgrab', r'scrapy',
]]

# ── Шкідливі шляхи ────────────────────────────────────────────
MALICIOUS_PATH_RE = [re.compile(p, re.IGNORECASE) for p in [
    r'\.\./', r'etc/passwd', r'etc/shadow',
    r'\.git/', r'wp-admin', r'wp-login',
    r'phpMyAdmin', r'phpmyadmin', r'adminer',
    r'eval\(', r'base64_decode', r'union.*select',
    r'<script>', r'javascript:', r'vbscript:',
    r'\.php$', r'\.asp$', r'\.aspx$',
]]

# ── VPN/Proxy заголовки ────────────────────────────────────────
PROXY_HEADERS = [
    'HTTP_VIA', 'HTTP_PROXY_CONNECTION',
    'HTTP_X_PROXY_ID', 'HTTP_X_BLUECOAT_VIA',
]

# ── Whitelist (ніколи не блокуємо) ───────────────────────────
IP_WHITELIST = {'127.0.0.1', '::1', 'localhost', '0.0.0.0', '::ffff:127.0.0.1'}

# ── In-memory storage ─────────────────────────────────────────
_lock   = threading.Lock()
_reqs   = defaultdict(lambda: deque(maxlen=500))
_stats_ip = defaultdict(lambda: {
    'count': 0, 'first_seen': time.time(), 'last_seen': time.time(),
    'warnings': 0, 'banned_count': 0,
})
_temp_bans = {}   # {ip: unban_ts}
_perm_bans = {}   # {ip: reason}
_events    = deque(maxlen=500)

_stats = {
    'total_requests': 0, 'blocked_requests': 0,
    'temp_bans_issued': 0, 'perm_bans_issued': 0,
    'suspicious_ua_blocked': 0, 'malicious_path_blocked': 0,
    'vpn_proxy_blocked': 0, 'started_at': time.time(),
}


def _get_ip(request):
    for h in ['HTTP_CF_CONNECTING_IP', 'HTTP_X_REAL_IP',
              'HTTP_X_FORWARDED_FOR', 'REMOTE_ADDR']:
        ip = request.META.get(h, '').split(',')[0].strip()
        if ip and ip not in ('', 'unknown'):
            return ip
    return '0.0.0.0'


def _log(ip, event, detail='', sev='WARNING'):
    _events.appendleft({
        'time': time.time(),
        'time_fmt': timezone.now().strftime('%d.%m %H:%M:%S'),
        'ip': ip, 'event': event, 'detail': detail, 'severity': sev,
    })
    getattr(logger, sev.lower(), logger.warning)(
        f'[SEC] {event} | {ip} | {detail}'
    )


def _is_temp_banned(ip):
    ts = _temp_bans.get(ip)
    if ts is None: return False
    if time.time() >= ts:
        del _temp_bans[ip]; _log(ip, 'UNBAN_EXPIRED', sev='INFO'); return False
    return True


def _is_perm_banned(ip):
    if ip in _perm_bans: return True
    c = cache.get(f'pban_{ip}')
    if c: _perm_bans[ip] = c; return True
    return False


def _temp_ban(ip, reason, dur=None):
    d = dur or RATE_LIMIT_CONFIG['auto_ban_duration']
    _temp_bans[ip] = time.time() + d
    _stats_ip[ip]['banned_count'] += 1
    _stats['temp_bans_issued'] += 1
    _log(ip, 'TEMP_BAN', f'{reason} {d}s')
    if _stats_ip[ip]['banned_count'] >= RATE_LIMIT_CONFIG['perm_ban_after']:
        _perm_ban(ip, f'Too many bans: {reason}')


def _perm_ban(ip, reason):
    _perm_bans[ip] = reason
    cache.set(f'pban_{ip}', reason, timeout=None)
    _stats['perm_bans_issued'] += 1
    _log(ip, 'PERM_BAN', reason, 'ERROR')


def _unban_ip(ip):
    _temp_bans.pop(ip, None); _perm_bans.pop(ip, None)
    cache.delete(f'pban_{ip}')
    if ip in _stats_ip:
        _stats_ip[ip]['warnings'] = 0; _stats_ip[ip]['banned_count'] = 0
    _log(ip, 'UNBANNED', sev='INFO')


def _check_rate(ip, path):
    now = time.time()
    cfg = RATE_LIMIT_CONFIG
    with _lock:
        q = _reqs[ip]; q.append(now)
        r60 = sum(1 for t in q if now-t < 60)
        r5  = sum(1 for t in q if now-t < 5)

        # Auth
        if any(path.startswith(p) for p in ['/login', '/register', '/api/']):
            ra = sum(1 for t in q if now-t < 60)
            if ra > cfg['auth']['limit']:
                _stats_ip[ip]['warnings'] += 1
                return True, f'Auth flood: {ra}/60s'

        if r5 > cfg['global_burst']['limit']:
            _stats_ip[ip]['warnings'] += 1
            if _stats_ip[ip]['warnings'] >= cfg['auto_ban_after']:
                _temp_ban(ip, f'Burst {r5}/5s')
            return True, f'Burst: {r5}/5s'

        if r60 > cfg['global']['limit']:
            _stats_ip[ip]['warnings'] += 1
            if _stats_ip[ip]['warnings'] >= cfg['auto_ban_after']:
                _temp_ban(ip, f'Flood {r60}/min')
            return True, f'Rate: {r60}/min'
    return False, ''


def _check_vpn(request, ip):
    meta = request.META
    for h in PROXY_HEADERS:
        if meta.get(h):
            return True, f'Proxy header: {h}'
    xff = meta.get('HTTP_X_FORWARDED_FOR', '')
    if xff and len(xff.split(',')) >= 3:
        return True, f'Proxy chain: {xff[:50]}'
    return False, ''


def _check_ua(ua):
    if not ua: return False, ''
    for p in SUSPICIOUS_UA_RE:
        if p.search(ua): return True, f'Bad UA: {ua[:60]}'
    return False, ''


def _check_path(path):
    for p in MALICIOUS_PATH_RE:
        if p.search(path): return True, f'Bad path: {path[:60]}'
    return False, ''


def _block(request, reason, retry=300, btype='suspicious'):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'error': 'Підозріла активність', 'retry_after': retry}, status=429)
    return render(request, 'security/blocked.html', {
        'reason': reason, 'retry_after': retry,
        'ip': _get_ip(request), 'block_type': btype,
    }, status=429)


# ── Middleware ─────────────────────────────────────────────────
class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        ip   = _get_ip(request)
        path = request.path
        ua   = request.META.get('HTTP_USER_AGENT', '')

        with _lock:
            _stats['total_requests'] += 1
            _stats_ip[ip]['count'] += 1
            _stats_ip[ip]['last_seen'] = time.time()

        # Whitelist — завжди пропускаємо
        if ip in IP_WHITELIST:
            return self.get_response(request)

        # Пerm ban
        if _is_perm_banned(ip):
            _stats['blocked_requests'] += 1
            return _block(request, 'Ваш IP заблокований. Зверніться до адміністратора.', 0, 'perm')

        # Temp ban
        if _is_temp_banned(ip):
            _stats['blocked_requests'] += 1
            retry = max(0, int(_temp_bans.get(ip, 0) - time.time()))
            return _block(request, 'Вибачте, підозріла активність.', retry, 'temp')

        # Anti-VPN
        vpn, vr = _check_vpn(request, ip)
        if vpn:
            _stats['blocked_requests'] += 1; _stats['vpn_proxy_blocked'] += 1
            _temp_ban(ip, vr, 300); _log(ip, 'VPN', vr)
            return _block(request, 'Вибачте, підозріла активність. Виявлено VPN/проксі.', 300, 'vpn')

        # Bad UA
        ua_bad, ur = _check_ua(ua)
        if ua_bad:
            _stats['blocked_requests'] += 1; _stats['suspicious_ua_blocked'] += 1
            _temp_ban(ip, ur, 300); _log(ip, 'BAD_UA', ur)
            return _block(request, 'Вибачте, підозріла активність.', 300, 'ua')

        # Bad path
        p_bad, pr = _check_path(path)
        if p_bad:
            _stats['blocked_requests'] += 1; _stats['malicious_path_blocked'] += 1
            _temp_ban(ip, pr, 300); _log(ip, 'BAD_PATH', pr, 'ERROR')
            return _block(request, 'Вибачте, підозріла активність.', 300, 'path')

        # Rate limit
        rl, rr = _check_rate(ip, path)
        if rl:
            _stats['blocked_requests'] += 1
            return _block(request, 'Вибачте, підозріла активність. Забагато запитів.', 60, 'rate')

        response = self.get_response(request)

        # 404 flood
        if response.status_code == 404:
            k = f'404_{ip}'; cnt = cache.get(k, 0) + 1
            cache.set(k, cnt, 300)
            if cnt > 40:
                _temp_ban(ip, f'404 flood {cnt}', 300)

        return response


# ── Decorator ─────────────────────────────────────────────────
def rate_limit(limit=30, window=60, ban_on_exceed=False):
    def dec(fn):
        @wraps(fn)
        def wrap(request, *args, **kwargs):
            ip = _get_ip(request)
            if ip in IP_WHITELIST: return fn(request, *args, **kwargs)
            k = f'rl_{fn.__name__}_{ip}'; now = time.time()
            ts = [t for t in cache.get(k, []) if now-t < window]
            ts.append(now); cache.set(k, ts, window+5)
            if len(ts) > limit:
                if ban_on_exceed: _temp_ban(ip, f'RL:{fn.__name__}', 300)
                return _block(request, 'Вибачте, підозріла активність.', window, 'rate')
            return fn(request, *args, **kwargs)
        return wrap
    return dec


# ── Security dashboard ─────────────────────────────────────────
@login_required
def security_dashboard(request):
    if not request.user.is_superuser:
        return redirect('feed')

    if request.method == 'POST':
        a  = request.POST.get('action')
        ip = request.POST.get('ip', '').strip()
        if a == 'unban' and ip:   _unban_ip(ip)
        elif a == 'ban' and ip:   _perm_ban(ip, request.POST.get('reason','Manual'))
        elif a == 'temp_ban' and ip:
            _temp_ban(ip, request.POST.get('reason','Manual'), int(request.POST.get('duration',300)))
        elif a == 'clear_logs':
            with _lock: _events.clear()
        return redirect('security_dashboard')

    now = time.time()
    ctx = {
        'stats':   _stats.copy(),
        'top_ips': sorted(_stats_ip.items(), key=lambda x: x[1]['count'], reverse=True)[:20],
        'events':  list(_events)[:100],
        'temp_bans': [
            {'ip':ip,'expires':timezone.datetime.fromtimestamp(ts).strftime('%d.%m %H:%M'),
             'remaining':max(0,int(ts-now))}
            for ip,ts in sorted(_temp_bans.items(),key=lambda x:x[1]) if ts>now
        ],
        'perm_bans': list(_perm_bans.items()),
        'uptime':    _fmt(now - _stats['started_at']),
        'config':    RATE_LIMIT_CONFIG,
        'total_tracked_ips': len(_stats_ip),
        'block_rate': round(_stats['blocked_requests']/max(_stats['total_requests'],1)*100,1),
    }
    return render(request, 'security/dashboard.html', ctx)


def _fmt(s):
    s=int(s); return f'{s//3600}г {(s%3600)//60}хв {s%60}с'


@login_required
def security_stats_api(request):
    if not request.user.is_superuser:
        return JsonResponse({'error':'Forbidden'},status=403)
    now=time.time()
    return JsonResponse({
        'total_requests':   _stats['total_requests'],
        'blocked_requests': _stats['blocked_requests'],
        'block_rate': round(_stats['blocked_requests']/max(_stats['total_requests'],1)*100,1),
        'temp_bans':  len([ip for ip,ts in _temp_bans.items() if ts>now]),
        'perm_bans':  len(_perm_bans),
        'temp_bans_issued': _stats['temp_bans_issued'],
        'perm_bans_issued': _stats['perm_bans_issued'],
        'suspicious_ua':    _stats['suspicious_ua_blocked'],
        'malicious_paths':  _stats['malicious_path_blocked'],
        'vpn_proxy':        _stats['vpn_proxy_blocked'],
        'recent_events':    list(_events)[:10],
        'uptime':           _fmt(now-_stats['started_at']),
    })
