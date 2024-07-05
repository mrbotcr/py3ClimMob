import unittest
import secrets
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from unittest.mock import patch, MagicMock
from pyramid.testing import DummyRequest
import smtplib

from climmob.views.basic_views import render_template
from climmob.views.basic_views import (
    HomeView,
    HealthView,
    TermsView,
    PrivacyView,
    NotFoundView,
    StoreCookieView,
    get_policy,
    LoginView,
    RecoverPasswordView,
    ResetPasswordView,
    logout_view,
    register_view,
)


class TestRenderTemplate(unittest.TestCase):
    @patch("climmob.views.basic_views.jinjaEnv")
    def test_render_template(self, mock_jinjaEnv):
        mock_reset = MagicMock()
        mock_request = MagicMock()
        _template_filename = "email/recover_email.jinja2"
        _context = {
            "recovery_date": "asdf",
            "reset_token": secrets.token_hex(16),
            "user_dict": {"1", "2", "3", "4", "5"},
            "reset_url": mock_reset,
            "_": mock_request,
        }

        mock_template = MagicMock()
        mock_template.render.return_value = "Rendered template content"

        mock_jinjaEnv.get_template.return_value = mock_template

        result = render_template(_template_filename, _context)

        mock_jinjaEnv.get_template.assert_called_with(_template_filename)
        mock_template.render.assert_called_with(_context)
        self.assertEqual(result, "Rendered template content")


class TestProcessView(unittest.TestCase):
    @patch("climmob.views.basic_views.getProjectCount")
    @patch("climmob.views.basic_views.getUserCount")
    def test_process_view_without_cookies(
        self, mock_getProjectCount, mock_getUserCount
    ):
        mock_request = MagicMock()
        mock_request.cookies = {}

        mock_public_view = MagicMock()
        mock_public_view.request = mock_request

        _num_users = 3
        _num_projs = 3
        mock_getUserCount.return_value = _num_users
        mock_getProjectCount.return_value = _num_projs

        view = HomeView(mock_public_view)
        view.request = mock_request
        result = view.processView()

        self.assertEqual(result["numUsers"], 3)
        self.assertEqual(result["numProjs"], 3)
        self.assertTrue(result["ask_for_cookies"])


class TestProcessViewCookie(unittest.TestCase):
    @patch("climmob.views.basic_views.getProjectCount")
    @patch("climmob.views.basic_views.getUserCount")
    def test_process_view_with_cookies(self, mock_getProjectCount, mock_getUserCount):
        mock_request = MagicMock()
        mock_request.cookies = {"climmob_cookie_question": "some_value"}

        mock_public_view = MagicMock()
        mock_public_view.request = mock_request

        _num_users = 3
        _num_projs = 3
        mock_getUserCount.return_value = _num_users
        mock_getProjectCount.return_value = _num_projs

        view = HomeView(mock_public_view)
        view.request = mock_request
        result = view.processView()

        self.assertEqual(result["numUsers"], 3)
        self.assertEqual(result["numProjs"], 3)
        self.assertFalse(result["ask_for_cookies"])


class TestHealthView(unittest.TestCase):
    def setUp(self):
        # Configurar el mock para request y dbsession
        self.mock_request = MagicMock()
        self.mock_request.dbsession = MagicMock()
        self.mock_engine = MagicMock()
        self.mock_engine.pool.status.return_value = "Pool status info"
        self.mock_request.dbsession.get_bind.return_value = self.mock_engine

    def test_process_view_success(self):
        self.mock_request.dbsession.execute.return_value.fetchone.return_value = (
            "Threads_connected",
            5,
        )
        view = HealthView(self.mock_request)
        result = view.processView()
        self.assertEqual(result["health"]["pool"], "Pool status info")
        self.assertEqual(result["health"]["threads_connected"], 5)

    def test_process_view_exception(self):
        self.mock_request.dbsession.execute.side_effect = Exception("Database error")
        view = HealthView(self.mock_request)
        result = view.processView()
        self.assertEqual(result["health"]["pool"], "Pool status info")
        self.assertEqual(result["health"]["threads_connected"], "Database error")


class TestTermsView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()

    def test_process_view(self):
        view = TermsView(self.mock_request)
        result = view.processView()

        self.assertEqual(result, {})


class TestPrivacyView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()

    def test_process_view(self):
        view = PrivacyView(self.mock_request)
        result = view.processView()

        self.assertEqual(result, {})


