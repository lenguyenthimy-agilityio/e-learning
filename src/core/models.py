"""
Base models.
"""

import uuid

from django.db import models


class AbstractUUIDModel(models.Model):
    """
    UUID Model Mixin, use uuid instead of id as primary key.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        """
        Meta class.
        """

        abstract = True


class AbstractTimeStampedModel(models.Model):
    """
    TimeStamped Model.
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created_at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated_at")

    class Meta:
        """
        Meta class.
        """

        abstract = True
