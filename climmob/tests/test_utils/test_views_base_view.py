import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from time import time
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import utils

from dateutil.relativedelta import relativedelta
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
    get_policy,
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
    @patch("climmob.views.basic_views.jinjaEnv")
    def test_render_template(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered"
        mock_jinja_env.get_template.return_value = mock_template
        template_filename = "template.html"
        context = {
            "recovery_date": "date_string",
            "reset_token": "reset_token",
            "user_dict": "user_dict",
            "reset_url": "reset_url",
            "_": "_",
        }
        result = render_template(template_filename, context)
        mock_jinja_env.get_template.assert_called_once_with(template_filename)
        mock_template.render.assert_called_once_with(context)
        self.assertEqual(result, "rendered")


class TestHomeView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = HomeView(self.request)

    @patch("climmob.views.basic_views.getProjectCount", return_value=8)
    @patch("climmob.views.basic_views.getUserCount", return_value=2)
    def test_process_view_home_view_cookie_none(
        self, mock_getUserCount, mock_getProjectCount
    ):
        self.request.cookies = {}
        result = self.view.processView()
        self.assertEqual(
            result, {"numUsers": 2, "numProjs": 8, "ask_for_cookies": True}
        )
        mock_getUserCount.assert_called_once_with(self.request)
        mock_getProjectCount.assert_called_once_with(self.request)

    @patch("climmob.views.basic_views.getProjectCount", return_value=8)
    @patch("climmob.views.basic_views.getUserCount", return_value=2)
    def test_process_view_cookie_true(self, mock_getUserCount, mock_getProjectCount):
        self.request.cookies = {"climmob_cookie_question": 1}
        result = self.view.processView()
        self.assertEqual(
            result, {"numUsers": 2, "numProjs": 8, "ask_for_cookies": False}
        )
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
        self.mock_dbsession.execute.assert_called_once_with(
            "show status like 'Threads_connected%'"
        )
        self.mock_result.fetchone.assert_called_once()
        self.assertEqual(
            result,
            {
                "health": {
                    "pool": "Pool status OK",
                    "threads_connected": 12,
                }
            },
        )

    def test_process_view_health_view_exception(self):
        self.mock_dbsession.execute.side_effect = Exception("Database error")
        result = self.view.processView()
        self.mock_dbsession.get_bind.assert_called_once()
        self.assertEqual(
            result,
            {
                "health": {
                    "pool": "Pool status OK",
                    "threads_connected": "Database error",
                }
            },
        )


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
        self.assertEqual(
            context.exception.explanation, "The resource could not be found."
        )

    def test_process_view_store_cookie_view_success(self):
        self.request.route_url.return_value = "home"
        self.request.params.get.return_value = "next"
        self.request.POST = "accept"
        with patch.object(HTTPFound, "set_cookie", autospec=True) as mock_set_cookie:
            result = self.view.processView()
            self.assertIsInstance(result, HTTPFound)
            self.assertEqual(result.status_code, 302)
            self.assertEqual(result.location, "next")
            mock_set_cookie.assert_called_once_with(
                result, "climmob_cookie_question", "accept", max_age=31536000
            )


class TestGetPolicy(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()

    def test_process_view_get_policy_found(self):
        self.request.policies.return_value = [
            {"name": "Trust", "policy": "Trust on this process"}
        ]
        result = get_policy(self.request, "Trust")
        self.assertEqual(result, "Trust on this process")

    def test_process_view_get_policy_no_found(self):
        self.request.policies.return_value = [
            {"name": "Forbidden", "policy": "Trust on this process"}
        ]
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
    def test_process_view_login_no_cookies_no_login_data_no_submit_dataw(
        self, mock_get_policy
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.params.get.return_value = "next"
        self.request.POST = {}
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "login": "",
                "failed_attempt": False,
                "next": "next",
                "ask_for_cookies": True,
            },
        )

    @patch(
        "climmob.views.basic_views.getUserData",
        return_value=({"user_email": "climmob@climmob.com"}),
    )
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_cookies_login_data(
        self, mock_get_policy, mock_get_user_data
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = (
            "{'login': 'user_test', 'group': 'mainApp'}"
        )
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.cookies = {"climmob_cookie_question": True}
        self.request.route_url.return_value = "dashboard"
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "dashboard")

    @patch("climmob.views.basic_views.remember")
    @patch(
        "climmob.views.basic_views.getUserData", return_value=({"user_name": "climmob"})
    )
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_no_cookies_no_login_data_submit_dataw(
        self, mock_get_policy, mock_get_user_data, mock_remember
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.params.get.return_value = "next"
        self.request.POST = {
            "submit": True,
            "login": "LOGIN_USER",
            "passwd": "PASS_USER",
        }
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        mock_get_user_data.return_value = mock_user
        result = self.view.processView()
        mock_get_policy.assert_called_once_with(self.request, "main")
        mock_get_user_data.assert_called_once_with("LOGIN_USER", self.request)
        mock_remember.assert_called_once_with(
            self.request,
            "{'login': 'LOGIN_USER', 'group': 'mainApp'}",
            policies=["main"],
        )
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "next")

    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_login_no_cookies_no_login_data_submit_no_user(
        self, mock_get_policy, mock_get_user_data
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        self.request.policy = MagicMock()
        self.request.policy.authenticated_userid.return_value = None
        self.request.params.get.return_value = "next"
        self.request.POST = {
            "submit": True,
            "login": "LOGIN_USER",
            "passwd": "PASS_USER",
        }
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "login": "LOGIN_USER",
                "failed_attempt": True,
                "next": "next",
                "ask_for_cookies": True,
            },
        )


