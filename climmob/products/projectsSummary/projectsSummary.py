from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from climmob.products.projectsSummary.celerytasks import createProjectsSummary

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_projects_summary(request):
    settings = {}
    for key, value in request.registry.settings.items():
        if isinstance(value, str):
            settings[key] = value

    # We call the Celery task that will generate the output packages.pdf
    task = createProjectsSummary.apply_async((settings, ""), queue="ClimMob")
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    registerProductInstance(
        None,
        "projectssummary",
        "projectsSummary.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "create_projectssummary_csv",
        task.id,
        request,
    )

    return ""