class TestNotFoundView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_response = MagicMock()
        self.mock_request.response = self.mock_response

    def test_process_view(self):
        view = NotFoundView(self.mock_request)

        result = view.processView()
        self.assertEqual(result, {})

        self.mock_request.response.status = 404
        self.assertEqual(self.mock_request.response.status, 404)


class TestStoreCookieView(unittest.TestCase):

    # Enable the settings
    def setUp(self):
        self.mock_request = MagicMock()
        self.view = StoreCookieView(self.mock_request)

    # If the request method is "GET", an HTTPNotFound exception is expected to be thrown
    def test_process_view_get_method(self):
        self.mock_request.method = "GET"
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    # A POST request is simulated without the "accept" parameter
    # It is verified that the response is a redirect (HTTPFound) to the "home" URL
    # Makes sure that the "climammob_cookie_question" cookie has not been set
    def test_process_view_post_method_without_accept(self):
        self.mock_request.method = "POST"
        self.mock_request.params.get.return_value = None
        self.mock_request.route_url.return_value = "http://example.com/home"
        self.mock_request.POST = {}

        response = self.view.processView()

        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "http://example.com/home")
        self.assertFalse(response.headers.get("Set-Cookie"))

    # A POST request is simulated with the "accept" parameter
    # It is verified that the response is a redirect (HTTPFound) to the "home" URL
    # Ensures that the cookie "climmob_cookie_question" has been set with the value "accept"
    def test_process_view_post_method_with_accept(self):
        self.mock_request.method = "POST"
        self.mock_request.params.get.return_value = None
        self.mock_request.route_url.return_value = "http://example.com/home"
        self.mock_request.POST = {"accept": "true"}

        response = self.view.processView()

        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "http://example.com/home")
        self.assertIn(
            "climmob_cookie_question=accept", response.headers.get("Set-Cookie", "")
        )

    # A POST request is simulated with the "next" parameter and the "accept" parameter
    # The response is verified to be a redirect (HTTPFound) to the URL specified in the "next" parameter
    # Ensures that the cookie "climmob_cookie_question" has been set with the value "accept"
    def test_process_view_post_method_with_next_param(self):
        self.mock_request.method = "POST"
        self.mock_request.params.get.return_value = "http://example.com/next"
        self.mock_request.POST = {"accept": "true"}

        response = self.view.processView()

        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "http://example.com/next")
        self.assertIn(
            "climmob_cookie_question=accept", response.headers.get("Set-Cookie", "")
        )


class TestGetPolicy(unittest.TestCase):

    # Enable the settings
    def setUp(self):
        self.mock_request = MagicMock()

    # Test when the policy exists
    def test_policy_exists(self):
        policies = [
            {"name": "policy1", "policy": "Policy Content 1"},
            {"name": "policy2", "policy": "Policy Content 2"},
        ]
        self.mock_request.policies.return_value = policies

        result = get_policy(self.mock_request, "policy1")
        self.assertEqual(result, "Policy Content 1")

    # Test when the policy does not exist
    def test_policy_does_not_exist(self):
        policies = [
            {"name": "policy1", "policy": "Policy Content 1"},
            {"name": "policy2", "policy": "Policy Content 2"},
        ]
        self.mock_request.policies.return_value = policies

        result = get_policy(self.mock_request, "policy3")
        self.assertIsNone(result)

    # Try an empty list of policies
    def test_empty_policies(self):
        self.mock_request.policies.return_value = []

        result = get_policy(self.mock_request, "policy1")
        self.assertIsNone(result)

    # Test when the policies method does not exist
    def test_no_policies_method(self):
        self.mock_request.policies.side_effect = AttributeError("No policies method")

        with self.assertRaises(AttributeError):
            get_policy(self.mock_request, "policy1")


