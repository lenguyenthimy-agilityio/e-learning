"""
User model.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

from core.constants import UserRole
from core.models import AbstractTimeStampedModel, AbstractUUIDModel


class UserManager(BaseUserManager):
    """
    User manager for creating and managing user accounts.

    This manager provides methods to create users
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a user with an email and password.

        Args:
            email (Email): Email address of the user.
            password (string): Password for the user.
            extra_fields (dict): Additional fields for the user.

        """
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, AbstractUUIDModel, AbstractTimeStampedModel):
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
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    objects = UserManager()

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
        return f"{self.email} ({self.role})"
