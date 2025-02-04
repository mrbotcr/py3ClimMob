import datetime
import json
import unittest
from unittest.mock import patch

from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.projectCreation import (
    ReadListOfTemplatesView,
    ReadListOfCountriesView,
    CreateProjectView,
    ReadProjectsView,
    DeleteProjectViewApi,
    ReadCollaboratorsView,
    AddCollaboratorView,
    DeleteCollaboratorView,
)


class TestReadListOfTemplatesView(BaseViewTestCase):
    view_class = ReadListOfTemplatesView
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
    view_class = ReadListOfCountriesView
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
    view_class = CreateProjectView
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
            "project_label_a": "Label A",
            "project_label_b": "Label B",
            "project_label_c": "Label C",
            "project_languages": ["en"],
            "project_affiliation": "MrBot",
            "project_type": 2,
            "project_location": 0,
            "project_unit_of_analysis": 0,
            "project_objectives": [0, 1],
        }
        self.view.body = json.dumps(self.valid_data)

    @patch("climmob.views.Api.projectCreation.add_project_location_unit_objective")
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch("climmob.views.Api.projectCreation.existsCountryByCode", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    @patch(
        "climmob.views.Api.projectCreation.addProject",
        return_value=(True, "new_project_id"),
    )
    @patch("climmob.views.Api.projectCreation.addPrjLang", return_value=(True, ""))
    def test_process_view_success(
        self,
        mock_add_prj_lang,
        mock_add_project,
        mock_exists_country,
        mock_project_in_db,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
        mock_add_project_location_unit_objective,
    ):
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        mock_get_location_unit_of_analysis_objectives_by_combination.return_value = {
            "pluoaobj_id": 0
        }
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Project created successfully.", response.body.decode())
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_language_exist.assert_called_with(self.view.request, "US")
        mock_project_in_db.assert_called_with("en", "test_user", self.view.request)
        mock_exists_country.assert_called_with("test_user", "PRJ123", self.view.request)
        mock_add_project.assert_called()
        mock_add_prj_lang.assert_called_with(
            {"lang_code": "en", "project_id": "new_project_id"}, self.view.request
        )
        mock_add_project_location_unit_objective.assert_called_with(
            {"project_id": "new_project_id", "pluoaobj_id": 0}, self.view.request
        )

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
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_parameters(self, mock_language_exist):
        self.valid_data["invalid_param"] = "invalid"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to use a parameter that is not allowed.",
            response.body.decode(),
        )
        mock_language_exist.assert_not_called()

    def test_process_view_invalid_project_languages_type(self):
        self.valid_data["project_languages"] = "en"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter project_languages must be a list.", response.body.decode()
        )

    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_project_type(self, mock_language_exist):
        self.valid_data["project_type"] = "test"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter project_type must be a number.", response.body.decode()
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_value_project_type(self, mock_language_exist):
        self.valid_data["project_type"] = 3
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter project_type must be [1: Real. 2: Training - This project was only used to explain the use of the ClimMob platform and was created as an example].",
            response.body.decode(),
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=False)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_project_location(
        self, mock_language_exist, mock_get_location_by_id
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("The project_location does not exist.", response.body.decode())
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=False,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_project_unit_of_analysis(
        self,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The project_unit_of_analysis does not exist.", response.body.decode()
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination",
        return_value={},
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_location_unit_of_analysis_by_combination(
        self,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "This project_location with this project_unit_of_analysis has no defined relationship.",
            response.body.decode(),
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_invalid_project_objectives(
        self,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
    ):
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        self.valid_data["project_objectives"] = "0"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "project_objectives should be in list format.",
            response.body.decode(),
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination",
        return_value={},
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_invalid_value_project_objective(
        self,
        mock_project_in_db,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The objective 0 does not correspond to the experiment site and the unit of analysis indicated.",
            response.body.decode(),
        )
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_project_in_db.assert_not_called()
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=False
    )
    def test_process_view_invalid_project_language(self, mock_language_exist):
        self.valid_data["project_languages"] = ["invalid_lang"]
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a language to the project that is not part of the list of languages to be used.",
            response.body.decode(),
        )
        mock_language_exist.assert_called_with(
            "invalid_lang", "test_user", self.view.request
        )

    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_clone_and_template(self, mock_language_exist):
        self.valid_data["project_clone"] = "clone_id"
        self.valid_data["project_template"] = "template_id"
        self.view.body = json.dumps(self.valid_data)
        with patch(
            "climmob.views.Api.projectCreation.projectInDatabase", return_value=False
        ):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot create a clone and use a template at the same time.",
            response.body.decode(),
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch("climmob.views.Api.projectCreation.getProjectIsTemplate", return_value=None)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_invalid_template(
        self,
        mock_project_in_db,
        mock_get_project_is_template,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        self.valid_data["project_template"] = "invalid_template_id"
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no template with this identifier.", response.body.decode()
        )
        mock_get_project_is_template.assert_called_with(
            self.view.request, "invalid_template_id"
        )
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_project_in_db.assert_not_called()
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch(
        "climmob.views.Api.projectCreation.getProjectIsTemplate",
        return_value={"project_registration_and_analysis": "0"},
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_template_registration_mismatch(
        self,
        mock_project_in_db,
        mock_get_project_is_template,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_template"] = "template_id"
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 1,
        }
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to use a template that does not correspond to the type of project you are creating.",
            response.body.decode(),
        )
        mock_get_project_is_template.assert_called_with(
            self.view.request, "template_id"
        )
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_project_in_db.assert_not_called()
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=True)
    def test_process_view_project_code_already_exists(
        self,
        mock_project_in_db,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("This project ID already exists.", response.body.decode())
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_project_cod_invalid_characters(
        self,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_cod"] = "PRJ 123"
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        with patch(
            "climmob.views.Api.projectCreation.projectInDatabase", return_value=False
        ):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "For the project ID only letters and numbers are allowed. The project ID must start with a letter.",
            response.body.decode(),
        )
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_project_cod_starts_with_digit(
        self,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_cod"] = "1PRJ123"
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        with patch(
            "climmob.views.Api.projectCreation.projectInDatabase", return_value=False
        ):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The project ID must start with a letter.", response.body.decode()
        )
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    def test_process_view_missing_data_in_parameters(self):
        self.valid_data["project_name"] = ""
        self.view.body = json.dumps(self.valid_data)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch("climmob.views.Api.projectCreation.existsCountryByCode", return_value=False)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_invalid_country_code(
        self,
        mock_project_in_db,
        mock_language_exist,
        mock_exists_country,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_cnty"] = "XX"
        self.view.body = json.dumps(self.valid_data)

        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The country assigned to the project does not exist in the ClimMob list.",
            response.body.decode(),
        )
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

        mock_exists_country.assert_called_with(self.view.request, "XX")
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    def test_process_view_labels_not_unique(
        self,
        mock_project_in_db,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_label_a"] = "Label"
        self.valid_data["project_label_b"] = "Label"
        self.valid_data["project_label_c"] = "Label"
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The names that the items will receive should be different.",
            response.body.decode(),
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_project_in_db.assert_called_once_with(
            "test_user", "PRJ123", self.view.request
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.addProject",
        return_value=(False, "Error adding project"),
    )
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_add_project_fails(
        self,
        mock_language_exist,
        mock_project_in_db,
        mock_add_project,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }

        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error adding project", response.body.decode())
        mock_add_project.assert_called()

        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_project_in_db.assert_called_once_with(
            "test_user", "PRJ123", self.view.request
        )
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_project_numobs_invalid(
        self,
        mock_language_exist,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_numobs"] = "invalid"
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        with patch(
            "climmob.views.Api.projectCreation.projectInDatabase", return_value=False
        ):
            response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The parameter project_numobs must be a number.", response.body.decode()
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

    # @patch(
    #     "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    # )
    # def test_process_view_registration_and_analysis_invalid_value(
    #     self, mock_language_exist
    # ):
    #     self.valid_data["project_registration_and_analysis"] = "2"
    #     self.view.body = json.dumps(self.valid_data)
    #     with patch(
    #         "climmob.views.Api.projectCreation.projectInDatabase", return_value=False
    #     ):
    #         response = self.view.processView()
    #     self.assertEqual(response.status_code, 401)
    #     self.assertIn(
    #         "The possible values in the parameter 'project_registration_and_analysis' are: ['0':' Registration is done first, followed by one or more data collection moments (with different forms)','1':'Requires registering participants and immediately asking questions to analyze the information']",
    #         response.body.decode(),
    #     )

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch("climmob.views.Api.projectCreation.projectInDatabase")
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_project_clone_not_exist(
        self,
        mock_language_exist,
        mock_project_in_db,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_clone"] = "nonexistent_project"
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        mock_project_in_db.return_value = False
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The project to be cloned does not exist.", response.body.decode()
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)

        mock_project_in_db.assert_called_once_with(
            "test_user", "nonexistent_project", self.view.request
        )

    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_location_unit_of_analysis_by_combination"
    )
    @patch(
        "climmob.views.Api.projectCreation.get_unit_of_analysis_by_id",
        return_value=True,
    )
    @patch("climmob.views.Api.projectCreation.get_location_by_id", return_value=True)
    @patch("climmob.views.Api.projectCreation.projectInDatabase", return_value=False)
    @patch(
        "climmob.views.Api.projectCreation.languageExistInI18nUser", return_value=True
    )
    def test_process_view_number_of_observations_zero(
        self,
        mock_language_exist,
        mock_project_in_db,
        mock_get_location_by_id,
        mock_get_unit_of_analysis_by_id,
        mock_get_location_unit_of_analysis_by_combination,
        mock_get_location_unit_of_analysis_objectives_by_combination,
    ):
        self.valid_data["project_numobs"] = 0
        self.view.body = json.dumps(self.valid_data)
        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 0,
            "plocation_id": 0,
            "puoa_id": 0,
            "registration_and_analysis": 0,
        }
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The number of combinations and observations must be greater than 0.",
            response.body.decode(),
        )
        mock_project_in_db.assert_called_with("test_user", "PRJ123", self.view.request)
        mock_language_exist.assert_called_with("en", "test_user", self.view.request)
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_with(
            self.view.request, 0, 1
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_with(
            self.view.request, 0, 0
        )
        mock_get_unit_of_analysis_by_id.assert_called_with(self.view.request, 0)
        mock_get_location_by_id.assert_called_with(self.view.request, 0)


class TestReadProjectsView(BaseViewTestCase):
    view_class = ReadProjectsView
    request_method = "GET"

    @patch("climmob.views.Api.projectCreation.getUserProjects")
    def test_process_view_success(self, mock_get_user_projects):
        projects = [
            {
                "project_id": 1,
                "project_name": "Project 1",
                "project_cod": "PRJ1",
                "project_date": datetime.datetime(2023, 1, 1, 12, 0, 0),
            },
            {
                "project_id": 2,
                "project_name": "Project 2",
                "project_cod": "PRJ2",
                "project_date": datetime.datetime(2023, 2, 1, 12, 0, 0),
            },
        ]
        mock_get_user_projects.return_value = projects

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)

        expected_body = json.dumps(projects, default=lambda o: o.__str__())

        self.assertEqual(response.body.decode(), expected_body)
        mock_get_user_projects.assert_called_once_with("test_user", self.view.request)

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestDeleteProjectViewApi(BaseViewTestCase):
    view_class = DeleteProjectViewApi
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

        mock_project_exists.assert_called_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_with(
            "test_user", "project_id", self.view.request
        )
        mock_delete_project.assert_called_with("project_id", self.view.request)

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
        mock_project_exists.assert_called_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_with(
            "test_user", "project_id", self.view.request
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

        mock_project_exists.assert_called_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_with(
            "test_user", "project_id", self.view.request
        )
        mock_delete_project.assert_called_with("project_id", self.view.request)

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
    view_class = ReadCollaboratorsView
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
    view_class = AddCollaboratorView
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
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
        )

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
        mock_get_user_info.assert_called_once_with(self.view.request, "collaborator123")
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
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

        mock_user_belongs.assert_called_once_with(
            "collaborator123", "project_id", self.view.request
        )
        mock_get_user_info.assert_called_once_with(self.view.request, "collaborator123")
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
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

        mock_user_belongs.assert_called_once_with(
            "collaborator123", "project_id", self.view.request
        )
        mock_get_user_info.assert_called_once_with(self.view.request, "collaborator123")
        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
        )

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


