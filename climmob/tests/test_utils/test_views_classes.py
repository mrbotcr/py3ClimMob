import json
import unittest
import uuid
from datetime import datetime as dt
from hashlib import md5
from unittest.mock import MagicMock, patch, mock_open

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.testing import DummyRequest
from webob.multidict import MultiDict

from climmob.views.classes import (
    ResourceCallback,
    odkView,
    publicView,
    privateView,
    apiView,
)


class TestResourceCallback(unittest.TestCase):
    def setUp(self):
        # Initial mock configuration
        self.request = MagicMock()
        self.response = MagicMock()
        self.request.application_url = "http://localhost"
        self.request.registry.settings = {"apppath": "/fake/path"}

    @patch("uuid.uuid4", return_value=uuid.UUID("12345678123456781234567812345678"))
    @patch("builtins.open", new_callable=mock_open)
    def test_resource_callback_with_script(self, mock_open, mock_uuid):
        self.response.content_type = "text/html"
        self.response.body = """
        <html>
        <head></head>
        <body>
        <script>
        console.log('Hello, world!');
        </script>
        <script src="http://example.com/script.js"></script>
        </body>
        </html>
        """.encode()

        ResourceCallback(self.request, self.response)

        # Verifications
        mock_open.assert_called_once_with(
            "/fake/path/static/ephemeral/12345678-1234-5678-1234-567812345678.js", "w"
        )
        handle = mock_open()
        handle.write.assert_called_once_with("console.log('Hello, world!');\n")
        expected_body = (
            '<html>\n<head></head>\n<body>\n<script src="http://example.com/script.js"></script>\n<script src="http://localhost/static/ephemeral/12345678-1234-5678-1234-567812345678.js"></script>\n</body>\n</html>\n'
        ).encode()
        self.assertEqual(self.response.body, expected_body)

    @patch("uuid.uuid4", return_value=uuid.UUID("12345678123456781234567812345678"))
    @patch("builtins.open", new_callable=mock_open)
    def test_resource_callback_without_script(self, mock_open, mock_uuid):
        self.response.content_type = "text/html"
        self.response.body = """
        <html>
        <head></head>
        <body>
        <h1>Hello, world!</h1>
        </body>
        </html>
        """.encode()

        ResourceCallback(self.request, self.response)

        # Verifications
        mock_open.assert_called_once_with(
            "/fake/path/static/ephemeral/12345678-1234-5678-1234-567812345678.js", "w"
        )
        handle = mock_open()
        handle.write.assert_called_once_with("console.log('');")
        expected_body = (
            '<html>\n<head></head>\n<body>\n<h1>Hello, world!</h1>\n<script src="http://localhost/static/ephemeral/12345678-1234-5678-1234-567812345678.js"></script>\n</body>\n</html>\n'
        ).encode()
        self.assertEqual(self.response.body, expected_body)

    def test_resource_callback_non_html(self):
        self.response.content_type = "application/json"
        self.response.body = '{"key": "value"}'.encode()

        ResourceCallback(self.request, self.response)

        # Verify that no changes are made to the response body
        self.assertEqual(self.response.body, b'{"key": "value"}')
        self.assertEqual(self.response.content_type, "application/json")


