"""
Exception classes for the application.
"""

from rest_framework import status


class BaseErrorMessage:
    """
    Error message class.
    """

    BAD_REQUEST = "Bad request."
    UNAUTHORIZED = "Unauthorized."
    FORBIDDEN = "Forbidden."
    NOT_FOUND = "Not found."
    INVALID_OFFSET = "Invalid 'offset' parameter. Please provide a positive integer."
    INVALID_LIMIT = "Invalid 'limit' parameter. Please provide a positive integer."


class SystemErrorMessage(BaseErrorMessage):
    """
    System error message class.
    """

    SYSTEM_ERROR = "System error."
    SYSTEM_UNAVAILABLE = "System unavailable."
    SYSTEM_TIMEOUT = "System timeout."
    SYSTEM_BUSY = "System busy."
    SYSTEM_MAINTENANCE = "System maintenance."


class TokenErrorMessage(BaseErrorMessage):
    """
    Token error message class.
    """

    INVALID = "Token is invalid."


class UserErrorMessage(BaseErrorMessage):
    """
    Token error message class.
    """

    NOT_FOUND = "User not found."


class FileUploadErrorMessage(BaseErrorMessage):
    """
    File upload error message class.
    """

    FILE_TOO_LARGE = "File is too large."
    UNSUPPORTED_FILE_TYPE = "Unsupported file type."
    UPLOAD_FAILED = "File upload failed."


class BaseCustomException(Exception):
    """
    The base custom exception class.
    """

    # The HTTP status code
    status_code = status.HTTP_400_BAD_REQUEST

    app_name = "APP"

    error = None

    # The custom error code
    default_code = ""

    # The developer message about the error
    default_dev_msg = None

    # The friendly user message about the error
    default_user_message = "Something went wrong. Please try again."

    # A flag to determine this error will be sent back in response data or not.
    is_an_error_response = True

    def __init__(self, code=None, user_message=None, developer_message=None):
        """
        Initialize the exception.

        Args:
            code (str, optional): Error code. Defaults to None.
            user_message (str, optional): User error message. Defaults to None.
            developer_message (str, optional): Developer error message. Defaults to None.
        """
        Exception.__init__(self)

        self.developer_message = developer_message
        self.user_message = user_message
        self.code = code if code is not None else self.default_code

        # Set default message
        default_message = self.default_dev_msg = (
            f"{self.app_name.replace('_', ' ').capitalize()} API is not working properly."
        )

        if not self.default_dev_msg:
            self.default_dev_msg = default_message

        if not self.default_user_message:
            self.default_user_message = default_message

        if not developer_message:
            self.developer_message = self.default_dev_msg

        if not user_message:
            if self.error and self.code:
                self.user_message = getattr(self.error, self.code)
            else:
                self.user_message = self.default_user_message


class SystemException(BaseCustomException):
    """
    System exception.
    """

    app_name = "SYSTEM"
    error = SystemErrorMessage
    status_code = status.HTTP_400_BAD_REQUEST
    default_dev_msg = "Something went wrong. Please try again later."
    default_user_message = "Something went wrong. Please try again later."


class TokenException(BaseCustomException):
    """
    System exception.
    """

    app_name = "TOKEN"
    error = TokenErrorMessage
    status_code = status.HTTP_400_BAD_REQUEST


class UserException(BaseCustomException):
    """
    System exception.
    """

    app_name = "USER"
    error = UserErrorMessage
    status_code = status.HTTP_400_BAD_REQUEST


class FileUploadException(BaseCustomException):
    """
    File upload exception.
    """

    app_name = "FILE_UPLOAD"
    error = BaseErrorMessage
    status_code = status.HTTP_400_BAD_REQUEST
    default_dev_msg = "File upload failed."
    default_user_message = "File upload failed. Please try again."
