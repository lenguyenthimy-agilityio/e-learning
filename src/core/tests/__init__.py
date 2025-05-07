"""
Copyright © 2022-present Agility IO, LLC. All rights reserved.

The contents of this file are subject to the terms of the End User License
Agreement (EULA) and Enterprise Services Agreement (ESA) agreed upon between
You and Agility IO, LLC, collectively (“License”).
You may not use this file except in compliance with the License. You can obtain
a copy of the License by contacting Agility IO, LLC.
See the License for the specific language governing permissions and limitations
under the License including but not limited to modification and distribution
rights of the Software.
"""

import logging
import uuid

import jwt
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from requests import Response
from rest_framework.test import APIClient, APITestCase

from users.factories import UserFactory

logger = logging.getLogger("test")


class BaseAPITestCase(APITestCase):
    """
    The base for test class.
    """

    resource = None
    authenticated_user: User = None
    app_client_id: str = None

    uri: str = ""
    auth: str = "token"
    api_client = APIClient()
    jwt_payload = None

    @classmethod
    def setUpClass(cls):
        """
        Set up the test environment for the test class before all tests run.

        This method is called once for the entire test class.
        """
        super().setUpClass()

        # get resource URI
        cls_resource = cls.resource()
        uri = cls_resource.get_resource_uri()
        # if resource name is empty, the resource URI should be fixed by
        # removing the last splash character
        resource_name = cls_resource.resource_name
        if resource_name is None or resource_name == "":
            uri = uri[:-1]

        cls.uri: str = uri

    @classmethod
    def tearDownClass(cls):
        """
        Clean up the test environment for the test class after all tests run.

        This method is called once for the entire test class.
        """
        super().tearDownClass()

    def setUp(self):
        """
        Set up the test environment for a test case before a test run.
        """

    def tearDown(self):
        """
        Clean up the test environment for a test case after a test run.
        """

    def set_authentication(self, user: User):
        """
        Log in the user using the test client.
        """
        self.authenticated_user = user

        self.jwt_payload = {
            "email": user.email,
            "password": user.password,
        }

    def make_user(
        self,
        username="user",
        first_name=None,
        last_name=None,
        email=None,
        password="123456",
        is_staff=False,
        is_superuser=False,
    ):
        """
        Create a user for testing.
        """
        assert username
        assert password
        user = UserFactory(
            username=username,
            first_name=first_name or username,
            last_name=last_name or username,
            email=email or f"{username}@domain.com",
            is_staff=is_staff,
            is_superuser=is_superuser,
            password=make_password(password),
        )

        return user

    def assertHttpOk(self, resp):
        """
        Test the response status code is 200.
        """
        self.assertEqual(resp.status_code, 200)

    def assertHttpCreated(self, resp):
        """
        Test the response status code is 201.
        """
        self.assertEqual(resp.status_code, 201)

    def assertHttpNoContent(self, resp):
        """
        Test the response status code is 204.
        """
        self.assertEqual(resp.status_code, 204)

    def assertHttpBadRequest(self, resp):
        """
        Test the response status code is 400.
        """
        self.assertEqual(resp.status_code, 400)

    def assertHttpUnauthorized(self, resp):
        """
        Test the response status code is 401.
        """
        self.assertEqual(resp.status_code, 401)

    def assertHttpForbidden(self, resp):
        """
        Test the response status code is 403.
        """
        self.assertEqual(resp.status_code, 403)

    def assertHttpTooManyRequests(self, resp):
        """
        Test the response status code is 429.
        """
        self.assertEqual(resp.status_code, 429)

    def assertHttpNotFound(self, resp):
        """
        Test the response status code is 404.
        """
        self.assertEqual(resp.status_code, 404)

    def assertHttpNotAllowed(self, resp):
        """
        Test the response status code is 405.
        """
        self.assertEqual(resp.status_code, 405)

    def assertHasCustomErrorMessages(self, response: Response) -> None:
        """
        Test custom error to make sure the error response has right data format.

        The right data format should be:
        {
            "errors": {
                "developer_message": "The developer message",
                "message": "The message",
                "code": "The_code"
            }
        }
        """
        error_data = response.data.get("errors", {})
        required_fields = ["developer_message", "message", "code"]

        for field in required_fields:
            self.assertTrue(field in error_data.keys())

    def assertDataSuccess(self, data: dict):
        """
        Check the data has the success object.

        The right data format should be:
        {
            "data": {
                "success": True
            }
        }
        """
        self.assertTrue(data.get("data", {}).get("success", ""))

    # GET JSON
    # ---------------------------------------#

    def get_credentials(self) -> str:
        """
        Create a token.
        """
        self.assertIsNotNone(
            self.jwt_payload,
            "Expected an JSON object. You should set authentication first",
        )

        token = jwt.encode(self.jwt_payload, "secret", algorithm=settings.JWT_SIGNING_ALGORITHM)

        return f"Bearer {token}"

    def build_api_url(self, fragment: str = None) -> str:
        """
        Build the API URL.
        """
        uri = self.uri

        if fragment:
            uri = f"{uri}{fragment}"

        if not uri.endswith("/") and "?" not in uri:
            uri = f"{uri}/"

        return uri

    def get_json(self, fragment=None, data_format="json", **params):
        """
        Send a GET request to the API and return the response.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data_format (str, optional): The format of the data to be sent with the request.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        url = self.build_api_url(fragment)
        logger.debug("GET %s", url)

        headers = {}
        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = self.get_credentials()
        elif self.auth == "invalid_token":
            invalid_token = str(uuid.uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Bearer {invalid_token}"

        self.api_client.credentials(**headers)

        # Simplify the GET call (headers are now set via credentials)
        return self.api_client.get(url, format=data_format) if data_format else self.api_client.get(url)

    def get_json_ok(self, fragment="", **params):
        """
        Assert that the response is 200 OK when sending a GET request to the API.

        This is a convenience method for the common case of asserting that a GET request.
        This method is used when the user is authenticated but does not have the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.get_json(fragment, **params)
        self.assertHttpOk(resp)
        return resp

    def get_json_unauthorized(self, fragment="", **params):
        """
        Assert that the response is a 401 Unauthorized when sending a GET request to the API.

        This is a convenience method for the common case of asserting that a GET request.
        This method is used when the user is not authenticated.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        self.auth = "invalid_token"
        resp = self.get_json(fragment, **params)
        self.assertHttpUnauthorized(resp)
        return resp

    def get_json_forbidden(self, fragment="", **params):
        """
        Assert that the response is a 403 Forbidden when sending a GET request to the API.

        This is a convenience method for the common case of asserting that a GET request.
        This method is used when the user is authenticated but does not have the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.get_json(fragment, **params)
        self.assertHttpForbidden(resp)
        return resp

    def get_json_bad_request(self, fragment="", **params):
        """
        Assert that the response is a 400 Bad Request when sending a GET request to the API.

        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.get_json(fragment, **params)
        self.assertHttpBadRequest(resp)
        return resp

    def get_json_not_found(self, fragment="", **params):
        """
        Assert that the response is a 404 Not Found when requesting a resource that does not exist.

        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.get_json(fragment, **params)
        self.assertHttpNotFound(resp)
        return resp

    def get_json_method_not_allowed(self, fragment="", **params):
        """
        Assert that the response is a 405 Method Not Allowed.

        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.get_json(fragment, **params)
        self.assertHttpNotAllowed(resp)
        return resp

    # POST JSON
    # ---------------------------------------#
    def post_json(self, fragment, data, **params):
        """
        Send a POST request to the API.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        url = self.build_api_url(fragment)
        logger.debug("POST %s", url)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = self.get_credentials()
        elif self.auth == "invalid_token":
            invalid_token = str(uuid.uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Bearer {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.post(url, format="json", data=data)

    def post_json_ok(self, fragment="", data=None, **params):
        """
        Assert that the response is a 200 OK response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        try:
            self.assertHttpOk(resp)
        except Exception as exc:
            logger.exception(exc)
        return resp

    def post_json_created(self, fragment="", data=None, **params):
        """
        Assert that the response is a 201 Created response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        self.assertHttpCreated(resp)
        return resp

    def post_json_no_content(self, fragment="", data=None, **params):
        """
        Assert that the response is a 204 No Content response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        self.assertHttpNoContent(resp)
        return resp

    def post_json_forbidden(self, fragment="", data=None, **params):
        """
        Assert that the response is a 403 Forbidden response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used when the user is authenticated but does not have the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        self.assertHttpForbidden(resp)
        return resp

    def post_json_bad_request(self, fragment="", data=None, **params):
        """
        Assert that the response is a 400 Bad Request response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used to test the API with invalid data.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        self.assertHttpBadRequest(resp)
        return resp

    def post_json_unauthorized(self, fragment="", data=None, **params):
        """
        Assert that the response is a 401 Unauthorized response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used when user is not authenticated.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        self.auth = "invalid_token"
        resp = self.post_json(fragment, data, **params)
        self.assertHttpUnauthorized(resp)
        return resp

    def post_json_not_found(self, fragment="", data=None, **params):
        """
        Assert that the response is a 404 Not Found response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request
        to a non-existent resource returns a 404 response.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        self.assertHttpNotFound(resp)

    def post_json_too_many_requests(self, fragment="", data=None, **params):
        """
        Assert that the response is a 429 Too Many Requests response when posting data to the API.

        This is a convenience method for the common case of asserting that a POST request.
        This method is used to test the API when the user has sent too many requests
        in a given amount of time ("rate limiting").

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        resp = self.post_json(fragment, data, **params)
        self.assertHttpTooManyRequests(resp)
        return resp

    # PUT JSON
    # ---------------------------------------#
    def put_json(self, fragment="", data=None, **params):
        """
        Send a PUT request to the API.

        This is a convenience method for the common case of sending a PUT request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment (str, optional): The fragment of the URL to be appended to the base URL. Defaults to "".
            data (dict, optional): The data to be sent with the request. Defaults to None.
            params (dict, optional): The parameters to be sent with the request.

        Returns:
            Response: Response data
        """
        url = self.build_api_url(fragment)
        logger.debug("PUT %s", url)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = self.get_credentials()
        elif self.auth == "invalid_token":
            invalid_token = str(uuid.uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Bearer {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.put(url, format="json", data=data)

    def put_json_ok(self, fragment="", data=None, **params):
        """
        Assert that the response is a 200 OK when sending a PUT request to the API.

        This is a convenience method for the common case of asserting that a PUT request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.put_json(fragment, data, **params)
        self.assertHttpOk(resp)
        return resp

    def put_json_bad_request(self, fragment="", data=None, **params):
        """
        Assert that the response is a 400 Bad Request when sending a PUT request to the API.

        This is a convenience method for the common case of asserting that a PUT request.
        This method is used to test the API with invalid data.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.put_json(fragment, data, **params)
        self.assertHttpBadRequest(resp)
        return resp

    def put_json_unauthorized(self, fragment="", data=None, **params):
        """
        Assert that the response is a 401 Unauthorized when sending a PUT request to the API.

        This is a convenience method for the common case of asserting that a PUT request.
        This method is used when the user is not authenticated.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        self.auth = "invalid_token"
        resp = self.put_json(fragment, data, **params)
        self.assertHttpUnauthorized(resp)
        return resp

    def put_json_forbidden(self, fragment="", data=None, **params):
        """
        Assert that the response is a 403 Forbidden when sending a PUT request to the API.

        This is a convenience method for the common case of asserting that a PUT request.
        This method is used when the user is authenticated but does not have the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.put_json(fragment, data, **params)
        self.assertHttpForbidden(resp)
        return resp

    def put_json_not_found(self, fragment="", data=None, **params):
        """
        Assert that the response is a 404 Not Found when sending a PUT request to the API.

        This is a convenience method for the common case of asserting that a PUT request
        to a non-existent resource returns a 404 response.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.put_json(fragment, data, **params)
        self.assertHttpNotFound(resp)

    # PATCH JSON
    # ---------------------------------------#
    def patch_json(self, fragment="", data=None, **params):
        """
        Send a PATCH request to the API.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        url = self.build_api_url(fragment)
        logger.debug("PATCH %s", url)

        headers = {}

        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = self.get_credentials()
        elif self.auth == "invalid_token":
            invalid_token = str(uuid.uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Bearer {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.patch(url, format="json", data=data)

    def patch_json_ok(self, fragment="", data=None, **params):
        """
        Assert that the response is a 200 OK when user send a PATCH method to the API.

        This is a convenience method for the common case of asserting that a PATCH request.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.patch_json(fragment, data, **params)
        self.assertHttpOk(resp)
        return resp

    def patch_json_bad_request(self, fragment="", data=None, **params):
        """
        Assert that the response is a 400 Bad Request when user send a PATCH method to the API.

        This method is used to test the API with invalid data.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.patch_json(fragment, data, **params)
        self.assertHttpBadRequest(resp)
        return resp

    def patch_json_unauthorized(self, fragment="", data=None, **params):
        """
        Assert that the response is a 401 Unauthorized when user send a PATCH method to the API.

        This is used when the user is not logged in.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        self.auth = "invalid_token"
        resp = self.patch_json(fragment, data, **params)
        self.assertHttpUnauthorized(resp)
        return resp

    def patch_json_forbidden(self, fragment="", data=None, **params):
        """
        Assert that the response is a 403 Forbidden when user send a PATCH method to the API.

        This is used when the user is authenticated but does not have the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.patch_json(fragment, data, **params)
        self.assertHttpForbidden(resp)
        return resp

    def patch_json_not_found(self, fragment="", data=None, **params):
        """
        Assert that the response is a 404 Not Found when user send a PATCH method to the API.

        This is a convenience method for the common case of asserting that a PATCH request
        to a non-existent resource returns a 404 response.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.patch_json(fragment, data, **params)
        self.assertHttpNotFound(resp)

    # DELETE JSON
    # ---------------------------------------#
    def delete_json(self, fragment="", data=None, **params):
        """
        Send a DELETE request to the API.

        This method is used when the user is authenticated and has the correct permissions.

        Args:
           fragment: The fragment of the URL to be appended to the base URL.
           data: The data to be sent with the request.
           params: The parameters to be sent with the request.
        """
        url = self.build_api_url(fragment)
        logger.debug("DELETE %s", url)

        headers = {}
        if self.auth == "token":
            headers["HTTP_AUTHORIZATION"] = self.get_credentials()
        elif self.auth == "invalid_token":
            invalid_token = str(uuid.uuid4())
            headers["HTTP_AUTHORIZATION"] = f"Bearer {invalid_token}"
        else:
            headers["HTTP_AUTHORIZATION"] = None

        self.api_client.credentials(**headers)

        return self.api_client.delete(url, data, **params)

    def delete_json_ok(self, fragment="", data=None, **params):
        """
        Assert that the response status code is 200 OK when request API with DELETE method.

        This method is used to test the API with valid data.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.delete_json(fragment, data, **params)
        self.assertHttpOk(resp)
        return resp

    def delete_json_no_content(self, fragment="", data=None, **params):
        """
        Assert that the response status code is 204 No Content when request API with DELETE method.

        This method is used to test the API with valid data.
        This method is used when the user is authenticated and has the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.delete_json(fragment, data, **params)
        self.assertHttpNoContent(resp)
        return resp

    def delete_json_bad_request(self, fragment="", data=None, **params):
        """
        Assert that the response status code is 400 Bad Request when request API with DELETE method.

        This method is used to test the API with invalid data.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.delete_json(fragment, data, **params)
        self.assertHttpBadRequest(resp)
        return resp

    def delete_json_unauthorized(self, fragment="", data=None, **params):
        """
        Assert that the response status code is 401 Unauthorized when request API with DELETE method.

        This is used when the user is not logged in.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        self.auth = "invalid_token"
        resp = self.delete_json(fragment, data, **params)
        self.assertHttpUnauthorized(resp)
        return resp

    def delete_json_forbidden(self, fragment="", data=None, **params):
        """
        Assert that the response status code is 403 Forbidden when request API with DELETE method.

        This is used when the user is authenticated but does not have the correct permissions.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.delete_json(fragment, data, **params)
        self.assertHttpForbidden(resp)
        return resp

    def delete_json_not_found(self, fragment="", data=None, **params):
        """
        Assert the response status code is 404 when request API with DELETE method.

        This is a convenience method for the common case of asserting that a DELETE request
        to a non-existent resource returns a 404 response.

        Args:
            fragment: The fragment of the URL to be appended to the base URL.
            data: The data to be sent with the request.
            params: The parameters to be sent with the request.
        """
        resp = self.delete_json(fragment, data, **params)
        self.assertHttpNotFound(resp)
