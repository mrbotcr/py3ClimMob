import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch, ANY, call

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.project import (
    GetUnitOfAnalysisByLocationView,
    GetObjectivesByLocationAndUnitOfAnalysisView,
    NewProjectView,
    ModifyProjectView,
    GetTemplatesByTypeOfProjectView,
    ProjectListView,
    DeleteProjectView,
    FinishProjectView,
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


class TestNewProjectView(ViewBaseTest):
    view_class = NewProjectView
    request_method = "POST"

    def setup(self):
        super().setUp()
        self.view.request.registry.settings = {"projects.limit": "false"}
        self.view.request.POST = {
            "submit": "1",
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
        }

    @patch("climmob.views.project.getTotalNumberOfProjectsInClimMob", return_value=0)
    def test_process_view_new_project_view_project_limits_true(
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

    @patch(
        "climmob.views.project.get_all_affiliations", return_value="LIST_AFFILIATIONS"
    )
    @patch(
        "climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis",
        return_value="OBJECTIVES_AND_UNIT_OF_ANALYSIS",
    )
    @patch(
        "climmob.views.project.get_all_unit_of_analysis_by_location",
        return_value="UNIT_OF_ANALYSIS",
    )
    @patch(
        "climmob.views.project.get_all_project_location",
        return_value="PROJECT_LOCATION",
    )
    @patch(
        "climmob.views.project.getListOfLanguagesByUser",
        return_value="LIST_OF_LANGUAGES",
    )
    @patch(
        "climmob.views.project.getProjectTemplates", return_value="PROJECT_TEMPLATES"
    )
    @patch("climmob.views.project.getActiveProject", return_value="ACTIVE_PROJECT_INFO")
    @patch(
        "climmob.views.project.create_project_function",
        return_value=(
            {},
            "This project does not comply with the limitations on the number of participants per project.",
            False,
        ),
    )
    def test_process_view_new_project_view_post_no_added(
        self,
        mock_create_project_function,
        mock_get_active_project,
        mock_get_project_templates,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
    ):
        self.view.user.fullName = ("SOME_VALUE",)
        self.view.user.email = ("CLIMMOB@EXAMPLE.COM",)
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": "ACTIVE_PROJECT_INFO",
                "indashboard": True,
                "dataworking": {
                    "project_cod": "",
                    "project_name": "",
                    "project_abstract": "",
                    "project_tags": "",
                    "project_pi": ("SOME_VALUE",),
                    "project_piemail": ("CLIMMOB@EXAMPLE.COM",),
                    "project_numobs": 0,
                    "project_numcom": 3,
                    "project_regstatus": 0,
                    "project_localvariety": "on",
                    "project_cnty": None,
                    "project_registration_and_analysis": 0,
                    "project_label_a": "Option A",
                    "project_label_b": "Option B",
                    "project_label_c": "Option C",
                    "project_template": 0,
                    "usingTemplate": "",
                    "project_location": "-1",
                    "project_unit_of_analysis": "-1",
                },
                "newproject": False,
                "countries": [],
                "error_summary": {},
                "listOfTemplates": "PROJECT_TEMPLATES",
                "listOfLanguages": "LIST_OF_LANGUAGES",
                "listOfLocations": "PROJECT_LOCATION",
                "listOfUnitOfAnalysis": "UNIT_OF_ANALYSIS",
                "listOfObjectives": "OBJECTIVES_AND_UNIT_OF_ANALYSIS",
                "list_of_affiliation": "LIST_AFFILIATIONS",
                "sectionActive": "addproject",
            },
        )
        mock_get_active_project.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_project_templates.assert_called_once_with(self.view.request, 0)
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, self.view.user.login
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "-1"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "-1", "-1"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch("climmob.views.project.create_project_function")
    def test_process_view_new_project_view_post_success(
        self, mock_create_project_function, mock_p_plugin_implementations
    ):
        self.view.request.POST = {
            "submit": "1",
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_numobs": 1,
        }
        mock_create_project_function.return_value = (
            {"project_cod": "VALUE123"},
            {},
            True,
        )
        plugin_mock1 = MagicMock()
        plugin_mock2 = MagicMock()
        mock_p_plugin_implementations.return_value = [plugin_mock1, plugin_mock2]

        self.view.user.fullName = "SOME_VALUE"
        self.view.user.email = "CLIMMOB@EXAMPLE.COM"
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        plugin_mock1.after_adding_project.assert_called_once_with(
            self.view.request, "test_user", {"project_cod": "VALUE123"}
        )
        plugin_mock2.after_adding_project.assert_called_once_with(
            self.view.request, "test_user", {"project_cod": "VALUE123"}
        )


