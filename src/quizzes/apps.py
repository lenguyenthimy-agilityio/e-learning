"""
Quizzes application configuration module.
"""

from django.apps import AppConfig


class QuizzesConfig(AppConfig):
    """
    Quizzes application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "quizzes"
