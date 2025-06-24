"""
Classes application configuration.
"""

from django.apps import AppConfig


class ClassesConfig(AppConfig):
    """
    Class for configuring the Classes application.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "classes"
