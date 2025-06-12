"""
Test users views.
"""

from django.core.files.uploadedfile import SimpleUploadedFile

from core.tests import BaseAPITestCase
from users.apis import UserViewSet

MINIMAL_JPEG = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    b"\xff\xdb\x00C\x00" + b"\x08" * 64 + b'\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x03\x01"\x00\x02\x11\x01\x03\x11\x01'
    b"\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xd2\xcf \xff\xd9"
)


class UserAPITestCase(BaseAPITestCase):
    """
    User API test cases.
    """

    resource = UserViewSet

    def setUp(self):
        """
        Set up an authenticated user for testing.
        """
        super().setUp()
        self.fragment = "me"

    def test_get_user_info_success(self):
        """
        Test retrieving authenticated user's info.
        """
        response = self.get_json_ok(fragment=self.fragment)
        assert response.status_code == 200
        assert response.data["email"] == self.authenticated_user.email

    def test_update_user_info_success(self):
        """
        Test updating user profile fields.
        """
        payload = {
            "first_name": "John",
            "last_name": "Doe",
        }

        response = self.patch_json_ok(fragment=self.fragment, data=payload)
        assert response.status_code == 200
        assert response.data["first_name"] == "John"
        assert response.data["last_name"] == "Doe"
        assert response.data["email"] == self.authenticated_user.email

    def test_update_user_info_validation_error(self):
        """
        Test invalid update data.
        """
        response = self.patch_json_bad_request(fragment=self.fragment, data={"email": "not-an-email"})
        assert response.status_code == 400

    def test_get_user_info_unauthenticated(self):
        """
        Test getting user info without authentication.
        """
        response = self.get_json_unauthorized(fragment=self.fragment)
        assert response.status_code == 401

    def test_upload_avatar_success(self):
        """
        Test uploading a valid avatar image.
        """
        image = SimpleUploadedFile("avatar.jpeg", MINIMAL_JPEG, content_type="image/jpeg")

        response = self.post_json_ok(data={"avatar": image}, fragment="me/upload-avatar", format_data="multipart")

        assert response.status_code == 200
        assert response.data["success"] is True

    def test_upload_avatar_missing_file(self):
        """
        Test uploading avatar without providing a file.
        """
        response = self.post_json_ok(data={}, fragment="me/upload-avatar", format_data="multipart")
        assert response.status_code == 400

    def test_upload_avatar_invalid_file_type(self):
        """
        Test uploading a non-image file.
        """
        file = SimpleUploadedFile("document.txt", b"this is not an image", content_type="text/plain")

        response = self.post_json_ok(data={"avatar": file}, fragment="me/upload-avatar", format_data="multipart")
        assert response.status_code == 400

    def test_upload_avatar_too_large(self):
        """
        Test uploading a file that's too large.
        """
        # Create 2.5 MB fake JPEG file (just repeating valid header + padding)
        large_content = MINIMAL_JPEG + b"\x00" * (2_500_000 - len(MINIMAL_JPEG))
        big_file = SimpleUploadedFile("avatar.jpeg", large_content, content_type="image/jpeg")

        response = self.post_json_ok(data={"avatar": big_file}, fragment="me/upload-avatar", format_data="multipart")

        assert response.status_code == 400
        assert response.json()["errors"][0]["message"][0] == "File is too large."