class TestLoginView(unittest.TestCase):

    # Enable the settings
    def setUp(self):
        self.mock_request = MagicMock()
        self.view = LoginView(self.mock_request)

    # Test for when the user is already authenticated
    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.literal_eval")
    @patch("climmob.views.basic_views.getUserData")
    def test_process_view_logged_in(
        self, mock_getUserData, mock_literal_eval, mock_get_policy
    ):
        # Set up cookies and policy mocks
        self.mock_request.cookies = {"climmob_cookie_question": "accept"}
        policy = MagicMock()
        policy.authenticated_userid.return_value = (
            "{'login': 'test_user', 'group': 'mainApp'}"
        )
        mock_get_policy.return_value = policy
        mock_literal_eval.return_value = {"login": "test_user", "group": "mainApp"}
        mock_getUserData.return_value = {"id": 1, "name": "Test User"}
        self.mock_request.route_url.return_value = "/dashboard"

        result = self.view.processView()

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dashboard")
        self.assertTrue(self.view.returnRawViewResult)

    # Test for when the user is not authenticated
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_not_logged_in(self, mock_get_policy):
        self.mock_request.cookies = {}
        policy = MagicMock()
        policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = policy
        self.mock_request.route_url.return_value = "/dashboard"
        self.mock_request.params.get.return_value = "/dashboard"

        result = self.view.processView()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["login"], "")
        self.assertFalse(result["failed_attempt"])
        self.assertEqual(result["next"], "/dashboard")
        self.assertTrue(result["ask_for_cookies"])

    # Test for successful login
    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.remember")
    def test_process_view_login_success(
        self, mock_remember, mock_getUserData, mock_get_policy
    ):
        self.mock_request.cookies = {}
        self.mock_request.POST = {
            "submit": "submit",
            "login": "test_user",
            "passwd": "correct_password",
        }
        self.mock_request.params.get.return_value = "/dashboard"
        policy = MagicMock()
        policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = policy
        user = MagicMock()
        user.check_password.return_value = True
        mock_getUserData.return_value = user
        self.mock_request.route_url.return_value = "/dashboard"
        mock_remember.return_value = []

        result = self.view.processView()

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dashboard")

    # Test for failed login
    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getUserData")
    def test_process_view_login_failure(self, mock_getUserData, mock_get_policy):
        self.mock_request.cookies = {}
        self.mock_request.POST = {
            "submit": "submit",
            "login": "test_user",
            "passwd": "wrong_password",
        }
        self.mock_request.params.get.return_value = "/dashboard"
        policy = MagicMock()
        policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = policy
        user = MagicMock()
        user.check_password.return_value = False
        mock_getUserData.return_value = user
        self.mock_request.route_url.return_value = "/dashboard"

        result = self.view.processView()

        self.assertIsInstance(result, dict)
        self.assertEqual(result["login"], "test_user")
        self.assertTrue(result["failed_attempt"])
        self.assertEqual(result["next"], "/dashboard")
        self.assertTrue(result["ask_for_cookies"])


