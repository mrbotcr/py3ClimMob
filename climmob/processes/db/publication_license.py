from climmob.models import mapFromSchema
from climmob.models.climmobv4 import PublicationLicense

__all__ = [
    "get_publication_licenses",
]


def get_publication_licenses(request):
    return mapFromSchema(request.dbsession.query(PublicationLicense).all())
