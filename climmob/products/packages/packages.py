from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from .celerytasks import createPackages

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_packages_excell(request, user, project, data, tech):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, user, project, "packages")
    # We call the Celery task that will generate the output packages.pdf
    task = createPackages.delay(path, project, data, tech)
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    registerProductInstance(
        user,
        project,
        "packages",
        "packages_" + project + ".xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "create_packages",
        task.id,
        request,
    )
