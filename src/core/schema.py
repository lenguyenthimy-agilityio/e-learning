"""
Copyright © 2022-present Agility IO, LLC. All rights reserved.

The contents of this file are subject to the terms of the End User License
Agreement (EULA) and Enterprise Services Agreement (ESA) agreed upon between
You and Agility IO, LLC, collectively (“License”).
You may not use this file except in compliance with the License. You can obtain
a copy of the License by contacting Agility IO, LLC.
See the License for the specific language governing permissions and limitations
under the License including but not limited to modification and distribution
rights of the Software.
"""

from typing import List, Type

from drf_spectacular.utils import OpenApiParameter
from rest_framework import serializers

from core.serializers import (
    BaseBadRequestResponseSerializer,
    BaseForbiddenResponseSerializer,
    BaseSuccessResponseSerializer,
    BaseUnauthorizedResponseSerializer,
)

base_responses = {
    200: BaseSuccessResponseSerializer,
    400: BaseBadRequestResponseSerializer,
    401: BaseUnauthorizedResponseSerializer,
    403: BaseForbiddenResponseSerializer,
}


def build_query_parameters(serializer_class: Type[serializers.Serializer]) -> List[OpenApiParameter]:
    """
    Build a list of OpenApiParameter objects from a DRF Serializer.

    This function maps serializer fields to OpenAPI query parameters,
    preserving details such as field name, type, description, and constraints.

    Args:
        serializer_class (Type[serializers.Serializer]):
            A DRF serializer class whose fields will be converted into OpenAPI parameters.

    Returns:
        List[OpenApiParameter]:
            A list of OpenApiParameter objects representing the serializer fields as query parameters.

    Example:
        class ExampleSerializer(serializers.Serializer):
            query = serializers.CharField(required=False, help_text="Search query")
            is_active = serializers.BooleanField(required=False, help_text="Active status")

        parameters = build_query_parameters(ExampleSerializer)
    """
    parameters: List[OpenApiParameter] = []
    for field_name, field in serializer_class().fields.items():
        param_location = OpenApiParameter.QUERY  # Default location for parameters

        param = OpenApiParameter(
            name=field_name,
            description=field.help_text or "",
            required=field.required,
            type=field.__class__.__name__,
            location=param_location,
        )

        # Handle specific field types for precise typing
        match field:
            case serializers.ChoiceField():
                param.enum = list(field.choices.keys())
            case serializers.BooleanField():
                param.type = bool
            case serializers.IntegerField():
                param.type = int
            case serializers.FloatField():
                param.type = float
            case serializers.CharField():
                param.type = str

        parameters.append(param)

    return parameters
