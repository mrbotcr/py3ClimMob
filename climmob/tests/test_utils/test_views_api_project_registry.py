import json
import unittest
from unittest.mock import patch, MagicMock
from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.Api.projectRegistry import (
    readProjectRegistry_view,
    readPossibleQuestionsForRegistryGroup_view,
    addRegistryGroup_view,
    updateRegistryGroup_view,
    deleteRegistryGroup_view,
    addQuestionToGroupRegistry_view,
    deleteQuestionFromGroupRegistry_view,
    orderRegistryQuestions_view
)


class TestReadProjectRegistryView(BaseViewTestCase):
    view_class = readProjectRegistry_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    @patch("climmob.views.Api.projectRegistry.getRegistryQuestions", return_value=[
        {"section_id": 1, "question_id": 101, "question_reqinreg": 1}
    ])
    @patch("climmob.views.Api.projectRegistry.getProjectData", return_value={
        "project_label_a": "Label A",
        "project_label_b": "Label B",
        "project_label_c": "Label C",
    })
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_project_data,
        mock_get_registry_questions
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertIn("data", response_data)
        self.assertIn("finalCloseQst", response_data)
        self.assertIsInstance(response_data["data"], list)
        self.assertIsInstance(response_data["finalCloseQst"], bool)

        # Datos esperados ajustados manualmente
        expected_data = [
            {
                "section_id": 1,
                "question_id": 101,
                "createGRP": True,
                "grpCannotDelete": True,  # Porque question_reqinreg == 1
                "closeQst": False,        # Primer elemento
                "closeGrp": False,        # Primer elemento
                "hasQuestions": True,
                "question_reqinreg": 1    # Incluido en los datos esperados
            },
        ]

        self.assertEqual(response_data["data"], expected_data)
        self.assertTrue(response_data["finalCloseQst"])

        # Verificar que los mocks fueron llamados con los argumentos correctos
        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_data.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_get_registry_questions.assert_called_once_with(
            "owner123",
            "project_id",
            self.view.request,
            ["Label A", "Label B", "Label C"],
            onlyShowTheBasicQuestions=True
        )

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = '{"invalid_json": "missing_end_quote}'
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode()
        )

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({"project_cod": "PRJ123"})  # Falta "user_owner"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        self.view.body = json.dumps({"project_cod": "", "user_owner": "owner123"})
        response = self.view.processView()

        # La vista no verifica si 'project_cod' está vacío, así que projectExists se llama con 'project_cod' vacío
        # y retorna False, por lo tanto el mensaje es "There is no a project with that code."
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.getProjectData", return_value={
        "project_label_a": "Label A",
        "project_label_b": "Label B",
        "project_label_c": "Label C",
    })
    @patch("climmob.views.Api.projectRegistry.getRegistryQuestions", return_value=None)
    def test_process_view_get_registry_questions_none(
        self,
        mock_get_registry_questions,
        mock_get_project_data,
        mock_get_project_id,
        mock_project_exists
    ):
        # Dado que la vista original no maneja data=None, se espera un TypeError
        with self.assertRaises(TypeError):
            self.view.processView()

        # Verificar llamadas de mocks
        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_data.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_get_registry_questions.assert_called_once_with(
            "owner123",
            "project_id",
            self.view.request,
            ["Label A", "Label B", "Label C"],
            onlyShowTheBasicQuestions=True
        )

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.getProjectData", return_value={
        "project_label_a": "Label A",
        "project_label_b": "Label B",
        "project_label_c": "Label C",
    })
    @patch("climmob.views.Api.projectRegistry.getRegistryQuestions", side_effect=Exception("Database Error"))
    def test_process_view_registry_questions_exception(
        self,
        mock_get_registry_questions,
        mock_get_project_data,
        mock_get_project_id,
        mock_project_exists
    ):
        # Dado que la vista original no maneja excepciones, se espera que la excepción se propague
        with self.assertRaises(Exception) as context:
            self.view.processView()

        self.assertEqual(str(context.exception), "Database Error")

        # Verificar llamadas de mocks
        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_data.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_get_registry_questions.assert_called_once_with(
            "owner123",
            "project_id",
            self.view.request,
            ["Label A", "Label B", "Label C"],
            onlyShowTheBasicQuestions=True
        )


