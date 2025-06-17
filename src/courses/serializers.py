"""
Serializers for the Course model.
"""

from rest_framework import serializers

from core.constants import CourseStatus
from core.exception import CourseErrorMessage
from core.mixins import PaginationParamSerializerMixin
from core.serializers import BaseSerializer
from courses.models import Course, Enrollment


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


class EnrollmentRequestSerializer(BaseSerializer):
    """
    Serializer for course enrollment requests.
    """

    course_id = serializers.IntegerField(required=True)


class EnrollmentSerializer(serializers.ModelSerializer):
    """
    Enrollment serializer for course enrollments.
    """

    student_id = serializers.CharField(source="student.id", read_only=True)
    course_id = serializers.CharField(source="course.id", read_only=True)

    class Meta:
        """
        Meta class for EnrollmentSerializer.
        """

        model = Enrollment
        fields = ["id", "student_id", "course_id", "enrolled_at"]


class MyEnrollmentSerializer(BaseSerializer):
    """
    Serializer for the current user's enrollment in a course.
    """

    id = serializers.CharField(read_only=True)
    course = serializers.SerializerMethodField()
    enrolled_at = serializers.DateTimeField()

    def get_course(self, obj):
        """
        Get course details for the enrolled course.
        """
        course = obj.course
        return {
            "id": course.id,
            "title": course.title,
            "category": course.category.name if course.category else None,
        }


class EnrollmentStudentSerializer(BaseSerializer):
    """
    Serializer for enrolled students in a course.
    """

    student = serializers.SerializerMethodField()
    enrolled_at = serializers.DateTimeField()

    def get_student(self, obj):
        """Get student details for the enrolled student.

        Args:
            obj (course): course enrollment object

        """
        student = obj.student
        return {
            "id": f"user_{student.id}",
            "name": f"{student.first_name} {student.last_name}".strip(),
            "email": student.email,
        }
