from ast import literal_eval

from pyramid.httpexceptions import HTTPFound

from climmob.config.auth import getUserData
from climmob.views.validators.BaseValidator import BaseValidator


class NotLoggedInValidator(BaseValidator):
    def run(self):
        # If logged in then go to dashboard
        policy = self.view.get_policy("main")
        login_data = policy.authenticated_userid(self.view.request)
        if login_data is None:
            return

        login_data = literal_eval(login_data)
        if login_data["group"] != "mainApp":
            return

        current_user = getUserData(login_data["login"], self.view.request)
        if current_user is not None:
            raise HTTPFound(location=self.view.request.route_url("dashboard"))
