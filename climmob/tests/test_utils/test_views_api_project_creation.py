import json
import unittest
import datetime
from unittest.mock import patch, MagicMock, call
from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.projectCreation import (
    readListOfTemplates_view,
    readListOfCountries_view,
    createProject_view,
    readProjects_view,
    updateProject_view,
    deleteProject_view_api,
    readCollaborators_view,
    addCollaborator_view,
)

class TestReadListOfTemplatesView(BaseViewTestCase):
    view_class = readListOfTemplates_view
    request_method = "GET"
    request_body = json.dumps({"project_type": "agriculture"})

    @patch(
        "climmob.views.Api.projectCreation.getProjectTemplates",
        return_value=[{"template": "data"}],
    )
    def test_process_view_success(self, mock_get_project_templates):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, [{"template": "data"}])

        mock_get_project_templates.assert_called_with(self.view.request, "agriculture")

    def test_process_view_invalid_json(self):
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({"other_key": "value"})

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        self.view.body = json.dumps({"project_type": ""})

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_post_method(self):
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_empty_body(self):
        self.view.body = "{}"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_malformed_json(self):
        self.view.body = '{"project_type": "agriculture",}'

        with self.assertRaises(json.JSONDecodeError):
            self.view.processView()

    @patch("climmob.views.Api.projectCreation.getProjectTemplates", return_value=None)
    def test_process_view_get_project_templates_none(self, mock_get_project_templates):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.body), None)

        mock_get_project_templates.assert_called_with(self.view.request, "agriculture")

class TestReadListOfCountriesView(BaseViewTestCase):
    view_class = readListOfCountries_view
    request_method = "GET"

    @patch(
        "climmob.views.Api.projectCreation.getCountryList",
        return_value=[{"country": "Costa Rica"}],
    )
    def test_process_view_success(self, mock_get_country_list):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data, [{"country": "Costa Rica"}])
        mock_get_country_list.assert_called_with(self.view.request)

    def test_process_view_post_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

