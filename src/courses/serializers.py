"""
Serializers for the Course model.
"""

from rest_framework import serializers

from core.constants import CourseStatus
from core.exception import CourseErrorMessage
from core.mixins import PaginationParamSerializerMixin
from core.serializers import BaseSerializer
from courses.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for the Course model."""

    class Meta:
        """
        Meta class for CourseSerializer.
        """

        model = Course
        fields = ["id", "title", "description", "instructor", "category", "created_at", "status"]
        read_only_fields = ["instructor", "created_at"]

    def validate_title(self, value):
        """
        Ensure the title is unique per instructor.
        """
        request = self.context.get("request")
        instructor = request.user if request else None

        if instructor and Course.objects.filter(title__iexact=value, instructor=instructor).exists():
            raise serializers.ValidationError(CourseErrorMessage.ALREADY_EXISTS)

        return value


class CourseRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for course creation requests.
    """

    class Meta:
        """
        Meta class for CourseRequestSerializer.
        """

        model = Course
        fields = ["title", "description", "category"]
        extra_kwargs = {
            "title": {"required": True},
            "description": {"required": True},
            "category": {"required": False},
        }


class CourseUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for course creation requests.
    """

    class Meta:
        """
        Meta class for CourseRequestSerializer.
        """

        model = Course
        fields = ["title", "description", "category"]
        extra_kwargs = {
            "title": {"required": False},
            "description": {"required": False},
            "category": {"required": False},
        }


class CourseParamSerializer(PaginationParamSerializerMixin):
    """
    Application user list Parameter Serializer.
    """

    title = serializers.CharField(
        required=False,
        help_text="Filter by title.",
    )
    category = serializers.CharField(
        required=False,
        help_text="Filter by category name.",
    )

    status = serializers.CharField(
        required=False,
        help_text="Filter by course status.",
    )


class CourseStatusUpdateSerializer(BaseSerializer):
    """
    Serializer for updating course status.
    """

    status = serializers.ChoiceField(
        choices=CourseStatus.choices(),
        help_text="Status of the course.",
        required=True,
    )

    def validate_status(self, value):
        """
        Validate the status field.
        """
        if value not in CourseStatus.values():
            raise serializers.ValidationError("Invalid status value.")
        return value
