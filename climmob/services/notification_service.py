import logging
from enum import auto, IntEnum

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from climmob.config.auth import getUserData
from climmob.processes import getAllUserAdmin
from climmob.services.service import Service
from climmob.utility import EmailSender, EmailBuilder

log = logging.getLogger("climmob")


class NotificationService(Service):
    def __init__(self, request):
        super().__init__(request)
        self.notifier: Notifier | None = None

    def set_notifier(self, notifier_type):
        self.notifier = notifier_type(self.request)

    def notify_publication_request(self, context: dict):
        self.set_notifier(EmailNotifier)
        self.notifier.notify_publication_request(context)

    def notify_publication_rejection(self, context):
        self.set_notifier(EmailNotifier)
        self.notifier.notify_publication_rejection(context)

    def notify_publication_success(self, context: dict):
        self.set_notifier(EmailNotifier)
        self.notifier.notify_publication_success(context)

    def notify_publication_failure(self, context: dict):
        self.set_notifier(SlackNotifier)
        self.notifier.notify_publication_failure(context)


class Notifier:
    def __init__(self, request):
        self.request = request

    def send_notification(self):
        """"""

    def notify_publication_request(self, context: dict):
        """"""

    def notify_publication_rejection(self, context: dict):
        """"""

    def notify_publication_success(self, context: dict):
        """"""

    def notify_publication_failure(self, context: dict):
        """"""


class EmailNotifier(Notifier):
    def __init__(self, request, template="", subject=""):
        super().__init__(request)
        self._template = template
        self._context = {}
        self._subject = subject
        self._to: list = []
        self._from = self.request.registry.settings.get("email.from", None)
        self.sender = EmailSender(request.registry.settings)

    def send_notification(self):
        print(f"sending {self._template} as {self._subject}")
        builder = EmailBuilder(
            self.request.registry.settings,
            self._to,
            self._subject,
            self._template,
            self._context,
        )
        msg = builder.build()
        if not msg:
            return False
        recipient_emails = [user["user_email"] for user in self._to]
        self.sender.send_email(recipient_emails, msg)

    def notify_publication_request(self, context: dict):
        self._template = "email/publication/publication_request_admin.jinja2"
        self._context = context
        self._subject = (
            f'New publication request for project: {context["project"]["project_name"]}'
        )
        self._to: list = getAllUserAdmin(self.request)

        self.send_notification()

    def notify_publication_rejection(self, context: dict):
        self._template = "email/publication/publication_rejection.jinja2"
        self._context = context
        self._subject = (
            f'Publication request rejected for: {context["project"]["project_name"]}'
        )
        user = getUserData(context["project"]["owner"]["user_name"], self.request)
        self._to: list = [{"user_fullname": user.login, "user_email": user.email}]

        self.send_notification()

    def notify_publication_success(self, context: dict):
        self._template = "email/publication/publication_success.jinja2"
        self._context = context
        self._subject = (
            f'Publication completed for: {context["project"]["project_name"]}'
        )
        user = getUserData(context["project"]["owner"]["user_name"], self.request)
        self._to: list = [{"user_fullname": user.login, "user_email": user.email}]

        self.send_notification()


class EmailRecipient(IntEnum):
    ADMIN = auto()
    OWNER = auto()


class SlackNotifier(Notifier):
    channel = "#climmob-notifications"

    def __init__(self, request):
        super().__init__(request)
        self.client = WebClient(
            token=request.registry.settings.get("slack.token", None)
        )
        self.text = None
        self.blocks = None
        self.attachments = None

    def send_notification(self):
        try:
            self.client.chat_postMessage(
                channel=self.channel,
                text=self.text,
                attachments=self.attachments,
            )
        except SlackApiError as e:
            error_type = e.response["error"]
            log.error(f"Slack API Rejected Request: {error_type}")
        except Exception as e:
            log.error(f"An unexpected Python error occurred: {e}")

    def notify_publication_failure(self, context: dict):
        self.text = "Project publication failure!"
        repository_list = f"\n\t• ".join(context["repositories"])
        self.blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"Project {context['project']['owner']['user_name']}_{context['project']['project_cod']}"
                    f"({context['project']['project_id']}) "
                    f"failed to publish on the following repositories:\n\t• {repository_list}",
                },
            }
        ]
        self.attachments = [{"color": "#D00000", "blocks": self.blocks}]
        self.send_notification()
