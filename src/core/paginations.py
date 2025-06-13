"""Custom pagination class for the API."""

from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.LimitOffsetPagination):
    """
    Base class for pagination.
    """

    default_limit = 20
    limit_query_param = "limit"
    offset_query_param = "offset"
    template = "rest_framework/pagination/numbers.html"

    def get_paginated_response(self, data):
        """
        Customize paginated response.
        """
        return Response(
            {
                "data": data,
                "pagination": {
                    "limit": self.limit,
                    "offset": self.offset,
                    "total": self.count,
                },
            }
        )
