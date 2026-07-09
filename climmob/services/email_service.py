import datetime
import logging
from typing import TypedDict

from climmob.config.auth import User
from climmob.processes import getAllUserAdmin, get_collaborators_in_project
from climmob.utility.email import EmailSender, EmailBuilder

log = logging.getLogger("climmob")


class EmailRecipient(TypedDict):
    user_fullname: str
    user_email: str


class EmailService:
    def __init__(self, request):
        self.request = request
        self.settings = request.registry.settings
        self.sender = EmailSender(self.settings)
        self._ = self.request.translate

    def _send_email(self, email_builder: EmailBuilder):
        """
        Sends an email using the provided EmailBuilder instance.
        """
        mail_from = self.settings.get("email.from", None)
        if mail_from is None:
            log.error(
                "ClimMob has no email settings in place. Email service is disabled."
            )
            return False

        msg = email_builder.build()
        if not msg:
            return False

        try:
            recipient_emails = [email for _, email in email_builder._recipients]
            self.sender.send_email(recipient_emails, msg)
            return True
        except Exception as e:
            log.error(f"Error sending email: {e}")
            return False

    def send_project_closed_notification(self, project_info):
        """
        Sends a notification to admins when a project is closed.
        """
        admin_users = getAllUserAdmin(self.request)
        if not admin_users:
            log.warning("Email didn't send. No admin recipients found.")
            return False

        subject = f"✅ Project {project_info['project_cod']} has been closed"
        link = self.request.route_url("projectsSummaryRecent")
        logo = self.request.url_for_static("landing/climmob2.png")

        email_builder = (
            EmailBuilder(self.settings)
            .recipients(admin_users)
            .subject(subject)
            .template("email/close_project.jinja2")
            .context(
                {
                    "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "project_info": project_info,
                    "_": self._,
                    "link": link,
                    "logo": logo,
                }
            )
        )
        return self._send_email(email_builder)

    def send_project_closed_collaborators_notification(self, project_info):
        """
        Sends a notification to project collaborators when a project is closed.
        """
        related_collaborators = get_collaborators_in_project(
            self.request, project_info["project_id"]
        )
        recipients = []
        collaborators = []
        for collaborator in related_collaborators:
            if collaborator["access_type"] == 1:
                recipients.append(
                    (collaborator["user_fullname"], collaborator["user_email"])
                )
            else:
                collaborators.append(collaborator)

        if not recipients:
            log.warning("Email didn't send. No collaborator recipients found.")
            return False

        subject = f"Project {project_info['project_cod']} has been closed"
        logo = self.request.url_for_static("landing/climmob2.png")

        email_builder = (
            EmailBuilder(self.settings)
            .recipients(recipients)
            .subject(subject)
            .template("email/close_project_participants_registration.jinja2")
            .context(
                {
                    "project_info": project_info,
                    "_": self._,
                    "logo": logo,
                    "collaborators": collaborators,
                }
            )
        )
        return self._send_email(email_builder)

    def send_publication_request_notification(self, project, user_owner: User):
        """
        Sends a notification to admins and the project owner for a publication request.
        """
        admin_users = getAllUserAdmin(self.request)
        project_cod = project["project_cod"]
        link = self.request.route_url(
            "project_publish", project=project_cod, user=user_owner.login
        )
        logo = self.request.url_for_static("landing/climmob2.png")
        context = {
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_info": project,
            "_": self._,
            "link": link,
            "logo": logo,
        }

        # Send to admins
        admin_email_builder = (
            EmailBuilder(self.settings)
            .recipients(admin_users)
            .subject(f"Publication request for {project_cod}")
            .template("email/publication_request.jinja2")
            .context(context)
        )
        self._send_email(admin_email_builder)

        # Send to owner
        owner_recipients = [
            {"user_fullname": user_owner.login, "user_email": user_owner.email}
        ]
        owner_email_builder = (
            EmailBuilder(self.settings)
            .recipients(owner_recipients)
            .subject(f"YOU. Publication request for {project_cod}")
            .template("email/publication_request.jinja2")
            .context(context)
        )
        self._send_email(owner_email_builder)