class TestRecoverPasswordView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.registry.settings = {
            "email.server": "smtp.gmail.com",
            "email.user": "user",
            "email.password": "password",
            "email.from": "no-reply@example.com",
        }
        self.mock_request.route_url.return_value = "http://example.com/reset_password"
        self.mock_request.translate = lambda x: x
        self.mock_request.POST = {}

    @patch("smtplib.SMTP")
    def test_send_password_by_email_success(self, mock_smtp):
        view = RecoverPasswordView(self.mock_request)

        view.send_password_by_email(
            body="Test email body",
            target_name="Test User",
            target_email="test@example.com",
            mail_from="no-reply@example.com",
        )

        mock_smtp.assert_called_with("smtp.gmail.com", 587)
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.ehlo.assert_called()
        mock_smtp_instance.starttls.assert_called()
        mock_smtp_instance.login.assert_called_with("user", "password")
        mock_smtp_instance.sendmail.assert_called()
        mock_smtp_instance.quit.assert_called()

    @patch("smtplib.SMTP", side_effect=smtplib.SMTPException("Test Exception"))
    def test_send_password_by_email_exception(self, mock_smtp):
        view = RecoverPasswordView(self.mock_request)

        with patch("builtins.print") as mock_print:
            view.send_password_by_email(
                body="Test email body",
                target_name="Test User",
                target_email="test@example.com",
                mail_from="no-reply@example.com",
            )

            mock_print.assert_called_once_with("Test Exception")

    @patch("climmob.views.basic_views.render_template")
    @patch("climmob.views.basic_views.readble_date")
    @patch("climmob.views.basic_views.getUserByEmail")
    @patch("smtplib.SMTP")
    def test_send_password_email(
        self, mock_smtp, mock_get_user, mock_readble_date, mock_render_template
    ):
        view = RecoverPasswordView(self.mock_request)

        mock_user = MagicMock()
        mock_user.fullName = "Test User"
        mock_user.email = "test@example.com"
        mock_get_user.return_value = (mock_user, "password")

        mock_readble_date.return_value = "June 6, 2024"
        mock_render_template.return_value = "Rendered Email Content"

        view.send_password_email(
            email_to="test@example.com",
            reset_token="test_token",
            reset_key="test_key",
            user_dict=mock_user,
        )

        mock_render_template.assert_called_with(
            "email/recover_email.jinja2",
            {
                "recovery_date": "June 6, 2024",
                "reset_token": "test_token",
                "user_dict": mock_user,
                "reset_url": "http://example.com/reset_password",
                "_": self.mock_request.translate,
            },
        )

        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.sendmail.assert_called()

    @patch("climmob.views.basic_views.log")
    @patch("smtplib.SMTP")
    def test_send_password_email_no_email_from(self, mock_smtp, mock_log):
        self.mock_request.registry.settings["email.from"] = None
        view = RecoverPasswordView(self.mock_request)

        mock_user = MagicMock()
        mock_user.fullName = "Test User"
        mock_user.email = "test@example.com"

        result = view.send_password_email(
            email_to="test@example.com",
            reset_token="test_token",
            reset_key="test_key",
            user_dict=mock_user,
        )

        self.assertFalse(result)
        mock_log.error.assert_called_with(
            "ClimMob has no email settings in place. Email service is disabled."
        )

    @patch("climmob.views.basic_views.log")
    @patch("smtplib.SMTP")
    def test_send_password_email_empty_email_from(self, mock_smtp, mock_log):
        self.mock_request.registry.settings["email.from"] = ""
        view = RecoverPasswordView(self.mock_request)

        mock_user = MagicMock()
        mock_user.fullName = "Test User"
        mock_user.email = "test@example.com"

        result = view.send_password_email(
            email_to="test@example.com",
            reset_token="test_token",
            reset_key="test_key",
            user_dict=mock_user,
        )

        self.assertFalse(result)

    @patch("climmob.views.basic_views.log")
    @patch("smtplib.SMTP")
    def test_send_password_email_no_or_empty_email_from(self, mock_smtp, mock_log):
        view = RecoverPasswordView(self.mock_request)

        mock_user = MagicMock()
        mock_user.fullName = "Test User"
        mock_user.email = "test@example.com"

        cases = [None, ""]

        for email_from in cases:
            with self.subTest(email_from=email_from):
                self.mock_request.registry.settings["email.from"] = email_from

                result = view.send_password_email(
                    email_to="test@example.com",
                    reset_token="test_token",
                    reset_key="test_key",
                    user_dict=mock_user,
                )

                self.assertFalse(result)
                mock_log.error.assert_called_with(
                    "ClimMob has no email settings in place. Email service is disabled."
                )

    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getUserData")
    @patch("smtplib.SMTP")
    def test_process_view_authenticated_user(
        self, mock_smtp, mock_get_user_data, mock_get_policy
    ):
        view = RecoverPasswordView(self.mock_request)

        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "user_id"
        mock_get_policy.return_value = mock_policy
        mock_get_user_data.return_value = {"user_email": "test@example.com"}

        with self.assertRaises(HTTPNotFound):
            view.processView()

    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getUserData")
    @patch("smtplib.SMTP")
    def test_process_view_no_email_provided(
        self, mock_smtp, mock_get_user_data, mock_get_policy
    ):
        view = RecoverPasswordView(self.mock_request)
        self.mock_request.POST = {"submit": "Submit"}

        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        mock_get_user_data.return_value = None

        result = view.processView()

        self.assertIn("error_summary", result)
        self.assertIn("email", result["error_summary"])
        self.assertEqual(
            result["error_summary"]["email"], "You need to provide an email address"
        )

    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getUserByEmail")
    @patch("climmob.views.basic_views.getUserData")
    @patch("smtplib.SMTP")
    def test_process_view_email_not_found(
        self, mock_smtp, mock_get_user_data, mock_get_user_by_email, mock_get_policy
    ):
        view = RecoverPasswordView(self.mock_request)
        self.mock_request.POST = {"submit": "Submit", "user_email": "test@example.com"}

        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        mock_get_user_data.return_value = (
            None  # Simulamos que no hay usuario autenticado
        )

        mock_get_user_by_email.return_value = (None, None)

        result = view.processView()

        self.assertIn("error_summary", result)
        self.assertIn("email", result["error_summary"])
        self.assertEqual(
            result["error_summary"]["email"],
            "Cannot find an user with such email address",
        )

    @patch("climmob.views.basic_views.secrets.token_hex")
    @patch("climmob.views.basic_views.uuid.uuid4")
    @patch("climmob.views.basic_views.setPasswordResetToken")
    @patch("climmob.views.basic_views.getUserByEmail")
    @patch("climmob.views.basic_views.RecoverPasswordView.send_password_email")
    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getUserData")
    @patch("smtplib.SMTP")
    def test_process_view_successful(
        self,
        mock_smtp,
        mock_get_user_data,
        mock_get_policy,
        mock_send_password_email,
        mock_get_user_by_email,
        mock_set_password_reset_token,
        mock_uuid4,
        mock_token_hex,
    ):
        view = RecoverPasswordView(self.mock_request)
        self.mock_request.POST = {"submit": "Submit", "user_email": "test@example.com"}

        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        mock_get_user_data.return_value = (
            None  # Simulamos que no hay usuario autenticado
        )

        mock_user = MagicMock()
        mock_user.email = "test@example.com"
        mock_user.login = "user_login"
        mock_get_user_by_email.return_value = (mock_user, "password")
        mock_uuid4.return_value = "uuid4"
        mock_token_hex.return_value = "token_hex"

        result = view.processView()

        mock_set_password_reset_token.assert_called_once_with(
            self.mock_request, "user_login", "uuid4", "token_hex"
        )
        mock_send_password_email.assert_called_once_with(
            "test@example.com", "token_hex", "uuid4", mock_user
        )
        self.assertTrue(view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.mock_request.route_url("login"))

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.getUserData")
    def test_invalid_key(self, mock_get_user_data, mock_reset_key_exists):
        # Test case where the reset key is invalid
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "test_user",
            "token": "test_token",
            "password": "new_password",
            "password2": "new_password",
            "email": "test@example.com",
            "user_name": "test_username",
        }

        # Simulate user data with invalid reset key
        mock_get_user_data.return_value = MagicMock(
            userData={
                "user_password_reset_key": "invalid_reset_key",
                "user_password_reset_token": "test_token",
                "user_password_reset_expires_on": datetime.now() + timedelta(days=1),
            }
        )

        with patch.object(view, "_", side_effect=lambda x: x):
            result = view.processView()

        self.assertIn("error_summary", result)
        self.assertEqual(result["error_summary"], {"Error": "Invalid key"})


