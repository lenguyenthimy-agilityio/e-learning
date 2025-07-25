"""
Core constants for the project.
"""

from enum import Enum
from typing import List, Tuple


class BaseChoiceEnum(Enum):
    """
    The base class for choices enumeration.
    """

    @classmethod
    def to_tuple(cls) -> List[Tuple]:
        """
        Parse enum to tuple.

        Returns:
            List[Tuple]:  List of tuples.
        """
        return [(data.name, data.value) for data in cls]

    @classmethod
    def values(cls) -> List[int]:
        """
        Get values of enum.

        Returns:
            List[int]: List of values.
        """
        return [data.value for data in cls]

    @classmethod
    def choices(cls) -> List[Tuple]:
        """
        Get choices of enum.

        Returns:
            List[Tuple]: List of choice.
        """
        return [(data.value, data.name) for data in cls]


class UserRole(BaseChoiceEnum):
    """
    Role choices for the user model.
    """

    INSTRUCTOR = "Instructor"
    STUDENT = "Student"


class CourseStatus(BaseChoiceEnum):
    """
    Status choices for the course model.
    """

    PUBLISHED = "Published"
    UNPUBLISHED = "Unpublished"


class DailyProcessStatus(BaseChoiceEnum):
    """
    Status choices for daily process.
    """

    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB
PAGINATION_LIMIT_DEFAULT = 100
