import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import utils
import logging
from time import time

log = logging.getLogger("climmob")


def send_email(self, body, subject, target_name, target_email, mail_from):
    msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
    ssubject = subject
    subject = Header(ssubject.encode("utf-8"), "utf-8")
    msg["Subject"] = subject
    msg["From"] = "{} <{}>".format("ClimMob", mail_from)
    recipient = "{} <{}>".format(target_name.encode("utf-8"), target_email)
    msg["To"] = Header(recipient, "utf-8")
    msg["Date"] = utils.formatdate(time())
    try:
        smtp_server = self.request.registry.settings.get("email.server", "localhost")
        smtp_user = self.request.registry.settings.get("email.user")
        smtp_password = self.request.registry.settings.get("email.password")

        server = smtplib.SMTP(smtp_server, 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_password)
        server.sendmail(mail_from, [target_email], msg.as_string())
        server.quit()

    except Exception as e:
        print(str(e))
