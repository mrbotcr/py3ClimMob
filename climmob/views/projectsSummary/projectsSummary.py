import datetime
import json
import os

from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from pyramid.response import FileResponse

from climmob.processes import (
    getProductData,
    getUserInfo,
    modifyProject,
    get_all_project_summary,
)
from climmob.products import product_found
from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from climmob.views.classes import privateView
from climmob.views.projectsSummary.column.DataColumn import get_project_summary_columns
from climmob.views.validators import TextField


class ProjectsSummaryView(privateView):
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def get_data_product(self, request):
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

        lastReport = ProjectsSummaryView.get_data_product(self, self.request)
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

        valid_fields = (
            TextField("project_cod"),
            TextField("user_owner"),
        )

        return {
            "listOfProjects": listOfProjects,
            "lastReport": lastReport,
            "sectionActive": "projectssummary",
            "valid_fields": valid_fields,
        }


class DownloadProjectsSummaryView(privateView):
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


class ProjectsSummaryCurationView(privateView):
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def processView(self):

        if self.user.admin not in [1]:
            raise HTTPNotFound()

        table_structure = get_project_summary_columns()
        listOfProjects = get_all_project_summary(self.request)

        return {
            "tableStructure": table_structure,
            "listOfProjects": listOfProjects,
        }


def save_project_row(request):
    if request.method == "POST":
        try:
            data = request.json_body
            dataworking = {}
            project_id = data["project_id"]

            dataworking["project_affiliation"] = data.get("affiliation")
            dataworking["climmob_analytics"] = data.get("analytics")
            dataworking["project_curated_cropname"] = data.get("crop")
            dataworking["project_checked"] = 1

        except Exception as e:
            return HTTPBadRequest(json_body={"message": f"Internal Error : {str(e)}"})

        modify, message = modifyProject(project_id, dataworking, request)

        if not modify:
            return {
                "message": f"Error: {str(message)}",
                "status": 500,
            }
        else:
            return {"status": 200, "message": "Row updated right"}
