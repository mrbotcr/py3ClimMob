import datetime
import json
import os

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import FileResponse

from climmob.processes import (
    getProductData,
    getUserInfo,
    modifyProject,
    get_all_project_summary,
)
from climmob.processes.db.project_summary import update_row_project_summary, get_user_project_summary, \
    get_recent_project_summary, get_project_id_row
from climmob.products import product_found
from climmob.products.projectsSummary import create_json_exel_file
from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from climmob.utility.project import ProjectAdmin
from climmob.views.classes import privateView
from climmob.views.projectsSummary.column.DataColumn import DataColumn



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

    def post(self):
        no_admin_redirect_not_found(self)

        if "btn_generate_report" in self.request.POST:
            create_projects_summary(self.request)
            self.returnRawViewResult = True
            return HTTPFound(
                location=self.request.route_url(
                    "projectsSummary",
                )
            )

    def get(self):
        no_admin_redirect_not_found(self)

        lastReport = ProjectsSummaryView.get_data_product(self, self.request)
        listOfProjects = {}

        if lastReport:
            listOfProjects = get_all_project_summary(self.request)

        return {
            "listOfProjects": listOfProjects,
            "lastReport": lastReport,
            "sectionActive": "projectssummary",
        }


class DownloadProjectsSummaryView(privateView):
    def get(self):
        userInSession = getUserInfo(self.request, self.user.login)
        if userInSession["user_admin"] == ProjectAdmin.NO.value:
            raise HTTPNotFound()

        celery_taskid = self.request.matchdict["celery_taskid"]
        product_id = self.request.matchdict["product_id"]

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

            path_folder = os.path.join(self.request.registry.settings["user.repository"], "_report")

            DownloadProjectsSummaryView.create_projects_summary_json_xlsx(self, self.request, path_folder,
                                                                          process_name="projectsSummary")
            path_file = os.path.join(path_folder, filename)

            response = FileResponse(
                path_file,
                request=self.request,
                content_type=contentType,
            )

            response.content_disposition = 'attachment; filename="' + filename + '"'
            self.returnRawViewResult = True
            return response

        else:
            self.returnRawViewResult = True
            return False

    def create_projects_summary_json_xlsx(self, request, jsonLocation, process_name="projectsSummary"):
        settings = {}
        for key, value in request.registry.settings.items():
            if isinstance(value, str):
                settings[key] = value
        listOfProjects = get_all_project_summary(request)

        create_json_exel_file(jsonLocation, process_name, settings, listOfProjects)
        return


class ProjectsSummaryCurationView(privateView):
    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def get(self):
        edit_mode = False
        table_structure = DataColumn.get_project_summary_columns(self)
        if self.user.admin == ProjectAdmin.YES.value:
            edit_mode = True
            listOfProjects = get_all_project_summary(self.request)

        else:
            listOfProjects = get_user_project_summary(self.request, self.user.userData['user_name'])

        return {
            "tableStructure": table_structure,
            "listOfProjects": listOfProjects,
            "edit_mode": edit_mode,
        }


class SaveProjectRow(privateView):
    def post(self):
        no_admin_redirect_not_found(self)
        request = self.request

        try:
            data = request.POST
            project_id = data.get("project_id")
            dataworking = {
                "project_affiliation": data.get("affiliation"),
                "climmob_analytics": data.get("analytics"),
                "project_curated_cropname": data.get("crop"),
                "project_checked": 1,
            }

            # psm_json = json.loads(data.get("psm_json"))

            user_dict = self.user.to_dict() if hasattr(self.user, "to_dict") else None
            self.classResult["activeUser"] = user_dict

        except Exception as e:
            return {"status": 400, "message": f"Data Error: {str(e)}"}
        messages=[]
        error = None

        psm_json = get_project_id_row(request, project_id)["psm_json"]
        psm_json.update({
            'affiliation': data.get('affiliation'),
            'climmob_analytics': int(data.get('analytics')),
            'cropname': data.get('crop')
        })


        ##modify on the project
        modify, message = modifyProject(project_id, dataworking, request)
        if not modify:
            error = True
            messages.append(message)

        ##modify on the row of the table data
        modify_table, message = update_row_project_summary(psm_json, project_id, request)

        if not modify_table:
            error = True
            messages.append(message)

        if error:
            return {
                "message": f"Error: {str(messages)}",
                "status": 400,
            }

        return {
            "status": 200,
            "message": "Row updated right",
            "activeUser": user_dict,
        }

class ProjectSummaryRecentView(privateView):
    def get(self):
        no_admin_redirect_not_found(self)
        table_structure = DataColumn.get_project_summary_columns(self)
        listOfProjects = get_recent_project_summary(self.request)
        print(listOfProjects)
        return {
            "tableStructure": table_structure,
            "listOfProjects": listOfProjects,
            "edit_mode": True,
        }

def no_admin_redirect_not_found(self):
    if ProjectAdmin.NO.value == self.user.admin:
        raise HTTPNotFound()
