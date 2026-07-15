from enum import auto, IntEnum

from climmob.services.service import Service

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class NotificationService(Service):
    def __init__(self, request):
        super().__init__(request)
        self.notifier = None

    def set_notifier(self, notifier_type):
        self.notifier = notifier_type(self.request)

    def notify_publication_request(self):
        self.set_notifier(EmailNotifier)
        self.notifier.send_notification("A publication request has been made.")
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

    def send_notification(self, message):
        """"""


class EmailNotifier(Notifier):
    def __init__(self, request, template="", subject=""):
        super().__init__(request)
        self._template = template
        self._context = {}
        self._subject = subject
        self._body = ""
        self._to = ""
        self._from = self.request.registry.settings.get("email.from", None)

    def send_notification(self, message):
        # Implement the logic to send an email notification
        print(f"EmailNotifier: Sending email notification with message: {message}")
        pass


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

    def send_notification(self, message):
        # Implement the logic to send a Slack notification
        response = self.client.chat_postMessage(
            channel=self.channel,
            text="¡Hola desde mi bot de Slack!",
        )
        # TODO: Handle the response and any errors