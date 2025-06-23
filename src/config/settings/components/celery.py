"""
Celery configuration for the Django project.
"""

from decouple import config

from config.settings.components.common import INSTALLED_APPS

INSTALLED_APPS += ["django_celery_beat"]

# Celery config
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://localhost:6379/0")
CELERY_RESULT_BACKEND = None
CELERY_BROKER_TRANSPORT = config("CELERY_BROKER_TRANSPORT", default="redis")

CELERY_TIMEZONE = "UTC"

if CELERY_BROKER_TRANSPORT == "sqs":
    CELERY_BROKER_TRANSPORT_OPTIONS = {
        "region": config("AWS_REGION", "us-west-1"),
        "predefined_queues": {"celery": {"url": config("CELERY_SQS_QUEUE_URL", "")}},
        "polling_interval": config("CELERY_POLLING_INTERVAL", default=10, cast=int),
        "visibility_timeout": config("CELERY_VISIBILITY_TIMEOUT", default=300, cast=int),
        "wait_time_seconds": config("CELERY_WAIT_TIME_SECONDS", default=20, cast=int),
    }
