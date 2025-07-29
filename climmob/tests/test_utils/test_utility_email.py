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
