import unittest
from unittest.mock import MagicMock, patch

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.views.registry import (
    DeleteRegistrySectionView,
    actionsInSections,
    RegistrySectionActionsView,
    CancelRegistryView,
    CloseRegistryView,
    GetRegistrySectionView,
    createDocumentForm
)


class TestDeleteRegistrySectionView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "groupid": "test_group"
        }
        self.view = DeleteRegistrySectionView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.getRegistryGroupInformation', return_value={"group": "info"})
    def test_process_view_get(self, mock_getRegistryGroupInformation, mock_getTheProjectIdForOwner, mock_projectExists):
        # Mock request method to GET
        self.mock_request.method = "GET"

        # Call the processView method
        result = self.view.processView()

        # Assertions
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_getRegistryGroupInformation.assert_called_once_with("project_id", "test_group", self.mock_request)

        self.assertEqual(result["activeUser"], self.view.user)
        self.assertEqual(result["data"], {"group": "info"})
        self.assertEqual(result["groupid"], "test_group")

    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.getRegistryGroupInformation', return_value={"group": "info"})
    @patch('climmob.views.registry.deleteRegistryGroup', return_value=(False, "Delete Error"))
    def test_process_view_delete_failure(self, mock_deleteRegistryGroup, mock_getRegistryGroupInformation, mock_getTheProjectIdForOwner, mock_projectExists):
        # Mock request method to POST
        self.mock_request.method = "POST"

        # Call the processView method
        result = self.view.processView()

        # Assertions
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_deleteRegistryGroup.assert_called_once_with("project_id", "test_group", self.mock_request)

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result["status"], 400)
        self.assertEqual(result["error"], "Delete Error")

    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.getRegistryGroupInformation', return_value={"group": "info"})
    @patch('climmob.views.registry.deleteRegistryGroup', return_value=(True, ""))
    def test_process_view_delete_success(self, mock_deleteRegistryGroup, mock_getRegistryGroupInformation, mock_getTheProjectIdForOwner, mock_projectExists):
        # Mock request method to POST
        self.mock_request.method = "POST"

        # Call the processView method
        result = self.view.processView()

        # Assertions
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_deleteRegistryGroup.assert_called_once_with("project_id", "test_group", self.mock_request)

        self.assertTrue(self.view.returnRawViewResult)
        self.assertEqual(result["status"], 200)

    @patch('climmob.views.registry.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        # Mock request method to GET
        self.mock_request.method = "GET"

        # Call the processView method and assert HTTPNotFound is raised
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        # Assertions
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)


class TestActionsInSections(unittest.TestCase):
    def setUp(self):
        self.view = MagicMock()
        self.view._ = MagicMock(side_effect=lambda x: x)  # Mocking translation method

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.addRegistryGroup', return_value=(True, ""))
    def test_insert_success(self, mock_addRegistryGroup):
        postdata = {"action": "insert"}
        result = actionsInSections(self.view, postdata)

        mock_addRegistryGroup.assert_called_once_with(postdata, self.view)
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["success"], "The section was successfully added")

    @patch('climmob.views.registry.addRegistryGroup', return_value=(False, "repeated"))
    def test_insert_repeated_error(self, mock_addRegistryGroup):
        postdata = {"action": "insert"}
        result = actionsInSections(self.view, postdata)

        mock_addRegistryGroup.assert_called_once_with(postdata, self.view)
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["error"], "There is already a group with this name.")

    @patch('climmob.views.registry.addRegistryGroup', return_value=(False, "Some other error"))
    def test_insert_other_error(self, mock_addRegistryGroup):
        postdata = {"action": "insert"}
        result = actionsInSections(self.view, postdata)

        mock_addRegistryGroup.assert_called_once_with(postdata, self.view)
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["error"], "Some other error")

    @patch('climmob.views.registry.modifyRegistryGroup', return_value=(True, ""))
    def test_update_success(self, mock_modifyRegistryGroup):
        postdata = {"action": "update"}
        result = actionsInSections(self.view, postdata)

        mock_modifyRegistryGroup.assert_called_once_with(postdata, self.view)
        self.assertEqual(result["result"], "success")
        self.assertEqual(result["success"], "The section was successfully updated")

    @patch('climmob.views.registry.modifyRegistryGroup', return_value=(False, "repeated"))
    def test_update_repeated_error(self, mock_modifyRegistryGroup):
        postdata = {"action": "update"}
        result = actionsInSections(self.view, postdata)

        mock_modifyRegistryGroup.assert_called_once_with(postdata, self.view)
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["error"], "There is already a group with this name.")

    @patch('climmob.views.registry.modifyRegistryGroup', return_value=(False, "Some other error"))
    def test_update_other_error(self, mock_modifyRegistryGroup):
        postdata = {"action": "update"}
        result = actionsInSections(self.view, postdata)

        mock_modifyRegistryGroup.assert_called_once_with(postdata, self.view)
        self.assertEqual(result["result"], "error")
        self.assertEqual(result["error"], "Some other error")

