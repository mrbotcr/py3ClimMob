import unittest
from unittest.mock import patch, MagicMock

from climmob.utility import *


@patch("climmob.utility.email.jinjaEnv")
class TestRenderTemplate(unittest.TestCase):
    def test_render_template(self, mock_jinja_env):
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered template"
        mock_jinja_env.get_template.return_value = mock_template

        result = render_template("dummy_template.html", {"data1": "some_data"})

        self.assertEqual(result, "rendered template")
        mock_jinja_env.get_template.assert_called_once_with("dummy_template.html")
        mock_template.render.assert_called_with({"data1": "some_data"})


class TestBuildEmailMessage(unittest.TestCase):
    def test_build_email_message(self):
        body = "This is the body test."
        subject = "Subject Test"
        target_name = "target_name_test"
        target_email = "target@example.com"
        mail_from = "from@example.com"

        msg = build_email_message(body, subject, target_name, target_email, mail_from)
        self.assertIn("Subject", msg)
        self.assertIn("From", msg)
        self.assertIn("To", msg)
        self.assertIn("Date", msg)

        self.assertEqual(msg["From"], "ClimMob <from@example.com>")
        self.assertIn("target_name_test", msg["To"])
        self.assertIn("target@example.com", msg["To"])
        self.assertEqual(msg.get_payload(decode=True).decode("utf-8"), body)


class TestBuildEmailMessageMultipleRecipients(unittest.TestCase):
    def test_build_email_message_multiple_recipients(self):
        body = "This is the body test."
        subject = "Subject Test"
        recipients = [("target_name_test", "target@example.com")]
        mail_from = "from@example.com"

        msg = build_email_message_multiple_recipients(
            body, subject, recipients, mail_from
        )
        self.assertIn("Subject", msg)
        self.assertIn("From", msg)
        self.assertIn("To", msg)
        self.assertIn("Date", msg)

        self.assertEqual(msg["From"], "ClimMob <from@example.com>")
        self.assertIn("target_name_test", msg["To"])
        self.assertIn("target@example.com", msg["To"])
        self.assertEqual(msg.get_payload(decode=True).decode("utf-8"), body)


class TestEmailSender(unittest.TestCase):
    def setUp(self):
        super().setUp()

        self.translate = MagicMock()
        self.registry = MagicMock()
        self.registry.settings = {
            "email.server": MagicMock(str, name="email_server"),
            "email.port": 587,
            "email.user": MagicMock(str, name="email_user"),
            "email.password": MagicMock(str, name="email_password"),
            "email.default_sender": MagicMock(str, name="email_from"),
        }

        self.email_sender = EmailSender(self.registry.settings)

        self.log_patcher = patch("climmob.utility.email.log")
        self.smtp_patcher = patch("climmob.utility.email.smtplib.SMTP")

        self.mock_log = self.log_patcher.start()
        self.mock_smtp = self.smtp_patcher.start()

        self.addCleanup(self.log_patcher.stop)
        self.addCleanup(self.smtp_patcher.stop)

    def tearDown(self):
        super().tearDown()

    def test_send_email_success(self):
        mock_server = MagicMock()
        self.mock_smtp.return_value = mock_server

        to_email = ["recipient@example.com"]
        msg = MagicMock()
        msg.as_string.return_value = "fake email content"

        self.email_sender.send_email(to_email, msg)

        self.mock_smtp.assert_called_once_with(
            self.registry.settings["email.server"], 587
        )
        mock_server.login.assert_called_once_with(
            self.registry.settings["email.user"],
            self.registry.settings["email.password"],
        )

        mock_server.quit.assert_called_once_with()

        self.mock_log.error.assert_not_called()

    def test_send_email_smtp_failure(self):
        mock_server = MagicMock()
        self.mock_smtp.return_value = mock_server

        to_email = ["recipient@example.com"]
        msg = MagicMock()
        msg.as_string.return_value = "fake email content"

        mock_server.login.side_effect = Exception("SMTP error")
        exception = self.email_sender.send_email(to_email, msg)
        self.assertFalse(exception)
        self.mock_log.error.assert_called_once_with("SMTP error")
