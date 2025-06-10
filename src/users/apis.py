"""
Users Views.
"""

from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.apis import BaseAPIViewSet
from core.exception import TokenException
from core.schema import base_responses
from users.models import User
from users.serializers import (
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    LogoutRequestSerializer,
    SignupSerializer,
    UserSerializer,
)


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


class AuthenticationViewSet(viewsets.ViewSet, BaseAPIViewSet):
    """
    Authentication viewset for handling user authentication.
    """

    resource_name = "auth"

    @extend_schema(
        request=SignupSerializer,
        responses={**base_responses, 201: UserSerializer},
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def signup(self, request: Request, *args, **kwargs) -> Response:
        """
        Sign up a new user.
        """
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return self.response_created(data=serializer.data)

    @extend_schema(
        request=LoginSerializer,
        responses={**base_responses, 200: CustomTokenObtainPairSerializer},
    )
    @action(detail=False, methods=["post"], url_path="signin", permission_classes=[AllowAny])
    def signin(self, request: Request, *args, **kwargs) -> Response:
        """
        Login a user and return access and refresh tokens.
        """
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self.response_ok(data=serializer.validated_data)

    @extend_schema(request=LogoutRequestSerializer, responses={**base_responses, 204: None})
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request: Request, *args, **kwargs) -> Response:
        """
        Logout a user by blacklisting the refresh token.
        """
        try:
            refresh_token = request.data.get("refresh")
            token = RefreshToken(refresh_token)
            token.blacklist()
            return self.response_deleted()
        except Exception as exc:
            raise TokenException(code="INVALID", developer_message=str(exc)) from exc


apps = [UserViewSet, AuthenticationViewSet]
