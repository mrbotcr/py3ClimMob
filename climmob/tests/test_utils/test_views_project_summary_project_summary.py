from unittest.mock import MagicMock, call
from unittest.mock import patch, mock_open

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

    def test_projects_summary_view_processView_no_admin(self):
        self.view.user.admin = None
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch(
        "climmob.views.projectsSummary.projectsSummary.create_projects_summary",
        return_value="",
    )
    def test_projects_summary_view_processView_post(self, mock_create_projects_summary):
        self.view.user.admin = 1
        self.view.request.method = "POST"
        self.request.POST = {"btn_generate_report": 1}
        self.view.request.route_url = MagicMock(return_value="/projectsSummary")

        response = self.view.processView()
        self.assertIsInstance(response, HTTPFound)
        self.assertEqual(response.location, "/projectsSummary")
        mock_create_projects_summary.assert_called_once_with(self.view.request)

    @patch(
        "climmob.views.projectsSummary.projectsSummary.open",
        new_callable=mock_open,
        read_data='{"key":"value"}',
    )
    @patch(
        "climmob.views.projectsSummary.projectsSummary.os.path.exists",
        return_value=True,
    )
    @patch("climmob.views.projectsSummary.projectsSummary.os.path.join")
    @patch(
        "climmob.views.projectsSummary.projectsSummary.ProjectsSummaryView.get_data_product"
    )
    def test_projects_summary_view_processView_success(
        self, mock_get_data_product, mock_path_join, mock_path_exists, mock_open
    ):
        self.view.user.admin = 1
        mock_get_data_product.return_value = [
            {
                "celery_taskid": "some_value_celery_task",
                "project_id": None,
                "product_id": "projects_summary",
                "datetime_added": datetime.datetime(2025, 1, 1, 12, 0),
                "output_id": "projectsSummary_mock.json",
                "state": "Success",
                "output_mimetype": "application/sheet",
                "process_name": "create_projects_summary_csv",
            }
        ]
        mock_path_join1 = "/mocked/path/_report"
        mock_path_join2 = "/mocked/path/_report/projectsSummary_mock.json"
        mock_path_join.side_effect = [mock_path_join1, mock_path_join2, mock_path_join2]
        result = self.view.processView()

        self.assertEqual(
            result,
            {
                "listOfProjects": {"key": "value"},
                "lastReport": mock_get_data_product.return_value,
                "sectionActive": "projectssummary",
                "valid_fields": (
                    TextField("project_cod"),
                    TextField("user_owner"),
                ),
            },
        )
        mock_get_data_product.assert_called_once_with(self.view, self.view.request)
        mock_path_join.assert_has_calls(
            [
                call(self.view.request.registry.settings["user.repository"], "_report"),
                call(
                    "/mocked/path/_report",
                    "{}_{}.json".format(
                        "projectsSummary",
                        self.view.request.registry.settings.get(
                            "analytics.instancename"
                        ),
                        "",
                    ),
                ),
            ]
        )
        mock_path_exists.assert_called_once_with(
            "/mocked/path/_report/projectsSummary_mock.json"
        )
        mock_open.assert_called_once_with(mock_path_join2, "r")


