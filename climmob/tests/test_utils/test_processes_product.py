from pathlib import Path
from unittest.mock import patch, MagicMock

from climmob.processes import (
    product_file_exists,
)
from climmob.tests.test_utils.test_processes import DBProcessBaseTest


class TestProductFileExists(DBProcessBaseTest):
    def setUp(self):
        super().setUp()
        self.process = product_file_exists
        self.owner_username = "test_user"
        self.project_cod = "PROJ123"

    @classmethod
    def setUpClass(cls):
        cls.patchers["getProductDirectory"] = {
            "patch": patch("climmob.processes.db.products.getProductDirectory"),
            "return_value": "/mock/base/dir",
        }
        cls.patchers["os.path.exists"] = {
            "patch": patch("climmob.processes.db.products.os.path.exists"),
            "return_value": True,
        }
        super().setUpClass()

    def test_product_file_exists_returns_true_when_file_exists(self):
        self.get_mock("os.path.exists").return_value = True

        expected_path = (
            Path(self.get_mock("getProductDirectory").return_value)
            / "outputs"
            / f"Report_{self.project_cod}.docx"
        )

        result = self.process(
            self.request, self.owner_username, self.project_cod, "reports"
        )

        self.assertTrue(result)
        self.get_mock("getProductDirectory").assert_called_once_with(
            self.request, self.owner_username, self.project_cod, "reports"
        )
        self.get_mock("os.path.exists").assert_called_once_with(expected_path)

    def test_product_file_exists_returns_false_when_file_does_not_exist(self):
        self.get_mock("os.path.exists").return_value = False

        result = product_file_exists(
            self.request, self.owner_username, self.project_cod, "reports"
        )

        self.assertFalse(result)

    def test_product_file_exists_raises_not_implemented_error_for_unknown_product(self):

        with self.assertRaises(NotImplementedError):
            product_file_exists(
                self.request,
                self.owner_username,
                self.project_cod,
                "unsupported_product",
            )
