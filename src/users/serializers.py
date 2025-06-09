"""
Serializers for the User model.
"""

from rest_framework import serializers

from users.models import User


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

    class Meta:
        """
        Class Meta.
        """

        model = User
        fields = ("email", "password", "role", "first_name", "last_name", "username")
        extra_kwargs = {"password": {"write_only": True}}

    def validate_email(self, value):
        """
        Validate the email field.

        Args:
            value (string): The email value to validate.

        """
        if "@" not in value:
            raise serializers.ValidationError("Enter a valid email address")
        return value

    def validate_password(self, value):
        """
        Validate the password field.

        Args:
            value (string): The password value to validate.

        """
        if not value or len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters")

        return value

    def create(self, validated_data):
        """
        Create User instance from validated data.

        Args:
            validated_data (dict): User data

        """
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """
    Login serializer for user authentication.
    """

    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutRequestSerializer(serializers.Serializer):
    """
    Serializer for logout request.
    """

    refresh = serializers.CharField(
        help_text="Refresh token to be blacklisted.",
        required=True,
        write_only=True,
    )
