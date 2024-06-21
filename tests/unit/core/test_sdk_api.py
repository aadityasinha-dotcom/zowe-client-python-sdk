"""Unit tests for the Zowe Python SDK Core package."""

# Including necessary paths
import os
from unittest import mock

from pyfakefs.fake_filesystem_unittest import TestCase
from zowe.core_for_zowe_sdk import (
    SdkApi,
    session_constants
)

class TestSdkApiClass(TestCase):
    """SdkApi class unit tests."""

    def setUp(self):
        """Setup fixtures for SdkApi class."""
        common_props = {"host": "mock-url.com", "port": 443, "protocol": "https", "rejectUnauthorized": True}
        self.basic_props = {**common_props, "user": "Username", "password": "Password"}
        self.bearer_props = {**common_props, "tokenValue": "BearerToken"}
        self.token_props = {
            **common_props,
            "tokenType": "MyToken",
            "tokenValue": "TokenValue",
        }
        self.default_url = "https://default-api.com/"

    def test_object_should_be_instance_of_class(self):
        """Created object should be instance of SdkApi class."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertIsInstance(sdk_api, SdkApi)

    @mock.patch("logging.Logger.error")
    def test_session_no_host_logger(self, mock_logger_error: mock.MagicMock):
        props = {}
        try:
            sdk_api = SdkApi(props, self.default_url)
        except Exception:
            mock_logger_error.assert_called()
            self.assertIn("Host", mock_logger_error.call_args[0][0])

    @mock.patch("logging.Logger.error")
    def test_session_no_authentication_logger(self, mock_logger_error: mock.MagicMock):
        props = {"host": "test"}
        try:
            sdk_api = SdkApi(props, self.default_url)
        except Exception:
            mock_logger_error.assert_called()
            self.assertIn("Authentication", mock_logger_error.call_args[0][0])

    def test_should_handle_basic_auth(self):
        """Created object should handle basic authentication."""
        sdk_api = SdkApi(self.basic_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_BASIC)
        self.assertEqual(
            sdk_api.request_arguments["auth"],
            (self.basic_props["user"], self.basic_props["password"]),
        )

    def test_should_handle_bearer_auth(self):
        """Created object should handle bearer authentication."""
        sdk_api = SdkApi(self.bearer_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_BEARER)
        self.assertEqual(
            sdk_api.default_headers["Authorization"],
            "Bearer " + self.bearer_props["tokenValue"],
        )

    def test_should_handle_token_auth(self):
        """Created object should handle token authentication."""
        sdk_api = SdkApi(self.token_props, self.default_url)
        self.assertEqual(sdk_api.session.type, session_constants.AUTH_TYPE_TOKEN)
        self.assertEqual(
            sdk_api.default_headers["Cookie"],
            self.token_props["tokenType"] + "=" + self.token_props["tokenValue"],
        )

    def test_encode_uri_component(self):
        """Test string is being adjusted to the correct URL parameter"""

        sdk_api = SdkApi(self.basic_props, self.default_url)

        actual_not_empty = sdk_api._encode_uri_component("MY.STRING@.TEST#.$HERE(MBR#NAME)")
        expected_not_empty = "MY.STRING%40.TEST%23.%24HERE(MBR%23NAME)"
        self.assertEqual(actual_not_empty, expected_not_empty)

        actual_wildcard = sdk_api._encode_uri_component("GET.#DS.*")
        expected_wildcard = "GET.%23DS.*"
        self.assertEqual(actual_wildcard, expected_wildcard)

        actual_none = sdk_api._encode_uri_component(None)
        expected_none = None
        self.assertEqual(actual_none, expected_none)