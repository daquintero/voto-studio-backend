from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
TESTING = False
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env('DJANGO_SECRET_KEY', default='bTQAYpxY4cfIIJbe4lJtoOdPgScrFJCWIqcSndXL5qd0OcsDvvDKIbYNTe7NTgDa')
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "localhost",
    "0.0.0.0",
    "127.0.0.1",
]

# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': ''
    }
}

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]['OPTIONS']['debug'] = DEBUG  # noqa F405

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = 'localhost'
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

# django-debug-toolbar
# ------------------------------------------------------------------------------
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#prerequisites
INSTALLED_APPS += ['debug_toolbar']  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#middleware
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']  # noqa F405
# https://django-debug-toolbar.readthedocs.io/en/latest/configuration.html#debug-toolbar-config
DEBUG_TOOLBAR_CONFIG = {
    'DISABLE_PANELS': [
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ],
    'SHOW_TEMPLATE_CONTEXT': True,
}
# https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#internal-ips
INTERNAL_IPS = ['127.0.0.1', '10.0.2.2']


# django-extensions
# ------------------------------------------------------------------------------
# https://django-extensions.readthedocs.io/en/latest/installation_instructions.html#configuration
INSTALLED_APPS += ['django_extensions']  # noqa F405

# ------------------------------------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=django,public',
        },
        'NAME': env('DJANGO_DATABASE_NAME'),
        'USER': env('DJANGO_DATABASE_USER'),
        'PASSWORD': env('DJANGO_DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
            'NAME': 'default',
            'DEPENDENCIES': ['main_site'],
        },
        'ATOMIC_REQUESTS': True,
    },
    'main_site': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=main_site,public',
        },
        'NAME': env('DJANGO_DATABASE_NAME'),
        'USER': env('DJANGO_DATABASE_USER'),
        'PASSWORD': env('DJANGO_DATABASE_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'TEST': {
            'NAME': 'main_site',
            'DEPENDENCIES': [],
        },
        'ATOMIC_REQUESTS': True,
    }
}

CORS_ORIGIN_WHITELIST = (
    'localhost:3000',
    'localhost:3001',
)
