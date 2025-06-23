"""
Service for managing live classes.
"""

from django.utils import timezone

from classes.models import LiveClass
from core.exception import LiveClassException
from courses.models import Enrollment


class LiveClassService:
    """
    Service for managing live classes.
    """

    def get_upcoming_classes(self, user):
        """
        List all live classes for the authenticated user.
        """
        # Assuming the user has a method to get their enrolled courses
        enrolled_course_ids = Enrollment.objects.filter(student=user).values_list("course_id", flat=True)
        return LiveClass.objects.filter(
            course_id__in=enrolled_course_ids, date_time__gte=timezone.now(), is_canceled=False
        ).order_by("date_time")

    def verify_send_reminder(self, live_class):
        """
        Verify if the user can send a reminder for the live class.
        """
        if live_class.is_canceled:
            raise LiveClassException(code="CLASS_CANCELLED")

        enrollments = Enrollment.objects.filter(course=live_class.course)
        if not enrollments.exists():
            raise LiveClassException(code="NOT_ENROLLED")