class TestDownloadProjectsSummaryView(ViewBaseTest):
    view_class = DownloadProjectsSummaryView

    @patch("climmob.views.projectsSummary.projectsSummary.getUserInfo")
    def test_download_project_summary_view_proces_view_no_admin(
        self, mock_get_user_info
    ):
        self.view.request.matchdict["celery_taskid"] = "some_value_celery_taskid"
        self.view.request.matchdict["product_id"] = "some_value_product_id"

        mock_get_user_info.return_value = {
            "user_admin": None,
        }
        with self.assertRaises(HTTPNotFound):
            self.view.processView()
        mock_get_user_info.asser_called_once(self.view.request, self.view.user.login)

    @patch("climmob.views.projectsSummary.projectsSummary.FileResponse")
    @patch("climmob.views.projectsSummary.projectsSummary.os.path.join")
    @patch(
        "climmob.views.projectsSummary.projectsSummary.product_found", return_value=True
    )
    @patch("climmob.views.projectsSummary.projectsSummary.getProductData")
    @patch("climmob.views.projectsSummary.projectsSummary.getUserInfo")
    def test_download_project_summary_view_proces_view_admin(
        self,
        mock_get_user_info,
        mock_get_product_data,
        mock_product_found,
        mock_join,
        mock_file_response,
    ):
        self.view.request.matchdict["celery_taskid"] = "some_value_celery_taskid"
        self.view.request.matchdict["product_id"] = "some_value_product_id"
        self.view.request.registry.settings["user.repository"] = "/mocked/path/"
        mock_get_user_info.return_value = {
            "user_admin": 1,
        }
        mock_get_product_data.return_value = {
            "product_id": "some_value_product_id",
            "output_mimetype": "application/sheet",
            "output_id": "projectsSummary_mock.json",
        }
        mock_join.return_value = "/mocked/path/_report/projectsSummary_mock.json"
        mock_response = MagicMock()
        mock_file_response.return_value = mock_response

        response = self.view.processView()
        self.assertTrue(hasattr(response, "content_disposition"))
        self.assertEqual(
            response.content_disposition,
            'attachment; filename="projectsSummary_mock.json"',
        )
        mock_get_user_info.asser_called_once(self.view.request, self.view.user.login)
        mock_get_product_data.assert_called_once_with(
            None,
            self.view.request.matchdict["celery_taskid"],
            self.view.request.matchdict["product_id"],
            self.view.request,
        )
        mock_product_found.assert_called_once_with(
            mock_get_product_data.return_value["product_id"]
        )
        mock_join.assert_called_once_with(
            self.view.request.registry.settings["user.repository"],
            "_report",
            mock_get_product_data.return_value["output_id"],
        )
        mock_file_response.assert_called_once_with(
            mock_join.return_value,
            request=self.view.request,
            content_type="application/sheet",
        )

    @patch(
        "climmob.views.projectsSummary.projectsSummary.product_found",
        return_value=False,
    )
    @patch("climmob.views.projectsSummary.projectsSummary.getProductData")
    @patch("climmob.views.projectsSummary.projectsSummary.getUserInfo")
    def test_download_project_summary_view_proces_view_admin_no_prodict(
        self,
        mock_get_user_info,
        mock_get_product_data,
        mock_product_found,
    ):
        self.view.request.matchdict["celery_taskid"] = "some_value_celery_taskid"
        self.view.request.matchdict["product_id"] = "some_value_product_id"
        self.view.request.registry.settings["user.repository"] = "/mocked/path/"
        mock_get_user_info.return_value = {
            "user_admin": 1,
        }
        mock_get_product_data.return_value = {
            "product_id": "some_value_product_id",
            "output_mimetype": "application/sheet",
            "output_id": "projectsSummary_mock.json",
        }

        response = self.view.processView()
        self.assertFalse(response)
        mock_get_user_info.asser_called_once(self.view.request, self.view.user.login)
        mock_get_product_data.assert_called_once_with(
            None,
            self.view.request.matchdict["celery_taskid"],
            self.view.request.matchdict["product_id"],
            self.view.request,
        )
        mock_product_found.assert_called_once_with(
            mock_get_product_data.return_value["product_id"]
        )


class TestProjectsSummaryCurationView(ViewBaseTest):
    view_class = ProjectsSummaryCurationView

    def test_projects_summary_curation_view_my_converter_success(self):
        date_time = datetime.datetime(2025, 1, 1, 12, 00, 00)
        result = ProjectsSummaryCurationView.myconverter(date_time)
        self.assertEqual(result, str(date_time))

    def test_projects_summary_curation_view_process_view_no_admin(self):
        self.view.user.admin = None
        with self.assertRaises(HTTPNotFound):
            self.view.processView()

    @patch("climmob.views.projectsSummary.projectsSummary.get_all_project_summary")
    @patch(
        "climmob.views.projectsSummary.projectsSummary.DataColumn.get_project_summary_columns"
    )
    def test_projects_summary_curation_view_process_view_admin(
        self, mock_get_project_summary_columns, mock_get_all_project_summary
    ):
        self.view.user.admin = 1
        mock_get_project_summary_columns.return_value = {
            "column1": "column1",
        }
        mock_get_all_project_summary.return_value = {"data1": "data1"}

        response = self.view.processView()
        self.assertEqual(
            response,
            {
                "tableStructure": mock_get_project_summary_columns.return_value,
                "listOfProjects": mock_get_all_project_summary.return_value,
            },
        )


class TestSaveProjectRow(ViewBaseTest):
    view_class = SaveProjectRow

    def setUp(self):
        super().setUp()
        self.mock_user = MagicMock()
        self.view.user = self.mock_user
        self.view.request.POST = {
            "project_id": "fake_project_id",
            "affiliation": "fake_affiliation",
            "crop": "fake_crop",
            "analytics": "1",
            "csrf_token": "fake_csrf_token",
        }
        self.data = self.view.request.POST
        self.dataworking = {
            "project_affiliation": self.data.get("affiliation"),
            "climmob_analytics": self.data.get("analytics"),
            "project_curated_cropname": self.data.get("crop"),
            "project_checked": 1,
        }

    def test_save_project_row_post_exception(self):
        self.mock_user.to_dict.side_effect = Exception("Test error")
        response = self.view.post()

        self.assertEqual(response["status"], 400)
        self.assertIn("Data Error: Test error", response["message"])

    @patch(
        "climmob.views.projectsSummary.projectsSummary.modifyProject",
        return_value=(False, "Error"),
    )
    def test_save_project_row_post_modify_error(self, mock_modify_project):
        response = self.view.post()
        self.assertEqual(response["status"], 400)
        self.assertIn("Error: Error", response["message"])
        mock_modify_project.assert_called_once_with(
            self.data.get("project_id"), self.dataworking, self.view.request
        )

    @patch(
        "climmob.views.projectsSummary.projectsSummary.modifyProject",
        return_value=(True, ""),
    )
    def test_save_project_row_post_success(self, mock_modify_project):
        response = self.view.post()
        self.assertEqual(response["status"], 200)
        self.assertIn("Row updated right", response["message"])
        mock_modify_project.assert_called_once_with(
            self.data.get("project_id"), self.dataworking, self.view.request
        )
