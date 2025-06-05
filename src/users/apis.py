"""
Users Views.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from core.apis import BaseAPIViewSet
from core.schema import base_responses
from users.models import User
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet, BaseAPIViewSet):
    """
    User viewset for handling user-related operations.
    """

    resource_name = "users"
    queryset = User.objects.all().order_by("-created_at")
    serializer_class = UserSerializer
    permission_classes = []

    @extend_schema(
        responses={
            **base_responses,
            200: UserSerializer,
        },
    )
    def list(self, request: Request, *args, **kwargs) -> Response:
        """
        Get list of users in an application.
        """
        return super().list(request, *args, **kwargs)


apps = [UserViewSet]
