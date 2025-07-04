from climmob.processes.db.project import get_project_summary_columns
from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from pyramid.httpexceptions import HTTPFound, HTTPNotFound, HTTPBadRequest
from climmob.processes import getProductData, getUserInfo, modifyProject
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


class projectsSummaryCuration_view(privateView):
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
                success, table_structure = get_project_summary_columns(self.request)

                if not success:
                    return {
                        'message': f'Error: {table_structure}',
                        "status": 500,
                    }

                table_structure_dicts = [
                    {
                        "id": c.id,
                        "key": c.key,
                        "column_name": c.column_name,
                        "field_editable": c.field_editable,
                        "type": c.type,
                        "options": c.options,
                        "show": c.show
                    }
                    for c in table_structure
                ]

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
                    "tableStructure": table_structure_dicts,
                    "listOfProjects": listOfProjects,
                    "lastReport": lastReport,
                    "sectionActive": "projectssummary",
                }

class DownloadProjectsSummary_view(privateView):
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


def save_project_row(request):
        if request.method == "POST":
            try:
                data = request.json_body
                dataworking = {}
                project_id = data["project_id"]

                dataworking['project_affiliation'] = data.get('affiliation')
                dataworking['climmob_analytics'] = data.get('analytics')
                dataworking['project_curated_cropname'] = data.get('crop')
                dataworking['project_checked'] = 1

            except Exception as e:
                return HTTPBadRequest(json_body={'message': f'Internal Error : {str(e)}'})

            modify, message = modifyProject(project_id, dataworking, request)

            if not modify:
                return {
                    'message': f'Error: {str(message)}',
                    "status": 500,
                }
            else:
                return {
                    "status": 200,
                    'message': 'Row updated right'
                }