class TestRecoverPasswordView(unittest.TestCase):
    @patch("climmob.views.basic_views.smtplib.SMTP")
    def test_send_password_by_email_success(self, mock_smtp_server):
        self.request = MagicMock()
        mock_server = MagicMock()
        mock_smtp_server.return_value = mock_server
        body = "THIS_IS_THE_BODY_OF_THE_EMAIL_TEST"
        subject = "SUBJECT_TEST_EMAIL"
        target_name = "YOUR_EMAIL"
        target_email = "YOUR_EMAIL@CLIMMOB.COM"
        mail_from = "TEST@CLIMMOB.COM"
        msg = build_email_message(body, subject, target_name, target_email, mail_from)

        self.view = RecoverPasswordView(self.request)
        self.view.send_password_by_email(
            body, subject, target_name, target_email, mail_from
        )
        mock_smtp_server.assert_called_once()
        mock_server.sendmail.assert_called_once_with(
            mail_from, [target_email], msg.as_string()
        )
        self.assertIn("Subject", mock_server.sendmail.call_args[0][2])

    @patch("climmob.views.basic_views.print")
    @patch("climmob.views.basic_views.smtplib.SMTP")
    def test_send_password_by_email_fail(self, mock_smtp_server, mock_print):
        self.request = MagicMock()
        mock_smtp_server.side_effect = Exception("Connection failed")
        body = "THIS_IS_THE_BODY_OF_THE_EMAIL_TEST"
        subject = "SUBJECT_TEST_EMAIL"
        target_name = "YOUR_EMAIL"
        target_email = "YOUR_EMAIL@CLIMMOB.COM"
        mail_from = "TEST@CLIMMOB.COM"

        self.view = RecoverPasswordView(self.request)
        self.view.send_password_by_email(
            body, subject, target_name, target_email, mail_from
        )
        mock_smtp_server.assert_called_once()
        mock_print.assert_called_with("Connection failed")

    @patch("climmob.views.basic_views.log.error")
    def test_send_password_email_no_email(self, mock_log_error):
        self.request = MagicMock()
        self.request.registry = MagicMock()
        self.request.registry.settings = {"email.from": None}
        email_to = "YOUR_EMAIL@CLIMMOB.COM"
        reset_token = "NEW_TOKEN"
        reset_key = "RESET_KEY"
        user_dict = {"user": "USER", "password": "PASSWORD"}

        self.view = RecoverPasswordView(self.request)
        result = self.view.send_password_email(
            email_to, reset_token, reset_key, user_dict
        )
        mock_log_error.assert_called_once_with(
            "ClimMob has no email settings in place. Email service is disabled."
        )
        self.assertEqual(result, False)

    def test_send_password_email_empty_email(self):
        self.request = MagicMock()
        self.request.registry = MagicMock()
        self.request.registry.settings = {"email.from": ""}
        email_to = "YOUR_EMAIL@CLIMMOB.COM"
        reset_token = "NEW_TOKEN"
        reset_key = "RESET_KEY"
        user_dict = {"user": "USER", "password": "PASSWORD"}

        self.view = RecoverPasswordView(self.request)
        result = self.view.send_password_email(
            email_to, reset_token, reset_key, user_dict
        )
        self.assertEqual(result, False)

    @patch("climmob.views.basic_views.RecoverPasswordView.send_password_by_email")
    @patch("climmob.views.basic_views.render_template")
    @patch(
        "climmob.views.basic_views.readble_date",
        return_value=("Monday 01th of May, 2025", "en"),
    )
    def test_send_password_email_success(
        self, mock_readable_date, mock_render_template, mock_send_password_by_email
    ):
        email_to = "YOUR_EMAIL@CLIMMOB.COM"
        reset_token = "NEW_TOKEN"
        reset_key = "RESET_KEY"
        user_dict = MagicMock()
        user_dict.fullName = "FULL_NAME_USER"
        user_dict.user = "USER"
        user_dict.password = "PASSWORD"
        self.request = MagicMock()
        self.request.registry = MagicMock()
        self.request.registry.settings = {"email.from": "TEST@CLIMMOB.COM"}
        self.request.route_url = MagicMock(return_value="/reset/RESET_KEY/password")
        self.view = RecoverPasswordView(self.request)
        result = self.view.send_password_email(
            email_to, reset_token, reset_key, user_dict
        )

        mock_send_password_by_email.assert_called_once()
        mock_readable_date.assert_called_once()
        mock_render_template.assert_called_once()
        self.assertEqual(result, None)

    @patch("climmob.views.basic_views.getUserData", return_value="USER")
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_recovery_password_user_exist(
        self, mock_get_policy, mock_get_user_data
    ):
        self.request = MagicMock()
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "True"
        mock_get_policy.return_value = mock_policy
        self.view = RecoverPasswordView(self.request)
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
            self.assertEqual(context.exception.code, 404)
            self.assertEqual(
                context.exception.explanation, "The resource could not be found."
            )
        mock_get_policy.assert_called_once_with(self.request, "main")
        mock_get_user_data.assert_called_once_with("True", self.request)

    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_recovery_password_user_no_exist_submit_it_no_email(
        self, mock_get_policy, mock_get_user_data
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "True"
        mock_get_policy.return_value = mock_policy
        self.request = MagicMock()
        self.view = RecoverPasswordView(self.request)
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.request.POST = {"submit": "1", "user_email": None}

        response = self.view.processView()
        mock_get_policy.assert_called_once_with(self.request, "main")
        mock_get_user_data.assert_called_once_with("True", self.request)
        self.assertEqual(
            response,
            {"error_summary": {"email": "You need to provide an email address"}},
        )

    @patch("climmob.views.basic_views.getUserByEmail", return_value=(None, None))
    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_recovery_password_user_no_exist_submit_it_no_user(
        self, mock_get_policy, mock_get_user_data, mock_getUserByEmail
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "True"
        mock_get_policy.return_value = mock_policy
        self.request = MagicMock()
        self.view = RecoverPasswordView(self.request)
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.request.POST = {"submit": "1", "user_email": "YOUR_EMAIL@CLIMMOB.COM"}

        response = self.view.processView()
        mock_get_policy.assert_called_once_with(self.request, "main")
        mock_get_user_data.assert_called_once_with("True", self.request)
        self.assertEqual(
            response,
            {"error_summary": {"email": "Cannot find an user with such email address"}},
        )
        mock_getUserByEmail.assert_called_once_with(
            "YOUR_EMAIL@CLIMMOB.COM", self.request
        )

    @patch.object(RecoverPasswordView, "send_password_email", return_value=None)
    @patch("climmob.views.basic_views.setPasswordResetToken", return_value=None)
    @patch(
        "climmob.views.basic_views.getUserByEmail",
        return_value=(
            MagicMock(login="USER", email="YOUR_EMAIL@CLIMMOB.COM"),
            "PASSWORD",
        ),
    )
    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_recovery_password_success(
        self,
        mock_get_policy,
        mock_get_user_data,
        mock_get_user_by_email,
        mock_set_password_email,
        mock_send_password_reset_token,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "True"
        mock_get_policy.return_value = mock_policy

        self.request = MagicMock()
        self.view = RecoverPasswordView(self.request)
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.request.locale_name = "en"
        self.request.POST = {"submit": "1", "user_email": "YOUR_EMAIL@CLIMMOB.COM"}

        result = self.view.processView()
        self.assertEqual(result.status_code, 302)
        mock_get_policy.assert_called_once_with(self.request, "main")
        mock_get_user_data.assert_called_once_with("True", self.request)
        mock_get_user_by_email.assert_called_once_with(
            "YOUR_EMAIL@CLIMMOB.COM", self.request
        )
        mock_set_password_email.assert_called_once()
        mock_send_password_reset_token.assert_called_once()


class TestResetPasswordView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = ResetPasswordView(self.request)
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.request.method = "POST"
        self.request.matchdict = {"reset_key": "DUMMY_RESET_KEY"}
        self.view.getPostDict = MagicMock(
            return_value={
                "user": "SOME_VALUE",
                "token": "TOKEN",
                "password": "PASSWORD",
                "password2": "PASSWORD",
                "email": "EMAIL",
            }
        )
        self.request.remote_addr = "127.0.0.1"
        self.request.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

    @patch("climmob.views.basic_views.resetKeyExists", return_value=False)
    def test_process_view_reset_password_view_no_reset_key(self, mock_reset_Key_exists):
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.status_code, 404)
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")

    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_no_post(self, mock_reset_Key_exists):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response, {"error_summary": {}, "dataworking": {}})
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")

    @patch("climmob.views.basic_views.check_csrf_token", return_value=False)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_user_no_safe(
        self, mock_reset_Key_exists, mock_check_csrf_token
    ):
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.status_code, 404)
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)

    @patch("climmob.views.basic_views.getUserData", return_value=None)
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_user_no_user(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
    ):
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "dataworking": {
                    "email": "EMAIL",
                    "password": "PASSWORD",
                    "password2": "PASSWORD",
                    "token": "TOKEN",
                    "user": "SOME_VALUE",
                },
                "error_summary": {"Error": "User does not exist"},
            },
        )
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_user_invalid_Key(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": "RESET_KEY",
            "user_password_reset_token": "RESET_TOKEN",
            "user_password_reset_expires_on": datetime(2025, 5, 12, 15, 0, 0),
        }
        mock_get_user_data.return_value = mock_user
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "dataworking": {
                    "email": "EMAIL",
                    "password": "PASSWORD",
                    "password2": "PASSWORD",
                    "token": "TOKEN",
                    "user": "SOME_VALUE",
                },
                "error_summary": {"Error": "Invalid key"},
            },
        )

        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_user_invalid_token(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": "DUMMY_RESET_KEY",
            "user_password_reset_token": "RESET_TOKEN",
            "user_password_reset_expires_on": "2025-05-12 15:00:00",
        }
        mock_get_user_data.return_value = mock_user
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "dataworking": {
                    "email": "EMAIL",
                    "password": "PASSWORD",
                    "password2": "PASSWORD",
                    "token": "TOKEN",
                    "user": "SOME_VALUE",
                },
                "error_summary": {"Error": "Invalid token"},
            },
        )

        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_user_invalid_token_by_time(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": "DUMMY_RESET_KEY",
            "user_password_reset_token": "RESET_TOKEN",
            "user_password_reset_expires_on": datetime(2025, 5, 12, 15, 0, 0),
        }
        mock_get_user_data.return_value = mock_user
        self.view.getPostDict = MagicMock(
            return_value={
                "user": "SOME_VALUE",
                "token": "RESET_TOKEN",
                "password": "PASSWORD",
                "password2": "PASSWORD",
                "email": "EMAIL",
            }
        )
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "dataworking": {
                    "email": "EMAIL",
                    "password": "PASSWORD",
                    "password2": "PASSWORD",
                    "token": "RESET_TOKEN",
                    "user": "SOME_VALUE",
                },
                "error_summary": {"Error": "Invalid token"},
            },
        )
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_password_empty(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": "DUMMY_RESET_KEY",
            "user_password_reset_token": "RESET_TOKEN",
            "user_password_reset_expires_on": datetime.now() + relativedelta(hours=+1),
        }
        mock_get_user_data.return_value = mock_user
        self.view.getPostDict = MagicMock(
            return_value={
                "user": "SOME_VALUE",
                "token": "RESET_TOKEN",
                "password": "",
                "password2": "",
                "email": "EMAIL",
            }
        )
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "dataworking": {
                    "email": "EMAIL",
                    "password": "",
                    "password2": "",
                    "token": "RESET_TOKEN",
                    "user": "SOME_VALUE",
                },
                "error_summary": {"Error": "The password cannot be empty"},
            },
        )
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_pass1_different_pass2(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": "DUMMY_RESET_KEY",
            "user_password_reset_token": "RESET_TOKEN",
            "user_password_reset_expires_on": datetime.now() + relativedelta(hours=+1),
        }
        mock_get_user_data.return_value = mock_user
        self.view.getPostDict = MagicMock(
            return_value={
                "user": "SOME_VALUE",
                "token": "RESET_TOKEN",
                "password": "PASSWORD",
                "password2": "OTHER_PASSWORD",
                "email": "EMAIL",
            }
        )
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "dataworking": {
                    "email": "EMAIL",
                    "password": "PASSWORD",
                    "password2": "OTHER_PASSWORD",
                    "token": "RESET_TOKEN",
                    "user": "SOME_VALUE",
                },
                "error_summary": {
                    "Error": "The password and the confirmation are not the same"
                },
            },
        )
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.resetPassword")
    @patch("climmob.views.basic_views.encodeData", return_value="data")
    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.check_csrf_token", return_value=True)
    @patch("climmob.views.basic_views.resetKeyExists", return_value=True)
    def test_process_view_reset_password_view_success(
        self,
        mock_reset_Key_exists,
        mock_check_csrf_token,
        mock_log_error,
        mock_get_user_data,
        mock_encode_data,
        mock_reset_password,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_name": "SOME_VALUE",
            "user_password_reset_key": "DUMMY_RESET_KEY",
            "user_password_reset_token": "TOKEN",
            "user_password_reset_expires_on": datetime.now() + relativedelta(hours=+1),
        }
        mock_get_user_data.return_value = mock_user
        response = self.view.processView()
        self.assertIsInstance(response, HTTPFound)
        mock_reset_Key_exists.assert_called_once_with(self.request, "DUMMY_RESET_KEY")
        mock_check_csrf_token.assert_called_once_with(self.request, raises=False)
        mock_log_error.assert_called_once_with(
            "Suspicious bot password recovery from IP: "
            + self.request.remote_addr
            + ". Agent: "
            + self.request.user_agent
            + ". Email: EMAIL"
        )
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)
        mock_encode_data.assert_called_once_with(self.request, "PASSWORD")
        mock_reset_password.assert_called_once_with(
            self.request, "SOME_VALUE", "DUMMY_RESET_KEY", "TOKEN", "data"
        )


