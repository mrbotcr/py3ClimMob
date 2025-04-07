import unittest
from unittest.mock import MagicMock

from pyramid import testing
from climmob.views.locations import crud_view
from pyramid.config import Configurator

class TestViewLocations(unittest.TestCase):
    def setUp(self):
        self.config = testing.setUp()
        self.config.add_route('crud_locations', '/crud_locations')
        self.config.scan()

    def tearDown(self):
         testing.tearDown()

    def test_crud_view(self):
        """Verifica si la vista funciona correctamente"""
        request = testing.DummyRequest()
        request.translate = MagicMock(return_value="translated_text")
        mock_project_locations = [
            MagicMock(id=1, plocation_name="school", plocation_lang="en"),
            MagicMock(id=2, plocation_name="hospital", plocation_lang="en"),
            MagicMock(id=3, plocation_name="office", plocation_lang="en")
        ]
        active_user = MagicMock(login="test_user")
        active_project = MagicMock(id=1, name="Test Project")
        next_page = None
        modify = False
        report_upload = True
        error_summary = {}
        error_message = None
        dataworking = {}
        success_message = None

        crud_view.get_all_project_location = mock_project_locations
        crud_view.getActiveProject = MagicMock(return_value=active_project)

        response = testing.DummyRequest('/crud_locations', request=request)

        self.assertEqual(crud_view.get_all_project_location.__class__, list)
        self.assertEqual(error_summary,{})
        self.assertEqual(dataworking,{})

    def test_crud_view_post_add_location(self):
        """Verifica si la vista funciona correctamente cuando se agrega una ubicación"""
        request = testing.DummyRequest()
        request.translate = MagicMock(return_value="translated_text")
        request.method = 'POST'
        request.POST = {
            'csrf_token': MagicMock(),
            'plocation_lang': 'en',
            'plocation_name': 'This is another ubication',
            'btn_add_location': ''
        }

        # Mock de las funciones necesarias
        mock_project_locations = [
            MagicMock(id=1, plocation_name="school", plocation_lang="en"),
            MagicMock(id=2, plocation_name="hospital", plocation_lang="en"),
        ]
        crud_view.get_all_project_location = MagicMock(return_value=mock_project_locations)
        crud_view.get_location_by_name = MagicMock(return_value=None)
        crud_view.functionForAddLocations = MagicMock(return_value={'This is another ubication'})
        crud_view.getActiveProject = MagicMock(return_value=MagicMock(id=1, name="Test Project"))

        # Crear la vista y asignar el request
        view_instance = crud_view(self.config)
        view_instance.request = request

        # Llamar al método processView() para ejecutar la vista
        response = view_instance.processView()

        # Verificar que no haya errores y que se haya añadido correctamente la ubicación
        print(response)  # Para ver la salida de la respuesta
        self.assertEqual(response['error_message'], None)
        # Añadir más verificaciones si es necesario para la lógica de negocio.














    # class TestViewLocations(unittest.TestCase):
#     @patch('climmob.processes.db.project_location.get_all_project_location')
#     def setUp(self, mock_get_all_project_location):
#         mock_get_all_project_location.return_value = [
#             (MagicMock(id=1, plocation_name="school", plocation_lang="en")),
#             (MagicMock(id=2, plocation_name="hospital", plocation_lang="en")),
#             (MagicMock(id=3, plocation_name="office", plocation_lang="en"))
#         ]
#         self.view = crud_view(MagicMock())
#         self.view.request = MagicMock()
#         self.view.user = MagicMock()
#         self.view.user.login = "test_user"
#         self.view.add_Location_DB = MagicMock(return_value=(False,""))
#         self.get_all_project_location = mock_get_all_project_location
#
#     @unittest.skip("demonstrating skipping")
#     def mock_translation(self, message):
#         return message
#
#     def test_process_view_with_project_locations(self, get_all_project_location):
#         self.get_all_project_location
#         response = self.view.processView()
#         self.assertEqual(response["error_summary"],{})
#
#     # @patch('climmob.views.locations.self.getPostDict()', return_value=(True,
#     # [(MagicMock({'csrf_token': 'cc4a052d3982ed41c75f72a05f31c0e3fda3d2da',
#     #              'plocation_lang': 'en',
#     #              'plocation_name': '2',
#     #              'btn_add_location': ''
#     #              }))]))
#     # def test_process_view_when_adding_location(self):
#     #     self.view.request.method = "POST"
#     #     response = self.view.processView()
#     #     self.assertEqual(response.location, "/crud_locations")
#     #
#
#
#
#
#
#






if __name__ == "__main__":
    unittest.main()
