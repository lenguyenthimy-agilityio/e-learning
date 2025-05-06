"""
Serializers for the User model.
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer.
    """

    class Meta:
        """
        Meta class for UserSerializer.
        """

        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "is_active", "date_joined"]
