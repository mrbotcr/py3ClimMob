import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from dateutil.relativedelta import relativedelta
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.basic_views import (
    HomeView,
    HealthView,
    NotFoundView,
    LoginView,
    RegisterView,
    LogoutView,
    RecoverPasswordView,
    ResetPasswordView,
    StoreCookieView,
    TermsView,
    PrivacyView,
    render_template,
    RefreshSessionTokensView,
)
from climmob.views.validators.session import NotLoggedInValidator


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


class TestHomeView(ViewBaseTest):
    view_class = HomeView

    @patch("climmob.views.basic_views.getProjectCount", return_value=8)
    @patch("climmob.views.basic_views.getUserCount", return_value=2)
    def test_get_home_view_cookie_none(
        self, mock_get_user_count, mock_get_project_count
    ):
        self.view.request.cookies = {}
        result = self.view.get()
        self.assertEqual(
            result, {"user_count": 2, "project_count": 8, "ask_for_cookies": True}
        )
        mock_get_user_count.assert_called_once_with(self.view.request)
        mock_get_project_count.assert_called_once_with(self.view.request)

    @patch("climmob.views.basic_views.getProjectCount", return_value=8)
    @patch("climmob.views.basic_views.getUserCount", return_value=2)
    def test_get_cookie_true(self, mock_get_user_count, mock_get_project_count):
        self.view.request.cookies = {"climmob_cookie_question": 1}
        result = self.view.get()
        self.assertEqual(
            result, {"user_count": 2, "project_count": 8, "ask_for_cookies": False}
        )
        mock_get_user_count.assert_called_once_with(self.view.request)
        mock_get_project_count.assert_called_once_with(self.view.request)


##*****##
class TestHealthView(ViewBaseTest):
    view_class = HealthView
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.mock_dbsession = MagicMock()
        self.mock_engine = MagicMock()
        self.mock_result = MagicMock()
        self.mock_engine.pool.status.return_value = "Pool status OK"
        self.mock_result.fetchone.return_value = ("Threads_connected", 12)
        self.mock_dbsession.get_bind.return_value = self.mock_engine
        self.mock_dbsession.execute.return_value = self.mock_result
        self.view.request.dbsession = self.mock_dbsession
        self.view.request.add_response_callback = MagicMock()
        self.view = HealthView(self.view.request)

    def test_get_health_view_thread_connected(self):
        result = self.view.get()
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

    def test_get_health_view_exception(self):
        self.mock_dbsession.execute.side_effect = Exception("Database error")
        result = self.view.get()
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


class TestTermsView(ViewBaseTest):
    view_class = TermsView

    def test_get_terms_view_success(self):
        result = self.view.get()
        self.assertEqual(result, {})


class TestPrivacyView(ViewBaseTest):
    view_class = PrivacyView

    def test_get_privacy_view_success(self):
        result = self.view.get()
        self.assertEqual(result, {})


class TestNotFoundView(ViewBaseTest):
    view_class = NotFoundView

    def test_get_not_found_view_success(self):
        result = self.view.get()
        self.assertEqual(result, {})
        self.assertEqual(self.view.request.response.status, 404)


class TestStoreCookieView(ViewBaseTest):
    view_class = StoreCookieView

    def test_post_store_cookie_view_success(self):
        self.view.request.cookies = {"climmob_cookie_question": 1}
        self.view.request.route_url.return_value = "home"
        self.view.request.params.get.return_value = "next"
        self.view.request.POST = "accept"
        with patch.object(HTTPFound, "set_cookie", autospec=True) as mock_set_cookie:
            result = self.view.post()
            self.assertIsInstance(result, HTTPFound)
            self.assertEqual(result.status_code, 302)
            self.assertEqual(result.location, "next")
            mock_set_cookie.assert_called_once_with(
                result, "climmob_cookie_question", "accept", max_age=31536000
            )


