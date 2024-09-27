import json
import unittest
from unittest.mock import patch, MagicMock
from pyramid.response import Response
from datetime import datetime
from climmob.views.Api.projectProducts import (
    readProducts_view,
    downloadApi_view
)
from climmob.tests.test_utils.common import BaseViewTestCase

class TestReadProductsView(BaseViewTestCase):
    view_class = readProducts_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps({
            "project_cod": "PRJ123",
            "user_owner": "owner_user"
        })
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)

    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    @patch("climmob.views.Api.projectProducts.getDataProduct", return_value=[
        {"product_name": "Product 1", "created_at": datetime.now()},
        {"product_name": "Product 2", "created_at": datetime.now()},
    ])
    def test_process_view_successful_retrieval(self, mock_get_products, mock_project_exists, mock_get_project_id):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        products = json.loads(response.body.decode())
        self.assertEqual(len(products), 2)
        self.assertIn("Product 1", products[0]["product_name"])
        self.assertIn("Product 2", products[1]["product_name"])
        mock_project_exists.assert_called_once()
        mock_get_products.assert_called_once_with(1, self.view.request)
        mock_get_project_id.assert_called_with('owner_user', 'PRJ123', self.view.request)

    @patch("climmob.views.Api.projectProducts.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertIn("There is not project with that code.", response.body.decode())
        mock_project_exists.assert_called_once_with('test_user', 'owner_user', 'PRJ123', self.view.request)

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({
            "project_cod": "",
            "user_owner": ""
        })
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
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        mock_json_loads.assert_called_once()

class TestDownloadApiView(BaseViewTestCase):
    view_class = downloadApi_view
    request_method = "GET"

    def setUp(self):
        super().setUp()
        self.request_body = json.dumps({
            "project_cod": "PRJ123",
            "user_owner": "owner_user",
            "celery_taskid": "task123",
            "product_id": "prod123"
        })
        self.view.body = self.request_body
        self.view.request.json_body = json.loads(self.request_body)


    @patch("climmob.views.Api.projectProducts.FileResponse", return_value=Response(status=200))
    @patch("climmob.views.Api.projectProducts.getProductDirectory", return_value="/fake/path/to/product")
    @patch("climmob.views.Api.projectProducts.product_found", return_value=True)
    @patch("climmob.views.Api.projectProducts.getProductData", return_value={
        "product_id": "prod123",
        "output_mimetype": "application/zip",
        "output_id": "file123.zip"
    })
    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    def test_process_view_successful_download(
            self, mock_project_exists, mock_get_project_id, mock_get_product_data,
            mock_product_found, mock_get_product_directory, mock_file_response
    ):
        response = self.view.processView()

        self.assertEqual(response.status_code, 200)
        mock_project_exists.assert_called_once_with('test_user', 'owner_user', 'PRJ123', self.view.request)
        mock_get_project_id.assert_called_once_with('owner_user', 'PRJ123', self.view.request)
        mock_get_product_data.assert_called_once_with(1, 'task123', 'prod123', self.view.request)
        mock_product_found.assert_called_once_with('prod123')
        mock_get_product_directory.assert_called_once_with(self.view.request, 'owner_user', 'PRJ123', 'prod123')
        mock_file_response.assert_called_once_with('/fake/path/to/product/outputs/file123.zip',
                                                   request=self.view.request, content_type='application/zip')



    @patch("climmob.views.Api.projectProducts.projectExists", return_value=False)
    def test_process_view_project_does_not_exist(self, mock_project_exists):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no project with that code.", response.body.decode())
        mock_project_exists.assert_called_once_with('test_user', 'owner_user', 'PRJ123', self.view.request)

    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    @patch("climmob.views.Api.projectProducts.getProductData", return_value=None)
    def test_process_view_product_not_found(self, mock_get_product_data, mock_project_exists, mock_get_project_id):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no product with that celery_taskid or product_id.", response.body.decode())
        mock_project_exists.assert_called_once_with('test_user', 'owner_user', 'PRJ123', self.view.request)
        mock_get_project_id.assert_called_once_with('owner_user', 'PRJ123', self.view.request)
        mock_get_product_data.assert_called_once_with(1, 'task123', 'prod123', self.view.request)


    @patch("climmob.views.Api.projectProducts.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.Api.projectProducts.projectExists", return_value=True)
    @patch("climmob.views.Api.projectProducts.getProductData", return_value={
        "product_id": "prod123",
        "output_mimetype": "application/zip",
        "output_id": "file123.zip"
    })
    @patch("climmob.views.Api.projectProducts.product_found", return_value=False)
    def test_process_view_invalid_product_id(self, mock_product_found, mock_get_product_data, mock_project_exists, mock_get_project_id):
        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.assertIn("There is no product with that product_id.", response.body.decode())
        mock_project_exists.assert_called_once_with('test_user', 'owner_user', 'PRJ123', self.view.request)
        mock_get_project_id.assert_called_once_with('owner_user', 'PRJ123', self.view.request)
        mock_get_product_data.assert_called_once_with(1, 'task123', 'prod123', self.view.request)
        mock_product_found.assert_called_once_with('prod123')

    def test_process_view_missing_parameters(self):
        self.view.body = json.dumps({
            "project_cod": "",
            "user_owner": "",
            "celery_taskid": "task123",
            "product_id": ""
        })
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
        self.assertIn("Error in the JSON, It does not have the 'body' parameter.", response.body.decode())
        mock_json_loads.assert_called_once()


if __name__ == "__main__":
    unittest.main()