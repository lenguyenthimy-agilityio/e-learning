"""
APIs for quizzes app.
"""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.apis import BaseAPIViewSet
from core.schema import base_responses
from courses.permissions import IsEntityCourseOwner, IsStudent
from courses.services import CourseService, EnrollmentService
from lessons.services import LessonService
from quizzes.models import Quiz
from quizzes.serializers import (
    QuestionSerializer,
    QuizRequestSerializer,
    QuizSerializer,
    QuizSubmissionSerializer,
    QuizUpdateSerializer,
)
from quizzes.services import QuizService


class QuizViewSet(BaseAPIViewSet):
    """
    QuizViewSet for managing quizzes within courses.
    """

    resource_name = "quizzes"
    permission_classes = [IsAuthenticated]
    queryset = Quiz.objects.select_related("course").all()

    def __init__(self, **kwargs):
        """
        Initialize the QuizViewSet.
        """
        super().__init__(**kwargs)
        self.quiz_service = QuizService()
        self.course_service = CourseService()
        self.lesson_service = LessonService()
        self.enrollment_service = EnrollmentService()

    def get_permissions(self):
        """
        Get permissions based on the action being performed.
        """
        if self.action in ["create", "update", "destroy", "add_question", "partial_update"]:
            return [IsAuthenticated(), IsEntityCourseOwner()]

        return super().get_permissions()

    @extend_schema(request=QuizRequestSerializer, responses={**base_responses, 201: QuizSerializer})
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Create a new quiz for a course.
        """
        serializer = QuizRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course_id = serializer.validated_data["course_id"]

        course = self.course_service.get_course(course_id)
        title = serializer.validated_data["title"]

        quiz = self.quiz_service.create_quiz(course, title)
        serializer = QuizSerializer(quiz)

        return self.response_created(data=serializer.data)

    @extend_schema(request=QuizUpdateSerializer, responses={**base_responses, 201: QuizSerializer})
    def partial_update(self, request: Request, *args, **kwargs) -> Response:
        """
        Update a quiz's title.

        """
        quiz = self.get_object()

        serializer = QuizUpdateSerializer(quiz, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.response_ok(data=QuizSerializer(quiz).data)

    @extend_schema(
        responses={**base_responses, 200: QuizSerializer},
    )
    def retrieve(self, request: Request, *args, **kwargs) -> Response:
        """

        Retrieve a specific quiz by its ID.
        """
        quiz = self.get_object()

        user = request.user
        course = quiz.course
        # Verify if the user is enrolled in the course
        self.course_service.verify_enrolled(user, course)

        return self.response_ok(data=QuizSerializer(quiz).data)

    @extend_schema(responses={**base_responses, 204: None})
    def destroy(self, request: Request, *args, **kwargs) -> Response:
        """
        Delete a quiz.
        """
        quiz = self.get_object()

        quiz.delete()
        return self.response_deleted()

    @extend_schema(
        request=QuestionSerializer,
        responses={201: QuestionSerializer},
    )
    @action(detail=True, methods=["post"], url_path="questions")
    def add_question(self, request: Request, *args, **kwargs) -> Response:
        """
        Add a question to a quiz.
        """
        quiz = self.get_object()

        serializer = QuestionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(quiz=quiz)
        return self.response_created(data=serializer.data)

    @extend_schema(
        request=QuizSubmissionSerializer,
        responses={200: dict},
    )
    @action(detail=True, methods=["post"], url_path="submit", permission_classes=[IsStudent])
    def submit(self, request: Request, pk=None) -> Response:
        """
        Submit answers for a quiz.
        """
        quiz = self.get_object()
        user = request.user

        self.course_service.verify_enrolled(user, quiz.course)
        # Verify if the quiz is submitted
        self.quiz_service.is_submitted(user, quiz)

        serializer = QuizSubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        answers = serializer.validated_data["answers"]

        self.quiz_service.verify_all_questions_answered(answers, quiz)
        submission, score = self.quiz_service.submit_quiz(answers, user, quiz)

        return self.response_ok(
            data={
                "submission_id": submission.id,
                "quiz_id": quiz.id,
                "score": score,
                "submitted_at": submission.submitted_at.isoformat(),
            }
        )


apps = [QuizViewSet]
