import unittest

from unittest.mock import MagicMock, patch

from webob.multidict import MultiDict

from climmob.views.locations import crud_view, deleteLocation_view


class TestViewLocations(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.params = {}
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"
        self.view = crud_view(self.mock_request)
        self.view.user = self.mock_user
        self.view._ = MagicMock(side_effect=lambda x: x)

    @patch("climmob.views.locations.get_all_project_location",
           return_value=[
               {"id": 1, "plocation_name": "school", "plocation_lang": "en"},
               {"id": 2, "plocation_name": "hospital", "plocation_lang": "en"},
               {"id": 3, "plocation_name": "office", "plocation_lang": "en"}
           ])
    def test_proces_view_not_post(self, mock_get_all_project_location):
        """Verifica si la vista funciona correctamente"""

        self.mock_request.method = "GET"
        result = self.view.processView()
        mock_get_all_project_location.assert_called_once_with(self.mock_request)
        self.assertEqual(len(result['searchAllProyectLocation']), 3)
        self.assertEqual(result["error_summary"], {})
        self.assertEqual(result["dataworking"], {})

    @patch("climmob.views.locations.get_all_project_location",
           return_value=[
               {"id": 1, "plocation_name": "school", "plocation_lang": "en"},
               {"id": 2, "plocation_name": "hospital", "plocation_lang": "en"},
               {"id": 3, "plocation_name": "office", "plocation_lang": "en"}
           ])
    @patch("climmob.views.locations.add_Location_DB", return_value=True)
    @patch("climmob.views.locations.get_location_by_name", return_value={})
    def test_proces_view_post_add(self, mock_get_location_by_name, mock_add_Location_DB, mock_get_all_project_location):
        """Verifica si la vista funciona correctamente"""

        location_data = {
            'csrf_token': 'dummy_token',
            'plocation_lang': 'en',
            'plocation_name': '2',
            'btn_add_location': ''
        }

        self.mock_request.method = "POST"
        self.mock_request.POST = location_data

        result = self.view.processView()

        mock_add_Location_DB.assert_called_once_with(location_data, self.mock_request)
        mock_get_location_by_name.assert_called_once_with(self.mock_request, location_data["plocation_name"])
        mock_get_all_project_location.assert_called_once_with(self.mock_request)
        self.assertEqual(result["error_summary"], {})
        self.assertEqual(result["success_message"], "Location created successfully")

    @patch("climmob.views.locations.get_all_project_location",
           return_value=[
               {"id": 1, "plocation_name": "school", "plocation_lang": "en"},
               {"id": 2, "plocation_name": "hospital", "plocation_lang": "en"},
               {"id": 3, "plocation_name": "office", "plocation_lang": "en"}
           ])
    @patch("climmob.views.locations.get_location_by_name", return_value={"school"})
    def test_proces_view_post_no_add(self, mock_get_location_by_name, mock_get_all_project_location):
        """Verifica si la vista funciona correctamente"""

        location_data = {
            'csrf_token': 'dummy_token',
            'plocation_lang': 'en',
            'plocation_name': 'school',
            'btn_add_location': ''
        }

        self.mock_request.method = "POST"
        self.mock_request.POST = location_data

        result = self.view.processView()
        mock_get_location_by_name.assert_called_once_with(self.mock_request, location_data["plocation_name"])
        mock_get_all_project_location.assert_called_once_with(self.mock_request)
        self.assertEqual(result["error_summary"], {})
        self.assertEqual(result["error_message"], "There is already a record with that name, it was not created")

    @patch("climmob.views.locations.get_all_project_location",
           return_value=[
               {"id": 1, "plocation_name": "school", "plocation_lang": "en"},
               {"id": 2, "plocation_name": "hospital", "plocation_lang": "en"},
               {"id": 3, "plocation_name": "office", "plocation_lang": "en"}
           ])
    @patch("climmob.views.locations.editLocation", return_value=True)
    @patch("climmob.views.locations.get_location_by_name", return_value={})
    def test_proces_view_post_edit(self, mock_get_location_by_name, mock_editLocation, mock_get_all_project_location):
        """Verifica si la vista funciona correctamente"""

        location_data = {
            'csrf_token': 'dummy_token',
            'edit_plocation_id': '1',
            'plocation_lang': 'en',
            'edit_plocation_name': 'school',
            'btn_edit_location': ''
        }

        self.mock_request.method = "POST"
        self.mock_request.POST = location_data

        result = self.view.processView()

        mock_editLocation.assert_called_once_with(self.mock_request.POST,
                                                  self.mock_request.POST['edit_plocation_id'],
                                                  self.mock_request)
        mock_get_location_by_name.assert_called_once_with(self.mock_request, location_data["edit_plocation_name"])
        mock_get_all_project_location.assert_called_once_with(self.mock_request)
        self.assertEqual(result["error_summary"], {})
        self.assertEqual(result["success_message"], "Location edited successfully")

    @patch("climmob.views.locations.get_all_project_location",
           return_value=[
               {"id": 1, "plocation_name": "school", "plocation_lang": "en"},
               {"id": 2, "plocation_name": "hospital", "plocation_lang": "en"},
               {"id": 3, "plocation_name": "office", "plocation_lang": "en"}
           ])
    @patch("climmob.views.locations.get_location_by_name", return_value={"school"})
    def test_proces_view_post_no_edit(self, mock_get_location_by_name, mock_get_all_project_location):
        """Verifica si la vista funciona correctamente"""

        location_data = {
            'csrf_token': 'dummy_token',
            'edit_plocation_id': '1',
            'plocation_lang': 'en',
            'edit_plocation_name': 'school',
            'btn_edit_location': ''
        }

        self.mock_request.method = "POST"
        self.mock_request.POST = location_data
        result = self.view.processView()

        mock_get_location_by_name.assert_called_once_with(self.mock_request, location_data["edit_plocation_name"])
        mock_get_all_project_location.assert_called_once_with(self.mock_request)
        self.assertEqual(result["error_summary"], {})
        self.assertEqual(result["error_message"], "There is already a record with that name, it was not modified.")

class TestdeleteLocation_view(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.params = {}
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"
        self.view = deleteLocation_view(self.mock_request)
        self.view.user = self.mock_user
        self.view._ = MagicMock(side_effect=lambda x: x)

    @patch("climmob.views.locations.deleteLocationdb", return_value=True)
    def test_proces_view_delete(self,mock_deleteLocationdb):
        # data = MultiDict([('csrf_token', 'dummy_token')])
        data = { 'csrf_token': 'dummy_token' }
        self.mock_request.matchdict = {"locationid" : "1"}
        self.mock_request.method = "POST"
        self.mock_request.POST = data
        result = self.view.processView()
        mock_deleteLocationdb.assert_called_once_with("1", self.mock_request)

if __name__ == "__main__":
    unittest.main()
