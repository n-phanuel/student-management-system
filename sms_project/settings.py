"""
Django settings for the Student Management System (SMS) project.
"""

from pathlib import Path

# ==============================================================
# Base directory — all paths are relative to this
# ==============================================================
BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================
# Security
# ==============================================================
SECRET_KEY = 'django-insecure-sms-university-assignment-key-change-in-production'
DEBUG = True
ALLOWED_HOSTS = ['*']

# ==============================================================
# Application definition
# ==============================================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'students',          # Our custom MVC app
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

ROOT_URLCONF = 'sms_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],   # Project-level templates
        'APP_DIRS': True,                   # Also look inside apps/templates/
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

WSGI_APPLICATION = 'sms_project.wsgi.application'

# ==============================================================
# Database  (SQLite — zero config, perfect for assignments)
# ==============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ==============================================================
# Password validation
# ==============================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================================================
# Localisation
# ==============================================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ==============================================================
# Static files
# ==============================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ==============================================================
# Authentication redirects
# ==============================================================
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/dashboard/'          # Admin lands on admin dashboard
LOGOUT_REDIRECT_URL = '/'                   # Everyone lands on the landing page

# ==============================================================
# Session security — session expires when browser closes
# and after 2 hours of inactivity
# ==============================================================
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 7200                   # 2 hours in seconds
SESSION_SAVE_EVERY_REQUEST = True           # Reset timer on activity