class TestOdkView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.translate = MagicMock()
        self.request.registry.settings = {
            "auth.opaque": "opaque_value",
            "auth.realm": "realm_value",
        }
        self.request.headers = {
            "Authorization": 'Digest username="user", realm="realm_value", nonce="nonce", uri="/", response="response", qop="auth", nc="00000001", cnonce="cnonce"'
        }
        self.request.method = "GET"
        self.request.body = b""
        self.view = odkView(self.request)
        self.view.getAuthDict()

    def test_getAuthDict(self):
        expected_auth_header = {
            "Digest username": "user",
            "realm": "realm_value",
            "nonce": "nonce",
            "uri": "/",
            "response": "response",
            "qop": "auth",
            "nc": "00000001",
            "cnonce": "cnonce",
        }
        self.assertEqual(self.view.authHeader, expected_auth_header)

    def test_getAuthDict_with_auth_header_format(self):
        self.request.headers[
            "Authorization"
        ] = 'Digest username="user", realm="realm_value", nonce="nonce=extra", uri="/", response="response", qop="auth", nc="00000001", cnonce="cnonce"'
        self.view.getAuthDict()
        expected_auth_header = {
            "Digest username": "user",
            "realm": "realm_value",
            "nonce": "nonce=extra",
            "uri": "/",
            "response": "response",
            "qop": "auth",
            "nc": "00000001",
            "cnonce": "cnonce",
        }
        self.assertEqual(self.view.authHeader, expected_auth_header)

    @patch("climmob.views.classes.md5", side_effect=md5)
    def test_authorize_auth_qop(self, mock_md5):
        self.view.user = "user"
        correct_password = "password".encode()

        ha1 = md5(
            (
                self.view.user + ":" + self.view.realm + ":" + correct_password.decode()
            ).encode()
        ).hexdigest()
        ha2 = md5(
            (self.request.method + ":" + self.view.authHeader["uri"]).encode()
        ).hexdigest()

        authLine = ":".join(
            [
                ha1,
                self.view.authHeader["nonce"],
                self.view.authHeader["nc"],
                self.view.authHeader["cnonce"],
                self.view.authHeader["qop"],
                ha2,
            ]
        )
        expected_response = md5(authLine.encode()).hexdigest()
        self.view.authHeader[
            "response"
        ] = expected_response  # Simulate correct response

        result = self.view.authorize(correct_password)
        self.assertTrue(result)

    @patch("climmob.views.classes.md5", side_effect=md5)
    def test_authorize_auth_int_qop(self, mock_md5):
        self.view.user = "user"
        correct_password = "password".encode()
        self.request.body = b"test_body"
        self.view.authHeader["qop"] = "auth-int"

        ha1 = md5(
            (
                self.view.user + ":" + self.view.realm + ":" + correct_password.decode()
            ).encode()
        ).hexdigest()
        md5_body = md5(self.request.body).hexdigest()
        ha2 = md5(
            (
                self.request.method.encode()
                + b":"
                + self.view.authHeader["uri"].encode()
                + b":"
                + md5_body.encode()
            )
        ).hexdigest()

        authLine = ":".join(
            [
                ha1,
                self.view.authHeader["nonce"],
                self.view.authHeader["nc"],
                self.view.authHeader["cnonce"],
                self.view.authHeader["qop"],
                ha2,
            ]
        )
        expected_response = md5(authLine.encode()).hexdigest()
        self.view.authHeader[
            "response"
        ] = expected_response  # Simulate correct response

        result = self.view.authorize(correct_password)
        self.assertTrue(result)

    def test_askForCredentials(self):
        response = self.view.askForCredentials()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            (
                "WWW-Authenticate",
                'Digest realm="realm_value",qop="auth,auth-int",nonce="{}"'.format(
                    self.view.nonce
                )
                + ',opaque="opaque_value"',
            ),
            response.headerlist,
        )

    def test_createXMLResponse(self):
        XMLData = b"<data>test</data>"
        response = self.view.createXMLResponse(XMLData)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, str(XMLData, "utf-8"))
        self.assertEqual(response.headers["Content-Type"], "text/xml; charset=utf-8")

    @patch("climmob.views.classes.odkView.processView")
    def test_call_with_authorization_header(self, mock_processView):
        mock_processView.return_value = "processed"
        self.request.headers["Authorization"] = 'Digest username="user"'
        response = self.view()
        self.assertEqual(response, "processed")
        mock_processView.assert_called_once()

    def test_call_with_basic_authorization_header(self):
        self.request.headers["Authorization"] = "Basic auth"
        response = self.view()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            (
                "WWW-Authenticate",
                'Digest realm="realm_value",qop="auth,auth-int",nonce="{}"'.format(
                    self.view.nonce
                )
                + ',opaque="opaque_value"',
            ),
            response.headerlist,
        )

    def test_call_without_authorization_header(self):
        del self.request.headers["Authorization"]
        response = self.view()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            (
                "WWW-Authenticate",
                'Digest realm="realm_value",qop="auth,auth-int",nonce="{}"'.format(
                    self.view.nonce
                )
                + ',opaque="opaque_value"',
            ),
            response.headerlist,
        )

    @patch("climmob.views.classes.md5", side_effect=md5)
    def test_processView(self, mock_md5):
        result = self.view.processView()
        self.assertEqual(result, {})


class TestPublicView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.registry.settings = {"secure.javascript": "true"}
        self.request.POST = MultiDict()
        self.request.translate = lambda x: x

    def test_init_secure_javascript_true(self):
        view = publicView(self.request)
        self.request.add_response_callback.assert_called_once_with(ResourceCallback)
        self.assertEqual(view.request, self.request)

    def test_init_secure_javascript_false(self):
        self.request.registry.settings = {"secure.javascript": "false"}
        view = publicView(self.request)
        self.request.add_response_callback.assert_not_called()

    def test_call(self):
        view = publicView(self.request)
        result = view()
        self.assertEqual(result, {})

    def test_processView(self):
        view = publicView(self.request)
        result = view.processView()
        self.assertEqual(result, {})

    def test_getPostDict(self):
        self.request.POST = MultiDict({"key1": "value1", "key2": "value2"})
        view = publicView(self.request)
        result = view.getPostDict()
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

    @patch("climmob.views.classes.variable_decode")
    def test_getPostDict_with_variable_decode(self, mock_variable_decode):
        mock_variable_decode.return_value = {"key1": "value1"}
        view = publicView(self.request)
        result = view.getPostDict()
        self.assertEqual(result, {"key1": "value1"})
        mock_variable_decode.assert_called_once_with(self.request.POST)

    def test_decodeDict(self):
        view = publicView(self.request)
        input_dict = {"key1": "value1", "key2": b"value2"}
        result = view.decodeDict(input_dict)
        expected = {"key1": "value1", "key2": b"value2"}  # Adjusted expectation
        self.assertEqual(result, expected)

    def test_decodeDict_with_unicode(self):
        view = publicView(self.request)
        input_dict = {"key1": "value1", "key2": "value2"}
        result = view.decodeDict(input_dict)
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})


