"""
User model.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from core.constants import UserRole
from core.models import AbstractTimeStampedModel, AbstractUUIDModel


class User(PermissionsMixin, AbstractBaseUser, AbstractUUIDModel, AbstractTimeStampedModel):
    """
    User model.
    """

    username = models.CharField(max_length=150, unique=True, verbose_name="username")
    email = models.EmailField(unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=30, blank=True, verbose_name="first name")
    last_name = models.CharField(max_length=30, blank=True, verbose_name="last name")
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices(),
        default=UserRole.STUDENT.value,
        verbose_name="role",
    )
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        """
        Meta class.
        """

        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        """
        String representation of the User model.
        """
        return f"{self.username} ({self.role})"
