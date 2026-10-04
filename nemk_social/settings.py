"""
Django settings for НЕМК Соціальна Мережа.
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ─── Security ────────────────────────────────────────────────────────────────
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'dev-secret-key-change-in-production-!@#$%^&*()'
)
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'DJANGO_ALLOWED_HOSTS',
    '127.0.0.1 localhost'
).split() + ['.onrender.com']

# ─── Applications ─────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    # Django built-ins
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'channels',

    # Project apps
    'accounts',
    'posts',
    'friends',
    'groups',
    'chat',
    'notifications',
    'nemk_social',
]

# ─── ASGI / Channels ──────────────────────────────────────────────────────────
ASGI_APPLICATION = 'nemk_social.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        # In-memory layer для розробки.
        # Для продакшну замінити на channels_redis:
        # 'BACKEND': 'channels_redis.core.RedisChannelLayer',
        # 'CONFIG': {'hosts': [('127.0.0.1', 6379)]},
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

# ─── Middleware ───────────────────────────────────────────────────────────────
MIDDLEWARE = [
    # ── НЕФК Anti-DDoS — ПЕРШИЙ у ланцюжку ──────────────────────
    'nemk_social.security.RateLimitMiddleware',

    'django.middleware.security.SecurityMiddleware',
    # ── WhiteNoise — одразу після SecurityMiddleware ──────────────
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nemk_social.urls'

# ─── Templates ────────────────────────────────────────────────────────────────
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nemk_social.wsgi.application'

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
# Для PostgreSQL (розкоментуй і встанови psycopg2):
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', 'nemk_social'),
#         'USER': os.environ.get('DB_USER', 'postgres'),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#     }
# }

# ─── Auth ─────────────────────────────────────────────────────────────────────
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/feed/'
LOGOUT_REDIRECT_URL = '/'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ─── Internationalization ─────────────────────────────────────────────────────
LANGUAGE_CODE = 'uk'
TIME_ZONE = 'Europe/Kiev'
USE_I18N = True
USE_TZ = True

# ─── Static & Media ───────────────────────────────────────────────────────────
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# WhiteNoise — стиснення та кешування статики для продакшну
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ─── Messages ─────────────────────────────────────────────────────────────────
from django.contrib.messages import constants as messages_constants
MESSAGE_TAGS = {
    messages_constants.DEBUG: 'secondary',
    messages_constants.INFO: 'info',
    messages_constants.SUCCESS: 'success',
    messages_constants.WARNING: 'warning',
    messages_constants.ERROR: 'danger',
}

# ─── Session ──────────────────────────────────────────────────────────────────
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 60 * 60 * 24 * 14  # 2 тижні

# ─── Security headers (для продакшну) ────────────────────────────────────────
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'

# ─── Admin customization ──────────────────────────────────────────────────────
ADMIN_SITE_HEADER = 'НЕМК Соціальна Мережа — Адміністрування'
ADMIN_SITE_TITLE = 'НЕМК Адмін'
ADMIN_INDEX_TITLE = 'Панель управління'

# ─── File upload limits ───────────────────────────────────────────────────────
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10 MB

# ─── Security / Anti-DDoS ─────────────────────────────────────────────────────
# Вайтліст IP які ніколи не блокуються (можна розширити)
SECURITY_IP_WHITELIST = ['127.0.0.1', '::1']

# ─── Logging ─────────────────────────────────────────────────────────────────
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'security': {
            'format': '[%(asctime)s] %(levelname)s %(name)s: %(message)s',
            'datefmt': '%d.%m.%Y %H:%M:%S',
        },
    },
    'handlers': {
        'security_file': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'security.log',
            'maxBytes': 5 * 1024 * 1024,  # 5 MB
            'backupCount': 5,
            'formatter': 'security',
            'encoding': 'utf-8',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'security',
        },
    },
    'loggers': {
        'nemk_security': {
            'handlers': ['security_file', 'console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
