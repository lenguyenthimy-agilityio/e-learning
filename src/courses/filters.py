"""
Module defines filters for the Course model using Django Filters.
"""

import django_filters

from courses.models import Course


class CourseFilter(django_filters.FilterSet):
    """
    FilterSet for the Course model.
    """

    title = django_filters.CharFilter(lookup_expr="icontains")
    category = django_filters.CharFilter(field_name="category__name", lookup_expr="icontains")
    status = django_filters.CharFilter(method="filter_status")

    def filter_status(self, queryset, name, value):
        """
        Custom filter method for status field.
        """
        return queryset.filter(status__iexact=value)

    class Meta:
        """
        Meta class for CourseFilter.
        """

        model = Course
        fields = ["title", "category"]
