"""
Factories for Certificate model.
"""

from certificates.models import Certificate
from core import factories
from courses.factories import CourseFactory
from users.factories import UserFactory


class CertificateFactory(factories.ModelFactory):
    """
    Faker for Certificate model.
    """

    class Meta:
        """
        Class Meta for CertificateFactory.
        """

        model = Certificate

    student = factories.SubFactory(UserFactory)
    course = factories.SubFactory(CourseFactory)
    issued_at = factories.Faker("date_time_this_year")