class TestLoginView(ViewBaseTest):
    view_class = LoginView

    def setUp(self):
        super().setUp()
        self.view.request.cookies = {}
        self.username = "test_user"

    @classmethod
    def setUpClass(cls):
        cls.patchers["getUserData"] = {
            "patch": patch(
                "climmob.views.basic_views.getUserData",
            )
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("getUserData").called:
            self.get_mock("getUserData").assert_called_once_with(
                self.username,
                self.view.request,
            )

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (NotLoggedInValidator,))

    def test_get_no_cookies_no_login_data_no_submit_data(self):
        self.view.request.params.get.return_value = "next"
        result = self.view.get()
        self.assertEqual(
            result,
            {
                "login": "",
                "failed_attempt": False,
                "next": "next",
                "ask_for_cookies": True,
            },
        )

    @patch("climmob.views.basic_views.remember")
    def test_post_success(self, mock_remember):
        self.view.request.params.get.return_value = "next"
        self.view.request.POST = {
            "submit": True,
            "login": self.username,
            "passwd": "PASS_USER",
        }
        mock_user = MagicMock()
        mock_user.check_password.return_value = True
        self.get_mock("getUserData").return_value = mock_user
        result = self.view.post()
        mock_remember.assert_called_once_with(
            self.view.request,
            "{'login': '" + self.username + "', 'group': 'mainApp'}",
            policies=["main"],
        )
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, "next")

    def test_post_success_wrong_password(self):
        self.view.request.params.get.return_value = "next"
        self.view.request.POST = {
            "submit": True,
            "login": self.username,
            "passwd": "PASS_USER",
        }
        mock_user = MagicMock()
        mock_user.check_password.return_value = False
        self.get_mock("getUserData").return_value = mock_user

        result = self.view.post()

        self.assertEqual(
            result,
            {
                "login": self.username,
                "failed_attempt": True,
                "next": "next",
                "ask_for_cookies": True,
            },
        )

    def test_post_invalid_user(self):
        self.get_mock("getUserData").return_value = None
        self.view.request.params.get.return_value = "next"
        self.view.request.POST = {
            "submit": True,
            "login": self.username,
            "passwd": "PASS_USER",
        }
        result = self.view.post()
        self.assertEqual(
            result,
            {
                "login": self.username,
                "failed_attempt": True,
                "next": "next",
                "ask_for_cookies": True,
            },
        )

    def test_is_cookie_question_set_false(self):
        result = self.view.is_cookie_question_set()

        self.assertFalse(result)

    def test_is_cookie_question_set_true(self):
        self.request.cookies = {"climmob_cookie_question": MagicMock()}
        result = self.view.is_cookie_question_set()

        self.assertTrue(result)


