import json
import os
import shutil
import unittest
import datetime
from unittest.mock import MagicMock, patch
from climmob.views.Api.projectRegistryStart import (
    ReadProjectCombinationsView,
    SetUsableCombinationsView,
    SetAvailabilityCombinationView,
    CreatePackagesView,
    CreateProjectRegistryView,
    CancelRegistryApiView,
    CloseRegistryApiView,
    ReadRegistryStructureView,
    PushJsonToRegistryView,
    RegistryDataCleaningView,
    ReadRegistryDataView,
    ApiRegistrationPushProcess,
    functionForProcessAndValidateUpdate,
)

GET_PROJECT_PROGRESS = {
    "enumerators_by_user": {"john_doe": 3, "ana_smith": 2},
    "enumerators": True,
    "numberOfFieldAgents": 5,
    "technology": True,
    "techalias": True,
    "numberOfCombinations": 54,
    "registry": True,
    "numberOfQuestionsInRegistry": 18,
    "regsubmissions": 1,
    "regtotal": 140,
    "regerrors": 3,
    "regperc": 93.33,
    "lastreg": "2025-04-18",
    "assessment": True,
    "asssubmissions": 1,
    "assessments": [
        {
            "ass_cod": "A01",
            "ass_desc": "Market Assessment Round 1",
            "ass_status": "active",
            "asstotal": 100,
            "assperc": 71.43,
            "submissions": 140,
            "errors": 1,
            "lastass": "2025-04-19",
            "enketo_url": "https://123.com",
            "ass_rhomis": "RHOMISv3",
        },
        {
            "ass_cod": "A02",
            "ass_desc": "On-Farm Testing Phase 2",
            "ass_status": "pending",
            "asstotal": 0,
            "assperc": 0.0,
            "submissions": 140,
            "errors": 0,
            "lastass": "Without submissions",
            "enketo_url": "",
            "ass_rhomis": "",
        },
    ],
    "metadata": True,
}

GET_PROJECT_DATA = {
    "project_id": "abc123",
    "project_cod": "PROJ001",
    "project_name": "Climate Research Project",
    "project_abstract": "Investigación sobre clima y cultivos en regiones rurales.",
    "project_tags": "agriculture,climate,trial",
    "project_pi": "Jane Doe",
    "project_piemail": "jane.doe@example.com",
    "project_active": 1,
    "project_public": 0,
    "project_regstatus": 1,
    "project_assstatus": 0,
    "project_createcomb": 1,
    "project_createpkgs": 0,
    "project_numobs": 100,
    "project_numcom": 3,
    "project_lat": "10.1234",
    "project_lon": "-75.1234",
    "project_creationdate": datetime.datetime(2025, 1, 15, 10, 0),
    "project_localvariety": 0,
    "project_cnty": "CO",
    "project_registration_and_analysis": 1,
    "project_label_a": "Option A",
    "project_label_b": "Option B",
    "project_label_c": "Option C",
    "project_template": 1,
    "extra": '{"notes": "Extra info about project."}',
    "project_status": 1,
    "project_type": 2,
    "project_location": 3,
    "project_unit_of_analysis": 4,
    "project_affiliation": "CIAT",
    "climmob_analytics": 1,
    "project_curated_cropname": "Maize",
    "project_continent": 5,
    # Datos agregados por funciones adicionales
    "languages": ["en", "es"],
    "objectives": [
        {"id": 1, "description": "Measure yield under drought"},
        {"id": 2, "description": "Assess varietal preferences"},
    ],
}


class MockResponse:  # TestPushJsonToRegistryView
    def __init__(self, status_code, body):
        self.status_code = status_code
        self.body = body


class FakeSelf:  # TestApiRegistrationPushProcess
    def __init__(self):
        self.apiKey = "TESTKEY"
        self.user = MagicMock()
        self.user.login = "test_user"
        self.request = MagicMock()
        self._ = lambda x: x


