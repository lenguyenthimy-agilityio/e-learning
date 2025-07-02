"""
Factories for creating course-related objects in the database.
"""

from core import factories
from core.constants import CourseStatus
from courses.models import Category, Course, Enrollment
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


class EnrollmentFactory(factories.ModelFactory):
    """
    Faker for Enrollment model.
    """

    class Meta:
        """
        Class Meta for EnrollmentFactory.
        """

        model = Enrollment

    student = factories.SubFactory(UserFactory)
    course = factories.SubFactory(CourseFactory)
    completed = factories.Faker("boolean", chance_of_getting_true=50)


class LessonFactory(factories.ModelFactory):
    """
    Faker for Lesson model.
    """

    class Meta:
        """
        Class Meta for LessonFactory.
        """

        model = "lessons.Lesson"

    title = factories.Sequence(lambda n: f"Lesson {n}")
    content = factories.Faker("paragraph")
    video_url = factories.Faker("url")
    course = factories.SubFactory(CourseFactory)
