"""
Test users views.
"""

from core.tests import BaseAPITestCase
from users.apis import UserViewSet


class UsersAPITestCase(BaseAPITestCase):
    """
    Users apis test case.
    """

    resource = UserViewSet

    def test_assert_ok(self):
        """
        Test setting up the test case.
        """
        self.assertEqual(True, True)
