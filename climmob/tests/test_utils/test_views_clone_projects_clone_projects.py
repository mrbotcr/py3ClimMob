import unittest
from unittest.mock import patch, MagicMock, ANY, call

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.tests.test_utils.common import BaseViewTestCase
from climmob.views.cloneProjects.cloneProjects import (
    CloneProjectsView,
    get_all_information_for_project,
)


class TestModifyProjectView(BaseViewTestCase):
    view_class = CloneProjectsView
    request_method = "POST"

    def setup(self):
        super().setUp()
        self.view.request.registry.settings = {"projects.limit": "false"}

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getTotalNumberOfProjectsInClimMob",
        return_value=0,
    )
    def test_process_view_clone_projects_view_project_limits_true(
        self, mock_get_total_number_of_projects_in_climmob
    ):
        self.view.request.registry.settings = {
            "projects.limit": "true",
            "projects.quantity": 0,
        }
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)
        mock_get_total_number_of_projects_in_climmob.assert_called_once_with(
            self.view.request
        )

    def test_process_view_clone_project_view_stage_error(self):
        self.view.request.params = {"stage": "0"}
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)

    @patch(
        "climmob.views.cloneProjects.cloneProjects.projectExists", return_value=False
    )
    def test_process_view_clone_project_view_stage_not_1_project_not_exist(
        self, mock_project_exists
    ):
        self.view.request.params = {
            "stage": "2",
            "project": "CLIMMOB",
            "user": "test_user",
        }

        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
            self.assertEqual(context.exception.code, 404)
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.projectExists", return_value=False
    )
    def test_process_view_clone_project_view_no_stage_success(
        self, mock_project_exists
    ):
        self.view.request.params = {
            "project": "CLIMMOB",
            "user": "test_user",
        }
        self.view.request.POST = {"slt_project_by_owner": "test_user___CLIMMOB"}
        self.view.request.route_url = MagicMock(
            return_value="/cloneProject?stage=2&project=my_project&user=test_user"
        )
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location, "/cloneProject?stage=2&project=my_project&user=test_user"
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.projectExists", return_value=False
    )
    def test_process_view_clone_project_view_stage_error_success(
        self, mock_project_exists
    ):
        self.view.request.params = {
            "stage": "a",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        self.view.request.POST = {"slt_project_by_owner": "test_user___CLIMMOB"}
        self.view.request.route_url = MagicMock(
            return_value="/cloneProject?stage=2&project=my_project&user=test_user"
        )
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location, "/cloneProject?stage=2&project=my_project&user=test_user"
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.projectExists", return_value=False
    )
    def test_process_view_clone_project_view_stage_1_success(self, mock_project_exists):
        self.view.request.params = {
            "stage": "1",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        self.view.request.POST = {"slt_project_by_owner": "test_user___CLIMMOB"}
        self.view.request.route_url = MagicMock(
            return_value="/cloneProject?stage=2&project=my_project&user=test_user"
        )
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location, "/cloneProject?stage=2&project=my_project&user=test_user"
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getUserProjects",
        return_value={"data": "data"},
    )
    @patch("climmob.views.cloneProjects.cloneProjects.getActiveProject", return_value=1)
    @patch(
        "climmob.views.cloneProjects.cloneProjects.projectExists", return_value=False
    )
    def test_process_view_clone_project_view_stage_1_error(
        self, mock_project_exists, mock_get_active_project, mock_get_user_projects
    ):
        self.view.request.params = {
            "stage": "1",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        self.view.request.method = "GET"

        self.view.request.route_url = MagicMock(
            return_value="/cloneProject?stage=2&project=CLIMMOB&user=test_user"
        )
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": 1,
                "dataworking": {
                    "structureToBeCloned": "",
                    "slt_project_by_owner": "test_user___CLIMMOB",
                },
                "projects": {"data": "data"},
                "stage": 1,
            },
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )
        mock_get_active_project.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_user_projects.assert_called_once_with(
            self.view.user.login, self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getUserProjects",
        return_value={"data1": "data1"},
    )
    @patch("climmob.views.cloneProjects.cloneProjects.getActiveProject", return_value=1)
    @patch(
        "climmob.views.cloneProjects.cloneProjects.get_all_information_for_project",
        return_value={"data": "data"},
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.cloneProjects.cloneProjects.projectExists", return_value=True)
    def test_process_view_clone_project_view_stage_2_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_all_information_for_project,
        mock_get_active_project,
        mock_get_user_projects,
    ):
        self.view.request.params = {
            "stage": "2",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": 1,
                "dataworking": {
                    "structureToBeCloned": "",
                    "slt_project_by_owner": "test_user___CLIMMOB",
                    "projectBeingCloned": {"data": "data"},
                },
                "projects": {"data1": "data1"},
                "stage": 2,
            },
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "CLIMMOB", self.view.request
        )
        mock_get_all_information_for_project.assert_called_once_with(
            self.view, "test_user", 1
        )
        mock_get_active_project.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_user_projects.assert_called_once_with(
            self.view.user.login, self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.function_create_clone",
        return_value="",
    )
    @patch("climmob.views.cloneProjects.cloneProjects.create_project_function")
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.cloneProjects.cloneProjects.projectExists", return_value=True)
    def test_process_view_clone_project_view_stage_3_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_create_project_function,
        mock_function_create_clone,
    ):
        self.view.request.params = {
            "stage": "3",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "CLIMMOB",
            "structureToBeCloned": "SOME_VALUE,OTHER_VALUE",
        }
        mock_create_project_function.return_value = (
            {"project_cod": "CLIMMOB", "structureToBeCloned": "SOME_VALUE,OTHER_VALUE"},
            {},
            True,
        )
        self.view.request.route_url = MagicMock(
            return_value="/cloneProject?stage=4&project=CLIMMOB&user=test_user"
        )
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(
            result.location, "/cloneProject?stage=4&project=CLIMMOB&user=test_user"
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "test_user", "CLIMMOB", self.view.request
        )
        mock_create_project_function.assert_called_once_with(ANY, {}, self.view)
        mock_function_create_clone.assert_called_once_with(
            self.view, 1, 1, ["SOME_VALUE", "OTHER_VALUE"]
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.get_all_affiliations",
        return_value="AFFILIATION",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.get_all_objectives_by_location_and_unit_of_analysis",
        return_value="ALL_OBJECTIVES_BY_LOCATION_AND_UNIT_OF_ANALYSIS",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.get_all_unit_of_analysis_by_location",
        return_value="ALL_UNIT_OF_ANALYSIS_BY_LOCATION",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.get_all_project_location",
        return_value="ALL_PROJECT_LOCATION",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getListOfLanguagesByUser",
        return_value="LIST_OF_LANGUAGES_BY_USER",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getProjectAssessments",
        return_value="PROJECT_ASSESSMENTS",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getCountryList",
        return_value="COUNTRY_LIST",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getUserProjects",
        return_value="USER_PROJECTS",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getActiveProject",
        return_value="ACTIVE_PROJECT",
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.cloneProjects.cloneProjects.projectExists", return_value=True)
    def test_process_view_clone_project_view_stage_3_error(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_active_project,
        mock_get_user_projects,
        mock_get_country_list,
        mock_get_project_assessments,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
    ):
        self.view.request.params = {
            "stage": "3",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        self.view.request.POST = {
            "project_cod": "CLIMMOB",
            "structureToBeCloned": "SOME_VALUE,OTHER_VALUE",
            "project_location": "CLIMMOB_LOCATION",
            "project_unit_of_analysis": "5",
        }
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": "ACTIVE_PROJECT",
                "dataworking": {
                    "project_cod": "CLIMMOB",
                    "structureToBeCloned": "SOME_VALUE,OTHER_VALUE",
                    "project_location": "CLIMMOB_LOCATION",
                    "project_unit_of_analysis": "5",
                    "project_numobs": 0,
                    "project_numcom": 3,
                    "project_regstatus": 0,
                    "project_registration_and_analysis": 0,
                },
                "projects": "USER_PROJECTS",
                "countries": "COUNTRY_LIST",
                "assessments": "PROJECT_ASSESSMENTS",
                "showForm": False,
                "error_summary": {},
                "stage": 3,
                "listOfLanguages": "LIST_OF_LANGUAGES_BY_USER",
                "listOfLocations": "ALL_PROJECT_LOCATION",
                "listOfUnitOfAnalysis": "ALL_UNIT_OF_ANALYSIS_BY_LOCATION",
                "listOfObjectives": "ALL_OBJECTIVES_BY_LOCATION_AND_UNIT_OF_ANALYSIS",
                "list_of_affiliation": "AFFILIATION",
            },
        )
        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            "test_user", "CLIMMOB", self.view.request
        )
        mock_get_active_project.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_user_projects.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_country_list.assert_called_once_with(self.view.request)
        mock_get_project_assessments.assert_called_once_with(1, self.view.request)
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, self.view.user.login
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "CLIMMOB_LOCATION"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "CLIMMOB_LOCATION", "5"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.cloneProjects.cloneProjects.projectExists", return_value=True)
    def test_process_view_clone_project_view_stage_4_no_data_cloned(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
    ):
        self.view.request.params = {
            "stage": "4",
            "project": "CLIMMOB",
            "user": "test_user",
        }
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)

        mock_project_exists.assert_called_once_with(
            self.view.user.login, "test_user", "CLIMMOB", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "CLIMMOB", self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getTheProjectIdForOwner",
        return_value=1,
    )
    @patch("climmob.views.cloneProjects.cloneProjects.projectExists")
    def test_process_view_clone_project_view_stage_4_no_project_exist(
        self, mock_project_exists, mock_get_the_project_id_for_owner
    ):
        self.view.request.params = {
            "stage": "4",
            "project": "CLIMMOB",
            "user": "test_user",
            "cloned": "CLIMMOB_CLONED",
        }
        mock_project_exists.side_effect = [True, False]

        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)
        mock_project_exists.assert_has_calls(
            [
                call(self.view.user.login, "test_user", "CLIMMOB", self.view.request),
                call(
                    self.view.user.login,
                    "test_user",
                    "CLIMMOB_CLONED",
                    self.view.request,
                ),
            ]
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "CLIMMOB", self.view.request
        )

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getActiveProject",
        return_value={"data2": "data2"},
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.get_all_information_for_project",
    )
    @patch("climmob.views.cloneProjects.cloneProjects.getTheProjectIdForOwner")
    @patch("climmob.views.cloneProjects.cloneProjects.projectExists")
    def test_process_view_clone_project_view_stage_4_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_all_information_for_project,
        mock_get_active_project,
    ):
        self.view.request.params = {
            "stage": "4",
            "project": "CLIMMOB",
            "user": "test_user",
            "cloned": "CLIMMOB_CLONED",
        }
        mock_get_all_information_for_project.side_effect = [
            {"data": "data"},
            {"data1": "data1"},
        ]
        mock_get_the_project_id_for_owner.side_effect = [1, 2]
        mock_project_exists.side_effect = [True, True]

        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": {"data2": "data2"},
                "dataworking": {
                    "structureToBeCloned": "",
                    "slt_project_by_owner": "test_user___CLIMMOB",
                    "project_cod": "CLIMMOB_CLONED",
                    "userInSetion": "test_user",
                    "clonedProject": {"data": "data"},
                    "projectBeingCloned": {"data1": "data1"},
                },
                "stage": 4,
            },
        )
        mock_project_exists.assert_has_calls(
            [
                call("test_user", "test_user", "CLIMMOB", self.view.request),
                call("test_user", "test_user", "CLIMMOB_CLONED", self.view.request),
            ]
        )
        mock_get_the_project_id_for_owner.assert_has_calls(
            [
                call("test_user", "CLIMMOB", self.view.request),
                call(self.view.user.login, "CLIMMOB_CLONED", self.view.request),
            ]
        )
        mock_get_active_project.assert_called_once_with(
            self.view.user.login, self.view.request
        )


