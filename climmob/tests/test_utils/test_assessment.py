import unittest
from unittest.mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound
from types import SimpleNamespace

# Importa la clase a probar
from climmob.views.assessment import (
    deleteAssessmentSection_view,
    assessmentSectionActions_view,
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


if __name__ == '__main__':
    unittest.main()
