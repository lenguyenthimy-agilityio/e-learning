"""
Factories for creating course-related objects in the database.
"""

from core import factories
from core.constants import CourseStatus
from courses.models import Category, Course
from users.factories import UserFactory


class CategoryFactory(factories.ModelFactory):
    """
    Faker for Category model.
    """

    class Meta:
        """
        Class Meta for CategoryFactory.
        """

        model = Category

    name = factories.Sequence(lambda n: f"Category {n}")
    description = factories.Faker("sentence", nb_words=6)


class CourseFactory(factories.ModelFactory):
    """
    Faker for Course model.
    """

    class Meta:
        """
        Class Meta for CourseFactory.
        """

        model = Course

    title = factories.Sequence(lambda n: f"Course {n}")
    description = factories.Faker("sentence", nb_words=6)
    instructor = factories.SubFactory(UserFactory)
    category = factories.SubFactory(CategoryFactory)
    status = CourseStatus.PUBLISHED.value
