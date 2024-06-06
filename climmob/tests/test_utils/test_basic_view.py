import unittest
import secrets
from unittest.mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from unittest.mock import patch, MagicMock
from pyramid.testing import DummyRequest

from climmob.views.basic_views import render_template
from climmob.views.basic_views import (
    HomeView,
    HealthView,
    TermsView,
    PrivacyView,
    NotfoundView,
    StoreCookieView,
    get_policy,
    LoginView,
    RecoverPasswordView
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
    def test_process_view_without_cookies(self, mock_getProjectCount, mock_getUserCount):
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
        self.mock_engine.pool.status.return_value = 'Pool status info'
        self.mock_request.dbsession.get_bind.return_value = self.mock_engine

    def test_process_view_success(self):
        self.mock_request.dbsession.execute.return_value.fetchone.return_value = ('Threads_connected', 5)
        view = HealthView(self.mock_request)
        result = view.processView()
        self.assertEqual(result['health']['pool'], 'Pool status info')
        self.assertEqual(result['health']['threads_connected'], 5)

    def test_process_view_exception(self):
        self.mock_request.dbsession.execute.side_effect = Exception('Database error')
        view = HealthView(self.mock_request)
        result = view.processView()
        self.assertEqual(result['health']['pool'], 'Pool status info')
        self.assertEqual(result['health']['threads_connected'], 'Database error')

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
        view = NotfoundView(self.mock_request)

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
        self.assertIn("climmob_cookie_question=accept", response.headers.get("Set-Cookie", ""))

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
        self.assertIn("climmob_cookie_question=accept", response.headers.get("Set-Cookie", ""))

class TestGetPolicy(unittest.TestCase):

    # Enable the settings
    def setUp(self):
        self.mock_request = MagicMock()

    # Test when the policy exists
    def test_policy_exists(self):
        policies = [
            {"name": "policy1", "policy": "Policy Content 1"},
            {"name": "policy2", "policy": "Policy Content 2"}
        ]
        self.mock_request.policies.return_value = policies

        result = get_policy(self.mock_request, "policy1")
        self.assertEqual(result, "Policy Content 1")

    # Test when the policy does not exist
    def test_policy_does_not_exist(self):
        policies = [
            {"name": "policy1", "policy": "Policy Content 1"},
            {"name": "policy2", "policy": "Policy Content 2"}
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
    @patch('climmob.views.basic_views.get_policy')
    @patch('climmob.views.basic_views.literal_eval')
    @patch('climmob.views.basic_views.getUserData')
    def test_process_view_logged_in(self, mock_getUserData, mock_literal_eval, mock_get_policy):
        # Set up cookies and policy mocks
        self.mock_request.cookies = {"climmob_cookie_question": "accept"}
        policy = MagicMock()
        policy.authenticated_userid.return_value = "{'login': 'test_user', 'group': 'mainApp'}"
        mock_get_policy.return_value = policy
        mock_literal_eval.return_value = {"login": "test_user", "group": "mainApp"}
        mock_getUserData.return_value = {"id": 1, "name": "Test User"}
        self.mock_request.route_url.return_value = "/dashboard"

        result = self.view.processView()

        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "/dashboard")
        self.assertTrue(self.view.returnRawViewResult)

    # Test for when the user is not authenticated
    @patch('climmob.views.basic_views.get_policy')
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
    @patch('climmob.views.basic_views.get_policy')
    @patch('climmob.views.basic_views.getUserData')
    @patch('climmob.views.basic_views.remember')
    def test_process_view_login_success(self, mock_remember, mock_getUserData, mock_get_policy):
        self.mock_request.cookies = {}
        self.mock_request.POST = {"submit": "submit", "login": "test_user", "passwd": "correct_password"}
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
    @patch('climmob.views.basic_views.get_policy')
    @patch('climmob.views.basic_views.getUserData')
    def test_process_view_login_failure(self, mock_getUserData, mock_get_policy):
        self.mock_request.cookies = {}
        self.mock_request.POST = {"submit": "submit", "login": "test_user", "passwd": "wrong_password"}
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
        # Crear un objeto request simulado
        self.mock_request = MagicMock()
        self.mock_request.registry.settings = {
            'email.server': 'smtp.test.com',
            'email.user': 'user',
            'email.password': 'password',
            'email.from': 'no-reply@example.com'
        }
        self.mock_request.route_url.return_value = 'http://example.com/reset_password'
        self.mock_request.translate = lambda x: x

    @patch('climmob.views.basic_views.smtplib.SMTP')
    def test_send_password_by_email_success(self, mock_smtp):
        view = RecoverPasswordView(self.mock_request)

        view.send_password_by_email(
            body="Test email body",
            target_name="Test User",
            target_email="test@example.com",
            mail_from="no-reply@example.com"
        )

        mock_smtp.assert_called_with('smtp.test.com', 587)
        mock_smtp_instance = mock_smtp.return_value
        mock_smtp_instance.ehlo.assert_called()
        mock_smtp_instance.starttls.assert_called()
        mock_smtp_instance.login.assert_called_with('user', 'password')
        mock_smtp_instance.sendmail.assert_called()
        mock_smtp_instance.quit.assert_called()

    @patch('climmob.views.basic_views.render_template')
    @patch('climmob.views.basic_views.readble_date')
    @patch('climmob.views.basic_views.getUserByEmail')
    @patch('climmob.views.basic_views.setPasswordResetToken')
    def test_send_password_email(self, mock_set_token, mock_get_user, mock_readble_date, mock_render_template):
        view = RecoverPasswordView(self.mock_request)

        mock_user = MagicMock()
        mock_user.fullName = 'Test User'
        mock_user.email = 'test@example.com'
        mock_get_user.return_value = (mock_user, 'password')

        mock_readble_date.return_value = 'June 6, 2024'
        mock_render_template.return_value = 'Rendered Email Content'

        view.send_password_email(
            email_to='test@example.com',
            reset_token='test_token',
            reset_key='test_key',
            user_dict=mock_user
        )

        mock_render_template.assert_called_with(
            'email/recover_email.jinja2',
            {
                'recovery_date': 'June 6, 2024',
                'reset_token': 'test_token',
                'user_dict': mock_user,
                'reset_url': 'http://example.com/reset_password',
                '_': self.mock_request.translate
            }
        )

    # @patch('climmob.views.basic_views.get_policy')
    # @patch('climmob.views.basic_views.getUserData')
    # @patch('climmob.views.basic_views.getUserByEmail')
    # @patch('climmob.views.basic_views.setPasswordResetToken')
    # def test_processView(self, mock_set_token, mock_get_user_by_email, mock_get_user_data, mock_get_policy):
    #     view = RecoverPasswordView(self.mock_request)
    #
    #     mock_policy = MagicMock()
    #     mock_policy.authenticated_userid.return_value = None
    #     mock_get_policy.return_value = mock_policy
    #
    #     mock_user = MagicMock()
    #     mock_user.email = 'test@example.com'
    #     mock_get_user_by_email.return_value = (mock_user, 'password')
    #     mock_get_user_data.return_value = None
    #
    #     self.mock_request.POST = {'submit': True, 'user_email': 'test@example.com'}
    #     self.mock_request.route_url.return_value = 'http://example.com/login'
    #
    #     response = view.processView()
    #
    #     mock_get_user_by_email.assert_called_with('test@example.com', self.mock_request)
    #     mock_set_token.assert_called()
    #     self.assertTrue(view.returnRawViewResult)
    #     self.assertEqual(response.status_int, 302)
    #     self.assertEqual(response.location, 'http://example.com/login')


if __name__ == '__main__':
    unittest.main()
