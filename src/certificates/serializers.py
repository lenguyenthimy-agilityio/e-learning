"""
Certificate serializers.
"""

from rest_framework import serializers

from certificates.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    """
    Serializer for the Certificate model.
    """

    course_title = serializers.CharField(source="course.title")

    class Meta:
        """
        Meta options for the CertificateSerializer.
        """

        model = Certificate
        fields = ["id", "course_title", "issued_at"]
