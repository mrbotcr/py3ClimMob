import unittest
from unittest.mock import MagicMock, patch
from pyramid.httpexceptions import HTTPNotFound
from climmob.views.cleanErrorLogs import CleanErrorLogsView


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
            "secure.javascript": "false"
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

    @patch('climmob.views.cleanErrorLogs.projectExists', return_value=False)
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

    @patch('climmob.views.cleanErrorLogs.projectExists', return_value=True)
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner', return_value="mock_project_id")
    @patch('climmob.views.cleanErrorLogs.getProjectData', return_value={"project_regstatus": 1})
    def test_processView_project_exists(self, mock_getProjectData, mock_getTheProjectIdForOwner, mock_projectExists):
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
        mock_getProjectData.assert_called_with(
            "mock_project_id", self.request
        )

        # Verificamos que los valores en el request se hayan utilizado correctamente
        self.assertEqual(self.view.request.matchdict["user"], "test_user")
        self.assertEqual(self.view.request.matchdict["project"], "test_project")
        self.assertEqual(self.view.request.matchdict["formid"], "test_formid")

###

    @patch('climmob.views.cleanErrorLogs.projectExists', return_value=True)
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner', return_value='mock_project_id')
    @patch('climmob.views.cleanErrorLogs.getProjectData', return_value={"project_regstatus": "1"})
    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen', return_value=False)
    def test_processView_codeid_present_assessment_not_open(self, mock_isAssessmentOpen, mock_getProjectData, mock_getTheProjectIdForOwner, mock_projectExists):
        print("Iniciando prueba: test_processView_codeid_present_assessment_not_open")

        # Ejecutar el método que se está probando
        self.view.processView()

        # Verificar si la llamada a isAssessmentOpen se realizó correctamente
        mock_isAssessmentOpen.assert_called_with(
            "mock_project_id", "test_codeid", self.request
        )

        # Verificar el resto de las llamadas a los mocks
        mock_projectExists.assert_called_with(
            self.view.user.login, "test_user", "test_project", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_with(
            "test_user", "test_project", self.request
        )
        mock_getProjectData.assert_called_with(
            "mock_project_id", self.request
        )

        # Verificar que se lance la excepción HTTPNotFound
        try:
            self.view.processView()
        except HTTPNotFound:
            print("HTTPNotFound lanzado como se esperaba")
            return

        # Si no se lanza la excepción, falla la prueba
        self.fail("processView no lanzó HTTPNotFound cuando la evaluación no estaba abierta")


    @patch('climmob.views.cleanErrorLogs.projectExists', return_value=True)
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner', return_value='mock_project_id')
    @patch('climmob.views.cleanErrorLogs.getProjectData', return_value={"project_regstatus": "2"})
    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen', return_value=True)
    def test_processView_codeid_not_present_regstatus_2(self, mock_isAssessmentOpen, mock_getProjectData, mock_getTheProjectIdForOwner, mock_projectExists):
        """
        Esta prueba verifica el comportamiento de processView cuando codeid no está presente y project_regstatus es 2.
        """
        self.request.matchdict.pop("codeid", None)

        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch('climmob.views.cleanErrorLogs.projectExists', return_value=True)
    @patch('climmob.views.cleanErrorLogs.getTheProjectIdForOwner', return_value='mock_project_id')
    @patch('climmob.views.cleanErrorLogs.getProjectData', return_value={"project_regstatus": "1"})
    @patch('climmob.views.cleanErrorLogs.isAssessmentOpen', return_value=True)
    def test_processView_codeid_not_present(self, mock_isAssessmentOpen, mock_getProjectData, mock_getTheProjectIdForOwner, mock_projectExists):
        """
        Esta prueba verifica el comportamiento de processView cuando codeid no está presente en matchdict.
        """
        self.request.matchdict.pop("codeid", None)

        try:
            self.view.processView()
        except HTTPNotFound:
            self.fail("processView lanzó HTTPNotFound cuando codeid no estaba presente y project_regstatus no es 2")


if __name__ == '__main__':
    unittest.main()