class TestDeleteCollaboratorView(BaseViewTestCase):
    view_class = DeleteCollaboratorView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "user_collaborator": "collaborator_user",
            }
        )
        self.view.body = self.request_body  # Cuerpo de la petición simulado
        self.view.request.json_body = json.loads(self.request_body)

    @patch("climmob.views.Api.projectCreation.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=3)
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectCreation.remove_collaborator", return_value=(True, "")
    )
    def test_process_view_successful_removal(
        self,
        mock_remove,
        mock_user_belongs,
        mock_get_user_info,
        mock_access_type,
        mock_project_exists,
        mock_get_project_id,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The collaborator has been successfully removed.", response.body.decode()
        )
        mock_remove.assert_called_once()

        mock_user_belongs.assert_called_once_with(
            "collaborator_user", 1, self.view.request
        )
        mock_get_user_info.assert_called_once_with(
            self.view.request, "collaborator_user"
        )
        mock_access_type.called_once_with(self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectCreation.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(
        self, mock_project_exists, mock_get_project_id
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("This project does not exist.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_not_called()

    @patch("climmob.views.Api.projectCreation.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=4)
    def test_process_view_no_permission(
        self, mock_access_type, mock_project_exists, mock_get_project_id
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete collaborators from the project.",
            response.body.decode(),
        )

        mock_access_type.called_once_with(self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectCreation.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=3)
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=False)
    def test_process_view_user_does_not_exist(
        self,
        mock_get_user_info,
        mock_access_type,
        mock_project_exists,
        mock_get_project_id,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The user you want to delete as a collaborator does not exist.",
            response.body.decode(),
        )

        mock_get_user_info.assert_called_once_with(
            self.view.request, "collaborator_user"
        )
        mock_access_type.called_once_with(self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectCreation.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=3)
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=False,
    )
    def test_process_view_user_not_in_project(
        self,
        mock_user_belongs,
        mock_get_user_info,
        mock_access_type,
        mock_project_exists,
        mock_get_project_id,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to delete a collaborator that does not belong to this project.",
            response.body.decode(),
        )

        mock_user_belongs.assert_called_once_with(
            "collaborator_user", 1, self.view.request
        )
        mock_get_user_info.assert_called_once_with(
            self.view.request, "collaborator_user"
        )
        mock_access_type.called_once_with(self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectCreation.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectCreation.projectExists", return_value=True)
    @patch("climmob.views.Api.projectCreation.getAccessTypeForProject", return_value=3)
    @patch("climmob.views.Api.projectCreation.getUserInfo", return_value=True)
    @patch(
        "climmob.views.Api.projectCreation.theUserBelongsToTheProject",
        return_value=True,
    )
    def test_process_view_cannot_delete_owner(
        self,
        mock_user_belongs,
        mock_get_user_info,
        mock_access_type,
        mock_project_exists,
        mock_get_project_id,
    ):
        self.request_body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "user_collaborator": "owner_user",
            }
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The user who owns the project cannot be deleted.", response.body.decode()
        )

        mock_user_belongs.assert_called_once_with("owner_user", 1, self.view.request)
        mock_get_user_info.assert_called_once_with(self.view.request, "owner_user")
        mock_access_type.called_once_with(self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )


if __name__ == "__main__":
    unittest.main()
