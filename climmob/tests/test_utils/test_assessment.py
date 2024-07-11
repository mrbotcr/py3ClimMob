import json
import unittest
from unittest.mock import MagicMock, patch

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.views.assessment import (
    DeleteAssessmentSectionView,
    AssessmentSectionActionsView,
    actionsInSections,
    GetAssessmentDetailsView,
    AssessmentHeadView,
    DeleteAssessmentHeadView,
    AssessmentView,
    AssessmentFormCreationView,
    GetAssessmentSectionView,
    CancelAssessmentView,
    CloseAssessmentView,
    createDocumentForm,
    StartAssessmentsView,
)


class TestDeleteAssessmentSectionView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_user = MagicMock()
        self.view = DeleteAssessmentSectionView(self.mock_request)
        self.view.user = self.mock_user

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    @patch("climmob.views.assessment.deleteAssessmentGroup")
    def test_process_view_project_not_exists(
        self, mock_delete, mock_get_info, mock_get_id, mock_exists
    ):
        mock_exists.return_value = False

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid",
        }

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    @patch("climmob.views.assessment.deleteAssessmentGroup")
    def test_process_view_delete_success(
        self, mock_delete, mock_get_info, mock_get_id, mock_exists
    ):
        mock_exists.return_value = True
        mock_get_id.return_value = "project_id"
        mock_get_info.return_value = {"info": "data"}
        mock_delete.return_value = (True, "")

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, {"status": 200})
        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    @patch("climmob.views.assessment.deleteAssessmentGroup")
    def test_process_view_delete_failure(
        self, mock_delete, mock_get_info, mock_get_id, mock_exists
    ):
        mock_exists.return_value = True
        mock_get_id.return_value = "project_id"
        mock_get_info.return_value = {"info": "data"}
        mock_delete.return_value = (False, "Error message")

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, {"status": 400, "error": "Error message"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    @patch("climmob.views.assessment.deleteAssessmentGroup")
    def test_process_view_non_post_method(
        self, mock_delete, mock_get_info, mock_get_id, mock_exists
    ):
        mock_exists.return_value = True
        mock_get_id.return_value = "project_id"
        mock_get_info.return_value = {"info": "data"}

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_groupid",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "activeUser": self.mock_user,
                "assessmentid": "test_assessmentid",
                "data": {"info": "data"},
                "error_summary": {},
                "groupid": "test_groupid",
            },
        )
        self.assertFalse(self.view.returnRawViewResult)


