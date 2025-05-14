import unittest
from unittest.mock import MagicMock, patch, ANY

from formencode.variabledecode import variable_decode
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.views.project import (
    GetUnitOfAnalysisByLocationView,
    GetObjectivesByLocationAndUnitOfAnalysisView,
    NewProjectView,
create_project_function,
ModifyProjectView
)
from climmob.tests.test_utils.common import BaseViewTestCase



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

class TestNewProjectView(BaseViewTestCase):
    view_class = NewProjectView
    request_method = "POST"

    def setup(self):
        super().setUp()
        self.view.request.registry.settings = {"projects.limit": "false"}
        self.view.request.POST = {
            "submit": "1",
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": '1',
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
        }

    @patch("climmob.views.project.getTotalNumberOfProjectsInClimMob", return_value=0)
    def test_process_view_new_project_view_project_limits_true(self, mock_get_total_number_of_projects_in_climmob):
        self.view.request.registry.settings = {"projects.limit": "true", "projects.quantity": 0}
        with self.assertRaises(HTTPNotFound) as context:
            self.view.processView()
        self.assertEqual(context.exception.code, 404)
        mock_get_total_number_of_projects_in_climmob.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.get_all_affiliations", return_value="LIST_AFFILIATIONS")
    @patch("climmob.views.project.get_all_objectives_by_location_and_unit_of_analysis", return_value="OBJECTIVES_AND_UNIT_OF_ANALYSIS")
    @patch("climmob.views.project.get_all_unit_of_analysis_by_location", return_value="UNIT_OF_ANALYSIS")
    @patch("climmob.views.project.get_all_project_location", return_value="PROJECT_LOCATION")
    @patch("climmob.views.project.getListOfLanguagesByUser", return_value="LIST_OF_LANGUAGES")
    @patch("climmob.views.project.getProjectTemplates", return_value="PROJECT_TEMPLATES")
    @patch("climmob.views.project.getActiveProject", return_value="ACTIVE_PROJECT_INFO")
    @patch("climmob.views.project.create_project_function", return_value=({},"This project does not comply with the limitations on the number of participants per project.",False))
    def test_process_view_new_project_view_post_no_added(self, mock_create_project_function, mock_get_active_project, mock_get_project_templates, mock_get_list_of_languages_by_user, mock_get_all_project_location,mock_get_all_unit_of_analysis_by_location,mock_get_all_objectives_by_location_and_unit_of_analysis, mock_get_all_affiliations):
        self.view.user.fullName = "SOME_VALUE",
        self.view.user.email = "CLIMMOB@EXAMPLE.COM",
        result = self.view.processView()
        self.assertEqual(result, {
            'activeProject': 'ACTIVE_PROJECT_INFO',
            'indashboard': True,
            'dataworking': {
                'project_cod': '',
                'project_name': '',
                'project_abstract': '',
                'project_tags': '',
                'project_pi': ('SOME_VALUE',),
                'project_piemail': ('CLIMMOB@EXAMPLE.COM',),
                'project_numobs': 0,
                'project_numcom': 3,
                'project_regstatus': 0,
                'project_localvariety': 'on',
                'project_cnty': None,
                'project_registration_and_analysis': 0,
                'project_label_a': 'Option A',
                'project_label_b': 'Option B',
                'project_label_c': 'Option C',
                'project_template': 0,
                'usingTemplate': '',
                'project_location': '-1',
                'project_unit_of_analysis': '-1'
            },
            'newproject': False,
            'countries': [],
            'error_summary': {},
            'listOfTemplates': 'PROJECT_TEMPLATES',
            'listOfLanguages': 'LIST_OF_LANGUAGES',
            'listOfLocations': 'PROJECT_LOCATION',
            'listOfUnitOfAnalysis': 'UNIT_OF_ANALYSIS',
            'listOfObjectives': 'OBJECTIVES_AND_UNIT_OF_ANALYSIS',
            'list_of_affiliation': 'LIST_AFFILIATIONS'
        })
        mock_get_active_project.assert_called_once_with(self.view.user.login, self.view.request)
        mock_get_project_templates.assert_called_once_with(self.view.request,0)
        mock_get_list_of_languages_by_user.assert_called_once_with(self.view.request, self.view.user.login)
        mock_get_all_project_location.assert_called_once_with(self.view.request)
        mock_get_all_unit_of_analysis_by_location.assert_called_once_with(self.view.request, "-1" )
        mock_get_all_objectives_by_location_and_unit_of_analysis.assert_called_once_with(self.view.request, "-1" , "-1")
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch("climmob.views.project.create_project_function")
    def test_process_view_new_project_view_post_success(self, mock_create_project_function):
        self.view.request.POST = {
            "submit": "1",
            "btn_addNewProject": "1",
            "project_cod": "VALUE123",
            "project_registration_and_analysis": '1',
            "project_location": "CLIMMOB",
            "project_unit_of_analysis": "1",
            "project_numobs":1,
        }
        mock_create_project_function.return_value = (
            {"project_cod": "VALUE123"},
            {},
            True
        )
        self.view.user.fullName = "SOME_VALUE"
        self.view.user.email = "CLIMMOB@EXAMPLE.COM"
        result = self.view.processView()
        self.assertIsInstance(result, HTTPFound)

