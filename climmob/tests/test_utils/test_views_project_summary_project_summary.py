import unittest
from unittest.mock import MagicMock, call
from unittest.mock import patch

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.projectsSummary.projectsSummary import *


class TestProjectsSummaryView(ViewBaseTest):
    view_class = ProjectsSummaryView

    def test_projects_summary_view_my_converter_success(self):
        date_time = datetime.datetime(2025, 1, 1, 12, 00, 00)
        result = ProjectsSummaryView.myconverter(date_time)
        self.assertEqual(result, str(date_time))

    def test_projects_summary_view_get_data_product(self):
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

    @patch(
        "climmob.views.projectsSummary.projectsSummary.create_projects_summary",
        return_value="",
    )
    def test_projects_summary_view_post(self, mock_create_projects_summary):
        self.view.request.method = "POST"
        self.view.user.admin = 1
        self.request.POST = {"btn_generate_report": 1}
        self.view.request.route_url = MagicMock(return_value="/projectsSummary")

        response = self.view.post()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/projectsSummary")
        mock_create_projects_summary.assert_called_once_with(self.view.request)

    @patch("climmob.views.projectsSummary.projectsSummary.get_all_project_summary")
    @patch(
        "climmob.views.projectsSummary.projectsSummary.ProjectsSummaryView.get_data_product"
    )
    def test_projects_summary_view_get(
        self, mock_get_data_product, mock_get_all_project_summary
    ):
        self.view.user.admin = 1
        mock_get_data_product.return_value = [{"data": "data"}]
        mock_get_all_project_summary.return_value = {"data1": "data1"}

        result = self.view.get()

        self.assertEqual(
            result,
            {
                "listOfProjects": mock_get_all_project_summary.return_value,
                "lastReport": mock_get_data_product.return_value,
                "sectionActive": "projectssummary",
            },
        )
        mock_get_data_product.assert_called_once_with(self.view, self.view.request)
        mock_get_all_project_summary.assert_called_once_with(self.view.request)


class TestDownloadProjectsSummaryView(ViewBaseTest):
    view_class = DownloadProjectsSummaryView

    @patch("climmob.views.projectsSummary.projectsSummary.getUserInfo")
    def test_download_project_summary_view_get_no_admin(self, mock_get_user_info):
        mock_get_user_info.return_value = {
            "user_admin": 0,
        }
        with self.assertRaises(HTTPNotFound):
            self.view.get()
        mock_get_user_info.asser_called_once(self.view.request, self.view.user.login)

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

    @patch("climmob.views.projectsSummary.projectsSummary.create_json_exel_file")
    @patch("climmob.views.projectsSummary.projectsSummary.get_all_project_summary")
    def test_create_projects_summary_json_xlsx(
        self, mock_get_all_projects, mock_create_json_excel
    ):
        mock_request = MagicMock()
        mock_request.registry.settings = {
            "setting1": "value1",
            "setting2": "value2",
        }
        mock_get_all_projects.return_value = ["proj1", "proj2"]

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
            "/fake/path", "projectsSummaryTest", expected_settings, ["proj1", "proj2"]
        )


