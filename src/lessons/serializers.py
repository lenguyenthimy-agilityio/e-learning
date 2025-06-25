"""
Serializers for the Lesson model.
"""

from datetime import datetime

from rest_framework import serializers

from core.mixins import PaginationParamSerializerMixin
from core.serializers import BaseSerializer
from lessons.models import Lesson


class LessonRequestSerializer(BaseSerializer):
    """
    Serializer for lesson creation requests.
    """

    course_id = serializers.IntegerField()
    title = serializers.CharField()
    content = serializers.CharField(required=False, allow_blank=True)
    video_url = serializers.URLField(required=False, allow_blank=True)


class LessonUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating lesson details.
    """

    class Meta:
        """
        Meta class for LessonUpdateSerializer.
        """

        model = Lesson
        fields = ["title", "content", "video_url"]


class LessonSerializer(serializers.ModelSerializer):
    """
    Serializer for lesson details.
    """

    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        """
        Meta class for LessonSerializer.
        """

        model = Lesson
        fields = ["id", "title", "content", "video_url", "course_id"]


class LessonParamSerializer(PaginationParamSerializerMixin):
    """
    Lesson list Parameter Serializer.
    """

    title = serializers.CharField(
        required=False,
        help_text="Filter by title.",
    )


class DailyProgressCourseSerializer(BaseSerializer):
    """
    Serializer for daily progress in a course.
    """

    course_title = serializers.CharField()
    completed = serializers.IntegerField()
    in_progress = serializers.IntegerField()


class DailyProgressParamSerializer(BaseSerializer):
    """
    Daily progress Parameter Serializer.
    """

    date = serializers.CharField(
        required=False,
        help_text="Filters the results by the specified date. e.g. 2025-11-21T17:30:30.999999Z.",
    )

    def validate_date(self, value: str):
        """
        Parse and validate date from string (YYYY-MM-DD).
        """
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as e:
            raise serializers.ValidationError("Invalid date format. Use YYYY-MM-DD.") from e
