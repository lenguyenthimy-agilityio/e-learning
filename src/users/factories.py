"""
Users factories.
"""

from uuid import uuid4

from django.contrib.auth.hashers import make_password

from core import factories
from users.models import User

test_password = make_password("test_password")


class UserFactory(factories.ModelFactory):
    """
    Faker for User model.

    See https://docs.djangoproject.com/en/dev/ref/contrib/auth/#user
    for details.
    """

    password = test_password
    username = factories.LazyFunction(lambda: str(uuid4()))
    first_name = factories.Faker("first_name")
    last_name = factories.Faker("last_name")
    email = factories.Sequence(lambda n: f"email_{n}@example.com")

    class Meta:
        """
        Meta class.
        """

        model = User
        django_get_or_create = ("username",)