class TestAssessmentSectionActionsView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_user = MagicMock()
        self.view = AssessmentSectionActionsView(self.mock_request)
        self.view.user = self.mock_user

    @patch("climmob.views.assessment.projectExists")
    def test_project_not_exists(self, mock_projectExists):
        mock_projectExists.return_value = False

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid",
        }

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch("climmob.views.assessment.projectExists", return_value=True)
    @patch(
        "climmob.views.assessment.getTheProjectIdForOwner", return_value="project_id"
    )
    @patch("climmob.views.assessment.actionsInSections")
    def test_add_new_section_success(
        self, mock_actionsInSections, mock_get_project_id, mock_project_exists
    ):
        mock_actionsInSections.return_value = {"result": "success"}

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.method = "POST"
        self.mock_request.POST = {"action": "btnNewSection", "group_cod": "test_group"}

        result = self.view.processView()

        self.assertEqual(result, {"result": "success"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.assessment.projectExists", return_value=True)
    @patch(
        "climmob.views.assessment.getTheProjectIdForOwner", return_value="project_id"
    )
    @patch("climmob.views.assessment.actionsInSections")
    def test_update_section_success(
        self, mock_actionsInSections, mock_get_project_id, mock_project_exists
    ):
        mock_actionsInSections.return_value = {"result": "success"}

        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.method = "POST"
        self.mock_request.POST = {"action": "btnUpdateSection"}

        result = self.view.processView()

        self.assertEqual(result, {"result": "success"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.assessment.projectExists", return_value=True)
    @patch(
        "climmob.views.assessment.getTheProjectIdForOwner", return_value="project_id"
    )
    def test_non_post_method(self, mock_get_project_id, mock_project_exists):
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(result, {})
        self.assertFalse(self.view.returnRawViewResult)


class TestActionsInSections(unittest.TestCase):
    def setUp(self):
        # Set up the mock instance of the class with the _ method
        self.instance = MagicMock()
        self.instance._ = lambda x: x  # Simulate the translation

    @patch("climmob.views.assessment.addAssessmentGroup")
    def test_insert_success(self, mock_addAssessmentGroup):
        mock_addAssessmentGroup.return_value = (True, "success")
        postdata = {"action": "insert"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(
            result,
            {
                "result": "success",
                "success": "The section was successfully added",
            },
        )

    @patch("climmob.views.assessment.addAssessmentGroup")
    def test_insert_repeated(self, mock_addAssessmentGroup):
        mock_addAssessmentGroup.return_value = (False, "repeated")
        postdata = {"action": "insert"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(
            result,
            {
                "result": "error",
                "error": "There is already a group with this name.",
            },
        )

    @patch("climmob.views.assessment.addAssessmentGroup")
    def test_insert_error(self, mock_addAssessmentGroup):
        mock_addAssessmentGroup.return_value = (False, "other error")
        postdata = {"action": "insert"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(
            result,
            {
                "result": "error",
                "error": "other error",
            },
        )

    @patch("climmob.views.assessment.modifyAssessmentGroup")
    def test_update_success(self, mock_modifyAssessmentGroup):
        mock_modifyAssessmentGroup.return_value = (True, "success")
        postdata = {"action": "update"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(
            result,
            {
                "result": "success",
                "success": "The section was successfully updated",
            },
        )

    @patch("climmob.views.assessment.modifyAssessmentGroup")
    def test_update_repeated(self, mock_modifyAssessmentGroup):
        mock_modifyAssessmentGroup.return_value = (False, "repeated")
        postdata = {"action": "update"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(
            result,
            {
                "result": "error",
                "error": "There is already a group with this name.",
            },
        )

    @patch("climmob.views.assessment.modifyAssessmentGroup")
    def test_update_error(self, mock_modifyAssessmentGroup):
        mock_modifyAssessmentGroup.return_value = (False, "other error")
        postdata = {"action": "update"}

        result = actionsInSections(self.instance, postdata)

        self.assertEqual(
            result,
            {
                "result": "error",
                "error": "other error",
            },
        )


class TestGetAssessmentDetailsView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.method = "GET"
        self.request.matchdict = {
            "user": "testuser",
            "project": "testproject",
            "assessmentid": "1",
        }

        self.view = GetAssessmentDetailsView(self.request)
        self.view.user = MagicMock(login="testlogin")

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    def test_process_view_success(
        self,
        mock_getProjectAssessmentInfo,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = 1
        mock_getProjectAssessmentInfo.return_value = {"id": "1", "info": "some info"}

        response = self.view.processView()

        self.assertEqual(response, {"id": "1", "info": "some info"})
        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.assessment.projectExists", return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    def test_process_view_method_not_get(self):
        self.request.method = "POST"
        with self.assertRaises(HTTPNotFound):
            self.view.processView()


class TestAssessmentHeadView(unittest.TestCase):
    def setUp(self):

        self.request = MagicMock()

        self.view = AssessmentHeadView(self.request)
        self.view.user = MagicMock()
        self.view._ = MagicMock(side_effect=lambda x: x)  # Mock translation function
        self.view.request.matchdict = {
            "user": "test_user",
            "project": "test_project",
        }
        self.view.request.POST = {}

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.addProjectAssessment")
    @patch("climmob.views.assessment.modifyProjectAssessment")
    @patch("climmob.views.assessment.there_is_final_assessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessments")
    def test_process_view_project_not_exist(
        self,
        mock_getProjectAssessments,
        mock_getActiveProject,
        mock_there_is_final_assessment,
        mock_modifyProjectAssessment,
        mock_addProjectAssessment,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.addProjectAssessment")
    @patch("climmob.views.assessment.modifyProjectAssessment")
    @patch("climmob.views.assessment.there_is_final_assessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessments")
    def test_process_view_get_method(
        self,
        mock_getProjectAssessments,
        mock_getActiveProject,
        mock_there_is_final_assessment,
        mock_modifyProjectAssessment,
        mock_addProjectAssessment,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_there_is_final_assessment.return_value = False
        mock_getActiveProject.return_value = "active_project"
        mock_getProjectAssessments.return_value = ["assessment1", "assessment2"]

        self.view.request.method = "GET"

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "new_available": True,
                "activeProject": "active_project",
                "assessments": ["assessment1", "assessment2"],
                "data": {},
                "error_summary": {},
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_there_is_final_assessment.assert_called_once_with(
            self.view.request, "test_project_id"
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_getProjectAssessments.assert_called_once_with(
            "test_project_id", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.addProjectAssessment")
    @patch("climmob.views.assessment.modifyProjectAssessment")
    @patch("climmob.views.assessment.there_is_final_assessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessments")
    @patch("climmob.plugins.PluginImplementations")
    def test_process_view_post_method_add(
        self,
        mock_pluginImplementations,
        mock_getProjectAssessments,
        mock_getActiveProject,
        mock_there_is_final_assessment,
        mock_modifyProjectAssessment,
        mock_addProjectAssessment,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_addProjectAssessment.return_value = (True, "msg")
        mock_there_is_final_assessment.return_value = False
        mock_getActiveProject.return_value = "active_project"
        mock_getProjectAssessments.return_value = ["assessment1", "assessment2"]
        mock_plugin = MagicMock()
        mock_plugin.before_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": 1}
            if data["ass_final"] == "on"
            else {"ass_final": 0}
        )
        mock_plugin.after_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": "on"}
            if data["ass_final"] == 1
            else {"ass_final": "off"}
        )
        mock_pluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"
        self.view.request.POST = {"btn_add_ass": True, "ass_final": "on"}
        self.view.getPostDict = MagicMock(return_value={"ass_final": "on"})

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "new_available": True,
                "activeProject": "active_project",
                "assessments": ["assessment1", "assessment2"],
                "data": {},
                "error_summary": {},
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_plugin.before_process_checkbox_data.assert_called_once()
        mock_addProjectAssessment.assert_called_once()
        mock_plugin.after_process_checkbox_data.assert_called_once()
        mock_there_is_final_assessment.assert_called_once_with(
            self.view.request, "test_project_id"
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_getProjectAssessments.assert_called_once_with(
            "test_project_id", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.addProjectAssessment")
    @patch("climmob.views.assessment.modifyProjectAssessment")
    @patch("climmob.views.assessment.there_is_final_assessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessments")
    @patch("climmob.plugins.PluginImplementations")
    def test_process_view_post_method_modify(
        self,
        mock_pluginImplementations,
        mock_getProjectAssessments,
        mock_getActiveProject,
        mock_there_is_final_assessment,
        mock_modifyProjectAssessment,
        mock_addProjectAssessment,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_modifyProjectAssessment.return_value = (True, "msg")
        mock_there_is_final_assessment.return_value = False
        mock_getActiveProject.return_value = "active_project"
        mock_getProjectAssessments.return_value = ["assessment1", "assessment2"]
        mock_plugin = MagicMock()
        mock_plugin.before_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": 1}
            if data["ass_final"] == "on"
            else {"ass_final": 0}
        )
        mock_plugin.after_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": "on"}
            if data["ass_final"] == 1
            else {"ass_final": "off"}
        )
        mock_pluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"
        self.view.request.POST = {"btn_modify_ass": True, "ass_final": "off"}
        self.view.getPostDict = MagicMock(return_value={"ass_final": "off"})

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "new_available": True,
                "activeProject": "active_project",
                "assessments": ["assessment1", "assessment2"],
                "data": {},
                "error_summary": {},
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_plugin.before_process_checkbox_data.assert_called_once()
        mock_modifyProjectAssessment.assert_called_once()
        mock_plugin.after_process_checkbox_data.assert_called_once()
        mock_there_is_final_assessment.assert_called_once_with(
            self.view.request, "test_project_id"
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_getProjectAssessments.assert_called_once_with(
            "test_project_id", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.addProjectAssessment")
    @patch("climmob.views.assessment.modifyProjectAssessment")
    @patch("climmob.views.assessment.there_is_final_assessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessments")
    @patch("climmob.plugins.PluginImplementations")
    def test_process_view_post_method_add_error(
        self,
        mock_pluginImplementations,
        mock_getProjectAssessments,
        mock_getActiveProject,
        mock_there_is_final_assessment,
        mock_modifyProjectAssessment,
        mock_addProjectAssessment,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_addProjectAssessment.return_value = (False, "error_message")
        mock_there_is_final_assessment.return_value = False
        mock_getActiveProject.return_value = "active_project"
        mock_getProjectAssessments.return_value = ["assessment1", "assessment2"]
        mock_plugin = MagicMock()
        mock_plugin.before_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": 1}
            if data["ass_final"] == "on"
            else {"ass_final": 0}
        )
        mock_plugin.after_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": "on"}
            if data["ass_final"] == 1
            else {"ass_final": "off"}
        )
        mock_pluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"
        self.view.request.POST = {"btn_add_ass": True, "ass_final": "on"}
        self.view.getPostDict = MagicMock(return_value={"ass_final": "on"})

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "new_available": True,
                "activeProject": "active_project",
                "assessments": ["assessment1", "assessment2"],
                "data": {"ass_final": "off"},
                "error_summary": {"addAssessment": "error_message"},
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_plugin.before_process_checkbox_data.assert_called_once()
        mock_addProjectAssessment.assert_called_once()
        mock_plugin.after_process_checkbox_data.assert_called_once()
        mock_there_is_final_assessment.assert_called_once_with(
            self.view.request, "test_project_id"
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_getProjectAssessments.assert_called_once_with(
            "test_project_id", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.addProjectAssessment")
    @patch("climmob.views.assessment.modifyProjectAssessment")
    @patch("climmob.views.assessment.there_is_final_assessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessments")
    @patch("climmob.plugins.PluginImplementations")
    def test_process_view_post_method_modify_error(
        self,
        mock_pluginImplementations,
        mock_getProjectAssessments,
        mock_getActiveProject,
        mock_there_is_final_assessment,
        mock_modifyProjectAssessment,
        mock_addProjectAssessment,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_modifyProjectAssessment.return_value = (False, "error_message")
        mock_there_is_final_assessment.return_value = False
        mock_getActiveProject.return_value = "active_project"
        mock_getProjectAssessments.return_value = ["assessment1", "assessment2"]
        mock_plugin = MagicMock()
        mock_plugin.before_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": 1}
            if data["ass_final"] == "on"
            else {"ass_final": 0}
        )
        mock_plugin.after_process_checkbox_data.side_effect = (
            lambda data, key: {"ass_final": "on"}
            if data["ass_final"] == 1
            else {"ass_final": "off"}
        )
        mock_pluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"
        self.view.request.POST = {"btn_modify_ass": True, "ass_final": "off"}
        self.view.getPostDict = MagicMock(return_value={"ass_final": "off"})

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "new_available": True,
                "activeProject": "active_project",
                "assessments": ["assessment1", "assessment2"],
                "data": {"ass_final": "off"},
                "error_summary": {"modifyAssessment": "error_message"},
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_plugin.before_process_checkbox_data.assert_called_once()
        mock_modifyProjectAssessment.assert_called_once()
        mock_plugin.after_process_checkbox_data.assert_called_once()
        mock_there_is_final_assessment.assert_called_once_with(
            self.view.request, "test_project_id"
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_getProjectAssessments.assert_called_once_with(
            "test_project_id", self.view.request
        )


class TestDeleteAssessmentHeadView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid",
        }

        self.view = DeleteAssessmentHeadView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_login"

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.deleteProjectAssessment")
    def test_process_view_project_not_exists(
        self,
        mock_delete_assessment,
        mock_get_assessment_info,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.deleteProjectAssessment")
    def test_process_view_get_request(
        self,
        mock_delete_assessment,
        mock_get_assessment_info,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_assessment_info.return_value = {"assessment": "info"}

        result = self.view.processView()

        self.assertIn("data", result)
        self.assertIn("error_summary", result)
        self.assertEqual(result["data"], {"assessment": "info"})
        self.assertEqual(result["error_summary"], {})

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.deleteProjectAssessment")
    def test_process_view_post_request_success(
        self,
        mock_delete_assessment,
        mock_get_assessment_info,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_assessment_info.return_value = {"assessment": "info"}

        self.mock_request.method = "POST"

        mock_delete_assessment.return_value = (True, "")

        result = self.view.processView()

        self.assertEqual(result["status"], 200)
        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.deleteProjectAssessment")
    def test_process_view_post_request_failure(
        self,
        mock_delete_assessment,
        mock_get_assessment_info,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_assessment_info.return_value = {"assessment": "info"}

        self.mock_request.method = "POST"

        mock_delete_assessment.return_value = (False, "Error message")

        result = self.view.processView()

        self.assertEqual(result["status"], 400)
        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result["error"], "Error message")


class TestAssessmentView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.method = "GET"
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessmentid",
        }
        self.mock_request.params = {}
        self.mock_request.POST = {}

        self.view = AssessmentView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_login"

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.availableAssessmentQuestions")
    @patch("climmob.views.assessment.getCategoriesFromUserCollaborators")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.languageExistInTheProject")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    def test_process_view_project_not_exists(
        self,
        mock_get_default_lang,
        mock_lang_exist,
        mock_get_dict,
        mock_get_categories,
        mock_get_questions,
        mock_get_data,
        mock_get_assessment_info,
        mock_get_active_project,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.availableAssessmentQuestions")
    @patch("climmob.views.assessment.getCategoriesFromUserCollaborators")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.languageExistInTheProject")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    def test_process_view_get_request(
        self,
        mock_get_default_lang,
        mock_lang_exist,
        mock_get_dict,
        mock_get_categories,
        mock_get_questions,
        mock_get_data,
        mock_get_assessment_info,
        mock_get_active_project,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_data.return_value = ({"data_key": "data_value"}, "finalCloseQst")
        mock_get_assessment_info.return_value = {"assessment": "info"}
        mock_get_questions.return_value = {"questions": "info"}
        mock_get_categories.return_value = {"categories": "info"}
        mock_get_dict.return_value = {
            "additional": {"additional_key": "additional_value"}
        }
        mock_get_active_project.return_value = {"activeProject": "info"}
        mock_get_default_lang.return_value = {"lang_code": "en"}
        mock_lang_exist.return_value = True

        result = self.view.processView()

        self.assertIn("data", result)
        self.assertIn("finalCloseQst", result)
        self.assertIn("error_summary", result)
        self.assertIn("activeProject", result)
        self.assertIn("assessmentid", result)
        self.assertIn("assinfo", result)
        self.assertIn("UserQuestion", result)
        self.assertIn("Categories", result)
        self.assertIn("languageActive", result)
        self.assertIn("additional", result)
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

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.availableAssessmentQuestions")
    @patch("climmob.views.assessment.getCategoriesFromUserCollaborators")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.languageExistInTheProject")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    @patch("climmob.views.assessment.createDocumentForm")
    def test_process_view_post_download_doc(
        self,
        mock_create_document,
        mock_get_default_lang,
        mock_lang_exist,
        mock_get_dict,
        mock_get_categories,
        mock_get_questions,
        mock_get_data,
        mock_get_assessment_info,
        mock_get_active_project,
        mock_get_project_id,
        mock_project_exists,
    ):
        mock_project_exists.return_value = True
        mock_get_project_id.return_value = 1
        mock_get_active_project.return_value = {"activeProject": "info"}

        self.mock_request.method = "POST"
        self.mock_request.POST = {"btn_download_doc": True}

        self.mock_request.route_url.return_value = "/productList"

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertIn("/productList", result.location)


class TestCancelAssessmentView(unittest.TestCase):
    def setUp(self):

        self.request = MagicMock()

        self.view = CancelAssessmentView(self.request)
        self.view.user = MagicMock()
        self.view.request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessment",
        }

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssesmentProgress")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getActiveProject")
    def test_process_view_project_not_exist(
        self,
        mock_getActiveProject,
        mock_getProjectAssessmentInfo,
        mock_getAssesmentProgress,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssesmentProgress")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.setAssessmentIndividualStatus")
    @patch("climmob.views.assessment.clean_assessments_error_logs")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.plugins.PluginImplementations")
    def test_process_view_post_method(
        self,
        mock_PluginImplementations,
        mock_getActiveProject,
        mock_clean_assessments_error_logs,
        mock_setAssessmentIndividualStatus,
        mock_getProjectAssessmentInfo,
        mock_getAssesmentProgress,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getAssesmentProgress.return_value = ("progress", "pcompleted")
        mock_getProjectAssessmentInfo.return_value = "assessmentData"
        mock_plugin = MagicMock()
        mock_PluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"
        self.view.request.params = {"closeAssessment": "1"}

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.view.request.route_url("dashboard"))

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getAssesmentProgress.assert_called_once_with(
            "test_user",
            "test_project_id",
            "test_project",
            "test_assessment",
            self.view.request,
        )
        mock_getProjectAssessmentInfo.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_setAssessmentIndividualStatus.assert_called_once_with(
            "test_project_id", "test_assessment", 0, self.view.request
        )
        mock_clean_assessments_error_logs.assert_called_once_with(
            self.view.request, "test_project_id", "test_assessment"
        )
        mock_plugin.after_deleting_form.assert_called_once_with(
            self.view.request,
            "test_user",
            "test_project_id",
            "test_project",
            "assessment",
            "test_assessment",
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssesmentProgress")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getActiveProject")
    def test_process_view_get_method(
        self,
        mock_getActiveProject,
        mock_getProjectAssessmentInfo,
        mock_getAssesmentProgress,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getAssesmentProgress.return_value = ("progress", "pcompleted")
        mock_getProjectAssessmentInfo.return_value = "assessmentData"
        mock_getActiveProject.return_value = "activeProject"

        self.view.request.method = "GET"

        result = self.view.processView()

        self.assertFalse(self.view.returnRawViewResult)
        self.assertEqual(
            result,
            {
                "activeProject": "activeProject",
                "activeUser": self.view.user,
                "redirect": False,
                "progress": "progress",
                "assessmentData": "assessmentData",
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getAssesmentProgress.assert_called_once_with(
            "test_user",
            "test_project_id",
            "test_project",
            "test_assessment",
            self.view.request,
        )
        mock_getProjectAssessmentInfo.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )


class TestGetAssessmentSectionView(unittest.TestCase):
    def setUp(self):

        self.request = MagicMock()

        self.view = GetAssessmentSectionView(self.request)
        self.view.user = MagicMock()
        self.view.request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessment",
            "section": "test_section",
        }

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    def test_process_view_project_not_exist(
        self,
        mock_getAssessmentGroupInformation,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    def test_process_view_get_method(
        self,
        mock_getAssessmentGroupInformation,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getAssessmentGroupInformation.return_value = {
            "section": "test_section_info"
        }

        self.view.request.method = "GET"

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, {"section": "test_section_info"})

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getAssessmentGroupInformation.assert_called_once_with(
            "test_project_id", "test_assessment", "test_section", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssessmentGroupInformation")
    def test_process_view_non_get_method(
        self,
        mock_getAssessmentGroupInformation,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"

        self.view.request.method = "POST"

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, {})

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getAssessmentGroupInformation.assert_not_called()


class TestCloseAssessmentView(unittest.TestCase):
    def setUp(self):

        self.request = MagicMock()
        self.view = CloseAssessmentView(self.request)
        self.view.user = MagicMock()
        self.view.request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessment",
        }

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssesmentProgress")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getActiveProject")
    def test_process_view_project_not_exist(
        self,
        mock_getActiveProject,
        mock_getProjectAssessmentInfo,
        mock_getAssesmentProgress,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssesmentProgress")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.setAssessmentIndividualStatus")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.plugins.PluginImplementations")
    def test_process_view_post_method(
        self,
        mock_PluginImplementations,
        mock_getActiveProject,
        mock_setAssessmentIndividualStatus,
        mock_getProjectAssessmentInfo,
        mock_getAssesmentProgress,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getAssesmentProgress.return_value = ("progress", "pcompleted")
        mock_getProjectAssessmentInfo.return_value = "assessmentData"
        mock_plugin = MagicMock()
        mock_PluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"
        self.view.request.params = {"closeAssessment": "1"}

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.view.request.route_url("dashboard"))

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getAssesmentProgress.assert_called_once_with(
            "test_user",
            "test_project_id",
            "test_project",
            "test_assessment",
            self.view.request,
        )
        mock_getProjectAssessmentInfo.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_setAssessmentIndividualStatus.assert_called_once_with(
            "test_project_id", "test_assessment", 2, self.view.request
        )
        mock_plugin.after_deleting_form.assert_called_once_with(
            self.view.request,
            "test_user",
            "test_project_id",
            "test_project",
            "assessment",
            "test_assessment",
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getAssesmentProgress")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.getActiveProject")
    def test_process_view_get_method(
        self,
        mock_getActiveProject,
        mock_getProjectAssessmentInfo,
        mock_getAssesmentProgress,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getAssesmentProgress.return_value = ("progress", "pcompleted")
        mock_getProjectAssessmentInfo.return_value = "assessmentData"
        mock_getActiveProject.return_value = "activeProject"

        self.view.request.method = "GET"

        result = self.view.processView()

        self.assertFalse(self.view.returnRawViewResult)
        self.assertEqual(
            result,
            {
                "activeProject": "activeProject",
                "activeUser": self.view.user,
                "redirect": False,
                "progress": "progress",
                "assessmentData": "assessmentData",
            },
        )

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getAssesmentProgress.assert_called_once_with(
            "test_user",
            "test_project_id",
            "test_project",
            "test_assessment",
            self.view.request,
        )
        mock_getProjectAssessmentInfo.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )


class TestCreateDocumentForm(unittest.TestCase):
    def setUp(self):
        # Crear un mock de self (la vista)
        self.view = MagicMock()
        self.view.request.locale_name = "en"

    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.create_document_form")
    def test_create_document_form_with_languages(
        self, mock_create_document_form, mock_getDataFormPreview
    ):

        mock_getDataFormPreview.return_value = ("data", "finalCloseQst")

        activeProjectUser = "test_user"
        activeProjectId = "test_project_id"
        activeProjectCod = "test_project_cod"
        assessment_id = "test_assessment"
        projectDetails = {
            "languages": [{"lang_code": "en", "lang_name": "English"}],
            "project_label_a": "Label A",
            "project_label_b": "Label B",
            "project_label_c": "Label C",
        }

        createDocumentForm(
            self.view,
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            assessment_id,
            projectDetails,
        )

        mock_getDataFormPreview.assert_called_once_with(
            self.view,
            activeProjectUser,
            activeProjectId,
            assessmentid=assessment_id,
            language="en",
        )
        mock_create_document_form.assert_called_once_with(
            self.view.request,
            "en",
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            "Assessment",
            assessment_id,
            [{"lang_code": "en", "lang_name": "English", "Data": "data"}],
            ["Label A", "Label B", "Label C"],
        )

    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.create_document_form")
    def test_create_document_form_without_languages(
        self, mock_create_document_form, mock_getDataFormPreview
    ):

        mock_getDataFormPreview.return_value = ("data", "finalCloseQst")

        activeProjectUser = "test_user"
        activeProjectId = "test_project_id"
        activeProjectCod = "test_project_cod"
        assessment_id = "test_assessment"
        projectDetails = {
            "languages": [],
            "project_label_a": "Label A",
            "project_label_b": "Label B",
            "project_label_c": "Label C",
        }

        createDocumentForm(
            self.view,
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            assessment_id,
            projectDetails,
        )

        mock_getDataFormPreview.assert_called_once_with(
            self.view,
            activeProjectUser,
            activeProjectId,
            assessmentid=assessment_id,
            language="en",
        )
        mock_create_document_form.assert_called_once_with(
            self.view.request,
            "en",
            activeProjectUser,
            activeProjectId,
            activeProjectCod,
            "Assessment",
            assessment_id,
            [{"lang_code": "en", "lang_name": "Default", "Data": "data"}],
            ["Label A", "Label B", "Label C"],
        )


class TestStartAssessmentsView(unittest.TestCase):
    def setUp(self):

        self.request = MagicMock()

        self.view = StartAssessmentsView(self.request)
        self.view.user = MagicMock()
        self.view._ = MagicMock(side_effect=lambda x: x)  # Mock translation function
        self.view.request.matchdict = {"user": "test_user", "project": "test_project"}

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    def test_process_view_project_not_exist(
        self, mock_getTheProjectIdForOwner, mock_projectExists
    ):

        mock_projectExists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    def test_process_view_get_method(
        self, mock_getTheProjectIdForOwner, mock_projectExists
    ):

        mock_projectExists.return_value = True

        self.view.request.method = "GET"

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getProjectAssessmentInfo")
    @patch("climmob.views.assessment.checkAssessments")
    @patch("climmob.views.assessment.getTheGroupOfThePackageCodeAssessment")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.generateAssessmentFiles")
    @patch("climmob.views.assessment.setAssessmentIndividualStatus")
    @patch("climmob.views.assessment.createDocumentForm")
    @patch("climmob.plugins.PluginImplementations")
    @patch.object(
        StartAssessmentsView,
        "getPostDict",
        return_value={"assessment_id": "test_assessment"},
    )
    def test_process_view_post_method(
        self,
        mock_getPostDict,
        mock_PluginImplementations,
        mock_createDocumentForm,
        mock_setAssessmentIndividualStatus,
        mock_generateAssessmentFiles,
        mock_getActiveProject,
        mock_getTheGroupOfThePackageCodeAssessment,
        mock_checkAssessments,
        mock_getProjectAssessmentInfo,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getProjectAssessmentInfo.return_value = {"ass_rhomis": 0}
        mock_checkAssessments.return_value = (True, {})
        mock_getTheGroupOfThePackageCodeAssessment.return_value = "section_code"
        mock_getActiveProject.return_value = {
            "languages": [{"lang_code": "en", "lang_name": "English"}],
            "project_label_a": "Label A",
            "project_label_b": "Label B",
            "project_label_c": "Label C",
        }
        mock_generateAssessmentFiles.return_value = [{"result": True}]

        mock_plugin = MagicMock()
        mock_PluginImplementations.return_value = [mock_plugin]

        self.view.request.method = "POST"

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.view.request.route_url("dashboard"))

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getProjectAssessmentInfo.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_checkAssessments.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_getTheGroupOfThePackageCodeAssessment.assert_called_once_with(
            "test_project_id", "test_assessment", self.view.request
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_generateAssessmentFiles.assert_called_once_with(
            "test_user",
            "test_project_id",
            "test_project",
            "test_assessment",
            self.view.request,
            "section_code",
            ["Label A", "Label B", "Label C"],
        )
        mock_setAssessmentIndividualStatus.assert_called_once_with(
            "test_project_id", "test_assessment", 1, self.view.request
        )
        mock_createDocumentForm.assert_called_once_with(
            self.view,
            "test_user",
            "test_project_id",
            "test_project",
            "test_assessment",
            mock_getActiveProject.return_value,
        )
        mock_plugin.after_adding_form.assert_called_once_with(
            self.view.request,
            "test_user",
            "test_project_id",
            "test_project",
            "assessment",
            "test_assessment",
        )
        mock_plugin.create_Excel_template_for_upload_data.assert_called_once_with(
            self.view.request,
            "test_user",
            "test_project_id",
            "test_project",
            "assessment",
            "test_assessment",
        )


class TestAssessmentFormCreationView(unittest.TestCase):
    def setUp(self):

        self.request = MagicMock()

        self.view = AssessmentFormCreationView(self.request)
        self.view.user = MagicMock()
        self.view._ = MagicMock(side_effect=lambda x: x)  # Mock translation function
        self.view.request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "assessmentid": "test_assessment",
        }
        self.view.request.url_for_static = MagicMock(
            side_effect=lambda x: f"/static/{x}"
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    @patch("climmob.views.assessment.saveAssessmentOrder")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.Environment")
    def test_process_view_project_not_exist(
        self,
        mock_environment,
        mock_getDictForPreview,
        mock_getActiveProject,
        mock_getDataFormPreview,
        mock_saveAssessmentOrder,
        mock_getPrjLangDefaultInProject,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = False

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    @patch("climmob.views.assessment.saveAssessmentOrder")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.Environment")
    def test_process_view_get_method(
        self,
        mock_environment,
        mock_getDictForPreview,
        mock_getActiveProject,
        mock_getDataFormPreview,
        mock_saveAssessmentOrder,
        mock_getPrjLangDefaultInProject,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getPrjLangDefaultInProject.return_value = {"lang_code": "en"}

        self.view.request.method = "GET"

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, "")

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getPrjLangDefaultInProject.assert_called_once_with(
            "test_project_id", self.view.request
        )

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    @patch("climmob.views.assessment.saveAssessmentOrder")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.Environment")
    @patch("json.loads")
    def test_process_view_post_method(
        self,
        mock_json_loads,
        mock_environment,
        mock_getDictForPreview,
        mock_getActiveProject,
        mock_getDataFormPreview,
        mock_saveAssessmentOrder,
        mock_getPrjLangDefaultInProject,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getPrjLangDefaultInProject.return_value = {"lang_code": "en"}
        mock_saveAssessmentOrder.return_value = (True, None)
        mock_getDataFormPreview.return_value = ([], False)
        mock_getActiveProject.return_value = "active_project"
        mock_getDictForPreview.return_value = {}
        mock_json_loads.return_value = [{"type": "group", "id": 1}]

        mock_template = MagicMock()
        mock_environment.return_value.get_template.return_value = mock_template
        mock_template.render.return_value = "rendered_template"

        self.view.request.method = "POST"
        self.view.request.POST.get.return_value = json.dumps(
            [{"type": "group", "id": 1}]
        )

        result = self.view.processView()

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result, "rendered_template")

        mock_projectExists.assert_called_once_with(
            self.view.user.login, "test_user", "test_project", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.view.request
        )
        mock_getPrjLangDefaultInProject.assert_called_once_with(
            "test_project_id", self.view.request
        )
        mock_saveAssessmentOrder.assert_called_once_with(
            "test_project_id",
            "test_assessment",
            [{"type": "group", "id": 1}],
            self.view.request,
        )
        mock_getDataFormPreview.assert_called_once_with(
            self.view,
            "test_user",
            "test_project_id",
            language="en",
            assessmentid="test_assessment",
        )
        mock_getActiveProject.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_getDictForPreview.assert_called_once_with(
            self.view.request, "test_user", "en"
        )
        mock_template.render.assert_called_once()

    @patch("climmob.views.assessment.projectExists")
    @patch("climmob.views.assessment.getTheProjectIdForOwner")
    @patch("climmob.views.assessment.getPrjLangDefaultInProject")
    @patch("climmob.views.assessment.saveAssessmentOrder")
    @patch("climmob.views.assessment.getDataFormPreview")
    @patch("climmob.views.assessment.getActiveProject")
    @patch("climmob.views.assessment.getDictForPreview")
    @patch("climmob.views.assessment.Environment")
    @patch("json.loads")
    def test_process_view_post_method_with_error(
        self,
        mock_json_loads,
        mock_environment,
        mock_getDictForPreview,
        mock_getActiveProject,
        mock_getDataFormPreview,
        mock_saveAssessmentOrder,
        mock_getPrjLangDefaultInProject,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = "test_project_id"
        mock_getPrjLangDefaultInProject.return_value = {"lang_code": "en"}
        mock_getDataFormPreview.return_value = ([], False)

        mock_template = MagicMock()
        mock_environment.return_value.get_template.return_value = mock_template
        mock_template.render.return_value = "rendered_template"

        self.view.request.method = "POST"
        mock_json_loads.return_value = [{"type": "question"}, {"type": "question"}]

        with patch.object(self.view, "_", wraps=self.view._) as mock_translate:
            with self.assertRaises(AssertionError) as context:
                self.view.processView()

                self.assertIn(
                    "Questions cannot be outside a group",
                    self.view._("Questions cannot be outside a group"),
                )

                mock_projectExists.assert_called_once_with(
                    self.view.user.login, "test_user", "test_project", self.view.request
                )
                mock_getTheProjectIdForOwner.assert_called_once_with(
                    "test_user", "test_project", self.view.request
                )
                mock_getPrjLangDefaultInProject.assert_called_once_with(
                    "test_project_id", self.view.request
                )
                mock_saveAssessmentOrder.assert_not_called()
                mock_getDataFormPreview.assert_not_called()
                mock_getActiveProject.assert_not_called()
                mock_getDictForPreview.assert_not_called()
                mock_template.render.assert_not_called()


if __name__ == "__main__":
    unittest.main()
