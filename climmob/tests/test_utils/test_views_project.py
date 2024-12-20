import unittest
from unittest.mock import MagicMock, patch
from climmob.views.project import (
    GetUnitOfAnalysisByLocationView,
    GetObjectivesByLocationAndUnitOfAnalysisView,
)


class TestGetUnitOfAnalysisByLocationView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"locationid": "1"}
        self.mock_request.method = None
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = GetUnitOfAnalysisByLocationView(self.mock_request)
        self.view.user = self.mock_user

    @patch("climmob.views.project.get_all_unit_of_analysis_by_location")
    def test_process_view_get(self, mock_get_all_unit_of_analysis_by_location):
        self.mock_request.method = "GET"

        test_unit_of_analysis = [
            {
                "puoa_id": 2,
                "puoa_name": "Agricutural input",
                "puoa_lang": "en",
            }
        ]

        mock_get_all_unit_of_analysis_by_location.return_value = test_unit_of_analysis

        result = self.view.processView()

        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.mock_request, self.mock_request.matchdict["locationid"]
        )

        self.assertEqual(
            result,
            test_unit_of_analysis,
        )

    def test_process_view_post(self):
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, {})


class TestGetObjectivesByLocationAndUnitOfAnalysisView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"locationid": "1", "unitofanalysisid": "1"}
        self.mock_request.method = None
        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = GetObjectivesByLocationAndUnitOfAnalysisView(self.mock_request)
        self.view.user = self.mock_user

    @patch("climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis")
    def test_process_view_get(
        self, mock_get_all_objectives_by_location_and_unit_of_analysis
    ):
        self.mock_request.method = "GET"

        res_get_all_objectives_by_location_and_unit_of_analysis = [
            {
                "pobjective_id": 0,
                "pobjective_name": "Variety release",
                "pobjective_lang": "en",
            }
        ]

        mock_get_all_objectives_by_location_and_unit_of_analysis.return_value = (
            res_get_all_objectives_by_location_and_unit_of_analysis
        )

        result = self.view.processView()

        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.mock_request,
            self.mock_request.matchdict["locationid"],
            self.mock_request.matchdict["unitofanalysisid"],
        )

        self.assertEqual(
            result,
            res_get_all_objectives_by_location_and_unit_of_analysis,
        )

    def test_process_view_post(self):
        self.mock_request.method = "POST"

        result = self.view.processView()

        self.assertEqual(result, {})
