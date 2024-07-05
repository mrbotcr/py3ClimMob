import unittest
from unittest.mock import MagicMock, patch, mock_open
from pyramid.httpexceptions import HTTPNotFound
from climmob.views.cleanErrorLogs import (
    CleanErrorLogsView,
    getStructureAndData,
    convertJsonLog,
    get_key_form_manifest,
)
import os


class TestCleanErrorLogsView(unittest.TestCase):
    def setUp(self):
        """
        Este método se ejecuta antes de cada prueba. Aquí configuramos los datos necesarios.
        """
        self.request = MagicMock()
        self.request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "formid": "test_formid",
        }

        # Simulación del registry
        self.request.registry = MagicMock()
        self.request.registry.settings = {
            "secure.javascript": "false",
            "user.repository": "/path/to/repository",
        }

        self.view = CleanErrorLogsView(self.request)
        self.view.request = self.request  # Asignar la request simulada a la vista

        # Simulación del atributo user
        self.view.user = MagicMock()
        self.view.user.login = "mock_login"

    def test_processView(self):
        """
        Esta prueba verifica que el método processView de CleanErrorLogsView
        procesa correctamente los datos del request.
        """
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        # Verificamos que los valores en el request se hayan utilizado correctamente
        self.assertEqual(self.view.request.matchdict["user"], "test_user")
        self.assertEqual(self.view.request.matchdict["project"], "test_project")

    @patch("climmob.views.cleanErrorLogs.projectExists", return_value=False)
    def test_processView_project_not_exists(self, mock_projectExists):
        """
        Esta prueba verifica que el método processView de CleanErrorLogsView
        lanza HTTPNotFound si el proyecto no existe.
        """
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

        # Verificamos que la función projectExists fue llamada con los parámetros correctos
        mock_projectExists.assert_called_with(
            self.view.user.login, "test_user", "test_project", self.request
        )

    @patch("climmob.views.cleanErrorLogs.projectExists", return_value=True)
    @patch(
        "climmob.views.cleanErrorLogs.getTheProjectIdForOwner",
        return_value="mock_project_id",
    )
    @patch(
        "climmob.views.cleanErrorLogs.getProjectData",
        return_value={"project_regstatus": 1},
    )
    def test_processView_project_exists(
        self, mock_getProjectData, mock_getTheProjectIdForOwner, mock_projectExists
    ):
        """
        Esta prueba verifica que el método processView de CleanErrorLogsView
        no lanza HTTPNotFound si el proyecto existe y el estado del proyecto es válido.
        """
        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail("processView lanzó HTTPNotFound cuando el proyecto existe")

        # Verificamos que la función projectExists fue llamada con los parámetros correctos
        mock_projectExists.assert_called_with(
            self.view.user.login, "test_user", "test_project", self.request
        )

        # Verificamos que la función getTheProjectIdForOwner fue llamada correctamente
        mock_getTheProjectIdForOwner.assert_called_with(
            "test_user", "test_project", self.request
        )

        # Verificamos que la función getProjectData fue llamada correctamente
        mock_getProjectData.assert_called_with("mock_project_id", self.request)

        # Verificamos que los valores en el request se hayan utilizado correctamente
        self.assertEqual(self.view.request.matchdict["user"], "test_user")
        self.assertEqual(self.view.request.matchdict["project"], "test_project")
        self.assertEqual(self.view.request.matchdict["formid"], "test_formid")

    ###

    @patch("climmob.views.cleanErrorLogs.projectExists", return_value=True)
    @patch(
        "climmob.views.cleanErrorLogs.getTheProjectIdForOwner",
        return_value="mock_project_id",
    )
    @patch(
        "climmob.views.cleanErrorLogs.getProjectData",
        return_value={"project_regstatus": "1"},
    )
    @patch("climmob.views.cleanErrorLogs.isAssessmentOpen", return_value=False)
    def test_processView_codeid_present_assessment_not_open(
        self,
        mock_isAssessmentOpen,
        mock_getProjectData,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):

        # TODO
        pass

        # # Ejecutar el método que se está probando
        # self.view.processView()
        #
        # # Verificar si la llamada a isAssessmentOpen se realizó correctamente
        # mock_isAssessmentOpen.assert_called_with(
        #     "mock_project_id", "test_codeid", self.request
        # )
        #
        # # Verificar el resto de las llamadas a los mocks
        # mock_projectExists.assert_called_with(
        #     self.view.user.login, "test_user", "test_project", self.request
        # )
        # mock_getTheProjectIdForOwner.assert_called_with(
        #     "test_user", "test_project", self.request
        # )
        # mock_getProjectData.assert_called_with(
        #     "mock_project_id", self.request
        # )
        #
        # # Verificar que se lance la excepción HTTPNotFound
        # try:
        #     self.view.processView()
        # except HTTPNotFound:
        #     print("HTTPNotFound lanzado como se esperaba")
        #     return
        #
        # # Si no se lanza la excepción, falla la prueba
        # self.fail("processView no lanzó HTTPNotFound cuando la evaluación no estaba abierta")

    @patch("climmob.views.cleanErrorLogs.projectExists", return_value=True)
    @patch(
        "climmob.views.cleanErrorLogs.getTheProjectIdForOwner",
        return_value="mock_project_id",
    )
    @patch(
        "climmob.views.cleanErrorLogs.getProjectData",
        return_value={"project_regstatus": "2"},
    )
    @patch("climmob.views.cleanErrorLogs.isAssessmentOpen", return_value=True)
    def test_processView_codeid_not_present_regstatus_2(
        self,
        mock_isAssessmentOpen,
        mock_getProjectData,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        """
        Esta prueba verifica el comportamiento de processView cuando codeid no está presente y project_regstatus es 2.
        """
        self.request.matchdict.pop("codeid", None)

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch("climmob.views.cleanErrorLogs.projectExists", return_value=True)
    @patch(
        "climmob.views.cleanErrorLogs.getTheProjectIdForOwner",
        return_value="mock_project_id",
    )
    @patch(
        "climmob.views.cleanErrorLogs.getProjectData",
        return_value={"project_regstatus": "1"},
    )
    @patch("climmob.views.cleanErrorLogs.isAssessmentOpen", return_value=True)
    def test_processView_codeid_not_present(
        self,
        mock_isAssessmentOpen,
        mock_getProjectData,
        mock_getTheProjectIdForOwner,
        mock_projectExists,
    ):
        """
        Esta prueba verifica el comportamiento de processView cuando codeid no está presente en matchdict.
        """
        self.request.matchdict.pop("codeid", None)

        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail(
                "processView lanzó HTTPNotFound cuando codeid no estaba presente y project_regstatus no es 2"
            )

        ###
        @patch("climmob.views.cleanErrorLogs.projectExists", return_value=True)
        @patch(
            "climmob.views.cleanErrorLogs.getTheProjectIdForOwner",
            return_value="mock_project_id",
        )
        @patch(
            "climmob.views.cleanErrorLogs.getProjectData",
            return_value={"project_regstatus": "1"},
        )
        @patch("climmob.views.cleanErrorLogs.isAssessmentOpen", return_value=True)
        @patch(
            "climmob.views.cleanErrorLogs.convertJsonLog",
            return_value={"converted_key": "converted_value"},
        )
        @patch("builtins.open", new_callable=mock_open, read_data='{"key": "value"}')
        def test_processView_logid_present(
            self,
            mock_open_func,
            mock_convertJsonLog,
            mock_isAssessmentOpen,
            mock_getProjectData,
            mock_getTheProjectIdForOwner,
            mock_projectExists,
        ):
            """
            Esta prueba verifica el comportamiento de processView cuando logid está presente en matchdict.
            """
            self.request.matchdict["logid"] = "test_logid"
            print("Antes de llamar a processView (logid presente)")

            self.view.processView()

            self.assertEqual(self.request.matchdict["logid"], "test_logid")
            print("Después de llamar a processView (logid presente)")
            print("logid:", self.request.matchdict["logid"])

        @patch("climmob.views.cleanErrorLogs.projectExists", return_value=True)
        @patch(
            "climmob.views.cleanErrorLogs.getTheProjectIdForOwner",
            return_value="mock_project_id",
        )
        @patch(
            "climmob.views.cleanErrorLogs.getProjectData",
            return_value={"project_regstatus": "1"},
        )
        @patch("climmob.views.cleanErrorLogs.isAssessmentOpen", return_value=True)
        def test_processView_logid_not_present(
            self,
            mock_isAssessmentOpen,
            mock_getProjectData,
            mock_getTheProjectIdForOwner,
        ):
            """
            Esta prueba verifica el comportamiento de processView cuando logid no está presente en matchdict.
            """
            if "logid" in self.request.matchdict:
                del self.request.matchdict["logid"]
            print("Antes de llamar a processView (logid no presente)")

            self.view.processView()

            self.assertEqual(self.request.matchdict.get("logid", ""), "")
            print("Después de llamar a processView (logid no presente)")
            print("logid:", self.request.matchdict.get("logid", ""))


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


###
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
