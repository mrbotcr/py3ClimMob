import unittest
import json

from unittest.mock import patch, MagicMock

from climmob.views.Api.projectEnumerators import (
    AddProjectEnumeratorView,
    ReadProjectEnumeratorsView,
    ReadPossibleProjectEnumeratorsView,
    DeleteProjectEnumeratorView,
)


class TestAddProjectEnumeratorView(unittest.TestCase):
    def setUp(self):
        self.view = AddProjectEnumeratorView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "enum_id": "5",
                "enum_user_name": "bioversity",
            }
        )

    def test_process_view_add_project_enum_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_add_project_exption(self):
        self.view.body = "This in not a json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_add_project_enum_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=False)
    def test_process_view_add_project_enum_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no a project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_add_project_enum_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to add field agents.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_add_project_enum_user_no_belongs_to_project(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You are trying to add a field agent from a user that does not belong to this project.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_theUserBelongsToTheProject.assert_called_once_with(
            "bioversity", 1, self.view.request
        )

    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=False)
    @patch(
        "climmob.views.Api.projectEnumerators.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_add_project_enum_no_enumerator_id(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_enumeratorExists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"There is not enumerator with that identifier.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_theUserBelongsToTheProject.assert_called_once_with(
            "bioversity", 1, self.view.request
        )
        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_add_project_enum_field_agent_inactive(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The field agent is inactive or is already assigned to the project.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_theUserBelongsToTheProject.assert_called_once_with(
            "bioversity", 1, self.view.request
        )
        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "bioversity", 1, "5", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.addEnumeratorToProject",
        return_value=(False, "Error To add."),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_add_project_enum_error_to_add(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
        mock_addEnumeratorToProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"Error To add.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_theUserBelongsToTheProject.assert_called_once_with(
            "bioversity", 1, self.view.request
        )
        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "bioversity", 1, "5", self.view.request
        )
        mock_addEnumeratorToProject.assert_called_once_with(
            self.view.request,
            {
                "project_id": 1,
                "enum_user": "bioversity",
                "enum_id": "5",
            },
        )

    @patch("climmob.views.Api.projectEnumerators.getProjectData")
    @patch("climmob.views.Api.projectEnumerators.create_fieldagents_report")
    @patch("climmob.views.Api.projectEnumerators.stopTasksByProcess")
    @patch(
        "climmob.views.Api.projectEnumerators.addEnumeratorToProject",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_add_project_enum_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
        mock_addEnumeratorToProject,
        mock_stopTasksByProcess,
        mock_create_fieldagents_report,
        mock_getProjectData,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b"The field agent has been added to the project.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_theUserBelongsToTheProject.assert_called_once_with(
            "bioversity", 1, self.view.request
        )
        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "bioversity", 1, "5", self.view.request
        )
        mock_addEnumeratorToProject.assert_called_once_with(
            self.view.request,
            {
                "project_id": 1,
                "enum_user": "bioversity",
                "enum_id": "5",
            },
        )
        mock_stopTasksByProcess.assert_called_once_with(
            self.view.request, 1, "create_fieldagents"
        )
        mock_create_fieldagents_report.assert_called_once()
        mock_getProjectData.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectEnumerators.getProjectData")
    @patch("climmob.views.Api.projectEnumerators.create_fieldagents_report")
    @patch("climmob.views.Api.projectEnumerators.stopTasksByProcess")
    @patch(
        "climmob.views.Api.projectEnumerators.addEnumeratorToProject",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    @patch("climmob.views.Api.projectEnumerators.p.PluginImplementations")
    def test_process_view_add_project_enum_success_with_plugins(
        self,
        mock_PluginImplementations,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_theUserBelongsToTheProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
        mock_addEnumeratorToProject,
        mock_stopTasksByProcess,
        mock_create_fieldagents_report,
        mock_getProjectData,
    ):
        plugin_mock = MagicMock()
        plugin_mock.before_adding_enumerator_to_project.return_value = (True, "")
        plugin_mock.after_adding_enumerator_to_project.return_value = None
        mock_PluginImplementations.return_value = [plugin_mock]
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body, b"The field agent has been added to the project."
        )

        plugin_mock.before_adding_enumerator_to_project.assert_called_once_with(
            self.view.request,
            {
                "project_id": 1,
                "enum_user": "bioversity",
                "enum_id": "5",
            },
        )
        plugin_mock.after_adding_enumerator_to_project.assert_called_once_with(
            self.view.request,
            {
                "project_id": 1,
                "enum_user": "bioversity",
                "enum_id": "5",
            },
        )


