import logging
from enum import auto, IntEnum

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from climmob.processes import getAllUserAdmin
from climmob.services.service import Service
from climmob.utility import EmailSender, EmailBuilder

log = logging.getLogger("climmob")


class NotificationService(Service):
    def __init__(self, request):
        super().__init__(request)
        self.notifier = None

    def set_notifier(self, notifier_type):
        self.notifier = notifier_type(self.request)

    def notify_publication_request(self, context: dict):
        self.set_notifier(EmailNotifier)
        self.notifier.notify_publication_request(context)
        print("NotificationService: Notifying about publication request.")

    def notify_publication_rejection(self):
        self.set_notifier(EmailNotifier)
        self.notifier.send_notification("A publication request has been rejected.")
        print("NotificationService: Notifying about publication rejection.")

    def notify_publication_success(self):
        self.set_notifier(EmailNotifier)
        self.notifier.send_notification("Publication has been performed.")
        print("NotificationService: Notifying about publication success.")

    def notify_publication_failure(self):
        self.set_notifier(SlackNotifier)
        self.notifier.send_notification("A publication request has failed.")
        print("NotificationService: Notifying about publication failure.")


class Notifier:
    def __init__(self, request):
        self.request = request

    def send_notification(self):
        """"""

    def notify_publication_request(self, context: dict):
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

    def send_notification(self):
        # Implement the logic to send a Slack notification
        response = self.client.chat_postMessage(
            channel=self.channel,
            text="¡Hola desde mi bot de Slack!",
        )
        # TODO: Handle the response and any errors
