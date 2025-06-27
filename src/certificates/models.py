"""Certificate model for managing student course completion certificates."""

from django.db import models

from core.models import AbstractTimeStampedModel, AbstractUUIDModel
from courses.models import Course
from users.models import User


class Certificate(AbstractTimeStampedModel, AbstractUUIDModel):
    """
    Certificate model to represent a student's course completion certificate.
    """

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="certificates")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="certificates")
    issued_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """
        Meta options for the Certificate model.
        """

        unique_together = ("student", "course")
