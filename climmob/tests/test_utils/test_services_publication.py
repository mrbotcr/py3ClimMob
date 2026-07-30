from unittest.mock import MagicMock, patch

from climmob.services import PublicationService
from climmob.tests.test_utils.common import ServiceBaseTest
from climmob.utility import PublicationStatus, PublicationApproved


class TestPublicationService(ServiceBaseTest):
    service_class = PublicationService

    def setUp(self):
        self.project_id = MagicMock(str, name="project_id")
        self.license_id = 1

        with patch(
            "climmob.services.publication_service.p.PluginImplementations"
        ) as mock_plugins:
            # Set up a couple of default active destinations for the tests
            plugin_mock = MagicMock()
            plugin_mock.get_destination_name.return_value = "climmob"
            plugin_mock2 = MagicMock()
            plugin_mock2.get_destination_name.return_value = "zenodo"
            mock_plugins.return_value = [plugin_mock, plugin_mock2]

            super().setUp()

        self.service.request.user_in_session = "test_user"

    # ==========================================
    # Tests for _handle_license
    # ==========================================

    @patch("climmob.services.publication_service.get_project_publication_license_id")
    def test_handle_license_no_license_provided_or_existing(self, mock_get_license):
        mock_get_license.return_value = None
        success, msg, license_id = self.service._handle_license(self.project_id, None)
        self.assertFalse(success)
        self.assertEqual(msg, "no_license")
        self.assertIsNone(license_id)

    @patch("climmob.services.publication_service.save_project_publication_license")
    @patch("climmob.services.publication_service.get_project_publication_license_id")
    def test_handle_license_saves_new_license(
        self, mock_get_license, mock_save_license
    ):
        mock_get_license.return_value = None
        success, msg, license_id = self.service._handle_license(self.project_id, 2)

        self.assertTrue(success)
        self.assertEqual(license_id, 2)
        mock_save_license.assert_called_once_with(
            self.project_id, 2, self.service.request
        )

    @patch("climmob.services.publication_service.get_project_publication_license_id")
    def test_handle_license_returns_existing(self, mock_get_license):
        mock_get_license.return_value = 5
        success, msg, license_id = self.service._handle_license(self.project_id, 2)

        self.assertTrue(success)
        self.assertEqual(license_id, 5)

    # ==========================================
    # Tests for _handle_climmob_not_published
    # ==========================================

    @patch("climmob.services.publication_service.get_project_by_id")
    @patch("climmob.services.publication_service.save_project_publication_status")
    def test_handle_climmob_not_published_db_error(
        self, mock_save_status, mock_get_project
    ):
        mock_save_status.return_value = (False, "DB Error")

        success, msg = self.service._handle_climmob_not_published(
            self.project_id, ["zenodo"]
        )
        self.assertFalse(success)
        self.assertEqual(msg, "db_error")

    @patch("climmob.services.publication_service.get_project_by_id")
    @patch("climmob.services.publication_service.save_project_publication_status")
    def test_handle_climmob_not_published_success(
        self, mock_save_status, mock_get_project
    ):
        mock_save_status.return_value = (True, "")
        mock_get_project.return_value = MagicMock(dict, name="project")

        success, msg = self.service._handle_climmob_not_published(
            self.project_id, ["zenodo"]
        )
        self.assertTrue(success)
        self.service.notification_service.notify_publication_failure.assert_called_once_with(
            self.project_id,
            [
                {
                    "destination": "zenodo",
                    "msg": "ClimMob repository is in FAILED status, therefore the publication file might not exist",
                }
            ],
        )

    # ==========================================
    # Tests for _handle_climmob_status
    # ==========================================

    @patch(
        "climmob.services.publication_service.get_project_publication_status_by_destination_name"
    )
    def test_handle_climmob_status_already_published(self, mock_get_status):
        mock_get_status.return_value = {
            "publication_status_id": PublicationStatus.PUBLISHED.value
        }

        success, msg = self.service._handle_climmob_status(self.project_id, ["zenodo"])
        self.assertTrue(success)

    @patch(
        "climmob.services.publication_service.get_project_publication_status_by_destination_name"
    )
    def test_handle_climmob_status_failed(self, mock_get_status):
        mock_get_status.return_value = {
            "publication_status_id": PublicationStatus.FAILED.value
        }
        self.service._handle_climmob_not_published = MagicMock(
            return_value=(False, "handled_error")
        )

        success, msg = self.service._handle_climmob_status(self.project_id, ["zenodo"])
        self.assertFalse(success)
        self.assertEqual(msg, "handled_error")

    @patch(
        "climmob.services.publication_service.get_project_publication_status_by_destination_name"
    )
    def test_handle_climmob_status_not_exists_triggers_request(self, mock_get_status):
        mock_get_status.return_value = None
        self.service._request_repository = MagicMock()
        self.service._publish_repository = MagicMock()

        success, msg = self.service._handle_climmob_status(self.project_id, ["zenodo"])
        self.assertTrue(success)
        self.service._request_repository.assert_called_once_with(
            self.project_id, "climmob"
        )
        self.service._publish_repository.assert_called_once_with(
            self.project_id, "climmob"
        )

    # ==========================================
    # Tests for request_project_publication
    # ==========================================

    @patch("climmob.services.publication_service.get_project_publication_approved")
    def test_request_project_publication_license_failure(self, mock_approved):
        self.service._handle_license = MagicMock(
            return_value=(False, "license_error", None)
        )

        success, msg = self.service.request_project_publication(
            self.project_id, self.license_id, ["zenodo"]
        )
        self.assertFalse(success)
        self.assertEqual(msg, "license_error")

    @patch("climmob.services.publication_service.get_project_publication_approved")
    def test_request_project_publication_climmob_failure(self, mock_approved):
        self.service._handle_license = MagicMock(
            return_value=(True, "", self.license_id)
        )
        self.service._handle_climmob_status = MagicMock(
            return_value=(False, "climmob_error")
        )

        success, msg = self.service.request_project_publication(
            self.project_id, self.license_id, ["zenodo"]
        )
        self.assertFalse(success)
        self.assertEqual(msg, "climmob_error")

    @patch("climmob.services.publication_service.get_project_publication_approved")
    def test_request_project_publication_approved_workflow(self, mock_approved):
        self.service._handle_license = MagicMock(
            return_value=(True, "", self.license_id)
        )
        self.service._handle_climmob_status = MagicMock(return_value=(True, ""))
        mock_approved.return_value = PublicationApproved.APPROVED.value

        self.service._request_repository = MagicMock()
        self.service._publish_repository = MagicMock()

        success, msg = self.service.request_project_publication(
            self.project_id, self.license_id, ["zenodo"]
        )

        self.assertTrue(success)
        self.service._request_repository.assert_called_once_with(
            self.project_id, "zenodo"
        )
        self.service._publish_repository.assert_called_once_with(
            self.project_id, "zenodo"
        )
        self.service.notification_service.notify_publication_request.assert_called_once_with(
            self.project_id, self.license_id
        )

    # ==========================================
    # Tests for _request_repository
    # ==========================================

    @patch("climmob.services.publication_service.save_project_publication_status")
    def test_request_repository_active(self, mock_save_status):
        mock_save_status.return_value = (True, "Success")
        success, msg = self.service._request_repository(self.project_id, "zenodo")
        self.assertTrue(success)

    def test_request_repository_inactive(
        self,
    ):
        success, msg = self.service._request_repository(self.project_id, "invalid_repo")
        self.assertFalse(success)
        self.assertIn("is not active", msg)

    # ==========================================
    # Tests for approve_project_publication
    # ==========================================

    @patch("climmob.services.publication_service.get_all_project_publication_statuses")
    @patch("climmob.services.publication_service.save_project_publication_approved")
    def test_approve_project_publication_save_failed(
        self, mock_save_approved, mock_get_statuses
    ):
        mock_save_approved.return_value = (False, "DB connection error")

        success, errors = self.service.approve_project_publication(self.project_id)
        self.assertFalse(success)
        self.assertEqual(errors, ["DB connection error"])

    @patch("climmob.services.publication_service.get_all_project_publication_statuses")
    @patch("climmob.services.publication_service.save_project_publication_approved")
    def test_approve_project_publication_partial_errors(
        self, mock_save_approved, mock_get_statuses
    ):
        mock_save_approved.return_value = (True, "")
        mock_get_statuses.return_value = [
            {"destination": "climmob"},
            {"destination": "zenodo"},
        ]
        self.service._approve_repository = MagicMock(
            return_value=(False, "Failed to approve")
        )

        success, errors = self.service.approve_project_publication(self.project_id)
        self.assertFalse(success)
        self.assertEqual(errors, [("zenodo", "Failed to approve")])

    # ==========================================
    # Tests for reject_project_publication
    # ==========================================

    @patch("climmob.services.publication_service.get_project_publication_license_id")
    @patch("climmob.services.publication_service.get_project_by_id")
    @patch("climmob.services.publication_service.get_all_project_publication_statuses")
    @patch("climmob.services.publication_service.save_project_publication_approved")
    def test_reject_project_publication_success(
        self, mock_save_approved, mock_get_statuses, mock_get_project, mock_get_license
    ):
        mock_save_approved.return_value = (True, "")
        mock_get_statuses.return_value = [
            {"destination": "zenodo", "destination_label": "Zenodo Repository"}
        ]
        mock_get_project.return_value = {"id": 1, "name": "Test Project"}
        mock_get_license.return_value = self.license_id  # MIT

        self.service._reject_repository = MagicMock(return_value=(True, ""))

        success, errors = self.service.reject_project_publication(
            self.project_id, "Rejected by Admin"
        )

        self.assertTrue(success)
        self.assertEqual(errors, [])
        self.service.notification_service.notify_publication_rejection.assert_called_once()

    # ==========================================
    # Tests for handle_publication_approval
    # ==========================================

    @patch("climmob.services.publication_service.get_project_publication_approved")
    def test_handle_publication_approval_no_change(self, mock_approved):
        mock_approved.return_value = PublicationApproved.APPROVED.value
        self.service.approve_project_publication = MagicMock()

        self.service.handle_publication_approval(
            self.project_id, PublicationApproved.APPROVED.value, "msg"
        )
        self.service.approve_project_publication.assert_not_called()

    @patch("climmob.services.publication_service.get_project_publication_approved")
    def test_handle_publication_approval_triggers_publish(self, mock_approved):
        mock_approved.return_value = PublicationApproved.DEFAULT.value
        self.service.approve_project_publication = MagicMock(return_value=(True, []))
        self.service.publish_project = MagicMock()

        self.service.handle_publication_approval(
            self.project_id, PublicationApproved.APPROVED, "msg"
        )
        self.service.publish_project.assert_called_once_with(self.project_id)

    # ==========================================
    # Tests for publish_project & _publish_repository
    # ==========================================

    @patch("climmob.services.publication_service.publish_project")
    @patch("climmob.services.publication_service.get_all_project_publication_statuses")
    @patch("climmob.services.publication_service.get_project_by_id")
    def test_publish_project(self, mock_get_project, mock_get_statuses, mock_publish):
        mock_get_project.return_value = {
            "project_cod": "P01",
            "owner": {"user_name": "owner_user"},
            "project_curated_cropname": "Maize",
        }
        mock_get_statuses.return_value = [
            {"destination": "climmob"},
            {"destination": "zenodo"},
        ]

        self.service.publish_project(self.project_id)
        mock_publish.assert_called_once_with(
            self.project_id,
            "P01",
            "owner_user",
            "Maize",
            ["zenodo"],
            self.service.request,
        )

    @patch("climmob.services.publication_service.publish_project")
    @patch("climmob.services.publication_service.get_project_by_id")
    def test_publish_repository_active(self, mock_get_project, mock_publish):
        mock_get_project.return_value = {
            "project_cod": "P01",
            "owner": {"user_name": "owner_user"},
            "project_curated_cropname": "Maize",
        }

        success, msg = self.service._publish_repository(self.project_id, "zenodo")
        self.assertTrue(success)
        mock_publish.assert_called_once()
