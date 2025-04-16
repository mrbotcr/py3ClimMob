import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.models import Techalia
from climmob.views.Api.techaliases import (
    CreateAliasView,
    ReadAliasView,
    UpdateAliasView,
    DeleteAliasViewAPI,
)


class TestCreateAliasView(unittest.TestCase):
    def setUp(self):
        self.view = CreateAliasView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    def test_process_view_no_create_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_no_create_json_error_other_param(self):
        self.view.body = json.dumps(
            {
                "Other": "fake_name",
                "tech_id": "123",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_create_json_error_less_param(self):
        self.view.body = json.dumps(
            {
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_create_no_param(self):
        self.view.body = json.dumps(
            {
                "tech_id": "",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    def test_process_view_no_create_no_param_2(self):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=False)
    def test_process_view_no_create_no_user_technology(self, mock_getTechnologyByUser):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a technology with this ID.")

    @patch("climmob.views.Api.techaliases.findTechalias", return_value=True)
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=True)
    def test_process_view_no_create_technology_already_exist(
        self, mock_getTechnologyByUser, mock_findTechalias
    ):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "Fake Alias",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"This technology option already exists in the technology."
        )

    @patch(
        "climmob.views.Api.techaliases.addTechAlias",
        return_value=(False, "Error at Add"),
    )
    @patch("climmob.views.Api.techaliases.findTechalias", return_value=False)
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=True)
    def test_process_view_no_create_add_false(
        self, mock_getTechnologyByUser, mock_findTechalias, addTechAlias
    ):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "test_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error at Add")

    @patch("climmob.views.Api.techaliases.addTechAlias", return_value=(True, ""))
    @patch("climmob.views.Api.techaliases.findTechalias", return_value=False)
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=True)
    def test_process_view_create_add_true(
        self, mock_getTechnologyByUser, mock_findTechalias, mock_addTechAlias
    ):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_name": "test_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'""')
        expected_body = json.loads(self.view.body)
        expected_body.update({"user_name": "test_user", "alias_id": None})
        mock_addTechAlias.assert_called_once_with(
            expected_body, self.view.request, "API"
        )