class TestReadPossibleQuestionsForRegistryGroupView(BaseViewTestCase):
    view_class = readPossibleQuestionsForRegistryGroup_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = '{"invalid_json": "missing_end_quote}'
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode()
        )

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({"project_cod": "PRJ123"})  # Falta "user_owner"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no a project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to get this information.",
            response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.QuestionsOptions", return_value=["Option1", "Option2"])
    @patch("climmob.views.Api.projectRegistry.availableRegistryQuestions", return_value=["Question1", "Question2"])
    @patch("climmob.views.Api.projectRegistry.getProjectData", return_value={
        "project_registration_and_analysis": "analysis_data",
    })
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_project_data,
        mock_available_registry_questions,
        mock_questions_options
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)

        expected_data = {
            "Questions": ["Question1", "Question2"],
            "QuestionsOptions": ["Option1", "Option2"],
        }

        self.assertEqual(response_data, expected_data)

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_get_project_data.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_available_registry_questions.assert_called_once_with(
            "project_id",
            self.view.request,
            "analysis_data"
        )
        mock_questions_options.assert_called_once_with(
            "test_user",
            "owner123",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.availableRegistryQuestions", side_effect=Exception("Database Error"))
    @patch("climmob.views.Api.projectRegistry.getProjectData", return_value={
        "project_registration_and_analysis": "analysis_data",
    })
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_available_registry_questions_exception(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_get_project_data,
        mock_available_registry_questions
    ):
        with self.assertRaises(Exception) as context:
            self.view.processView()

        self.assertEqual(str(context.exception), "Database Error")

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_get_project_data.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_available_registry_questions.assert_called_once_with(
            "project_id",
            self.view.request,
            "analysis_data"
        )


class TestAddRegistryGroupView(BaseViewTestCase):
    view_class = addRegistryGroup_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "section_name": "New Section",
            "section_content": "Section Content",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        # Falta 'section_content'
        invalid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "section_name": "New Section",
        }
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        # 'section_content' está vacío
        invalid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "section_name": "New Section",
            "section_content": "",
        }
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
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
            "You cannot create groups. You started registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to add groups.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_not_called()  # La ejecución se detiene antes de llamar a esta función

    @patch("climmob.views.Api.projectRegistry.addRegistryGroup", return_value=(True, "Group Added"))
    @patch("climmob.views.Api.projectRegistry.haveTheBasicStructure")
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic_structure,
        mock_add_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body.decode(), '"Group Added"')  # El cuerpo es un JSON con el mensaje

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        mock_have_basic_structure.assert_called_once_with(
            "owner123", "project_id", self.view.request
        )
        # Verificar que los datos pasados a addRegistryGroup son correctos
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_add_registry_group.assert_called_once_with(expected_dataworking, self.view, "API")

    @patch("climmob.views.Api.projectRegistry.addRegistryGroup", return_value=(False, "Error Adding Group"))
    @patch("climmob.views.Api.projectRegistry.haveTheBasicStructure")
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_add_group_failure(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic_structure,
        mock_add_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body.decode(), "Error Adding Group")

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        mock_have_basic_structure.assert_called_once_with(
            "owner123", "project_id", self.view.request
        )
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_add_registry_group.assert_called_once_with(expected_dataworking, self.view, "API")