class TestRegistrySectionActionsView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"user": "test_user", "project": "test_project"}
        self.view = RegistrySectionActionsView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.actionsInSections', return_value={"result": "success"})
    def test_process_view_post_insert_section(self, mock_actionsInSections, mock_projectExists, mock_getTheProjectIdForOwner):
        self.mock_request.method = "POST"
        self.mock_request.POST = {"action": "btnNewSection", "group_cod": "group_cod"}

        result = self.view.processView()

        self.assertEqual(result["result"], "success")
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_actionsInSections.assert_called_once()
        postdata = mock_actionsInSections.call_args[0][1]
        self.assertEqual(postdata["action"], "insert")
        self.assertNotIn("group_cod", postdata)

    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.actionsInSections', return_value={"result": "success"})
    def test_process_view_post_update_section(self, mock_actionsInSections, mock_projectExists, mock_getTheProjectIdForOwner):
        self.mock_request.method = "POST"
        self.mock_request.POST = {"action": "btnUpdateSection"}

        result = self.view.processView()

        self.assertEqual(result["result"], "success")
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_actionsInSections.assert_called_once()
        postdata = mock_actionsInSections.call_args[0][1]
        self.assertEqual(postdata["action"], "update")

    @patch('climmob.views.registry.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        with self.assertRaises(HTTPNotFound):
            self.view.processView()
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)

class TestCancelRegistryView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"user": "test_user", "project": "test_project"}
        self.view = CancelRegistryView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.getActiveProject', return_value={"project": "active_project"})
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    def test_process_view_get(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getActiveProject):
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(result["activeUser"], self.view.user)
        self.assertFalse(result["redirect"])
        self.assertEqual(result["activeProject"], {"project": "active_project"})
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_getActiveProject.assert_called_once_with("test_user", self.mock_request)

    @patch('climmob.views.registry.getActiveProject', return_value={"project": "active_project"})
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.setRegistryStatus')
    @patch('climmob.views.registry.clean_registry_error_logs')
    @patch('climmob.views.registry.stopTasksByProcess')
    @patch('climmob.views.registry.p.PluginImplementations')
    def test_process_view_post_cancel_registry(self, mock_pluginImplementations, mock_stopTasksByProcess, mock_clean_registry_error_logs, mock_setRegistryStatus, mock_projectExists, mock_getTheProjectIdForOwner, mock_getActiveProject):
        self.mock_request.method = "POST"
        self.mock_request.params = {"cancelRegistry": "1"}
        mock_plugin = MagicMock()
        mock_pluginImplementations.return_value = [mock_plugin]

        result = self.view.processView()

        mock_setRegistryStatus.assert_called_once_with("test_user", "test_project", "project_id", 0, self.mock_request)
        mock_clean_registry_error_logs.assert_called_once_with(self.mock_request, "project_id")
        mock_stopTasksByProcess.assert_called_once_with(self.mock_request, "project_id")
        mock_plugin.after_deleting_form.assert_called_once_with(self.mock_request, "test_user", "project_id", "test_project", "registry", "")
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.mock_request.route_url("dashboard"))

    @patch('climmob.views.registry.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        with self.assertRaises(HTTPNotFound):
            self.view.processView()
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)

