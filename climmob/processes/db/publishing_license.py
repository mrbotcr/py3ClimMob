from climmob.models import mapFromSchema
from climmob.models.climmobv4 import PublishingLicense

__all__ = [
    "get_publishing_licenses",
]


def get_publishing_licenses(request):
    return mapFromSchema(request.dbsession.query(PublishingLicense).all())
