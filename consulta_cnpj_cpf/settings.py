from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import timedelta
import dj_database_url
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

# Carrega .env se existir (útil para desenvolvimento local). Em produção, normalmente não há .env.
_env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(_env_path):
    load_dotenv(_env_path)

# Alternância única de ambiente: quando RUN_LOCAL=True, aplica presets de desenvolvimento local
RUN_LOCAL = os.getenv('RUN_LOCAL', 'False').lower() in ('1','true','yes','local','dev','development')

# Core config
SECRET_KEY = os.getenv('SECRET_KEY', 'unsafe-default-change-in-prod')
DEBUG = True if RUN_LOCAL else (os.getenv('DEBUG', 'False').lower() in ('1','true','yes'))
if RUN_LOCAL:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']
    CSRF_TRUSTED_ORIGINS = ['http://localhost:8000','http://127.0.0.1:8000','http://[::1]:8000']
else:
    ALLOWED_HOSTS = [h for h in os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') if h]
    CSRF_TRUSTED_ORIGINS = [o for o in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if o]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'consulta',
    'rest_framework',
    'widget_tweaks',
    'axes',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'axes.middleware.AxesMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'consulta_cnpj_cpf.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'consulta_cnpj_cpf.wsgi.application'

# Database configuration
# Prefer DATABASE_URL; otherwise PostgreSQL via POSTGRES_*/PG* vars.
if os.getenv('DATABASE_URL'):
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600,
            ssl_require=not RUN_LOCAL,  # em local não exige SSL
        )
    }
else:
    # Check PostgreSQL environment variables
    pg_name = os.getenv('PGDATABASE') or os.getenv('POSTGRES_DB')
    pg_user = os.getenv('PGUSER') or os.getenv('POSTGRES_USER')
    pg_password = os.getenv('PGPASSWORD') or os.getenv('POSTGRES_PASSWORD')
    pg_host = os.getenv('PGHOST') or os.getenv('POSTGRES_HOST') or 'localhost'
    pg_port = os.getenv('PGPORT') or os.getenv('POSTGRES_PORT') or '5432'

    if pg_name and pg_user:
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': pg_name,
                'USER': pg_user,
                'PASSWORD': pg_password,
                'HOST': pg_host,
                'PORT': pg_port,
            }
        }
    else:
        if RUN_LOCAL:
            raise ImproperlyConfigured(
                'RUN_LOCAL=True requer PostgreSQL configurado. Defina DATABASE_URL ou as variáveis POSTGRES_* (POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_HOST, POSTGRES_PORT).'
            )
        # Fallback apenas em produção se a plataforma não definir DB
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': BASE_DIR / 'db.sqlite3',
            }
        }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Em desenvolvimento, o Django já encontra static de cada app automaticamente.
# Evite apontar para a mesma pasta do app para não duplicar arquivos.
# STATICFILES_DIRS pode ser usado se você tiver uma pasta 'static' global.
# STATICFILES_DIRS = [BASE_DIR / 'static']
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CNPJá PRO API
CNPJA_API_KEY = os.getenv('CNPJA_API_KEY')
CNPJA_BASE_URL = os.getenv('CNPJA_BASE_URL', 'https://api.cnpja.com')
CNPJA_STRATEGY = os.getenv('CNPJA_STRATEGY', 'CACHE_IF_FRESH')
CNPJA_FORCE_CACHE_FIRST = os.getenv('CNPJA_FORCE_CACHE_FIRST', 'True').lower() in ('1','true','yes')
try:
    CNPJA_MAX_AGE_DAYS = int(os.getenv('CNPJA_MAX_AGE_DAYS', '40'))
except ValueError:
    CNPJA_MAX_AGE_DAYS = 14
try:
    CNPJA_MAX_STALE_DAYS = int(os.getenv('CNPJA_MAX_STALE_DAYS', '30'))
except ValueError:
    CNPJA_MAX_STALE_DAYS = 30

# DRF
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'user': '100/minute',
    },
}

# Django Axes (anti-bruteforce)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesBackend',
    'django.contrib.auth.backends.ModelBackend',
]
AXES_ENABLED = False if RUN_LOCAL else True
AXES_FAILURE_LIMIT = int(os.getenv('AXES_FAILURE_LIMIT', '5'))
AXES_COOLOFF_TIME = timedelta(minutes=int(os.getenv('AXES_COOLOFF_MINUTES', '15')))
AXES_RESET_ON_SUCCESS = True
# Lockout strategy: replicate user+IP+User-Agent combination
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address', 'user_agent']
# If behind a reverse proxy, enable and set header via env to get client IP correctly
AXES_BEHIND_REVERSE_PROXY = False if RUN_LOCAL else (os.getenv('AXES_BEHIND_REVERSE_PROXY', 'False').lower() in ('1','true','yes'))
AXES_REVERSE_PROXY_HEADER = os.getenv('AXES_REVERSE_PROXY_HEADER', 'HTTP_X_FORWARDED_FOR')

# Cache (LocMem in local; Redis if REDIS_URL in prod)
if RUN_LOCAL:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'consulta-cnpj-cache',
        }
    }
else:
    if os.getenv('REDIS_URL'):
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': os.getenv('REDIS_URL'),
            }
        }
    else:
        CACHES = {
            'default': {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'LOCATION': 'consulta-cnpj-cache',
            }
        }

# Auth URLs
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'login'

# HTTPS & Security
SECURE_SSL_REDIRECT = False if RUN_LOCAL else (os.getenv('SECURE_SSL_REDIRECT', 'True').lower() in ('1','true','yes'))
# Cookies seguros: em dev (DEBUG=True) desabilita para evitar problemas em HTTP local
if DEBUG:
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 0 if RUN_LOCAL else int(os.getenv('SECURE_HSTS_SECONDS', '31536000'))
SECURE_HSTS_INCLUDE_SUBDOMAINS = False if RUN_LOCAL else (os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'True').lower() in ('1','true','yes'))
SECURE_HSTS_PRELOAD = False if RUN_LOCAL else (os.getenv('SECURE_HSTS_PRELOAD', 'True').lower() in ('1','true','yes'))
SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
CSRF_COOKIE_SAMESITE = os.getenv('CSRF_COOKIE_SAMESITE', 'Lax')
SECURE_PROXY_SSL_HEADER = None if RUN_LOCAL else ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_REFERRER_POLICY = os.getenv('SECURE_REFERRER_POLICY', 'same-origin')

# (Removido) Parâmetros manuais de anti-bruteforce; usamos apenas o Django Axes

# Upload allowlist (CSV/XLSX)
ALLOWED_UPLOAD_EXTENSIONS = ['.csv', '.xlsx']
ALLOWED_UPLOAD_MIME_TYPES = [
    'text/csv',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
]
