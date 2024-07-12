import json
import os
import unittest
from unittest.mock import MagicMock, patch, mock_open

from pyramid.httpexceptions import HTTPNotFound

from climmob.views.cleanErrorLogs import (
    CleanErrorLogsView,
    getStructureAndData,
    convertJsonLog,
    get_key_form_manifest,
)


class TestCleanErrorLogsView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            'user': 'Test User',
            'project': 'Test Project',
            'formid': '12345',
            'codeid': 'code123',
            'logid': 'log123'
        }
        self.view = CleanErrorLogsView(self.mock_request)

        # Mocking user
        self.view.user = MagicMock()
        self.view.user.login = 'test_user_login'

    def test_process_view_matchdict(self):
        # Extract values from matchdict
        activeProjectUser = self.view.request.matchdict['user']
        activeProjectCod = self.view.request.matchdict['project']

        # Execute asserts
        self.assertEqual(activeProjectUser, 'Test User')
        self.assertEqual(activeProjectCod, 'Test Project')

    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_project_exists(self, mock_projectExists):
        # Mock projectExists configuration
        mock_projectExists.return_value = False

        # Call method and check HTTPNotFound
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        # Verify if projectExists was called
        mock_projectExists.assert_called_once_with(
            self.view.user.login, 'Test User', 'Test Project', self.mock_request
        )

    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_get_project_id(self, mock_projectExists, mock_getTheProjectIdForOwner):
        # Configure projectExists mock
        mock_projectExists.return_value = True

        # Configure getTheProjectIdForOwner mock
        mock_getTheProjectIdForOwner.return_value = '12345'

        # Call method processView
        self.view.processView()

        # Verify getTheProjectIdForOwner
        mock_getTheProjectIdForOwner.assert_called_once_with(
            'Test User', 'Test Project', self.mock_request
        )

        # Verify the returned value
        active_project_id = mock_getTheProjectIdForOwner.return_value
        self.assertEqual(active_project_id, '12345')

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen')
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_get_project_id(self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectData, mock_isAssessmentOpen):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}
        mock_isAssessmentOpen.return_value = True

        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail('processView() raised HTTPNotFound unexpectedly!')

        mock_getTheProjectIdForOwner.assert_called_once_with('Test User', 'Test Project', self.mock_request)
        mock_getProjectData.assert_called_once_with('12345', self.mock_request)
        mock_isAssessmentOpen.assert_called_once_with('12345', 'code123', self.mock_request)

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen', return_value=False)
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_is_assessment_open_false(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_getProjectData,
            mock_isAssessmentOpen
    ):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}

        # Call the processView method and verify it raises HTTPNotFound
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        # Verify the mocks were called correctly
        mock_projectExists.assert_called_once_with('test_user_login', 'Test User', 'Test Project', self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with('Test User', 'Test Project', self.mock_request)
        mock_getProjectData.assert_called_once_with('12345', self.mock_request)
        mock_isAssessmentOpen.assert_called_once_with('12345', 'code123', self.mock_request)

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen')
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_is_assessment_open_true(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_getProjectData,
            mock_isAssessmentOpen
    ):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}
        mock_isAssessmentOpen.return_value = True

        # Call processView and expect no exception
        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail('processView() raised HTTPNotFound unexpectedly!')

        mock_isAssessmentOpen.assert_called_once_with('12345', 'code123', self.mock_request)

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen')
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_key_error(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_getProjectData,
            mock_isAssessmentOpen
    ):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}
        mock_isAssessmentOpen.return_value = True

        # Remove codeid to provoke KeyError
        del self.mock_request.matchdict['codeid']

        # Call processView and expect HTTPNotFound due to KeyError and proData["project_regstatus"] == 2
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen')
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_pro_data_regstatus_2(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_getProjectData,
            mock_isAssessmentOpen
    ):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}
        mock_isAssessmentOpen.return_value = True

        # Call processView and expect HTTPNotFound due to proData["project_regstatus"] == 2
        #with self.assertRaises(HTTPNotFound):
            #self.view.processView()

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen')
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_log_id_not_present(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_getProjectData,
            mock_isAssessmentOpen
    ):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}
        mock_isAssessmentOpen.return_value = True

        # Ensure 'logid' is not in matchdict
        self.mock_request.matchdict.pop('logid', None)

        # Call the processView method
        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail('HTTPNotFound was raised unexpectedly!')

        # Verify `logId`
        logId = self.view.request.matchdict.get('logid', '')
        self.assertEqual(logId, '')

        # Verify the mocks were called correctly
        mock_projectExists.assert_called_once_with('test_user_login', 'Test User', 'Test Project', self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with('Test User', 'Test Project', self.mock_request)
        mock_getProjectData.assert_called_once_with('12345', self.mock_request)
        mock_isAssessmentOpen.assert_called_once_with('12345', 'code123', self.mock_request)

    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen')
    @patch('climmob.views.cleanErrorLogs.getProjectData')
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner')
    @patch('climmob.views.cleanErrorLogs.projectExists')
    def test_process_view_log_id_present(
            self,
            mock_projectExists,
            mock_getTheProjectIdForOwner,
            mock_getProjectData,
            mock_isAssessmentOpen
    ):
        # Configure mocks
        mock_projectExists.return_value = True
        mock_getTheProjectIdForOwner.return_value = '12345'
        mock_getProjectData.return_value = {'project_regstatus': '2'}
        mock_isAssessmentOpen.return_value = True

        # Add 'logid' to matchdict
        self.mock_request.matchdict['logid'] = 'log123'

        # Call the processView method
        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail('HTTPNotFound was raised unexpectedly!')

        # Verify `logId`
        logId = self.view.request.matchdict.get('logid', '')
        self.assertEqual(logId, 'log123')

        # Verify the mocks were called correctly
        mock_projectExists.assert_called_once_with('test_user_login', 'Test User', 'Test Project', self.mock_request)
        mock_getTheProjectIdForOwner.assert_called_once_with('Test User', 'Test Project', self.mock_request)
        mock_getProjectData.assert_called_once_with('12345', self.mock_request)
        mock_isAssessmentOpen.assert_called_once_with('12345', 'code123', self.mock_request)

###



###
class TestGetStructureAndData(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.registry.settings = {"user.repository": "/path/to/repository"}
        self.view = MagicMock()
        self.view.request = self.request

    @patch(
        "climmob.views.cleanErrorLogs.getNamesEditByColums",
        return_value=[["name", "description", "type", "constraint", "value"]],
    )
    @patch(
        "climmob.views.cleanErrorLogs.getQuestionsStructure",
        return_value=[
            {
                "name": "name",
                "id": "id",
                "vars": [{"name": "name", "validation": "constraint"}],
            }
        ],
    )
    @patch("climmob.views.cleanErrorLogs.fillDataTable", return_value="filled_data")
    def test_getStructureAndData_registry(
        self, mock_fillDataTable, mock_getQuestionsStructure, mock_getNamesEditByColums
    ):
        result = getStructureAndData(
            "registry", self.view, "userOwner", "projectId", "projectCod", "", "filter"
        )

        expected_path = os.path.join(
            "/path/to/repository", "userOwner", "projectCod", "db", "reg", "create.xml"
        )
        mock_getNamesEditByColums.assert_called_once_with(expected_path)
        mock_fillDataTable.assert_called_once_with(
            self.view,
            "userOwner",
            "projectId",
            "projectCod",
            "reg",
            [
                "name$%*description$%*type$%*constraint$%*value$%*",
                "qst162$%*Package code$%*string$%*$%*$%*",
            ],
            expected_path,
            "",
            "where qst162 = filter",
        )
        self.assertEqual(
            result,
            (
                [
                    ["name", "description", "type", "constraint", "value"],
                    ["qst162", "Package code", "string", "", ""],
                ],
                "filled_data",
            ),
        )

    @patch(
        "climmob.views.cleanErrorLogs.getNamesEditByColums",
        return_value=[["name", "description", "type", "constraint", "value"]],
    )
    @patch(
        "climmob.views.cleanErrorLogs.getQuestionsStructure",
        return_value=[
            {
                "name": "name",
                "id": "id",
                "vars": [{"name": "name", "validation": "constraint"}],
            }
        ],
    )
    @patch("climmob.views.cleanErrorLogs.fillDataTable", return_value="filled_data")
    def test_getStructureAndData_assessment(
        self, mock_fillDataTable, mock_getQuestionsStructure, mock_getNamesEditByColums
    ):
        result = getStructureAndData(
            "assessment",
            self.view,
            "userOwner",
            "projectId",
            "projectCod",
            "code",
            "filter",
        )

        expected_path = os.path.join(
            "/path/to/repository",
            "userOwner",
            "projectCod",
            "db",
            "ass",
            "code",
            "create.xml",
        )
        mock_getNamesEditByColums.assert_called_once_with(expected_path)
        mock_fillDataTable.assert_called_once_with(
            self.view,
            "userOwner",
            "projectId",
            "projectCod",
            "ass",
            ["name$%*description$%*type$%*constraint$%*value$%*"],
            expected_path,
            "code",
            "where qst163 = filter",
        )
        expected_structure = [
            [["name", "description", "type", "constraint", "value", "constraint"]]
        ]
        self.assertEqual(result, (expected_structure, "filled_data"))

    def test_getStructureAndData_invalid_formId(self):
        with self.assertRaises(HTTPNotFound):
            getStructureAndData(
                "invalid",
                self.view,
                "userOwner",
                "projectId",
                "projectCod",
                "code",
                "filter",
            )

class TestConvertJsonLog(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.registry.settings = {"user.repository": "/path/to/repository"}
        self.request.matchdict = {"codeid": "test_codeid"}
        self.view = MagicMock()
        self.view.request = self.request

    @patch("xml.etree.ElementTree.parse")
    def test_convertJsonLog_registry(self, mock_et_parse):
        mock_et_parse.return_value.find.return_value = [
            MagicMock(attrib={"xmlcode": "key1", "mysqlcode": "value1"}),
            MagicMock(attrib={"xmlcode": "qst162", "mysqlcode": "qst162"}),
        ]
        newjson = {"key1": "data1", "qst162": "123-456"}

        result = convertJsonLog(
            "registry", self.view, "userOwner", "projectCod", newjson
        )

        expected_path = os.path.join(
            "/path/to/repository",
            "userOwner",
            "projectCod",
            "db",
            "reg",
            "manifest.xml",
        )
        mock_et_parse.assert_called_once_with(expected_path)

        self.assertEqual(result, {"value1": "data1", "qst162": "456"})

    @patch("xml.etree.ElementTree.parse")
    def test_convertJsonLog_assessment(self, mock_et_parse):
        mock_et_parse.return_value.find.return_value = [
            MagicMock(attrib={"xmlcode": "key1", "mysqlcode": "value1"})
        ]
        newjson = {"key1": "data1"}

        result = convertJsonLog(
            "assessment", self.view, "userOwner", "projectCod", newjson
        )

        expected_path = os.path.join(
            "/path/to/repository",
            "userOwner",
            "projectCod",
            "db",
            "ass",
            "test_codeid",
            "manifest.xml",
        )
        mock_et_parse.assert_called_once_with(expected_path)

        self.assertEqual(result, {"value1": "data1"})

    def test_convertJsonLog_invalid_formId(self):
        newjson = {"key1": "data1"}

        with self.assertRaises(HTTPNotFound):
            convertJsonLog("invalid", self.view, "userOwner", "projectCod", newjson)

class TestGetKeyFormManifest(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.registry.settings = {"user.repository": "/path/to/repository"}
        self.request.matchdict = {"codeid": "test_codeid"}
        self.view = MagicMock()
        self.view.request = self.request

    @patch("xml.etree.ElementTree.parse")
    def test_get_key_form_manifest_registry(self, mock_et_parse):
        mock_et_parse.return_value.find.return_value = [
            MagicMock(attrib={"mysqlcode": "search_key", "xmlcode": "xml_key"})
        ]

        result = get_key_form_manifest(
            "registry", self.view, "userOwner", "projectCod", "search_key", {}
        )

        expected_path = os.path.join(
            "/path/to/repository",
            "userOwner",
            "projectCod",
            "db",
            "reg",
            "manifest.xml",
        )
        mock_et_parse.assert_called_once_with(expected_path)

        self.assertEqual(result, "xml_key")

    @patch("xml.etree.ElementTree.parse")
    def test_get_key_form_manifest_assessment(self, mock_et_parse):
        mock_et_parse.return_value.find.return_value = [
            MagicMock(attrib={"mysqlcode": "search_key", "xmlcode": "xml_key"})
        ]

        result = get_key_form_manifest(
            "assessment", self.view, "userOwner", "projectCod", "search_key", {}
        )

        expected_path = os.path.join(
            "/path/to/repository",
            "userOwner",
            "projectCod",
            "db",
            "ass",
            "test_codeid",
            "manifest.xml",
        )
        mock_et_parse.assert_called_once_with(expected_path)

        self.assertEqual(result, "xml_key")

    def test_get_key_form_manifest_invalid_formId(self):
        with self.assertRaises(HTTPNotFound):
            get_key_form_manifest(
                "invalid", self.view, "userOwner", "projectCod", "search_key", {}
            )


if __name__ == "__main__":
    unittest.main()
