"""
LiveClass model for managing live class sessions in a course management system.
"""

from django.db import models

from core.models import AbstractTimeStampedModel, AbstractUUIDModel
from courses.models import Course
from users.models import User


class LiveClass(AbstractTimeStampedModel, AbstractUUIDModel):
    """
    Model representing a live class session.
    """

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="class_sessions")
    title = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    meeting_url = models.URLField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_sessions")
    is_canceled = models.BooleanField(default=False)