class TestUpdateRegistryGroupView(BaseViewTestCase):
    view_class = updateRegistryGroup_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "group_cod": "GRP456",
            "section_name": "Updated Section",
            "section_content": "Updated Content",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        # Falta 'section_content'
        invalid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "group_cod": "GRP456",
            "section_name": "Updated Section",
        }
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        # 'section_content' está vacío
        invalid_data = self.valid_data.copy()
        invalid_data["section_content"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
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
            "You can not update groups. You started registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to update groups.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_not_called()  # Se detiene antes de llamar a esta función

    @patch("climmob.views.Api.projectRegistry.modifyRegistryGroup", return_value=(True, "Group updated successfully."))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_modify_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group updated successfully.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)
        mock_modify_registry_group.assert_called_once_with(expected_dataworking, self.view)

    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=False)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_group_does_not_exist(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)

    @patch("climmob.views.Api.projectRegistry.modifyRegistryGroup", return_value=(False, "Error updating group"))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_modify_group_failure(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_modify_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error updating group", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)
        mock_modify_registry_group.assert_called_once_with(expected_dataworking, self.view)


class TestDeleteRegistryGroupView(BaseViewTestCase):
    view_class = deleteRegistryGroup_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "group_cod": "GRP456",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        # Falta 'group_cod'
        invalid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
        }
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        # 'group_cod' está vacío
        invalid_data = self.valid_data.copy()
        invalid_data["group_cod"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
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
            "You cannot delete groups. You started registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to delete groups.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_not_called()  # Se detiene antes de llamar a esta función

    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=False)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_group_does_not_exist(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)

    @patch("climmob.views.Api.projectRegistry.canDeleteTheGroup", return_value=False)
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_cannot_delete_group(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_can_delete_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot delete this group because it contains questions required for the registration.",
            response.body.decode(),
        )

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)
        mock_can_delete_group.assert_called_once_with(expected_dataworking, self.view.request)

    @patch("climmob.views.Api.projectRegistry.deleteRegistryGroup", return_value=(True, "Group deleted successfully."))
    @patch("climmob.views.Api.projectRegistry.canDeleteTheGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_can_delete_group,
        mock_delete_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Group deleted successfully.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)
        mock_can_delete_group.assert_called_once_with(expected_dataworking, self.view.request)
        mock_delete_registry_group.assert_called_once_with(
            "project_id", "GRP456", self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.deleteRegistryGroup", return_value=(False, "Error deleting group"))
    @patch("climmob.views.Api.projectRegistry.canDeleteTheGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_delete_failure(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_can_delete_group,
        mock_delete_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error deleting group", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with("owner123", "PRJ123", self.view.request)
        mock_get_access_type.assert_called_once_with("test_user", "project_id", self.view.request)
        mock_project_reg_status.assert_called_once_with("project_id", self.view.request)
        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"
        mock_exits_registry_group.assert_called_once_with(expected_dataworking, self.view)
        mock_can_delete_group.assert_called_once_with(expected_dataworking, self.view.request)
        mock_delete_registry_group.assert_called_once_with(
            "project_id", "GRP456", self.view.request
        )


class TestAddQuestionToGroupRegistryView(BaseViewTestCase):
    view_class = addQuestionToGroupRegistry_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "group_cod": "GRP456",
            "question_id": "Q789",
            "question_user_name": "question_user",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        # Falta 'question_user_name'
        invalid_data = self.valid_data.copy()
        del invalid_data["question_user_name"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        # 'question_id' está vacío
        invalid_data = self.valid_data.copy()
        invalid_data["question_id"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.theUserBelongsToTheProject", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_user_not_in_project(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs_to_project,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to add a question from a user that does not belong to this project.",
            response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_user_belongs_to_project.assert_called_once_with(
            "question_user",
            "project_id",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=False)
    @patch("climmob.views.Api.projectRegistry.theUserBelongsToTheProject", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_registration_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs_to_project,
        mock_project_reg_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot add questions. You started registration.",
            response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_user_belongs_to_project.assert_called_once_with(
            "question_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=(None, False))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.theUserBelongsToTheProject", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_question_not_found(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs_to_project,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID.",
            response.body.decode()
        )

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_user_belongs_to_project.assert_called_once_with(
            "question_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.canUseTheQuestion", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"data": "question"}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.theUserBelongsToTheProject", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_cannot_use_question(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs_to_project,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
        mock_can_use_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The question has already been assigned to the registration or cannot be used in this section.",
            response.body.decode()
        )

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"
        expected_dataworking["section_id"] = "GRP456"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_user_belongs_to_project.assert_called_once_with(
            "question_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            {'project_cod': 'PRJ123', 'user_owner': 'owner123', 'group_cod': 'GRP456', 'question_id': 'Q789', 'question_user_name': 'question_user', 'user_name': 'test_user', 'project_id': 'project_id'},
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )
        mock_can_use_question.assert_called_once_with(
            "question_user",
            "project_id",
            "Q789",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.addRegistryQuestionToGroup", return_value=(True, "Question added"))
    @patch("climmob.views.Api.projectRegistry.canUseTheQuestion", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"data": "question"}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.theUserBelongsToTheProject", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs_to_project,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
        mock_can_use_question,
        mock_add_registry_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The question was added to the project",
            response.body.decode()
        )

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"
        expected_dataworking["section_id"] = "GRP456"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_user_belongs_to_project.assert_called_once_with(
            "question_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )
        mock_can_use_question.assert_called_once_with(
            "question_user",
            "project_id",
            "Q789",
            self.view.request
        )
        mock_add_registry_question.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.addRegistryQuestionToGroup", return_value=(False, "Error adding question"))
    @patch("climmob.views.Api.projectRegistry.canUseTheQuestion", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"data": "question"}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.theUserBelongsToTheProject", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_add_question_failure(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_user_belongs_to_project,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
        mock_can_use_question,
        mock_add_registry_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error adding question",
            response.body.decode()
        )

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"
        expected_dataworking["section_id"] = "GRP456"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_user_belongs_to_project.assert_called_once_with(
            "question_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )
        mock_can_use_question.assert_called_once_with(
            "question_user",
            "project_id",
            "Q789",
            self.view.request
        )
        mock_add_registry_question.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )


class TestDeleteQuestionFromGroupRegistryView(BaseViewTestCase):
    view_class = deleteQuestionFromGroupRegistry_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "group_cod": "GRP456",
            "question_id": "Q789",
            "question_user_name": "question_user",
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        # Falta 'question_user_name'
        invalid_data = self.valid_data.copy()
        del invalid_data["question_user_name"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        # 'question_id' está vacío
        invalid_data = self.valid_data.copy()
        invalid_data["question_id"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
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
            "You cannot delete questions. You started the registration.",
            response.body.decode()
        )

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=False)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_group_does_not_exist(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not a group with that code.", response.body.decode())

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["section_private"] = None
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            {'project_cod': 'PRJ123', 'user_owner': 'owner123', 'group_cod': 'GRP456', 'question_id': 'Q789', 'question_user_name': 'question_user', 'user_name': 'test_user', 'project_id': 'project_id'},
            self.view
        )

    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=(None, False))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_question_not_found(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("You do not have a question with this ID.", response.body.decode())

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"question_reqinreg": 1}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_question_required(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You can not delete this question because is required during registration.",
            response.body.decode()
        )

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.exitsQuestionInGroup", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"question_reqinreg": 0}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_question_not_in_group(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
        mock_exits_question_in_group,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You do not have a question with this ID in this group.",
            response.body.decode()
        )

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )
        mock_exits_question_in_group.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.deleteRegistryQuestionFromGroup", return_value=(True, "Question deleted successfully."))
    @patch("climmob.views.Api.projectRegistry.exitsQuestionInGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"question_reqinreg": 0}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
        mock_exits_question_in_group,
        mock_delete_registry_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Question deleted successfully.", response.body.decode())

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )
        mock_exits_question_in_group.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )
        mock_delete_registry_question.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.deleteRegistryQuestionFromGroup", return_value=(False, "Error deleting question"))
    @patch("climmob.views.Api.projectRegistry.exitsQuestionInGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getQuestionData", return_value=({"question_reqinreg": 0}, True))
    @patch("climmob.views.Api.projectRegistry.exitsRegistryGroup", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_delete_failure(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_exits_registry_group,
        mock_get_question_data,
        mock_exits_question_in_group,
        mock_delete_registry_question,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error deleting question", response.body.decode())

        expected_dataworking = self.valid_data.copy()
        expected_dataworking["user_name"] = "test_user"
        expected_dataworking["project_id"] = "project_id"

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )
        mock_exits_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_question_data.assert_called_once_with(
            "question_user",
            "Q789",
            self.view.request
        )
        mock_exits_question_in_group.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )
        mock_delete_registry_question.assert_called_once_with(
            expected_dataworking,
            self.view.request
        )


class TestOrderRegistryQuestionsView(BaseViewTestCase):
    view_class = orderRegistryQuestions_view
    request_method = "POST"

    def setUp(self):
        super().setUp()
        order_list = [
            {"type": "group", "id": "GRP1", "children": [
                {"type": "question", "id": "QST1"},
                {"type": "question", "id": "QST2"}
            ]},
            {"type": "group", "id": "GRP2", "children": [
                {"type": "question", "id": "QST3"}
            ]}
        ]
        self.valid_data = {
            "project_cod": "PRJ123",
            "user_owner": "owner123",
            "order": json.dumps(order_list)
        }
        self.view.body = json.dumps(self.valid_data)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def test_process_view_invalid_method(self):
        self.view.request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_parameters(self):
        # Falta 'order'
        invalid_data = self.valid_data.copy()
        del invalid_data["order"]
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_empty_parameters(self):
        # 'order' está vacío
        invalid_data = self.valid_data.copy()
        invalid_data["order"] = ""
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_invalid_json_order(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
    ):
        # 'order' no es un JSON válido
        invalid_data = self.valid_data.copy()
        invalid_data["order"] = "{invalid_json}"
        self.view.body = json.dumps(invalid_data)
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON order.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user",
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123",
            "PRJ123",
            self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user",
            "project_id",
            self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id",
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=False)
    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=False)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_registration_started(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_have_basic,
        mock_project_reg_status,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You cannot order the groups and questions. You have started the registration.",
            response.body.decode()
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
        mock_project_reg_status.assert_called_once_with(
            "project_id", self.view.request
        )
        mock_have_basic.assert_not_called()

    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=False)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_no_groups_or_questions(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("No group and questions to order.", response.body.decode())

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id", self.view.request
        )
        mock_have_basic.assert_called_once_with(
            "project_id", self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.getRegistryQuestionsApi", return_value=[1, 2, 3])
    @patch("climmob.views.Api.projectRegistry.getRegistryGroup", return_value=[1, 2])
    @patch("climmob.views.Api.projectRegistry.saveRegistryOrder", return_value=(True, None))
    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_success(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic,
        mock_save_registry_order,
        mock_get_registry_group,
        mock_get_registry_questions,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The order of the groups and questions has been changed.",
            response.body.decode()
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
        mock_project_reg_status.assert_called_once_with(
            "project_id", self.view.request
        )
        mock_have_basic.assert_called_once_with(
            "project_id", self.view.request
        )
        expected_dataworking = {
            'project_cod': 'PRJ123',
            'user_owner': 'owner123',
            'order': self.valid_data["order"],
            'user_name': 'test_user',
            'project_id': 'project_id'
        }
        mock_get_registry_group.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_get_registry_questions.assert_called_once_with(
            expected_dataworking,
            self.view
        )
        mock_save_registry_order.assert_called_once_with(
            "project_id",
            json.loads(self.valid_data["order"]),
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.saveRegistryOrder", return_value=(False, "Error saving order"))
    @patch("climmob.views.Api.projectRegistry.getRegistryQuestionsApi", return_value=[1, 2, 3])
    @patch("climmob.views.Api.projectRegistry.getRegistryGroup", return_value=[1, 2])
    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_save_order_failure(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic,
        mock_get_registry_group,
        mock_get_registry_questions,
        mock_save_registry_order,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The order of the groups and questions has been changed.",
            response.body.decode()
        )

        # Nota: Aunque `saveRegistryOrder` retorna un error, la vista original no maneja este caso y sigue adelante

        mock_project_exists.assert_called_once_with(
            "test_user", "owner123", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner123", "PRJ123", self.view.request
        )
        mock_get_access_type.assert_called_once_with(
            "test_user", "project_id", self.view.request
        )
        mock_project_reg_status.assert_called_once_with(
            "project_id", self.view.request
        )
        mock_have_basic.assert_called_once_with(
            "project_id", self.view.request
        )
        mock_get_registry_group.assert_called_once()
        mock_get_registry_questions.assert_called_once()
        mock_save_registry_order.assert_called_once_with(
            "project_id",
            json.loads(self.valid_data["order"]),
            self.view.request
        )

    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=4)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_no_access(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The access assigned for this project does not allow you to do this action.",
            response.body.decode()
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
        mock_project_reg_status.assert_not_called()
        mock_have_basic.assert_not_called()

    @patch("climmob.views.Api.projectRegistry.getRegistryQuestionsApi", return_value=[1, 2, 3, 4])
    @patch("climmob.views.Api.projectRegistry.getRegistryGroup", return_value=[1, 2])
    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_missing_questions(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_access_type,
        mock_project_reg_status,
        mock_have_basic,
        mock_get_registry_group,
        mock_get_registry_questions,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering questions that are not part of the form or you are forgetting to order some questions that belong to the form.",
            response.body.decode()
        )

        mock_project_exists.assert_called_once()
        mock_get_project_id.assert_called_once()
        mock_get_access_type.assert_called_once()
        mock_project_reg_status.assert_called_once()
        mock_have_basic.assert_called_once()
        mock_get_registry_group.assert_called_once()
        mock_get_registry_questions.assert_called_once()

    @patch("climmob.views.Api.projectRegistry.getRegistryQuestionsApi", return_value=[1, 2, 3])
    @patch("climmob.views.Api.projectRegistry.getRegistryGroup", return_value=[1, 2, 3])
    @patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=True)
    @patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True)
    @patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2)
    @patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.Api.projectRegistry.projectExists", return_value=True)
    def test_process_view_missing_groups(
            self,
            mock_project_exists,
            mock_get_project_id,
            mock_get_access_type,
            mock_project_reg_status,
            mock_have_basic,
            mock_get_registry_group,
            mock_get_registry_questions,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are ordering groups that are not part of the form or you are forgetting to order some groups that belong to the form.",
            response.body.decode()
        )

        mock_project_exists.assert_called_once()
        mock_get_project_id.assert_called_once()
        mock_get_access_type.assert_called_once()
        mock_project_reg_status.assert_called_once()
        mock_have_basic.assert_called_once()
        mock_get_registry_group.assert_called_once()

    def test_process_view_question_outside_group(self):
        # 'order' contiene una pregunta fuera de un grupo
        invalid_data = self.valid_data.copy()
        invalid_data["order"] = json.dumps([
            {"type": "question", "id": "QST1"}
        ])
        self.view.body = json.dumps(invalid_data)
        with patch("climmob.views.Api.projectRegistry.projectExists", return_value=True), \
             patch("climmob.views.Api.projectRegistry.getTheProjectIdForOwner", return_value="project_id"), \
             patch("climmob.views.Api.projectRegistry.getAccessTypeForProject", return_value=2), \
             patch("climmob.views.Api.projectRegistry.projectRegStatus", return_value=True), \
             patch("climmob.views.Api.projectRegistry.haveTheBasic", return_value=True):

            response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Questions cannot be outside a group", response.body.decode())


if __name__ == "__main__":
    unittest.main()
