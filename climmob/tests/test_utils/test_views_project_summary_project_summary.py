from unittest.mock import MagicMock, call, ANY
from unittest.mock import patch

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.projectsSummary.projectsSummary import *


class TestDownloadProjectsSummaryView(ViewBaseTest):
    view_class = DownloadProjectsSummaryView

    @patch("climmob.views.projectsSummary.projectsSummary.FileResponse")
    @patch(
        "climmob.views.projectsSummary.projectsSummary.DownloadProjectsSummaryView.create_projects_summary_json_xlsx"
    )
    @patch("climmob.views.projectsSummary.projectsSummary.os.path.join")
    @patch(
        "climmob.views.projectsSummary.projectsSummary.product_found", return_value=True
    )
    @patch("climmob.views.projectsSummary.projectsSummary.getProductData")
    @patch("climmob.views.projectsSummary.projectsSummary.getUserInfo")
    def test_download_project_summary_view_get_admin(
        self,
        mock_get_user_info,
        mock_get_product_data,
        mock_product_found,
        mock_join,
        mock_create_projects_summary_json_xlsx,
        mock_file_response,
    ):
        self.request.params = {
            "celery_taskid": "some_value_celery_taskid",
            "product_id": "some_value_product_id",
        }
        self.view.request.registry.settings["user.repository"] = "/mocked/path/"
        mock_get_user_info.return_value = {
            "user_admin": 1,
        }
        mock_get_product_data.return_value = {
            "product_id": "some_value_product_id",
            "output_mimetype": "application/sheet",
            "output_id": "projectsSummary_mock.xlsx",
        }
        mock_join.side_effect = [
            "/mocked/path/_report",
            "/mocked/path/_report/projectsSummary_mock.xlsx",
        ]
        mock_create_projects_summary_json_xlsx.return_value = None
        mock_response = MagicMock()
        mock_file_response.return_value = mock_response

        response = self.view.get()

        self.assertTrue(hasattr(response, "content_disposition"))
        self.assertEqual(
            response.content_disposition,
            'attachment; filename="projectsSummary_mock.xlsx"',
        )
        mock_get_user_info.asser_called_once(self.view.request, self.view.user.login)
        mock_get_product_data.assert_called_once_with(
            None,
            self.view.request.params.get("celery_taskid"),
            self.view.request.params.get("product_id"),
            self.view.request,
        )
        mock_product_found.assert_called_once_with(
            mock_get_product_data.return_value["product_id"]
        )
        mock_join.assert_has_calls(
            [
                call(self.view.request.registry.settings["user.repository"], "_report"),
                call(
                    "/mocked/path/_report",
                    mock_get_product_data.return_value["output_id"],
                ),
            ]
        )

        mock_create_projects_summary_json_xlsx.assert_called_once_with(
            self.view.request, "/mocked/path/_report", process_name="projectsSummary"
        )

        mock_file_response.assert_called_once_with(
            "/mocked/path/_report/projectsSummary_mock.xlsx",
            request=self.view.request,
            content_type="application/sheet",
        )

    @patch(
        "climmob.views.projectsSummary.projectsSummary.product_found",
        return_value=False,
    )
    @patch("climmob.views.projectsSummary.projectsSummary.getProductData")
    @patch("climmob.views.projectsSummary.projectsSummary.getUserInfo")
    def test_download_project_summary_view_get_admin_no_product(
        self,
        mock_get_user_info,
        mock_get_product_data,
        mock_product_found,
    ):
        self.request.params = {
            "celery_taskid": "some_value_celery_taskid",
            "product_id": "some_value_product_id",
        }

        self.view.request.registry.settings["user.repository"] = "/mocked/path/"
        mock_get_user_info.return_value = {
            "user_admin": 1,
        }
        mock_get_product_data.return_value = {
            "product_id": "some_value_product_id",
            "output_mimetype": "application/sheet",
            "output_id": "projectsSummary_mock.json",
        }

        response = self.view.get()
        self.assertFalse(response)
        mock_get_user_info.asser_called_once(self.view.request, self.view.user.login)
        mock_get_product_data.assert_called_once_with(
            None,
            self.view.request.params.get("celery_taskid"),
            self.view.request.params.get("product_id"),
            self.view.request,
        )
        mock_product_found.assert_called_once_with(
            mock_get_product_data.return_value["product_id"]
        )

    @patch("climmob.views.projectsSummary.projectsSummary.DataColumn")
    @patch("climmob.views.projectsSummary.projectsSummary.create_json_exel_file")
    @patch("climmob.views.projectsSummary.projectsSummary.get_all_project_summary")
    def test_create_projects_summary_json_xlsx(
        self, mock_get_all_projects, mock_create_json_excel, mock_data_column
    ):
        mock_request = MagicMock()
        mock_request.registry.settings = {
            "setting1": "value1",
            "setting2": "value2",
        }
        mock_get_all_projects.return_value = ["proj1", "proj2"]
        mock_data_column.get_key_project_summary = MagicMock(list, name="order_column")
        mock_order_column = mock_data_column.get_key_project_summary()
        result = self.view.create_projects_summary_json_xlsx(
            mock_request, jsonLocation="/fake/path", process_name="projectsSummaryTest"
        )

        self.assertIsNone(result)

        expected_settings = {
            "setting1": "value1",
            "setting2": "value2",
        }

        mock_get_all_projects.assert_called_once_with(mock_request)
        mock_create_json_excel.assert_called_once_with(
            "/fake/path",
            "projectsSummaryTest",
            expected_settings,
            ["proj1", "proj2"],
            column_order=mock_order_column,
        )


