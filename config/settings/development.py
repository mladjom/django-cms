from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]

# Additional development-only apps
INSTALLED_APPS += [
    'django_browser_reload',
    'django_extensions',
]

MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]