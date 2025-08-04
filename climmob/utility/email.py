from email import utils
from email.header import Header
from email.mime.text import MIMEText
from time import time


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
