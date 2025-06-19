"""
Lesson factories for creating lesson instances in tests.
"""

from core import factories
from courses.factories import CourseFactory


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


class LessonProgressFactory(factories.ModelFactory):
    """
    Faker for LessonProgress model.
    """

    class Meta:
        """
        Class Meta for LessonProgressFactory.
        """

        model = "lessons.LessonProgress"

    user = factories.SubFactory("users.factories.UserFactory")
    lesson = factories.SubFactory(LessonFactory)
    completed = factories.Faker("boolean")
    time_spent = factories.Faker("time_delta")
    date = factories.Faker("date")
