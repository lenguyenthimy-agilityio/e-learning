"""
Tests for the Daily Progress API.
"""

from datetime import timedelta

from django.utils import timezone

from core.constants import DailyProcessStatus, UserRole
from core.tests import BaseAPITestCase
from courses.factories import CategoryFactory, CourseFactory
from lessons.apis import DailyProgressViewSet
from lessons.factories import LessonFactory, LessonProgressFactory


class DailyProgressAPITestCase(BaseAPITestCase):
    """
    Test case for Daily Progress API endpoints.
    """

    resource = DailyProgressViewSet

    def setUp(self):
        """
        Set up users, course, and lessons for testing.
        """
        super().setUp()
        self.date = timezone.now().date()

        self.student = self.make_user(role=UserRole.STUDENT.value)
        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.category = CategoryFactory(name="Math")

        self.course = CourseFactory(instructor=self.instructor, category=self.category)
        self.lesson1 = LessonFactory(course=self.course, title="Lesson 1")
        self.lesson2 = LessonFactory(course=self.course, title="Lesson 2")

        self.set_authenticate(user=self.student)

    def test_progress_counts_by_course(self):
        """
        Test daily completed and in-progress lesson counts by course.
        """
        LessonProgressFactory.create(
            user=self.student,
            lesson=self.lesson1,
            status=DailyProcessStatus.COMPLETED.value,
            date=self.date,
        )
        LessonProgressFactory.create(
            user=self.student,
            lesson=self.lesson2,
            status=DailyProcessStatus.IN_PROGRESS.value,
            date=self.date,
        )

        response = self.get_json_ok(fragment=f"courses/?date={self.date.isoformat()}")

        assert response.status_code == 200
        assert len(response.data) == 1

        course = response.data[0]
        assert course["course_title"] == self.course.title
        assert course["completed"] == 1
        assert course["in_progress"] == 1

    def test_returns_empty_when_no_progress(self):
        """
        Test that no data is returned if student has no progress.
        """
        response = self.get_json_ok(fragment=f"courses/?date={self.date.isoformat()}")
        assert response.status_code == 200
        assert response.data == []

    def test_filters_only_today_progress(self):
        """
        Test that only progress from the specified date is counted.
        """
        yesterday = self.date - timedelta(days=1)

        # One from yesterday
        LessonProgressFactory(
            user=self.student,
            lesson=self.lesson1,
            status=DailyProcessStatus.COMPLETED.value,
            date=yesterday,
        )

        # One from today
        LessonProgressFactory(
            user=self.student,
            lesson=self.lesson2,
            status=DailyProcessStatus.IN_PROGRESS.value,
            date=self.date,
        )

        response = self.get_json_ok(fragment=f"courses/?date={self.date.isoformat()}")
        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0]["in_progress"] == 1
        assert response.data[0]["completed"] == 0
