from climmob.models.climmobv4 import ProjectPublishingLicense

__all__ = [
    "save_project_publishing_license",
]


def save_project_publishing_license(project_id, license_id, request):
    existing = (
        request.dbsession.query(ProjectPublishingLicense)
        .filter_by(project_id=project_id)
        .first()
    )
    if existing:
        existing.publishing_license_id = license_id
    else:
        request.dbsession.add(
            ProjectPublishingLicense(
                project_id=project_id, publishing_license_id=license_id
            )
        )
