import json
import unittest
from unittest.mock import patch, MagicMock
from time import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import utils
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.views.basic_views import (
    HomeView,
    HealthView,
    NotFoundView,
    LoginView,
    RegisterView,
    logout_view,
    RecoverPasswordView,
    ResetPasswordView,
    StoreCookieView,
    TermsView,
    PrivacyView,
    render_template,
    get_policy
)

def build_email_message(body, subject, target_name, target_email, mail_from):

    msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
    ssubject = subject
    subject = Header(ssubject.encode("utf-8"), "utf-8")
    msg["Subject"] = subject
    msg["From"] = "{} <{}>".format("ClimMob", mail_from)
    recipient = "{} <{}>".format(target_name.encode("utf-8"), target_email)
    msg["To"] = Header(recipient, "utf-8")
    msg["Date"] = utils.formatdate(time())
    return msg

class TestRenderTemplate(unittest.TestCase):
    @patch('climmob.views.basic_views.jinjaEnv')
    def test_render_template(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = 'rendered'
        mock_jinja_env.get_template.return_value = mock_template
        template_filename = 'template.html'
        context = {
            "recovery_date": "date_string",
            "reset_token": "reset_token",
            "user_dict": "user_dict",
            "reset_url": "reset_url",
            "_": "_",}
        result = render_template(template_filename, context)
        mock_jinja_env.get_template.assert_called_once_with(template_filename)
        mock_template.render.assert_called_once_with(context)
        self.assertEqual(result, 'rendered')

class TestHomeView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = HomeView(self.request)

    @patch('climmob.views.basic_views.getProjectCount', return_value=8)
    @patch('climmob.views.basic_views.getUserCount', return_value=2)
    def test_process_view_home_view_cookie_none(self, mock_getUserCount, mock_getProjectCount):
        self.request.cookies = {}
        result = self.view.processView()
        self.assertEqual(result, {
            "numUsers": 2,
            "numProjs": 8,
            "ask_for_cookies": True
        })
        mock_getUserCount.assert_called_once_with(self.request)
        mock_getProjectCount.assert_called_once_with(self.request)

    @patch('climmob.views.basic_views.getProjectCount', return_value=8)
    @patch('climmob.views.basic_views.getUserCount', return_value=2)
    def test_process_view_cookie_true(self, mock_getUserCount, mock_getProjectCount):
        self.request.cookies = {"climmob_cookie_question":1}
        result = self.view.processView()
        self.assertEqual(result, {
            "numUsers": 2,
            "numProjs": 8,
            "ask_for_cookies": False
        })
        mock_getUserCount.assert_called_once_with(self.request)
        mock_getProjectCount.assert_called_once_with(self.request)

class TestHealthView(unittest.TestCase):

    def setUp(self):
        self.mock_dbsession = MagicMock()
        self.mock_engine = MagicMock()
        self.mock_result = MagicMock()
        self.mock_engine.pool.status.return_value = "Pool status OK"
        self.mock_result.fetchone.return_value = ("Threads_connected", 12)
        self.mock_dbsession.get_bind.return_value = self.mock_engine
        self.mock_dbsession.execute.return_value = self.mock_result
        self.request = MagicMock()
        self.request.dbsession = self.mock_dbsession
        self.request.add_response_callback = MagicMock()
        self.view = HealthView(self.request)

    def test_process_view_health_view_thread_connected(self):
        result = self.view.processView()
        self.mock_dbsession.get_bind.assert_called_once()
        self.mock_dbsession.execute.assert_called_once_with("show status like 'Threads_connected%'")
        self.mock_result.fetchone.assert_called_once()
        self.assertEqual(result,{"health":{
                                            "pool": "Pool status OK",
                                            "threads_connected": 12,
        }})

    def test_process_view_health_view_exception(self):
        self.mock_dbsession.execute.side_effect = Exception("Database error")
        result = self.view.processView()
        self.mock_dbsession.get_bind.assert_called_once()
        self.assertEqual(result,{"health":{
                                            "pool": "Pool status OK",
                                            "threads_connected": "Database error",
        }})

class TestTermsView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = TermsView(self.request)

    def test_process_view_terms_view_success(self):
        result = self.view.processView()
        self.assertEqual(result, {})

class TestPrivacyView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = PrivacyView(self.request)

    def test_process_view_privacy_view_success(self):
        result = self.view.processView()
        self.assertEqual(result, {})

class TestNotFoundView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = NotFoundView(self.request)

    def test_process_view_not_found_view_success(self):
        result = self.view.processView()
        self.assertEqual(result, {})
        self.assertEqual(self.request.response.status, 404)

class TestStoreCookieView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = StoreCookieView(self.request)
        self.request.method = "POST"

    def test_process_view_store_cookie_view_with_get(self):
        self.request.method = "GET"
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)
        self.assertEqual(context.exception.explanation, "The resource could not be found.")

    def test_process_view_store_cookie_view_success(self):
        self.request.route_url.return_value = "home"
        self.request.params.get.return_value = "next"
        self.request.POST = "accept"
        with patch.object(HTTPFound, 'set_cookie', autospec=True) as mock_set_cookie:
            result = self.view.processView()
            self.assertIsInstance(result, HTTPFound)
            self.assertEqual(result.status_code, 302)
            self.assertEqual(result.location, "next")
            mock_set_cookie.assert_called_once_with(
                result,
                "climmob_cookie_question",
                "accept",
                max_age=31536000
            )