class TestRecoverPasswordView(ViewBaseTest):
    view_class = RecoverPasswordView

    def setUp(self):
        super().setUp()
        self.username = "test_user"
        self.email = "test_email"

    @classmethod
    def setUpClass(cls):
        cls.patchers["getUserData"] = {
            "patch": patch(
                "climmob.views.basic_views.getUserData",
            )
        }
        cls.patchers["getUserByEmail"] = {
            "patch": patch(
                "climmob.views.basic_views.getUserByEmail",
            )
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("getUserData").called:
            self.get_mock("getUserData").assert_called_once_with(
                self.username,
                self.view.request,
            )
        if self.get_mock("getUserByEmail").called:
            self.get_mock("getUserByEmail").assert_called_once_with(
                self.email, self.request
            )

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (NotLoggedInValidator,))

    @patch("climmob.views.basic_views.build_email_message")
    @patch("climmob.views.basic_views.smtplib.SMTP")
    def test_send_password_by_email_success(
        self, mock_smtp_server, mock_build_email_message
    ):
        mock_server = MagicMock()
        mock_smtp_server.return_value = mock_server
        body = MagicMock(str)
        subject = MagicMock(str)
        target_name = MagicMock(str)
        target_email = MagicMock(str)
        mail_from = MagicMock(str)

        self.view.send_password_by_email(
            body, subject, target_name, target_email, mail_from
        )
        mock_build_email_message.assert_called_once_with(
            body, subject, target_name, target_email, mail_from
        )
        mock_smtp_server.assert_called_once()
        mock_server.sendmail.assert_called_once_with(
            mail_from, [target_email], mock_build_email_message.return_value.as_string()
        )
        mock_server.quit.assert_called_once()

    @patch("climmob.views.basic_views.build_email_message")
    @patch("climmob.views.basic_views.print")
    @patch("climmob.views.basic_views.smtplib.SMTP")
    def test_send_password_by_email_fail(
        self, mock_smtp_server, mock_print, mock_build_email_message
    ):
        mock_smtp_server.side_effect = Exception("Connection failed")

        body = MagicMock(str)
        subject = MagicMock(str)
        target_name = MagicMock(str)
        target_email = MagicMock(str)
        mail_from = MagicMock(str)

        self.view.send_password_by_email(
            body, subject, target_name, target_email, mail_from
        )
        mock_smtp_server.assert_called_once()
        mock_print.assert_called_with("Connection failed")

    @patch("climmob.views.basic_views.log.error")
    @patch("climmob.views.basic_views.jinjaEnv")
    def test_send_password_email_no_email(self, mock_jinja_env, mock_log_error):
        self.request.registry = MagicMock()
        self.request.registry.settings = {"email.from": None}
        email_to = MagicMock(str)
        reset_token = MagicMock(str)
        reset_key = MagicMock(str)
        user_dict = MagicMock()

        result = self.view.send_password_email(
            email_to, reset_token, reset_key, user_dict
        )
        mock_log_error.assert_called_once_with(
            "ClimMob has no email settings in place. Email service is disabled."
        )
        self.assertEqual(result, False)

    @patch("climmob.views.basic_views.jinjaEnv")
    def test_send_password_email_empty_email(self, mock_jinja_env):
        self.request.registry = MagicMock()
        self.request.registry.settings = {"email.from": ""}
        email_to = MagicMock(str)
        reset_token = MagicMock(str)
        reset_key = MagicMock(str)
        user_dict = MagicMock()

        result = self.view.send_password_email(
            email_to, reset_token, reset_key, user_dict
        )
        self.assertEqual(result, False)

    @patch("climmob.views.basic_views.RecoverPasswordView.send_password_by_email")
    @patch("climmob.views.basic_views.render_template")
    @patch("climmob.views.basic_views.datetime")
    @patch("climmob.views.basic_views.readble_date")
    def test_send_password_email_success(
        self,
        mock_readable_date,
        mock_datetime,
        mock_render_template,
        mock_send_password_by_email,
    ):
        email_to = MagicMock(str)
        reset_token = MagicMock(str)
        reset_key = MagicMock(str)
        user_dict = MagicMock()
        self.request.registry = MagicMock()
        self.request.registry.settings = {"email.from": MagicMock(str)}
        result = self.view.send_password_email(
            email_to, reset_token, reset_key, user_dict
        )

        mock_send_password_by_email.assert_called_once_with(
            mock_render_template.return_value,
            "ClimMob - Password reset request",
            user_dict.fullName,
            email_to,
            self.request.registry.settings.get("email.from"),
        )
        mock_readable_date.assert_called_once_with(
            mock_datetime.datetime.now.return_value, self.request.locale_name
        )
        self.request.route_url.assert_called_once_with(
            "reset_password", reset_key=reset_key
        )
        mock_render_template.assert_called_once_with(
            "email/recover_email.jinja2",
            {
                "recovery_date": mock_readable_date.return_value,
                "reset_token": reset_token,
                "user_dict": user_dict,
                "reset_url": self.request.route_url.return_value,
                "_": self.request.translate,
            },
        )
        self.assertEqual(result, None)

    def test_get(self):
        result = self.view.get()
        self.assertEqual(result, {})

    def test_post_user_does_no_email(self):
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.request.POST = {"submit": "1", "user_email": None}

        response = self.view.post()
        self.assertEqual(
            response,
            {"error_summary": {"email": "You need to provide an email address"}},
        )

    def test_post_user_does_no_user(self):
        self.get_mock("getUserByEmail").return_value = (None, None)
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.request.POST = {"submit": "1", "user_email": self.email}

        response = self.view.post()
        self.assertEqual(
            response,
            {"error_summary": {"email": "Cannot find an user with such email address"}},
        )
        self.get_mock("getUserByEmail").assert_called_once()

    @patch.object(RecoverPasswordView, "send_password_email")
    @patch("climmob.views.basic_views.setPasswordResetToken")
    @patch("climmob.views.basic_views.uuid")
    @patch("climmob.views.basic_views.secrets")
    def test_post_success(
        self,
        mock_secrets,
        mock_uuid,
        mock_send_password_reset_token,
        mock_send_password_email,
    ):
        self.get_mock("getUserData").return_value = None
        self.get_mock("getUserByEmail").return_value = (
            MagicMock(login=self.username, email=self.email),
            "PASSWORD",
        )

        self.view._ = MagicMock(side_effect=lambda x: x)
        self.request.locale_name = "en"
        self.request.POST = {"submit": "1", "user_email": self.email}

        result = self.view.post()
        self.assertEqual(result.status_code, 302)
        self.get_mock("getUserByEmail").assert_called_once()
        mock_send_password_email.assert_called_once_with(
            self.email,
            mock_secrets.token_hex.return_value,
            str(mock_uuid.uuid4.return_value),
            self.get_mock("getUserByEmail").return_value[0],
        )
        mock_send_password_reset_token.assert_called_once_with(
            self.request,
            self.username,
            str(mock_uuid.uuid4.return_value),
            mock_secrets.token_hex.return_value,
        )


