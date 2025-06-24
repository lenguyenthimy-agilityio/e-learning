"""
Class factories for creating class instances in tests.
"""

from core import factories
from courses.factories import CourseFactory


class LiveClassFactory(factories.ModelFactory):
    """
    Faker for LiveClass model.
    """

    class Meta:
        """
        Class Meta for LiveClassFactory.
        """

        model = "classes.LiveClass"

    title = factories.Faker("sentence", nb_words=4)
    date_time = factories.Faker("future_datetime", end_date="+30d")
    meeting_url = factories.Faker("url")
    course = factories.SubFactory(CourseFactory)
