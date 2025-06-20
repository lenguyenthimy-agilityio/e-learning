"""
APIs for the lessons app.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.apis import BaseAPIViewSet

# from lessons.exceptions import LessonException
from core.schema import base_responses
from courses.permissions import IsEntityCourseOwner, IsStudent
from courses.services import CourseService
from lessons.models import Lesson
from lessons.serializers import LessonRequestSerializer, LessonSerializer, LessonUpdateSerializer
from lessons.services import LessonService


class LessonViewSet(BaseAPIViewSet):
    """
    LessonViewSet for managing lessons within courses.
    """

    permission_classes = [IsAuthenticated]
    resource_name = "lessons"
    queryset = Lesson.objects.select_related("course").all()
    serializer_class = LessonSerializer

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the LessonViewSet.
        """
        super().__init__(**kwargs)
        self.lesson_service = LessonService()
        self.course_service = CourseService()

    def get_permissions(self):
        """
        Apply custom permissions based on the action being performed.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsEntityCourseOwner()]
        elif self.action == "complete_lesson":
            return [IsStudent()]

        return super().get_permissions()

    @extend_schema(request=LessonRequestSerializer, responses={**base_responses, 201: LessonSerializer})
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new lesson for a course.
        """
        serializer = LessonRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        course_id = data.get("course_id")

        course = self.course_service.get_course(course_id)

        lesson = self.lesson_service.create_lesson(data={"course": course, **data})
        serializer = LessonSerializer(lesson)
        return self.response_created(data=serializer.data)

    @extend_schema(request=LessonUpdateSerializer, responses={**base_responses, 200: LessonSerializer})
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update an existing lesson.
        """
        lesson = self.get_object()

        serializer = LessonUpdateSerializer(lesson, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.response_ok(data=LessonSerializer(lesson).data)

    @extend_schema(responses={200: LessonSerializer})
    def retrieve(self, request, *args, **kwargs) -> Response:
        """
        Retrieve a specific lesson by its ID.
        """
        lesson = self.get_object()
        course = lesson.course
        user = request.user

        # access control: student must be enrolled OR instructor
        self.course_service.verify_enrolled(user, course)

        return self.response_ok(data=LessonSerializer(lesson).data)

    @extend_schema(responses={**base_responses, 204: None})
    def destroy(self, request, *args, **kwargs):
        """
        Delete a lesson.
        """
        lesson = self.get_object()

        # access control: lesson must not have progress
        self.lesson_service.verify_lesson_has_progress(lesson)
        lesson.delete()
        return self.response_deleted()

    @extend_schema(request=None, responses={200: LessonSerializer})
    @action(detail=True, methods=["post"], url_path="complete")
    def complete_lesson(self, request: Request, *args, **kwargs) -> Response:
        """
        Complete a lesson for the authenticated student.
        """
        user = request.user
        lesson = self.get_object()

        progress = self.lesson_service.complete_lesson(user, lesson)

        return self.response_ok(
            data={"id": str(lesson.id), "status": "completed", "completed_at": progress.date.isoformat()}
        )


apps = [LessonViewSet]
