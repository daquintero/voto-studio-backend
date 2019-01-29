"""
With these settings, testing run faster.
"""

from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = False
TESTING = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY", default="VZxrZx5bCoZWbkjuDKzh0Hr8YBGByDbF2ZxBmaJbujMkM8NOBu8LNKSqRRF3zQ6u")
# https://docs.djangoproject.com/en/dev/ref/settings/#test-runner
TEST_RUNNER = "django.test.runner.DiscoverRunner"

INSTALLED_APPS += ['shared.testing.test_app']

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache", "LOCATION": ""
    }
}

# PASSWORDS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#password-hashers
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG  # noqa F405
TEMPLATES[0]["OPTIONS"]["loaders"] = [  # noqa F405
    (
        "django.template.loaders.cached.Loader",
        [
            "django.template.loaders.filesystem.Loader",
            "django.template.loaders.app_directories.Loader",
        ],
    )
]

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-host
EMAIL_HOST = "localhost"
# https://docs.djangoproject.com/en/dev/ref/settings/#email-port
EMAIL_PORT = 1025

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

WORKSHOP_MODELS += ('test_app.BasicModel', )
MODELS_TO_INDEX += ('test_app.BasicModel', )