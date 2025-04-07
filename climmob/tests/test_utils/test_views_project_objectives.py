import json
import unittest
from http import HTTPStatus
from unittest.mock import MagicMock, patch, call
from climmob.views.project_objective import ObjectiveByIdView


class TestProjectObjectiveByIdView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.method = None
        self.mock_request.matchdict = {"objective_id": "1"}

        self.mock_user = MagicMock()
        self.mock_user.login = "test_user"

        self.view = ObjectiveByIdView(self.mock_request)
        self.view.user = self.mock_user

    @patch("climmob.views.project_objective.get_objective_by_id")
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

    @patch("climmob.views.project_objective.delete_objective_by_id")
    def test_process_view_delete_existing_objective(self, mock_delete_objective_by_id):
        self.mock_request.method = "DELETE"

        mock_delete_objective_by_id.return_value = True, ""

        result = self.view.processView()

        mock_delete_objective_by_id.assert_called_once_with(
            self.mock_request, self.mock_request.matchdict["objective_id"]
        )

        self.assertTrue(self.view.returnRawViewResult)

        self.assertEqual(result.status_int, HTTPStatus.NO_CONTENT)

    @patch("climmob.views.project_objective.ObjectiveByIdView.process_patch")
    def test_process_view_patch(self, mock_process_patch):  # pragma: no cover
        self.mock_request.method = "PATCH"

        result = self.view.processView()

        mock_process_patch.assert_called_once_with(
            self.mock_request.matchdict["objective_id"]
        )

    @patch(
        "climmob.views.project_objective.ObjectiveByIdView.update_objective_luoaobjs"
    )
    @patch("climmob.views.project_objective.get_objective_by_id")
    @patch("climmob.views.project_objective.update_objective", return_value=(True, ""))
    @patch(
        "climmob.views.project_objective.ProjectObjectives",
        return_value={"pobjective_id": 1, "pobjective_name": "Off-farm verification"},
    )
    def test_process_patch_valid(
        self,
        mock_project_objective_class,
        mock_update_objective,
        mock_get_objective_by_id,
        mock_update_objective_luoaobjs,
    ):
        updated_name = "Off-farm verification"
        update_luoas = [4, 6]
        pobjective_id = self.mock_request.matchdict["objective_id"]

        self.mock_request.json_body = {
            "pobjective_name": updated_name,
            "luoas": update_luoas,
        }

        expected_output = {
            "pobjective_id": 1,
            "pobjective_name": "Off-farm verification",
            "luoas": update_luoas,
        }

        mock_get_objective_by_id.return_value = expected_output

        result = self.view.process_patch(pobjective_id)

        mock_update_objective_luoaobjs.assert_called_once_with(
            update_luoas, pobjective_id
        )

        mock_get_objective_by_id.assert_called_once_with(
            self.mock_request, self.mock_request.matchdict["objective_id"]
        )

        result_body = json.loads(result.body.decode("utf-8"))

        self.assertEqual(result.status_int, HTTPStatus.OK)

        self.assertEqual(result_body, expected_output)

    @patch(
        "climmob.views.project_objective.get_location_unit_of_analysis_objectives_by_proj_objective_id"
    )
    @patch("climmob.views.project_objective.ObjectiveByIdView.delete_removed_luoaobjs")
    @patch("climmob.views.project_objective.ObjectiveByIdView.add_new_luoaobjs")
    def test_update_objective_luoaobjs(
        self,
        mock_add_new_luoaobjs,
        mock_delete_removed_luoaobjs,
        mock_get_location_unit_of_analysis_objectives_by_proj_objective_id,
    ):
        pobj_id = self.mock_request.matchdict["objective_id"]

        # Previous list => [4, 7]
        loc_unit_of_an_objectives = [
            {
                "pluoaobj_id": 1,
                "pluoa_id": 4,  #
                "pobjective_id": pobj_id,
            },
            {
                "pluoaobj_id": 2,
                "pluoa_id": 7,  #
                "pobjective_id": pobj_id,
            },
        ]

        # Updated list
        loc_unit_of_analyses = [4, 6]

        mock_get_location_unit_of_analysis_objectives_by_proj_objective_id.return_value = (
            loc_unit_of_an_objectives
        )

        self.view.update_objective_luoaobjs(loc_unit_of_analyses, pobj_id)

        mock_get_location_unit_of_analysis_objectives_by_proj_objective_id.assert_called_once_with(
            self.mock_request, pobj_id
        )

        mock_delete_removed_luoaobjs.assert_called_once_with(
            loc_unit_of_an_objectives, loc_unit_of_analyses
        )

        mock_add_new_luoaobjs.assert_called_once_with(
            loc_unit_of_an_objectives, loc_unit_of_analyses, pobj_id
        )

    @patch("climmob.views.project_objective.add_location_unit_of_analysis_objective")
    def test_add_new_luoaobjs(self, mock_add_location_unit_of_analysis_objective):
        pobj_id = self.mock_request.matchdict["objective_id"]

        # Previous list => [4, 7]
        loc_unit_of_an_objectives = [
            {
                "pluoaobj_id": 1,
                "pluoa_id": 4,  #
                "pobjective_id": pobj_id,
            },
            {
                "pluoaobj_id": 2,
                "pluoa_id": 7,  #
                "pobjective_id": pobj_id,
            },
        ]

        # Updated list
        loc_unit_of_analyses = [4, 6]

        # What it needs to be added
        expected_parameters = [6]

        self.view.add_new_luoaobjs(
            loc_unit_of_an_objectives, loc_unit_of_analyses, pobj_id
        )

        self.assertEqual(
            mock_add_location_unit_of_analysis_objective.call_count,
            len(expected_parameters),
        )

        expected_calls = [
            call(self.mock_request, pobj_id, p) for p in expected_parameters
        ]

        mock_add_location_unit_of_analysis_objective.assert_has_calls(
            expected_calls, any_order=False
        )

    @patch("climmob.views.project_objective.delete_location_unit_of_analysis_objective")
    def test_delete_removed_luoaobjs(
        self, mock_delete_location_unit_of_analysis_objective
    ):
        pobj_id = self.mock_request.matchdict["objective_id"]

        # Previous list => [4, 7]
        loc_unit_of_an_objectives = [
            {
                "pluoaobj_id": 1,
                "pluoa_id": 4,  #
                "pobjective_id": pobj_id,
            },
            {
                "pluoaobj_id": 2,
                "pluoa_id": 7,  #
                "pobjective_id": pobj_id,
            },
        ]

        # Updated list
        loc_unit_of_analyses = [4, 6]

        # What it needs to be deleted => [7]. The parameter is the pluoaobj_id
        expected_parameters = [2]

        self.view.delete_removed_luoaobjs(
            loc_unit_of_an_objectives, loc_unit_of_analyses
        )

        self.assertEqual(
            mock_delete_location_unit_of_analysis_objective.call_count,
            len(expected_parameters),
        )

        expected_calls = [call(self.mock_request, p) for p in expected_parameters]

        mock_delete_location_unit_of_analysis_objective.assert_has_calls(
            expected_calls, any_order=False
        )
