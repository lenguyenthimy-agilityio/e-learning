"""
Lesson services module.
"""

from rest_framework.exceptions import PermissionDenied

from core.exception import LessonException
from courses.models import Enrollment
from lessons.models import Lesson


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

    def verify_lesson_enrolled(self, user, course):
        """
        Verify if a lesson enrolled for student access.
        """
        if user != course.instructor and not Enrollment.objects.filter(course=course, student=user).exists():
            raise PermissionDenied("You do not have access to this lesson.")

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
        if lesson.progress.filter(user=user, completed=True).exists():
            raise LessonException(code="ALREADY_COMPLETED")

    def complete_lesson(self, user, lesson):
        """
        Mark a lesson as completed for a student.
        """
        self.verify_to_complete_lesson(user, lesson)

        progress, _ = lesson.progress.get_or_create(user=user)
        progress.completed = True
        progress.save()

        return progress
