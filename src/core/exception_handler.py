"""
Exception handler.
"""

from rest_framework.response import Response
from rest_framework.views import exception_handler


def is_registered(exception) -> bool:
    """
    Check if exception is registered.

    Returns:
        bool: True if the exception is registered, False otherwise.
    """
    try:
        return exception.is_an_error_response
    except AttributeError:
        return False


def process_exception(exception, context) -> Response:
    """
    Process the exception.

    Args:
        exception (Exception): The exception
        context (dict): the context

    Returns:
        Response: Response
    """
    response = exception_handler(exception, context)

    if is_registered(exception):
        # Handle the case where the response is None
        return Response(
            data={
                "errors": {
                    "developer_message": exception.developer_message,
                    "message": exception.user_message,
                    "code": f"ERR_{exception.app_name}_{exception.code}" if exception.code else exception.app_name,
                }
            },
            status=exception.status_code,
        )
    # Update the structure of the response data.
    if response is not None:
        customized_response = {"errors": []}

        for key, value in response.data.items():
            error = {"field": key, "message": value}
            customized_response["errors"].append(error)

        response.data = customized_response

    return response
