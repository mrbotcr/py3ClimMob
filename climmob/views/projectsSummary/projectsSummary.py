import datetime
import json
import os
import logging
import smtplib

from pyramid.httpexceptions import HTTPFound, HTTPNotFound
from pyramid.response import FileResponse

from climmob.processes import (
    getProductData,
    getUserInfo,
    modifyProject,
    get_all_project_summary,
    update_row_project_summary,
    get_user_project_summary,
    get_recent_project_summary,
    get_project_id_row,
    getProjectUserAndOwner,
)

from climmob.products import product_found
from climmob.products.projectsSummary import create_json_exel_file
from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from climmob.utility.email import (
    build_email_message_multiple_recipients,
    render_template,
)
from climmob.utility.project import ProjectAdmin
from climmob.views.classes import privateView
from climmob.views.projectsSummary.column.DataColumn import DataColumn

log = logging.getLogger("climmob")


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
        no_admin_redirect(self)

        if "btn_generate_report" in self.request.POST:
            create_projects_summary(self.request)
            self.returnRawViewResult = True
            return HTTPFound(
                location=self.request.route_url(
                    "projectsSummary",
                )
            )

    def get(self):
        no_admin_redirect(self)

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
        if userInSession["user_admin"] != ProjectAdmin.YES.value:
            raise HTTPNotFound()
        self.returnRawViewResult = True
        celery_taskid = self.request.params.get("celery_taskid")
        product_id = self.request.params.get("product_id")

        dataworking = getProductData(
            None,
            celery_taskid,
            product_id,
            self.request,
        )

        if product_found(dataworking["product_id"]):
            contentType = dataworking["output_mimetype"]
            filename = dataworking["output_id"]

            path_folder = os.path.join(
                self.request.registry.settings["user.repository"], "_report"
            )

            self.create_projects_summary_json_xlsx(
                self.request, path_folder, process_name="projectsSummary"
            )
            path_file = os.path.join(path_folder, filename)

            response = FileResponse(
                path_file,
                request=self.request,
                content_type=contentType,
            )

            response.content_disposition = 'attachment; filename="' + filename + '"'

            return response
        else:
            return False

    def create_projects_summary_json_xlsx(
        self, request, jsonLocation, process_name="projectsSummary"
    ):
        settings = {}
        for key, value in request.registry.settings.items():
            if isinstance(value, str):
                settings[key] = value
        list_of_projects = get_all_project_summary(request)

        create_json_exel_file(jsonLocation, process_name, settings, list_of_projects)
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
            list_of_projects = get_all_project_summary(self.request)

        else:
            list_of_projects = get_user_project_summary(
                self.request, self.user.userData["user_name"]
            )

        return {
            "tableStructure": table_structure,
            "listOfProjects": list_of_projects,
            "edit_mode": edit_mode,
        }


class SaveProjectRow(privateView):
    def post(self):
        no_admin_redirect(self)
        self.returnRawViewResult = True
        request = self.request

        data = request.POST
        project_id = data.get("project_id")
        dataworking = {
            "project_affiliation": data.get("affiliation"),
            "climmob_analytics": data.get("analytics"),
            "project_curated_cropname": data.get("crop"),
            "project_checked": 1,
        }

        messages = []
        error = None

        psm_json = get_project_id_row(request, project_id)["psm_json"]
        psm_json.update(
            {
                "affiliation": data.get("affiliation"),
                "climmob_analytics": int(data.get("analytics")),
                "cropname": data.get("crop"),
                "project_checked": 1,
            }
        )

        ##modify on the project
        modify, message = modifyProject(project_id, dataworking, request)
        if not modify:
            error = True
            messages.append(message)

        ##modify on the row of the table data
        modify_table, message = update_row_project_summary(
            psm_json, project_id, request
        )

        if not modify_table:
            error = True
            messages.append(message)

        if error:
            return {
                "message": f"Error: {str(messages)}",
                "status": 400,
            }

        admin_message = data.get("admin_message")

        admin_name = self.user.fullName
        admin_email = self.user.email
        user_project_name = getProjectUserAndOwner(project_id, self.request)[
            "user_name"
        ]
        user_project = getUserInfo(self.request, user_project_name)
        user_project_email = user_project["user_email"]
        user_project_full_name = user_project["user_fullname"]
        project_name = psm_json["projectTitle"]

        self.send_email_notification(
            admin_name,
            admin_email,
            user_project_full_name,
            user_project_email,
            project_name,
            project_id,
            admin_message,
            dataworking["project_curated_cropname"],
            dataworking["project_affiliation"],
        )

        return {
            "status": 200,
            "message": "Row updated right",
        }

    def send_email_notification(
        self,
        admin_name,
        admin_email,
        user_project_full_name,
        user_project_email,
        project_name,
        project_id,
        admin_message,
        cropname,
        affiliation,
    ):
        _ = self.request.translate
        mail_from = self.request.registry.settings.get("email.from", None)
        if mail_from is None:
            log.error(
                "ClimMob has no email settings in place. Email service is disabled."
            )
            return False

        recipients = [
            (admin_name, admin_email),
            (user_project_full_name, user_project_email),
        ]
        subject = "Update on Your Climmob Project(" + project_name + ")"
        text = render_template(
            "email/curation_notification_email.jinja2",
            {
                "name_user": user_project_full_name,
                "project_name": project_name,
                "project_id": project_id,
                "admin_name": admin_name,
                "admin_email": admin_email,
                "admin_message": admin_message,
                "cropname": cropname,
                "affiliation": affiliation,
                "_": _,
            },
        )

        msg = build_email_message_multiple_recipients(
            text, subject, recipients, mail_from
        )
        try:

            smtp_server = self.request.registry.settings.get(
                "email.server", "localhost"
            )
            smtp_user = self.request.registry.settings.get("email.user")
            smtp_password = self.request.registry.settings.get("email.password")

            server = smtplib.SMTP(smtp_server, 587)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_user, smtp_password)
            recipient_emails = [email for _, email in recipients]
            server.sendmail(mail_from, recipient_emails, msg.as_string())
            server.quit()

        except Exception as e:
            log.error(str(e))


class ProjectSummaryRecentView(privateView):
    def get(self):
        no_admin_redirect(self)
        table_structure = DataColumn.get_project_summary_columns(self)
        list_of_projects = get_recent_project_summary(self.request)

        return {
            "tableStructure": table_structure,
            "listOfProjects": list_of_projects,
            "edit_mode": True,
        }


def no_admin_redirect(self):
    if ProjectAdmin.YES.value != self.user.admin:
        raise HTTPNotFound()
