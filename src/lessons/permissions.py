"""
Permission to only allow instructors to access the course.
"""

from rest_framework.permissions import BasePermission

from courses.models import Course


class IsOwnerLesson(BasePermission):
    """
    Permission to only allow instructors to access the course.
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
