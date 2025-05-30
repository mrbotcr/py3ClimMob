import datetime as real_datetime
from unittest.mock import patch

from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.project_metadata import ProjectMetadataFormView, ShowMetadataFormView


class TestProjectMetadataFormView(ViewBaseTest):
    view_class = ProjectMetadataFormView
    request_method = "POST"

    def setUp(self):
        super().setUp()
        self.view.request.matchdict = {"project": "Test_Project", "user": "test_user"}
        self.view.request.params = {"metadataForm": {"data1": "data1"}}
        self.view.request.POST = {
            "btn_save_metadata": 1,
            "_jsonResult": '{"some": "data3"}',
            "metadata_id": 3,
        }

    @patch("climmob.views.project_metadata.projectExists", return_value=False)
    @patch("climmob.views.project_metadata.getActiveProject", return_value=1)
    def test_process_view_project_metadata_form_view_no_metadata_no_project_exist(
        self, mock_get_active_project, mock_project_exists
    ):
        self.view.request.params = {}
        with self.assertRaises(HTTPNotFound):
            self.view.processView()
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )

    @patch(
        "climmob.views.project_metadata.getMetadataForProject",
        return_value={"Data2": "data2"},
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=2)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    @patch("climmob.views.project_metadata.getActiveProject", return_value=1)
    @patch("climmob.views.project_metadata.getMetadataForm", return_value=None)
    def test_process_view_project_metadata_form_view_no_post(
        self,
        mock_get_metadata_form,
        mock_get_active_project,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_for_project,
    ):
        self.view.request.method = "GET"
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "activeProject": 1,
                "dataworking": {},
                "metadataForm": None,
                "listOfProjectMetadata": {"Data2": "data2"},
            },
        )
        mock_get_metadata_form.assert_called_once_with(
            self.view.request, {"data1": "data1"}
        )
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_for_project.assert_called_once_with(self.view.request, 2)

    @patch(
        "climmob.views.project_metadata.modifyProjectMetadataForm",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.project_metadata.getProjectMetadataForm",
        return_value={"data4": "data4"},
    )
    @patch(
        "climmob.views.project_metadata.getMetadataForProject",
        return_value={"Data2": "data2"},
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=2)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    @patch("climmob.views.project_metadata.getActiveProject", return_value=1)
    @patch("climmob.views.project_metadata.getMetadataForm", return_value=None)
    def test_process_view_project_metadata_form_view_edited(
        self,
        mock_get_metadata_form,
        mock_get_active_project,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_for_project,
        mock_get_project_metadata_form,
        mock_modify_project_metadata_form,
    ):
        response = self.view.processView()
        self.assertIsInstance(response, HTTPFound)
        mock_get_metadata_form.assert_called_once_with(
            self.view.request, {"data1": "data1"}
        )
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_for_project.assert_called_once_with(self.view.request, 2)
        mock_get_project_metadata_form.assert_called_once_with(self.view.request, 2, 3)
        mock_modify_project_metadata_form.assert_called_once_with(
            self.view.request,
            2,
            3,
            {
                "btn_save_metadata": 1,
                "_jsonResult": '{"some": "data3"}',
                "metadata_id": 3,
                "project_id": 2,
                "pmf_json": {"some": "data3"},
            },
        )

    @patch("climmob.views.project_metadata.datetime")
    @patch(
        "climmob.views.project_metadata.addProjectMetadataForm", return_value=(True, "")
    )
    @patch("climmob.views.project_metadata.getProjectMetadataForm", return_value={})
    @patch(
        "climmob.views.project_metadata.getMetadataForProject",
        return_value={"Data2": "data2"},
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=2)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    @patch("climmob.views.project_metadata.getActiveProject", return_value=1)
    @patch("climmob.views.project_metadata.getMetadataForm", return_value=None)
    def test_process_view_project_metadata_form_view_added(
        self,
        mock_get_metadata_form,
        mock_get_active_project,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_for_project,
        mock_get_project_metadata_form,
        mock_add_project_metadata_form,
        mock_datetime,
    ):
        fixed_time = real_datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: real_datetime.datetime(
            *args, **kwargs
        )
        self.view.request.locale_name = "en"
        response = self.view.processView()
        self.assertIsInstance(response, HTTPFound)
        mock_get_metadata_form.assert_called_once_with(
            self.view.request, {"data1": "data1"}
        )
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_for_project.assert_called_once_with(self.view.request, 2)
        mock_get_project_metadata_form.assert_called_once_with(self.view.request, 2, 3)
        mock_add_project_metadata_form.assert_called_once_with(
            {
                "btn_save_metadata": 1,
                "_jsonResult": '{"some": "data3"}',
                "metadata_id": 3,
                "project_id": 2,
                "pmf_json": {"some": "data3"},
                "pmf_last_update": fixed_time,
                "pmf_lang": "en",
            },
            self.view.request,
        )

    @patch("climmob.views.project_metadata.datetime")
    @patch(
        "climmob.views.project_metadata.modifyProjectMetadataForm",
        return_value=(True, ""),
    )
    @patch(
        "climmob.views.project_metadata.getProjectMetadataForm",
        return_value={"data4": "data4"},
    )
    @patch(
        "climmob.views.project_metadata.getMetadataForProject",
        return_value={"Data2": "data2"},
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=2)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    @patch("climmob.views.project_metadata.getActiveProject", return_value=1)
    @patch("climmob.views.project_metadata.getMetadataForm", return_value=None)
    def test_process_view_project_metadata_form_view_edited(
        self,
        mock_get_metadata_form,
        mock_get_active_project,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_for_project,
        mock_get_project_metadata_form,
        mock_modify_project_metadata_form,
        mock_datetime,
    ):
        fixed_time = real_datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: real_datetime.datetime(
            *args, **kwargs
        )

        response = self.view.processView()
        self.assertIsInstance(response, HTTPFound)
        mock_get_metadata_form.assert_called_once_with(
            self.view.request, {"data1": "data1"}
        )
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_for_project.assert_called_once_with(self.view.request, 2)
        mock_get_project_metadata_form.assert_called_once_with(self.view.request, 2, 3)
        mock_modify_project_metadata_form.assert_called_once_with(
            self.view.request,
            2,
            3,
            {
                "btn_save_metadata": 1,
                "_jsonResult": '{"some": "data3"}',
                "metadata_id": 3,
                "project_id": 2,
                "pmf_json": {"some": "data3"},
                "pmf_last_update": fixed_time,
            },
        )

    @patch("climmob.views.project_metadata.datetime")
    @patch(
        "climmob.views.project_metadata.addProjectMetadataForm",
        return_value=(False, "Error to add"),
    )
    @patch("climmob.views.project_metadata.getProjectMetadataForm", return_value={})
    @patch(
        "climmob.views.project_metadata.getMetadataForProject",
        return_value={"Data2": "data2"},
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=2)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    @patch("climmob.views.project_metadata.getActiveProject", return_value=1)
    @patch("climmob.views.project_metadata.getMetadataForm", return_value=None)
    def test_process_view_project_metadata_form_view_added_failure(
        self,
        mock_get_metadata_form,
        mock_get_active_project,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_for_project,
        mock_get_project_metadata_form,
        mock_add_project_metadata_form,
        mock_datetime,
    ):
        fixed_time = real_datetime.datetime(2024, 1, 1, 12, 0, 0)
        mock_datetime.now.return_value = fixed_time
        mock_datetime.side_effect = lambda *args, **kwargs: real_datetime.datetime(
            *args, **kwargs
        )

        self.view.request.locale_name = "en"
        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "activeProject": 1,
                "dataworking": {},
                "metadataForm": None,
                "listOfProjectMetadata": {"Data2": "data2"},
            },
        )
        mock_get_metadata_form.assert_called_once_with(
            self.view.request, {"data1": "data1"}
        )
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_for_project.assert_called_once_with(self.view.request, 2)
        mock_get_project_metadata_form.assert_called_once_with(self.view.request, 2, 3)
        mock_add_project_metadata_form.assert_called_once_with(
            {
                "btn_save_metadata": 1,
                "_jsonResult": '{"some": "data3"}',
                "metadata_id": 3,
                "project_id": 2,
                "pmf_json": {"some": "data3"},
                "pmf_last_update": fixed_time,
                "pmf_lang": "en",
            },
            self.view.request,
        )


