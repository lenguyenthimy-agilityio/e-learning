"""
Serializers for handling live class sessions in the application.
"""

from django.utils import timezone
from rest_framework import serializers

from classes.models import LiveClass
from courses.models import Course


class LiveClassRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new live class session.
    """

    course_id = serializers.IntegerField(write_only=True)

    class Meta:
        """
        Meta class for LiveClassRequestSerializer.
        """

        model = LiveClass
        fields = ["id", "course_id", "title", "date_time", "meeting_url"]

    def validate_date_time(self, value):
        """
        Validate the date_time field to ensure it is not in the past.
        """
        if value <= timezone.now():
            raise serializers.ValidationError("The class start time cannot be in the past.")
        return value

    def create(self, validated_data):
        """
        Create a new LiveClass instance with the validated data.
        """
        course = Course.objects.get(id=validated_data.pop("course_id"))
        return LiveClass.objects.create(course=course, created_by=self.context["request"].user, **validated_data)


class LiveClassSerializer(serializers.ModelSerializer):
    """
    Serializer for displaying live class session details.
    """

    course_id = serializers.IntegerField(source="course.id", read_only=True)

    class Meta:
        """
        Meta class for LiveClassSerializer.
        """

        model = LiveClass
        fields = ["id", "course_id", "title", "date_time", "meeting_url", "created_by", "created_at", "updated_at"]
