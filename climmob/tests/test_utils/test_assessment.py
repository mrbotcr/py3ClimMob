import unittest
from unittest.mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import json
import os
from jinja2 import Environment, FileSystemLoader

# Importa la clase a probar
from climmob.views.assessment import (
    deleteAssessmentSection_view,
    assessmentSectionActions_view,
    actionsInSections,
    getAssessmentDetails_view,
    assessmenthead_view,
    deleteassessmenthead_view,
    assessment_view,
    assessmentFormCreation_view
)

class TestDeleteAssessmentSectionView(unittest.TestCase):

    def setUp(self):
        # Configura el mock para request y user
        self.mock_request = MagicMock()
        self.mock_user = MagicMock()
        self.view = deleteAssessmentSection_view(self.mock_request)
        self.view.user = self.mock_user

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getAssessmentGroupInformation')
    @patch('climmob.views.assessment.deleteAssessmentGroup')
    def test_process_view_project_not_exists(self, mock_delete, mock_get_info, mock_get_id, mock_exists):
        # Configura el mock para simular que el proyecto no existe
        mock_exists.return_value = False

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid"
        }

        # Verifica que se lanza HTTPNotFound cuando el proyecto no existe
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getAssessmentGroupInformation')
    @patch('climmob.views.assessment.deleteAssessmentGroup')
    def test_process_view_delete_success(self, mock_delete, mock_get_info, mock_get_id, mock_exists):
        # Configura los mocks para simular un caso de éxito
        mock_exists.return_value = True
        mock_get_id.return_value = "project_id"
        mock_get_info.return_value = {"info": "data"}
        mock_delete.return_value = (True, "")

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, {"status": 200})
        self.assertTrue(self.view.returnRawViewResult)

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getAssessmentGroupInformation')
    @patch('climmob.views.assessment.deleteAssessmentGroup')
    def test_process_view_delete_failure(self, mock_delete, mock_get_info, mock_get_id, mock_exists):
        # Configura los mocks para simular un fallo al eliminar el grupo de evaluación
        mock_exists.return_value = True
        mock_get_id.return_value = "project_id"
        mock_get_info.return_value = {"info": "data"}
        mock_delete.return_value = (False, "Error message")

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, {"status": 400, "error": "Error message"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getAssessmentGroupInformation')
    @patch('climmob.views.assessment.deleteAssessmentGroup')
    def test_process_view_non_post_method(self, mock_delete, mock_get_info, mock_get_id, mock_exists):
        # Configura los mocks para un acceso con un método distinto de POST
        mock_exists.return_value = True
        mock_get_id.return_value = "project_id"
        mock_get_info.return_value = {"info": "data"}

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(result, {
            "activeUser": self.mock_user,
            "assessmentid": "test_assessmentid",
            "data": {"info": "data"},
            "error_summary": {},
            "groupid": "test_groupid",
        })
        self.assertFalse(self.view.returnRawViewResult)

class TestAssessmentSectionActionsView(unittest.TestCase):

    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_user = MagicMock()
        self.view = assessmentSectionActions_view(self.mock_request)
        self.view.user = self.mock_user

    @patch('climmob.views.assessment.projectExists')
    def test_project_not_exists(self, mock_projectExists):
        # Configura el mock para simular que el proyecto no existe
        mock_projectExists.return_value = False

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }

        # Verifica que se lanza HTTPNotFound cuando el proyecto no existe
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.assessment.projectExists', return_value=True)
    @patch('climmob.views.assessment.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.assessment.actionsInSections')
    def test_add_new_section_success(self, mock_actionsInSections, mock_get_project_id, mock_project_exists):
        mock_actionsInSections.return_value = {"result": "success"}

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.method = "POST"
        # Aseguramos que 'group_cod' esté presente en los datos POST
        self.mock_request.POST = {"action": "btnNewSection", "group_cod": "test_group"}

        result = self.view.processView()

        self.assertEqual(result, {"result": "success"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch('climmob.views.assessment.projectExists', return_value=True)
    @patch('climmob.views.assessment.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.assessment.actionsInSections')
    def test_update_section_success(self, mock_actionsInSections, mock_get_project_id, mock_project_exists):
        mock_actionsInSections.return_value = {"result": "success"}

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.method = "POST"
        self.mock_request.POST = {"action": "btnUpdateSection"}

        result = self.view.processView()

        self.assertEqual(result, {"result": "success"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch('climmob.views.assessment.projectExists', return_value=True)
    @patch('climmob.views.assessment.getTheProjectIdForOwner', return_value="project_id")
    def test_non_post_method(self, mock_get_project_id, mock_project_exists):
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(result, {})
        self.assertFalse(self.view.returnRawViewResult)

class TestActionsInSections(unittest.TestCase):
    def setUp(self):
        # Configura la instancia simulada de la clase con el método _
        self.instance = MagicMock()
        self.instance._ = lambda x: x  # Simula la traducción

    @patch('climmob.views.assessment.addAssessmentGroup')
    def test_insert_success(self, mock_addAssessmentGroup):
        # Simula el caso de éxito para la acción 'insert'
        mock_addAssessmentGroup.return_value = (True, "success")
        postdata = {"action": "insert"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(result, {
            "result": "success",
            "success": "The section was successfully added",
        })

    @patch('climmob.views.assessment.addAssessmentGroup')
    def test_insert_repeated(self, mock_addAssessmentGroup):
        # Simula el caso donde la inserción falla debido a un grupo repetido
        mock_addAssessmentGroup.return_value = (False, "repeated")
        postdata = {"action": "insert"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(result, {
            "result": "error",
            "error": "There is already a group with this name.",
        })

    @patch('climmob.views.assessment.addAssessmentGroup')
    def test_insert_error(self, mock_addAssessmentGroup):
        # Simula el caso donde la inserción falla por otro motivo
        mock_addAssessmentGroup.return_value = (False, "other error")
        postdata = {"action": "insert"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(result, {
            "result": "error",
            "error": "other error",
        })

    @patch('climmob.views.assessment.modifyAssessmentGroup')
    def test_update_success(self, mock_modifyAssessmentGroup):
        # Simula el caso de éxito para la acción 'update'
        mock_modifyAssessmentGroup.return_value = (True, "success")
        postdata = {"action": "update"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(result, {
            "result": "success",
            "success": "The section was successfully updated",
        })

    @patch('climmob.views.assessment.modifyAssessmentGroup')
    def test_update_repeated(self, mock_modifyAssessmentGroup):
        # Simula el caso donde la actualización falla debido a un grupo repetido
        mock_modifyAssessmentGroup.return_value = (False, "repeated")
        postdata = {"action": "update"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(result, {
            "result": "error",
            "error": "There is already a group with this name.",
        })

    @patch('climmob.views.assessment.modifyAssessmentGroup')
    def test_update_error(self, mock_modifyAssessmentGroup):
        # Simula el caso donde la actualización falla por otro motivo
        mock_modifyAssessmentGroup.return_value = (False, "other error")
        postdata = {"action": "update"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(result, {
            "result": "error",
            "error": "other error",
        })

class TestGetAssessmentDetailsView(unittest.TestCase):
    def setUp(self):
        # Configura la solicitud simulada y la instancia de la vista
        self.request = MagicMock()
        self.request.method = "GET"
        self.request.matchdict = {
            "user": "testuser",
            "project": "testproject",
            "assessmentid": "1"
        }
        # Pasa la solicitud simulada al inicializador de la vista
        self.view = getAssessmentDetails_view(self.request)
        self.view.user = MagicMock(login="testlogin")

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    def test_process_view_success(self, mock_getProjectAssessmentInfo, mock_getTheProjectIdForOwner,
                                  mock_projectExists):
        # Simula el caso de éxito
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = 1
        mock_getProjectAssessmentInfo.return_value = {"id": "1", "info": "some info"}

        response = self.view.processView()

        self.assertEqual(response, {"id": "1", "info": "some info"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch('climmob.views.assessment.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        # Simula el caso donde el proyecto no existe
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    def test_process_view_method_not_get(self):
        # Simula el caso donde el método HTTP no es GET
        self.request.method = "POST"
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

class TestAssessmentHeadView(unittest.TestCase):
    def setUp(self):
        # Setup a mock request object
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {"user": "test_user", "project": "test_project"}
        self.mock_request.POST = {}

        # Initialize the view
        self.view = assessmenthead_view(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_login"

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.addProjectAssessment')
    @patch('climmob.views.assessment.modifyProjectAssessment')
    @patch('climmob.views.assessment.there_is_final_assessment')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getProjectAssessments')
    @patch('climmob.views.assessment.p.PluginImplementations')
    def test_process_view_project_not_exists(
        self, mock_plugins, mock_get_project_assessments, mock_get_active_project,
        mock_there_is_final_assessment, mock_modify_project_assessment,
        mock_add_project_assessment, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return False
        mock_project_exists.return_value = False

        # Call the method
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.addProjectAssessment')
    @patch('climmob.views.assessment.modifyProjectAssessment')
    @patch('climmob.views.assessment.there_is_final_assessment')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getProjectAssessments')
    @patch('climmob.views.assessment.p.PluginImplementations')
    def test_process_view_post_add_assessment(
        self, mock_plugins, mock_get_project_assessments, mock_get_active_project,
        mock_there_is_final_assessment, mock_modify_project_assessment,
        mock_add_project_assessment, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_there_is_final_assessment.return_value = False

        # Mock plugin behavior
        mock_plugin = MagicMock()
        mock_plugin.before_process_checkbox_data.side_effect = lambda data, _: data
        mock_plugin.after_process_checkbox_data.side_effect = lambda data, _: data
        mock_plugins.return_value = [mock_plugin]

        # Set request method to POST and add btn_add_ass to POST data
        self.mock_request.method = "POST"
        self.mock_request.POST = {"btn_add_ass": True, "ass_final": "on"}

        # Mock getPostDict to return expected data
        self.view.getPostDict = MagicMock(return_value={
            "btn_add_ass": True,
            "ass_final": "on",
            "project_id": 1,
            "userOwner": "test_user"
        })

        # Mock addProjectAssessment to simulate successful addition
        mock_add_project_assessment.return_value = (True, "")

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertIn('new_available', result)
        self.assertIn('activeProject', result)
        self.assertIn('assessments', result)
        self.assertIn('data', result)
        self.assertIn('error_summary', result)

        # Check specific lines
        mock_plugin.before_process_checkbox_data.assert_called_once()
        mock_plugin.after_process_checkbox_data.assert_called_once()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.addProjectAssessment')
    @patch('climmob.views.assessment.modifyProjectAssessment')
    @patch('climmob.views.assessment.there_is_final_assessment')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getProjectAssessments')
    @patch('climmob.views.assessment.p.PluginImplementations')
    def test_process_view_post_modify_assessment(
        self, mock_plugins, mock_get_project_assessments, mock_get_active_project,
        mock_there_is_final_assessment, mock_modify_project_assessment,
        mock_add_project_assessment, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_there_is_final_assessment.return_value = False

        # Mock plugin behavior
        mock_plugin = MagicMock()
        mock_plugin.before_process_checkbox_data.side_effect = lambda data, _: data
        mock_plugin.after_process_checkbox_data.side_effect = lambda data, _: data
        mock_plugins.return_value = [mock_plugin]

        # Set request method to POST and add btn_modify_ass to POST data
        self.mock_request.method = "POST"
        self.mock_request.POST = {"btn_modify_ass": True, "ass_final": "off"}

        # Mock getPostDict to return expected data
        self.view.getPostDict = MagicMock(return_value={
            "btn_modify_ass": True,
            "ass_final": "off",
            "project_id": 1,
            "userOwner": "test_user"
        })

        # Mock modifyProjectAssessment to simulate successful modification
        mock_modify_project_assessment.return_value = (True, "")

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertIn('new_available', result)
        self.assertIn('activeProject', result)
        self.assertIn('assessments', result)
        self.assertIn('data', result)
        self.assertIn('error_summary', result)

        # Check specific lines
        mock_plugin.before_process_checkbox_data.assert_called_once()
        mock_plugin.after_process_checkbox_data.assert_called_once()

class TestDeleteAssessmentHeadView(unittest.TestCase):
    def setUp(self):
        # Setup a mock request object
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }

        # Initialize the view
        self.view = deleteassessmenthead_view(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_login"

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.deleteProjectAssessment')
    def test_process_view_project_not_exists(
        self, mock_delete_assessment, mock_get_assessment_info, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return False
        mock_project_exists.return_value = False

        # Call the method
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.deleteProjectAssessment')
    def test_process_view_get_request(
        self, mock_delete_assessment, mock_get_assessment_info, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_assessment_info.return_value = {"assessment": "info"}

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertIn('data', result)
        self.assertIn('error_summary', result)
        self.assertEqual(result["data"], {"assessment": "info"})
        self.assertEqual(result["error_summary"], {})

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.deleteProjectAssessment')
    def test_process_view_post_request_success(
        self, mock_delete_assessment, mock_get_assessment_info, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_assessment_info.return_value = {"assessment": "info"}

        # Set request method to POST
        self.mock_request.method = "POST"

        # Mock deleteProjectAssessment to simulate successful deletion
        mock_delete_assessment.return_value = (True, "")

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertEqual(result["status"], 200)
        self.assertTrue(self.view.returnRawViewResult)

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.deleteProjectAssessment')
    def test_process_view_post_request_failure(
        self, mock_delete_assessment, mock_get_assessment_info, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_assessment_info.return_value = {"assessment": "info"}

        # Set request method to POST
        self.mock_request.method = "POST"

        # Mock deleteProjectAssessment to simulate failed deletion
        mock_delete_assessment.return_value = (False, "Error message")

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertEqual(result["status"], 400)
        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result["error"], "Error message")

class TestAssessmentView(unittest.TestCase):
    def setUp(self):
        # Setup a mock request object
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.params = {}
        self.mock_request.POST = {}

        # Initialize the view
        self.view = assessment_view(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_login"

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.availableAssessmentQuestions')
    @patch('climmob.views.assessment.getCategoriesFromUserCollaborators')
    @patch('climmob.views.assessment.getDictForPreview')
    @patch('climmob.views.assessment.languageExistInTheProject')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    def test_process_view_project_not_exists(
        self, mock_get_default_lang, mock_lang_exist, mock_get_dict, mock_get_categories,
        mock_get_questions, mock_get_data, mock_get_assessment_info, mock_get_active_project,
        mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return False
        mock_project_exists.return_value = False

        # Call the method
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.availableAssessmentQuestions')
    @patch('climmob.views.assessment.getCategoriesFromUserCollaborators')
    @patch('climmob.views.assessment.getDictForPreview')
    @patch('climmob.views.assessment.languageExistInTheProject')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    def test_process_view_get_request(
        self, mock_get_default_lang, mock_lang_exist, mock_get_dict, mock_get_categories,
        mock_get_questions, mock_get_data, mock_get_assessment_info, mock_get_active_project,
        mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_data.return_value = ({"data_key": "data_value"}, "finalCloseQst")
        mock_get_assessment_info.return_value = {"assessment": "info"}
        mock_get_questions.return_value = {"questions": "info"}
        mock_get_categories.return_value = {"categories": "info"}
        mock_get_dict.return_value = {"additional": {"additional_key": "additional_value"}}
        mock_get_active_project.return_value = {"activeProject": "info"}
        mock_get_default_lang.return_value = {"lang_code": "en"}
        mock_lang_exist.return_value = True

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertIn('data', result)
        self.assertIn('finalCloseQst', result)
        self.assertIn('error_summary', result)
        self.assertIn('activeProject', result)
        self.assertIn('assessmentid', result)
        self.assertIn('assinfo', result)
        self.assertIn('UserQuestion', result)
        self.assertIn('Categories', result)
        self.assertIn('languageActive', result)
        self.assertIn('additional', result)
        self.assertEqual(result["data"], {"data_key": "data_value"})
        self.assertEqual(result["finalCloseQst"], "finalCloseQst")
        self.assertEqual(result["error_summary"], {})
        self.assertEqual(result["activeProject"], {"activeProject": "info"})
        self.assertEqual(result["assessmentid"], "test_assessmentid")
        self.assertEqual(result["assinfo"], {"assessment": "info"})
        self.assertEqual(result["UserQuestion"], {"questions": "info"})
        self.assertEqual(result["Categories"], {"categories": "info"})
        self.assertEqual(result["languageActive"], "en")
        self.assertEqual(result["additional"], {"additional_key": "additional_value"})

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getProjectAssessmentInfo')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.availableAssessmentQuestions')
    @patch('climmob.views.assessment.getCategoriesFromUserCollaborators')
    @patch('climmob.views.assessment.getDictForPreview')
    @patch('climmob.views.assessment.languageExistInTheProject')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    @patch('climmob.views.assessment.createDocumentForm')
    def test_process_view_post_download_doc(
        self, mock_create_document, mock_get_default_lang, mock_lang_exist, mock_get_dict,
        mock_get_categories, mock_get_questions, mock_get_data, mock_get_assessment_info,
        mock_get_active_project, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_active_project.return_value = {"activeProject": "info"}

        # Set request method to POST and add btn_download_doc to POST data
        self.mock_request.method = "POST"
        self.mock_request.POST = {"btn_download_doc": True}

        # Mock the route_url method on the request object
        self.mock_request.route_url.return_value = "/productList"

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertTrue(self.view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertIn("/productList", result.location)

class TestAssessmentFormCreationView(unittest.TestCase):
    def setUp(self):
        # Setup a mock request object
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid"
        }
        self.mock_request.params = {}
        self.mock_request.POST = {}

        # Initialize the view
        self.view = assessmentFormCreation_view(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_login"
        self.view._ = MagicMock(return_value="translated message")

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    @patch('climmob.views.assessment.saveAssessmentOrder')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getDictForPreview')
    def test_process_view_project_not_exists(
        self, mock_get_dict, mock_get_active_project, mock_get_data, mock_save_order,
        mock_get_lang, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return False
        mock_project_exists.return_value = False

        # Call the method
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    @patch('climmob.views.assessment.saveAssessmentOrder')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getDictForPreview')
    def test_process_view_get_request(
        self, mock_get_dict, mock_get_active_project, mock_get_data, mock_save_order,
        mock_get_lang, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_data.return_value = ({"data_key": "data_value"}, "finalCloseQst")
        mock_get_active_project.return_value = {"activeProject": "info"}
        mock_get_dict.return_value = {"additional": "info"}
        mock_get_lang.return_value = {"lang_code": "en"}

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, "")

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    @patch('climmob.views.assessment.saveAssessmentOrder')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getDictForPreview')
    @patch('climmob.views.assessment.FileSystemLoader')
    @patch('climmob.views.assessment.Environment')
    def test_process_view_post_request_success(
        self, mock_env, mock_loader, mock_get_dict, mock_get_active_project, mock_get_data,
        mock_save_order, mock_get_lang, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_data.return_value = ({"data_key": "data_value"}, "finalCloseQst")
        mock_get_active_project.return_value = {"activeProject": "info"}
        mock_get_dict.return_value = {"additional": "info"}
        mock_get_lang.return_value = {"lang_code": "en"}
        mock_save_order.return_value = (True, "")

        # Set request method to POST
        self.mock_request.method = "POST"
        self.mock_request.POST = {"neworder": json.dumps([{"type": "question"}])}

        # Mock the template rendering
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered_template"
        mock_env.return_value.get_template.return_value = mock_template

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, "rendered_template")
        mock_save_order.assert_called_once()

    @patch('climmob.views.assessment.projectExists')
    @patch('climmob.views.assessment.getTheProjectIdForOwner')
    @patch('climmob.views.assessment.getPrjLangDefaultInProject')
    @patch('climmob.views.assessment.saveAssessmentOrder')
    @patch('climmob.views.assessment.getDataFormPreview')
    @patch('climmob.views.assessment.getActiveProject')
    @patch('climmob.views.assessment.getDictForPreview')
    @patch('climmob.views.assessment.FileSystemLoader')
    @patch('climmob.views.assessment.Environment')
    def test_process_view_post_request_failure(
        self, mock_env, mock_loader, mock_get_dict, mock_get_active_project, mock_get_data,
        mock_save_order, mock_get_lang, mock_get_project_id, mock_project_exists
    ):
        # Mock the projectExists function to return True
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_data.return_value = ({"data_key": "data_value"}, "finalCloseQst")
        mock_get_active_project.return_value = {"activeProject": "info"}
        mock_get_dict.return_value = {"additional": "info"}
        mock_get_lang.return_value = {"lang_code": "en"}
        mock_save_order.return_value = (False, "error_message")

        # Set request method to POST
        self.mock_request.method = "POST"
        self.mock_request.POST = {"neworder": json.dumps([{"type": "question"}])}

        # Mock the template rendering
        mock_template = MagicMock()
        mock_template.render.return_value = "rendered_template"
        mock_env.return_value.get_template.return_value = mock_template

        # Call the method
        result = self.view.processView()

        # Assertions
        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, "rendered_template")
        mock_save_order.assert_not_called()


if __name__ == '__main__':
    unittest.main()