class TestReadProjectEnumeratorsView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request._ = lambda x: x
        self.request.method = "GET"
        self.view = ReadProjectEnumeratorsView(self.request)
        self.view._ = lambda x: x
        self.view.user = MagicMock(login="test_user")

    def test_process_view_read_project_enum_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    def test_process_view_read_project_exption(self):
        self.view.body = "This in not a json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_read_project_enum_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=False)
    def test_process_view_read_project_enum_no_project_exist(self, mock_projectExists):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no a project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.getProjectEnumerators",
        return_value=("data from Enumerators DB."),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_project_enum_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getProjectEnumerators,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b'"data from Enumerators DB."',
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getProjectEnumerators.assert_called_once_with(1, self.view.request)


class TestReadPossibleProjectEnumeratorsView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request._ = lambda x: x
        self.request.method = "GET"
        self.view = ReadPossibleProjectEnumeratorsView(self.request)
        self.view._ = lambda x: x
        self.view.user = MagicMock(login="test_user")

    def test_process_view_read_possible_project_enum_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    def test_process_view_read_possible_project_exption(self):
        self.view.body = "This in not a json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_read_possible_project_enum_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=False)
    def test_process_view_read_possible_project_enum_no_project_exist(
        self, mock_projectExists
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no a project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_no_allow_modifications(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to make modifications.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.getUsableEnumerators",
        return_value=("Get usable enumerators from DB."),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getUsableEnumerators,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'"Get usable enumerators from DB."')
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getUsableEnumerators.assert_called_once_with(1, self.view.request)


class TestDeleteProjectEnumeratorView(unittest.TestCase):
    def setUp(self):
        self.view = DeleteProjectEnumeratorView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "enum_id": "5",
                "enum_user_name": "bioversity",
            }
        )

    def test_process_view_delete_project_enum_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_add_project_exption(self):
        self.view.body = "This in not a json"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_delete_project_enum_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=False)
    def test_process_view_delete_project_enum_no_project_exist(
        self, mock_projectExists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_no_allow_delete(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to delete field agents.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=False)
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_no_enumerator_id(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_enumeratorExists,
    ):

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"There is not enumerator with that identifier."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=True
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_no_field_agent_assigned(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
    ):

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The field agent is inactive or is not assigned to the project.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "bioversity", 1, "5", self.view.request
        )

    @patch(
        "climmob.views.Api.projectEnumerators.removeEnumeratorFromProject",
        return_value=(False, "Error to delete."),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_error_to_delete(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
        mock_removeEnumeratorFromProject,
    ):

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error to delete.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "bioversity", 1, "5", self.view.request
        )
        mock_removeEnumeratorFromProject.assert_called_once_with(
            1, "5", self.view.request
        )

    @patch("climmob.views.Api.projectEnumerators.getProjectData")
    @patch("climmob.views.Api.projectEnumerators.create_fieldagents_report")
    @patch("climmob.views.Api.projectEnumerators.stopTasksByProcess")
    @patch(
        "climmob.views.Api.projectEnumerators.removeEnumeratorFromProject",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectEnumerators.isEnumeratorAssigned", return_value=False
    )
    @patch("climmob.views.Api.projectEnumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.projectEnumerators.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectEnumerators.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectEnumerators.projectExists", return_value=True)
    def test_process_view_read_possible_project_enum_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_enumeratorExists,
        mock_isEnumeratorAssigned,
        mock_removeEnumeratorFromProject,
        mock_stopTasksByProcess,
        mock_create_fieldagents_report,
        mock_getProjectData,
    ):

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body, b"The field agent was removed from the project."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

        mock_enumeratorExists.assert_called_once_with(
            "bioversity", "5", self.view.request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "bioversity", 1, "5", self.view.request
        )
        mock_removeEnumeratorFromProject.assert_called_once_with(
            1, "5", self.view.request
        )
