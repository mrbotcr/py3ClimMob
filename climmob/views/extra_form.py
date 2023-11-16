from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from climmob.views.classes import privateView
from climmob.processes import getActiveForm, addExtraFormAnswers
import datetime


class extraFormPOST_view(privateView):
    def processView(self):

        if self.request.method == "POST":
            dataworking = self.getPostDict()

            del dataworking["csrf_token"]

            hasActiveForm, formDetails = getActiveForm(self.request, self.user.login)

            if hasActiveForm:
                for field in dataworking.keys():
                    info = {}
                    info["form_id"] = formDetails["form_id"]
                    info["user_name"] = self.user.login
                    info["answer_field"] = field
                    info["answer_date"] = datetime.datetime.now()
                    info["answer_data"] = dataworking[field]

                    added, message = addExtraFormAnswers(info, self.request)

                self.returnRawViewResult = True
                return HTTPFound(location=self.request.route_url("dashboard"))

        raise HTTPNotFound