class TestProjectsSummaryCurationView(ViewBaseTest):
    view_class = ProjectsSummaryCurationView

    def setUp(self):
        super().setUp()
        self.report_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.ProjectsSummaryCurationView.get_data_product"
        )
        self.column_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.DataColumn.get_project_summary_columns"
        )
        self.user_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_user_project_summary"
        )
        self.all_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_all_project_summary"
        )
        self.create_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.create_projects_summary"
        )
        self.affiliations_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_all_affiliations"
        )
        self.get_dict_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.DataColumn.get_dict"
        )

        self.mock_get_data_product = self.report_patcher.start()
        self.mock_get_columns = self.column_patcher.start()
        self.mock_get_user = self.user_patcher.start()
        self.mock_get_all = self.all_patcher.start()
        self.mock_create = self.create_patcher.start()
        self.mock_affiliations = self.affiliations_patcher.start()
        self.mock_get_dict = self.get_dict_patcher.start()

        self.mock_get_data_product.return_value = "last_report"
        self.mock_get_columns.return_value = {"column1": "column1"}
        self.mock_get_user.return_value = {"data1": "data1"}
        self.mock_get_all.return_value = {"data1": "data1"}
        self.mock_affiliations.return_value = {"Affiliation": "affiliation1"}
        self.mock_get_dict.return_value = {"dictColumn": "dictValue"}

        self.addCleanup(self.report_patcher.stop)
        self.addCleanup(self.column_patcher.stop)
        self.addCleanup(self.user_patcher.stop)
        self.addCleanup(self.all_patcher.stop)
        self.addCleanup(self.create_patcher.stop)
        self.addCleanup(self.affiliations_patcher.stop)
        self.addCleanup(self.get_dict_patcher.stop)

    def tearDown(self):

        if self.mock_get_columns.called:
            self.mock_get_columns.assert_called_once_with(self.view)
        if self.mock_get_user.called:
            self.mock_get_user.assert_called_once_with(
                self.view.request, self.view.user.userData["user_name"]
            )
        if self.mock_get_all.called:
            self.mock_get_all.assert_called_once_with(self.view.request)
        if self.mock_affiliations.called:
            self.mock_affiliations.assert_called_once_with(self.view.request)
        if self.mock_get_dict.called:
            self.mock_get_dict.assert_called_once_with(self.view)

        super().tearDown()

    def test_projects_summary_curation_view_my_converter_success(self):
        date_time = datetime.datetime(2025, 1, 1, 12, 00, 00)
        result = ProjectsSummaryCurationView.myconverter(date_time)
        self.assertEqual(result, str(date_time))

    def test_projects_summary_curation_view_get_no_admin(self):
        response = self.view.get()
        self.assertEqual(
            response,
            {
                "table_structure": {"dictColumn": "dictValue"},
                "tableStructure": self.mock_get_columns.return_value,
                "listOfProjects": json.dumps(self.mock_get_all.return_value, indent=4),
                "lastReport": "last_report",
                "edit_mode": False,
                "sectionActive": "projectsSummaryCuration",
                "list_of_affiliation": {"Affiliation": "affiliation1"},
            },
        )

    def test_projects_summary_curation_get_view_admin(self):
        self.view.user.admin = 1
        response = self.view.get()
        self.assertEqual(
            response,
            {
                "lastReport": "last_report",
                "sectionActive": "projectsSummaryCuration",
                "table_structure": {"dictColumn": "dictValue"},
                "tableStructure": self.mock_get_columns.return_value,
                "listOfProjects": json.dumps(self.mock_get_all.return_value, indent=4),
                "edit_mode": True,
                "list_of_affiliation": {"Affiliation": "affiliation1"},
            },
        )

    def test_projects_summary_curation_view_post_success(self):
        self.view.user.admin = 1
        self.request_method = "POST"
        self.view.request.POST = {"btn_generate_report": True}
        self.view.request.route_url = MagicMock(return_value="/projectsSummary")

        response = self.view.post()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/projectsSummary")
        self.assertEqual(response.status_code, 302)
        self.mock_create.assert_called_once_with(self.view.request)