class TestResetPasswordView(ViewBaseTest):
    view_class = ResetPasswordView
    _ = MagicMock(side_effect=lambda x: x)
    request_method = "POST"

    @classmethod
    def setUpClass(cls):
        cls.patchers["resetKeyExists"] = {
            "patch": patch(
                "climmob.views.basic_views.resetKeyExists",
            ),
            "return_value": True,
        }
        cls.patchers["check_csrf_token"] = {
            "patch": patch(
                "climmob.views.basic_views.check_csrf_token",
            ),
            "return_value": True,
        }
        cls.patchers["getUserData"] = {
            "patch": patch(
                "climmob.views.basic_views.getUserData",
            ),
            "return_value": True,
        }
        cls.patchers["log.error"] = {
            "patch": patch(
                "climmob.views.basic_views.log.error",
            ),
            "return_value": True,
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("resetKeyExists").called:
            self.get_mock("resetKeyExists").assert_called_once_with(
                self.view.request, self.view.request.reset_key
            )
        if self.get_mock("check_csrf_token").called:
            self.get_mock("check_csrf_token").assert_called_once_with(
                self.view.request, raises=False
            )
        if self.get_mock("getUserData").called:
            self.get_mock("getUserData").assert_called_once_with(
                self.username, self.view.request
            )
        if self.get_mock("log.error").called:
            self.get_mock("log.error").assert_called_once_with(
                "Suspicious bot password recovery from IP: "
                + self.view.request.remote_addr
                + ". Agent: "
                + self.view.request.user_agent
                + f". Email: {self.email}"
            )

    def setUp(self):
        super().setUp()
        self.view.request.reset_key = MagicMock(str, name="reset_key")
        self.username = MagicMock(str, name="username")
        self.token = MagicMock(str, name="token")
        self.password = MagicMock(str, name="password")
        self.email = MagicMock(str, name="email")
        self.post_dict = {
            "user": self.username,
            "token": self.token,
            "password": self.password,
            "password2": self.password,
            "email": self.email,
        }
        self.view.getPostDict = MagicMock(return_value=self.post_dict)

        self.view.request.remote_addr = "127.0.0.1"
        self.view.request.user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"

    def update_post_dict(self, update):
        self.post_dict.update(update)
        self.view.getPostDict = MagicMock(return_value=self.post_dict)

    def test_get_no_reset_key(self):
        self.get_mock("resetKeyExists").return_value = False
        with self.assertRaises(HTTPNotFound) as context:
            self.view.get()
        self.assertEqual(context.exception.status_code, 404)
        self.get_mock("resetKeyExists").assert_called_once()

    def test_post_no_reset_key(self):
        self.get_mock("resetKeyExists").return_value = False
        with self.assertRaises(HTTPNotFound) as context:
            self.view.post()
        self.assertEqual(context.exception.status_code, 404)
        self.get_mock("resetKeyExists").assert_called_once()

    def test_get_success(self):
        response = self.view.get()
        self.assertEqual(response, {"error_summary": {}, "dataworking": {}})
        self.get_mock("resetKeyExists").assert_called_once()

    def test_post_user_no_safe(self):
        self.get_mock("check_csrf_token").return_value = False
        with self.assertRaises(HTTPNotFound) as context:
            self.view.post()
        self.assertEqual(context.exception.status_code, 404)
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()

    def test_post_user_no_user(self):
        self.get_mock("getUserData").return_value = None
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "dataworking": self.post_dict,
                "error_summary": {"Error": "User does not exist"},
            },
        )
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_post_user_invalid_Key(self):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": MagicMock(str, name="other_reset_key"),
            "user_password_reset_token": self.token,
            "user_password_reset_expires_on": datetime(2025, 5, 12, 15, 0, 0),
        }
        self.get_mock("getUserData").return_value = mock_user
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "dataworking": self.post_dict,
                "error_summary": {"Error": "Invalid key"},
            },
        )
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_post_user_invalid_token(self):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": self.view.request.reset_key,
            "user_password_reset_token": MagicMock(str, name="other_token"),
            "user_password_reset_expires_on": "2025-05-12 15:00:00",
        }
        self.get_mock("getUserData").return_value = mock_user
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "dataworking": self.post_dict,
                "error_summary": {"Error": "Invalid token"},
            },
        )
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_post_user_invalid_token_by_time(self):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": self.view.request.reset_key,
            "user_password_reset_token": self.token,
            "user_password_reset_expires_on": datetime(2025, 5, 12, 15, 0, 0),
        }
        self.get_mock("getUserData").return_value = mock_user
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "dataworking": self.post_dict,
                "error_summary": {"Error": "Invalid token"},
            },
        )
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_post_password_empty(self):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": self.view.request.reset_key,
            "user_password_reset_token": self.token,
            "user_password_reset_expires_on": datetime.now() + relativedelta(hours=+1),
        }
        self.get_mock("getUserData").return_value = mock_user
        self.update_post_dict({"password": "", "password2": ""})
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "dataworking": self.post_dict,
                "error_summary": {"Error": "The password cannot be empty"},
            },
        )
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_post_pass1_different_pass2(self):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_password_reset_key": self.view.request.reset_key,
            "user_password_reset_token": self.token,
            "user_password_reset_expires_on": datetime.now() + relativedelta(hours=+1),
        }
        self.get_mock("getUserData").return_value = mock_user
        other_password = MagicMock(str, name="other_password")
        self.update_post_dict({"password2": other_password})
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "dataworking": self.post_dict,
                "error_summary": {
                    "Error": "The password and the confirmation are not the same"
                },
            },
        )
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    @patch("climmob.views.basic_views.resetPassword")
    @patch("climmob.views.basic_views.encodeData", return_value="data")
    def test_post_success(
        self,
        mock_encode_data,
        mock_reset_password,
    ):
        mock_user = MagicMock()
        mock_user.userData = {
            "user_name": self.username,
            "user_password_reset_key": self.view.request.reset_key,
            "user_password_reset_token": self.token,
            "user_password_reset_expires_on": datetime.now() + relativedelta(hours=+1),
        }
        self.get_mock("getUserData").return_value = mock_user
        response = self.view.post()
        self.assertIsInstance(response, HTTPFound)
        self.get_mock("resetKeyExists").assert_called_once()
        self.get_mock("check_csrf_token").assert_called_once()
        self.get_mock("log.error").assert_called_once()
        self.get_mock("getUserData").assert_called_once()
        mock_encode_data.assert_called_once_with(
            self.view.request, self.password.strip.return_value
        )
        mock_reset_password.assert_called_once_with(
            self.view.request,
            self.username,
            self.view.request.reset_key,
            self.token,
            "data",
        )


