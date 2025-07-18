"""Lessons application configuration module."""

from django.apps import AppConfig


class LessonsConfig(AppConfig):
    """
    Lessons application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "lessons"
