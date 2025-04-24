import unittest
from unittest.mock import MagicMock, patch

from climmob.views.context.PrivateContext import PrivateContext


class TestPrivateContext(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.user = "test_user"
        self.request.project = "test_project"
        self.context = PrivateContext(self.request)

    @patch("climmob.views.context.PrivateContext.getTheProjectIdForOwner")
    def test_active_project_id_success(self, mock_getTheProjectIdForOwner):

        mock_getTheProjectIdForOwner.return_value = "test_project_id"

        active_project_id = self.context.active_project_id

        mock_getTheProjectIdForOwner.assert_called_once_with(
            self.request.user, self.request.project, self.request
        )
        self.assertEqual(active_project_id, mock_getTheProjectIdForOwner.return_value)

    @patch("climmob.views.context.PrivateContext.getTheProjectIdForOwner")
    def test_active_project_id_cache(self, mock_getTheProjectIdForOwner):
        mock_getTheProjectIdForOwner.return_value = "test_project_id"

        # First call
        active_project_id = self.context.active_project_id
        self.assertEqual(active_project_id, mock_getTheProjectIdForOwner.return_value)

        # Second call
        active_project_id = self.context.active_project_id
        self.assertEqual(active_project_id, mock_getTheProjectIdForOwner.return_value)

        # Assert database was called just once
        mock_getTheProjectIdForOwner.assert_called_once_with(
            self.request.user, self.request.project, self.request
        )
