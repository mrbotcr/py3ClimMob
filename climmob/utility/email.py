import smtplib
from email import utils
from email.header import Header
from email.mime.text import MIMEText
from time import time
import logging

from climmob.config.jinja_extensions import jinjaEnv

log = logging.getLogger("climmob")

__all__ = [
    "render_template",
    "build_email_message",
    "build_email_message_multiple_recipients",
    "EmailSender",
]


def render_template(template_filename, context):
    return jinjaEnv.get_template(template_filename).render(context)


def build_email_message(body, subject, target_name, target_email, mail_from):
    msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
    ssubject = subject
    subject = Header(ssubject.encode("utf-8"), "utf-8")
    msg["Subject"] = subject
    msg["From"] = "{} <{}>".format("ClimMob", mail_from)
    recipient = "{} <{}>".format(target_name.encode("utf-8"), target_email)
    msg["To"] = Header(recipient, "utf-8")
    msg["Date"] = utils.formatdate(time())

    return msg


def build_email_message_multiple_recipients(body, subject, recipients, mail_from):
    """
    recipients: List of tuples: [(name1, email1), (name2, email2), ...]
    """
    msg = MIMEText(body.encode("utf-8"), "html", "utf-8")
    msg["Subject"] = Header(subject.encode("utf-8"), "utf-8")
    msg["From"] = "ClimMob <{}>".format(mail_from)

    to_header = ", ".join(["{} <{}>".format(name, email) for name, email in recipients])
    msg["To"] = to_header
    msg["Date"] = utils.formatdate(time())

    return msg


class EmailSender:
    def __init__(self, settings):
        self.smtp_server = settings.get("email.server", "localhost")
        self.smtp_port = int(settings.get("email.port", 587))
        self.smtp_user = settings.get("email.user")
        self.smtp_password = settings.get("email.password")
        self.default_sender = settings.get("email.default_sender", self.smtp_user)

    def send_email(self, to_email, msg):
        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.smtp_user, self.smtp_password)
            server.sendmail(self.default_sender, to_email, msg.as_string())
            server.quit()
        except Exception as e:
            log.error(str(e))
