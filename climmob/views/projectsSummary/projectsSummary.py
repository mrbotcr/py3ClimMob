from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from climmob.processes import getProductData, getUserInfo
from climmob.views.classes import privateView
from climmob.products import product_found
from pyramid.response import FileResponse
import json
import os


def getDataProduct(request):

    sql = (
        "select edited.celery_taskid,edited.project_id,edited.product_id, edited.datetime_added, edited.output_id,edited.state, edited.output_mimetype, edited.output_mimetype, edited.process_name "
        "from "
        "("
        "SELECT *,'Success' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 0) "
        "UNION "
        "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid in (select taskid from finishedtasks where taskerror = 1) "
        "UNION "
        "SELECT *,'Pending...' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)<2 "
        "UNION "
        "SELECT *,'Fail.' as state  FROM products p where p.celery_taskid not in (select taskid from finishedtasks) and datediff(sysdate(),datetime_added)>=2 "
        ") "
        "as edited "
        "where edited.datetime_added = (SELECT max(datetime_added) FROM products where product_id= edited.product_id and process_name= edited.process_name) and product_id='projectssummary' order by edited.datetime_added "
    )

    products = request.dbsession.execute(sql).fetchall()

    result = []
    for qst in products:
        dct = dict(qst)
        result.append(dct)

    return result


import datetime


class projectsSummary_view(privateView):
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def processView(self):

        if self.user.admin not in [1]:
            raise HTTPNotFound()

        if self.request.method == "POST":

            if "btn_generate_report" in self.request.POST:
                create_projects_summary(self.request)
                self.returnRawViewResult = True
                return HTTPFound(
                    location=self.request.route_url(
                        "projectsSummary",
                    )
                )

        lastReport = getDataProduct(self.request)
        listOfProjects = {}

        if lastReport:
            jsonLocation = os.path.join(
                self.request.registry.settings["user.repository"], "_report"
            )
            projectsSummary = "projectsSummary"
            if os.path.exists(
                os.path.join(
                    jsonLocation,
                    "{}_{}.json".format(
                        projectsSummary,
                        self.request.registry.settings.get(
                            "analytics.instancename", ""
                        ),
                    ),
                )
            ):
                jsonFile = open(
                    os.path.join(
                        jsonLocation,
                        "{}_{}.json".format(
                            projectsSummary,
                            self.request.registry.settings.get(
                                "analytics.instancename", ""
                            ),
                        ),
                    ),
                    "r",
                )
                listOfProjects = json.loads(jsonFile.read())

        return {
            "listOfProjects": listOfProjects,
            "lastReport": lastReport,
            "sectionActive": "projectssummary",
        }


class downloadProjectsSummary_view(privateView):
    def processView(self):
        celery_taskid = self.request.matchdict["celery_taskid"]
        product_id = self.request.matchdict["product_id"]

        userInSession = getUserInfo(self.request, self.user.login)

        if userInSession["user_admin"] not in [1]:
            raise HTTPNotFound()

        dataworking = getProductData(
            None,
            celery_taskid,
            product_id,
            self.request,
        )

        product_id = dataworking["product_id"]

        if product_found(product_id):
            contentType = dataworking["output_mimetype"]
            filename = dataworking["output_id"]

            path = os.path.join(
                self.request.registry.settings["user.repository"], "_report", filename
            )

            response = FileResponse(
                path,
                request=self.request,
                content_type=contentType,
            )
            response.content_disposition = 'attachment; filename="' + filename + '"'
            self.returnRawViewResult = True
            return response

        else:
            self.returnRawViewResult = True
            return False
