import unittest
from unittest.mock import MagicMock, patch
from climmob.views.prj_objective import objective_by_id_view


class TestProjectObjectivesByIdView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.method = None
        self.mock_request.matchdict = {"objective_id": "1"}

        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = objective_by_id_view(self.mock_request)
        self.view.user = self.mock_user

    @patch("climmob.views.prj_objective.get_objective_by_id")
    def test_process_view_get_existing_objective(self, mock_get_objective_by_id):
        self.mock_request.method = "GET"

        objective = {
            "pobjective_id": 1,
            "pobjective_name": "Adaptation trials",
            "pluoa_ids": [2, 3],
        }

        mock_get_objective_by_id.return_value = objective

        result = self.view.processView()

        mock_get_objective_by_id.assert_called_once_with(
            self.mock_request, self.mock_request.matchdict["objective_id"]
        )

        self.assertEqual(
            result,
            objective,
        )

        self.assertTrue(self.view.returnRawViewResult)

    @patch("climmob.views.prj_objective.delete_objective_by_id")
    def test_process_view_delete_existing_objective(self, mock_delete_objective_by_id):
        self.mock_request.method = "DELETE"

        mock_delete_objective_by_id.return_value = True, ""

        result = self.view.processView()

        mock_delete_objective_by_id.assert_called_once_with(
            self.mock_request, self.mock_request.matchdict["objective_id"]
        )

        self.assertTrue(self.view.returnRawViewResult)
