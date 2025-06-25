"""
The module contains tests for the lessons app.
"""

from core.constants import DailyProcessStatus, UserRole
from core.tests import BaseAPITestCase
from courses.factories import CategoryFactory, CourseFactory
from courses.models import Enrollment
from lessons.apis import LessonViewSet
from lessons.factories import LessonFactory, LessonProgressFactory
from lessons.models import Lesson


class LessonAPITestCase(BaseAPITestCase):
    """
    Test case for Lesson API endpoints.
    """

    resource = LessonViewSet

    def setUp(self):
        """Set up the test case with initial data."""
        super().setUp()

        self.student = self.make_user(role=UserRole.STUDENT.value)

        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.category = CategoryFactory.create(name="Programming")

        self.course = CourseFactory(
            instructor=self.instructor,
            category=self.category,
        )

        self.lesson = LessonFactory(course=self.course)

        self.enrollment = Enrollment.objects.create(course=self.course, student=self.student)

    def test_create_lesson_success(self):
        """
        Test creating a lesson successfully by an instructor.
        """
        self.set_authenticate(user=self.instructor)

        payload = {
            "course_id": self.course.id,
            "title": "Lesson 2",
            "content": "Advanced topics",
            "videoUrl": "http://video.com",
        }

        response = self.post_json_created(data=payload)
        assert response.status_code == 201
        assert response.data["title"] == "Lesson 2"

    def test_create_lesson_forbidden_if_not_owner(self):
        """
        Test that a student cannot create a lesson.
        """
        self.set_authenticate(user=self.student)
        payload = {
            "course_id": self.course.id,
            "title": "Lesson 2",
            "content": "Advanced topics",
            "videoUrl": "http://video.com",
        }
        response = self.post_json_forbidden(data=payload)
        assert response.status_code == 403

    def test_get_lesson_as_enrolled_student(self):
        """
        Test that an enrolled student can view a lesson.
        """
        self.set_authenticate(user=self.student)

        response = self.get_json_ok(fragment=f"{self.lesson.id}")
        assert response.status_code == 200
        assert response.data["title"] == self.lesson.title

    def test_get_lesson_forbidden_if_not_enrolled(self):
        """
        Test that a student cannot view a lesson if not enrolled.
        """
        other_student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(user=other_student)

        response = self.get_json_forbidden(fragment=f"{self.lesson.id}")
        assert response.status_code == 403

    def test_update_lesson_success(self):
        """
        Test updating a lesson successfully by an instructor.
        """
        self.set_authenticate(user=self.instructor)
        response = self.patch_json_ok(
            fragment=f"{self.lesson.id}",
            data={"title": "Updated Lesson", "content": "Updated content"},
        )
        assert response.status_code == 200
        assert response.data["title"] == "Updated Lesson"

    def test_delete_lesson_success(self):
        """
        Test deleting a lesson successfully by an instructor.
        """
        self.set_authenticate(user=self.instructor)
        response = self.delete_json_no_content(fragment=f"{self.lesson.id}")
        assert response.status_code == 204
        assert Lesson.objects.filter(id=self.lesson.id).count() == 0

    def test_delete_lesson_with_progress_forbidden(self):
        """
        Test that a lesson with progress cannot be deleted.
        """
        LessonProgressFactory(user=self.student, lesson=self.lesson)
        self.set_authenticate(user=self.instructor)
        response = self.delete_json_bad_request(fragment=f"{self.lesson.id}")
        assert response.status_code == 400

    def test_delete_lesson_forbidden_if_not_owner(self):
        """
        Test that a student cannot delete a lesson.
        """
        self.set_authenticate(user=self.student)
        response = self.delete_json_forbidden(fragment=f"{self.lesson.id}")
        assert response.status_code == 403

    def test_complete_lesson_success(self):
        """
        Test completing a lesson successfully by an enrolled student.
        """
        self.set_authenticate(user=self.student)
        response = self.post_json_ok(fragment=f"{self.lesson.id}/complete")
        assert response.status_code == 200
        assert response.data["status"] == "Completed"

    def test_instructor_can_not_complete_lesson_success(self):
        """
        Test that an instructor cannot complete a lesson.
        """
        self.set_authenticate(user=self.instructor)
        response = self.post_json_forbidden(fragment=f"{self.lesson.id}/complete")
        assert response.status_code == 403

    def test_complete_lesson_already_done(self):
        """
        Test that a student cannot complete a lesson that is already completed.
        """
        LessonProgressFactory.create(user=self.student, lesson=self.lesson, status=DailyProcessStatus.COMPLETED.value)
        self.set_authenticate(user=self.student)

        response = self.post_json_bad_request(fragment=f"{self.lesson.id}/complete")
        assert response.status_code == 400
        assert response.data["errors"]["code"] == "ERR_LESSON_ALREADY_COMPLETED"
