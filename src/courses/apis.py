"""
Course API ViewSet.
"""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response

from core.apis import BaseAPIViewSet
from core.paginations import CustomPagination
from core.schema import base_responses, build_query_parameters
from courses.filters import CourseFilter
from courses.models import Course
from courses.permissions import IsCourseOwner, IsInstructor
from courses.serializers import (
    CourseRequestSerializer,
    CourseSerializer,
    CourseStatusUpdateSerializer,
    CourseUpdateSerializer,
)


class CourseViewSet(BaseAPIViewSet, viewsets.ModelViewSet):
    """
    ViewSet for managing courses.
    """

    resource_name = "courses"
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend]
    pagination_class = CustomPagination
    filterset_class = CourseFilter
    search_fields = ["title", "category__name"]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        """
        Apply custom permissions per action.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor(), IsCourseOwner()]
        return super().get_permissions()

    @extend_schema(
        parameters=build_query_parameters(CourseUpdateSerializer),
        responses={**base_responses, 200: CourseSerializer(many=True)},
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        List all courses with optional filters.
        """
        return super().list(request, *args, **kwargs)

    @extend_schema(request=CourseRequestSerializer, responses={**base_responses, 201: CourseSerializer})
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new course (instructors only).
        """
        instructor = request.user
        # TODO: Check the title duplicate
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(instructor=instructor)
        return self.response_created(data=serializer.data)

    @extend_schema(responses={**base_responses, 200: CourseSerializer})
    def retrieve(self, request: Request, **kwargs) -> Response:
        """
        Retrieve a specific course by ID.
        """
        course = self.get_object()
        if not course:
            return

        serializer = CourseSerializer(course)
        return self.response_ok(data=serializer.data)

    @extend_schema(request=CourseUpdateSerializer, responses={200: CourseSerializer})
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update course (only if instructor and owner).
        """
        course = self.get_object()
        serializer = CourseUpdateSerializer(course, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.response_ok(data=serializer.data)

    @extend_schema(responses={204: None})
    def destroy(self, request, *args, **kwargs):
        """
        Delete a course (if not enrolled by any student).
        """
        course = self.get_object()
        # TODO: Check if the course has enrolled students
        course.delete()
        return self.response_deleted()

    @extend_schema(
        request=CourseStatusUpdateSerializer,
        responses={200: CourseSerializer},
    )
    @action(
        detail=True,
        methods=["post"],
        url_path="set-status",
        permission_classes=[IsInstructor, IsCourseOwner],
    )
    def set_status(self, request: Request, *args, **kwargs) -> Response:
        """
        Set course status to 'published' or 'unpublished'.

        Prevent unpublishing if the course has enrolled students.
        """
        course = self.get_object()

        # TODO: Uncomment and implement status update logic
        # new_status = request.data.get("status")

        # if new_status == CourseStatus.UNPUBLISHED.value and course.enrollments.exists():
        #     raise CourseException(code="HAS_ENROLLMENTS")

        serializer = CourseSerializer(course)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.response_ok(data=serializer.data)


apps = [CourseViewSet]
