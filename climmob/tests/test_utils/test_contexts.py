import json
import unittest
from unittest.mock import MagicMock, patch

from climmob.views.context.ApiContext import ApiContext
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


class TestApiContext(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.params = {"user_owner": "test_user", "project_cod": "test_project"}
        self.context = ApiContext(self.request)

    @patch("climmob.views.context.ApiContext.getTheProjectIdForOwner")
    @patch("climmob.views.context.ApiContext.get_body_from_api_request")
    def test_active_project_id_success(
        self, mock_get_body_from_api_request, mock_get_the_project_id_for_owner
    ):
        mock_get_body_from_api_request.return_value = json.dumps(self.request.params)
        mock_get_the_project_id_for_owner.return_value = "test_project_id"

        active_project_id = self.context.active_project_id

        mock_get_the_project_id_for_owner.assert_called_once_with(
            self.request.params["user_owner"],
            self.request.params["project_cod"],
            self.request,
        )
        self.assertEqual(
            active_project_id, mock_get_the_project_id_for_owner.return_value
        )

    @patch("climmob.views.context.ApiContext.getUserByApiKey")
    def test_user_success(self, mock_get_user_by_api_key):
        self.request.params["Apikey"] = MagicMock()
        user = self.context.user

        mock_get_user_by_api_key.assert_called_once_with(
            self.request.params["Apikey"], self.request
        )

        self.assertEqual(user, mock_get_user_by_api_key.return_value)

    @patch("climmob.views.context.ApiContext.getAccessTypeForProject")
    def test_access_type_success(self, mock_get_access_type_for_project):
        with patch.object(ApiContext, "user") as mock_user, patch.object(
            ApiContext, "active_project_id"
        ) as mock_active_project_id:
            access_type = self.context.access_type

        mock_get_access_type_for_project.assert_called_once_with(
            mock_user.login, mock_active_project_id, self.request
        )

        self.assertEqual(access_type, mock_get_access_type_for_project.return_value)
