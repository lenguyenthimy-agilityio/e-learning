"""
Permissions for the courses app.
"""

from rest_framework.permissions import BasePermission


class IsInstructor(BasePermission):
    """
    Permission to allow only instructors to access certain views.
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and has the role of 'instructor'.
        """
        return request.user.is_authenticated and request.user.role == "Instructor"


class IsCourseOwner(BasePermission):
    """
    Permission to allow only the owner of a course to access it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the instructor of the course.
        """
        return obj.instructor == request.user
