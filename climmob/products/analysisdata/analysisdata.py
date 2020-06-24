from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from .celerytasks import create_CSV


def create_datacsv(user, project, info, request):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, user, project, "datacsv")
    # We call the Celery task that will generate the output packages.pdf
    task = create_CSV.delay(path, info, project)
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)
    registerProductInstance(
        user,
        project,
        "datacsv",
        "Information_of_the project_" + project + ".csv",
        "text/csv",
        "datacsv",
        task.id,
        request,
    )
