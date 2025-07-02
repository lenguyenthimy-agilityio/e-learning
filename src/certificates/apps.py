"""
Django app configuration for the certificate application.
"""

from django.apps import AppConfig


class CertificateConfig(AppConfig):
    """
    Certificate application configuration.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "certificates"