class TestCreateProjectView(BaseViewTestCase):
    view_class = createProject_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "project_name": "Test Project",
            "project_abstract": "Test abstract",
            "project_tags": "tag1, tag2",
            "project_pi": "John Doe",
            "project_piemail": "johndoe@example.com",
            "project_numobs": 5,
            "project_cnty": "US",
            "project_registration_and_analysis": "1",
            "project_label_a": "Label A",
            "project_label_b": "Label B",
            "project_label_c": "Label C",
            "project_languages": ["en"]
        }
        self.view.body = json.dumps(self.valid_data)

    @patch("climmob.views.Api.projectCreation.addPrjLang", return_value=(True, ""))
    @patch("climmob.views.Api.projectCreation.addProject", return_value=(True, "new_project_id"))
    @patch("climmob.views.Api.projectCreation.existsCountryByCode", return_value=True)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_success(
        self, mock_language_exist, mock_project_in_db, mock_exists_country, mock_add_project, mock_add_prj_lang
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Project created successfully.", response.body.decode())
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)
        mock_exists_country.assert_called_with(self.view.request, "US")
        mock_add_project.assert_called()

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        del self.valid_data["project_name"]
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("It is not complying with the obligatory keys.", response.body.decode())

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_invalid_parameters(self, mock_language_exist):
        self.valid_data["invalid_param"] = "invalid"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("You are trying to use a parameter that is not allowed.", response.body.decode())

    def test_process_view_invalid_project_languages_type(self):
        self.valid_data["project_languages"] = "en"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("The parameter project_languages must be a list.", response.body.decode())

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=False)
    def test_process_view_invalid_project_language(self, mock_language_exist):
        self.valid_data["project_languages"] = ["invalid_lang"]
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a language to the project that is not part of the list of languages to be used.",
            response.body.decode()
        )
        mock_language_exist.assert_called_with("invalid_lang", "test_user", self.view.request)

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_clone_and_template(self, mock_language_exist):
        self.valid_data["project_clone"] = "clone_id"
        self.valid_data["project_template"] = "template_id"
        self.view.body = json.dumps(self.valid_data)
        with patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot create a clone and use a template at the same time.",
            response.body.decode()
        )

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.projectCreation.getProjectIsTemplate", return_value=None)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_invalid_template(self, mock_project_in_db, mock_get_project_is_template, mock_language_exist):
        self.valid_data["project_template"] = "invalid_template_id"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no template with this identifier.",
            response.body.decode()
        )
        mock_get_project_is_template.assert_called_with(self.view.request, "invalid_template_id")

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.projectCreation.getProjectIsTemplate", return_value={"project_registration_and_analysis": "0"})
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_template_registration_mismatch(self, mock_project_in_db, mock_get_project_is_template, mock_language_exist):
        self.valid_data["project_template"] = "template_id"
        self.valid_data["project_registration_and_analysis"] = "1"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to use a template that does not correspond to the type of project you are creating.",
            response.body.decode()
        )
        mock_get_project_is_template.assert_called_with(self.view.request, "template_id")

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=True)
    def test_process_view_project_code_already_exists(self, mock_project_in_db, mock_language_exist):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("This project ID already exists.", response.body.decode())
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_project_cod_invalid_characters(self, mock_language_exist):
        self.valid_data["project_cod"] = "PRJ 123"
        self.view.body = json.dumps(self.valid_data)
        with patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "For the project ID only letters and numbers are allowed. The project ID must start with a letter.",
            response.body.decode()
        )

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_project_cod_starts_with_digit(self, mock_language_exist):
        self.valid_data["project_cod"] = "1PRJ123"
        self.view.body = json.dumps(self.valid_data)
        with patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The project ID must start with a letter.",
            response.body.decode()
        )

    def test_process_view_missing_data_in_parameters(self):
        self.valid_data["project_name"] = ""
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.projectCreation.existsCountryByCode", return_value=False)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_invalid_country_code(self, mock_project_in_db, mock_exists_country, mock_language_exist):
        self.valid_data["project_cnty"] = "XX"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The country assigned to the project does not exist in the ClimMob list.",
            response.body.decode()
        )
        mock_exists_country.assert_called_with(self.view.request, "XX")
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_labels_not_unique(self, mock_project_in_db, mock_language_exist):
        self.valid_data["project_label_a"] = "Label"
        self.valid_data["project_label_b"] = "Label"
        self.valid_data["project_label_c"] = "Label"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The names that the items will receive should be different.",
            response.body.decode()
        )
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)

    @patch("climmob.views.Api.projectCreation.addProject", return_value=(False, "Error adding project"))
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_add_project_fails(self, mock_language_exist, mock_project_in_db, mock_add_project):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding project", response.body.decode())
        mock_add_project.assert_called()

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_project_numobs_invalid(self, mock_language_exist):
        self.valid_data["project_numobs"] = "invalid"
        self.view.body = json.dumps(self.valid_data)
        with patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter project_numobs must be a number.",
            response.body.decode()
        )

    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_registration_and_analysis_invalid_value(self, mock_language_exist):
        self.valid_data["project_registration_and_analysis"] = "2"
        self.view.body = json.dumps(self.valid_data)
        with patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The possible values in the parameter 'project_registration_and_analysis' are: ['0':' Registration is done first, followed by one or more data collection moments (with different forms)','1':'Requires registering participants and immediately asking questions to analyze the information']",
            response.body.decode()
        )

    @patch("climmob.views.Api.projectCreation.projectInDatabase")
    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_project_clone_not_exist(self, mock_language_exist, mock_project_in_db):
        self.valid_data["project_clone"] = "nonexistent_project"
        self.view.body = json.dumps(self.valid_data)

        mock_project_in_db.return_value = False
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The project to be cloned does not exist.",
            response.body.decode()
        )

        mock_project_in_db.assert_called_once_with("test_user", "nonexistent_project", self.view.request)

    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_number_of_observations_zero(self, mock_language_exist, mock_project_in_db):
        self.valid_data["project_numobs"] = 0
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The number of combinations and observations must be greater than 0.",
            response.body.decode()
        )
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)

    @patch("climmob.views.Api.projectCreation.projectInDatabase")
    @patch("climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True)
    def test_process_view_project_clone_not_exist(self, mock_language_exist, mock_project_in_db):
        self.valid_data["project_clone"] = "nonexistent_project"
        self.view.body = json.dumps(self.valid_data)

        mock_project_in_db.return_value = False
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The project to be cloned does not exist.",
            response.body.decode()
        )

        mock_project_in_db.assert_called_once_with("test_user", "nonexistent_project", self.view.request)

class TestReadProjectsView(BaseViewTestCase):
    view_class = readProjects_view
    request_method = "GET"

    @patch("climmob.views.Api.projectCreation.getUserProjects")
    def test_process_view_success(self, mock_get_user_projects):
        # Simular datos de proyectos
        projects = [
            {
                "project_id": 1,
                "project_name": "Project 1",
                "project_cod": "PRJ1",
                "project_date": datetime.datetime(2023, 1, 1, 12, 0, 0)
            },
            {
                "project_id": 2,
                "project_name": "Project 2",
                "project_cod": "PRJ2",
                "project_date": datetime.datetime(2023, 2, 1, 12, 0, 0)
            }
        ]
        mock_get_user_projects.return_value = projects

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)

        # Convertir fechas a string para comparación
        expected_body = json.dumps(projects, default=lambda o: o.__str__())

        self.assertEqual(response.body.decode(), expected_body)
        mock_get_user_projects.assert_called_once_with("test_user", self.view.request)

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

