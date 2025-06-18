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
from courses.permissions import IsCourseOwner, IsInstructor, IsStudent
from courses.serializers import (
    CourseParamSerializer,
    CourseRequestSerializer,
    CourseSerializer,
    CourseStatusUpdateSerializer,
    CourseUpdateSerializer,
    EnrollmentRequestSerializer,
    EnrollmentSerializer,
    EnrollmentStudentSerializer,
    MyEnrollmentSerializer,
)
from courses.services import CourseService, EnrollmentService
from lessons.models import Lesson
from lessons.serializers import LessonSerializer
from lessons.services import LessonService


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

    def __init__(self, **kwargs):
        """
        Initialize the CourseViewSet.
        """
        super().__init__(**kwargs)
        self.enrollment_service = EnrollmentService()
        self.course_service = CourseService()
        self.lesson_service = LessonService()

    def get_permissions(self):
        """
        Apply custom permissions per action.
        """
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsInstructor(), IsCourseOwner()]
        return super().get_permissions()

    @extend_schema(
        parameters=build_query_parameters(CourseParamSerializer),
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
        serializer = CourseSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save(instructor=instructor)
        return self.response_created(data=serializer.data)

    @extend_schema(responses={**base_responses, 200: CourseSerializer})
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """
        Retrieve a specific course by ID.
        """
        course = self.get_object()

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

    @extend_schema(responses={**base_responses, 204: None})
    def destroy(self, request, *args, **kwargs):
        """
        Delete a course (if not enrolled by any student).
        """
        course = self.get_object()
        self.course_service.verify_destroy_course(course)
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
        new_status = request.data.get("status")

        # DO NOT allow changing status if the course has enrolled students
        self.course_service.verify_update_status(course, new_status)

        course.status = new_status
        course.save()
        serializer = self.get_serializer(course)
        return self.response_ok(data=serializer.data)

    @extend_schema(responses={**base_responses, 200: EnrollmentStudentSerializer(many=True)})
    @action(
        detail=True,
        methods=["get"],
        url_path="students",
        permission_classes=[IsInstructor, IsCourseOwner],
    )
    def students(self, request: Request, *args, **kwargs) -> Response:
        """
        Get list of students enrolled in this course (instructor only).
        """
        course = self.get_object()

        enrollments = self.enrollment_service.list_enrollment_specific_course(course)
        page = self.paginate_queryset(enrollments)
        serializer = EnrollmentStudentSerializer(page, many=True)

        return self.get_paginated_response(serializer.data)

    extend_schema(responses={200: LessonSerializer(many=True)})

    @action(detail=True, methods=["get"], url_path="lessons")
    def lessons(self, request: Request, *args, **kwargs) -> Response:
        """
        List all lessons for a course.
        """
        course = self.get_object()
        user = request.user

        self.lesson_service.verify_lesson_enrolled(user, course)

        queryset = Lesson.objects.filter(course=course)

        # Optional filter by title
        title = request.query_params.get("title")
        if title:
            queryset = queryset.filter(title__icontains=title)

        page = self.paginate_queryset(queryset)
        serializer = LessonSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class EnrollmentViewSet(BaseAPIViewSet):
    """
    Handling enrollments.
    """

    resource_name = "enrollments"
    pagination_class = CustomPagination
    permission_classes = [IsStudent]

    def __init__(self, **kwargs):
        """
        Initialize the EnrollmentViewSet.
        """
        super().__init__(**kwargs)
        self.course_service = CourseService()
        self.enrollment_service = EnrollmentService()

    @extend_schema(request=EnrollmentRequestSerializer, responses={**base_responses, 201: EnrollmentSerializer})
    def create(self, request):
        """
        Enroll in a course.
        """
        user = request.user
        serializer = EnrollmentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data["course_id"]

        course = self.course_service.get_course(course_id)

        # Verify if the course is published
        self.course_service.verify_course_status(course)

        # Verify if the user is already enrolled in the course
        self.enrollment_service.verify(course, user)

        enrollment = self.enrollment_service.create(course, user)
        response_data = EnrollmentSerializer(enrollment).data
        return self.response_created(data=response_data)

    @extend_schema(responses={**base_responses, 200: MyEnrollmentSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="me")
    def my_enrollments(self, request):
        """
        List all enrollments for the authenticated user.
        """
        enrollments = self.enrollment_service.list(request.user)
        page = self.paginate_queryset(enrollments)
        serializer = MyEnrollmentSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)


apps = [CourseViewSet, EnrollmentViewSet]
