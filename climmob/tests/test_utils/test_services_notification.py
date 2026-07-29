from unittest.mock import MagicMock

from climmob.services import NotificationService
from climmob.services.notification_service import EmailNotifier, SlackNotifier
from climmob.tests.test_utils.common import ServiceBaseTest


class TestNotificationServiceBase(ServiceBaseTest):
    service_class = NotificationService

    def setUp(self):
        super().setUp()
        self.service.notifier = MagicMock(name="notifier")
        self.context = MagicMock(dict, name="context")

    def test_set_notifier(self):
        mock_notifier = MagicMock()

        self.service.set_notifier(mock_notifier)

        mock_notifier.assert_called_once_with(self.request)
        self.assertEqual(self.service.notifier, mock_notifier.return_value)

    def test_notify_publication_request(self):
        self.service.set_notifier = MagicMock(name="set_notifier")
        self.service.notify_publication_request(self.context)

        self.service.set_notifier.assert_called_once_with(EmailNotifier)
        self.service.notifier.notify_publication_request(self.context)

    def test_notify_publication_rejection(self):
        self.service.set_notifier = MagicMock(name="set_notifier")
        self.service.notify_publication_rejection(self.context)

        self.service.set_notifier.assert_called_once_with(EmailNotifier)
        self.service.notifier.notify_publication_rejection(self.context)

    def test_notify_publication_success(self):
        self.service.set_notifier = MagicMock(name="set_notifier")
        self.service.notify_publication_success(self.context)

        self.service.set_notifier.assert_called_once_with(EmailNotifier)
        self.service.notifier.notify_publication_success(self.context)

    def test_notify_publication_failure(self):
        self.service.set_notifier = MagicMock(name="set_notifier")
        self.service.notify_publication_failure(self.context)

        self.service.set_notifier.assert_called_once_with(SlackNotifier)
        self.service.notifier.notify_publication_failure(self.context)
