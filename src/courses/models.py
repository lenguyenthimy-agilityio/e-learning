"""Models for the courses app."""

from django.db import models

from core.constants import CourseStatus
from core.models import AbstractTimeStampedModel, AbstractUUIDModel
from users.models import User


# --- Category ---
class Category(AbstractTimeStampedModel, AbstractUUIDModel):
    """
    Category model to categorize courses.
    """

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        """
        String representation of the Category model.
        """
        return str(self.name)


# --- Course ---
class Course(AbstractTimeStampedModel):
    """
    Course model to represent a course in the system.
    """

    title = models.CharField(max_length=255)
    description = models.TextField()
    instructor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="courses")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20,
        choices=CourseStatus.choices(),
        default=CourseStatus.UNPUBLISHED.value,
    )

    def __str__(self):
        """
        String representation of the Course model.
        """
        return str(self.title)


# --- Enrollment ---
class Enrollment(AbstractTimeStampedModel, AbstractUUIDModel):
    """
    Enrollment model.
    """

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        """
        Class Meta.
        """

        unique_together = ("student", "course")

    def __str__(self):
        """
        String representation of the Enrollment model.
        """
        return f"{self.student.username} enrolled in {self.course.title}"
