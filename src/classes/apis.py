"""
Classes apis.
"""

from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from classes.models import LiveClass
from classes.serializers import LiveClassRequestSerializer, LiveClassSerializer
from classes.services import LiveClassService
from classes.tasks import send_class_reminder_email
from core.apis import BaseAPIViewSet
from core.schema import base_responses
from courses.permissions import IsEntityCourseOwner


class LiveClassViewSet(BaseAPIViewSet):
    """
    ViewSet to manage live (upcoming) classes.
    """

    queryset = LiveClass.objects.all()
    serializer_class = LiveClassSerializer
    permission_classes = [IsAuthenticated]
    resource_name = "classes"

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the LiveClassViewSet.
        """
        super().__init__(**kwargs)
        self.live_class_service = LiveClassService()

    def get_permissions(self):
        """
        Apply custom permissions based on the action being performed.
        """
        if self.action in ["create"]:
            return [IsEntityCourseOwner()]
        return super().get_permissions()

    @extend_schema(request=LiveClassRequestSerializer, responses={**base_responses, 201: LiveClassSerializer})
    def create(self, request: Request, *args, **kwargs) -> Response:
        """
        Schedule a new upcoming class.
        """
        serializer = LiveClassRequestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return self.response_created(data=LiveClassSerializer(instance).data)

    @extend_schema(responses={200: LiveClassSerializer(many=True)})
    @action(detail=False, methods=["get"], url_path="upcoming")
    def upcoming(self, request: Request, *args, **kwargs) -> Response:
        """
        View upcoming classes for the authenticated student.
        """
        user = request.user

        queryset = self.live_class_service.get_upcoming_classes(user)

        return self.response_ok(data=LiveClassSerializer(queryset, many=True).data)

    @action(detail=True, methods=["post"], url_path="send-reminder", permission_classes=[IsEntityCourseOwner])
    def send_reminder(self, request: Request, *args, **kwargs) -> Response:
        """
        Send reminder emails for the live class.
        """
        live_class = self.get_object()

        self.live_class_service.verify_send_reminder(live_class)

        send_class_reminder_email.delay_on_commit(live_class.id)  # Celery task

        return self.response_ok(data={"message": "Reminder emails have been queued."})


apps = [LiveClassViewSet]
