"""
Base serializer.
"""

from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    """
    Base serializer class for handling request and response data.
    """

    def update(self, instance, validated_data):
        """
        Will be overridden in the inherited class if needed.

        Args:
            instance (class): The class instance
            validated_data (dict): Validated data
        """

    def create(self, validated_data):
        """
        Will be overridden in the inherited class if needed.

        Args:
            validated_data (dict): Validated data
        """


class DataSuccessSerializer(BaseSerializer):
    """
    Success data.
    """

    success = serializers.BooleanField(default=True)


class ErrorSerializer(BaseSerializer):
    """
    Error serializer.
    """

    field = serializers.CharField(help_text="The error field.")
    message = serializers.CharField(help_text="Default error message.")


class BadRequestSerializer(BaseSerializer):
    """
    Error data.
    """

    developer_message = serializers.CharField(help_text="Developer message.")
    message = serializers.CharField(help_text="User friendly message.")
    code = serializers.CharField(help_text="Custom error code. Example Code_001.")


class BaseSuccessResponseSerializer(BaseSerializer):
    """
    Base serializer for data success.
    """

    data = DataSuccessSerializer()


class BaseBadRequestResponseSerializer(BaseSerializer):
    """
    Base serializer for bad request.
    """

    errors = BadRequestSerializer()


class BaseUnauthorizedResponseSerializer(BaseSerializer):
    """
    Base serializer for unauthorized response.
    """

    errors = ErrorSerializer(many=True)


class BaseForbiddenResponseSerializer(BaseSerializer):
    """
    Base serializer for forbidden response.
    """

    errors = ErrorSerializer(many=True)