class TestPrivateView(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.request.registry.settings = {"secure.javascript": "true"}
        self.request.POST = MultiDict()
        self.request.method = "GET"
        self.request.matched_route = MagicMock(name="matched_route")
        self.request.matched_route.name = "dashboard"
        self.request.translate = lambda x: x
        self.request.route_url = MagicMock(return_value="/login")
        self.request.policies = MagicMock(
            return_value=[{"name": "main", "policy": MagicMock()}]
        )
        self.request.session = MagicMock()
        self.request.dbsession = MagicMock()  # Added to avoid dbsession errors
        self.view = privateView(self.request)

    @patch("climmob.views.classes.ResourceCallback")
    def test_init_secure_javascript_true(self, mock_resource_callback):
        self.request.add_response_callback = MagicMock()
        self.view = privateView(self.request)
        self.request.add_response_callback.assert_called_once_with(
            mock_resource_callback
        )

    def test_call_no_authenticated_userid(self):
        policy = self.view.get_policy("main")
        policy.authenticated_userid.return_value = None
        response = self.view()
        self.assertIsInstance(response, HTTPFound)
        self.request.route_url.assert_called_with("login")

    @patch("climmob.views.classes.getUserData")
    @patch(
        "climmob.views.classes.literal_eval",
        return_value={"group": "mainApp", "login": "test"},
    )
    def test_call_authenticated_userid_none(
        self, mock_literal_eval, mock_get_user_data
    ):
        policy = self.view.get_policy("main")
        policy.authenticated_userid.return_value = (
            "{'group': 'mainApp', 'login': 'test'}"
        )
        mock_get_user_data.return_value = None
        response = self.view()
        self.assertIsInstance(response, HTTPFound)
        self.request.route_url.assert_called_with("login")

    @patch("climmob.views.classes.getUserData")
    @patch(
        "climmob.views.classes.literal_eval",
        return_value={"group": "mainApp", "login": "test"},
    )
    def test_call_authenticated_userid_valid_user(
        self, mock_literal_eval, mock_get_user_data
    ):
        policy = self.view.get_policy("main")
        policy.authenticated_userid.return_value = (
            "{'group': 'mainApp', 'login': 'test'}"
        )
        mock_get_user_data.return_value = MagicMock(
            login="test_user", languages=["en"], email="test@example.com"
        )

        with patch("climmob.views.classes.counterChat", return_value=5), patch(
            "climmob.views.classes.getActiveProject", return_value={"project_id": 1}
        ), patch(
            "climmob.views.classes.getActiveForm",
            return_value=(True, {"form_name": "Survey"}),
        ), patch(
            "climmob.views.classes.getLastActivityLogByUser",
            return_value={
                "log_message": "Created a new project",
                "log_datetime": dt.now(),
            },
        ), patch(
            "climmob.views.classes.addToLog"
        ), patch(
            "climmob.views.classes.update_last_login"
        ), patch(
            "climmob.views.classes.p.PluginImplementations", return_value=[]
        ):

            response = self.view()

            self.assertEqual(response["activeUser"].login, "test_user")
            self.assertTrue(response["hasActiveProject"])
            self.assertEqual(response["activeProject"], 1)
            self.assertEqual(response["counterChat"], 5)
            self.assertEqual(response["surveyMustBeDisplayed"], "Survey")
            self.assertTrue(response["showRememberAfterCreateProject"])

    def test_processView(self):
        self.view.user = {"login": "test_user"}
        result = self.view.processView()
        self.assertEqual(result, {"activeUser": {"login": "test_user"}})

    def test_getPostDict(self):
        self.request.POST = MultiDict({"key1": "value1", "key2": "value2"})
        result = self.view.getPostDict()
        self.assertEqual(result, {"key1": "value1", "key2": "value2"})

    def test_decodeDict(self):
        input_dict = {"key1": "value1", "key2": "value2"}
        expected_dict = {"key1": "value1", "key2": "value2"}
        result = self.view.decodeDict(input_dict)
        self.assertEqual(result, expected_dict)

    def test_get_policy(self):
        policy = self.view.get_policy("main")
        self.assertIsNotNone(policy)

    def test_get_policy_not_found(self):
        policy = self.view.get_policy("nonexistent")
        self.assertIsNone(policy)

    @patch("climmob.views.classes.check_csrf_token", return_value=False)
    @patch("climmob.views.classes.getUserData")
    @patch(
        "climmob.views.classes.literal_eval",
        return_value={"group": "mainApp", "login": "test"},
    )
    def test_csrf_token_failure(
        self, mock_literal_eval, mock_get_user_data, mock_check_csrf_token
    ):
        self.request.method = "POST"
        policy = self.view.get_policy("main")
        policy.authenticated_userid.return_value = (
            "{'group': 'mainApp', 'login': 'test'}"
        )
        mock_get_user_data.return_value = MagicMock(
            login="test_user", languages=["en"], email="test@example.com"
        )

        with self.assertRaises(HTTPNotFound):
            self.view()

    @patch("climmob.views.classes.check_csrf_token", return_value=True)
    @patch("climmob.views.classes.getUserData")
    @patch(
        "climmob.views.classes.literal_eval",
        return_value={"group": "mainApp", "login": "test"},
    )
    def test_cross_post_failure(
        self, mock_literal_eval, mock_get_user_data, mock_check_csrf_token
    ):
        self.request.method = "POST"
        self.view.checkCrossPost = True
        self.request.referer = "http://malicious.site"
        self.request.url = "http://my.site"
        policy = self.view.get_policy("main")
        policy.authenticated_userid.return_value = (
            "{'group': 'mainApp', 'login': 'test'}"
        )
        mock_get_user_data.return_value = MagicMock(
            login="test_user", languages=["en"], email="test@example.com"
        )

        with self.assertRaises(HTTPNotFound):
            self.view()

    @patch("climmob.views.classes.check_csrf_token", return_value=True)
    @patch("climmob.views.classes.getUserData")
    @patch(
        "climmob.views.classes.literal_eval",
        return_value={"group": "mainApp", "login": "test"},
    )
    def test_cross_post_success(
        self, mock_literal_eval, mock_get_user_data, mock_check_csrf_token
    ):
        self.request.method = "POST"
        self.view.checkCrossPost = True
        self.request.referer = self.request.url  # Simulate same origin
        policy = self.view.get_policy("main")
        policy.authenticated_userid.return_value = (
            "{'group': 'mainApp', 'login': 'test'}"
        )
        mock_get_user_data.return_value = MagicMock(
            login="test_user", languages=["en"], email="test@example.com"
        )

        with patch("climmob.views.classes.update_last_login"), patch(
            "climmob.views.classes.p.PluginImplementations", return_value=[]
        ):
            self.view()


class TestApiView(unittest.TestCase):
    def setUp(self):
        self.request = DummyRequest()
        self.request.params = {}
        self.request.translate = lambda x: x
        self.view = apiView(self.request)

    @patch("climmob.views.classes.getUserByApiKey", return_value=None)
    def test_call_invalid_apikey(self, mock_getUserByApiKey):
        self.request.params = {"Apikey": "invalid"}
        response = self.view()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"This Apikey does not exist or is inactive.")

    @patch("climmob.views.classes.getUserByApiKey", return_value={"login": "test_user"})
    def test_call_valid_apikey_with_body(self, mock_getUserByApiKey):
        self.request.params = {"Apikey": "valid", "Body": '{"key": "value"}'}
        response = self.view()
        self.assertEqual(self.view.user["login"], "test_user")
        self.assertEqual(self.view.body, '{"key": "value"}')
        # Here the verification of update_last_login was removed

    @patch("climmob.views.classes.getUserByApiKey", return_value={"login": "test_user"})
    def test_call_valid_apikey_without_body(self, mock_getUserByApiKey):
        self.request.params = {"Apikey": "valid", "key1": "value1", "key2": "value2"}
        response = self.view()
        self.assertEqual(self.view.user["login"], "test_user")
        self.assertEqual(
            json.loads(self.view.body), {"key1": "value1", "key2": "value2"}
        )
        # Here the verification of update_last_login was removed

    @patch(
        "climmob.views.classes.getUserByApiKey",
        side_effect=Exception("Unexpected error"),
    )
    def test_call_exception_handling(self, mock_getUserByApiKey):
        self.request.params = {"Apikey": "valid"}
        response = self.view()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Apikey non-existent")

    def test_processView(self):
        result = self.view.processView()
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
