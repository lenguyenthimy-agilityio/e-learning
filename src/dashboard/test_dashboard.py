"""
Test cases for Dashboard Stats API endpoints.
"""

from datetime import timedelta

from django.utils import timezone

from classes.factories import LiveClassFactory
from core.constants import DailyProcessStatus, UserRole
from core.tests import BaseAPITestCase
from courses.factories import CourseFactory, EnrollmentFactory, LessonFactory
from dashboard.apis import DashboardViewSet
from lessons.factories import LessonProgressFactory
from quizzes.factories import QuizSubmissionFactory


class DashboardAPITestCase(BaseAPITestCase):
    """
    Test case for Dashboard Stats API endpoints.
    """

    resource = DashboardViewSet

    def setUp(self):
        """Set up common objects for dashboard tests."""
        super().setUp()
        self.student = self.make_user(role=UserRole.STUDENT.value)
        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)

        self.set_authenticate(user=self.student)

        self.course1 = CourseFactory(instructor=self.instructor)
        self.course2 = CourseFactory(instructor=self.instructor)
        self.course3 = CourseFactory(instructor=self.instructor)

        self.enrollment1 = EnrollmentFactory(student=self.student, course=self.course1, completed=False)
        self.enrollment2 = EnrollmentFactory(student=self.student, course=self.course2, completed=False)
        self.enrollment3 = EnrollmentFactory(student=self.student, course=self.course3, completed=True)

        self.lesson1 = LessonFactory(course=self.course1)
        self.lesson2 = LessonFactory(course=self.course2)

    def test_total_enrolled_courses(self):
        """
        Should return correct count of enrolled courses.
        """
        response = self.get_json_ok(fragment="total-enrolled-courses")
        assert response.status_code == 200
        assert response.data["total_enrolled_courses"] == 3

    def test_completed_courses(self):
        """
        Should return correct count of completed courses.
        """
        response = self.get_json_ok(fragment="completed-courses")
        assert response.status_code == 200
        assert response.data["completed_courses"] == 1

    def test_average_quiz_score(self):
        """
        Should calculate average quiz score for student.
        """
        QuizSubmissionFactory(student=self.student, score=80, quiz__course=self.course1)
        QuizSubmissionFactory(student=self.student, score=90, quiz__course=self.course2)

        response = self.get_json_ok(fragment="average-quiz-score")
        assert response.status_code == 200
        assert response.data["average_quiz_score"] == 85.00

    def test_recent_enrolled_courses(self):
        """
        Should return recently enrolled courses (max 5).
        """
        self.enrollment1.enrolled_at = timezone.now() - timedelta(days=2)
        self.enrollment2.enrolled_at = timezone.now() - timedelta(days=1)
        self.enrollment3.enrolled_at = timezone.now()
        self.enrollment1.save()
        self.enrollment2.save()
        self.enrollment3.save()

        response = self.get_json_ok(fragment="recent-enrolled-courses")
        assert response.status_code == 200
        assert len(response.data) == 3
        assert response.data[0]["course_id"] == self.course3.id  # most recent first

    def test_recent_classes_combines_lessons_and_live_sessions(self):
        """
        Should return combined list of recent lessons and live classes.
        """
        # Completed lesson
        LessonProgressFactory(
            user=self.student,
            lesson=self.lesson1,
            status=DailyProcessStatus.COMPLETED.value,
            updated_at=timezone.now() - timedelta(days=1),
        )

        # Upcoming live session
        LiveClassFactory(
            course=self.course1,
            date_time=timezone.now() + timedelta(hours=1),
            is_canceled=False,
            created_by=self.instructor,
        )

        response = self.get_json_ok(fragment="recent-classes")
        assert response.status_code == 200
        assert len(response.data) == 2
        assert "total_minutes" in response.data[0]
        assert any(r["type"] == "lesson" for r in response.data)
        assert any(r["type"] == "live_session" for r in response.data)