class TestReadProjectCombinationsView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request._ = lambda x: x
        self.request.method = "GET"
        self.view = ReadProjectCombinationsView(self.request)
        self.view._ = lambda x: x
        self.view.user = MagicMock(login="test_user")

    def test_process_view_read_project_combination_no_get(self):
        self.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    def test_process_view_read_project_combination_json_error(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
                "user_owner": "Owner_user",
                "other_param": "other_param",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_read_project_combination_json_error_2(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_read_project_combination_json_error_body(self):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_read_project_combination_json_error_no_data(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_read_project_combination_no_project_code(
        self, mock_projectExists
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(
            {
                "enumerators_by_user": {},
                "enumerators": False,
                "numberOfFieldAgents": 0,
                "technology": True,
                "techalias": True,
                "numberOfCombinations": 54,
                "registry": True,
                "numberOfQuestionsInRegistry": 18,
                "regsubmissions": 1,
                "regtotal": 140,
                "regerrors": 3,
                "regperc": 93.33,
                "lastreg": "2025-04-18",
                "assessment": True,
                "asssubmissions": 1,
                "assessments": [
                    {
                        "ass_cod": "A01",
                        "ass_desc": "Market Assessment Round 1",
                        "ass_status": "active",
                        "asstotal": 100,
                        "assperc": 71.43,
                        "submissions": 140,
                        "errors": 1,
                        "lastass": "2025-04-19",
                        "enketo_url": "https://123.com",
                        "ass_rhomis": "RHOMISv3",
                    },
                    {
                        "ass_cod": "A02",
                        "ass_desc": "On-Farm Testing Phase 2",
                        "ass_status": "pending",
                        "asstotal": 0,
                        "assperc": 0.0,
                        "submissions": 140,
                        "errors": 0,
                        "lastass": "Without submissions",
                        "enketo_url": "",
                        "ass_rhomis": "",
                    },
                ],
                "metadata": True,
            },
            100,
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner",
        return_value="RANDOMNUM123",
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_project_combination_no_enumeradors(
        self, mock_projectExists, mock_getTheProjectIdForOwner, mock_getProjectProgress
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You must have the field agents, technologies, technology options and created the registration form to read the combinations.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinations",
        return_value=(
            [
                {"tech_id": "T001", "tech_name": "Fertilizer A"},
                {"tech_id": "T002", "tech_name": "Seed Type B"},
                {"tech_id": "T003", "tech_name": "Pesticide C"},
            ],
            3,
            [
                {
                    "comb_code": 1,
                    "comb_usable": True,
                    "quantity_available": 50,
                    "tech_id": "T001",
                    "alias_id": "A001",
                    "alias_name": "Urea 46%",
                    "alias_order": 1,
                    "number_of_times_used": 12,
                },
                {
                    "comb_code": 1,
                    "comb_usable": True,
                    "quantity_available": 50,
                    "tech_id": "T002",
                    "alias_id": "A015",
                    "alias_name": "Hybrid Maize",
                    "alias_order": 2,
                    "number_of_times_used": 12,
                },
                {
                    "comb_code": 2,
                    "comb_usable": False,
                    "quantity_available": 0,
                    "tech_id": "T001",
                    "alias_id": "C003",  # Custom alias sin i18n
                    "alias_name": "Organic Fertilizer X",
                    "alias_order": 1,
                    "number_of_times_used": 0,
                },
            ],
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.createCombinations",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner",
        return_value="RANDOMNUM123",
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_project_combination_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getProjectProgress,
        mock_createCombinations,
        mock_getCombinations,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b'{"techs": [{"tech_id": "T001", "tech_name": "Fertilizer A"}, {"tech_id": "T002", "tech_name": "Seed Type B"}, {"tech_id": "T003", "tech_name": "Pesticide C"}], "combinations": [{"ncomb": 3, "comb_usable": false, "quantity_available": 0, "elements": [{"alias_id": "A001", "alias_name": "Urea 46%"}, {"alias_id": "A015", "alias_name": "Hybrid Maize"}, {"alias_id": "C003", "alias_name": "Organic Fertilizer X"}]}]}',
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", "RANDOMNUM123", self.request
        )
        mock_createCombinations.assert_called_once()
        mock_getCombinations.assert_called_once_with("RANDOMNUM123", self.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinations",
        return_value=(
            [
                {"tech_id": "T001", "tech_name": "Fertilizer A"},
            ],
            3,
            [
                {
                    "comb_code": 1,
                    "comb_usable": True,
                    "quantity_available": 50,
                    "tech_id": "T001",
                    "alias_id": "A001",
                    "alias_name": "Urea 46%",
                    "alias_order": 1,
                    "number_of_times_used": 12,
                },
                {
                    "comb_code": 1,
                    "comb_usable": True,
                    "quantity_available": 50,
                    "tech_id": "T002",
                    "alias_id": "A015",
                    "alias_name": "Hybrid Maize",
                    "alias_order": 2,
                    "number_of_times_used": 12,
                },
                {
                    "comb_code": 2,
                    "comb_usable": False,
                    "quantity_available": 0,
                    "tech_id": "T001",
                    "alias_id": "C003",  # Custom alias sin i18n
                    "alias_name": "Organic Fertilizer X",
                    "alias_order": 1,
                    "number_of_times_used": 0,
                },
            ],
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.createCombinations",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner",
        return_value="RANDOMNUM123",
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_project_combination_success_one_tech(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getProjectProgress,
        mock_createCombinations,
        mock_getCombinations,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b'{"techs": [{"tech_id": "T001", "tech_name": "Fertilizer A"}], "combinations": [{"ncomb": 0, "comb_usable": true, "quantity_available": 50, "elements": [{"alias_id": "A001", "alias_name": "Urea 46%"}]}, {"ncomb": 1, "comb_usable": true, "quantity_available": 50, "elements": [{"alias_id": "A015", "alias_name": "Hybrid Maize"}]}, {"ncomb": 3, "comb_usable": false, "quantity_available": 0, "elements": [{"alias_id": "C003", "alias_name": "Organic Fertilizer X"}]}]}',
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", "RANDOMNUM123", self.request
        )
        mock_createCombinations.assert_called_once()
        mock_getCombinations.assert_called_once_with("RANDOMNUM123", self.request)


class TestSetUsableCombinationsView(unittest.TestCase):
    def setUp(self):
        self.view = SetUsableCombinationsView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "ncomb": "A01",
                "status": "0",
            }
        )

    def test_process_view_no_set_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_set_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_set_no_data_params(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
                "ncomb": "A01",
                "status": "0",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_no_set_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to set usable combinations.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_registry_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has already started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(
            {
                "enumerators_by_user": {},
                "enumerators": False,
                "numberOfFieldAgents": 0,
                "technology": True,
                "techalias": True,
                "numberOfCombinations": 54,
                "registry": True,
                "numberOfQuestionsInRegistry": 18,
                "regsubmissions": 1,
                "regtotal": 140,
                "regerrors": 3,
                "regperc": 93.33,
                "lastreg": "2025-04-18",
                "assessment": True,
                "asssubmissions": 1,
                "assessments": [
                    {
                        "ass_cod": "A01",
                        "ass_desc": "Market Assessment Round 1",
                        "ass_status": "active",
                        "asstotal": 100,
                        "assperc": 71.43,
                        "submissions": 140,
                        "errors": 1,
                        "lastass": "2025-04-19",
                        "enketo_url": "https://123.com",
                        "ass_rhomis": "RHOMISv3",
                    },
                    {
                        "ass_cod": "A02",
                        "ass_desc": "On-Farm Testing Phase 2",
                        "ass_status": "pending",
                        "asstotal": 0,
                        "assperc": 0.0,
                        "submissions": 140,
                        "errors": 0,
                        "lastass": "Without submissions",
                        "enketo_url": "",
                        "ass_rhomis": "",
                    },
                ],
                "metadata": True,
            },
            100,
        ),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_no_fa_tech_or_regis(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You must have the field agents, technology options and registration form ready.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_no_combinations(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"The combinations have not been created.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(False, ""),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_no_combinations_whit_this_id(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a combination with this ID.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(True, 1),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_status_error(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "ncomb": "A01",
                "status": "4",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"The value of the status is 0 [unusable] or 1 [usable]."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(True, 0),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_set_no_change(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"The state is the same.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.setCombinationStatus")
    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(True, 1),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_set_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
        mock_setCombinationStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"The state of the combination was changed.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)
        mock_setCombinationStatus.assert_called_once_with(
            1, "A01", "0", self.view.request
        )


class TestSetAvailabilityCombinationView(unittest.TestCase):
    def setUp(self):
        self.view = SetAvailabilityCombinationView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "ncomb": "A01",
                "availability": "4",
            }
        )

    def test_process_view_no_set_availability_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_no_set_availability_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_no_set_availability_json_no_data(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "",
                "ncomb": "A01",
                "availability": "4",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_no_set_availability_no_project_exist(
        self, mock_projectExists
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_availability_no_access_to_set(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to set usable combinations.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_availability_registration_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has already started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(
            {
                "enumerators_by_user": {"john_doe": 3, "ana_smith": 2},
                "enumerators": True,
                "numberOfFieldAgents": 5,
                "technology": False,
                "techalias": True,
                "numberOfCombinations": 54,
                "registry": True,
                "numberOfQuestionsInRegistry": 18,
                "regsubmissions": 1,
                "regtotal": 140,
                "regerrors": 3,
                "regperc": 93.33,
                "lastreg": "2025-04-18",
                "assessment": True,
                "asssubmissions": 1,
                "assessments": [
                    {
                        "ass_cod": "A01",
                        "ass_desc": "Market Assessment Round 1",
                        "ass_status": "active",
                        "asstotal": 100,
                        "assperc": 71.43,
                        "submissions": 140,
                        "errors": 1,
                        "lastass": "2025-04-19",
                        "enketo_url": "https://123.com",
                        "ass_rhomis": "RHOMISv3",
                    },
                    {
                        "ass_cod": "A02",
                        "ass_desc": "On-Farm Testing Phase 2",
                        "ass_status": "pending",
                        "asstotal": 0,
                        "assperc": 0.0,
                        "submissions": 140,
                        "errors": 0,
                        "lastass": "Without submissions",
                        "enketo_url": "",
                        "ass_rhomis": "",
                    },
                ],
                "metadata": True,
            },
            100,
        ),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_availability_no_technology(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You must have the field agents, technology options and registration form ready.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_availability_no_combination(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"The combinations have not been created.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        # mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(False, ""),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_availability_no_combination_whit_id(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"You do not have a combination with this ID.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(True, 1),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_no_set_availability_availability_no_number(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "ncomb": "A01",
                "availability": "four",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The number of items available in the combination must be an integer.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.setCombinationQuantityAvailable")
    @patch(
        "climmob.views.Api.projectRegistryStart.getCombinationStatus",
        return_value=(True, 1),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_set_availability_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getCombinationStatus,
        mock_setCombinationQuantityAvailable,
    ):

        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body, b"The availability of the combination was changed."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getCombinationStatus.assert_called_once_with(1, "A01", self.view.request)
        mock_setCombinationQuantityAvailable.assert_called_once_with(
            1, "A01", "4", self.view.request
        )


class TestCreateProjectRegistryView(unittest.TestCase):
    def setUp(self):
        self.view = CreateProjectRegistryView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )

    def test_process_view_create_project_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_create_project_json_error(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "other_param": "other_param",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_create_project_json_error_2(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_create_project_json_no_data(self):
        self.view.body = json.dumps({"project_cod": "PRJ001", "user_owner": ""})
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_create_project_no_project_code(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_no_allow_to_create(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to create the registry.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_registration_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has already started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(
            {
                "enumerators_by_user": {},
                "enumerators": False,
                "numberOfFieldAgents": 0,
                "technology": True,
                "techalias": True,
                "numberOfCombinations": 54,
                "registry": True,
                "numberOfQuestionsInRegistry": 18,
                "regsubmissions": 1,
                "regtotal": 140,
                "regerrors": 3,
                "regperc": 93.33,
                "lastreg": "2025-04-18",
                "assessment": True,
                "asssubmissions": 1,
                "assessments": [
                    {
                        "ass_cod": "A01",
                        "ass_desc": "Market Assessment Round 1",
                        "ass_status": "active",
                        "asstotal": 100,
                        "assperc": 71.43,
                        "submissions": 140,
                        "errors": 1,
                        "lastass": "2025-04-19",
                        "enketo_url": "https://123.com",
                        "ass_rhomis": "RHOMISv3",
                    },
                    {
                        "ass_cod": "A02",
                        "ass_desc": "On-Farm Testing Phase 2",
                        "ass_status": "pending",
                        "asstotal": 0,
                        "assperc": 0.0,
                        "submissions": 140,
                        "errors": 0,
                        "lastass": "Without submissions",
                        "enketo_url": "",
                        "ass_rhomis": "",
                    },
                ],
                "metadata": True,
            },
            100,
        ),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_no_field_agents(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You must have the field agents, technology options and registration form ready.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_no_combinations(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"This project has not created the combinations. You need to create the combinations first.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreatePackages",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_no_packages(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_projectCreatePackages,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"Packages have not available yet. You need to do the randomization first.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_projectCreatePackages.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.startTheRegistry",
        return_value=(None, "error"),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectData",
        return_value=GET_PROJECT_DATA,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreatePackages",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_structure_problem(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_projectCreatePackages,
        mock_getProjectData,
        mock_startTheRegistry,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form. Contact the ClimMob team with the next message to get the solution to the problem: error",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_projectCreatePackages.assert_called_once_with(1, self.view.request)
        mock_getProjectData.assert_called_once_with(1, self.view.request)
        mock_startTheRegistry.assert_called_once()

    @patch(
        "climmob.views.Api.projectRegistryStart.startTheRegistry",
        return_value=(True, b""),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectData",
        return_value=GET_PROJECT_DATA,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreatePackages",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_project_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_projectCreatePackages,
        mock_getProjectData,
        mock_startTheRegistry,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"Registration started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_projectCreatePackages.assert_called_once_with(1, self.view.request)
        mock_getProjectData.assert_called_once_with(1, self.view.request)
        mock_startTheRegistry.assert_called_once()


class TestCreatePackagesView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request._ = lambda x: x
        self.request.method = "GET"
        self.view = CreatePackagesView(self.request)
        self.view._ = lambda x: x
        self.view.user = MagicMock(login="test_user")
        self.view.request.locale_name = "en"

    def test_process_view_create_package_no_get(self):
        self.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    def test_process_view_create_package_json_error(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
                "user_owner": "Owner_user",
                "other_param": "other_param",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_create_package_json_error_2(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_create_package_json_error_body(self):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_create_package_json_error_no_data(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_create_package_no_project_code(self, mock_projectExists):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_no_allow_create(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to create packages.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(
            {
                "enumerators_by_user": {},
                "enumerators": False,
                "numberOfFieldAgents": 0,
                "technology": False,
                "techalias": True,
                "numberOfCombinations": 54,
                "registry": True,
                "numberOfQuestionsInRegistry": 18,
                "regsubmissions": 1,
                "regtotal": 140,
                "regerrors": 3,
                "regperc": 93.33,
                "lastreg": "2025-04-18",
                "assessment": True,
                "asssubmissions": 1,
                "assessments": [
                    {
                        "ass_cod": "A01",
                        "ass_desc": "Market Assessment Round 1",
                        "ass_status": "active",
                        "asstotal": 100,
                        "assperc": 71.43,
                        "submissions": 140,
                        "errors": 1,
                        "lastass": "2025-04-19",
                        "enketo_url": "https://123.com",
                        "ass_rhomis": "RHOMISv3",
                    },
                    {
                        "ass_cod": "A02",
                        "ass_desc": "On-Farm Testing Phase 2",
                        "ass_status": "pending",
                        "asstotal": 0,
                        "assperc": 0.0,
                        "submissions": 140,
                        "errors": 0,
                        "lastass": "Without submissions",
                        "enketo_url": "",
                        "ass_rhomis": "",
                    },
                ],
                "metadata": True,
            },
            100,
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_no_field_agents(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectProgress,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You must have the field agents, technology options and registration form ready.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_no_created_combinations(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"This project has not created the combinations. You need to create the combinations first.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.create_randomization")
    @patch("climmob.views.Api.projectRegistryStart.createSettings", return_value={})
    @patch(
        "climmob.views.Api.projectRegistryStart.deleteProjectPackages",
        return_value=True,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.updateCreatePackages", return_value=True
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectData",
        return_value=(
            {
                "project_createpkgs": 1,
            }
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_success_pkgs_1(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getProjectData,
        mock_updateCreatePackages,
        mock_deleteProjectPackages,
        mock_createSettings,
        mock_create_randomization,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b"ClimMob has started the package creation process, please check back in a moment to verify that the process has been completed.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getProjectData.assert_called_once_with(1, self.view.request)
        mock_updateCreatePackages.assert_called_once_with(1, 2, self.view.request)
        mock_deleteProjectPackages.assert_called_once_with(1, self.view.request)
        mock_createSettings.assert_called_once_with(self.view.request)
        mock_create_randomization.assert_called_once_with(
            self.view.request, "en", "Owner_user", 1, "PRJ001", {}
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectData",
        return_value=(
            {
                "project_createpkgs": 2,
            }
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_success_pkgs_2(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getProjectData,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.body,
            b"ClimMob is still generating the packages, please try this request again in a moment.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getProjectData.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectData",
        return_value=(
            {
                "project_createpkgs": 3,
            }
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_success_pkgs_3(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getProjectData,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"There was a problem with the creation of the packages please check the available quantity of each combination.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getProjectData.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.getPackages", return_value=(1, 1))
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectData",
        return_value=(
            {
                "project_createpkgs": 0,
            }
        ),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectCreateCombinations",
        return_value=False,
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 100),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_create_package_success_pkgs_0(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_getProjectProgress,
        mock_projectCreateCombinations,
        mock_getProjectData,
        mock_getPackages,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_projectCreateCombinations.assert_called_once_with(1, self.view.request)
        mock_getProjectData.assert_called_once_with(1, self.view.request)
        mock_getPackages.assert_called_once_with("Owner_user", 1, self.view.request)


class TestCancelRegistryApiView(unittest.TestCase):
    def setUp(self):
        self.view = CancelRegistryApiView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )

    def test_process_cancel_no_set_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_cancel_no_set_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_cancel_no_data_params(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_cancel_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_cancel_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to cancel the registry.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_cancel_registry_no_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"The registration has not started. You cannot cancel it."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.stopTasksByProcess")
    @patch("climmob.views.Api.projectRegistryStart.setRegistryStatus")
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_cancel_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_setRegistryStatus,
        mock_stopTasksByProcess,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"Cancel registration.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_setRegistryStatus.assert_called_once_with(
            "Owner_user", "PRJ001", 1, 0, self.view.request
        )
        mock_stopTasksByProcess.assert_called_once_with(self.view.request, 1)


class TestReadRegistryStructureView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request._ = lambda x: x
        self.request.method = "GET"
        self.view = ReadRegistryStructureView(self.request)
        self.view._ = lambda x: x
        self.view.user = MagicMock(login="test_user")

    def test_process_view_read_registry_no_get(self):
        self.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    def test_process_view_read_registry_json_error(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
                "user_owner": "Owner_user",
                "other_param": "other_param",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_read_registry_json_error_2(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_read_registry_json_error_3(self):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_read_registry_json_no_data(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_read_registry_no_project_code(self, mock_projectExists):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_registry_no_registration(
        self, mock_projectExists, mock_getTheProjectIdForOwner, mock_projectRegStatus
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has not started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.request)

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_registry_registry_no_started(
        self, mock_projectExists, mock_getTheProjectIdForOwner, mock_projectRegStatus
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has not started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.generateStructureForInterfaceForms",
        return_value=({"Data": "data"}),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_registry_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_projectRegStatus,
        mock_generateStructureForInterfaceForms,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'{"Data": "data"}')
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.request)
        mock_generateStructureForInterfaceForms.assert_called_once_with(
            "Owner_user", 1, "PRJ001", "registry", self.view.request
        )


class TestCloseRegistryApiView(unittest.TestCase):
    def setUp(self):
        self.view = CloseRegistryApiView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )

    def test_process_view_close_registry_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_close_registry_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_close_registry_data_params(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_close_registry_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_close_registry_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to finish the registry.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_close_registry_no_registration(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"The registration has not started. You cannot cancel it."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=({"regtotal": 0}, 0),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_close_registry_no_close_no_data(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"You cannot close the registration because you do not have data.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.setRegistryStatus")
    @patch(
        "climmob.views.Api.projectRegistryStart.getProjectProgress",
        return_value=(GET_PROJECT_PROGRESS, 0),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_close_registry_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_getProjectProgress,
        mock_setRegistryStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"Closed registration.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_getProjectProgress.assert_called_once_with(
            "Owner_user", "PRJ001", 1, self.view.request
        )
        mock_setRegistryStatus.assert_called_once_with(
            "Owner_user", "PRJ001", 1, 2, self.view.request
        )


class TestPushJsonToRegistryView(unittest.TestCase):
    def setUp(self):
        self.view = PushJsonToRegistryView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {"project_cod": "PRJ001", "user_owner": "Owner_user", "json": "json"}
        )

    def test_process_view_push_json_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_push_json_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_push_json_data_params(self):
        self.view.body = json.dumps(
            {"project_cod": "", "user_owner": "Owner_user", "json": "json"}
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_push_json_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_push_json_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to push information to the project.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_push_json_registry_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has not started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.isRegistryClose", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_push_json_registry_closed(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_isRegistryClose,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"Registration has closed. No more participants can be registered.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_isRegistryClose.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.ApiRegistrationPushProcess")
    @patch("climmob.views.Api.projectRegistryStart.generateStructureForInterfaceForms", return_value=[
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ])
    @patch("climmob.views.Api.projectRegistryStart.isRegistryClose", return_value=False)
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_push_json_registry_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_isRegistryClose,
        mock_generateStructureForInterfaceForms,
        mock_ApiRegistrationPushProcess,
    ):
        mock_ApiRegistrationPushProcess.return_value = MockResponse(
            status_code=200, body=b"Data registered."
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"Data registered.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_isRegistryClose.assert_called_once_with(1, self.view.request)


class TestApiRegistrationPushProcess(unittest.TestCase):
    def setUp(self):
        self.fake_self = FakeSelf()
        if not os.path.exists("./temp_test_repo"):
            os.makedirs("./temp_test_repo")

    def tearDown(self):
        if os.path.exists("./temp_test_repo"):
            shutil.rmtree("./temp_test_repo")

    def test_api_registration_no_structure(self):
        structure = {}
        dataworking = {}
        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(response.body, b"This project do not have structure.")

    def test_api_registration_json_raises_exception(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": '{"package_id": "123", "bad_json":}',
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }

        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )

        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(b"Error in the JSON sent by parameter.", response.body)

    def test_api_registration_error_json(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps({}),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }
        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"Error in the JSON sent by parameter. Check the obligatory Keys: package_id, some_data.",
        )

    def test_api_registration_error_param(
        self,
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {"package_id": "5", "some_data": "valid", "hacker_key": "boom"}
            ),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }

        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"Error in the JSON sent by parameter. Check the permited Keys: ['clm_start', 'clm_end', '_submitted_date', 'package_id', 'some_data']",
        )

    def test_api_registration_data_in_param_empty(
        self,
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps({"package_id": "   ", "some_data": "valid"}),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }

        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(b"Not all parameters have data", response.body)

    def test_api_registration_no_int_packg_code(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps({"package_id": "abc123", "some_data": "ok"}),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }
        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(b"The package code must be a number", response.body)

    @patch("climmob.views.Api.projectRegistryStart.getProjectNumobs", return_value=2)
    def test_api_registration_no_package_code(
        self,
        mock_getProjectNumobs,
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps({"package_id": "5", "some_data": "valid"}),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }
        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )

        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body, b"ERROR: You do not have a package code with this ID."
        )

    @patch("climmob.views.Api.projectRegistryStart.storeJSONInMySQL")
    @patch("climmob.views.Api.projectRegistryStart.getProjectNumobs", return_value=10)
    @patch("uuid.uuid1", return_value="12345678")
    def test_api_registration_reads_log_error(
        self, mock_uuid, mock_getProjectNumobs, mock_storeJSONInMySQL
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps({"package_id": "5", "some_data": "valid"}),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }
        ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )
        json_dir = os.path.join(
            self.fake_self.request.registry.settings["user.repository"],
            "Owner_user",
            "PRJ001",
            "data",
            "reg",
            "json",
            "12345678",
        )
        os.makedirs(json_dir, exist_ok=True)

        log_path = os.path.join(json_dir, "12345678.log")
        with open(log_path, "w") as f:
            f.write(
                """<?xml version="1.0"?>
            <log>
                <error Error="Simulated system failure"/>
            </log>"""
            )
        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )

        self.assertEqual(response.status, "401 Unauthorized")
        self.assertIn(
            b"The data could not be registered. ERROR: Simulated system failure",
            response.body,
        )
        mock_storeJSONInMySQL.assert_called()

    @patch("climmob.views.Api.projectRegistryStart.storeJSONInMySQL")
    @patch("climmob.views.Api.projectRegistryStart.getProjectNumobs", return_value=10)
    def test_api_registration_successful(
        self, mock_getProjectNumobs, mock_storeJSONInMySQL
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST162",
                        "question_datafield": "package_id",
                        "question_requiredvalue": 1,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "some_data",
                        "question_requiredvalue": 1,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps({"package_id": "5", "some_data": "valid"}),
            "user_owner": "Owner_user",
            "project_cod": "PRJ001",
        }
        response = ApiRegistrationPushProcess(
            self.fake_self, structure, dataworking, activeProjectId=1
        )

        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.body, b"Data registered.")
        mock_storeJSONInMySQL.assert_called_once()


class TestReadRegistryDataView(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request._ = lambda x: x
        self.request.method = "GET"
        self.view = ReadRegistryDataView(self.request)
        self.view._ = lambda x: x
        self.view.user = MagicMock(login="test_user")

    def test_process_view_read_registry_no_get(self):
        self.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts GET method.")

    def test_process_view_read_registry_json_error(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
                "user_owner": "Owner_user",
                "other_param": "other_param",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_read_registry_json_error_2(self):
        self.view.body = json.dumps(
            {
                "project_cod": "PROJ123",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_read_registry_json_error_body(self):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Error in the JSON, It does not have the 'body' parameter."
        )

    def test_process_view_read_registry_json_error_no_data(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_read_registry_no_project_code(self, mock_projectExists):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_registry_no_registration_started(
        self, mock_projectExists, mock_getTheProjectIdForOwner, mock_projectRegStatus
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has not started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner("test_user", "Owner_user", "PRJ001", self.request)

    @patch(
        "climmob.views.Api.projectRegistryStart.getJSONResult",
        return_value=({"data": "data", "registry": "registry"}),
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_read_registry_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_projectRegStatus,
        mock_getJSONResult,
    ):
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'{"structure": "registry", "data": "data"}')
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.request
        )
        mock_getTheProjectIdForOwner("test_user", "Owner_user", "PRJ001", self.request)


class TestRegistryDataCleaningView(unittest.TestCase):
    def setUp(self):
        self.view = RegistryDataCleaningView(MagicMock())
        self.view.request.method = "POST"
        self.view.user = MagicMock(login="test_user")
        self.view._ = MagicMock(side_effect=lambda x: x)
        self.view.body = json.dumps(
            {
                "project_cod": "PRJ001",
                "user_owner": "Owner_user",
                "json": json.dumps({"package_id": "5", "some_data": "valid"}),
            }
        )

    def test_process_view_registry_data_json_no_post(self):
        self.view.request.method = ""
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Only accepts POST method.")

    def test_process_view_registry_data_json_error(self):
        self.view.body = json.dumps(
            {
                "other_cathegory": "Uncategorized",
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Error in the JSON.")

    def test_process_view_registry_data_json_data_params(self):
        self.view.body = json.dumps(
            {
                "project_cod": "",
                "user_owner": "Owner_user",
                "json": json.dumps({"package_id": "5", "some_data": "valid"}),
            }
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Not all parameters have data.")

    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=False)
    def test_process_view_registry_data_no_project_exist(self, mock_projectExists):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"There is no project with that code.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )

    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=4
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_registry_data_no_access(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body,
            b"The access assigned for this project does not allow you to push information to the project.",
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )

    @patch("climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_registry_data_registry_started(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.body, b"Registration has not started.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.isRegistryClose", return_value=True)
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_registry_data_registry_closed(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_isRegistryClose,
    ):
        response = self.view.processView()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.body, b"Registration has closed. You cannot edit the information."
        )
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_isRegistryClose.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.Api.projectRegistryStart.functionForProcessAndValidateUpdate")
    @patch(
        "climmob.views.Api.projectRegistryStart.generateStructureForInterfaceForms",
        return_value=({"data": "data"}),
    )
    @patch("climmob.views.Api.projectRegistryStart.isRegistryClose", return_value=False)
    @patch(
        "climmob.views.Api.projectRegistryStart.projectRegStatus", return_value=False
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getAccessTypeForProject", return_value=1
    )
    @patch(
        "climmob.views.Api.projectRegistryStart.getTheProjectIdForOwner", return_value=1
    )
    @patch("climmob.views.Api.projectRegistryStart.projectExists", return_value=True)
    def test_process_view_registry_data_success(
        self,
        mock_projectExists,
        mock_getTheProjectIdForOwner,
        mock_getAccessTypeForProject,
        mock_projectRegStatus,
        mock_isRegistryClose,
        mock_generateStructureForInterfaceForms,
        mock_functionForProcessAndValidateUpdate,
    ):
        mock_functionForProcessAndValidateUpdate.return_value = MockResponse(
            status_code=200, body=b"Data registered."
        )
        response = self.view.processView()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b"Data registered.")
        mock_projectExists.assert_called_once_with(
            "test_user", "Owner_user", "PRJ001", self.view.request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "Owner_user", "PRJ001", self.view.request
        )
        mock_getAccessTypeForProject.assert_called_once_with(
            "test_user", 1, self.view.request
        )
        mock_projectRegStatus.assert_called_once_with(1, self.view.request)
        mock_isRegistryClose.assert_called_once_with(1, self.view.request)
        mock_generateStructureForInterfaceForms.assert_called_once_with(
            "Owner_user", 1, "PRJ001", "registry", self.view.request
        )
        mock_functionForProcessAndValidateUpdate.assert_called_once()


class TestFunctionForProcessAndValidateUpdate(unittest.TestCase):
    def setUp(self):
        self.fake_self = FakeSelf()

    def test_function_for_process_and_validate_update_json_error(self):

        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1/group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {
                    "rowuuid": "abc-123/abc-456",
                    "group_field_1": "A/B",
                    "group_field_2": "B/C",
                }
            )
        }
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"Error in the JSON sent by parameter. Check the permitted Keys.",
        )

    def test_function_for_process_and_validate_update_no_obligatory_question(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {"json": json.dumps({"group_field_1": "A", "group_field_2": "B"})}
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"Error in the JSON sent by parameter. Check the obligatory Keys.",
        )

    def test_function_for_process_and_validate_update_no_json_data(self):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {"rowuuid": " ", "group_field_1": "A", "group_field_2": "B"}
            )
        }
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"Error in the JSON. Not all the obligatory parameters have data.",
        )

    @patch("climmob.views.Api.projectRegistryStart.sql_fetch_one", return_value=None)
    def test_function_for_process_and_validate_update_no_record_identifier(
        self, mock_sql_fetch_one
    ):
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {
                    "rowuuid": "abc-123",
                    "group_field_1/group_field_2": "A",
                    "group_field_2": "B",
                }
            )
        }
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(response.body, b"There is no record with this identifier")
        mock_sql_fetch_one.assert_called_once()

    @patch("climmob.views.Api.projectRegistryStart.sql_fetch_one")
    def test_function_for_process_and_validate_update_repeated_data(
        self, mock_sql_fetch_one
    ):
        mock_sql_fetch_one.return_value = {
            "rowuuid": "abc-123",
            "group_field_1": "A",
            "group_field_2": "B",
        }
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {"rowuuid": "abc-123", "group_field_1": "A", "group_field_2": "A"}
            )
        }
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"You have repeated data in the next column: group_field_2. Remember that the options can not be repeated.",
        )
        mock_sql_fetch_one.assert_called_once()

    @patch("climmob.views.Api.projectRegistryStart.sql_fetch_one")
    def test_function_for_process_and_validate_update_repeated_data_second_way(
        self, mock_sql_fetch_one
    ):
        mock_sql_fetch_one.return_value = {"rowuuid": "abc-123", "group_field_2": "A"}
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST001",
                        "question_datafield": "rowuuid",
                        "question_requiredvalue": 1,
                        "question_dtype2": 1,
                    },
                ]
            }
        ]
        dataworking = {"json": json.dumps({"rowuuid": "abc-123", "group_field_1": "A"})}
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(
            response.body,
            b"You have repeated data in the next column: group_field_2. Remember that the options can not be repeated.",
        )
        mock_sql_fetch_one.assert_called_once()

    @patch("climmob.views.Api.projectRegistryStart.update_edited_data")
    @patch("climmob.views.Api.projectRegistryStart.sql_fetch_one")
    def test_function_for_process_and_validate_update_data_not_at_json_success(
        self, mock_sql_fetch_one, mock_update_edited_data
    ):
        mock_sql_fetch_one.return_value = {"rowuuid": "abc-123", "group_field_2": "B"}
        mock_update_edited_data.return_value = (1, "Data registered.")
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {"json": json.dumps({"rowuuid": "abc-123", "group_field_1": "A"})}
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.body, b"Data registered.")
        mock_sql_fetch_one.assert_called_once()
        mock_update_edited_data.assert_called_once()

    @patch("climmob.views.Api.projectRegistryStart.update_edited_data")
    @patch("climmob.views.Api.projectRegistryStart.sql_fetch_one")
    def test_function_for_process_and_validate_update_update_error(
        self, mock_sql_fetch_one, mock_update_edited_data
    ):
        mock_sql_fetch_one.return_value = {
            "rowuuid": "abc-123",
            "group_field_1": "A",
            "group_field_2": "B",
        }
        mock_update_edited_data.return_value = (0, "Error.")
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 2,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 2,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {"rowuuid": "abc-123", "group_field_1": "A", "group_field_2": "A"}
            )
        }
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "401 Unauthorized")
        self.assertEqual(response.body, b"Error.")
        mock_sql_fetch_one.assert_called_once()

    @patch("climmob.views.Api.projectRegistryStart.update_edited_data")
    @patch("climmob.views.Api.projectRegistryStart.sql_fetch_one")
    def test_function_for_process_and_validate_update_data_success(
        self, mock_sql_fetch_one, mock_update_edited_data
    ):
        mock_sql_fetch_one.return_value = {
            "rowuuid": "abc-123",
            "group_field_1": "A",
            "group_field_2": "B",
        }
        mock_update_edited_data.return_value = (1, "Data registered.")
        structure = [
            {
                "section_questions": [
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_1",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                    {
                        "question_code": "QST999",
                        "question_datafield": "group_field_2",
                        "question_requiredvalue": 1,
                        "question_dtype2": 9,
                    },
                ]
            }
        ]
        dataworking = {
            "json": json.dumps(
                {"rowuuid": "abc-123", "group_field_1": "A", "group_field_2": "B"}
            )
        }
        response = functionForProcessAndValidateUpdate(
            self.fake_self,
            structure,
            dataworking,
            activeProjectId=1,
            user_owner="test_owner",
            project_cod="PRJ001",
            formId="FORMX",
        )
        self.assertEqual(response.status, "200 OK")
        self.assertEqual(response.body, b"Data registered.")
        mock_sql_fetch_one.assert_called_once()
        mock_update_edited_data.assert_called_once()