class TestProjectsSummaryCurationView2(ViewBaseTest):
    view_class = ProjectsSummaryCurationView

    def test_projects_summary_curation_view_get_data_product(self):
        self.mock_request = MagicMock()
        fake_row = {
            "celery_taskid": "some_value_celery_task",
            "project_id": None,
            "product_id": "projects_summary",
            "datetime_added": datetime.datetime(2025, 1, 1, 12, 0),
            "output_id": "projectsSummary_mock.json",
            "state": "Success",
            "output_mimetype": "application/sheet",
            "process_name": "create_projects_summary_csv",
        }
        self.mock_request.dbsession.execute.return_value.fetchall.return_value = [
            fake_row
        ]
        result = self.view.get_data_product(self.mock_request)
        self.assertEqual(result, [fake_row])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["state"], "Success")
        self.assertEqual(result[0]["product_id"], "projects_summary")


class TestSaveProjectRow(ViewBaseTest):
    view_class = SaveProjectRow

    def setUp(self):
        super().setUp()

        self.view.user.admin = 1
        self.view.user.fullName = "Test Admin"
        self.view.user.email = "admin@test.com"
        self.view.request.POST = {
            "project_id": MagicMock(str, name="project_id"),
            "affiliation": MagicMock(str, name="affiliation"),
            "crop": MagicMock(str, name="crop"),
            "analytics": MagicMock(int, name="analytics", return_value=1),
            "admin_message": MagicMock(str, name="admin_message"),
            "csrf_token": MagicMock(str, name="csrf_token"),
        }

        self.last_project_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.ProjectsSummaryCurationView.get_data_product"
        )
        self.project_id_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_project_id_row"
        )
        self.modify_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.modifyProject"
        )
        self.update_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.update_row_project_summary"
        )
        self.owner_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.getProjectUserAndOwner"
        )
        self.user_info_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.getUserInfo"
        )
        self.email_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.SaveProjectRow.send_email_notification"
        )

        self.mock_last_report = self.last_project_patcher.start()
        self.mock_get_project = self.project_id_patcher.start()
        self.mock_modify = self.modify_patcher.start()
        self.mock_update = self.update_patcher.start()
        self.mock_get_owner = self.owner_patcher.start()
        self.mock_get_user = self.user_info_patcher.start()
        self.mock_send_email = self.email_patcher.start()

        self.mock_last_report.return_value = [{"state": "Success"}]
        self.mock_get_project.return_value = {
            "psm_json": {
                "projectTitle": "Test Project",
                "affiliation": "old_affiliation",
                "climmob_analytics": None,
                "cropname": "old_crop",
                "project_checked": 0,
            }
        }
        self.mock_modify.return_value = (True, "")
        self.mock_update.return_value = (True, "")
        self.mock_get_owner.return_value = {"user_name": "test_user"}
        self.mock_get_user.return_value = {
            "user_email": "user@test.com",
            "user_fullname": "Test User",
        }
        self.mock_send_email.return_value = True

        self.addCleanup(self.mock_last_report.stop)
        self.addCleanup(self.project_id_patcher.stop)
        self.addCleanup(self.modify_patcher.stop)
        self.addCleanup(self.update_patcher.stop)
        self.addCleanup(self.owner_patcher.stop)
        self.addCleanup(self.user_info_patcher.stop)
        self.addCleanup(self.email_patcher.stop)

    def tearDown(self):
        super().tearDown()

    def test_save_row_post_state_no_success(self):
        self.mock_last_report.return_value = [{"state": "Pending..."}]
        response = self.view.post()
        self.assertEqual(
            response,
            {
                "message": "The process that updates the list of projects is currently running. Please wait a moment for it to finish.",
                "status": 409,
            },
        )
        self.mock_last_report.assert_called_once_with(self.view, self.view.request)

    def test_save_project_row_post_modify_error(self):
        self.mock_modify.return_value = (False, "This Error")
        self.mock_update.return_value = (False, "Error #1")

        response = self.view.post()

        self.assertEqual(response["status"], 400)
        self.assertIn("Error: ['This Error', 'Error #1']", response["message"])

        self.mock_get_project.assert_called_once_with(
            self.view.request, self.view.request.POST["project_id"]
        )
        self.mock_modify.assert_called_once_with(
            self.view.request.POST["project_id"],
            {
                "project_affiliation": self.view.request.POST["affiliation"],
                "climmob_analytics": self.view.request.POST["analytics"],
                "project_curated_cropname": self.view.request.POST["crop"],
                "project_checked": 1,
            },
            self.view.request,
        )
        self.mock_update.assert_called_once_with(
            {
                "psm_json": self.mock_get_project.return_value["psm_json"],
                "admin_user_name": "test_user",
                "admin_update_date": ANY,
            },
            self.view.request.POST["project_id"],
            self.view.request,
        )

    def test_save_project_row_post_success(self):
        response = self.view.post()

        self.assertEqual(response["status"], 200)
        self.assertIn("Row updated right", response["message"])

        self.mock_get_project.assert_called_once_with(
            self.view.request, self.view.request.POST["project_id"]
        )
        self.mock_modify.assert_called_once_with(
            self.view.request.POST["project_id"],
            {
                "project_affiliation": self.view.request.POST["affiliation"],
                "climmob_analytics": self.view.request.POST["analytics"],
                "project_curated_cropname": self.view.request.POST["crop"],
                "project_checked": 1,
            },
            self.view.request,
        )
        self.mock_update.assert_called_once_with(
            {
                "psm_json": self.mock_get_project.return_value["psm_json"],
                "admin_user_name": "test_user",
                "admin_update_date": ANY,
            },
            self.view.request.POST["project_id"],
            self.view.request,
        )
        self.mock_get_owner.assert_called_once_with(
            self.view.request.POST["project_id"], self.view.request
        )
        self.mock_get_user.assert_called_once_with(
            self.view.request, self.mock_get_owner.return_value["user_name"]
        )
        self.mock_send_email.assert_called_once_with(
            "Test Admin",
            "admin@test.com",
            "Test User",
            "user@test.com",
            "Test Project",
            self.view.request.POST["project_id"],
            self.view.request.POST["admin_message"],
            self.view.request.POST["crop"],
            self.view.request.POST["affiliation"],
            self.view.request.POST["analytics"],
            "old_affiliation",
            "old_crop",
        )


