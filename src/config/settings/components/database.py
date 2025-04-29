"""
Database setting
"""

from decouple import config


DATABASE_HOST: str = config("DATABASE_HOST", default="localhost")
DATABASE_NAME: str = config("DATABASE_NAME")
DATABASE_USER: str = config("DATABASE_USER")
DATABASE_PASSWORD: str = config("DATABASE_PASSWORD")

# Runs database migration if DATABASE_MIGRATE flag is set
DATABASE_ENGINE: str = config("DATABASE_ENGINE", default="django.db.backends.postgresql")
DATABASE_MIGRATE: str = config("DATABASE_MIGRATE", default="true")
DATABASE_PORT: int = config("DATABASE_PORT", default=5432, cast=int)

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "NAME": DATABASE_NAME,
        "USER": DATABASE_USER,
        "ENGINE": DATABASE_ENGINE,
        "PASSWORD": DATABASE_PASSWORD,
        "HOST": DATABASE_HOST,
        "PORT": DATABASE_PORT,
    }
}
