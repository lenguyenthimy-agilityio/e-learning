"""
The module contains services related to course management.
"""

from rest_framework.exceptions import PermissionDenied

from certificates.services import CertificateService
from core.constants import CourseStatus, DailyProcessStatus
from core.exception import CourseException, EnrollmentException
from courses.models import Course, Enrollment
from lessons.models import LessonProgress
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

    def get_enrollment_specific_course(self, course_id: int, user_id: int) -> Enrollment:
        """
        Returns the Enrollment object for the specified course and user.

        Raises an exception if the enrollment does not exist.
        """
        try:
            return Enrollment.objects.get(course_id=course_id, student_id=user_id)
        except Enrollment.DoesNotExist as exc:
            raise EnrollmentException(code="NOT_FOUND") from exc


class CourseService:
    """
    Service class for handling course operations.
    """

    def __init__(self):
        """
        Initialize the CourseService with necessary dependencies.
        """
        self.certificate_service = CertificateService()

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

    def verify_enrolled(self, user, course):
        """
        Verify if a lesson enrolled for student access.
        """
        if user != course.instructor and not Enrollment.objects.filter(course=course, student=user).exists():
            raise PermissionDenied("You do not have access to this lesson.")

    def check_and_mark_course_completion(self, user, course):
        """
        Check if all lessons in the course are completed by the user and mark the course as completed.

        Args:
            user (User): Request user
            course (Course): The course to check for completion.
        """
        total_lessons = course.lessons.count()
        completed_lessons = LessonProgress.objects.filter(
            user=user,
            lesson__course=course,
            status=DailyProcessStatus.COMPLETED.value,
        ).count()

        if total_lessons > 0 and total_lessons == completed_lessons:
            updated = Enrollment.objects.filter(student=user, course=course).update(completed=True)

            if updated:
                self.certificate_service.generate_certificate(user, course)
