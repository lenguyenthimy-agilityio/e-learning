"""
Serializers for the dashboard app.
"""

from rest_framework import serializers

from core.serializers import BaseSerializer


class TotalEnrolledCoursesSerializer(BaseSerializer):
    """
    Serializer for total enrolled courses in the dashboard.
    """

    total_enrolled_courses = serializers.IntegerField()


class CompletedCoursesSerializer(BaseSerializer):
    """
    Serializer for completed courses in the dashboard.
    """

    completed_courses = serializers.IntegerField()


class AverageQuizScoreSerializer(BaseSerializer):
    """
    Serializer for average quiz score in the dashboard.
    """

    average_quiz_score = serializers.DecimalField(max_digits=5, decimal_places=2)


class RecentEnrolledCourseSerializer(BaseSerializer):
    """
    Serializer for recent enrolled courses in the dashboard.
    """

    course_id = serializers.IntegerField(source="course.id")
    title = serializers.CharField(source="course.title")
    enrolled_at = serializers.DateTimeField()


class RecentClassSerializer(BaseSerializer):
    """
    Recent class serializer.
    """

    type = serializers.ChoiceField(choices=["lesson", "live_session"])
    title = serializers.CharField()
    timestamp = serializers.DateTimeField(required=False)
