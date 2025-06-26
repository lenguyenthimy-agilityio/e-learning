"""
Service layer for the dashboard application.
"""

from classes.models import LiveClass
from core.constants import DailyProcessStatus
from lessons.models import LessonProgress


class DashboardService:
    """
    Service class for handling dashboard-related operations.
    """

    def get_recent_enrollment_course(self, user):
        """
        Get the most recent course the user has enrolled in.
        """
        enrollments = user.enrollments.select_related("course").order_by("-enrolled_at")[:5]
        return enrollments[:5] if enrollments else None

    def get_recent_classes(self, user):
        """
        Get recent lessons and live sessions for the authenticated student.
        """
        recent_classes = []
        # Fetch recent lessons
        progress = (
            LessonProgress.objects.filter(user=user, status=DailyProcessStatus.COMPLETED.value)
            .select_related("lesson")
            .order_by("-updated_at")[:5]
        )
        for p in progress:
            recent_classes.append(
                {
                    "title": p.lesson.title,
                    "type": "lesson",
                    "timestamp": p.updated_at,
                }
            )

        # Fetch recent live sessions
        course_ids = user.enrollments.values_list("course_id", flat=True)
        live_sessions = LiveClass.objects.filter(course_id__in=course_ids, is_canceled=False).order_by("date_time")[:5]
        for session in live_sessions:
            recent_classes.append(
                {
                    "title": session.title,
                    "type": "live_session",
                    "timestamp": session.date_time,
                }
            )
        recent_classes = sorted(recent_classes, key=lambda x: x["timestamp"], reverse=True)[:5]

        return recent_classes