class TestModifyProjectView(BaseViewTestCase):
    view_class = ModifyProjectView
    request_method = "POST"

    def setUp(self):
        super().setUp()

        self.view = ModifyProjectView(self.view.request)
        self.view.request.matchdict = {
            'user': 'testuser',
            'project': 'testproject'
        }
        self.view.user = MagicMock()
        self.view.user.login = 'testuser'
        self.view.user.email = 'testuser@example.com'
        self.view.user.fullName = 'COMPLETE_TEST_USER'
        self.view.request.registry.settings = {
            'projects.limit': 'false',
            'project.maximumnumberofobservations': '100'
        }

    @patch('climmob.views.project.function_create_clone', return_value=1)
    @patch('climmob.views.project.getProjectAssessments', return_value=[
        {"ass_cod": "assessment1"},
        {"ass_cod": "assessment2"},
    ])
    @patch('climmob.views.project.deleteProjectAssessments', return_value=(True, ""))
    @patch('climmob.views.project.deleteRegistryByProjectId', return_value=(True, ""))
    @patch('climmob.views.project.addPrjLang', return_value=(True, ""))
    @patch('climmob.views.project.deleteAllPrjLang', return_value=(True, ""))
    @patch('climmob.views.project.add_project_location_unit_objective', return_value=(True, ""))
    @patch('climmob.views.project.get_location_unit_of_analysis_objectives_by_combination')
    @patch('climmob.views.project.delete_all_project_location_unit_objective', return_value=(True, ""))
    @patch('climmob.views.project.modifyProject', return_value= (True,""))
    @patch('climmob.views.project.get_location_unit_of_analysis_by_combination')
    @patch('climmob.views.project.getProjectData')
    @patch('climmob.views.project.getTheProjectIdForOwner', return_value=1)
    def test_processView_success(self, mock_get_the_project_id_for_owner, mock_get_project_data,
                                 mock_get_location_unit_of_analysis_by_combination, mock_modify_project,
                                 mock_delete_all_project_location_unit_objective, mock_get_location_unit_of_analysis_objectives_by_combination,
                                 mock_add_project_location_unit_objective, mock_delete_all_frj_lang,mock_add_prj_lang,
                                 mock_delete_registry_by_project_id, mock_delete_project_assessments, mock_get_project_assessments,
                                 mock_function_create_clone):

        mock_plugin = MagicMock()
        mock_plugin.before_updating_project.return_value = (True,"","data")

        mock_plugin.before_updating_project.return_value = (True, "", "data")

        self.view.request.POST = {
            'btn_addNewProject': '1',
            'project_cod': 'VALUE123',
            'project_registration_and_analysis': '1',
            'project_location': 'CLIMMOB',
            'project_unit_of_analysis': '1',
            'project_label_a': 'PROJECT_LABEL_A',
            'project_label_b': 'PROJECT_LABEL_B',
            'project_label_c': 'PROJECT_LABEL_C',
            'project_numobs': '20',
            'project_numcom': '20',
            'project_localvariety': 1,
            'project_type': 'on',
            'project_template': 'on',
            'usingTemplate': 'template1',
            'project_languages': ['en', 'es'],
            "testproject": "true"
        }

        mock_get_project_data.return_value = {
            'project_localvariety': 1,
            'project_regstatus': 0,
            'project_numobs': 3,
            'project_numcom': 2,
            'project_registration_and_analysis': 1,
            'project_template_used': '',
            'project_cod': 'VALUE123',
            'project_objectives': ['obj1'],
            'project_languages': ['en'],
            "testproject": "true"
        }

        self.view.getPostDict = MagicMock(return_value={
            'project_cod': 'VALUE123',
            'project_registration_and_analysis': '1',
            'project_location': 'CLIMMOB',
            'project_unit_of_analysis': '1',
            'project_label_a': 'Label A',
            'project_label_b': 'Label B',
            'project_label_c': 'Label C',
            'project_numobs': '3',
            'project_numcom': '2',
            'project_localvariety': '1',
            'project_type': 'on',
            'project_template': 'on',
            'usingTemplate': 'template1',  # <-- Cambiado aquí
            'project_languages': ['en'],
            'project_objectives': ['obj1'],
            "testproject": "true"
        })

        mock_get_location_unit_of_analysis_by_combination.return_value = {
            "pluoa_id":2,
            "plocation_id":1,
            "puoa_id": 2,
            "registration_and_analysis": 12,

        }

        mock_get_location_unit_of_analysis_objectives_by_combination.return_value = {
            "pluoaobj_id":2,
            "pluoa_id": 2,
            "pobjective_id": 1,

        }
        result = self.view.processView()

        self.assertIsInstance(result, HTTPFound)
        mock_get_the_project_id_for_owner.assert_called_with(
            self.view.user.login, 'testproject', self.view.request
        )
        assert mock_get_project_data.call_count >= 2

        mock_get_location_unit_of_analysis_by_combination.assert_called_once_with(
            self.view.request, 'CLIMMOB', '1'
        )

        mock_modify_project.assert_called_once()
        mock_modify_project.assert_called_with(1, ANY, self.view.request)
        mock_delete_all_project_location_unit_objective.assert_called_once_with(1, self.view.request)
        mock_get_location_unit_of_analysis_objectives_by_combination.assert_called()
        mock_add_project_location_unit_objective.assert_called()
        mock_delete_all_frj_lang.assert_called_once_with(1, self.view.request)
        mock_add_prj_lang.assert_called()
        mock_delete_registry_by_project_id.assert_called()
        mock_delete_project_assessments.assert_called()
        mock_get_project_assessments.assert_called()
        mock_function_create_clone.assert_called_once()




if __name__ == '__main__':
    unittest.main()