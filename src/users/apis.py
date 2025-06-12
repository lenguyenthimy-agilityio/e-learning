"""
Users Views.
"""

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from core.apis import BaseAPIViewSet
from core.exception import TokenException, UserException
from core.schema import base_responses
from users.serializers import (
    AvatarUploadSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer,
    LogoutRequestSerializer,
    SignupSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class UserViewSet(BaseAPIViewSet):
    """
    User viewset for handling user-related operations.
    """

    resource_name = "users"
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Get the authenticated user object.
        """
        if self.kwargs.get("pk") == "me":
            return self.request.user

        return super().get_object()

    @extend_schema(responses={**base_responses, 200: UserSerializer})
    def retrieve(self, request: Request, **kwargs) -> Response:
        """
        Retrieve the authenticated user's details.
        """
        user = self.get_object()
        if not user:
            raise UserException(code="NOT_FOUND")

        serializer = UserSerializer(user)
        return self.response_ok(data=serializer.data)

    @extend_schema(request=UserUpdateSerializer, responses={**base_responses, 200: UserSerializer})
    def partial_update(self, request: Request, **kwargs) -> Response:
        """
        Update the authenticated user's details.
        """
        user = self.get_object()
        if not user:
            raise UserException(code="NOT_FOUND")

        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.response_ok(data=serializer.data)

    @extend_schema(request=AvatarUploadSerializer, responses={**base_responses, 200: UserSerializer})
    @action(detail=True, methods=["post"], url_path="upload-avatar")
    def upload_avatar(self, request: Request, *args, **kwargs) -> Response:
        """
        Upload user avatar.
        """
        user = self.get_object()
        if not user:
            raise UserException(code="NOT_FOUND")

        serializer = AvatarUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user.avatar = serializer.validated_data["avatar"]
        user.save()
        return self.response_data_success()


class AuthenticationViewSet(BaseAPIViewSet):
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