class TestDeleteProjectViewApi(BaseViewTestCase):
    view_class = deleteProject_view_api
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {"project_cod": "PRJ123", "user_owner": "owner123"}
        self.view.body = json.dumps(self.valid_data)

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch("climmob.views.Api.projectCreation.deleteProject", return_value=(True, ""))
    def test_process_view_success(
        self,
        mock_delete_project,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("The project was deleted successfully", response.body.decode())

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=4)
    def test_process_view_no_delete_access(
        self, mock_get_access_type, mock_get_project_id, mock_project_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete the project.",
            response.body.decode(),
        )

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch(
        "climmob.views.Api.projectCreation.deleteProject",
        return_value=(False, "Error deleting project"),
    )
    def test_process_view_delete_project_fails(
        self,
        mock_delete_project,
        mock_get_access_type,
        mock_get_project_id,
        mock_project_exists,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error deleting project", response.body.decode())

    def test_process_view_invalid_json(self):
        invalid_data = {"project_cod": "PRJ123"}
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

class TestReadCollaboratorsView(BaseViewTestCase):
    view_class = readCollaborators_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.valid_data = {"project_cod": "PRJ123", "user_owner": "owner123"}
        self.view.body = json.dumps(self.valid_data)

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch(
        "climmob.views.Api.projectCreation.get_collaborators_in_project",
        return_value=[{"user": "collaborator1"}, {"user": "collaborator2"}],
    )
    def test_process_view_success(
        self, mock_get_collaborators, mock_get_project_id, mock_project_exists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        expected_response = json.dumps(
            [{"user": "collaborator1"}, {"user": "collaborator2"}]
        )
        self.assertEqual(response.body.decode(), expected_response)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_collaborators.assert_called_once_with(self.view.request, "project_id")

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )

    def test_process_view_invalid_json(self):
        invalid_data = {"project_cod": "PRJ123"}
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

class TestAddCollaboratorView(BaseViewTestCase):
    view_class = addCollaborator_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "user_collaborator": "collaborator123",
            "access_type": "2",
        }
        self.view.body = json.dumps(self.valid_data)

    @patch(
        "climmob.views.Api.projectCreation.add_project_collaborator",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_user_info,
        mock_user_belongs,
        mock_add_collaborator,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Collaborator added successfully.", response.body.decode())
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
        )
        mock_get_user_info.assert_called_once_with(self.view.request, "collaborator123")
        mock_user_belongs.assert_called_once_with(
            "collaborator123", "project_id", self.view.request
        )
        expected_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "user_collaborator": "collaborator123",
            "access_type": 2,
            "project_id": "project_id",
            "user_name": "collaborator123",
            "project_dashboard": 0,
        }
        mock_add_collaborator.assert_called_once_with(self.view.request, expected_data)

    @patch("climmob.views.Api.projectCreation.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=4)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    def test_process_view_no_permission(
        self, mock_project_exists, mock_get_project_id, mock_get_access_type
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add collaborators to the project.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
        )

    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=False)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    def test_process_view_user_does_not_exist(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_user_info,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The user you want to add as a collaborator does not exist.",
            response.body.decode(),
        )
        mock_get_user_info.assert_called_once_with(self.view.request, "collaborator123")

    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    def test_process_view_user_already_in_project(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_user_info,
        mock_user_belongs,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The collaborator you want to add already belongs to the project.",
            response.body.decode(),
        )
        mock_user_belongs.assert_called_once_with(
            "collaborator123", "project_id", self.view.request
        )

    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    def test_process_view_invalid_access_type(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_user_info,
        mock_user_belongs,
    ):
        self.valid_data["access_type"] = "5"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The types of access for collaborators are as follows: 2=Admin, 3=Editor, 4=Member.",
            response.body.decode(),
        )

    @patch(
        "climmob.views.Api.projectCreation.add_project_collaborator",
        return_value=(False, "Error adding collaborator"),
    )
    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=False,
    )
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=1)
    @patch(
        "climmob.views.Api.projectCreation.getTheProjectIdForOwner",
        return_value="project_id",
    )
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    def test_process_view_add_collaborator_fails(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_user_info,
        mock_user_belongs,
        mock_add_collaborator,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding collaborator", response.body.decode())
        mock_add_collaborator.assert_called_once()

    def test_process_view_missing_obligatory_keys(self):
        del self.valid_data["user_collaborator"]
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


if __name__ == "__main__":
    unittest.main()