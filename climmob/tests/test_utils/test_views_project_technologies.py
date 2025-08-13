from unittest.mock import patch, MagicMock, ANY

from decorator import append
from pyramid.httpexceptions import HTTPFound

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views import project_technologies
from climmob.views.project_technologies import ProjectTechnologiesView


class TestProjectTechnologiesView(ViewBaseTest):
    view_class = ProjectTechnologiesView

    def setUp(self):
        super().setUp()
        self.view.request.matchdict= {"user":"test_owner","project":1}

        self.project_id_owner_patcher = patch(
            "climmob.views.project_technologies.getTheProjectIdForOwner")
        self.prj_data_patcher = patch(
            "climmob.views.project_technologies.getProjectData")
        self.list_combinations_patcher = patch(
            "climmob.views.project_technologies.getCombinationsData")
        self.technologies_in_project_patcher = patch(
            "climmob.views.project_technologies.searchTechnologiesInProject")
        self.get_active_project_patcher = patch(
            "climmob.views.project_technologies.getActiveProject")
        self.search_technologies_patcher = patch(
            "climmob.views.project_technologies.searchTechnologies")
        self.number_of_combinations_patcher = patch(
            "climmob.views.project_technologies.numberOfCombinationsForTheProject")
        self.get_post_dict_patcher = patch(
            "climmob.views.project_technologies.ProjectTechnologiesView.getPostDict")
        self.add_technology_project_patcher = patch(
            "climmob.views.project_technologies.addTechnologyProject")
        self.prj_tech_aliases_patcher = patch(
            "climmob.views.project_technologies.prjTechAliases_view.processView")
        self.get_technology_patcher = patch(
            "climmob.views.project_technologies.getTechnology")
        self.is_technology_assigned_patcher = patch(
            "climmob.views.project_technologies.isTechnologyAssigned")


        self.mock_get_project_id_for_owner = self.project_id_owner_patcher.start()
        self.mock_prj_data = self.prj_data_patcher.start()
        self.mock_list_combinations_patcher = self.list_combinations_patcher.start()
        self.mock_search_technologies_in_project = self.technologies_in_project_patcher.start()
        self.mock_active_project = self.get_active_project_patcher.start()
        self.mock_technologies_user = self.search_technologies_patcher.start()
        self.mock_project_numcom = self.number_of_combinations_patcher.start()
        self.mock_post_data = self.get_post_dict_patcher.start()
        self.mock_add_tech = self.add_technology_project_patcher.start()
        self.mock_alias = self.prj_tech_aliases_patcher.start()
        self.mock_tech_see = self.get_technology_patcher.start()
        self.mock_assigned = self.is_technology_assigned_patcher.start()

        self.mock_get_project_id_for_owner.return_value = 1
        self.mock_prj_data.return_value = {
            "project_template":0,
            "project_createpkgs":1,
            "project_regstatus":0
        }
        self.mock_list_combinations_patcher.return_value = MagicMock(dict,name="list_combinations")
        self.mock_search_technologies_in_project.return_value = [
            {"quantity": 1},
            {"quantity": 2},
            {"quantity": 3}
        ]
        self.mock_active_project.return_value = MagicMock(dict,name="active_project")
        self.mock_technologies_user.return_value = MagicMock(dict,name="technologies_user")
        self.mock_project_numcom.return_value = MagicMock(dict, name="project_numcom")
        self.mock_post_data.return_value= {"tech_id":MagicMock(name="tech_id"),
                                           "txt_technologies_included":"",
                                           "txt_technologies_excluded": ""}
        self.mock_alias.return_value = MagicMock(dict,name="alias")
        self.mock_tech_see.return_value = MagicMock(dict,name="techSee")
        self.mock_assigned.return_value = False


        self.addCleanup(self.project_id_owner_patcher.stop)
        self.addCleanup(self.prj_data_patcher.stop)
        self.addCleanup(self.list_combinations_patcher.stop)
        self.addCleanup(self.technologies_in_project_patcher.stop)
        self.addCleanup(self.get_active_project_patcher.stop)
        self.addCleanup(self.search_technologies_patcher.stop)
        self.addCleanup(self.number_of_combinations_patcher.stop)
        self.addCleanup(self.get_post_dict_patcher.stop)
        self.addCleanup(self.add_technology_project_patcher.stop)
        self.addCleanup(self.prj_tech_aliases_patcher.stop)
        self.addCleanup(self.get_technology_patcher.stop)
        self.addCleanup(self.is_technology_assigned_patcher.stop)

    def tearDown(self):
        if self.mock_get_project_id_for_owner.called:
            self.mock_get_project_id_for_owner.assert_called_with(
                self.request.matchdict["user"],
                self.mock_get_project_id_for_owner.return_value,
                self.view.request)
        if self.mock_prj_data.called:
            self.mock_prj_data.assert_called_once_with(
                self.mock_get_project_id_for_owner.return_value, self.view.request
            )
        if self.mock_list_combinations_patcher.called:
            self.mock_list_combinations_patcher.assert_called_once_with(
                self.mock_get_project_id_for_owner.return_value, self.view.request
            )
        if self.mock_search_technologies_in_project.called:
            self.mock_search_technologies_in_project.assert_called_once_with(
                self.mock_get_project_id_for_owner.return_value, self.view.request
            )
        if self.mock_active_project.called:
            self.mock_active_project.assert_called_once_with(
                self.view.user.login, self.view.request
            )
        if self.mock_technologies_user.called:
            self.mock_technologies_user.assert_called_once_with(
                self.mock_get_project_id_for_owner.return_value, self.view.request
            )
        if self.mock_project_numcom.called:
            self.mock_project_numcom.assert_called_once_with(
                self.mock_get_project_id_for_owner.return_value, self.view.request
            )
        if self.mock_post_data.called:
            self.mock_post_data.assert_called_once()
        if self.mock_add_tech.called:
            self.mock_add_tech.assert_called_once_with(
                self.mock_get_project_id_for_owner.return_value, ANY, self.view.request
            )
        if self.mock_alias.called:
            self.mock_alias.assert_called_once_with(self.view
                                                    )
        if self.mock_tech_see.called:
            self.mock_tech_see.assert_called_once_with(
                self.mock_post_data.return_value, self.view.request
            )


        super().tearDown()

    def test_project_technologies_view_get(self):
        self.mock_prj_data.return_value["project_template"] = 1
        self.view.request.route_url = MagicMock(return_value="/dashboard")
        result = self.view.get()
        self.assertIsInstance(result, HTTPFound)
        self.assertEqual(result.status, "302 Found")
        self.assertEqual(result.location, "/dashboard")

    def test_project_technologies_view_get_complete(self):
        self.mock_prj_data.return_value["project_regstatus"] = 1
        result = self.view.get()
        self.assertEqual(result,
                         {
                             "activeUser": self.view.user,
                             "activeProject": self.mock_active_project.return_value,
                             "tech_id": "",
                             "TechnologiesUser": self.mock_technologies_user.return_value,
                             "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
                             "project_numcom": self.mock_project_numcom.return_value,
                             "alias": {},
                             "dataworking": {"alias_name": ""},
                             "error_summary": {},
                             "techSee": {},
                             "error_summary2": {},
                             "totalOfCombinations": 6,
                             "combinations": self.mock_list_combinations_patcher.return_value,
                         }
                         )

    def test_project_technologies_view_get_complete_w_error(self):
        self.mock_prj_data.return_value["project_regstatus"] = 1
        self.mock_search_technologies_in_project.return_value = [
            {"quantity": 10},
            {"quantity": 20},
            {"quantity": 30}
        ]
        result = self.view.get()
        self.assertEqual(result,{
                             "activeUser": self.view.user,
                             "activeProject": self.mock_active_project.return_value,
                             "tech_id": "",
                             "TechnologiesUser": self.mock_technologies_user.return_value,
                             "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
                             "project_numcom": self.mock_project_numcom.return_value,
                             "alias": {},
                             "dataworking": {"alias_name": ""},
                             "error_summary": {},
                             "techSee": {},
                             "error_summary2": {'totalOfCombinations': "ClimMob has limited the number of possible combinations to 50, at the moment you are exceeding this number so you must remove technology options to be able to create the packages later."},
                             "totalOfCombinations": 6000,
                             "combinations": self.mock_list_combinations_patcher.return_value,
                         })
    @patch("climmob.views.project_technologies.deleteTechnologyProject")
    def test_project_technologies_view_post_btn_save_tech(self, mock_delete_technology_project):
        self.mock_post_data.return_value.update({"btn_save_technologies":True,
                                                 "txt_technologies_included": "tech_123_new,other_456_old",
                                                 "txt_technologies_excluded": "tech_123_exists,other_456_old"})
        result = self.view.post()
        self.assertEqual(result, {
            "activeUser": self.view.user,
            "activeProject": self.mock_active_project.return_value,
            "tech_id": "",
            "TechnologiesUser": self.mock_technologies_user.return_value,
            "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
            "project_numcom": self.mock_project_numcom.return_value,
            "alias": {},
            "dataworking": {"alias_name": ""},
            "error_summary": {},
            "techSee": {},
            "error_summary2": {},
            "totalOfCombinations": 6,
            "combinations": [],
        })
        mock_delete_technology_project.assert_called_once_with(self.mock_get_project_id_for_owner.return_value, ANY, self.view.request)

    def test_project_technologies_view_post_btn_sh_tech_alias(self):
        self.mock_post_data.return_value.update({"btn_show_technology_alias": True,
                                                 "txt_technologies_included": "tech_123_new,other_456_old",
                                                 })
        result = self.view.post()
        self.assertEqual(result, {
            "activeUser": self.view.user,
            "activeProject": self.mock_active_project.return_value,
            "tech_id": self.mock_post_data.return_value["tech_id"],
            "TechnologiesUser": self.mock_technologies_user.return_value,
            "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
            "project_numcom": self.mock_project_numcom.return_value,
            "alias": self.mock_alias.return_value,
            "dataworking": {"alias_name": ""},
            "error_summary": {},
            "techSee": self.mock_tech_see.return_value,
            "error_summary2": {},
            "totalOfCombinations": 6,
            "combinations": [],
        })
        self.mock_tech_see.assert_called_once_with(
            {"tech_id": self.mock_post_data.return_value["tech_id"],
             'txt_technologies_included':self.mock_post_data.return_value["txt_technologies_included"],
             'txt_technologies_excluded': '',
             'btn_show_technology_alias': True
             },
            self.view.request
        )
        self.mock_tech_see.assert_called_once_with(
            {"tech_id": self.mock_post_data.return_value["tech_id"],
             'txt_technologies_included':self.mock_post_data.return_value["txt_technologies_included"],
             'txt_technologies_excluded': '',
             'btn_show_technology_alias': True
             },
            self.view.request
        )
    @patch("climmob.views.project_technologies.AliasSearchTechnology")
    def test_project_technologies_view_post_btn_sh_tech_alias_in_lib(self, mock_alias_search_technology):
        self.mock_post_data.return_value.update({"btn_show_technology_alias_in_library": True,
                                                 })
        mock_alias_search_technology.return_value =  MagicMock(name="AliasTechnology")
        result = self.view.post()
        self.assertEqual(result, {
            "activeUser": self.view.user,
            "activeProject": self.mock_active_project.return_value,
            "tech_id": self.mock_post_data.return_value["tech_id"],
            "TechnologiesUser": self.mock_technologies_user.return_value,
            "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
            "project_numcom": self.mock_project_numcom.return_value,
            "alias": {"AliasTechnology":mock_alias_search_technology.return_value},
            "dataworking": {'alias_name': ''},
            "error_summary": {},
            "techSee": self.mock_tech_see.return_value,
            "error_summary2": {},
            "totalOfCombinations": 6,
            "combinations": [],
        })
        mock_alias_search_technology.assert_called_once_with(
            self.mock_post_data.return_value["tech_id"],
            1,
            self.view.request)


    def test_project_technologies_view_post_btn_save_tech_alias(self):
        self.mock_post_data.return_value.update({"btn_save_technologies_alias": True})
        result = self.view.post()
        self.assertEqual(result, {
            "activeUser": self.view.user,
            "activeProject": self.mock_active_project.return_value,
            "tech_id": self.mock_post_data.return_value["tech_id"],
            "TechnologiesUser": self.mock_technologies_user.return_value,
            "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
            "project_numcom": self.mock_project_numcom.return_value,
            "alias": self.mock_alias.return_value,
            "dataworking": {'alias_name': '', "project_id":1,
                            "tech_id": self.mock_post_data.return_value["tech_id"], "user_name": self.view.user.login
                            },
            "error_summary": {},
            "techSee": self.mock_tech_see.return_value,
            "error_summary2": {},
            "totalOfCombinations": 6,
            "combinations": [],
        })
        self.mock_tech_see.assert_called_once_with(
            {"tech_id": self.mock_post_data.return_value["tech_id"],
             'txt_technologies_included':self.mock_post_data.return_value["txt_technologies_included"],
             'txt_technologies_excluded': '',
             'btn_save_technologies_alias': True
             },
            self.view.request
        )

    @patch("climmob.views.project_technologies.prjTechAliasAdd_view.processView")
    def test_project_technologies_view_post_btn_add_alias(self, mock_prj_tech_alias_add):
        self.maxDiff = None
        self.mock_post_data.return_value.update({"btn_add_alias": True})
        mock_data = MagicMock(name="dataworking_mock")
        mock_prj_tech_alias_add.return_value = {
            "dataworking": mock_data,
            "error_summary": {},
            "redirect": "some_value"
        }
        result = self.view.post()
        self.assertEqual(result, {
            "activeUser": self.view.user,
            "activeProject": self.mock_active_project.return_value,
            "tech_id": self.mock_post_data.return_value["tech_id"],
            "TechnologiesUser": self.mock_technologies_user.return_value,
            "TechnologiesInProject": self.mock_search_technologies_in_project.return_value,
            "project_numcom": self.mock_project_numcom.return_value,
            "alias": self.mock_alias.return_value,
            "dataworking": mock_data,
            "error_summary": {},
            "techSee": self.mock_tech_see.return_value,
            "error_summary2": {},
            "totalOfCombinations": 6,
            "combinations": [],
        })
        mock_prj_tech_alias_add.assert_called_once_with(self.view)

