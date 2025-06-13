"""
Pagination param serializer mixin.
"""

from rest_framework import serializers
from rest_framework.serializers import ValidationError

from core.constants import PAGINATION_LIMIT_DEFAULT
from core.exception import BaseErrorMessage
from core.serializers import BaseSerializer


class PaginationParamSerializerMixin(BaseSerializer):
    """
    Pagination parameter serializer.
    """

    limit = serializers.IntegerField(
        required=False, help_text="Limit the number of resources to be returned.", default=PAGINATION_LIMIT_DEFAULT
    )
    offset = serializers.IntegerField(required=False, help_text="Number of resources to skip.", default=0)

    def validate(self, attrs):
        """
        Validate the limit and offset.
        """
        if "offset" in attrs and int(attrs.get("offset")) < 0:
            raise ValidationError({"offset": BaseErrorMessage.INVALID_OFFSET})

        if "limit" in attrs and int(attrs.get("limit")) < 1:
            raise ValidationError({"limit": BaseErrorMessage.INVALID_LIMIT})

        return attrs
