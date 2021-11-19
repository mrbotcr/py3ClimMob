from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)

from .celerytasks import createRandomization


# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_randomization(
    request, locale, userOwner, projectId, projectCod, settings,
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, userOwner, projectCod, "randomization")
    # We call the Celery task that will generate the output packages.pdf
    print("*****create_randomization. Calling createRandomization.delay ")
    task = createRandomization.apply_async(
        (locale, path, settings, projectId, userOwner, projectCod), queue="ClimMob"
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    """print("*****create_randomization. registerProductInstance ")
    registerProductInstance(
        projectId,
        "randomization",
        "packages_" + projectCod + ".pdf",
        "application/pdf",
        "create_packages",
        task.id,
        request,
    )"""
