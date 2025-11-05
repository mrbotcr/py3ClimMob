from unittest.mock import patch, MagicMock

from climmob.tests.test_utils.common import BaseTest
from climmob.views.projectsSummary.column.DataColumn import *


class TestDataColumn(BaseTest):
    view_class = DataColumn

    def setUp(self):
        super().setUp()
        self.columns_patcher = patch(
            "climmob.views.projectsSummary.column.DataColumn.DATA_COLUMNS"
        )
        self.mock_data_columns = self.columns_patcher.start()
        self.mock_data_columns.__iter__.return_value = [
            {"key": "project_id", "label": "ID"},
            {"key": "project_name", "label": "Nombre"},
        ]
        self.addCleanup(self.columns_patcher.stop)

        self.column_patcher = patch(
            "climmob.views.projectsSummary.column.DataColumn.Column"
        )
        self.mock_column = self.column_patcher.start()
        self.mock_column.return_value = MagicMock()
        self.addCleanup(self.column_patcher.stop)

    def test_data_column_get_key_project_summary(
        self,
    ):
        result = self.view_class().get_key_project_summary()
        self.assertEqual(result, ["project_id", "project_name"])
        self.mock_data_columns.__iter__.assert_called_once()

    def test_successful_validation(self):
        result = self.view_class().get_project_summary_columns()
        self.assertEqual(len(result), 2)
        self.mock_column.assert_called()
        self.mock_data_columns.__iter__.assert_called()

    def test_failed_validation(self):
        def mock_column_side_effect(**kwargs):
            if kwargs.get("key") == "project_id":
                raise ValueError("Invalid label")
            return MagicMock()

        self.mock_column.side_effect = mock_column_side_effect

        with self.assertRaises(ValueError) as context:
            self.view_class().get_project_summary_columns()

        self.assertIn(
            "Error on the column 'project_id': Invalid label", str(context.exception)
        )

    def test_duplicate_key_validation(self):
        self.mock_data_columns.__iter__.return_value = [
            {
                "key": "project_id",
                "name": "ID",
                "type": "static",
                "id": 1,
                "show": True,
            },
            {
                "key": "project_id",
                "name": "ID duplicate",
                "type": "static",
                "id": 2,
                "show": True,
            },
        ]

        with self.assertRaises(ValueError) as context:
            self.view_class().get_project_summary_columns()

        self.assertIn("Duplicate key found: 'project_id'", str(context.exception))
