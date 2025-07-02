"""
Test cases for the Enrollment API.
"""

from core.constants import CourseStatus, UserRole
from core.tests import BaseAPITestCase
from courses.apis import EnrollmentViewSet
from courses.factories import CategoryFactory, CourseFactory
from courses.models import Enrollment


class EnrollmentAPITestCase(BaseAPITestCase):
    """
    Enrollment API test cases.
    """

    resource = EnrollmentViewSet

    def setUp(self):
        """
        Set up the test case with a student, instructor, course, and enrollment.
        """
        super().setUp()

        self.student = self.make_user(role=UserRole.STUDENT.value)
        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.category = CategoryFactory()
        self.course = CourseFactory(
            category=self.category,
        )

        self.unpublished_course = CourseFactory(
            title="Private Course",
            description="Hidden content",
            category=self.category,
            instructor=self.instructor,
            status=CourseStatus.UNPUBLISHED.value,
        )

        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course)

    def test_view_my_enrollments_success(self):
        """
        Test viewing enrollments for the authenticated student.
        """
        self.set_authenticate(self.student)

        response = self.get_json_ok(fragment="me")

        assert response.status_code == 200
        assert len(response.data["data"]) == 1

    def test_enroll_success(self):
        """
        Test enrolling a student in a course.
        """
        self.set_authenticate(self.student)

        course = CourseFactory(
            category=self.category,
            instructor=self.instructor,
        )
        payload = {"course_id": course.id}

        response = self.post_json_created(data=payload)
        assert response.status_code == 201
        assert response.data["course_id"] == str(course.id)

    def test_enroll_already_enrolled(self):
        """
        Test attempting to enroll in a course where the student is already enrolled.
        """
        self.set_authenticate(self.student)
        payload = {"course_id": self.course.id}
        response = self.post_json_bad_request(data=payload)
        assert response.status_code == 400
        assert response.data["errors"]["code"] == "ERR_ENROLLMENT_ALREADY_EXISTS"

    def test_enroll_unpublished_course(self):
        """
        Test attempting to enroll in an unpublished course.
        """
        self.set_authenticate(self.student)

        payload = {"course_id": self.unpublished_course.id}
        response = self.post_json_bad_request(data=payload)
        assert response.status_code == 400
        assert response.data["errors"]["code"] == "ERR_COURSE_UNPUBLISHED"

    def test_instructor_cannot_enroll(self):
        """
        Test that an instructor cannot enroll in a course.
        """
        self.set_authenticate(self.instructor)

        payload = {"course_id": self.course.id}
        response = self.get_json_forbidden(data=payload)
        assert response.status_code == 403
