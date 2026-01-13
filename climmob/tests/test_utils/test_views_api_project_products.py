import json
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from pyramid.response import Response

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.Api.projectProducts import (
    readProducts_view,
    downloadApi_view,
    GetListOfQuestionsByProject,
)


class TestReadProductsView(ViewBaseTest):
    view_class = readProducts_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {"project_cod": "PRJ123", "user_owner": "owner_user"}
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectProducts.getDataProduct",
        return_value=[
            {"product_name": "Product 1", "created_at": datetime.now()},
            {"product_name": "Product 2", "created_at": datetime.now()},
        ],
    )
    def test_process_view_successful_retrieval(
        self, mock_get_products, mock_project_exists, mock_get_project_id
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        products = json.loads(response.body.decode())
        self.assertEqual(len(products), 2)
        self.assertIn("Product 1", products[0]["product_name"])
        self.assertIn("Product 2", products[1]["product_name"])
        mock_project_exists.assert_called_once()
        mock_get_products.assert_called_once_with(1, self.view.request)
        mock_get_project_id.assert_called_with(
            "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectProducts.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not project with that code.", response.body.decode())
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({"project_cod": "", "user_owner": ""})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = '{"invalid": "json"}'
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_json_decode_error(self, mock_json_loads):
        self.view.body = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_json_loads.assert_called_once()


class TestDownloadApiView(ViewBaseTest):
    view_class = downloadApi_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps(
            {
                "project_cod": "PRJ123",
                "user_owner": "owner_user",
                "celery_taskid": "task123",
                "product_id": "prod123",
            }
        )
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch(
        "climmob.views.Api.projectProducts.FileResponse",
        return_value=Response(status=200),
    )
    @patch(
        "climmob.views.Api.projectProducts.getProductDirectory",
        return_value="/fake/path/to/product",
    )
    @patch("climmob.views.Api.projectProducts.product_found", return_value=True)
    @patch(
        "climmob.views.Api.projectProducts.getProductData",
        return_value={
            "product_id": "prod123",
            "output_mimetype": "application/zip",
            "output_id": "file123.zip",
        },
    )
    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    def test_process_view_successful_download(
        self,
        mock_project_exists,
        mock_get_project_id,
        mock_get_product_data,
        mock_product_found,
        mock_get_product_directory,
        mock_file_response,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_product_data.assert_called_once_with(
            1, "task123", "prod123", self.view.request
        )
        mock_product_found.assert_called_once_with("prod123")
        mock_get_product_directory.assert_called_once_with(
            self.view.request, "owner_user", "PRJ123", "prod123"
        )
        mock_file_response.assert_called_once_with(
            "/fake/path/to/product/outputs/file123.zip",
            request=self.view.request,
            content_type="application/zip",
        )

    @patch("climmob.views.Api.projectProducts.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )

    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    @patch("climmob.views.Api.projectProducts.getProductData", return_value=None)
    def test_process_view_product_not_found(
        self, mock_get_product_data, mock_project_exists, mock_get_project_id
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no product with that celery_taskid or product_id.",
            response.body.decode(),
        )
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_product_data.assert_called_once_with(
            1, "task123", "prod123", self.view.request
        )

    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    @patch(
        "climmob.views.Api.projectProducts.getProductData",
        return_value={
            "product_id": "prod123",
            "output_mimetype": "application/zip",
            "output_id": "file123.zip",
        },
    )
    @patch("climmob.views.Api.projectProducts.product_found", return_value=False)
    def test_process_view_invalid_product_id(
        self,
        mock_product_found,
        mock_get_product_data,
        mock_project_exists,
        mock_get_project_id,
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "There is no product with that product_id.", response.body.decode()
        )
        mock_project_exists.assert_called_once_with(
            "test_user", "owner_user", "PRJ123", self.view.request
        )
        mock_get_project_id.assert_called_once_with(
            "owner_user", "PRJ123", self.view.request
        )
        mock_get_product_data.assert_called_once_with(
            1, "task123", "prod123", self.view.request
        )
        mock_product_found.assert_called_once_with("prod123")

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "",
                "celery_taskid": "task123",
                "product_id": "",
            }
        )
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Not all parameters have data.", response.body.decode())

    def test_process_view_invalid_json(self):
        self.view.body = '{"invalid": "json"}'
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Error in the JSON.", response.body.decode())

    def test_process_view_invalid_method(self):
        self.view.request.method = "POST"
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("Only accepts GET method.", response.body.decode())

    @patch("json.loads", side_effect=json.JSONDecodeError("Expecting value", "", 0))
    def test_process_view_json_decode_error(self, mock_json_loads):
        self.view.body = ""
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn(
            "Error in the JSON, It does not have the 'body' parameter.",
            response.body.decode(),
        )
        mock_json_loads.assert_called_once()


class TestGetListOfQuestionsByProject(ViewBaseTest):
    view_class = GetListOfQuestionsByProject
    request_body = json.dumps(
        {"user_owner": "testuser", "project_cod": "testproject", "lang_code": "en"}
    )

    def setUp(self):
        super().setUp()
        self.active_project_id_patcher = patch(
            "climmob.views.Api.projectProducts.getTheProjectIdForOwner"
        )
        self.registry_questions_patcher = patch(
            "climmob.views.Api.projectProducts.get_registry_questions_by_project"
        )
        self.assessment_questions_patcher = patch(
            "climmob.views.Api.projectProducts.get_assessment_questions_by_project"
        )
        self.language_exist_patcher = patch(
            "climmob.views.Api.projectProducts.languageExistInI18n"
        )
        self.api_key_patcher = patch("climmob.views.classes.getUserByApiKey")

        self.mock_project_id = self.active_project_id_patcher.start()
        self.mock_registry_questions = self.registry_questions_patcher.start()
        self.mock_assessment_questions = self.assessment_questions_patcher.start()
        self.mock_language = self.language_exist_patcher.start()
        self.mock_api_key = self.api_key_patcher.start()

        self.mock_project_id.return_value = MagicMock(str, name="project_id")
        self.mock_registry_questions.return_value = [
            {
                "question_id": 1,
                "question_text": "Registry question 1",
                "type": "registry",
            }
        ]
        self.mock_assessment_questions.return_value = [
            {
                "question_id": 2,
                "question_text": "Assessment question 1",
                "type": "assessment",
            }
        ]
        self.mock_language.return_value = True
        self.mock_api_key.return_value = MagicMock(login="validuser")

        self.addCleanup(self.mock_project_id.stop)
        self.addCleanup(self.mock_registry_questions.stop)
        self.addCleanup(self.mock_assessment_questions.stop)
        self.addCleanup(self.mock_language.stop)
        self.addCleanup(self.mock_api_key.stop)

    def tearDown(self):
        request_body_dict = json.loads(self.request_body)

        if self.mock_project_id.called:
            self.mock_project_id.assert_called_once_with(
                request_body_dict["user_owner"],
                request_body_dict["project_cod"],
                self.view.request,
            )
        if self.mock_registry_questions.called:
            self.mock_registry_questions.assert_called_once_with(
                self.view.request, self.mock_project_id.return_value, "en"
            )
        if self.mock_assessment_questions.called:
            self.mock_assessment_questions.assert_called_once_with(
                self.view.request, self.mock_project_id.return_value, "en"
            )
        if self.mock_api_key.called:
            self.mock_api_key.assert_called_once_with(
                self.view.request.params["Apikey"], self.view.request
            )

    def test_get_no_ApiKey(self):
        self.mock_api_key.return_value = None
        _json = {
            "user_owner": "testuser",
            "project_cod": "testproject",
            "lang_code": "aae",
        }
        self.view.request.params = {"Body": json.dumps(_json)}
        response = self.view()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Apikey non-existent")

    @patch("climmob.views.classes.update_last_login")
    def test_get_no_user_owner(self, mock_update_last_login):

        apiKey = "VALID_KEY"
        _json = {"user_owner": "", "project_cod": "testproject", "lang_code": "aae"}

        self.view.request.params = {"Apikey": apiKey, "Body": json.dumps(_json)}
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.body, b"The following fields require a value: user_owner"
        )

    @patch("climmob.views.classes.update_last_login")
    def test_get_wrong_user_owner(self, mock_update_last_login):

        apiKey = "VALID_KEY"
        _json = {
            "user_owner": "something",
            "project_cod": "testproject",
            "lang_code": "aae",
        }

        self.view.request.params = {"Apikey": apiKey, "Body": json.dumps(_json)}
        response = self.view()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, b"There is no a project with that code.")

    @patch("climmob.views.classes.update_last_login")
    def test_get_no_project_cod(self, mock_update_last_login):

        apiKey = "VALID_KEY"
        _json = {"user_owner": "", "project_cod": "", "lang_code": "aae"}

        self.view.request.params = {"Apikey": apiKey, "Body": json.dumps(_json)}
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.body,
            b"The following fields require a value: user_owner, project_cod",
        )

    @patch("climmob.views.classes.update_last_login")
    def test_get_less_values(self, mock_update_last_login):
        apiKey = "VALID_KEY"
        self.view.request.params = {
            "Apikey": apiKey,
        }
        response = self.view()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.body, b"The following fields are required: user_owner, project_cod"
        )

    def test_get_not_lang(self):
        self.view.body = json.dumps(
            {"user_owner": "testuser", "project_cod": "testproject", "lang_code": ""}
        )

        response = self.view.get()
        self.assertEqual(response.status_code, 200)
        self.mock_language.assert_called_once_with("en", self.view.request)

    def test_get_no_lang_code(self):
        self.view.body = json.dumps(
            {"user_owner": "testuser", "project_cod": "testproject"}
        )
        response = self.view.get()
        self.assertEqual(response.status_code, 200)
        self.mock_language.assert_called_once_with("en", self.view.request)

    def test_get_no_exist_lang_code(self):
        self.view.body = json.dumps(
            {
                "user_owner": "testuser",
                "project_cod": "testproject",
                "lang_code": "Español",
            }
        )
        self.mock_language.return_value = False
        response = self.view.get()
        self.assertEqual(response.status_code, 400)
        self.mock_language.assert_called_once_with("Español", self.view.request)

    def test_get_success(self):
        response = self.view.get()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b'[{"question_id": 1, "question_text": "Registry question 1", "type": "registry"}, {"question_id": 2, "question_text": "Assessment question 1", "type": "assessment"}]',
        )
        self.mock_language.assert_called_once_with("en", self.view.request)


if __name__ == "__main__":
    unittest.main()