class TestGetAllInformationForProject(unittest.TestCase):
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getProjectAssessments",
        return_value=[{"ass_cod": 1}, {"ass_cod": 2}],
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getDataFormPreview",
        return_value=({"data": "DATA_7"}, "DATA_8"),
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getPrjLangDefaultInProject",
        return_value={"lang_code": "en"},
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.AliasExtraSearchTechnologyInProject"
    )
    @patch("climmob.views.cloneProjects.cloneProjects.AliasSearchTechnologyInProject")
    @patch("climmob.views.cloneProjects.cloneProjects.searchTechnologiesInProject")
    @patch("climmob.views.cloneProjects.cloneProjects.getProjectEnumerators")
    @patch("climmob.views.cloneProjects.cloneProjects.getProjectData")
    def test_get_all_information_for_project_success(
        self,
        mock_get_project_data,
        mock_get_project_enumerators,
        mock_search_technologies_in_project,
        mock_alias_search_technologies_in_project,
        mock_alias_extra_search_technology_in_project,
        mock_get_proj_lang_default_in_project,
        mock_get_data_form_preview,
        mock_get_project_assessments,
    ):
        userOwner = "test_user"
        projectId = 1
        fake_self = MagicMock()
        fake_self.request = MagicMock()

        mock_get_project_data.return_value = {
            "project_registration_and_analysis": "DATA"
        }
        mock_get_project_enumerators.return_value = {"project_enumerators": "DATA_1"}
        mock_search_technologies_in_project.return_value = [
            {"tech_id": 1, "tech1": "TECH1"},
            {"tech_id": 2, "tech1": "TECH2"},
        ]
        mock_alias_search_technologies_in_project.side_effect = ["DATA_3", "DATA_4"]
        mock_alias_extra_search_technology_in_project.side_effect = ["DATA_5", "DATA_6"]

        result = get_all_information_for_project(fake_self, userOwner, projectId)
        self.assertEqual(
            {
                "project_registration_and_analysis": "DATA",
                "project_fieldagents": {"project_enumerators": "DATA_1"},
                "project_techs": [
                    {
                        "tech_id": 1,
                        "tech1": "TECH1",
                        "alias": "DATA_3",
                        "aliasExtra": "DATA_5",
                    },
                    {
                        "tech_id": 2,
                        "tech1": "TECH2",
                        "alias": "DATA_4",
                        "aliasExtra": "DATA_6",
                    },
                ],
                "project_registry": {"data": "DATA_7"},
                "project_assessment": [
                    {"ass_cod": 1, "Questions": {"data": "DATA_7"}},
                    {"ass_cod": 2, "Questions": {"data": "DATA_7"}},
                ],
            },
            result,
        )
        mock_get_project_data.assert_called_once_with(projectId, fake_self.request)
        mock_get_project_enumerators.assert_called_once_with(
            projectId, fake_self.request
        )
        mock_search_technologies_in_project.assert_called_once_with(
            projectId, fake_self.request
        )
        mock_alias_search_technologies_in_project.assert_called_with(
            2, projectId, fake_self.request
        )
        mock_alias_extra_search_technology_in_project.assert_has_calls(
            [call(1, 1, fake_self.request), call(2, 1, fake_self.request)]
        )
        mock_get_proj_lang_default_in_project.assert_called_once_with(
            projectId, fake_self.request
        )
        mock_get_data_form_preview.assert_called_with(
            fake_self, "test_user", 1, assessmentid=2, language="en"
        )
        mock_get_project_assessments.assert_called_once_with(1, fake_self.request)

    @patch(
        "climmob.views.cloneProjects.cloneProjects.getProjectAssessments",
        return_value=[{"ass_cod": 1}, {"ass_cod": 2}],
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getDataFormPreview",
        return_value=({"data": "DATA_7"}, "DATA_8"),
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.getPrjLangDefaultInProject",
        return_value={},
    )
    @patch(
        "climmob.views.cloneProjects.cloneProjects.AliasExtraSearchTechnologyInProject"
    )
    @patch("climmob.views.cloneProjects.cloneProjects.AliasSearchTechnologyInProject")
    @patch("climmob.views.cloneProjects.cloneProjects.searchTechnologiesInProject")
    @patch("climmob.views.cloneProjects.cloneProjects.getProjectEnumerators")
    @patch("climmob.views.cloneProjects.cloneProjects.getProjectData")
    def test_get_all_information_for_project_success_2(
        self,
        mock_get_project_data,
        mock_get_project_enumerators,
        mock_search_technologies_in_project,
        mock_alias_search_technologies_in_project,
        mock_alias_extra_search_technology_in_project,
        mock_get_proj_lang_default_in_project,
        mock_get_data_form_preview,
        mock_get_project_assessments,
    ):
        userOwner = "test_user"
        projectId = 1
        fake_self = MagicMock()
        fake_self.request = MagicMock()
        fake_self.request.locale_name = "en"

        mock_get_project_data.return_value = {
            "project_registration_and_analysis": "DATA"
        }
        mock_get_project_enumerators.return_value = {"project_enumerators": "DATA_1"}
        mock_search_technologies_in_project.return_value = [
            {"tech_id": 1, "tech1": "TECH1"},
            {"tech_id": 2, "tech1": "TECH2"},
        ]
        mock_alias_search_technologies_in_project.side_effect = ["DATA_3", "DATA_4"]
        mock_alias_extra_search_technology_in_project.side_effect = ["DATA_5", "DATA_6"]

        result = get_all_information_for_project(fake_self, userOwner, projectId)
        self.assertEqual(
            {
                "project_registration_and_analysis": "DATA",
                "project_fieldagents": {"project_enumerators": "DATA_1"},
                "project_techs": [
                    {
                        "tech_id": 1,
                        "tech1": "TECH1",
                        "alias": "DATA_3",
                        "aliasExtra": "DATA_5",
                    },
                    {
                        "tech_id": 2,
                        "tech1": "TECH2",
                        "alias": "DATA_4",
                        "aliasExtra": "DATA_6",
                    },
                ],
                "project_registry": {"data": "DATA_7"},
                "project_assessment": [
                    {"ass_cod": 1, "Questions": {"data": "DATA_7"}},
                    {"ass_cod": 2, "Questions": {"data": "DATA_7"}},
                ],
            },
            result,
        )
        mock_get_project_data.assert_called_once_with(projectId, fake_self.request)
        mock_get_project_enumerators.assert_called_once_with(
            projectId, fake_self.request
        )
        mock_search_technologies_in_project.assert_called_once_with(
            projectId, fake_self.request
        )
        mock_alias_search_technologies_in_project.assert_called_with(
            2, projectId, fake_self.request
        )
        mock_alias_extra_search_technology_in_project.assert_has_calls(
            [call(1, 1, fake_self.request), call(2, 1, fake_self.request)]
        )
        mock_get_proj_lang_default_in_project.assert_called_once_with(
            projectId, fake_self.request
        )
        mock_get_data_form_preview.assert_called_with(
            fake_self, "test_user", 1, assessmentid=2, language="en"
        )
        mock_get_project_assessments.assert_called_once_with(1, fake_self.request)


if __name__ == "__main__":
    unittest.main()
