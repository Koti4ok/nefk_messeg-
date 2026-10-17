"""
Тест Anti-DDoS системи НЕФК
Запуск: python test_ddos.py
"""
import urllib.request
import urllib.error
import time
import threading

BASE = "http://127.0.0.1:8000"
results = {"ok": 0, "blocked": 0, "error": 0}
lock = threading.Lock()


def req(url, headers=None, label=""):
    try:
        r = urllib.request.Request(url, headers=headers or {})
        with urllib.request.urlopen(r, timeout=3) as resp:
            code = resp.getcode()
            with lock:
                results["ok"] += 1
            return code
    except urllib.error.HTTPError as e:
        with lock:
            results["blocked"] += 1
        return e.code
    except Exception:
        with lock:
            results["error"] += 1
        return 0


def separator(title):
    print(f"\n{'─'*50}")
    print(f"  {title}")
    print('─'*50)


# ══════════════════════════════════════════════════
print("╔══════════════════════════════════════════╗")
print("║   НЕФК Anti-DDoS Тест                   ║")
print("╚══════════════════════════════════════════╝")

# ── Тест 1: Burst flood (30+ запитів за 5 сек) ──
separator("ТЕСТ 1: Burst flood — 40 запитів за 3 сек")
print("Надсилаємо 40 запитів...")
ok = blocked = 0
for i in range(40):
    code = req(BASE + "/")
    if code in (429, 403):
        blocked += 1
    elif code in (200, 301, 302):
        ok += 1
    if i % 10 == 9:
        print(f"  [{i+1}/40] ✅ ok={ok}  🚫 blocked={blocked}")
print(f"\nРезультат: ✅ {ok} пропущено | 🚫 {blocked} заблоковано")
if blocked > 0:
    print("✔ Burst flood ЗАБЛОКОВАНО")
else:
    print("✘ Burst flood не спрацював (127.0.0.1 у whitelist — це нормально!)")

time.sleep(2)

# ── Тест 2: Підозрілий User-Agent ───────────────
separator("ТЕСТ 2: Підозрілий User-Agent (sqlmap)")
ua_tests = [
    ("sqlmap/1.0",             "SQLMap scanner"),
    ("nikto/2.1.6",            "Nikto scanner"),
    ("python-requests/0.14",   "Стара requests"),
    ("Mozilla/5.0 (нормальний)","Нормальний браузер"),
]
for ua, name in ua_tests:
    code = req(BASE + "/", headers={"User-Agent": ua})
    status = "🚫 BLOCKED" if code in (429, 403) else "✅ PASSED"
    print(f"  {status}  [{code}]  {name}")

time.sleep(1)

# ── Тест 3: Шкідливі шляхи ──────────────────────
separator("ТЕСТ 3: Path traversal / SQL injection")
bad_paths = [
    "/../../etc/passwd",
    "/.env",
    "/.git/config",
    "/wp-admin",
    "/phpmyadmin",
    "/login?q=<script>alert(1)</script>",
    "/feed?id=1 UNION SELECT * FROM users",
]
for path in bad_paths:
    code = req(BASE + path)
    status = "🚫 BLOCKED" if code in (429, 403) else f"⚠ [{code}]"
    print(f"  {status}  {path[:45]}")

time.sleep(1)

# ── Тест 4: Proxy заголовки ─────────────────────
separator("ТЕСТ 4: VPN / Proxy detection")
proxy_tests = [
    ({"Via": "1.1 proxy.example.com"},           "Via header"),
    ({"Proxy-Connection": "keep-alive"},          "Proxy-Connection"),
    ({"X-Forwarded-For": "1.2.3.4, 5.6.7.8, 9.10.11.12"}, "3-hop chain"),
    ({"Client-IP": "192.168.1.100"},              "Client-IP"),
]
for headers, name in proxy_tests:
    code = req(BASE + "/", headers=headers)
    status = "🚫 BLOCKED" if code in (429, 403) else "✅ PASSED"
    print(f"  {status}  [{code}]  {name}")

# ── Тест 5: Rate limit на логін ─────────────────
separator("ТЕСТ 5: Auth brute-force (15 спроб за хв)")
print("Надсилаємо 15 POST на /login/...")
ok = blocked = 0
for i in range(15):
    try:
        data = b"username=hacker&password=test"
        r = urllib.request.Request(
            BASE + "/login/",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Mozilla/5.0",
            }
        )
        with urllib.request.urlopen(r, timeout=3) as resp:
            ok += 1
    except urllib.error.HTTPError as e:
        if e.code in (429, 403):
            blocked += 1
        else:
            ok += 1
    except Exception:
        pass
print(f"Результат: ✅ {ok} | 🚫 {blocked}")

# ══════════════════════════════════════════════════
print(f"\n{'═'*50}")
print("  ПІДСУМОК")
print('═'*50)
print(f"  Всього запитів: {results['ok'] + results['blocked'] + results['error']}")
print(f"  Пропущено:      {results['ok']}")
print(f"  Заблоковано:    {results['blocked']}")
print(f"  Помилки:        {results['error']}")
print()
print("  ℹ️  127.0.0.1 у whitelist — burst/rate тести")
print("     не спрацюють для локального IP (це правильно).")
print("     Proxy/UA/Path тести спрацьовують незалежно.")
print()
print("  Щоб перевірити бан: відкрий Security Dashboard")
print("  http://127.0.0.1:8000/security/dashboard/")
print('═'*50)
