from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from .celerytasks import createPackages

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_packages_excell(
    request, locale, userOwner, projectId, projectCod, data, tech
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, userOwner, projectCod, "packages")
    # We call the Celery task that will generate the output packages.pdf
    task = createPackages.apply_async(
        (locale, path, projectCod, data, tech), queue="ClimMob"
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    registerProductInstance(
        projectId,
        "packages",
        "packages_" + projectCod + ".csv",
        "text/csv",
        "create_packages",
        task.id,
        request,
    )