class TestShowMetadataFormView(ViewBaseTest):
    view_class = ShowMetadataFormView

    def setUp(self):
        super().setUp()
        self.view.request.matchdict = {
            "project": "Test_Project",
            "user": "test_user",
            "metadataform": "data1",
        }
        self.view.request.locale_name = "en"

    def test_process_view_show_project_metadata_form_view_no_get(self):
        self.view.request.method = "POST"
        response = self.view.processView()
        self.assertEqual(response, "")

    @patch("climmob.views.project_metadata.projectExists", return_value=False)
    def test_process_view_show_project_metadata_form_view_no_project_exists(
        self, mock_project_exists
    ):
        response = self.view.processView()
        self.assertEqual(response, "")
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )

    @patch("climmob.views.project_metadata.getMetadataForm", return_value={})
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    def test_process_view_show_project_metadata_form_view_no_metadata_form(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_form,
    ):
        response = self.view.processView()
        self.assertEqual(response, "")
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_form.assert_called_once_with(self.view.request, "data1")

    @patch(
        "climmob.views.project_metadata.get_all_affiliations",
        return_value={"data8", "data8"},
    )
    @patch(
        "climmob.views.project_metadata.getActiveProject",
        return_value={"data7": "data7"},
    )
    @patch(
        "climmob.views.project_metadata.getCombinations",
        return_value=(
            {},
            {},
            [
                {"tech_id": 1, "alias_id": 2, "alias_name": "test"},
                {"tech_id": 3, "alias_id": 4, "alias_name": "test2"},
            ],
        ),
    )
    @patch(
        "climmob.views.project_metadata.languageByLanguageCode",
        return_value={"lang_code": "es", "lang_name": "Español"},
    )
    @patch(
        "climmob.views.project_metadata.getProjectMetadataForm",
        return_value={
            "data": "data3",
            "pmf_lang": "es",
            "pmf_json": {"data6": "data6"},
        },
    )
    @patch(
        "climmob.views.project_metadata.getMetadataForm",
        return_value={
            "data2": "data2",
            "metadata_for_technology_options": 1,
            "metadata_json": '{"data7":"data7"}',
            "metadata_name": "name",
        },
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    def test_process_view_show_project_metadata_form_view_success(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_form,
        mock_get_project_metadata_form,
        mock_language_by_language_code,
        mock_get_combinations,
        mock_get_active_project,
        mock_get_all_affiliations,
    ):
        response = self.view.processView()
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_form.assert_called_once_with(self.view.request, "data1")
        mock_get_project_metadata_form.assert_called_once_with(
            self.view.request, 1, "data1"
        )
        mock_language_by_language_code.assert_called_once_with("es", self.view.request)
        mock_get_combinations.assert_called_once_with(1, self.view.request)
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_get_all_affiliations.assert_called_once_with(self.view.request)

    @patch(
        "climmob.views.project_metadata.get_all_affiliations",
        return_value={"data8", "data8"},
    )
    @patch(
        "climmob.views.project_metadata.getActiveProject",
        return_value={"data7": "data7"},
    )
    @patch(
        "climmob.views.project_metadata.getCombinations",
        return_value=(
            {},
            {},
            [
                {"tech_id": 1, "alias_id": 2, "alias_name": "test"},
                {"tech_id": 3, "alias_id": 4, "alias_name": "test2"},
            ],
        ),
    )
    @patch(
        "climmob.views.project_metadata.languageByLanguageCode",
        return_value={"lang_code": "es", "lang_name": "Español"},
    )
    @patch(
        "climmob.views.project_metadata.getProjectMetadataForm",
        return_value={"data": "data3", "pmf_lang": "es", "pmf_json": {}},
    )
    @patch(
        "climmob.views.project_metadata.getMetadataForm",
        return_value={
            "data2": "data2",
            "metadata_for_technology_options": 1,
            "metadata_json": '{"data7":"data7"}',
            "metadata_name": "name",
        },
    )
    @patch("climmob.views.project_metadata.getTheProjectIdForOwner", return_value=1)
    @patch("climmob.views.project_metadata.projectExists", return_value=True)
    def test_process_view_show_project_metadata_form_view_success_no_information_filled(
        self,
        mock_project_exists,
        mock_get_the_project_id_for_owner,
        mock_get_metadata_form,
        mock_get_project_metadata_form,
        mock_language_by_language_code,
        mock_get_combinations,
        mock_get_active_project,
        mock_get_all_affiliations,
    ):
        response = self.view.processView()
        mock_project_exists.assert_called_once_with(
            "test_user", "test_user", "Test_Project", self.view.request
        )
        mock_get_the_project_id_for_owner.assert_called_once_with(
            "test_user", "Test_Project", self.view.request
        )
        mock_get_metadata_form.assert_called_once_with(self.view.request, "data1")
        mock_get_project_metadata_form.assert_called_once_with(
            self.view.request, 1, "data1"
        )
        mock_language_by_language_code.assert_called_once_with("es", self.view.request)
        mock_get_combinations.assert_called_once_with(1, self.view.request)
        mock_get_active_project.assert_called_once_with("test_user", self.view.request)
        mock_get_all_affiliations.assert_called_once_with(self.view.request)
