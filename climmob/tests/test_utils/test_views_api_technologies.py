import json
import unittest
from unittest.mock import patch, MagicMock
from climmob.views.Api.technologies import (
    CreateTechnologyView,
    ReadTechnologiesView,
    UpdateTechnologyView,
    DeleteTechnologyViewAPI,
    merge_two_dicts
)

class TestCreateTechnologyView(unittest.TestCase):
    def setUp(self):
        self.view = CreateTechnologyView(MagicMock())
        self.view.request.method = 'POST'
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    def test_process_view_no_add_no_post(self):
        self.view.request.method = 'GET'
        self.view.body = json.dumps({
             "tech_name" :"",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_add_json_error(self):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
             "Other" :"fake_name",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_add_json_error_param(self):
        self.view.request.method = "POST"
        self.view.body = json.dumps({
            "tech_id": "123456",
            "invalid_param": "not_allowed",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_add_no_param(self):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
             "tech_name" :"",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=True)
    def test_process_view_no_add_all_ready_exist(self, mock_findTechInLibrary):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_name": "fake_name",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"This technology already exists in the generic library.")

    @patch('climmob.views.Api.technologies.addTechnology', return_value=(False,""))
    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=False)
    def test_process_view_add_false(self,
                                    mock_findTechInLibrary,
                                    mock_addTechnology):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
             "tech_name" :"fake_name",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"")

    @patch('climmob.views.Api.technologies.getTechnologyByName', return_value={
            'user_name': 'test_user',
            'tech_name': 'fake_name',})
    @patch('climmob.views.Api.technologies.addTechnology', return_value=(True,""))
    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=False)
    def test_process_view_add_true(self,
                                   mock_findTechInLibrary,
                                   mock_addTechnology,
                                   mock_getTechnologyByName):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
             "tech_name" :"fake_name",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        mock_addTechnology.assert_called_once()

class TestReadTechnologiesView(unittest.TestCase):
    def setUp(self):
        self.view = ReadTechnologiesView(MagicMock())
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    @patch('climmob.views.Api.technologies.getUserTechs')
    def test_process_view(self, mock_getUserTechs):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)

    @patch('climmob.views.Api.technologies.getUserTechs')
    def test_process_view_no_view(self, mock_getUserTechs):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

class TestUpdateTechnologyView(unittest.TestCase):
    def setUp(self):
        self.view = UpdateTechnologyView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    def test_process_view_no_update_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_update_json_error(self):
        self.view.request.method = "POST"
        self.view.body = json.dumps({
            "Other": "fake_name",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_update_json_error_invalid_param(self):
        self.view.request.method = "POST"
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": "123456",
            "invalid_param": "not_allowed",
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_update_no_param_no_name(self):
        self.view.request.method = "POST"
        self.view.body = json.dumps({
            "tech_name": "",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    def test_process_view_no_update_no_param_no_tech_id(self):
        self.view.request.method = "POST"
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": ""
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=True)
    def test_process_view_no_update_already_exist(self, mock_findTechInLibrary):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"This technology already exists in "
                                        b"the generic library.")

    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=False)
    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=False)
    def test_process_view_no_update_no_user_technology(self,
                                                       mock_findTechInLibrary,
                                                       mock_getTechnologyByUser):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a technology with this ID.")

    @patch ('climmob.views.Api.technologies.getTechnologyAssigned', return_value=True)
    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=True)
    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=False)
    def test_process_view_no_update_technology_on_use(self,
                                                      mock_findTechInLibrary,
                                                      mock_getTechnologyByUser,
                                                      mock_getTechnologyAssigned):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You cannot update this technology because it"
                                        b" has been assigned to a project.")

    @patch('climmob.views.Api.technologies.updateTechnology', return_value=(False,"Error"))
    @patch('climmob.views.Api.technologies.getTechnologyAssigned', return_value=False)
    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=True)
    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=False)
    def test_process_view_no_update_error(self,
                                          mock_findTechInLibrary,
                                          mock_getTechnologyByUser,
                                          mock_getTechnologyAssigned,
                                          mock_updateTechnology):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error")

    @patch('climmob.views.Api.technologies.updateTechnology', return_value=(True,""))
    @patch('climmob.views.Api.technologies.getTechnologyAssigned', return_value=False)
    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=True)
    @patch('climmob.views.Api.technologies.findTechInLibrary', return_value=False)
    def test_process_view_update_success(self,
                                         mock_findTechInLibrary,
                                         mock_getTechnologyByUser,
                                         mock_getTechnologyAssigned,
                                         mock_updateTechonlogy):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_name": "fake_name",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"The technology was modified successfully.")
        mock_updateTechonlogy.assert_called_once()

class TestDeleteTechnologyViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = DeleteTechnologyViewAPI(MagicMock())
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.request.method = "POST"

    def mock_translation(self, message):
        return message

    def test_process_view_no_delete_no_post(self):
        self.view.request.method = ''
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_delete_json_param_error(self):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "other": "fake_name",
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=False)
    def test_process_view_no_delete_no_user_technology(self, mock_getTechnologyByUser):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a technology with this ID.")

    @patch('climmob.views.Api.technologies.getTechnologyAssigned', return_value=True)
    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=True)
    def test_process_view_no_delete_technology_on_use(self,
                                                      mock_getTechnologyByUser,
                                                      mock_getTechnologyAssigned):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You cannot delete this technology because "
                                        b"it has been assigned to a project.")

    @patch('climmob.views.Api.technologies.deleteTechnology', return_value=(False,"Error"))
    @patch('climmob.views.Api.technologies.getTechnologyAssigned', return_value=False)
    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=True)
    def test_process_view_no_delete_error(self,
                                          mock_getTechnologyByUser,
                                          mock_getTechnologyAssigned,
                                          mock_deleteTechnology):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error")

    @patch('climmob.views.Api.technologies.deleteTechnology', return_value=(True,""))
    @patch('climmob.views.Api.technologies.getTechnologyAssigned', return_value=False)
    @patch('climmob.views.Api.technologies.getTechnologyByUser', return_value=True)
    def test_process_view_delete_success(self,
                                          mock_getTechnologyByUser,
                                          mock_getTechnologyAssigned,
                                          mock_deleteTechnology):
        self.view.request.method = 'POST'
        self.view.body = json.dumps({
            "tech_id": "123456"
        })
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"The technology was deleted successfully.")
        mock_deleteTechnology.assert_called_once()

class TestMergeTwoDicts(unittest.TestCase):
    def test_merge_non_overlapping_keys(self):
        x = {"a": 1}
        y = {"b": 2}
        result = merge_two_dicts(x, y)
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_merge_overlapping_keys(self):
        x = {"a": 1, "b": 2}
        y = {"b": 3, "c": 4}
        result = merge_two_dicts(x, y)
        self.assertEqual(result, {"a": 1, "b": 3, "c": 4})

    def test_merge_with_empty_dicts(self):
        self.assertEqual(merge_two_dicts({}, {}), {})
        self.assertEqual(merge_two_dicts({"a": 1}, {}), {"a": 1})
        self.assertEqual(merge_two_dicts({}, {"b": 2}), {"b": 2})