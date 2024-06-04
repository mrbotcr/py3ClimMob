import unittest
import secrets
from unittest.mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.views.basic_views import render_template
from climmob.views.basic_views import (
    home_view,
    HealthView,
    TermsView,
    PrivacyView,
    notfound_view,
    StoreCookieView
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

        view = home_view(mock_public_view)
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

        view = home_view(mock_public_view)
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
        view = notfound_view(self.mock_request)

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


if __name__ == '__main__':
    unittest.main()