class TestModifyProjectView(ViewBaseTest):
    view_class = ModifyProjectView
    request_method = "POST"

    def setUp(self):
        super().setUp()

        self.view = ModifyProjectView(self.view.request)
        self.view.request.matchdict = {"user": "testuser", "project": "testproject"}
        self.view.user = MagicMock()
        self.view.user.login = "testuser"
        self.view.user.email = "testuser@example.com"
        self.view.user.fullName = "COMPLETE_TEST_USER"
        self.view.request.registry.settings = {
            "projects.limit": "false",
            "project.maximumnumberofobservations": "100",
        }

    @patch("climmob.views.project.function_create_clone", return_value=1)
    @patch(
        "climmob.views.project.getProjectAssessments",
        return_value=[
            {"ass_cod": "assessment1"},
            {"ass_cod": "assessment2"},
        ],
    )
    @patch("climmob.views.project.deleteProjectAssessments", return_value=(True, ""))
    @patch("climmob.views.project.deleteRegistryByProjectId", return_value=(True, ""))
    @patch("climmob.views.project.addPrjLang", return_value=(True, ""))
    @patch("climmob.views.project.deleteAllPrjLang", return_value=(True, ""))
    @patch(
        "climmob.views.project.add_project_location_unit_objective",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.project.get_location_unit_of_analysis_objectives_by_combination"
    )
    @patch(
        "climmob.views.project.delete_all_project_location_unit_objective",
        return_value=(True, ""),
    )
    @patch("climmob.views.project.modifyProject", return_value=(True, ""))
    @patch("climmob.views.project.get_location_unit_of_analysis_by_combination")
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_location_unit_of_analysis_by_combination,
        mock_modify_project,
        mock_delete_all_project_location_unit_objective,
        mock_get_location_unit_of_analysis_objectives_by_combination,
        mock_add_project_location_unit_objective,
        mock_delete_all_frj_lang,
        mock_add_prj_lang,
        mock_delete_registry_by_project_id,
        mock_delete_project_assessments,
        mock_get_project_assessments,
        mock_function_create_clone,
    ):
        mock_plugin = MagicMock()
        mock_plugin.before_updating_project.return_value = (True, "", "data")
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL_A",
            "project_label_b": "PROJECT_LABEL_B",
            "project_label_c": "PROJECT_LABEL_C",
            "project_numobs": "20",
            "project_numcom": "20",
            "project_localvariety": 1,
            "project_type": "on",
            "project_template": "on",
            "usingTemplate": "template1",
            "project_languages": ["en", "es"],
            "project_objectives": ["obj1"],
        }
        mock_get_project_data.return_value = {
            "project_localvariety": 1,
            "project_regstatus": 0,
            "project_numobs": 3,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": ["obj1"],
            "project_languages": ["en"],
        }
        self.view.getPostDict = MagicMock(
            return_value={
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
                "project_label_a": "PROJECT_LABEL_A",
                "project_label_b": "PROJECT_LABEL_B",
                "project_label_c": "PROJECT_LABEL_C",
                "project_numobs": "20",
                "project_numcom": "20",
                "project_localvariety": "1",
                "project_type": "on",
                "project_template": "on",
                "usingTemplate": "template1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
            }
        )

        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 2,
            "plocation_id": 1,
            "puoa_id": 2,
            "registration_and_analysis": 12,
        }

        mock_get_location_unit_of_analysis_objectives_by_combination.return_value = {
            "pluoaobj_id": 2,
            "pluoa_id": 2,
            "pobjective_id": 1,
        }
        result = self.view.processView()

        self.assertIsInstance(result, HTTPFound)
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, "testproject", self.view.request
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_modify_project.assert_called_once()
        mock_modify_project.assert_called_with(1, ANY, self.view.request)
        mock_delete_all_project_location_unit_objective.assert_called_once_with(
            1, self.view.request
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called()
        mock_add_project_location_unit_objective.assert_called()
        mock_delete_all_frj_lang.assert_called_once_with(1, self.view.request)
        mock_add_prj_lang.assert_called()
        mock_delete_registry_by_project_id.assert_called()
        mock_delete_project_assessments.assert_called()
        mock_get_project_assessments.assert_called()
        mock_function_create_clone.assert_called_once()

    @patch("climmob.views.project.p.PluginImplementations")
    @patch(
        "climmob.views.project.get_all_affiliations",
        return_value={"DATA_ALL_AFFILIATIONS": "DATA_7"},
    )
    @patch(
        "climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis",
        return_value={"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
    )
    @patch(
        "climmob.views.project.get_all_unit_of_analysis_by_location",
        return_value={"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.get_all_project_location",
        return_value={"DATA_ALL_PROJECT_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.getListOfLanguagesByUser",
        return_value={"DATA_LIST_LANG_BT_USER": {"DATA_4_A", "DATA_4_B"}},
    )
    @patch(
        "climmob.views.project.getProjectTemplates",
        return_value={"DATA_TEMPLATES": "DATA_3"},
    )
    @patch(
        "climmob.views.project.getCountryList", return_value=["DATA_2_A", "DATA_2_B"]
    )
    @patch(
        "climmob.views.project.getActiveProject",
        return_value={"DATA_ACTIVE_PROJECT": "DATA_1"},
    )
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_proj_no_comply_limitation(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_active_project,
        mock_get_country_list,
        mock_get_project_templates,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
        mock_plugin_implementations,
    ):
        mock_get_project_data.return_value = {
            "project_regstatus": 0,
            "project_numobs": 300,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": ["obj1"],
            "project_languages": ["en"],
            "project_localvariety": "2",
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL_A",
            "project_label_b": "PROJECT_LABEL_B",
            "project_label_c": "PROJECT_LABEL_C",
            "project_numobs": "300",
            "project_numcom": "20",
            "project_type": "off",
            "usingTemplate": "template1",
            "project_languages": ["en", "es"],
            "project_objectives": ["obj1"],
        }
        self.view.request.registry.settings = {
            "projects.limit": "true",
            "project.maximumnumberofobservations": "100",
        }
        plugin1 = MagicMock()
        plugin2 = MagicMock()

        plugin1.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin1": True,
        }
        plugin2.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin2": "ok",
        }
        mock_plugin_implementations.return_value = [plugin1, plugin2]

        self.view._ = MagicMock(
            return_value="This project does not comply with the limitations on the number of participants per project."
        )

        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "activeProject": {"DATA_ACTIVE_PROJECT": "DATA_1"},
                "indashboard": True,
                "data": {
                    "btn_addNewProject": "1",
                    "project_cod": "testproject",
                    "project_registration_and_analysis": "1",
                    "project_location": "CLIMMOB",
                    "project_unit_of_analysis": "1",
                    "project_label_a": "PROJECT_LABEL_A",
                    "project_label_b": "PROJECT_LABEL_B",
                    "project_label_c": "PROJECT_LABEL_C",
                    "project_numobs": "300",
                    "project_numcom": "20",
                    "project_type": 1,
                    "usingTemplate": "template1",
                    "project_languages": ["en", "es"],
                    "project_objectives": ["obj1"],
                    "project_template": 0,
                    "project_regstatus": 0,
                },
                "newproject": False,
                "countries": ["DATA_2_A", "DATA_2_B"],
                "error_summary": {
                    "projectslimits": "This project does not comply with the limitations on the number of participants per project."
                },
                "listOfTemplates": {"DATA_TEMPLATES": "DATA_3"},
                "listOfLanguages": {"DATA_LIST_LANG_BT_USER": {"DATA_4_B", "DATA_4_A"}},
                "listOfLocations": {"DATA_ALL_PROJECT_LOC": "DATA_5"},
                "listOfUnitOfAnalysis": {"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
                "listOfObjectives": {"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
                "list_of_affiliation": {"DATA_ALL_AFFILIATIONS": "DATA_7"},
                "plugin1": True,
                "plugin2": "ok",
            },
        )
        plugin1.before_returning_project_context.assert_called_once_with(
            self.view.request,
            {
                "activeProject": {"DATA_ACTIVE_PROJECT": "DATA_1"},
                "indashboard": True,
                "data": {
                    "btn_addNewProject": "1",
                    "project_cod": "testproject",
                    "project_registration_and_analysis": "1",
                    "project_location": "CLIMMOB",
                    "project_unit_of_analysis": "1",
                    "project_label_a": "PROJECT_LABEL_A",
                    "project_label_b": "PROJECT_LABEL_B",
                    "project_label_c": "PROJECT_LABEL_C",
                    "project_numobs": "300",
                    "project_numcom": "20",
                    "project_type": 1,
                    "usingTemplate": "template1",
                    "project_languages": ["en", "es"],
                    "project_objectives": ["obj1"],
                    "project_template": 0,
                    "project_regstatus": 0,
                },
                "newproject": False,
                "countries": ["DATA_2_A", "DATA_2_B"],
                "error_summary": {
                    "projectslimits": "This project does not comply with the limitations on the number of participants per project."
                },
                "listOfTemplates": {"DATA_TEMPLATES": "DATA_3"},
                "listOfLanguages": {"DATA_LIST_LANG_BT_USER": {"DATA_4_B", "DATA_4_A"}},
                "listOfLocations": {"DATA_ALL_PROJECT_LOC": "DATA_5"},
                "listOfUnitOfAnalysis": {"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
                "listOfObjectives": {"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
                "list_of_affiliation": {"DATA_ALL_AFFILIATIONS": "DATA_7"},
            },
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, "testproject", self.view.request
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_active_project.assert_called_once_with("testuser", self.view.request)
        mock_get_country_list.assert_called_once_with(self.view.request)
        mock_get_project_templates.assert_called_once_with(self.view.request, "1")
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, "testuser"
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "CLIMMOB"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch(
        "climmob.views.project.get_all_affiliations",
        return_value={"DATA_ALL_AFFILIATIONS": "DATA_7"},
    )
    @patch(
        "climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis",
        return_value={"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
    )
    @patch(
        "climmob.views.project.get_all_unit_of_analysis_by_location",
        return_value={"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.get_all_project_location",
        return_value={"DATA_ALL_PROJECT_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.getListOfLanguagesByUser",
        return_value={"DATA_LIST_LANG_BT_USER": {"DATA_4_A", "DATA_4_B"}},
    )
    @patch(
        "climmob.views.project.getProjectTemplates",
        return_value={"DATA_TEMPLATES": "DATA_3"},
    )
    @patch(
        "climmob.views.project.getCountryList", return_value=["DATA_2_A", "DATA_2_B"]
    )
    @patch(
        "climmob.views.project.getActiveProject",
        return_value={"DATA_ACTIVE_PROJECT": "DATA_1"},
    )
    @patch(
        "climmob.views.project.modifyProject", return_value=(False, "Error to modify")
    )
    @patch("climmob.views.project.get_location_unit_of_analysis_by_combination")
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_proj_error_to_modify(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_location_unit_of_analysis_by_combination,
        mock_modify_project,
        mock_get_active_project,
        mock_get_country_list,
        mock_get_project_templates,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
        mock_plugin_implementations,
    ):
        mock_get_project_data.return_value = {
            "project_regstatus": 1,
            "project_numobs": 300,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": ["obj1"],
            "project_languages": ["en"],
            "project_localvariety": 1,
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL_A",
            "project_label_b": "PROJECT_LABEL_B",
            "project_label_c": "PROJECT_LABEL_C",
            "project_numobs": "30",
            "project_numcom": "20",
            "project_type": "off",
            "usingTemplate": "template1",
            "project_languages": ["en", "es"],
            "project_objectives": ["obj1"],
            "project_template": "off",
            "project_localvariety": "1",
        }
        self.view.request.registry.settings = {
            "projects.limit": "true",
            "project.maximumnumberofobservations": "100",
        }
        plugin1 = MagicMock()
        plugin2 = MagicMock()

        plugin1.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin1": True,
        }
        plugin2.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin2": "ok",
        }
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "0",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        plugin2.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "0",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        self.view._ = MagicMock(
            return_value="This project does not comply with the limitations on the number of participants per project."
        )

        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 2,
            "plocation_id": 1,
            "puoa_id": 2,
            "registration_and_analysis": 1,
        }
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": {"DATA_ACTIVE_PROJECT": "DATA_1"},
                "indashboard": True,
                "data": {
                    "project_localvariety": "off",
                    "project_cod": "VALUE123",
                    "project_registration_and_analysis": 1,
                    "project_languages": ["en", "es"],
                    "project_objectives": ["obj1"],
                    "project_location": "CLIMMOB",
                    "project_unit_of_analysis": "1",
                },
                "newproject": False,
                "countries": ["DATA_2_A", "DATA_2_B"],
                "error_summary": {"dberror": "Error to modify"},
                "listOfTemplates": {"DATA_TEMPLATES": "DATA_3"},
                "listOfLanguages": {"DATA_LIST_LANG_BT_USER": {"DATA_4_B", "DATA_4_A"}},
                "listOfLocations": {"DATA_ALL_PROJECT_LOC": "DATA_5"},
                "listOfUnitOfAnalysis": {"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
                "listOfObjectives": {"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
                "list_of_affiliation": {"DATA_ALL_AFFILIATIONS": "DATA_7"},
                "plugin1": True,
                "plugin2": "ok",
            },
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, "testproject", self.view.request
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_modify_project.assert_called_once_with(
            1,
            {
                "project_localvariety": "off",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": 1,
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
            self.view.request,
        )
        mock_get_active_project.assert_called_once_with("testuser", self.view.request)
        mock_get_country_list.assert_called_once_with(self.view.request)
        mock_get_project_templates.assert_called_once_with(self.view.request, 1)
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, "testuser"
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "CLIMMOB"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch(
        "climmob.views.project.get_all_affiliations",
        return_value={"DATA_ALL_AFFILIATIONS": "DATA_7"},
    )
    @patch(
        "climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis",
        return_value={"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
    )
    @patch(
        "climmob.views.project.get_all_unit_of_analysis_by_location",
        return_value={"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.get_all_project_location",
        return_value={"DATA_ALL_PROJECT_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.getListOfLanguagesByUser",
        return_value={"DATA_LIST_LANG_BT_USER": {"DATA_4_A", "DATA_4_B"}},
    )
    @patch(
        "climmob.views.project.getProjectTemplates",
        return_value={"DATA_TEMPLATES": "DATA_3"},
    )
    @patch(
        "climmob.views.project.getCountryList", return_value=["DATA_2_A", "DATA_2_B"]
    )
    @patch(
        "climmob.views.project.getActiveProject",
        return_value={"DATA_ACTIVE_PROJECT": "DATA_1"},
    )
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_proj_same_question(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_active_project,
        mock_get_country_list,
        mock_get_project_templates,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
        mock_plugin_implementations,
    ):
        mock_get_project_data.return_value = {
            "project_regstatus": 1,
            "project_numobs": 300,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": ["obj1"],
            "project_languages": ["en"],
            "project_localvariety": 1,
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL",
            "project_label_b": "PROJECT_LABEL",
            "project_label_c": "PROJECT_LABEL",
            "project_numobs": "30",
            "project_numcom": "20",
            "project_type": "off",
            "usingTemplate": "template1",
            "project_languages": ["en", "es"],
            "project_objectives": ["obj1"],
            "project_template": "off",
            "project_localvariety": "1",
        }

        self.view._ = MagicMock(
            return_value="The names that the items will receive should be different."
        )

        result = self.view.processView()
        # self.assertEqual(result, {'activeProject': {'DATA_ACTIVE_PROJECT': 'DATA_1'}, 'indashboard': True, 'data': {'project_localvariety': 'on', 'project_cod': 'VALUE123', 'project_registration_and_analysis': 1, 'project_languages': ['en', 'es'], 'project_objectives': ['obj1'], 'project_location': 'CLIMMOB', 'project_unit_of_analysis': '1'}, 'newproject': False, 'countries': ['DATA_2_A', 'DATA_2_B'], 'error_summary': {'dberror': 'Error to modify'}, 'listOfTemplates': {'DATA_TEMPLATES': 'DATA_3'}, 'listOfLanguages': {'DATA_LIST_LANG_BT_USER': {'DATA_4_B', 'DATA_4_A'}}, 'listOfLocations': {'DATA_ALL_PROJECT_LOC': 'DATA_5'}, 'listOfUnitOfAnalysis': {'DATA_ALL_UNIT_ANA_LOC': 'DATA_5'}, 'listOfObjectives': {'DATA_ALL_OBJECT_&_UNIT_OF_ANA': 'DATA_6'}, 'list_of_affiliation': {'DATA_ALL_AFFILIATIONS': 'DATA_7'}, 'plugin1': True, 'plugin2': 'ok'})
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, "testproject", self.view.request
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_active_project.assert_called_once_with("testuser", self.view.request)
        mock_get_country_list.assert_called_once_with(self.view.request)
        mock_get_project_templates.assert_called_once_with(self.view.request, "1")
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, "testuser"
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "CLIMMOB"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch(
        "climmob.views.project.get_all_affiliations",
        return_value={"DATA_ALL_AFFILIATIONS": "DATA_7"},
    )
    @patch(
        "climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis",
        return_value={"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
    )
    @patch(
        "climmob.views.project.get_all_unit_of_analysis_by_location",
        return_value={"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.get_all_project_location",
        return_value={"DATA_ALL_PROJECT_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.getListOfLanguagesByUser",
        return_value={"DATA_LIST_LANG_BT_USER": {"DATA_4_A", "DATA_4_B"}},
    )
    @patch(
        "climmob.views.project.getProjectTemplates",
        return_value={"DATA_TEMPLATES": "DATA_3"},
    )
    @patch(
        "climmob.views.project.getCountryList", return_value=["DATA_2_A", "DATA_2_B"]
    )
    @patch(
        "climmob.views.project.getActiveProject",
        return_value={"DATA_ACTIVE_PROJECT": "DATA_1"},
    )
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_proj_error_in_plugin_to_modify(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_active_project,
        mock_get_country_list,
        mock_get_project_templates,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
        mock_plugin_implementations,
    ):
        mock_get_project_data.return_value = {
            "project_regstatus": 1,
            "project_numobs": 300,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": ["obj1"],
            "project_languages": ["en"],
            "project_localvariety": 1,
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL_A",
            "project_label_b": "PROJECT_LABEL_B",
            "project_label_c": "PROJECT_LABEL_C",
            "project_numobs": "30",
            "project_numcom": "20",
            "project_type": "off",
            "usingTemplate": "template1",
            "project_languages": ["en", "es"],
            "project_objectives": ["obj1"],
            "project_template": "off",
            "project_localvariety": "1",
        }
        self.view.request.registry.settings = {
            "projects.limit": "true",
            "project.maximumnumberofobservations": "100",
        }
        plugin1 = MagicMock()
        plugin2 = MagicMock()

        plugin1.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin1": True,
        }
        plugin2.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin2": "ok",
        }
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        plugin2.before_updating_project.return_value = (
            False,
            "Error to modify",
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": {"DATA_ACTIVE_PROJECT": "DATA_1"},
                "indashboard": True,
                "data": {
                    "project_localvariety": "1",
                    "project_cod": "VALUE123",
                    "project_registration_and_analysis": "1",
                    "project_languages": ["en", "es"],
                    "project_objectives": ["obj1"],
                    "project_location": "CLIMMOB",
                    "project_unit_of_analysis": "1",
                },
                "newproject": False,
                "countries": ["DATA_2_A", "DATA_2_B"],
                "error_summary": {"dberror": "Error to modify"},
                "listOfTemplates": {"DATA_TEMPLATES": "DATA_3"},
                "listOfLanguages": {"DATA_LIST_LANG_BT_USER": {"DATA_4_B", "DATA_4_A"}},
                "listOfLocations": {"DATA_ALL_PROJECT_LOC": "DATA_5"},
                "listOfUnitOfAnalysis": {"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
                "listOfObjectives": {"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
                "list_of_affiliation": {"DATA_ALL_AFFILIATIONS": "DATA_7"},
                "plugin1": True,
                "plugin2": "ok",
            },
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, "testproject", self.view.request
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_active_project.assert_called_once_with("testuser", self.view.request)
        mock_get_country_list.assert_called_once_with(self.view.request)
        mock_get_project_templates.assert_called_once_with(self.view.request, "1")
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, "testuser"
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "CLIMMOB"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch("climmob.views.project.deleteRegistryByProjectId", return_value=(True, ""))
    @patch("climmob.views.project.addPrjLang", return_value=(True, ""))
    @patch("climmob.views.project.deleteAllPrjLang", return_value=(True, ""))
    @patch(
        "climmob.views.project.add_project_location_unit_objective",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.project.get_location_unit_of_analysis_objectives_by_combination",
        return_value={"DATA_ALL_PROJECT_LOC": "DATA_8", "pluoaobj_id": 2},
    )
    @patch(
        "climmob.views.project.delete_all_project_location_unit_objective",
        return_value=(True, ""),
    )
    @patch("climmob.views.project.modifyProject", return_value=(True, ""))
    @patch("climmob.views.project.get_location_unit_of_analysis_by_combination")
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_proj_deleted_by_project(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_location_unit_of_analysis_by_combination,
        mock_modify_project,
        mock_delete_all_project_location_unit_objective,
        mock_get_location_unit_of_analysis_objectives_by_combination,
        mock_add_project_location_unit_objective,
        mock_delete_all_prj_lang,
        mock_add_prj_lang,
        mock_delete_registry_by_project_id,
        mock_plugin_implementations,
    ):
        mock_get_project_data.return_value = {
            "project_regstatus": 1,
            "project_numobs": 300,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": "obj1",
            "project_languages": "es",
            "project_localvariety": 1,
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL_A",
            "project_label_b": "PROJECT_LABEL_B",
            "project_label_c": "PROJECT_LABEL_C",
            "project_numobs": "30",
            "project_numcom": "20",
            "project_type": "off",
            "usingTemplate": "template1",
            "project_languages": "es",
            "project_objectives": "obj1",
            "project_template": "off",
            "project_localvariety": "1",
        }
        self.view.request.registry.settings = {
            "projects.limit": "true",
            "project.maximumnumberofobservations": "100",
        }
        plugin1 = MagicMock()
        plugin2 = MagicMock()
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin1": True,
        }
        plugin2.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin2": "ok",
        }
        plugin1.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": 0,
                "project_languages": "es",
                "project_objectives": "obj1",
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        plugin2.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": 0,
                "project_languages": "es",
                "project_objectives": "obj1",
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )

        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": "2",
            "plocation_id": 1,
            "puoa_id": 2,
            "registration_and_analysis": 0,
        }
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)
        mock_get_the_project_id_for_owner.assert_has_calls(
            [call(self.view.user.login, "testproject", self.view.request)]
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_modify_project.assert_called_once_with(
            1,
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": 0,
                "project_languages": ["es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
            self.view.request,
        )
        mock_delete_all_project_location_unit_objective.assert_called_once_with(
            1, self.view.request
        )
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called_once_with(
            self.view.request, "2", "obj1"
        )
        mock_add_project_location_unit_objective.assert_called_once_with(
            {"project_id": 1, "pluoaobj_id": 2}, self.view.request
        )
        mock_delete_all_prj_lang.assert_called_once_with(1, self.view.request)
        mock_add_prj_lang.assert_called_once_with(
            {"lang_default": 1, "lang_code": "es", "project_id": 1}, self.view.request
        )
        mock_delete_registry_by_project_id.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch(
        "climmob.views.project.get_all_affiliations",
        return_value={"DATA_ALL_AFFILIATIONS": "DATA_7"},
    )
    @patch(
        "climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis",
        return_value={"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
    )
    @patch(
        "climmob.views.project.get_all_unit_of_analysis_by_location",
        return_value={"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.get_all_project_location",
        return_value={"DATA_ALL_PROJECT_LOC": "DATA_5"},
    )
    @patch(
        "climmob.views.project.getListOfLanguagesByUser",
        return_value={"DATA_LIST_LANG_BT_USER": {"DATA_4_A", "DATA_4_B"}},
    )
    @patch(
        "climmob.views.project.getProjectTemplates",
        return_value={"DATA_TEMPLATES": "DATA_3"},
    )
    @patch(
        "climmob.views.project.getCountryList", return_value=["DATA_2_A", "DATA_2_B"]
    )
    @patch(
        "climmob.views.project.getActiveProject",
        return_value={"DATA_ACTIVE_PROJECT": "DATA_1"},
    )
    @patch(
        "climmob.views.project.modifyProject", return_value=(False, "Error to modify")
    )
    @patch("climmob.views.project.get_location_unit_of_analysis_by_combination")
    @patch("climmob.views.project.getProjectData")
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_modify_project_view_proj_error_to_modify2(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_get_location_unit_of_analysis_by_combination,
        mock_modify_project,
        mock_get_active_project,
        mock_get_country_list,
        mock_get_project_templates,
        mock_get_list_of_languages_by_user,
        mock_get_all_project_location,
        mock_get_all_unit_of_analysis_by_location,
        mock_get_all_objectives_by_location_and_unit_of_analysis,
        mock_get_all_affiliations,
        mock_plugin_implementations,
    ):
        mock_get_project_data.return_value = {
            "project_regstatus": 1,
            "project_numobs": 300,
            "project_numcom": 2,
            "project_registration_and_analysis": 1,
            "project_template_used": "",
            "project_cod": "VALUE123",
            "project_objectives": ["obj1"],
            "project_languages": ["en"],
            "project_localvariety": 1,
        }
        self.view.request.POST = {
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": "1",
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_label_a": "PROJECT_LABEL_A",
            "project_label_b": "PROJECT_LABEL_B",
            "project_label_c": "PROJECT_LABEL_C",
            "project_numobs": "30",
            "project_numcom": "20",
            "project_type": "off",
            "usingTemplate": "template1",
            "project_languages": ["en", "es"],
            "project_objectives": ["obj1"],
            "project_template": "off",
            "project_localvariety": "1",
        }
        self.view.request.registry.settings = {
            "projects.limit": "true",
            "project.maximumnumberofobservations": "100",
        }
        plugin1 = MagicMock()
        plugin2 = MagicMock()

        plugin1.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin1": True,
        }
        plugin2.before_returning_project_context.side_effect = lambda req, ctx: {
            **ctx,
            "plugin2": "ok",
        }
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        plugin2.before_updating_project.return_value = (
            True,
            "",
            {
                "project_localvariety": "1",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": "1",
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
        )
        self.view._ = MagicMock(
            return_value="This project does not comply with the limitations on the number of participants per project."
        )

        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id": 2,
            "plocation_id": 1,
            "puoa_id": 2,
            "registration_and_analysis": 0,
        }
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": {"DATA_ACTIVE_PROJECT": "DATA_1"},
                "indashboard": True,
                "data": {
                    "project_localvariety": "on",
                    "project_cod": "VALUE123",
                    "project_registration_and_analysis": 0,
                    "project_languages": ["en", "es"],
                    "project_objectives": ["obj1"],
                    "project_location": "CLIMMOB",
                    "project_unit_of_analysis": "1",
                },
                "newproject": False,
                "countries": ["DATA_2_A", "DATA_2_B"],
                "error_summary": {"dberror": "Error to modify"},
                "listOfTemplates": {"DATA_TEMPLATES": "DATA_3"},
                "listOfLanguages": {"DATA_LIST_LANG_BT_USER": {"DATA_4_B", "DATA_4_A"}},
                "listOfLocations": {"DATA_ALL_PROJECT_LOC": "DATA_5"},
                "listOfUnitOfAnalysis": {"DATA_ALL_UNIT_ANA_LOC": "DATA_5"},
                "listOfObjectives": {"DATA_ALL_OBJECT_&_UNIT_OF_ANA": "DATA_6"},
                "list_of_affiliation": {"DATA_ALL_AFFILIATIONS": "DATA_7"},
                "plugin1": True,
                "plugin2": "ok",
            },
        )
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, "testproject", self.view.request
        )
        mock_get_project_data.asssert_has_calls(
            [call(1, self.view.request), call(1, self.view.request)]
        )
        mock_get_location_unit_of_analysis_by_combination.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_modify_project.assert_called_once_with(
            1,
            {
                "project_localvariety": "on",
                "project_cod": "VALUE123",
                "project_registration_and_analysis": 0,
                "project_languages": ["en", "es"],
                "project_objectives": ["obj1"],
                "project_location": "CLIMMOB",
                "project_unit_of_analysis": "1",
            },
            self.view.request,
        )
        mock_get_active_project.assert_called_once_with("testuser", self.view.request)
        mock_get_country_list.assert_called_once_with(self.view.request)
        mock_get_project_templates.assert_called_once_with(self.view.request, 0)
        mock_get_list_of_languages_by_user.assert_called_once_with(
            self.view.request, "testuser"
        )
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(
            self.view.request, "CLIMMOB"
        )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(
            self.view.request, "CLIMMOB", "1"
        )
        mock_get_all_affiliations.assert_called_once_with(self.view.request)


class TestGetTemplatesByTypeOfProjectView(ViewBaseTest):
    view_class = GetTemplatesByTypeOfProjectView

    @patch("climmob.views.project.getProjectTemplates", return_value={"data": "data"})
    def test_process_view_get_templates_by_type_of_project_view_success(
        self, mock_get_project_templates
    ):
        self.view.request.matchdict = {"typeid": 0}
        result = self.view.processView()
        self.assertEqual(result, {"data": "data"})
        mock_get_project_templates.assert_called_once_with(self.view.request, 0)

    def test_process_view_get_templates_by_type_of_project_view_method_error(self):
        self.view.request.method = "POST"
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)


class TestProjectListView(ViewBaseTest):
    view_class = ProjectListView

    @patch(
        "climmob.views.project.getTotalNumberOfProjectsInClimMob",
        return_value={"data2": "data2"},
    )
    @patch("climmob.views.project.getUserProjects", return_value={"data1": "data1"})
    @patch("climmob.views.project.getActiveProject", return_value={"data": "data"})
    def test_project_list_view_success(
        self,
        mock_get_active_project,
        mock_get_user_projects,
        mock_get_total_projects_in_climmob,
    ):
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeProject": {"data": "data"},
                "numberOfProjects": {"data2": "data2"},
                "sectionActive": "projectlist",
                "userProjects": {"data1": "data1"},
            },
        )
        mock_get_active_project.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_user_projects.assert_called_once_with(
            self.view.user.login, self.view.request
        )
        mock_get_total_projects_in_climmob.assert_called_once_with(self.view.request)


class TestDeleteProjectView(ViewBaseTest):
    view_class = DeleteProjectView
    request_method = "POST"

    @patch("climmob.views.project.getProjectData", return_value={"data": "data"})
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_delete_project_view_method_error(
        self, mock_get_the_project_id_for_owner, mock_get_project_data
    ):
        self.view.request.matchdict = {"user": "TEST_USER", "project": "TEST_PROJECT"}
        self.view.request.method = "GET"
        result = self.view.processView()
        self.assertEqual(
            result,
            {
                "activeUser": self.view.user,
                "redirect": False,
                "data": {"data": "data"},
                "error_summary": {},
            },
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "TEST_USER", "TEST_PROJECT", self.view.request
        )
        mock_get_project_data.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.project.p.PluginImplementations")
    @patch("climmob.views.project.getProjectData", return_value={"data": "data"})
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_delete_project_view_error_to_delete(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_plugin_implementations,
    ):
        self.view.request.matchdict = {"user": "TEST_USER", "project": "TEST_PROJECT"}
        plugin1 = MagicMock()
        plugin2 = MagicMock()
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_deleting_project.return_value = (False, "Error to delete")
        plugin2.before_deleting_project.return_value = (False, "Error to delete")

        result = self.view.processView()
        self.assertEqual(result, {"status": 400, "error": "Error to delete"})
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "TEST_USER", "TEST_PROJECT", self.view.request
        )
        mock_get_project_data.assert_called_once_with(1, self.view.request)

    @patch(
        "climmob.views.project.deleteProject",
        return_value=(False, "Error to delete project"),
    )
    @patch("climmob.views.project.p.PluginImplementations")
    @patch("climmob.views.project.getProjectData", return_value={"data": "data"})
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_delete_project_view_error_to_delete_project(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_plugin_implementations,
        mock_delete_project,
    ):
        self.view.request.matchdict = {"user": "TEST_USER", "project": "TEST_PROJECT"}
        plugin1 = MagicMock()
        plugin2 = MagicMock()
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_deleting_project.return_value = (True, "")
        plugin2.before_deleting_project.return_value = (True, "")

        result = self.view.processView()
        self.assertEqual(result, {"status": 400, "error": "Error to delete project"})
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "TEST_USER", "TEST_PROJECT", self.view.request
        )
        mock_get_project_data.assert_called_once_with(1, self.view.request)
        mock_delete_project.assert_called_once_with(1, self.view.request)

    @patch("climmob.views.project.deleteProject", return_value=(True, ""))
    @patch("climmob.views.project.p.PluginImplementations")
    @patch("climmob.views.project.getProjectData", return_value={"data": "data"})
    @patch("climmob.views.project.getTheProjectIdForOwner", return_value=1)
    def test_process_view_delete_project_view_success(
        self,
        mock_get_the_project_id_for_owner,
        mock_get_project_data,
        mock_plugin_implementations,
        mock_delete_project,
    ):
        self.view.request.matchdict = {"user": "TEST_USER", "project": "TEST_PROJECT"}
        plugin1 = MagicMock()
        plugin2 = MagicMock()
        mock_plugin_implementations.return_value = [plugin1, plugin2]
        plugin1.before_deleting_project.return_value = (True, "")
        plugin2.before_deleting_project.return_value = (True, "")

        plugin1.after_deleting_project.return_value = None
        plugin2.after_deleting_project.return_value = None

        result = self.view.processView()
        self.assertEqual(result, {"status": 200})
        self.view.request.session.flash.assert_called_once_with(
            "The project was deleted successfully"
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "TEST_USER", "TEST_PROJECT", self.view.request
        )
        mock_get_project_data.assert_called_once_with(1, self.view.request)
        mock_delete_project.assert_called_once_with(1, self.view.request)


class TestFinishProjectView(ViewBaseTest):
    view_class = FinishProjectView

    def setUp(self):
        super().setUp()
        self.view.context.active_project_id = 1

        self.view.request.user = "test_user"
        self.view.request.project = "PRJ001"

        self.view.request.registry.settings = {"email.from": "email_send@test.com"}
        fake_now = datetime(2024, 1, 1, 12, 0, 0).strftime("%Y-%m-%d %H:%M:%S")
        self.view.request.translate = lambda text: text

        self.get_project_id_patcher = patch(
            "climmob.views.project.getTheProjectIdForOwner"
        )
        self.set_active_project_patcher = patch(
            "climmob.views.project.setActiveProject"
        )
        self.active_project_patcher = patch("climmob.views.project.getActiveProject")
        self.update_project_status_patcher = patch(
            "climmob.views.project.update_project_status"
        )
        self.get_all_user_admin_patcher = patch("climmob.views.project.getAllUserAdmin")
        self.get_project_progress_patcher = patch(
            "climmob.views.project.getProjectProgress"
        )
        self.render_template_patcher = patch("climmob.views.project.render_template")
        self.datetime_patcher = patch("climmob.views.project.datetime.datetime")
        self.build_email_message_multiple_recipients_patcher = patch(
            "climmob.views.project.build_email_message_multiple_recipients"
        )
        self.email_sender_patcher = patch("climmob.views.project.EmailSender")
        self.log_patcher = patch("climmob.views.project.log")

        self.mock_get_project_id = self.get_project_id_patcher.start()
        self.mock_set_active_project = self.set_active_project_patcher.start()
        self.mock_project_info = self.active_project_patcher.start()
        self.mock_progress = self.get_project_progress_patcher.start()
        self.mock_success = self.update_project_status_patcher.start()
        self.mock_admin_users_patcher = self.get_all_user_admin_patcher.start()
        self.mock_text = self.render_template_patcher.start()
        self.mock_datetime = self.datetime_patcher.start()
        self.mock_msg = self.build_email_message_multiple_recipients_patcher.start()
        self.mock_email_sender = self.email_sender_patcher.start()
        self.mock_email_sender.return_value.send_email.return_value = None

        self.mock_log = self.log_patcher.start()
        self.fake_project_id = MagicMock(name="fake_id")
        self.fake_project_cod = MagicMock(name="fake_cod")
        self.mock_project_info.return_value = {
            "project_id": self.fake_project_id,
            "project_cod": self.fake_project_cod,
        }
        self.mock_get_project_id.return_value = {
            "project_id": self.fake_project_id,
            "project_cod": self.fake_project_cod,
        }

        self.mock_success.return_value = (True, "")
        self.mock_admin_users_patcher.return_value = [
            {"user_fullname": "name1", "user_email": "email1"},
            {"user_fullname": "name2", "user_email": "email2"},
        ]
        self.mock_text.return_value = "rendered email body"
        self.mock_datetime.now.strftime.return_value = fake_now
        self.mock_msg.return_value = "some text to add to the email body"
        self.mock_progress.return_value = {
            "data_progress": "result_data",
            "assessments": [{"ass_status": 1, "asstotal": 1}],
        }, True

        self.view.request.matchdict = {"project": "PRJ001"}

        self.addCleanup(self.get_project_id_patcher.stop)
        self.addCleanup(self.set_active_project_patcher.stop)
        self.addCleanup(self.active_project_patcher.stop)
        self.addCleanup(self.get_project_progress_patcher.stop)
        self.addCleanup(self.update_project_status_patcher.stop)
        self.addCleanup(self.get_all_user_admin_patcher.stop)
        self.addCleanup(self.render_template_patcher.stop)
        self.addCleanup(self.datetime_patcher.stop)
        self.addCleanup(self.build_email_message_multiple_recipients_patcher.stop)
        self.addCleanup(self.email_sender_patcher.stop)
        self.addCleanup(self.mock_log.stop)

    def tearDown(self):
        if self.mock_get_project_id.called:
            self.mock_get_project_id.assert_called_once_with(
                self.view.request.user, "PRJ001", self.view.request
            )

        if self.mock_set_active_project.called:
            self.mock_set_active_project.assert_called_once_with(
                self.view.user.login,
                self.mock_get_project_id.return_value,
                self.view.request,
            )

        if self.mock_project_info.called:
            self.mock_project_info.assert_called_once_with(
                self.view.user.login, self.view.request
            )
        if self.mock_success.called:
            self.mock_success.assert_called_once_with(
                self.view.context.active_project_id, 3, self.view.request
            )
        if self.mock_admin_users_patcher.called:
            self.mock_admin_users_patcher.assert_called_once_with(self.view.request)
        if self.mock_text.called:
            self.mock_text.assert_called_once_with(
                "email/close_project.jinja2",
                {
                    "date": self.mock_datetime.now.return_value.strftime.return_value,
                    "project_info": self.mock_project_info.return_value,
                    "_": self.view.request.translate,
                    "link": self.view.request.route_url("projectsSummaryRecent"),
                    "logo": self.view.request.url_for_static("landing/climmob2.png"),
                },
            )
        if self.mock_msg.called:
            self.mock_msg.assert_called_once_with(
                self.mock_text.return_value,
                "✅  Project "
                + str(self.mock_get_project_id.return_value["project_cod"])
                + " has been finalized",
                [("name1", "email1"), ("name2", "email2")],
                self.view.request.registry.settings["email.from"],
            )
        if self.mock_progress.called:
            self.mock_progress.assert_called_once_with(
                self.view.user.login,
                self.view.request.project,
                self.mock_get_project_id.return_value,
                self.view.request,
            )
        super().tearDown()

    def test_finish_project_view_get(self):
        response = self.view.get()
        self.assertEqual(
            response,
            {
                "project_info": self.mock_get_project_id.return_value,
                "progress": {
                    "data_progress": "result_data",
                    "assessments": [{"ass_status": 1, "asstotal": 1}],
                },
                "total_ass_records": 1,
            },
        )

    @patch.object(FinishProjectView, "send_email_notification", return_value=True)
    def test_finish_project_view_post_success(self, mock_send_email_notification):
        mock_route = self.view.request.route_url("dashboard")
        response = self.view.post()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, mock_route)
        mock_send_email_notification.assert_called_once_with(
            self.mock_project_info.return_value
        )

    def test_finish_project_view_post_fail(self):
        self.mock_success.return_value = (False, "Fake Error")
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "error": self.mock_success.return_value[1],
                "project_info": self.mock_project_info.return_value,
            },
        )

    def test_send_email_success(self):
        response = self.view.send_email_notification(
            self.mock_project_info.return_value
        )
        self.assertEqual(response, True)

    def test_send_email_no_mail_from(self):
        self.view.request.registry.settings = {}
        response = self.view.send_email_notification(
            self.mock_project_info.return_value
        )
        self.assertEqual(response, False)

    def test_send_email_no_admin(self):
        self.mock_admin_users_patcher.return_value = []
        response = self.view.send_email_notification(
            self.mock_project_info.return_value
        )
        self.assertEqual(response, False)

    def test_send_email_template_error(self):
        self.mock_text.side_effect = Exception("template error")
        response = self.view.send_email_notification(
            self.mock_project_info.return_value
        )
        self.assertEqual(response, False)

    def test_send_email_msg_error(self):
        self.mock_msg.side_effect = Exception("msg error")
        response = self.view.send_email_notification(
            self.mock_project_info.return_value
        )
        self.assertEqual(response, False)

    def test_send_email_error(self):
        self.mock_email_sender.side_effect = Exception("server error")
        response = self.view.send_email_notification(
            self.mock_project_info.return_value
        )
        self.assertEqual(response, False)


if __name__ == "__main__":
    unittest.main()