class TestResetPasswordView(unittest.TestCase):
    def setUp(self):
        # Set up the mock request object with initial values
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {"reset_key": "test_reset_key"}
        self.mock_request.POST = {}
        self.mock_request.remote_addr = "127.0.0.1"
        self.mock_request.user_agent = "TestAgent"

    @patch("climmob.views.basic_views.resetKeyExists", return_value=False)
    def test_reset_key_does_not_exist(self, mock_reset_key_exists):
        # Test case where the reset key does not exist
        view = ResetPasswordView(self.mock_request)

        # Ensure the translate method returns strings correctly
        with patch.object(view, "_", side_effect=lambda x: x):
            with self.assertRaises(HTTPNotFound):
                view.processView()

    def test_invalid_csrf_token(self):
        # Test case where CSRF token is invalid
        with patch("climmob.views.basic_views.resetKeyExists", return_value=True):
            view = ResetPasswordView(self.mock_request)
            self.mock_request.method = "POST"
            with patch(
                "climmob.views.basic_views.check_csrf_token", return_value=False
            ):
                with self.assertRaises(HTTPNotFound):
                    view.processView()

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.check_csrf_token")
    def test_user_does_not_exist(
        self, mock_check_csrf, mock_get_user_data, mock_reset_key_exists
    ):
        # Test case where the user does not exist
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "nonexistent_user",
            "token": "test_token",
            "password": "new_password",
            "password2": "new_password",
            "email": "test@example.com",
            "user_name": "test_username",
        }
        mock_check_csrf.return_value = True
        mock_get_user_data.return_value = None

        with patch.object(view, "_", side_effect=lambda x: x):
            result = view.processView()

        self.assertIn("error_summary", result)

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.log")
    def test_empty_password(self, mock_log, mock_reset_key_exists):
        # Test case where the provided password is empty
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "test_user",
            "token": "test_token",
            "password": "",
            "password2": "",
            "email": "test@example.com",
            "user_name": "test_username",
        }
        with patch("climmob.views.basic_views.check_csrf_token", return_value=True):
            with patch(
                "climmob.views.basic_views.getUserData",
                return_value=MagicMock(
                    userData={
                        "user_password_reset_key": "test_reset_key",
                        "user_password_reset_token": "test_token",
                        "user_password_reset_expires_on": datetime.now()
                        + timedelta(days=1),
                    }
                ),
            ):
                with patch.object(view, "_", side_effect=lambda x: x):
                    result = view.processView()

        self.assertIn("error_summary", result)
        self.assertEqual(
            result["error_summary"], {"Error": "The password cannot be empty"}
        )
        mock_log.error.assert_called_once_with(
            "Suspicious bot password recovery from IP: {}. Agent: {}. Email: {}".format(
                self.mock_request.remote_addr,
                self.mock_request.user_agent,
                "test@example.com",
            )
        )

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.getUserData")
    def test_tokens_do_not_match(self, mock_get_user_data, mock_reset_key_exists):
        # Test case where the provided tokens do not match
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "test_user",
            "token": "wrong_token",
            "password": "new_password",
            "password2": "new_password",
            "email": "test@example.com",
            "user_name": "test_username",
        }
        with patch("climmob.views.basic_views.check_csrf_token", return_value=True):
            mock_get_user_data.return_value = MagicMock(
                userData={
                    "user_password_reset_key": "test_reset_key",
                    "user_password_reset_token": "test_token",
                    "user_password_reset_expires_on": datetime.now()
                    + timedelta(days=1),
                }
            )
            with patch.object(view, "_", side_effect=lambda x: x):
                result = view.processView()

        self.assertIn("error_summary", result)
        self.assertEqual(result["error_summary"], {"Error": "Invalid token"})

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.getUserData")
    def test_token_expired(self, mock_get_user_data, mock_reset_key_exists):
        # Test case where the provided token has expired
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "test_user",
            "token": "test_token",
            "password": "new_password",
            "password2": "new_password",
            "email": "test@example.com",
            "user_name": "test_username",
        }
        with patch("climmob.views.basic_views.check_csrf_token", return_value=True):
            mock_get_user_data.return_value = MagicMock(
                userData={
                    "user_password_reset_key": "test_reset_key",
                    "user_password_reset_token": "test_token",
                    "user_password_reset_expires_on": datetime.now()
                    - timedelta(days=1),
                }
            )
            with patch.object(view, "_", side_effect=lambda x: x):
                result = view.processView()

        self.assertIn("error_summary", result)
        self.assertEqual(result["error_summary"], {"Error": "Invalid token"})

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.getUserData")
    def test_passwords_do_not_match(self, mock_get_user_data, mock_reset_key_exists):
        # Test case where the provided passwords do not match
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "test_user",
            "token": "test_token",
            "password": "new_password",
            "password2": "different_password",
            "email": "test@example.com",
            "user_name": "test_username",
        }
        with patch("climmob.views.basic_views.check_csrf_token", return_value=True):
            mock_get_user_data.return_value = MagicMock(
                userData={
                    "user_password_reset_key": "test_reset_key",
                    "user_password_reset_token": "test_token",
                    "user_password_reset_expires_on": datetime.now()
                    + timedelta(days=1),
                }
            )
            with patch.object(view, "_", side_effect=lambda x: x):
                result = view.processView()

        self.assertIn("error_summary", result)
        self.assertEqual(
            result["error_summary"],
            {"Error": "The password and the confirmation are not the same"},
        )

    @patch("climmob.views.basic_views.resetKeyExists")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.encodeData")
    @patch("climmob.views.basic_views.resetPassword")
    def test_successful_password_reset(
        self,
        mock_reset_password,
        mock_encode_data,
        mock_get_user_data,
        mock_reset_key_exists,
    ):
        # Test case where the password reset is successful
        view = ResetPasswordView(self.mock_request)
        mock_reset_key_exists.return_value = True
        self.mock_request.method = "POST"
        self.mock_request.POST = {
            "user": "test_user",
            "token": "test_token",
            "password": "new_password",
            "password2": "new_password",
            "email": "test@example.com",
            "user_name": "test_username",
        }
        with patch("climmob.views.basic_views.check_csrf_token", return_value=True):
            mock_get_user_data.return_value = MagicMock(
                userData={
                    "user_password_reset_key": "test_reset_key",
                    "user_password_reset_token": "test_token",
                    "user_password_reset_expires_on": datetime.now()
                    + timedelta(days=1),
                    "user_name": "test_username",
                }
            )
            mock_encode_data.return_value = "encoded_password"

            with patch.object(view, "_", side_effect=lambda x: x):
                result = view.processView()

        mock_reset_password.assert_called_once_with(
            self.mock_request,
            "test_username",
            "test_reset_key",
            "test_token",
            "encoded_password",
        )
        self.assertTrue(view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.mock_request.route_url("login"))