class TestSendEmailNotification(ViewBaseTest):
    view_class = SaveProjectRow

    def setUp(self):
        super().setUp()

        self.mocks = {
            "admin_name": MagicMock(str, name="admin_name"),
            "admin_email": MagicMock(str, name="admin_email"),
            "user_project_full_name": MagicMock(str, name="user_project_full_name"),
            "user_project_email": MagicMock(str, name="user_project_email"),
            "project_name": "project_name",
            "project_id": MagicMock(str, name="project_id"),
            "admin_message": MagicMock(str, name="admin_message"),
            "cropname": MagicMock(str, name="cropname"),
            "affiliation": MagicMock(str, name="affiliation"),
            "prev_crop": MagicMock(str, name="prev_crop"),
            "prev_affiliation": MagicMock(str, name="prev_affiliation"),
            "climmob_analytics": "1",
        }

        self.view.request = MagicMock()
        self.view.request.translate = MagicMock()
        self.view.request.registry = MagicMock()
        self.view.request.registry.settings = {
            "email.from": MagicMock(str, name="email_from"),
            "email.server": MagicMock(str, name="email_server"),
            "email.user": MagicMock(str, name="email_user"),
            "email.password": MagicMock(str, name="email_password"),
        }

        self.log_patcher = patch("climmob.views.projectsSummary.projectsSummary.log")
        self.render_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.render_template"
        )
        self.build_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.build_email_message_multiple_recipients"
        )
        self.sender_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.EmailSender"
        )

        self.mock_log = self.log_patcher.start()
        self.mock_render = self.render_patcher.start()
        self.mock_build_email = self.build_patcher.start()
        self.mock_esender = self.sender_patcher.start()

        self.mock_render.return_value = MagicMock(name="rendered_template")
        self.mock_build_email.return_value = MagicMock(name="email_message")
        self.mock_esender = MagicMock(name="email_sender")

        self.addCleanup(self.log_patcher.stop)
        self.addCleanup(self.render_patcher.stop)
        self.addCleanup(self.build_patcher.stop)
        self.addCleanup(self.sender_patcher.stop)

    def tearDown(self):
        super().tearDown()

    def test_send_email_none_registry(self):
        self.view.request.registry.settings = {}
        response = self.view.send_email_notification(**self.mocks)
        self.assertFalse(response)
        self.mock_log.error.assert_called_once_with(
            "ClimMob has no email settings in place. Email service is disabled."
        )

    def test_send_email_success(self):
        response = self.view.send_email_notification(**self.mocks)

        self.mock_render.assert_called_once_with(
            "email/curation_notification_email.jinja2",
            {
                "name_user": self.mocks["user_project_full_name"],
                "project_name": self.mocks["project_name"],
                "project_id": self.mocks["project_id"],
                "admin_name": self.mocks["admin_name"],
                "admin_email": self.mocks["admin_email"],
                "admin_message": self.mocks["admin_message"],
                "cropname": self.mocks["cropname"],
                "affiliation": self.mocks["affiliation"],
                "climmob_analytics": int(self.mocks["climmob_analytics"]),
                "prev_affiliation": self.mocks["prev_affiliation"],
                "prev_crop": self.mocks["prev_crop"],
                "_": self.view.request.translate,
            },
        )

        expected_subject = (
            f"Update on Your ClimMob Project({self.mocks['project_name']})"
        )
        self.mock_build_email.assert_called_once_with(
            self.mock_render.return_value,
            expected_subject,
            [
                (self.mocks["admin_name"], self.mocks["admin_email"]),
                (
                    self.mocks["user_project_full_name"],
                    self.mocks["user_project_email"],
                ),
            ],
            self.view.request.registry.settings["email.from"],
        )
        self.mock_log.error.assert_not_called()


