"""
Settings for testing environment.
"""

import os

from config.settings.components.common import BASE_DIR

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

DEBUG = True
