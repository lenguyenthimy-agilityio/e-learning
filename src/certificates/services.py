"""
Certificate services module.
"""

from django.utils.timezone import now

from certificates.models import Certificate
from core.exception import CertificateException


class CertificateService:
    """
    Service class for handling certificate-related operations.
    """

    def generate_certificate(self, user, course):
        """
        Generate a certificate for the user upon course completion.

        This method should create a certificate instance and return it.
        """
        if not Certificate.objects.filter(student=user, course=course).exists():
            Certificate.objects.create(
                student=user,
                course=course,
                issued_at=now(),
            )

    def get_certificate(self, user, course):
        """
        Retrieve the certificate for the user and course.

        Returns the certificate instance if it exists, otherwise None.
        """
        try:
            return Certificate.objects.get(student=user, course=course)
        except Certificate.DoesNotExist as exc:
            raise CertificateException(code="NOT_FOUND") from exc