class TestProjectsSummaryCurationView(ViewBaseTest):
    view_class = ProjectsSummaryCurationView

    def setUp(self):
        super().setUp()

        self.column_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.DataColumn.get_project_summary_columns"
        )
        self.user_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_user_project_summary"
        )
        self.all_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_all_project_summary"
        )

        self.mock_get_columns = self.column_patcher.start()
        self.mock_get_user = self.user_patcher.start()
        self.mock_get_all = self.all_patcher.start()

        self.mock_get_columns.return_value = {"column1": "column1"}
        self.mock_get_user.return_value = {"data1": "data1"}
        self.mock_get_all.return_value = {"data1": "data1"}

        self.addCleanup(self.column_patcher.stop)
        self.addCleanup(self.user_patcher.stop)
        self.addCleanup(self.all_patcher.stop)

    def tearDown(self):

        if self.mock_get_columns.called:
            self.mock_get_columns.assert_called_once_with(self.view)
        if self.mock_get_user.called:
            self.mock_get_user.assert_called_once_with(
                self.view.request, self.view.user.userData["user_name"]
            )
        if self.mock_get_all.called:
            self.mock_get_all.assert_called_once_with(self.view.request)
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
                "tableStructure": {"column1": "column1"},
                "listOfProjects": {"data1": "data1"},
                "edit_mode": False,
            },
        )

    def test_projects_summary_curation_get_view_admin(self):
        self.view.user.admin = 1
        response = self.view.get()
        self.assertEqual(
            response,
            {
                "edit_mode": True,
                "tableStructure": {"column1": "column1"},
                "listOfProjects": {"data1": "data1"},
            },
        )


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

        self.mock_get_project = self.project_id_patcher.start()
        self.mock_modify = self.modify_patcher.start()
        self.mock_update = self.update_patcher.start()
        self.mock_get_owner = self.owner_patcher.start()
        self.mock_get_user = self.user_info_patcher.start()
        self.mock_send_email = self.email_patcher.start()

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

        self.addCleanup(self.project_id_patcher.stop)
        self.addCleanup(self.modify_patcher.stop)
        self.addCleanup(self.update_patcher.stop)
        self.addCleanup(self.owner_patcher.stop)
        self.addCleanup(self.user_info_patcher.stop)
        self.addCleanup(self.email_patcher.stop)

    def tearDown(self):
        super().tearDown()

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
            self.mock_get_project.return_value["psm_json"],
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
            self.mock_get_project.return_value["psm_json"],
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
        self.smtp_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.smtplib.SMTP"
        )

        self.mock_log = self.log_patcher.start()
        self.mock_render = self.render_patcher.start()
        self.mock_build_email = self.build_patcher.start()
        self.mock_smtp = self.smtp_patcher.start()

        self.mock_server = MagicMock()
        self.mock_smtp.return_value = self.mock_server

        self.mock_render.return_value = MagicMock(name="rendered_template")
        self.mock_build_email.return_value = MagicMock(name="email_message")

        self.addCleanup(self.log_patcher.stop)
        self.addCleanup(self.render_patcher.stop)
        self.addCleanup(self.build_patcher.stop)
        self.addCleanup(self.smtp_patcher.stop)

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

        self.mock_smtp.assert_called_once_with(
            self.view.request.registry.settings["email.server"], 587
        )
        self.mock_server.login.assert_called_once_with(
            self.view.request.registry.settings["email.user"],
            self.view.request.registry.settings["email.password"],
        )
        self.mock_server.sendmail.assert_called_once_with(
            self.view.request.registry.settings["email.from"],
            [self.mocks["admin_email"], self.mocks["user_project_email"]],
            self.mock_build_email.return_value.as_string(),
        )
        self.mock_server.quit.assert_called_once_with()

        self.mock_log.error.assert_not_called()

    def test_send_email_smtp_failure(self):
        self.mock_server.login.side_effect = Exception("SMTP error")
        response = self.view.send_email_notification(**self.mocks)
        self.assertFalse(response)
        self.mock_log.error.assert_called_once_with("SMTP error")


class TestProjectSummaryRecentView(ViewBaseTest):
    view_class = ProjectSummaryRecentView

    def setUp(self):
        super().setUp()
        self.view.user.admin = 1

        self.columns_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.DataColumn.get_project_summary_columns"
        )
        self.project_summary_patcher = patch(
            "climmob.views.projectsSummary.projectsSummary.get_recent_project_summary"
        )

        self.mock_columns = self.columns_patcher.start()
        self.mock_project_summary = self.project_summary_patcher.start()

        self.mock_columns.return_value = {"column1": "column1"}
        self.mock_project_summary.return_value = {"data1": "data1"}

        self.addCleanup(self.columns_patcher.stop)
        self.addCleanup(self.project_summary_patcher.stop)

    def tearDown(self):
        super().tearDown()

    def test_get(self):
        response = self.view.get()
        self.assertEqual(
            response,
            {
                "tableStructure": self.mock_columns.return_value,
                "listOfProjects": self.mock_project_summary.return_value,
                "edit_mode": True,
            },
        )
        self.mock_columns.assert_called_once_with(self.view)
        self.mock_project_summary.assert_called_once_with(self.view.request)


class TestNoAdminRedirect(unittest.TestCase):
    def test_no_admin_redirect(self):
        mock_self = MagicMock()
        mock_self.user.admin = ProjectAdmin.NO.value
        with self.assertRaises(HTTPNotFound):
            no_admin_redirect(mock_self)

    def test_no_admin_redirect_noparam(self):
        mock_self = MagicMock()
        mock_self.user.admin = None
        with self.assertRaises(HTTPNotFound):
            no_admin_redirect(mock_self)
