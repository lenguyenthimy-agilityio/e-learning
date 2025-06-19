"""
Tests for the courses app.
"""

from core.constants import CourseStatus, UserRole
from core.tests import BaseAPITestCase
from courses.apis import CourseViewSet
from courses.factories import CategoryFactory, CourseFactory
from courses.models import Course, Enrollment
from lessons.factories import LessonFactory
from users.models import User


class CourseAPITestCase(BaseAPITestCase):
    """
    Course API test cases.
    """

    resource = CourseViewSet

    def setUp(self):
        """
        Set up the test case with an instructor and a course.
        """
        super().setUp()
        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.set_authenticate(self.instructor)

        self.course = CourseFactory(instructor=self.instructor)

        self.fragment = str(self.course.id)

    def tearDown(self):
        """
        Clean up after each test case.
        """
        super().tearDown()
        User.objects.all().delete()

    def test_list_courses_success(self):
        """
        Test listing published courses.
        """
        response = self.get_json_ok()
        assert response.status_code == 200
        assert response.data["data"][0]["id"] == self.course.id

    def test_retrieve_course_success(self):
        """
        Test retrieving a single course.
        """
        response = self.get_json_ok(fragment=self.fragment)
        assert response.status_code == 200
        assert response.data["id"] == self.course.id

    def test_create_course_success(self):
        """
        Test course creation by an instructor.
        """
        payload = {
            "title": "New Course",
            "description": "New Description",
            "category": self.course.category.id,
        }
        response = self.post_json_ok(data=payload)
        assert response.status_code == 201
        assert response.data["title"] == "New Course"

    def test_create_course_duplicate_title(self):
        """
        Test creating a course with a duplicate title.
        """
        payload = {
            "title": self.course.title,
            "description": "Duplicate",
            "category": self.course.category.id,
        }
        response = self.post_json_bad_request(data=payload)
        assert response.status_code == 400

    def test_update_course_success(self):
        """
        Test updating course info.
        """
        payload = {
            "title": "Updated DRF",
            "description": "New desc",
            "category": self.course.category.id,
        }
        response = self.patch_json_ok(fragment=self.fragment, data=payload)
        assert response.status_code == 200
        assert response.data["title"] == "Updated DRF"

    def test_delete_course_success(self):
        """
        Test deleting a course with no enrollments.
        """
        response = self.delete_json_no_content(fragment=self.fragment)
        assert response.status_code == 204
        assert not Course.objects.filter(id=self.course.id).exists()

    def test_delete_course_has_enrollments(self):
        """
        Test deleting a course that has enrollments.
        """
        student = self.make_user(role=UserRole.STUDENT.value)
        self.course.enrollments.create(student=student)

        response = self.delete_json_bad_request(fragment=self.fragment)
        assert response.status_code == 400
        assert Course.objects.filter(id=self.course.id).exists()

    def test_set_status_to_publish_success(self):
        """
        Test publishing a course.
        """
        self.course.status = CourseStatus.UNPUBLISHED.value
        self.course.save()

        response = self.post_json_ok(
            fragment=f"{self.course.id}/set-status", data={"status": CourseStatus.PUBLISHED.value}
        )
        assert response.status_code == 200
        assert response.data["status"] == CourseStatus.PUBLISHED.value

    def test_set_status_to_unpublish_success(self):
        """
        Test publishing a course.
        """
        response = self.post_json_ok(
            fragment=f"{self.course.id}/set-status", data={"status": CourseStatus.UNPUBLISHED.value}
        )
        assert response.status_code == 200
        assert response.data["status"] == CourseStatus.UNPUBLISHED.value

    def test_student_create_course_forbidden(self):
        """
        Test that a student cannot create a course.
        """
        student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(student)

        payload = {
            "title": "Student Course",
            "description": "Student Description",
            "category": CategoryFactory().id,
        }
        response = self.post_json_forbidden(data=payload)
        assert response.status_code == 403

    def test_student_update_course_forbidden(self):
        """
        Test that a student cannot update a course.
        """
        student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(student)

        payload = {
            "title": "Student Update",
            "description": "Student Description",
            "category": self.course.category.id,
        }
        response = self.patch_json_forbidden(fragment=self.fragment, data=payload)
        assert response.status_code == 403

    def test_student_delete_course_forbidden(self):
        """
        Test that a student cannot delete a course.
        """
        student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(student)

        response = self.delete_json_forbidden(fragment=self.fragment)
        assert response.status_code == 403

    def test_set_status_to_unpublish_with_enrollments(self):
        """
        Test that a course with enrollments cannot be unpublished.
        """
        student = self.make_user(role=UserRole.STUDENT.value)
        self.course.enrollments.create(student=student)

        response = self.post_json_bad_request(
            fragment=f"{self.course.id}/set-status", data={"status": CourseStatus.UNPUBLISHED.value}
        )
        assert response.status_code == 400

    def test_view_enrolled_students_success(self):
        """
        Test viewing enrolled students in a course.
        """
        student_1 = self.make_user(role=UserRole.STUDENT.value)
        student_2 = self.make_user(role=UserRole.STUDENT.value)
        category = CategoryFactory()
        course = CourseFactory(
            category=category,
            instructor=self.instructor,
        )
        Enrollment.objects.create(student=student_1, course=course)
        Enrollment.objects.create(student=student_2, course=course)
        self.set_authenticate(user=self.instructor)

        response = self.get_json_ok(fragment=f"{course.id}/students")

        assert response.status_code == 200
        assert len(response.data["data"]) == 2

    def test_student_get_list_lessons_for_course(self):
        """
        Test listing lessons for a course.
        """
        student = self.make_user(role=UserRole.STUDENT.value)

        lesson = LessonFactory(course=self.course)
        Enrollment.objects.create(course=self.course, student=student)

        self.set_authenticate(user=student)
        response = self.get_json_ok(fragment=f"{self.course.id}/lessons")
        assert response.status_code == 200
        assert response.data["data"][0]["id"] == lesson.id

    def test_student_can_not_get_list_lessons_for_course_not_enroll(self):
        """
        Test listing lessons for a course.
        """
        student = self.make_user(role=UserRole.STUDENT.value)

        LessonFactory(course=self.course)
        self.set_authenticate(user=student)

        response = self.get_json_forbidden(fragment=f"{self.course.id}/lessons")
        assert response.status_code == 403

    def test_list_lessons_filtered_by_title(self):
        """
        Test listing lessons filtered by title.
        """
        student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(user=student)

        # Add an extra lesson with a different title
        LessonFactory(course=self.course, title="Django Basics")
        LessonFactory(course=self.course, title="Advanced Django")
        Enrollment.objects.create(course=self.course, student=student)

        response = self.get_json_ok(fragment=f"{self.course.id}/lessons/?title=Django Basics")

        assert response.status_code == 200
        data = response.data["data"]
        assert len(data) == 1
        assert "Django Basics" in data[0]["title"]
