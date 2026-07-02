from climmob.models.climmobv4 import ProjectPublicationLicense

__all__ = [
    "save_project_publication_license",
    "get_project_publication_license_id",
]


def save_project_publication_license(project_id, license_id, request):
    existing = (
        request.dbsession.query(ProjectPublicationLicense)
        .filter_by(project_id=project_id)
        .first()
    )
    if existing:
        existing.publication_license_id = license_id
    else:
        request.dbsession.add(
            ProjectPublicationLicense(
                project_id=project_id, publication_license_id=license_id
            )
        )


def get_project_publication_license_id(project_id, request):
    license = (
        request.dbsession.query(ProjectPublicationLicense.publication_license_id)
        .filter_by(project_id=project_id)
        .first()
    )
    if license:
        return license[0]
    return None