class TestLogoutView(unittest.TestCase):
    @patch("climmob.views.basic_views.get_policy")
    def test_logout_view(self, mock_get_policy):
        mock_policy = MagicMock()
        mock_policy.forget.return_value = [("Set-Cookie", "deleted")]
        mock_get_policy.return_value = mock_policy

        mock_request = MagicMock()
        mock_request.route_url.return_value = "/home"

        response = logout_view(mock_request)

        mock_get_policy.assert_called_once_with(mock_request, "main")
        mock_policy.forget.assert_called_once_with(mock_request)
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/home")

        headers = dict(response.headers)
        self.assertIn("Set-Cookie", headers)
        self.assertEqual(headers["Set-Cookie"], "deleted")


class TestRegisterView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.registry.settings = {"auth.register_users_via_web": "true"}
        self.mock_request.POST = {}

    @patch("climmob.views.basic_views.get_policy")
    def test_register_disabled(self, mock_get_policy):
        self.mock_request.registry.settings["auth.register_users_via_web"] = "false"
        view = register_view(self.mock_request)
        with self.assertRaises(HTTPNotFound):
            view.processView()

    @patch("climmob.views.basic_views.get_policy")
    def test_user_already_logged_in(self, mock_get_policy):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = (
            '{"group": "mainApp", "login": "test_user"}'
        )
        mock_get_policy.return_value = mock_policy
        self.mock_request.route_url.return_value = "/dashboard"
        view = register_view(self.mock_request)

        with patch(
            "climmob.views.basic_views.getUserData", return_value={"login": "test_user"}
        ):
            response = view.processView()
            self.assertIsInstance(response, HTTPFound)
            self.assertEqual(response.location, "/dashboard")

    @patch("climmob.views.basic_views.valideRegisterForm")
    @patch("climmob.views.basic_views.addUser")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.getCountryList", return_value=[])
    @patch("climmob.views.basic_views.getSectorList", return_value=[])
    @patch("climmob.views.basic_views.get_policy")
    def test_registration_success(
        self,
        mock_get_policy,
        mock_get_sector_list,
        mock_get_country_list,
        mock_get_user_data,
        mock_add_user,
        mock_valide_register_form,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        self.mock_request.route_url.return_value = "/dashboard"
        mock_valide_register_form.return_value = (False, {})
        mock_add_user.return_value = (True, "User created")
        mock_get_user_data.return_value = MagicMock(check_password=lambda x, y: True)
        view = register_view(self.mock_request)

        self.mock_request.POST = {
            "submit": "Submit",
            "user_name": "test_user",
            "user_password": "password",
            "user_email": "test@example.com",
        }

        response = view.processView()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/dashboard")

    @patch("climmob.views.basic_views.valideRegisterForm")
    @patch("climmob.views.basic_views.getCountryList", return_value=[])
    @patch("climmob.views.basic_views.getSectorList", return_value=[])
    @patch("climmob.views.basic_views.get_policy")
    def test_registration_form_errors(
        self,
        mock_get_policy,
        mock_get_sector_list,
        mock_get_country_list,
        mock_valide_register_form,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        self.mock_request.route_url.return_value = "/dashboard"
        mock_valide_register_form.return_value = (True, {"error": "validation error"})
        view = register_view(self.mock_request)

        self.mock_request.POST = {
            "submit": "Submit",
            "user_name": "test_user",
            "user_password": "password",
            "user_email": "test@example.com",
        }

        response = view.processView()
        self.assertIsInstance(response, dict)
        self.assertIn("error_summary", response)
        self.assertIn("error", response["error_summary"])

    @patch("climmob.views.basic_views.valideRegisterForm")
    @patch("climmob.views.basic_views.addUser")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.getCountryList", return_value=[])
    @patch("climmob.views.basic_views.getSectorList", return_value=[])
    @patch("climmob.views.basic_views.get_policy")
    def test_user_policy_true(
        self,
        mock_get_policy,
        mock_get_sector_list,
        mock_get_country_list,
        mock_get_user_data,
        mock_add_user,
        mock_valide_register_form,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        self.mock_request.route_url.return_value = "/dashboard"
        mock_valide_register_form.return_value = (False, {})
        mock_add_user.return_value = (True, "User created")
        mock_get_user_data.return_value = MagicMock(check_password=lambda x, y: True)
        view = register_view(self.mock_request)

        self.mock_request.POST = {
            "submit": "Submit",
            "user_name": "test_user",
            "user_password": "password",
            "user_email": "test@example.com",
            "user_policy": "True",
        }

        response = view.processView()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/dashboard")

    @patch("climmob.views.basic_views.get_policy")
    @patch("climmob.views.basic_views.getSectorList", return_value=[])
    @patch("climmob.views.basic_views.getCountryList", return_value=[])
    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.addUser")
    @patch("climmob.views.basic_views.valideRegisterForm")
    def test_user_is_none(
        self,
        mock_valide_register_form,
        mock_add_user,
        mock_get_user_data,
        mock_get_country_list,
        mock_get_sector_list,
        mock_get_policy,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        self.mock_request.route_url.return_value = "/dashboard"
        mock_valide_register_form.return_value = (False, {})
        mock_add_user.return_value = (True, "User created")
        view = register_view(self.mock_request)

        self.mock_request.POST = {
            "submit": "Submit",
            "user_name": "test_user",
            "user_password": "password",
            "user_email": "test@example.com",
        }

        with patch.object(view, "_", return_value="User is None!"):
            response = view.processView()
            self.assertIsInstance(response, dict)
            self.assertIn("error_summary", response)
            self.assertEqual(response["error_summary"]["createError"], "User is None!")

    @patch("climmob.views.basic_views.valideRegisterForm")
    @patch("climmob.views.basic_views.addUser")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.getCountryList", return_value=[])
    @patch("climmob.views.basic_views.getSectorList", return_value=[])
    @patch("climmob.views.basic_views.get_policy")
    def test_password_mismatch(
        self,
        mock_get_policy,
        mock_get_sector_list,
        mock_get_country_list,
        mock_get_user_data,
        mock_add_user,
        mock_valide_register_form,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        self.mock_request.route_url.return_value = "/dashboard"
        mock_valide_register_form.return_value = (False, {})
        mock_add_user.return_value = (True, "User created")
        mock_get_user_data.return_value = MagicMock(check_password=lambda x, y: False)
        view = register_view(self.mock_request)

        self.mock_request.POST = {
            "submit": "Submit",
            "user_name": "test_user",
            "user_password": "password",
            "user_email": "test@example.com",
        }

        with patch.object(view, "_", return_value="Password does not match password"):
            response = view.processView()
            self.assertIsInstance(response, dict)
            self.assertIn("error_summary", response)
            self.assertIn("createError", response["error_summary"])
            self.assertEqual(
                response["error_summary"]["createError"],
                "Password does not match password",
            )

    @patch("climmob.views.basic_views.valideRegisterForm")
    @patch(
        "climmob.views.basic_views.addUser",
        return_value=(False, "User creation failed"),
    )
    @patch("climmob.views.basic_views.getCountryList", return_value=[])
    @patch("climmob.views.basic_views.getSectorList", return_value=[])
    @patch("climmob.views.basic_views.get_policy")
    def test_user_creation_failed(
        self,
        mock_get_policy,
        mock_get_sector_list,
        mock_get_country_list,
        mock_add_user,
        mock_valide_register_form,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy

        self.mock_request.route_url.return_value = "/dashboard"
        mock_valide_register_form.return_value = (False, {})
        view = register_view(self.mock_request)

        self.mock_request.POST = {
            "submit": "Submit",
            "user_name": "test_user",
            "user_password": "password",
            "user_email": "test@example.com",
        }

        with patch.object(view, "_", return_value="Unable to create user"):
            response = view.processView()
            self.assertIsInstance(response, dict)
            self.assertIn("error_summary", response)
            self.assertIn("createError", response["error_summary"])
            self.assertEqual(
                response["error_summary"]["createError"], "Unable to create user"
            )


if __name__ == "__main__":
    unittest.main()
