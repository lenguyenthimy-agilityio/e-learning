"""
Serializers for the Lesson model.
"""

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
