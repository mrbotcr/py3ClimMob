from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from .celerytasks import createFieldAgentsReport

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_fieldagents_report(
    locale, request, userOwner, projectCode, projectId, fieldagents, projectDetails
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, userOwner, projectCode, "fieldagents")
    # We call the Celery task that will generate the output packages.pdf
    task = createFieldAgentsReport.apply_async(
        (locale, request.application_url, userOwner, path, projectCode, fieldagents, projectDetails),
        queue="ClimMob",
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    registerProductInstance(
        projectId,
        "fieldagents",
        "fieldagents_" + projectCode + ".pdf",
        "application/pdf",
        "create_fieldagents",
        task.id,
        request,
    )