class TestLogOutView(ViewBaseTest):
    view_class = LogoutView

    @patch.object(LogoutView, "get_policy")
    def test_get_success(self, mock_get_policy):
        self.request.route_url = MagicMock(return_value="/home")
        mock_policy = MagicMock()
        mock_policy.forget.return_value = [("Forget", "Session=deleted")]
        mock_get_policy.return_value = mock_policy
        result = self.view.get()
        mock_get_policy.assert_called_once_with("main")
        self.request.route_url.assert_called_once_with("home")
        self.assertIsInstance(result, HTTPFound)


class TestRegisterView(ViewBaseTest):
    view_class = RegisterView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.request.registry = MagicMock()
        self.view.request.registry.settings = {"auth.register_users_via_web": True}
        self.request.POST = {
            "submit": MagicMock(),
            "user_password": MagicMock(str, name="password"),
            "user_name": MagicMock(str, name="user_name"),
        }
        self.view.getPostDict = MagicMock(return_value=self.view.request.POST)
        self.view._ = self.mock_translation

    @classmethod
    def setUpClass(cls):
        cls.patchers["validate_register_form"] = {
            "patch": patch(
                "climmob.views.basic_views.validate_register_form",
            ),
            "return_value": (False, {}),
        }
        cls.patchers["add_user"] = {
            "patch": patch(
                "climmob.views.basic_views.add_user",
            ),
            "return_value": (True, ""),
        }
        cls.patchers["getUserData"] = {
            "patch": patch(
                "climmob.views.basic_views.getUserData",
            ),
            "return_value": MagicMock(),
        }
        super().setUpClass()

    def tearDown(self):
        super().tearDown()
        if self.get_mock("validate_register_form").called:
            self.get_mock("validate_register_form").assert_called_once_with(
                self.request.POST, self.view.request, self.view._
            )
        if self.get_mock("add_user").called:
            self.get_mock("add_user").assert_called_once_with(
                self.request.POST, self.view.request
            )
        if self.get_mock("getUserData").called:
            self.get_mock("getUserData").assert_called_once_with(
                self.request.POST["user_name"], self.view.request
            )

    def mock_translation(self, message, **kwargs):
        return message

    def test_has_validators(self):
        self.assertEqual(self.view.validators, (NotLoggedInValidator,))

    def test_process_view_auth_via_web_login_data_no_create_user(self):
        self.get_mock("add_user").return_value = (False, "Error to create new user.")

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "data": self.view.request.POST,
                "error_summary": {"createError": "Unable to create user"},
                "countries": [],
                "sectors": [],
            },
        )
        self.get_mock("validate_register_form").assert_called_once()
        self.get_mock("add_user").assert_called_once()

    def test_process_view_auth_via_web_login_data_none_user(self):
        self.get_mock("getUserData").return_value = None

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "data": self.view.request.POST,
                "error_summary": {"createError": "User is None!"},
                "countries": [],
                "sectors": [],
            },
        )
        self.get_mock("validate_register_form").assert_called_once()
        self.get_mock("add_user").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_process_view_auth_via_web_login_data_bad_password(self):
        mock_user = MagicMock()
        self.get_mock("getUserData").return_value = mock_user
        mock_user.check_password.return_value = False

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "data": self.view.request.POST,
                "error_summary": {
                    "createError": f"Password does not match {self.request.POST['user_password']}"
                },
                "countries": [],
                "sectors": [],
            },
        )
        self.get_mock("validate_register_form").assert_called_once()
        self.get_mock("add_user").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    def test_process_view_auth_via_web_login_data_success(self):
        mock_user = MagicMock()
        self.get_mock("getUserData").return_value = mock_user
        mock_user.check_password.return_value = True

        result = self.view.processView()

        self.assertIsInstance(result, HTTPFound)
        self.get_mock("validate_register_form").assert_called_once()
        self.get_mock("add_user").assert_called_once()
        self.get_mock("getUserData").assert_called_once()

    if __name__ == "__main__":
        unittest.main()


