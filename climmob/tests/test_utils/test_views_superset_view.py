import json
from unittest.mock import patch, Mock, MagicMock

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.superset_view import AdministratorsReportToken, AdministratorsReport


def make_response(status, body_dict):
    r = Mock()
    r.status_code = status
    r.text = json.dumps(body_dict)
    return r


class TestAdministratorsReportToken(ViewBaseTest):
    view_class = AdministratorsReportToken

    def setUp(self):
        super().setUp()
        self.request.registry.settings = dict(self.request.registry.settings)
        settings = self.request.registry.settings
        settings["analytics.username"] = "123test123test"
        settings["analytics.password"] = "passpasspass"
        settings["analytics.supersetHost"] = "http://SuperHost"
        settings["analytics.dashboard.users"] = "DashboardUsers"
        settings["analytics.dashboard.participants"] = "DashboardParticipants"
        settings["analytics.dashboard.trials"] = "DashboardTrials"
        settings["analytics.dashboard.crops"] = "DashboardCrops"

        self.post_patch = patch("climmob.views.superset_view.requests.post")
        self.post_mock = self.post_patch.start()

        self.resp_login_ok = make_response(200, {"access_token": "token1"})
        self.resp_token_ok = make_response(200, {"token": "token2"})
        self.resp_login_fail = make_response(400, {"error": "invalid"})

        self.post_mock.side_effect = [self.resp_login_ok, self.resp_token_ok]

        self.addCleanup(self.post_patch.stop)

    def test_get_success(self):
        response = self.view.get()
        self.assertEqual(response, "token2")
        self.assertEqual(self.post_mock.call_count, 2)
        first_call = self.post_mock.call_args_list[0]
        second_call = self.post_mock.call_args_list[1]

        expected_json_1 = {
            "username": self.request.registry.settings["analytics.username"],
            "password": self.request.registry.settings["analytics.password"],
            "provider": "db",
            "refresh": "true",
        }
        self.assertEqual(json.loads(first_call.kwargs["data"]), expected_json_1)

        expected_json_2 = {
            "user": {
                "username": self.request.registry.settings["analytics.username"],
            },
            "resources": [
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings["analytics.dashboard.users"],
                },
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings[
                        "analytics.dashboard.participants"
                    ],
                },
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings["analytics.dashboard.trials"],
                },
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings["analytics.dashboard.crops"],
                },
            ],
            "rls": [],
        }
        self.assertEqual(json.loads(second_call.kwargs["data"]), expected_json_2)

    def test_get_fail_first_call(self):
        self.post_mock.side_effect = [self.resp_login_fail]
        response = self.view.get()
        self.assertEqual(response, "")
        self.assertEqual(self.post_mock.call_count, 1)
        first_call = self.post_mock.call_args_list[0]
        expected_json_1 = {
            "username": self.request.registry.settings["analytics.username"],
            "password": self.request.registry.settings["analytics.password"],
            "provider": "db",
            "refresh": "true",
        }
        self.assertEqual(json.loads(first_call.kwargs["data"]), expected_json_1)

    def test_get_fail_second_call(self):
        self.post_mock.side_effect = [self.resp_login_ok, self.resp_login_fail]
        response = self.view.get()
        self.assertEqual(response, "")
        self.assertEqual(self.post_mock.call_count, 2)
        first_call = self.post_mock.call_args_list[0]
        second_call = self.post_mock.call_args_list[1]
        expected_json_1 = {
            "username": self.request.registry.settings["analytics.username"],
            "password": self.request.registry.settings["analytics.password"],
            "provider": "db",
            "refresh": "true",
        }
        self.assertEqual(json.loads(first_call.kwargs["data"]), expected_json_1)
        expected_json_2 = {
            "user": {
                "username": self.request.registry.settings["analytics.username"],
            },
            "resources": [
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings["analytics.dashboard.users"],
                },
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings[
                        "analytics.dashboard.participants"
                    ],
                },
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings["analytics.dashboard.trials"],
                },
                {
                    "type": "dashboard",
                    "id": self.request.registry.settings["analytics.dashboard.crops"],
                },
            ],
            "rls": [],
        }
        self.assertEqual(json.loads(second_call.kwargs["data"]), expected_json_2)


class TestAdministratorsReport(ViewBaseTest):
    view_class = AdministratorsReport

    def setUp(self):
        self.maxDiff = None
        super().setUp()
        self.request.registry.settings = dict(self.request.registry.settings)
        settings = self.request.registry.settings
        settings["analytics.dashboard.users"] = "DashboardUsers"
        settings["analytics.dashboard.participants"] = "DashboardParticipants"
        settings["analytics.dashboard.trials"] = "DashboardTrials"
        settings["analytics.dashboard.crops"] = "DashboardCrops"

    def test_get_view(self):
        response = self.view.get()
        expected = {
            "sectionActive": "administratorsReport",
            "sections": [
                {"name": "trials", "dashboard": "DashboardTrials", "size": 1290},
                {"name": "users", "dashboard": "DashboardUsers", "size": 1030},
                {
                    "name": "participants",
                    "dashboard": "DashboardParticipants",
                    "size": 1020,
                },
                {"name": "crops", "dashboard": "DashboardCrops", "size": 1630},
            ],
        }
        self.assertEqual(response, expected)
