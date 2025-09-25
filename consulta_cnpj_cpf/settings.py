from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(os.path.join(BASE_DIR, '.env'))


SECRET_KEY = 'django-insecure-g$z4%7y$w^r69l3qj9*=cm^_94@)cphu6=rgm-jyumt#qgds97'

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'consulta',
    'rest_framework',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB'),
        'USER': os.getenv('POSTGRES_USER'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# --- CNPJá PRO API ---
CNPJA_API_KEY = os.getenv("CNPJA_API_KEY")
CNPJA_BASE_URL = os.getenv("CNPJA_BASE_URL", "https://api.cnpja.com")
# Estratégia de cache da API CNPJá (CACHE, CACHE_IF_FRESH, CACHE_IF_ERROR, ONLINE)
CNPJA_STRATEGY = os.getenv("CNPJA_STRATEGY", "CACHE_IF_FRESH")
# Quantos dias os dados em cache são considerados "frescos" (usado com CACHE_IF_FRESH/CACHE_IF_ERROR)
try:
    CNPJA_MAX_AGE_DAYS = int(os.getenv("CNPJA_MAX_AGE_DAYS", "14"))
except ValueError:
    CNPJA_MAX_AGE_DAYS = 14
# Por quantos dias além do maxAge o cache ainda pode ser retornado em caso de falha online (usado com CACHE_IF_ERROR)
try:
    CNPJA_MAX_STALE_DAYS = int(os.getenv("CNPJA_MAX_STALE_DAYS", "30"))
except ValueError:
    CNPJA_MAX_STALE_DAYS = 30

# --- DRF settings ---
REST_FRAMEWORK = {
    # Throttling global (pode ser ajustado conforme necessidade)
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ],
    # Exemplo: 100 requisições/hora por IP anônimo e 1000/hora por usuário autenticado
    'DEFAULT_THROTTLE_RATES': {
        # Limite global: 100 requisições por minuto para todos os endpoints
        'anon': '100/minute',
        'user': '100/minute',
    },
}

# Cache (usado para créditos CNPJÁ). Em produção, configure um backend persistente (Redis/Memcached).
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'consulta-cnpj-cache',
    }
}