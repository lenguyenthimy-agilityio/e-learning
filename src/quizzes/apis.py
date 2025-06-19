"""
APIs for quizzes app.
"""

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated

from core.apis import BaseAPIViewSet
from courses.permissions import IsInstructor
from courses.services import CourseService
from quizzes.serializers import QuizRequestSerializer, QuizSerializer
from quizzes.services import QuizService


class QuizViewSet(BaseAPIViewSet):
    """
    QuizViewSet for managing quizzes within courses.
    """

    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        """
        Initialize the QuizViewSet.
        """
        super().__init__(**kwargs)
        self.quiz_service = QuizService()
        self.course_service = CourseService()

    def get_permissions(self):
        """
        Get permissions based on the action being performed.
        """
        if self.action in ["create", "update", "destroy", "add_question"]:
            return [IsAuthenticated(), IsInstructor()]

        return super().get_permissions()

    @extend_schema(request=QuizRequestSerializer, responses={201: QuizSerializer})
    def create(self, request):
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


apps = []
