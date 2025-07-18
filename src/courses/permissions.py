"""
Permissions for the courses app.
"""

from rest_framework.permissions import BasePermission

from core.constants import UserRole
from courses.models import Course


class IsInstructor(BasePermission):
    """
    Permission to allow only instructors to access certain views.
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and has the role of 'instructor'.
        """
        return request.user.is_authenticated and request.user.role == UserRole.INSTRUCTOR.value


class IsStudent(BasePermission):
    """
    Allows access only to users with the 'student' role.
    """

    def has_permission(self, request, view):
        """
        Check permission for student.
        """
        return request.user.is_authenticated and request.user.role == UserRole.STUDENT.value


class IsCourseOwner(BasePermission):
    """
    Permission to allow only the owner of a course to access it.
    """

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the instructor of the course.
        """
        return obj.instructor == request.user


class IsEntityCourseOwner(BasePermission):
    """
    Permission to allow only the owner of a course to access the lesson, quizz.
    """

    def has_permission(self, request, view):
        """
        Check if the user is authenticated and is the instructor of the course.
        """
        if view.action == "create":
            course_id = request.data.get("course_id")
            if not course_id:
                return False

            course = Course.objects.get(id=course_id)

            return course.instructor == request.user

        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Check if the user is the instructor of the course.
        """
        return obj.course.instructor == request.user
