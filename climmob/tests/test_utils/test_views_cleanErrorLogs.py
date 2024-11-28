import json
import os
import unittest
from unittest.mock import MagicMock, patch, mock_open

from pyramid.httpexceptions import HTTPNotFound

from climmob.views.cleanErrorLogs import (
    getStructureAndData,
    convertJsonLog,
    get_key_form_manifest,
)


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
