"""
Serializers for the User model.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from core.serializers import BaseSerializer
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


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    User update serializer.
    """

    class Meta:
        """
        Class Meta for UserUpdateSerializer.
        """

        model = User
        fields = ["first_name", "last_name", "email"]
        extra_kwargs = {
            "email": {"required": False},
        }


class SignupSerializer(serializers.ModelSerializer):
    """
    Sign up serializer.
    """

    class Meta:
        """
        Class Meta.
        """

        model = User
        fields = ("email", "password", "role", "first_name", "last_name")
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


class CustomTokenObtainPairSerializer(BaseSerializer, TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens.
    """

    def validate(self, attrs):
        """
        Validate the input attributes for login.
        """
        try:
            return super().validate(attrs)
        except serializers.ValidationError as e:
            raise e  # forward validation errors
        except Exception:
            # Convert AuthenticationFailed (401) into ValidationError (400)
            raise serializers.ValidationError({"message": "Invalid email or password"})


class LoginSerializer(BaseSerializer):
    """
    Login serializer for user authentication.
    """

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class LogoutRequestSerializer(BaseSerializer):
    """
    Serializer for logout request.
    """

    refresh = serializers.CharField(
        help_text="Refresh token to be blacklisted.",
        required=True,
        write_only=True,
    )