class TestCloseRegistryView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"user": "test_user", "project": "test_project"}
        self.view = CloseRegistryView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.getActiveProject', return_value={"project": "active_project"})
    @patch('climmob.views.registry.getProjectProgress', return_value=("progress", "completed"))
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    def test_process_view_get(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectProgress, mock_getActiveProject):
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(result["activeUser"], self.view.user)
        self.assertFalse(result["redirect"])
        self.assertEqual(result["progress"], "progress")
        self.assertEqual(result["activeProject"], {"project": "active_project"})
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_getProjectProgress.assert_called_once_with("test_user", "test_project", "project_id", self.mock_request)
        mock_getActiveProject.assert_called_once_with("test_user", self.mock_request)

    @patch('climmob.views.registry.getActiveProject', return_value={"project": "active_project"})
    @patch('climmob.views.registry.getProjectProgress', return_value=("progress", "completed"))
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.setRegistryStatus')
    @patch('climmob.views.registry.p.PluginImplementations')
    def test_process_view_post_close_registry(self, mock_pluginImplementations, mock_setRegistryStatus, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectProgress, mock_getActiveProject):
        self.mock_request.method = "POST"
        self.mock_request.params = {"closeRegistry": "1"}
        mock_plugin = MagicMock()
        mock_pluginImplementations.return_value = [mock_plugin]

        result = self.view.processView()

        mock_setRegistryStatus.assert_called_once_with("test_user", "test_project", "project_id", 2, self.mock_request)
        mock_plugin.after_deleting_form.assert_called_once_with(self.mock_request, "test_user", "project_id", "test_project", "registry", "")
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.mock_request.route_url("dashboard"))

    @patch('climmob.views.registry.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        with self.assertRaises(HTTPNotFound):
            self.view.processView()
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)

class TestCloseRegistryView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"user": "test_user", "project": "test_project"}
        self.view = CloseRegistryView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.getActiveProject', return_value={"project": "active_project"})
    @patch('climmob.views.registry.getProjectProgress', return_value=("progress", "completed"))
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    def test_process_view_get(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectProgress, mock_getActiveProject):
        self.mock_request.method = "GET"

        result = self.view.processView()

        self.assertEqual(result["activeUser"], self.view.user)
        self.assertFalse(result["redirect"])
        self.assertEqual(result["progress"], "progress")
        self.assertEqual(result["activeProject"], {"project": "active_project"})
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_getProjectProgress.assert_called_once_with("test_user", "test_project", "project_id", self.mock_request)
        mock_getActiveProject.assert_called_once_with("test_user", self.mock_request)

    @patch('climmob.views.registry.getActiveProject', return_value={"project": "active_project"})
    @patch('climmob.views.registry.getProjectProgress', return_value=("progress", "completed"))
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="project_id")
    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.setRegistryStatus')
    @patch('climmob.views.registry.p.PluginImplementations')
    def test_process_view_post_close_registry(self, mock_pluginImplementations, mock_setRegistryStatus, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectProgress, mock_getActiveProject):
        self.mock_request.method = "POST"
        self.mock_request.params = {"closeRegistry": "1"}
        mock_plugin = MagicMock()
        mock_pluginImplementations.return_value = [mock_plugin]

        result = self.view.processView()

        mock_setRegistryStatus.assert_called_once_with("test_user", "test_project", "project_id", 2, self.mock_request)
        mock_plugin.after_deleting_form.assert_called_once_with(self.mock_request, "test_user", "project_id", "test_project", "registry", "")
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.location, self.mock_request.route_url("dashboard"))

    @patch('climmob.views.registry.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        with self.assertRaises(HTTPNotFound):
            self.view.processView()
        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)

