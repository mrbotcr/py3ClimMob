import datetime
import logging
import os
import smtplib
import json

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
    get_published_project_summary,
    get_project_id_row,
    getProjectUserAndOwner,
    get_all_affiliations,
)
from climmob.products import product_found
from climmob.products.projectsSummary import (
    create_json_exel_file,
    process_with_project_for_analytics,
)
from climmob.products.projectsSummary.projectsSummary import create_projects_summary
from climmob.utility.email import (
    build_email_message_multiple_recipients,
    render_template,
)
from climmob.utility.project import ProjectAdmin
from climmob.views.classes import privateView
from climmob.views.projectsSummary.column.DataColumn import DataColumn
from climmob.views.basic_views import EmailSender
from climmob.views.validators import (
    SectionOnlyForAdminValidator,
    SectionOnlyForAdminJsonValidator,
)

log = logging.getLogger("climmob")


class DownloadProjectsSummaryView(privateView):
    validators = (SectionOnlyForAdminValidator,)

    def get(self):

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

        column_order = DataColumn.get_key_project_summary(self)

        create_json_exel_file(
            jsonLocation,
            process_name,
            settings,
            list_of_projects,
            column_order=column_order,
        )
        return


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.__str__()


class ProjectsSummaryCurationView(privateView):
    validators = (SectionOnlyForAdminValidator,)

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

        if "btn_generate_report" in self.request.POST:
            create_projects_summary(self.request)
            self.returnRawViewResult = True
            return HTTPFound(
                location=self.request.route_url(
                    "projectsSummaryCuration",
                )
            )

    def myconverter(o):
        if isinstance(o, datetime.datetime):
            return o.__str__()

    def get(self):

        lastReport = self.get_data_product(self.request)

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
            "table_structure": DataColumn.get_dict(self),
            "tableStructure": table_structure,
            "listOfProjects": json.dumps(
                list_of_projects, cls=DateTimeEncoder, indent=4
            ),
            "lastReport": lastReport,
            "edit_mode": edit_mode,
            "sectionActive": "projectsSummaryCuration",
            "list_of_affiliation": get_all_affiliations(self.request),
        }


class SaveProjectRow(privateView):
    validators = (SectionOnlyForAdminJsonValidator,)

    def post(self):
        self.returnRawViewResult = True

        lastReport = ProjectsSummaryCurationView.get_data_product(self, self.request)

        if lastReport:
            if lastReport[0]["state"] != "Success":
                return {
                    "message": self._(
                        "The process that updates the list of projects is currently running. Please wait a moment for it to finish."
                    ),
                    "status": 409,
                }

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

        admin_message = data.get("admin_message")

        admin_name = self.user.fullName
        admin_email = self.user.email

        psm_json = get_project_id_row(request, project_id)["psm_json"]
        prev_affiliation = psm_json["affiliation"]
        prev_crop = psm_json["cropname"]
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

        data_row = {}
        data_row["psm_json"] = psm_json
        data_row["admin_user_name"] = self.user.login
        data_row["admin_update_date"] = datetime.datetime.now()

        ##modify on the row of the table data
        modify_table, message = update_row_project_summary(
            data_row, project_id, request
        )

        if not modify_table:
            error = True
            messages.append(message)

        if error:
            return {
                "message": f"Error: {str(messages)}",
                "status": 400,
            }

        if self.request.registry.settings.get("analytics.active", "false") == "true":
            if self.request.registry.settings.get(
                "analytics.sqlalchemy.url", ""
            ) != self.request.registry.settings.get("sqlalchemy.url"):
                process_with_project_for_analytics(
                    self.request.registry.settings, psm_json
                )

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
            dataworking["climmob_analytics"],
            prev_affiliation,
            prev_crop,
        )

        return {
            "status": 200,
            "message": self._(f"Changes saved for project: {project_name}"),
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
        climmob_analytics,
        prev_affiliation,
        prev_crop,
    ):
        _ = self.request.translate
        mail_from = self.request.registry.settings.get("email.from", None)
        if mail_from is None:
            log.error(
                "ClimMob has no email settings in place. Email service is disabled."
            )
            return False

        recipients = [(admin_name, admin_email)]

        if (
            self.request.registry.settings.get("email.projectsummary", "false")
            == "true"
        ):
            recipients.append((user_project_full_name, user_project_email))

        subject = "Update on Your ClimMob Project(" + project_name + ")"
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
                "climmob_analytics": int(climmob_analytics),
                "prev_affiliation": prev_affiliation,
                "prev_crop": prev_crop,
                "_": _,
            },
        )

        msg = build_email_message_multiple_recipients(
            text, subject, recipients, mail_from
        )

        recipient_emails = [email for _, email in recipients]

        email_sender = EmailSender(self.request.registry.settings)
        email_sender.send_email(recipient_emails, msg)


class ProjectSummaryRecentView(privateView):
    validators = (SectionOnlyForAdminValidator,)

    def get(self):
        lastReport = ProjectsSummaryCurationView.get_data_product(self, self.request)
        table_structure = DataColumn.get_project_summary_columns(self)
        list_of_projects = get_recent_project_summary(self.request)

        return {
            "table_structure": DataColumn.get_dict(self),
            "lastReport": lastReport,
            "tableStructure": table_structure,
            "listOfProjects": json.dumps(
                list_of_projects, cls=DateTimeEncoder, indent=4
            ),
            "edit_mode": True,
            "sectionActive": "projectsSummaryRecent",
            "list_of_affiliation": get_all_affiliations(self.request),
        }


class ProjectSummaryPublishedView(privateView):
    validators = (SectionOnlyForAdminValidator,)

    def get(self):
        lastReport = ProjectsSummaryCurationView.get_data_product(self, self.request)
        table_structure = DataColumn.get_project_summary_columns(self)
        list_of_projects = get_published_project_summary(self.request)

        return {
            "table_structure": DataColumn.get_dict(self),
            "lastReport": lastReport,
            "tableStructure": table_structure,
            "listOfProjects": json.dumps(
                list_of_projects, cls=DateTimeEncoder, indent=4
            ),
            "edit_mode": True,
            "sectionActive": "projectsSummaryPublished",
            "list_of_affiliation": get_all_affiliations(self.request),
        }
