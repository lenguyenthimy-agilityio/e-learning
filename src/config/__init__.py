"""
The module initializes the Celery application for the project.
"""

from .celery import app as celery_app

__all__ = ("celery_app",)
