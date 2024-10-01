import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.projectTechnologies import (
    AddProjectTechnologyView,
    ReadProjectTechnologiesView,
    ReadPossibleProjectTechnologiesView,
    DeleteProjectTechnologyView,
    AddProjectTechnologyAliasView,
    AddProjectTechnologyAliasExtraView,
    ReadProjectTechnologiesAliasView,
    ReadProjectTechnologiesAliasExtraView,
    ReadPossibleProjectTechnologiesAliasView,
)


class TestAddProjectTechnologyView(BaseViewTestCase):
    view_class = AddProjectTechnologyView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
            }
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch(
        "climmob.views.Api.projectTechnologies.addTechnologyProject",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_add(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_add_technology_project,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The technology was added correctly.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_add_technology_project.assert_called_once_with(
            1, "TECH456", self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add technologies.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)

    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_user_not_in_project(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a tech from a user that does not belong to this project.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_project_registration_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot add more technologies. You started the registry.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=False)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_exists(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no technology with that identifier.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_already_assigned(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology is already assigned to the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectTechnologies.addTechnologyProject",
        return_value=(False, "Error adding technology"),
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_error_adding_technology(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_add_technology_project,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding technology", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_add_technology_project.assert_called_once_with(
            1, "TECH456", self.view.request
        )

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = "invalid json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )


class TestReadProjectTechnologiesView(BaseViewTestCase):
    view_class = ReadProjectTechnologiesView
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user"}
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch(
        "climmob.views.Api.projectTechnologies.searchTechnologiesInProject",
        return_value=[
            {"tech_id": "TECH001", "name": "Technology 1"},
            {"tech_id": "TECH002", "name": "Technology 2"},
        ],
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_retrieval(
        self, mock_project_exists, mock_get_project_id, mock_search_technologies
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        technologies = json.loads(response.body.decode())
        self.assertEqual(len(technologies), 2)
        self.assertEqual(technologies[0]["tech_id"], "TECH001")
        self.assertEqual(technologies[1]["tech_id"], "TECH002")

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_search_technologies.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({"user_owner": "owner_user"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = "invalid json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_json_decode_error(self, mock_json_loads):
        self.view.body = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_json_loads.assert_called_once_with(self.view.body)


class TestReadPossibleProjectTechnologiesView(BaseViewTestCase):
    view_class = ReadPossibleProjectTechnologiesView
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user"}
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch(
        "climmob.views.Api.projectTechnologies.searchTechnologies",
        return_value=[
            {"tech_id": "TECH003", "name": "Possible Technology 1"},
            {"tech_id": "TECH004", "name": "Possible Technology 2"},
        ],
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_retrieval(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_search_technologies,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        technologies = json.loads(response.body.decode())
        self.assertEqual(len(technologies), 2)
        self.assertEqual(technologies[0]["tech_id"], "TECH003")
        self.assertEqual(technologies[1]["tech_id"], "TECH004")

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_search_technologies.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to get this information.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({"user_owner": "owner_user"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = "invalid json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_json_decode_error(self, mock_json_loads):
        self.view.body = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_json_loads.assert_called_once_with(self.view.body)


class TestDeleteProjectTechnologyView(BaseViewTestCase):
    view_class = DeleteProjectTechnologyView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
            }
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch(
        "climmob.views.Api.projectTechnologies.deleteTechnologyProject",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_deletion(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_delete_technology_project,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The technology has been removed from the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_delete_technology_project.assert_called_once_with(
            1, "TECH456", self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete technologies.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_registration_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot delete technologies. You have started registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=False)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_exists(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_technology_exist,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no technology with that identifier.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_assigned(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology is not assigned to the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch(
        "climmob.views.Api.projectTechnologies.deleteTechnologyProject",
        return_value=(False, "Error deleting technology"),
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_error_deleting_technology(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_delete_technology_project,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error deleting technology", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_delete_technology_project.assert_called_once_with(
            1, "TECH456", self.view.request
        )

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = "invalid json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_json_decode_error(self, mock_json_loads):
        self.view.body = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_json_loads.assert_called_once_with(self.view.body)


class TestAddProjectTechnologyAliasView(BaseViewTestCase):
    view_class = AddProjectTechnologyAliasView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
            }
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch(
        "climmob.views.Api.projectTechnologies.AddAliasTechnology",
        return_value=(True, "Alias added successfully"),
    )
    @patch("climmob.views.Api.projectTechnologies.getAliasAssigned", return_value=False)
    @patch("climmob.views.Api.projectTechnologies.existAlias", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_add_alias(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_exist_alias,
        mock_get_alias_assigned,
        mock_add_alias_technology,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Alias added successfully", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_exist_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_get_alias_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            1,
            self.view.request,
        )
        mock_add_alias_technology.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add technology options.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)

    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_user_not_in_project(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a technology alias from a user that does not belong to this project.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_registration_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not add an technology option for technologies. You have already started registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectTechnologies.AddAliasTechnology",
        return_value=(False, "Error adding alias"),
    )
    @patch("climmob.views.Api.projectTechnologies.getAliasAssigned", return_value=False)
    @patch("climmob.views.Api.projectTechnologies.existAlias", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_error_adding_alias(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_exist_alias,
        mock_get_alias_assigned,
        mock_add_alias_technology,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding alias", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_exist_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_get_alias_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            1,
            self.view.request,
        )
        mock_add_alias_technology.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectTechnologies.existAlias", return_value=False)
    @patch("climmob.views.Api.projectTechnologies.getAliasAssigned", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_alias_not_exists(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_get_alias_assigned,
        mock_exist_alias,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no technology option with that identifier for this technology.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_exist_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_get_alias_assigned.assert_not_called()

    @patch("climmob.views.Api.projectTechnologies.getAliasAssigned", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.existAlias", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_alias_already_assigned(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_exist_alias,
        mock_get_alias_assigned,
    ):
        mock_get_alias_assigned.return_value = True

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology option has not been assigned to the project.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_exist_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_get_alias_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_id": "ALIAS789",
                "user_name": "test_user",
                "project_id": 1,
            },
            1,
            self.view.request,
        )

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user", "tech_id": "TECH456"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


class TestAddProjectTechnologyAliasExtraView(unittest.TestCase):
    def setUp(self):
        self.view = AddProjectTechnologyAliasExtraView(MagicMock())
        self.view.request.method = "POST"
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
            }
        )
        self.view.request.json_body = json.loads(self.view.body)
        self.view.user = MagicMock(login="test_user")
        self.view._ = lambda x: x

    @patch(
        "climmob.views.Api.projectTechnologies.addTechAliasExtra",
        return_value=(True, "Alias extra added successfully"),
    )
    @patch("climmob.views.Api.projectTechnologies.findTechAlias", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_add_extra_alias(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_find_tech_alias,
        mock_add_tech_alias_extra,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Alias extra added successfully", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_find_tech_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_add_tech_alias_extra.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add technology options.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)

    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_user_not_in_project(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a technology alias extra from a user that does not belong to this project.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_registration_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not add technology option for technologies. You have already started registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectTechnologies.addTechAliasExtra",
        return_value=(False, "Error adding alias extra"),
    )
    @patch("climmob.views.Api.projectTechnologies.findTechAlias", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_error_adding_alias_extra(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_find_tech_alias,
        mock_add_tech_alias_extra,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding alias extra", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_find_tech_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_add_tech_alias_extra.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectTechnologies.findTechAlias", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_alias_extra_already_exists(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_find_tech_alias,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This technology option already exists for the technology.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_find_tech_alias.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectTechnologies.findTechAlias", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch("climmob.views.Api.projectTechnologies.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_assigned(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs,
        mock_project_reg_status,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_find_tech_alias,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology is not assigned to the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_user_belongs.assert_called_once_with("tech_user", 1, self.view.request)
        mock_project_reg_status.assert_called_once_with(1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "alias_name": "ALIAS_EXTRA",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_find_tech_alias.assert_not_called()

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user", "tech_id": "TECH456"}
        )
        self.view.request.json_body = json.loads(self.view.body)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


class TestReadProjectTechnologiesAliasView(unittest.TestCase):
    def setUp(self):
        self.view = ReadProjectTechnologiesAliasView(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
            }
        )
        self.view.request.json_body = json.loads(self.view.body)
        self.view._ = lambda x: x

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch(
        "climmob.views.Api.projectTechnologies.AliasSearchTechnologyInProject",
        return_value={"alias": "ALIAS1"},
    )
    def test_process_view_successful_read_alias(
        self,
        mock_alias_search,
        mock_is_technology_assigned,
        mock_technology_exist,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_body = json.dumps({"alias": "ALIAS1"})
        self.assertEqual(response.body.decode(), expected_body)

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_alias_search.assert_called_once_with("TECH456", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=False)
    def test_process_view_technology_not_exist(
        self, mock_technology_exist, mock_get_project_id, mock_project_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no technology with that identifier.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    def test_process_view_technology_not_assigned(
        self,
        mock_is_technology_assigned,
        mock_technology_exist,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology is not assigned to the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user", "tech_id": "TECH456"}
        )
        self.view.request.json_body = json.loads(self.view.body)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json_decode_error(self):
        self.view.body = "invalid json"
        with patch(
            "json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0)
        ):
            response = self.view.processView()
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "Error in the JSON, It does not have the 'body' parameter.",
                response.body.decode(),
            )

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestReadProjectTechnologiesAliasExtraView(unittest.TestCase):
    def setUp(self):
        self.view = ReadProjectTechnologiesAliasExtraView(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
            }
        )
        self.view.request.json_body = json.loads(self.view.body)
        self.view._ = lambda x: x

    @patch(
        "climmob.views.Api.projectTechnologies.AliasExtraSearchTechnologyInProject",
        return_value={"alias_extra": "ALIAS_EXTRA1"},
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_read_alias_extra(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_extra_search,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_body = json.dumps({"alias_extra": "ALIAS_EXTRA1"})
        self.assertEqual(response.body.decode(), expected_body)

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_alias_extra_search.assert_called_once_with("TECH456", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_exist(
        self, mock_project_exists, mock_get_project_id, mock_technology_exist
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no technology with that identifier.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_assigned(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_technology_exist,
        mock_is_technology_assigned,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology is not assigned to the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user", "tech_id": "TECH456"}
        )
        self.view.request.json_body = json.loads(self.view.body)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json_decode_error(self):
        self.view.body = "invalid json"
        with patch(
            "json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0)
        ):
            response = self.view.processView()
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "Error in the JSON, It does not have the 'body' parameter.",
                response.body.decode(),
            )

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch(
        "climmob.views.Api.projectTechnologies.AliasExtraSearchTechnologyInProject",
        return_value={"alias_extra": "ALIAS_EXTRA1"},
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_read_alias_extra_with_different_alias(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_extra_search,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_body = json.dumps({"alias_extra": "ALIAS_EXTRA1"})
        self.assertEqual(response.body.decode(), expected_body)

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_alias_extra_search.assert_called_once_with("TECH456", 1, self.view.request)

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch(
        "climmob.views.Api.projectTechnologies.AliasExtraSearchTechnologyInProject",
        return_value={"alias_extra": "ALIAS_EXTRA1"},
    )
    def test_process_view_alias_extra_search_function_called(
        self,
        mock_alias_extra_search,
        mock_is_technology_assigned,
        mock_technology_exist,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        mock_alias_extra_search.assert_called_once_with("TECH456", 1, self.view.request)

    @patch(
        "climmob.views.Api.projectTechnologies.AliasExtraSearchTechnologyInProject",
        return_value={},
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_alias_extra_search_returns_empty(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_extra_search,
    ):
        mock_alias_extra_search.return_value = {}
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body.decode(), json.dumps({}))


class TestReadPossibleProjectTechnologiesAliasView(unittest.TestCase):
    def setUp(self):
        self.view = ReadPossibleProjectTechnologiesAliasView(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
            }
        )
        self.view.request.json_body = json.loads(self.view.body)
        self.view._ = lambda x: x

    @patch(
        "climmob.views.Api.projectTechnologies.AliasSearchTechnology",
        return_value={"alias_possible": "ALIAS_POSSIBLE1"},
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_read_possible_alias(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_possible_search,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_body = json.dumps({"alias_possible": "ALIAS_POSSIBLE1"})
        self.assertEqual(response.body.decode(), expected_body)

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_alias_possible_search.assert_called_once_with(
            "TECH456", 1, self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=False)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_exist(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_technology_exist,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no technology with that identifier.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.AliasSearchTechnology",
        return_value={"alias_possible": "ALIAS_POSSIBLE1"},
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_technology_not_assigned(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_possible_search,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The technology is not assigned to the project.", response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )

    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=4
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    def test_process_view_access_type_not_allowed(
        self,
        mock_is_technology_assigned,
        mock_technology_exist,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to get this information.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user", "tech_id": "TECH456"}
        )
        self.view.request.json_body = json.loads(self.view.body)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_json_decode_error(self):
        self.view.body = "invalid json"
        with patch(
            "json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0)
        ):
            response = self.view.processView()
            self.assertEqual(response.status_code, 401)
            self.assertIn(
                "Error in the JSON, It does not have the 'body' parameter.",
                response.body.decode(),
            )

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch(
        "climmob.views.Api.projectTechnologies.AliasSearchTechnology",
        return_value={"alias_possible": "ALIAS_POSSIBLE2"},
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_successful_read_possible_alias_different_alias(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_possible_search,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_body = json.dumps({"alias_possible": "ALIAS_POSSIBLE2"})
        self.assertEqual(response.body.decode(), expected_body)

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with("test_user", 1, self.view.request)
        mock_technology_exist.assert_called_once_with(
            "TECH456", "tech_user", self.view.request
        )
        mock_is_technology_assigned.assert_called_once_with(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "tech_id": "TECH456",
                "tech_user_name": "tech_user",
                "user_name": "test_user",
                "project_id": 1,
            },
            self.view.request,
        )
        mock_alias_possible_search.assert_called_once_with(
            "TECH456", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectTechnologies.AliasSearchTechnology", return_value={}
    )
    @patch(
        "climmob.views.Api.projectTechnologies.isTechnologyAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectTechnologies.technologyExist", return_value=True)
    @patch(
        "climmob.views.Api.projectTechnologies.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectTechnologies.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectTechnologies.projectExists", return_value=True)
    def test_process_view_alias_possible_search_returns_empty(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_technology_exist,
        mock_is_technology_assigned,
        mock_alias_possible_search,
    ):
        mock_alias_possible_search.return_value = {}
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body.decode(), json.dumps({}))


if __name__ == "__main__":
    unittest.main()
