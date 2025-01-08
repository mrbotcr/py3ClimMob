import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email import utils
import logging

log = logging.getLogger("climmob")


def send_email(
    subject, body, email_to, email_from, smtp_server, smtp_user, smtp_password
):
    """
    Envía un correo electrónico con el cuerpo y el asunto especificados.
    """
    try:
        msg = MIMEText(body.encode("utf-8"), "plain", "utf-8")
        msg["Subject"] = Header(subject.encode("utf-8"), "utf-8")
        msg["From"] = email_from
        msg["To"] = email_to
        msg["Date"] = utils.formatdate()

        with smtplib.SMTP(smtp_server, 587) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(email_from, [email_to], msg.as_string())

        return {"success": True, "message": "Email sent successfully"}
    except Exception as e:
        log.error(f"Error sending email: {str(e)}")
        return {"success": False, "message": str(e)}