class TestRefreshSessionTokensView(ViewBaseTest):
    view_class = RefreshSessionTokensView
    request_method = "POST"

    def setUp(self):
        super().setUp()

    @patch("climmob.views.basic_views.check_csrf_token")
    def test_post_success(self, mock_check_csrf_token):
        authenticated_userid = MagicMock()
        authenticated_userid.return_value = MagicMock(str)
        self.view.request.policies.return_value = [
            {
                "name": "main",
                "policy": MagicMock(authenticated_userid=authenticated_userid),
            }
        ]
        mock_check_csrf_token.return_value = True
        response = self.view.post()

        authenticated_userid.assert_called_once_with(self.view.request)
        mock_check_csrf_token.assert_called_once_with(self.view.request, raises=False)

        self.assertEqual(response.status, "200 OK")

    @patch("climmob.views.basic_views.check_csrf_token")
    def test_post_auth_expired(self, mock_check_csrf_token):
        authenticated_userid = MagicMock()
        authenticated_userid.return_value = None
        self.view.request.policies.return_value = [
            {
                "name": "main",
                "policy": MagicMock(authenticated_userid=authenticated_userid),
            }
        ]
        mock_check_csrf_token.return_value = True
        response = self.view.post()

        authenticated_userid.assert_called_once_with(self.view.request)

        mock_check_csrf_token.assert_not_called()

        self.assertEqual(response.status, "401 Unauthorized")

    @patch("climmob.views.basic_views.check_csrf_token")
    def test_post_session_expired(self, mock_check_csrf_token):
        authenticated_userid = MagicMock()
        authenticated_userid.return_value = MagicMock(str)
        self.view.request.policies.return_value = [
            {
                "name": "main",
                "policy": MagicMock(authenticated_userid=authenticated_userid),
            }
        ]
        mock_check_csrf_token.return_value = False
        response = self.view.post()

        authenticated_userid.assert_called_once_with(self.view.request)

        mock_check_csrf_token.assert_called_once_with(self.view.request, raises=False)

        self.assertEqual(response.status, "401 Unauthorized")
