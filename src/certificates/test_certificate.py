"""
Test cases for certificate listing and retrieval APIs.
"""

from certificates.apis import CertificateViewSet
from certificates.factories import CertificateFactory
from core.constants import UserRole
from core.tests import BaseAPITestCase
from courses.factories import CourseFactory, EnrollmentFactory


class CertificateAPITestCase(BaseAPITestCase):
    """
    Test case for certificate listing and retrieval APIs.
    """

    resource = CertificateViewSet

    def setUp(self):
        """
        Set up common objects for certificate tests.
        """
        super().setUp()
        self.student = self.make_user(role=UserRole.STUDENT.value)
        self.instructor = self.make_user(role=UserRole.INSTRUCTOR.value)
        self.set_authenticate(user=self.student)

        self.course1 = CourseFactory(instructor=self.instructor, title="Intro to Python")
        self.course2 = CourseFactory(instructor=self.instructor, title="Advanced JS")

        self.cert1 = CertificateFactory(student=self.student, course=self.course1)
        self.cert2 = CertificateFactory(student=self.student, course=self.course2)
        EnrollmentFactory(student=self.student, course=self.course1, completed=True)
        EnrollmentFactory(student=self.student, course=self.course2, completed=True)

    def test_list_certificates_success(self):
        """
        Should return all certificates of authenticated student.
        """
        response = self.get_json_ok()
        assert response.status_code == 200
        assert len(response.data) == 2

        titles = [cert["course_title"] for cert in response.data]
        assert "Intro to Python" in titles
        assert "Advanced JS" in titles

    def test_retrieve_certificate_success(self):
        """
        Should return a specific certificate for a completed course.
        """
        response = self.get_json_ok(fragment=str(self.course1.id))
        assert response.status_code == 200
        assert response.data["course_title"] == "Intro to Python"
        assert "issued_at" in response.data

    def test_retrieve_certificate_not_found(self):
        """
        Should return 400 if certificate does not exist.
        """
        new_course = CourseFactory(instructor=self.instructor)
        EnrollmentFactory(student=self.student, course=new_course, completed=True)
        response = self.get_json_bad_request(fragment=str(new_course.id))
        assert response.status_code == 400
        assert response.json()["errors"]["code"] == "ERR_CERTIFICATE_NOT_FOUND"

    def test_retrieve_certificate_incomplete_course(self):
        """
        Should return 400 if course is not completed.
        """
        incomplete_course = CourseFactory(instructor=self.instructor)
        EnrollmentFactory(student=self.student, course=incomplete_course, completed=False)
        response = self.get_json_bad_request(fragment=str(incomplete_course.id))
        assert response.status_code == 400
        assert response.json()["errors"]["code"] == "ERR_CERTIFICATE_COURSE_INCOMPLETE"

    def test_retrieve_certificate_forbidden_if_not_authenticated(self):
        """
        Should return 403 if user is not authenticated.
        """
        self.get_json_unauthorized(fragment=str(self.course1.id))

    def test_user_get_certificates_not_enrolled(self):
        """
        Should return empty list if user has no certificates.
        """
        other_student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(user=other_student)

        response = self.get_json_ok()
        assert response.status_code == 200
        assert len(response.data) == 0

    def test_user_retrieve_certificates_not_enrolled(self):
        """
        Should return 400 if user tries to retrieve a certificate for a course they are not enrolled in.
        """
        other_student = self.make_user(role=UserRole.STUDENT.value)
        self.set_authenticate(user=other_student)

        response = self.get_json_bad_request(fragment=str(self.course1.id))
        assert response.status_code == 400
        assert response.json()["errors"]["code"] == "ERR_ENROLLMENT_NOT_FOUND"
