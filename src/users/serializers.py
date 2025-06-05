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
        fields = ["id", "username", "email", "first_name", "last_name", "created_at"]


class SignupSerializer(serializers.ModelSerializer):
    """
    Sign up serializer.
    """

    password = serializers.CharField(write_only=True)

    class Meta:
        """
        Class Meta.
        """

        model = User
        fields = ("username", "email", "password")

    def create(self, validated_data):
        """
        Create user.
        """
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"],
        )
        return user
