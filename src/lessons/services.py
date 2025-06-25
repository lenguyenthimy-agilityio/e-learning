"""
Lesson services module.
"""

from datetime import date

from django.db.models import Count, Q

from core.constants import DailyProcessStatus
from core.exception import LessonException
from courses.models import Enrollment
from lessons.models import Lesson, LessonProgress


class LessonService:
    """
    Service class for handling lesson-related operations.
    """

    def create_lesson(self, data):
        """
        Create a new lesson for a course.
        """
        course = data.get("course")
        title = data.get("title")
        content = data.get("content", "")
        video_url = data.get("video_url", "")

        if not course or not title:
            raise ValueError("Course and title are required to create a lesson.")

        return Lesson.objects.create(course=course, title=title, content=content, video_url=video_url)

    def get_lessons_by_course(self, course):
        """
        Get all lessons for a specific course.
        """
        return Lesson.objects.filter(course=course)

    def verify_lesson_has_progress(self, lesson):
        """
        Verify if a lesson has progress associated with it.
        """
        if lesson.progress.exists():
            raise LessonException(code="HAS_PROGRESS")

    def verify_to_complete_lesson(self, user, lesson):
        """
        Verify if a student can complete a lesson.
        """
        if not Enrollment.objects.filter(course=lesson.course, student=user).exists():
            raise LessonException(code="NOT_ENROLLED")
        if lesson.progress.filter(user=user, status=DailyProcessStatus.COMPLETED.value).exists():
            raise LessonException(code="ALREADY_COMPLETED")

    def complete_lesson(self, user, lesson):
        """
        Mark a lesson as completed for a student.
        """
        self.verify_to_complete_lesson(user, lesson)

        progress, _ = lesson.progress.get_or_create(
            user=user, status=DailyProcessStatus.IN_PROGRESS.value, date=date.today()
        )

        return progress


class DailyProcessService:
    """
    Service class for handling daily processes related to lessons.
    """

    def daily_process_lessons(self, user, query_date):
        """
        Process all completed lessons for the day.
        """
        progress = (
            LessonProgress.objects.filter(user=user, date=query_date)
            .values("lesson__course__title")
            .annotate(
                completed=Count("id", filter=Q(status=DailyProcessStatus.COMPLETED.value)),
                in_progress=Count("id", filter=Q(status=DailyProcessStatus.IN_PROGRESS.value)),
            )
        )

        return [
            {
                "course_title": p.get("lesson__course__title"),
                "completed": p.get("completed"),
                "in_progress": p.get("in_progress"),
            }
            for p in progress
        ]
