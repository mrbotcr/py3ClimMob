from climmob.views.classes import privateView
from climmob.views.validators import (
    SectionOnlyForAdminValidator,
)
import requests
import json


class AdministratorsReportToken(privateView):
    validators = (SectionOnlyForAdminValidator,)

    def get(self):
        self.returnRawViewResult = True

        headers = {"Content-type": "application/json"}

        _json = {
            "username": self.request.registry.settings.get("analytics.username"),
            "password": self.request.registry.settings.get("analytics.password"),
            "provider": "db",
            "refresh": "true",
        }
        url = f"{self.request.registry.settings.get('analytics.supersetHost')}/api/v1/security/login"
        response = requests.post(url, data=json.dumps(_json), headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            headers["Authorization"] = "Bearer {}".format(result["access_token"])
            _json = {
                "user": {
                    "username": self.request.registry.settings.get(
                        "analytics.username", None
                    ),
                },
                "resources": [
                    {
                        "type": "dashboard",
                        "id": self.request.registry.settings.get(
                            "analytics.dashboard.users", None
                        ),
                    },
                    {
                        "type": "dashboard",
                        "id": self.request.registry.settings.get(
                            "analytics.dashboard.participants", None
                        ),
                    },
                    {
                        "type": "dashboard",
                        "id": self.request.registry.settings.get(
                            "analytics.dashboard.trials", None
                        ),
                    },
                    {
                        "type": "dashboard",
                        "id": self.request.registry.settings.get(
                            "analytics.dashboard.crops", None
                        ),
                    },
                ],
                "rls": [],
            }
            response = requests.post(
                "{}/api/v1/security/guest_token".format(
                    self.request.registry.settings.get("analytics.supersetHost", None)
                ),
                data=json.dumps(_json),
                headers=headers,
            )

            if response.status_code == 200:
                result = json.loads(response.text)

                return result["token"]

        return ""


class AdministratorsReport(privateView):
    validators = (SectionOnlyForAdminValidator,)

    def get(self):
        return {
            "sectionActive": "administratorsReport",
            "sections": [
                {
                    "name": "trials",
                    "dashboard": self.request.registry.settings.get(
                        "analytics.dashboard.trials", None
                    ),
                    "size": 1290,
                },
                {
                    "name": "users",
                    "dashboard": self.request.registry.settings.get(
                        "analytics.dashboard.users", None
                    ),
                    "size": 1030,
                },
                {
                    "name": "participants",
                    "dashboard": self.request.registry.settings.get(
                        "analytics.dashboard.participants", None
                    ),
                    "size": 1020,
                },
                {
                    "name": "crops",
                    "dashboard": self.request.registry.settings.get(
                        "analytics.dashboard.crops", None
                    ),
                    "size": 1630,
                },
            ],
        }
