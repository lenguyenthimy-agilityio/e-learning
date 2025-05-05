"""
Base API ViewSet.
"""

from rest_framework import status, viewsets
from rest_framework.response import Response


class BaseAPIViewSet(viewsets.GenericViewSet):
    """
    Base API ViewSet class that provides common functionality for all API ViewSets.
    """

    resource_name = ""

    def get_queryset(self):
        """
        Returns the queryset for the viewset.
        """
        return self.queryset

    def get_serializer_class(self):
        """
        Returns the serializer class for the viewset.
        """
        return self.serializer_class

    def response_ok(self, data: dict = None) -> Response:
        """
        Return default response ok. Status code is 200.
        """
        return Response(data=data, status=status.HTTP_200_OK)

    def response_created(self, data: dict = None) -> Response:
        """
        Return default response created. Status code is 201.
        """
        return Response(data=data, status=status.HTTP_201_CREATED)

    def response_data_success(self) -> Response:
        """
        Return default response data success object. Status code is 200.
        """
        data = {"data": {"success": True}}
        return self.response_ok(data)

    def response_deleted(self) -> Response:
        """
        Return default response deleted. Status code is 204.
        """
        return Response(status=status.HTTP_204_NO_CONTENT)
