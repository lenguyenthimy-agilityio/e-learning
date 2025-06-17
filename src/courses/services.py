"""
The module contains services related to course management.
"""

from core.constants import CourseStatus
from core.exception import CourseException, EnrollmentException
from courses.models import Course, Enrollment
from users.models import User


class EnrollmentService:
    """
    Service class for handling course enrollment operations.
    """

    def verify(self, course: Course, user: User) -> None:
        """
        Verify if the user is already enrolled in the course.

        Raises an exception if the user is already enrolled.
        """
        if Enrollment.objects.filter(course=course, student=user).exists():
            raise EnrollmentException(code="ALREADY_EXISTS")

    def create(self, course: Course, user: User) -> Enrollment:
        """
        Create a new enrollment for the user in the specified course.

        Returns the created Enrollment object.
        """
        return Enrollment.objects.create(course=course, student=user)

    def list(self, user: User) -> list[Course]:
        """
        Returns a queryset of Enrollment objects related to the user.
        """
        enrollments = Enrollment.objects.filter(student=user).select_related("course")
        return enrollments

    def list_enrollment_specific_course(self, course: Course) -> list:
        """
        Returns a queryset of Enrollment objects related to the specified course.
        """
        return course.enrollments.select_related("student")


class CourseService:
    """
    Service class for handling course operations.
    """

    def get_course(self, course_id: str) -> Course:
        """
        Verify if the course exists by its ID.

        Raises an exception if the course does not exist.
        """
        try:
            return Course.objects.get(id=course_id)
        except Exception as exc:
            raise CourseException(code="NOT_FOUND", developer_message=str(exc)) from exc

    def verify_course_status(self, course: Course) -> None:
        """
        Verify if the course is published.

        Raises an exception if the course is not published.
        """
        if course.status != CourseStatus.PUBLISHED.value:
            raise CourseException(code="UNPUBLISHED")

    def verify_destroy_course(self, course: Course) -> None:
        """
        Verify if the course can be destroyed.

        Raises an exception if the course has enrollments.
        """
        if course.enrollments.exists():
            raise CourseException(code="HAS_ENROLLMENTS")

    def verify_update_status(self, course: Course, new_status: str) -> None:
        """
        Verify if the course can be updated to the new status.

        Args:
            course (Course): Course instance to verify.
            new_status (str): New status to set for the course.
        """
        if new_status == CourseStatus.UNPUBLISHED.value and course.enrollments.exists():
            raise CourseException(code="HAS_ENROLLMENTS")