class TestGetRegistrySectionView(unittest.TestCase):

    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "section": "test_section"
        }
        self.mock_request.method = "GET"
        self.view = GetRegistrySectionView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="test_project_id")
    @patch('climmob.views.registry.getRegistryGroupInformation', return_value={"section_data": "some_data"})
    def test_process_view_success(self, mock_getRegistryGroupInformation, mock_getTheProjectIdForOwner, mock_projectExists):
        result = self.view.processView()

        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)
        mock_getRegistryGroupInformation.assert_called_once_with("test_project_id", "test_section", self.mock_request)

        self.assertEqual(result, {"section_data": "some_data"})

    @patch('climmob.views.registry.projectExists', return_value=False)
    def test_process_view_project_not_exists(self, mock_projectExists):
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)

    @patch('climmob.views.registry.projectExists', return_value=True)
    @patch('climmob.views.registry.getTheProjectIdForOwner', return_value="test_project_id")
    def test_process_view_non_get_method(self, mock_getTheProjectIdForOwner, mock_projectExists):
        self.mock_request.method = "POST"
        result = self.view.processView()

        mock_projectExists.assert_called_once_with("test_user", "test_user", "test_project", self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with("test_user", "test_project", self.mock_request)

        self.assertEqual(result, {})


class TestCreateDocumentForm(unittest.TestCase):

    def setUp(self):
        self.mock_self = MagicMock()
        self.mock_self.request = MagicMock()
        self.userOwner = "test_user"
        self.projectId = "test_project_id"
        self.locale = "en"
        self.projectCod = "test_project_cod"
        self.listOfLabelsForPackages = ["label1", "label2", "label3"]

    @patch('climmob.views.registry.getDataFormPreview', return_value=(["data"], "finalCloseQst"))
    @patch('climmob.views.registry.create_document_form')
    def test_create_document_form_with_languages(self, mock_create_document_form, mock_getDataFormPreview):
        languages = [
            {"lang_code": "en", "lang_name": "English"},
            {"lang_code": "es", "lang_name": "Spanish"}
        ]

        createDocumentForm(languages, self.mock_self, self.userOwner, self.projectId, self.locale, self.projectCod,
                           self.listOfLabelsForPackages)

        self.assertEqual(languages[0]["Data"], ["data"])
        self.assertEqual(languages[1]["Data"], ["data"])

        mock_getDataFormPreview.assert_any_call(self.mock_self, self.userOwner, self.projectId, language="en")
        mock_getDataFormPreview.assert_any_call(self.mock_self, self.userOwner, self.projectId, language="es")

        mock_create_document_form.assert_called_once_with(
            self.mock_self.request,
            self.locale,
            self.userOwner,
            self.projectId,
            self.projectCod,
            "Registration",
            "",
            languages,
            self.listOfLabelsForPackages
        )

    @patch('climmob.views.registry.getDataFormPreview', return_value=(["data"], "finalCloseQst"))
    @patch('climmob.views.registry.create_document_form')
    def test_create_document_form_without_languages(self, mock_create_document_form, mock_getDataFormPreview):
        languages = []

        createDocumentForm(languages, self.mock_self, self.userOwner, self.projectId, self.locale, self.projectCod,
                           self.listOfLabelsForPackages)

        mock_getDataFormPreview.assert_called_once_with(self.mock_self, self.userOwner, self.projectId,
                                                        language=self.locale)

        dataPreviewInMultipleLanguages = [
            {"lang_code": self.locale, "lang_name": "Default", "Data": ["data"]}
        ]

        mock_create_document_form.assert_called_once_with(
            self.mock_self.request,
            self.locale,
            self.userOwner,
            self.projectId,
            self.projectCod,
            "Registration",
            "",
            dataPreviewInMultipleLanguages,
            self.listOfLabelsForPackages
        )


if __name__ == '__main__':
    unittest.main()
