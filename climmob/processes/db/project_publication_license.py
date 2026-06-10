from climmob.models.climmobv4 import ProjectPublicationLicense

__all__ = [
    "save_project_publication_license",
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