class TestGetPolicy(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_process_view_get_policy_found(self):
        self.request.policies.return_value = [{"name": "Trust", "policy":"Trust on this process"}]
        result = get_policy(self.request, "Trust")
        self.assertEqual(result, "Trust on this process")

    def test_process_view_get_policy_no_found(self):
        self.request.policies.return_value = [{"name": "Forbidden", "policy":"Trust on this process"}]
        result = get_policy(self.request, "Trust")
        self.assertIsNone(result)

    def test_process_view_get_policy_empty(self):
        self.request.policies.return_value = []
        result = get_policy(self.request, "Trust")
        self.assertIsNone(result)

class TestLoginView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.cookies = {}
        self.view = LoginView(self.request)
        self.view.user = MagicMock(login="test_user")

    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_no_cookies_no_login_data_no_submit_dataw(self, mock_get_policy):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.params.get.return_value = "next"
        self.request.POST = {}
        result = self.view.processView()
        self.assertEqual(result,{"login": "",
            "failed_attempt": False,
            "next": "next",
            "ask_for_cookies": True,})

    @patch("climmob.views.basic_views.getUserData", return_value=({'user_email':'climmob@climmob.com'}))
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_cookies_login_data(self, mock_get_policy, mock_get_user_data):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "{'login': 'usuario_test', 'group': 'mainApp'}"
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.cookies = {"climmob_cookie_question":True}
        self.request.route_url.return_value = "dashboard"
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "dashboard")

    @patch("climmob.views.basic_views.remember")
    @patch("climmob.views.basic_views.getUserData", return_value=({'user_name':'climmob'}))
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_no_cookies_no_login_data_submit_dataw(self, mock_get_policy, mock_get_user_data, mock_remember):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.params.get.return_value = "next"
        self.request.POST = {
                "submit": True,
                "login": "LOGIN_USER",
                "passwd": "PASS_USER"
        }
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_get_user_data.return_value = mock_user
        result = self.view.processView()
        mock_get_policy.assert_called_once_with(self.request, "main")
        mock_get_user_data.assert_called_once_with("LOGIN_USER", self.request)
        mock_remember.assert_called_once_with(self.request, "{'login': 'LOGIN_USER', 'group': 'mainApp'}", policies=["main"] )
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "next")

    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_no_cookies_no_login_data_submit_no_user(self, mock_get_policy, mock_get_user_data):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.params.get.return_value = "next"
        self.request.POST = {
                "submit": True,
                "login": "LOGIN_USER",
                "passwd": "PASS_USER"
        }
        result = self.view.processView()
        self.assertEqual(result,{
            "login": "LOGIN_USER",
            "failed_attempt": True,
            "next": "next",
            "ask_for_cookies": True,})

class TestRecoverPasswordView(unittest.TestCase):

    @patch("climmob.views.basic_views.smtplib.SMTP")
    def test_send_password_by_email_no_success(self, mock_smtp_server):
        self.request = MagicMock()
        mock_server = MagicMock()
        mock_smtp_server.return_value = mock_server
        body = "this is the body of the email test"
        subject = "Subject test email"
        target_name = "YOUR_EMAIL"
        target_email = "YOUR_EMAIL@CLIMMOB.COM"
        mail_from = "CLIMMOB@CLIMMOB.COM"
        msg = build_email_message(body, subject, target_name, target_email, mail_from)

        self.view = RecoverPasswordView(self.request)
        self.view.send_password_by_email(body, subject, target_name, target_email, mail_from)
        mock_smtp_server.assert_called_once()
        mock_server.sendmail.assert_any_call(mail_from, [target_email],msg.as_string())
        self.assertIn("Subject", mock_server.sendmail.call_args[0][2])



if __name__ == '__main__':
    unittest.main()