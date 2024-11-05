import json
import unittest
from unittest.mock import patch, MagicMock

from climmob.views.Api.enumerators import (
    CreateEnumeratorView,
    ReadEnumeratorsView,
    UpdateEnumeratorView,
    UpdatePasswordEnumeratorView,
    ApiDeleteEnumeratorView,
)


class TestCreateEnumeratorView(unittest.TestCase):
    def setUp(self):
        self.view = CreateEnumeratorView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_name": "Test Enumerator",
                "enum_password": "password",
                "enum_password_re": "password",
                "enum_telephone": "123456789",
            }
        )

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=False)
    @patch(
        "climmob.views.Api.enumerators.addEnumerator", return_value=(True, "Success")
    )
    def test_process_view_success(self, mock_addEnumerator, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The field agent was created successfully.", response.body.decode()
        )

    def test_process_view_invalid_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())

    def test_process_view_missing_obligatory_keys(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {"enum_id": "test_enum", "enum_name": "Test Enumerator"}
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_not_all_parameters_have_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_name": "Test Enumerator",
                "enum_password": "password",
                "enum_password_re": "password",
                "enum_telephone": "",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_password_mismatch(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_name": "Test Enumerator",
                "enum_password": "password",
                "enum_password_re": "different_password",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The password and its retype are not the same.", response.body.decode()
        )

    def test_process_view_invalid_parameter(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_name": "Test Enumerator",
                "enum_password": "password",
                "enum_password_re": "password",
                "invalid_param": "not_allowed",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to use a parameter that is not allowed..",
            response.body.decode(),
        )

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=True)
    def test_process_view_enumerator_exists(self, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This field agent name already exists.", response.body.decode())

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=False)
    @patch(
        "climmob.views.Api.enumerators.addEnumerator",
        return_value=(False, "Error message"),
    )
    def test_process_view_add_enumerator_failure(
        self, mock_addEnumerator, mock_enumeratorExists
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error message", response.body.decode())


class TestReadEnumeratorsView(unittest.TestCase):
    def setUp(self):
        self.view = ReadEnumeratorsView(MagicMock())
        self.view.request.method = "GET"
        self.view.user = MagicMock(login="test_user")

    @patch(
        "climmob.views.Api.enumerators.searchEnumerator",
        return_value=[{"enum_id": "1", "enum_name": "Test Enumerator"}],
    )
    def test_process_view_success(self, mock_searchEnumerator):
        self.view._ = lambda x: x  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.body)
        self.assertEqual(response_data[0]["enum_id"], "1")
        self.assertEqual(response_data[0]["enum_name"], "Test Enumerator")

    def test_process_view_post_method(self):
        self.view._ = lambda x: x  # Mock translation function
        self.view.request.method = "POST"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())


class TestUpdateEnumeratorView(unittest.TestCase):
    def setUp(self):
        self.view = UpdateEnumeratorView(MagicMock())
        self.view.request.method = "POST"
        self.view.body = json.dumps({"enum_id": "test_enum", "enum_name": "Test Name"})
        self.view.user = MagicMock(login="test_user")

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.enumerators.modifyEnumerator", return_value=(True, "Success")
    )
    def test_process_view_success(self, mock_modifyEnumerator, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The field agent was modified successfully.", response.body.decode()
        )

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=False)
    def test_process_view_enumerator_not_exists(self, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        self.view.body = json.dumps({"enum_id": "test_enum"})
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no field agent with that identifier.", response.body.decode()
        )

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "It is not complying with the obligatory keys.", response.body.decode()
        )

    def test_process_view_invalid_keys(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps({"enum_id": "test_enum", "invalid_key": "value"})

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "You are trying to use a parameter that is not allowed..",
            response.body.decode(),
        )

    def test_process_view_missing_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps({"enum_id": "test_enum", "enum_name": ""})

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


class TestUpdatePasswordEnumeratorView(unittest.TestCase):
    def setUp(self):
        self.view = UpdatePasswordEnumeratorView(MagicMock())
        self.view.request.method = "POST"
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_password": "old_password",
                "enum_password_new": "new_password",
                "enum_password_new_re": "new_password",
            }
        )
        self.view.user = MagicMock(login="test_user")

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=True)
    @patch("climmob.views.Api.enumerators.isEnumeratorPassword", return_value=True)
    @patch(
        "climmob.views.Api.enumerators.modifyEnumeratorPassword",
        return_value=(True, "Success"),
    )
    def test_process_view_success(
        self,
        mock_modifyEnumeratorPassword,
        mock_isEnumeratorPassword,
        mock_enumeratorExists,
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn("The password was modified successfully.", response.body.decode())

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=False)
    def test_process_view_enumerator_not_exists(self, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no field agent with that identifier.", response.body.decode()
        )

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=True)
    @patch("climmob.views.Api.enumerators.isEnumeratorPassword", return_value=False)
    def test_process_view_incorrect_password(
        self, mock_isEnumeratorPassword, mock_enumeratorExists
    ):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("The current password is incorrect.", response.body.decode())

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=True)
    @patch("climmob.views.Api.enumerators.isEnumeratorPassword", return_value=True)
    def test_process_view_passwords_not_matching(
        self, mock_isEnumeratorPassword, mock_enumeratorExists
    ):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_password": "old_password",
                "enum_password_new": "new_password",
                "enum_password_new_re": "different_password",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "The new password and the retype are not the same.", response.body.decode()
        )

    def test_process_view_missing_data(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = json.dumps(
            {
                "enum_id": "test_enum",
                "enum_password": "",
                "enum_password_new": "new_password",
                "enum_password_new_re": "new_password",
            }
        )

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


class TestApiDeleteEnumeratorView(unittest.TestCase):
    def setUp(self):
        self.view = ApiDeleteEnumeratorView(MagicMock())
        self.view.request.method = "POST"
        self.view.body = json.dumps({"enum_id": "test_enum"})
        self.view.user = MagicMock(login="test_user")

    def mock_translation(self, message):
        return message

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=True)
    @patch(
        "climmob.views.Api.enumerators.deleteEnumerator", return_value=(True, "Success")
    )
    def test_process_view_success(self, mock_deleteEnumerator, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "The field agent was deleted successfully.", response.body.decode()
        )

    @patch("climmob.views.Api.enumerators.enumeratorExists", return_value=False)
    def test_process_view_enumerator_not_exists(self, mock_enumeratorExists):
        self.view._ = self.mock_translation  # Mock translation function

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("This field agent does not exist.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.body = '{"wrong_key": "value"}'

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_post_method(self):
        self.view._ = self.mock_translation  # Mock translation function
        self.view.request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts POST method.", response.body.decode())


if __name__ == "__main__":
    unittest.main()
