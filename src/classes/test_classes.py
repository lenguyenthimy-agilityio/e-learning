"""
Test live class.
"""

from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

from classes.apis import LiveClassViewSet
from classes.factories import LiveClassFactory
from core.constants import UserRole
from core.tests import BaseAPITestCase
from courses.factories import CourseFactory
from courses.models import Enrollment


class LiveClassAPITestCase(BaseAPITestCase):
    """
    Test case for live class API endpoints.
    """

    resource = LiveClassViewSet

    def setUp(self):
        """
        Set up the test case with an instructor, a student, and a course.
        """
        super().setUp()

        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.student = self.make_user(role=UserRole.STUDENT.value)
        self.course = CourseFactory.create(
            title="Math 101",
            description="Basic Mathematics Course",
            instructor=self.instructor,
        )
        self.future_time = timezone.now() + timedelta(days=1)

        self.live_class_data = {
            "course_id": str(self.course.id),
            "title": "Intro to Algebra",
            "date_time": self.future_time.isoformat(),
            "meeting_url": "https://example.com/class123",
        }

        self.set_authenticate(user=self.instructor)

    def test_create_class_success(self):
        """
        Test creating a live class successfully by an instructor.
        """
        response = self.post_json_created(data=self.live_class_data)

        assert response.status_code == 201
        assert response.data["title"] == "Intro to Algebra"
        assert response.data["meeting_url"] == "https://example.com/class123"

    def test_create_class_forbidden_for_non_owner(self):
        """
        Test that a student cannot create a live class.
        """
        other_user = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.set_authenticate(user=other_user)

        response = self.post_json_forbidden(data=self.live_class_data)

        assert response.status_code == 403

    def test_create_class_with_past_time_bad_request(self):
        """
        Test that creating a live class with a past date_time fails.
        """
        past_time = timezone.now() - timedelta(hours=1)
        data = {
            "course_id": str(self.course.id),
            "title": "Past Class",
            "date_time": past_time.isoformat(),
            "meeting_url": "https://example.com/past",
        }

        response = self.post_json_bad_request(data=data)

        assert response.status_code == 400

    def test_upcoming_classes_for_student(self):
        """
        Test that a student can view upcoming classes.
        """
        LiveClassFactory(
            course=self.course,
            title="Upcoming Class",
            date_time=self.future_time,
            meeting_url="https://example.com/upcoming",
            created_by=self.instructor,
        )
        Enrollment.objects.create(course=self.course, student=self.student)

        self.set_authenticate(user=self.student)

        response = self.get_json_ok(fragment="upcoming")

        assert response.status_code == 200
        assert len(response.data) == 1

    def test_upcoming_empty_for_unenrolled_student(self):
        """
        Test that an unenrolled student sees no upcoming classes.
        """
        LiveClassFactory(
            course=self.course,
            title="Upcoming Class",
            date_time=self.future_time,
            meeting_url="https://example.com/upcoming",
            created_by=self.instructor,
        )

        self.set_authenticate(user=self.student)
        response = self.get_json_ok(fragment="upcoming")

        assert response.status_code == 200
        assert response.data == []

    @patch("classes.apis.send_class_reminder_email.delay_on_commit")
    # TODO: need to check, not pass mock task
    def test_send_reminder_success(self, mock_task):
        """
        Test that an instructor can send a reminder for an upcoming class.
        """
        live_class = LiveClassFactory(
            course=self.course,
            title="Upcoming Class",
            date_time=self.future_time,
            meeting_url="https://example.com/upcoming",
            created_by=self.instructor,
        )
        Enrollment.objects.create(course=self.course, student=self.student)

        response = self.post_json_ok(fragment=f"{live_class.id}/send-reminder/")
        assert mock_task.assert_called_once_with(live_class.id)

        assert response.status_code == 200
        assert response.data["success"] is True

    def test_send_reminder_class_canceled(self):
        """
        Test that sending a reminder fails for a canceled class.
        """
        live_class = LiveClassFactory(
            course=self.course,
            title="Upcoming Class",
            date_time=self.future_time,
            meeting_url="https://example.com/upcoming",
            created_by=self.instructor,
            is_canceled=True,
        )

        Enrollment.objects.create(course=self.course, student=self.student)
        response = self.post_json_bad_request(fragment=f"{live_class.id}/send-reminder/")

        assert response.status_code == 400
        assert response.data["errors"]["code"] == "ERR_LIVE_CLASS_CLASS_CANCELLED"
