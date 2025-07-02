"""
Lesson model for the courses app.
"""

from django.db import models

from core.constants import DailyProcessStatus
from core.models import AbstractTimeStampedModel, AbstractUUIDModel
from courses.models import Course
from users.models import User


# --- Lesson ---
class Lesson(AbstractTimeStampedModel, AbstractUUIDModel):
    """
    Lesson model to represent a lesson in a course.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="lessons")
    title = models.CharField(max_length=255)
    content = models.TextField(blank=True, null=True)
    video_url = models.URLField(blank=True, null=True)
    duration_minutes = models.PositiveIntegerField(blank=True, null=True)

    def __str__(self):
        """
        String representation of the Lesson model.
        """
        return f"{self.course.title} - {self.title}"


# --- Lesson Progress ---
class LessonProgress(AbstractTimeStampedModel):
    """
    LessonProgress model to track user progress in lessons.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(
        max_length=20,
        choices=DailyProcessStatus.choices(),
        default=DailyProcessStatus.IN_PROGRESS.value,
    )
    time_spent = models.DurationField(blank=True, null=True)
    date = models.DateField()