class TestReadAliasView(unittest.TestCase):
    def setUp(self):
        self.view = ReadAliasView(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    def test_process_view_no_read_no_get(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    def test_process_view_no_read_no_json_error(self):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_no_read_json_error_other_param(self):
        self.view.body = json.dumps(
            {
                "Other": "fake_name",
                "tech_id": "123",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_read_json_error_param(self):
        self.view.body = json.dumps(
            {
                "Other": "fake_name",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_read_no_param(self):
        self.view.body = json.dumps(
            {
                "tech_id": "",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.techaliases.getTechnologyByUser")
    def test_process_view_no_read_no_technology_id(self, mock_getTechnologyByUser):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
            }
        )
        mock_getTechnologyByUser.side_effect = [False, False]
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no technology with this ID.")

    @patch(
        "climmob.views.Api.techaliases.getTechsAlias",
        return_value=(
            [
                {
                    "tech_id": 0,
                    "alias_id": 0,
                    "alias_name": "",
                    "quantity": 1,
                    "tech_name": "",
                },
            ]
        ),
    )
    @patch("climmob.views.Api.techaliases.getTechnologyByUser")
    def test_process_view_no_read_technology_by_user_bioversity(
        self, mock_getTechnologyByUser, mock_getTechsAlias
    ):
        dummy_response = [
            {
                "tech_id": 0,
                "alias_id": 0,
                "alias_name": "",
                "quantity": 1,
                "tech_name": "",
            }
        ]
        self.view.body = json.dumps(
            {
                "tech_id": "0",
            }
        )
        mock_getTechnologyByUser.side_effect = [False, True]
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(json.loads(response.body.decode()), dummy_response)

    @patch(
        "climmob.views.Api.techaliases.getTechsAlias",
        return_value=(
            [
                {
                    "tech_id": 0,
                    "alias_id": 0,
                    "alias_name": "",
                    "quantity": 1,
                    "tech_name": "",
                },
            ]
        ),
    )
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=True)
    def test_process_view_no_read_technology_by_user_(
        self, mock_getTechnologyByUser, mock_getTechsAlias
    ):
        dummy_response = [
            {
                "tech_id": 0,
                "alias_id": 0,
                "alias_name": "",
                "quantity": 1,
                "tech_name": "",
            }
        ]
        self.view.body = json.dumps(
            {
                "tech_id": "0",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertCountEqual(json.loads(response.body.decode()), dummy_response)


class TestUpdateAliasView(unittest.TestCase):
    def setUp(self):
        self.view = UpdateAliasView(MagicMock())
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

    def test_process_view_no_update_json_error_more_params(self):
        self.view.body = json.dumps(
            {
                "Other": "fake_name",
                "tech_id": "123",
                "alias_id": "12",
                "alias_name": "fake_name",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_update_json_error_less_params(self):
        self.view.body = json.dumps({"tech_id": "123", "alias_name": "fake_name"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_update_no_data_tech(self):
        self.view.body = json.dumps(
            {"tech_id": "", "alias_id": "12", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    def test_process_view_no_update_no_data_alias(self):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    def test_process_view_no_update_no_data_two_params(self):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "", "alias_name": ""}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(False))
    def test_process_view_no_update_no_tech_by_user(self, mock_getTechnologyByUser):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "12", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a technology with this ID.")

    @patch("climmob.views.Api.techaliases.existAlias", return_value=(False))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_update_no_alias(
        self, mock_getTechnologyByUser, mock_existAlias
    ):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "12", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"You do not have a technology option with this ID."
        )

    @patch("climmob.views.Api.techaliases.findTechalias", return_value=True)
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_update_no_found_alias(
        self, mock_getTechnologyByUser, mock_existAlias, mock_findTechalias
    ):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "12", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"This technology option already exists for the technology."
        )

    @patch(
        "climmob.views.Api.techaliases.getAliasAssignedWithoutProjectCode",
        return_value=True,
    )
    @patch("climmob.views.Api.techaliases.findTechalias", return_value=False)
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_update_project_assigned(
        self,
        mock_getTechnologyByUser,
        mock_existAlias,
        mock_findTechalias,
        mock_getAliasAssignedWithoutProjectCode,
    ):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "12", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You can not update this technology option because it has been assigned to a project.",
        )

    @patch(
        "climmob.views.Api.techaliases.updateAlias",
        return_value=(False, "Error at update."),
    )
    @patch(
        "climmob.views.Api.techaliases.getAliasAssignedWithoutProjectCode",
        return_value=False,
    )
    @patch("climmob.views.Api.techaliases.findTechalias", return_value=False)
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_update_proyect_asigned(
        self,
        mock_getTechnologyByUser,
        mock_existAlias,
        mock_findTechalias,
        mock_getAliasAssignedWithoutProjectCode,
        mock_updateAlias,
    ):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "12", "alias_name": "fake_name"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error at update.")

    @patch("climmob.views.Api.techaliases.updateAlias", return_value=(True, ""))
    @patch(
        "climmob.views.Api.techaliases.getAliasAssignedWithoutProjectCode",
        return_value=False,
    )
    @patch("climmob.views.Api.techaliases.findTechalias", return_value=False)
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_update_true(
        self,
        mock_getTechnologyByUser,
        mock_existAlias,
        mock_findTechalias,
        mock_getAliasAssignedWithoutProjectCode,
        mock_updateAlias,
    ):
        body_dict = {"tech_id": "123", "alias_id": "12", "alias_name": "fake_name"}
        self.view.body = json.dumps(body_dict)
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        body_dict["user_name"] = "test_user"
        self.assertEqual(
            response.body, b"The technology option was updated successfully."
        )
        mock_updateAlias.assert_called_once_with(body_dict, self.view.request)


class TestDeleteAliasViewAPI(unittest.TestCase):
    def setUp(self):
        self.view = DeleteAliasViewAPI(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)

    def mock_translation(self, message):
        return message

    def test_process_view_no_delete_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_delete_json_error_less_params(self):
        self.view.body = json.dumps({"tech_id": "123"})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_delete_json_error_more_params(self):
        self.view.body = json.dumps(
            {"tech_id": "123", "alias_id": "12", "other": "abc"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_delete_no_params_data(self):
        self.view.body = json.dumps(
            {
                "tech_id": "",
                "alias_id": "12",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(False))
    def test_process_view_no_delete_no_tech_by_user(self, mock_getTechnologyByUser):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_id": "12",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a technology with this ID.")

    @patch("climmob.views.Api.techaliases.existAlias", return_value=(False))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_delete_no_alias_by_user(
        self, mock_getTechnologyByUser, mock_existAlias
    ):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_id": "12",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a alias with this ID.")

    @patch(
        "climmob.views.Api.techaliases.getAliasAssignedWithoutProjectCode",
        return_value=(True),
    )
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_delete_proyect_assigned(
        self,
        mock_getTechnologyByUser,
        mock_existAlias,
        mock_getAliasAssignedWithoutProjectCode,
    ):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_id": "12",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You cannot delete this technology option because it has been assigned to a project.",
        )

    @patch(
        "climmob.views.Api.techaliases.removeAlias",
        return_value=(False, "Error to delete."),
    )
    @patch(
        "climmob.views.Api.techaliases.getAliasAssignedWithoutProjectCode",
        return_value=(False),
    )
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_delete_no_delete_error(
        self,
        mock_getTechnologyByUser,
        mock_existAlias,
        mock_getAliasAssignedWithoutProjectCode,
        mock_removeAlias,
    ):
        self.view.body = json.dumps(
            {
                "tech_id": "123",
                "alias_id": "12",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error to delete.")
        mock_removeAlias.assert_called_once()

    @patch("climmob.views.Api.techaliases.removeAlias", return_value=(True, ""))
    @patch(
        "climmob.views.Api.techaliases.getAliasAssignedWithoutProjectCode",
        return_value=(False),
    )
    @patch("climmob.views.Api.techaliases.existAlias", return_value=(True))
    @patch("climmob.views.Api.techaliases.getTechnologyByUser", return_value=(True))
    def test_process_view_no_delete_no_proyect_assigned(
        self,
        mock_getTechnologyByUser,
        mock_existAlias,
        mock_getAliasAssignedWithoutProjectCode,
        mock_removeAlias,
    ):
        body_dict = {
            "tech_id": "123",
            "alias_id": "12",
        }
        self.view.body = json.dumps(body_dict)
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        body_dict["user_name"] = "test_user"
        self.assertEqual(
            response.body, b"The technology option was deleted successfully."
        )
        mock_removeAlias.assert_called_once_with(body_dict, self.view.request)


if __name__ == "__main__":
    unittest.main()
