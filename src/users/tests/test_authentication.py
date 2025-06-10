"""
Test cases for user authentication APIs.
"""

from rest_framework_simplejwt.tokens import RefreshToken

from core.tests import BaseAPITestCase
from users.apis import AuthenticationViewSet
from users.models import User


class SignupAPITestCase(BaseAPITestCase):
    """
    Users apis test case.
    """

    resource = AuthenticationViewSet

    def setUp(self):
        """
        Set up the test case.
        """
        super().setUp()

        self.fragment = "signup"
        self.auth = None

    def test_signup_success(self):
        """
        Test user signup success.
        """
        payload = {"email": "testuser@example.com", "password": "Abcd@1234"}

        response = self.post_json_ok(fragment=self.fragment, data=payload)
        assert response.status_code == 201
        assert response.data["email"] == payload["email"]
        assert User.objects.filter(email=payload["email"]).exists()

    def test_signup_missing_password_bad_request(self):
        """
        Test user signup with missing password.
        """
        payload = {"email": "testuser@example.com"}

        response = self.post_json_bad_request(fragment=self.fragment, data=payload)
        assert response.status_code == 400

    def test_signup_invalid_email_format_bad_request(self):
        """
        Test user signup with invalid email format.
        """
        payload = {"email": "invalid_email.com", "password": "Abcd@1234"}

        response = self.post_json_bad_request(fragment=self.fragment, data=payload)
        assert response.status_code == 400

    def test_signup_email_already_exists_bad_request(self):
        """
        Test user signup with email already exists.
        """
        payload = {"email": "user@example.com", "password": "Abcd@1234"}
        User.objects.create(**payload)

        response = self.post_json_bad_request(fragment=self.fragment, data=payload)

        assert response.status_code == 400


class SigninAPITestCase(BaseAPITestCase):
    """
    Login (signin) API test cases.
    """

    resource = AuthenticationViewSet

    def setUp(self):
        """
        Set up a valid user for signin tests.
        """
        super().setUp()
        self.fragment = "signin"
        self.auth = None

        self.email = "testuser@example.com"
        self.password = "Abcd@1234"
        self.user = User.objects.create_user(email=self.email, password=self.password)

    def test_login_success(self):
        """
        Test user login success with correct credentials.
        """
        payload = {"email": self.email, "password": self.password}
        response = self.post_json_ok(fragment=self.fragment, data=payload)

        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_wrong_password(self):
        """
        Test login with incorrect password.
        """
        payload = {"email": self.email, "password": "WrongPassword123"}
        response = self.post_json_bad_request(fragment=self.fragment, data=payload)
        assert response.status_code == 400

    def test_login_nonexistent_user(self):
        """
        Test login with an email that does not exist.
        """
        payload = {"email": "nonexistent@example.com", "password": "Abcd@1234"}
        response = self.post_json_bad_request(fragment=self.fragment, data=payload)

        assert response.status_code == 400

    def test_login_missing_fields(self):
        """
        Test login with missing email or password.
        """
        # Missing password
        response = self.post_json_bad_request(fragment=self.fragment, data={"email": self.email})
        assert response.status_code == 400

        # Missing email
        response = self.post_json_bad_request(fragment=self.fragment, data={"password": self.password})
        assert response.status_code == 400


class LogoutAPITestCase(BaseAPITestCase):
    """
    Logout API test cases.
    """

    resource = AuthenticationViewSet

    def setUp(self):
        """
        Set up a user and generate JWT tokens for logout tests.
        """
        super().setUp()
        self.fragment = "logout"

        self.user = User.objects.create_user(
            email="logoutuser@example.com", username="logoutuser@example.com", password="Abcd@1234"
        )

        # Generate JWT tokens manually
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
        self.refresh_token = str(self.refresh)

    def test_logout_success(self):
        """
        Test that refresh token is blacklisted on logout.
        """
        response = self.post_json_ok(
            fragment=self.fragment,
            data={"refresh": self.refresh_token},
        )

        assert response.status_code == 204