class TestProjectSummaryRecentView(ViewBaseTest):
    view_class = ProjectSummaryRecentView

    def setUp(self):
        super().setUp()
        self.view.user.admin = 1

        self.last_rep = patch(
            "climmob.views.projectsSummary.projectsSummary.ProjectsSummaryCurationView.get_data_product"
        )

        self.columns_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.DataColumn.get_project_summary_columns"
        )
        self.project_summary_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_recent_project_summary"
        )
        self.affiliations_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_all_affiliations"
        )
        self.get_dict_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.DataColumn.get_dict"
        )

        self.mock_last_report = self.last_rep.start()
        self.mock_columns = self.columns_patcher.start()
        self.mock_project_summary = self.project_summary_patcher.start()
        self.mock_affiliations = self.affiliations_patcher.start()
        self.mock_get_dict = self.get_dict_patcher.start()

        self.mock_last_report.return_value = []
        self.mock_columns.return_value = {"column1": "column1"}
        self.mock_project_summary.return_value = {"data1": "data1"}
        self.mock_affiliations.return_value = {"Affiliation": "affiliation1"}
        self.mock_get_dict.return_value = {"dictColumn": "dictValue"}

        self.addCleanup(self.last_rep.stop)
        self.addCleanup(self.columns_patcher.stop)
        self.addCleanup(self.project_summary_patcher.stop)
        self.addCleanup(self.affiliations_patcher.stop)
        self.addCleanup(self.get_dict_patcher.stop)

    def tearDown(self):
        if self.mock_affiliations.called:
            self.mock_affiliations.assert_called_once_with(self.view.request)
        super().tearDown()

    def test_get(self):
        response = self.view.get()
        self.assertEqual(
            response,
            {
                "lastReport": [],
                "sectionActive": "projectsSummaryRecent",
                "table_structure":{"dictColumn": "dictValue"},
                "tableStructure": self.mock_columns.return_value,
                "listOfProjects": json.dumps(self.mock_project_summary.return_value, indent=4),
                "edit_mode": True,
                "list_of_affiliation": {"Affiliation": "affiliation1"},
            },
        )
        self.mock_last_report.assert_called_once_with(self.view, self.view.request)
        self.mock_columns.assert_called_once_with(self.view)
        self.mock_project_summary.assert_called_once_with(self.view.request)
