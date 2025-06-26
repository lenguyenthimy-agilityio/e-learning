"""
Dashboard APIs for managing and retrieving data related to the dashboard.
"""

# dashboard/views.py

from django.db.models import Avg
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.apis import BaseAPIViewSet
from core.schema import base_responses
from courses.models import Enrollment
from courses.permissions import IsStudent
from dashboard.serializers import (
    AverageQuizScoreSerializer,
    CompletedCoursesSerializer,
    RecentClassSerializer,
    RecentEnrolledCourseSerializer,
    TotalEnrolledCoursesSerializer,
)
from dashboard.services import DashboardService
from quizzes.models import QuizSubmission


class DashboardViewSet(BaseAPIViewSet):
    """
    Dashboard statistics and recent activity for students.
    """

    permission_classes = [IsAuthenticated, IsStudent]
    resource_name = "dashboard"

    def __init__(self, **kwargs):
        """
        Initialize the DashboardViewSet.
        """
        super().__init__(**kwargs)
        self.dashboard_service = DashboardService()

    @extend_schema(responses={**base_responses, 200: TotalEnrolledCoursesSerializer})
    @action(detail=False, methods=["get"], url_path="total-enrolled-courses")
    def total_enrolled_courses(self, request: Request) -> Response:
        """
        Get the total number of courses a student is enrolled in.
        """
        count = Enrollment.objects.filter(student=request.user).count()
        return self.response_ok({"total_enrolled_courses": count})

    @extend_schema(responses={**base_responses, 200: CompletedCoursesSerializer})
    @action(detail=False, methods=["get"], url_path="completed-courses")
    def completed_courses(self, request: Request) -> Response:
        """
        Get the number of courses a student has completed.
        """
        count = Enrollment.objects.filter(student=request.user, completed=True).count()
        return self.response_ok({"completed_courses": count})

    @extend_schema(responses={**base_responses, 200: AverageQuizScoreSerializer})
    @action(detail=False, methods=["get"], url_path="average-quiz-score")
    def average_quiz_score(self, request: Request) -> Response:
        """
        Get the average quiz score for the student.
        """
        submissions = QuizSubmission.objects.filter(student=request.user)
        avg = submissions.aggregate(avg_score=Avg("score"))["avg_score"]
        return self.response_ok({"average_quiz_score": round(avg or 0, 2)})

    @extend_schema(responses={200: RecentEnrolledCourseSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="recent-enrolled-courses")
    def recent_enrolled_courses(self, request: Request) -> Response:
        """
        Get the most recent courses a student has enrolled in.
        """
        recent_course = self.dashboard_service.get_recent_enrollment_course(request.user)
        serializer = RecentEnrolledCourseSerializer(recent_course, many=True).data
        return self.response_ok(data=serializer)

    @extend_schema(responses={**base_responses, 200: RecentClassSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="recent-classes")
    def recent_classes(self, request: Request) -> Response:
        """
        Get recent lessons and live sessions for the authenticated student.
        """
        user = request.user

        data = self.dashboard_service.get_recent_classes(user)

        serializer = RecentClassSerializer(data, many=True)

        return self.response_ok(data=serializer.data)


apps = [DashboardViewSet]