class TestLogOutView(unittest.TestCase):
    @patch("climmob.views.basic_views.get_policy")
    def test_logout_view_success(self, mock_get_policy):
        self.request = MagicMock()
        self.request.route_url = MagicMock(return_value="/home")
        mock_policy = MagicMock()
        mock_policy.forget.return_value = [("Forget", "Session=deleted")]
        mock_get_policy.return_value = mock_policy
        result = logout_view(self.request)
        mock_get_policy.assert_called_once_with(self.request, "main")
        self.request.route_url.assert_called_once_with("home")
        self.assertIsInstance(result, HTTPFound)


class TestRegisterView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.view = RegisterView(self.request)
        self.view.request.method = "POST"
        self.request.registry = MagicMock()
        self.request.registry.settings = {"auth.register_users_via_web": True}
        self.request.POST = {
            "submit": "1",
            "user": "SOME_VALUE",
            "user_policy": "True",
            "user_password": "<PASSWORD>",
            "user_password2": "<PASSWORD>",
            "user_name": "SOME_VALUE",
            "user_email": "YOUR_EMAIL@climmob.com",
            "CheckPolicy": "True",
            "user_fullname": "COMPLETE_SOME_VALUE",
        }

    def test_process_view_auth_via_web_no_registry(self):
        self.request.registry.settings = {"auth.register_users_via_web": "false"}
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)
        self.assertEqual(
            context.exception.explanation, "The resource could not be found."
        )

    @patch(
        "climmob.views.basic_views.getUserData",
        return_value=({"user_email": "climmob@climmob.com"}),
    )
    @patch(
        "climmob.views.basic_views.literal_eval",
        return_value={"group": "mainApp", "login": "LOGIN"},
    )
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_auth_via_web_login_data_no_none(
        self, mock_get_policy, mock_literal_eval, mock_get_user_data
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = "123456"
        mock_get_policy.return_value = mock_policy
        self.request.route_url = MagicMock(return_value="dashboard")
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "dashboard")
        mock_literal_eval.assert_called_once_with("123456")
        mock_get_user_data.assert_called_once_with("LOGIN", self.request)

    @patch(
        "climmob.views.basic_views.addUser",
        return_value=(False, "Error to create new user."),
    )
    @patch("climmob.views.basic_views.valideRegisterForm", return_value=(False, {}))
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_auth_via_web_login_data_no_create_user(
        self, mock_get_policy, mock_valid_register_form, mock_add_user
    ):
        self.request.POST = {
            "submit": "1",
            "user": "SOME_VALUE",
            "user_password": "<PASSWORD>",
            "user_password2": "<PASSWORD>",
            "user_name": "SOME_VALUE",
            "user_email": "YOUR_EMAIL@climmob.com",
            "CheckPolicy": "False",
            "user_fullname": "COMPLETE_SOME_VALUE",
        }
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        result = self.view.processView()

        self.assertEqual(result["data"]["user"], "SOME_VALUE")
        self.assertEqual(result["data"]["user_email"], "YOUR_EMAIL@climmob.com")
        self.assertEqual(result["countries"], [])
        self.assertEqual(result["sectors"], [])
        self.assertIn("createError", result["error_summary"])
        self.assertTrue(isinstance(result["error_summary"]["createError"], MagicMock))
        mock_valid_register_form.assert_called_once()
        mock_add_user.assert_called_once()

    @patch("climmob.views.basic_views.getUserData", return_value=(None))
    @patch("climmob.views.basic_views.addUser", return_value=(True, ""))
    @patch("climmob.views.basic_views.valideRegisterForm", return_value=(False, {}))
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_auth_via_web_login_data_none_user(
        self,
        mock_get_policy,
        mock_valid_register_form,
        mock_add_user,
        mock_get_user_data,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        result = self.view.processView()

        self.assertEqual(result["data"]["user"], "SOME_VALUE")
        self.assertEqual(result["data"]["user_email"], "YOUR_EMAIL@climmob.com")
        self.assertEqual(result["countries"], [])
        self.assertEqual(result["sectors"], [])
        self.assertIn("createError", result["error_summary"])
        self.assertTrue(isinstance(result["error_summary"]["createError"], MagicMock))
        mock_valid_register_form.assert_called_once()
        mock_add_user.assert_called_once()
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.addUser", return_value=(True, ""))
    @patch("climmob.views.basic_views.valideRegisterForm", return_value=(False, {}))
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_auth_via_web_login_data_bad_password(
        self,
        mock_get_policy,
        mock_valid_register_form,
        mock_add_user,
        mock_get_user_data,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        mock_user = MagicMock()
        mock_user.userData = {
            "user_name": "SOME_VALUE",
            "user_email": "YOUR_EMAIL@climmob.com",
            "user_id": 42,
            "languages": ["en", "es"],
            "technologies": ["Tech1", "Tech2"],
            "projectsByUserThatRequireSetup": ["Proj1"],
            "user_password": "PASSWORD",
        }
        mock_get_user_data.return_value = mock_user
        mock_user.check_password.return_value = False
        result = self.view.processView()
        self.assertEqual(result["data"]["user"], "SOME_VALUE")
        self.assertEqual(result["data"]["user_email"], "YOUR_EMAIL@climmob.com")
        self.assertEqual(result["countries"], [])
        self.assertEqual(result["sectors"], [])
        self.assertIn("createError", result["error_summary"])
        self.assertTrue(isinstance(result["error_summary"]["createError"], MagicMock))
        mock_valid_register_form.assert_called_once()
        mock_add_user.assert_called_once()
        mock_add_user.assert_called_once()
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    @patch("climmob.views.basic_views.getUserData")
    @patch("climmob.views.basic_views.addUser", return_value=(True, ""))
    @patch("climmob.views.basic_views.valideRegisterForm", return_value=(False, {}))
    @patch("climmob.views.basic_views.get_policy")
    def test_process_view_auth_via_web_login_data_success(
        self,
        mock_get_policy,
        mock_valid_register_form,
        mock_add_user,
        mock_get_user_data,
    ):
        mock_policy = MagicMock()
        mock_policy.authenticated_userid.return_value = None
        mock_get_policy.return_value = mock_policy
        mock_user = MagicMock()
        mock_user.userData = {
            "user_name": "SOME_VALUE",
            "user_email": "YOUR_EMAIL@climmob.com",
            "user_id": 42,
            "languages": ["en", "es"],
            "technologies": ["Tech1", "Tech2"],
            "projectsByUserThatRequireSetup": ["Proj1"],
            "user_password": "PASSWORD",
        }
        mock_get_user_data.return_value = mock_user
        mock_user.check_password.return_value = True

        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        mock_valid_register_form.assert_called_once()
        mock_add_user.assert_called_once()
        mock_add_user.assert_called_once()
        mock_get_user_data.assert_called_once_with("SOME_VALUE", self.request)

    if __name__ == "__main__":
        unittest.main()
