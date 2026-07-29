from unittest.mock import MagicMock, patch

import slack_sdk

from climmob.services.notification_service import EmailNotifier, SlackNotifier
from climmob.tests.test_utils.common import BaseTest


class NotifierBaseTest(BaseTest):
    notifier_class = None

    def setUp(self):
        super().setUp()
        self.request = MagicMock()
        self.notifier = self.notifier_class(self.request)


class TestEmailNotifier(NotifierBaseTest):
    notifier_class = EmailNotifier

    @patch("climmob.services.notification_service.EmailSender")
    def setUp(self, mock_email_sender):
        super().setUp()
        self.request.registry.settings = {"email.from": "noreply@example.com"}

        self.mock_context = {
            "project": {
                "project_name": "Test Project Name",
                "owner": {"user_name": "test_user_name"},
            }
        }

    @patch("climmob.services.notification_service.EmailBuilder")
    def test_send_notification_success(self, mock_email_builder):
        notifier = self.notifier
        notifier._to = [
            {"user_fullname": "Alice", "user_email": "alice@test.com"},
            {"user_fullname": "Bob", "user_email": "bob@test.com"},
        ]

        mock_builder_instance = mock_email_builder.return_value
        mock_builder_instance.build.return_value = "Constructed Email Body"

        notifier.send_notification()

        mock_email_builder.assert_called_once_with(
            self.request.registry.settings,
            notifier._to,
            notifier._subject,
            notifier._template,
            notifier._context,
        )
        notifier.sender.send_email.assert_called_once_with(
            ["alice@test.com", "bob@test.com"], "Constructed Email Body"
        )

    @patch("climmob.services.notification_service.EmailBuilder")
    def test_send_notification_fails_without_msg(self, mock_email_builder):
        notifier = self.notifier
        notifier._to = MagicMock(list)

        mock_builder_instance = mock_email_builder.return_value
        mock_builder_instance.build.return_value = None

        result = notifier.send_notification()

        self.assertFalse(result)
        notifier.sender.send_email.assert_not_called()

    @patch("climmob.services.notification_service.getAllUserAdmin")
    def test_notify_publication_request(self, mock_get_all_user_admin):
        notifier = self.notifier
        notifier.send_notification = MagicMock()
        mock_get_all_user_admin.return_value = MagicMock(list, name="admin_users")

        notifier.notify_publication_request(self.mock_context)

        self.assertEqual(
            notifier._template, "email/publication/publication_request_admin.jinja2"
        )
        self.assertEqual(
            notifier._subject, "New publication request for project: Test Project Name"
        )
        self.assertEqual(notifier._to, mock_get_all_user_admin.return_value)
        mock_get_all_user_admin.assert_called_once_with(self.request)
        notifier.send_notification.assert_called_once()

    @patch("climmob.services.notification_service.getUserData")
    def test_notify_publication_rejection(self, mock_get_user_data):
        notifier = self.notifier
        notifier.send_notification = MagicMock()

        mock_user = MagicMock()
        mock_user.login = MagicMock(str, name="test_user_login")
        mock_user.email = MagicMock(str, name="test_email")
        mock_get_user_data.return_value = mock_user

        notifier.notify_publication_rejection(self.mock_context)

        self.assertEqual(
            notifier._template, "email/publication/publication_rejection.jinja2"
        )
        self.assertEqual(
            notifier._subject, "Publication request rejected for: Test Project Name"
        )
        self.assertEqual(
            notifier._to,
            [{"user_fullname": mock_user.login, "user_email": mock_user.email}],
        )
        mock_get_user_data.assert_called_once_with("test_user_name", self.request)
        notifier.send_notification.assert_called_once()

    @patch("climmob.services.notification_service.getUserData")
    def test_notify_publication_success(self, mock_get_user_data):
        notifier = self.notifier
        notifier.send_notification = MagicMock()

        mock_user = MagicMock()
        mock_user.login = MagicMock(str, name="test_user_login")
        mock_user.email = MagicMock(str, name="test_email")
        mock_get_user_data.return_value = mock_user

        notifier.notify_publication_success(self.mock_context)

        self.assertEqual(
            notifier._template, "email/publication/publication_success.jinja2"
        )
        self.assertEqual(
            notifier._subject, "Publication completed for: Test Project Name"
        )
        self.assertEqual(
            notifier._to,
            [{"user_fullname": mock_user.login, "user_email": mock_user.email}],
        )
        mock_get_user_data.assert_called_once_with("test_user_name", self.request)
        notifier.send_notification.assert_called_once()


class TestSlackNotifier(NotifierBaseTest):
    notifier_class = SlackNotifier

    @patch("climmob.services.notification_service.slack_sdk.WebClient")
    def setUp(self, mock_web_client):
        super().setUp()

        self.request.registry.settings = {"slack.token": "xoxo-dummy-token-123"}

        self.mock_client = mock_web_client.return_value

    def test_init_configures_client_and_properties(self):
        self.assertEqual(self.notifier.channel, "#climmob-notifications")
        self.assertEqual(self.notifier.client, self.mock_client)
        self.assertIsNone(self.notifier.text)
        self.assertIsNone(self.notifier.blocks)
        self.assertIsNone(self.notifier.attachments)

    def test_send_notification_success(self):
        self.notifier.text = "Hello Slack"
        self.notifier.attachments = [{"color": "#D00000"}]

        self.notifier.send_notification()

        self.mock_client.chat_postMessage.assert_called_once_with(
            channel="#climmob-notifications",
            text="Hello Slack",
            attachments=[{"color": "#D00000"}],
        )

    @patch("climmob.services.notification_service.log")
    def test_send_notification_handles_slack_api_error(self, mock_log):
        mock_response = {"error": "invalid_auth"}

        slack_error = slack_sdk.errors.SlackApiError(
            message="Slack API Error", response=mock_response
        )

        self.mock_client.chat_postMessage.side_effect = slack_error

        self.notifier.send_notification()

        mock_log.error.assert_called_once_with(
            "Slack API Rejected Request: invalid_auth"
        )

    @patch("climmob.services.notification_service.log")
    def test_send_notification_handles_unexpected_exception(self, mock_log):
        self.mock_client.chat_postMessage.side_effect = Exception(
            "Connection timed out"
        )

        self.notifier.send_notification()

        mock_log.error.assert_called_once_with(
            "An unexpected Python error occurred: Connection timed out"
        )

    def test_notify_publication_failure_constructs_payload_correctly(self):
        self.notifier.send_notification = MagicMock()

        dummy_context = {
            "project": {
                "owner": {"user_name": "john_doe"},
                "project_cod": "PRJ-99",
                "project_id": 456,
            },
            "repositories": [
                {"destination": "Genesys", "msg": "File not found"},
                {"destination": "Zenodo", "msg": "Timeout"},
            ],
        }

        expected_markdown = (
            "Project john_doe_PRJ-99(456) failed to publish on the following repositories:\n"
            "\t• Genesys: File not found\n"
            "\t• Zenodo: Timeout"
        )

        self.notifier.notify_publication_failure(dummy_context)

        self.assertEqual(self.notifier.text, "Project publication failure!")

        self.assertEqual(len(self.notifier.blocks), 1)
        self.assertEqual(self.notifier.blocks[0]["type"], "section")
        self.assertEqual(self.notifier.blocks[0]["text"]["type"], "mrkdwn")
        self.assertEqual(self.notifier.blocks[0]["text"]["text"], expected_markdown)

        self.assertEqual(
            self.notifier.attachments,
            [{"color": "#D00000", "blocks": self.notifier.blocks}],
        )

        self.notifier.send_notification.assert_called_once()
