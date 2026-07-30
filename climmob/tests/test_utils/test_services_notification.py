from unittest.mock import MagicMock, patch

from climmob.services import NotificationService
from climmob.services.notification_service import EmailNotifier, SlackNotifier
from climmob.tests.test_utils.common import ServiceBaseTest
from climmob.utility import PublicationLicenseLabel, PublicationLicense


class TestNotificationService(ServiceBaseTest):
    service_class = NotificationService

    def setUp(self):
        super().setUp()
        self.service.notifier = MagicMock(name="notifier")

    def test_set_notifier(self):
        mock_notifier = MagicMock()

        self.service.set_notifier(mock_notifier)

        mock_notifier.assert_called_once_with(self.request)
        self.assertEqual(self.service.notifier, mock_notifier.return_value)

    @patch(
        "climmob.services.notification_service.get_all_project_publication_statuses",
        return_value=[{"destination_label": "Zenodo"}],
    )
    @patch("climmob.services.notification_service.get_project_by_id")
    def test_notify_publication_request(
        self, mock_get_project, mock_get_all_project_publication_statuses
    ):
        self.service.set_notifier = MagicMock(name="set_notifier")
        project_id = "p_id"
        license_id = 1
        expected_context = {
            "project": mock_get_project.return_value,
            "repositories": "Zenodo",
            "license": PublicationLicenseLabel[
                PublicationLicense(int(license_id)).name
            ].value,
            "_": self.request.translate,
        }
        self.service.notify_publication_request(project_id, license_id)

        self.service.set_notifier.assert_called_once_with(EmailNotifier)
        self.service.notifier.notify_publication_request.assert_called_once_with(
            expected_context
        )

    def test_notify_publication_rejection(self):
        self.service.set_notifier = MagicMock(name="set_notifier")
        expected_context = MagicMock()
        self.service.notify_publication_rejection(expected_context)

        self.service.set_notifier.assert_called_once_with(EmailNotifier)
        self.service.notifier.notify_publication_rejection.assert_called_once_with(
            expected_context
        )

    def test_notify_publication_success(self):
        self.service.set_notifier = MagicMock(name="set_notifier")
        expected_context = MagicMock()
        self.service.notify_publication_success(expected_context)

        self.service.set_notifier.assert_called_once_with(EmailNotifier)
        self.service.notifier.notify_publication_success.assert_called_once_with(
            expected_context
        )

    @patch("climmob.services.notification_service.get_project_by_id")
    def test_notify_publication_failure(self, mock_get_project):
        self.service.set_notifier = MagicMock(name="set_notifier")
        project_id = "p_id"
        repositories = [{"destination": "climmob", "msg": "Invalid path"}]
        expected_context = {
            "project": mock_get_project.return_value,
            "repositories": repositories,
        }
        self.service.notify_publication_failure(project_id, repositories)

        self.service.set_notifier.assert_called_once_with(SlackNotifier)
        self.service.notifier.notify_publication_failure.assert_called_once_with(
            expected_context
        )
