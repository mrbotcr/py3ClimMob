from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from .celerytasks import createReports


def create_analysis(locale, user, project, data, info, infosheet, request):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, user, project, "reports")
    # We call the Celery task that will generate the output packages.pdf
    task = createReports.delay(locale, path, user, project, data, info, infosheet)
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)
    registerProductInstance(
        user,
        project,
        "reports",
        "reports_" + project + ".zip",
        "application/zip",
        "reports",
        task.id,
        request,
    )
