"""
Local settings.
"""

from config.settings.components.common import INSTALLED_APPS, MIDDLEWARE

DEBUG = True
ALLOWED_HOSTS = ["*"]

# For debug toolbar
INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
    "0.0.0.0",
]

CELERY_TASK_ALWAYS_EAGER = True
