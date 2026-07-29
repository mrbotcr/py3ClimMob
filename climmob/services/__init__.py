from climmob.services.service import Service
from climmob.services.publication_service import PublicationService
from climmob.services.notification_service import NotificationService


def notification_factory(context, request):
    return NotificationService(request)


def publication_factory(context, request):
    return PublicationService(request)
