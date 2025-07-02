"""
API for managing certificates in the system.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from certificates.models import Certificate
from certificates.serializers import CertificateSerializer
from certificates.services import CertificateService
from core.apis import BaseAPIViewSet
from core.exception import CertificateException
from core.schema import base_responses
from courses.services import EnrollmentService


class CertificateViewSet(BaseAPIViewSet):
    """
    ViewSet for certificate issuing and viewing.
    """

    permission_classes = [IsAuthenticated]
    resource_name = "certificates"

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the CertificateViewSet.
        """
        super().__init__(**kwargs)
        self.enrollment_service = EnrollmentService()
        self.certificate_service = CertificateService()

    @extend_schema(responses={**base_responses, 200: CertificateSerializer(many=True)})
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        Get all certificates for the authenticated student.
        """
        certificates = Certificate.objects.filter(student=request.user).select_related("course")
        serializer = CertificateSerializer(certificates, many=True)
        return self.response_ok(serializer.data)

    @extend_schema(responses={**base_responses, 200: CertificateSerializer})
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Get a certificate for a specific course.
        """
        student = request.user
        course_id = kwargs.get("pk")

        enrollment = self.enrollment_service.get_enrollment_specific_course(
            course_id=course_id, user_id=str(student.id)
        )
        if not enrollment.completed:
            raise CertificateException(code="COURSE_INCOMPLETE")

        certificate = self.certificate_service.get_certificate(user=student, course=enrollment.course)

        serializer = CertificateSerializer(certificate)
        return self.response_ok(serializer.data)


apps = [CertificateViewSet]
