from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)
from climmob.products.qrpackages.celerytasks import createQR


# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_qr_packages(
    request, locale, userOwner, projectId, projectCod, options, packages
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, userOwner, projectCod, "qrpackage")
    # We call the Celery task that will generate the output packages.pdf
    print("*****create_qr_packages. Calling createQR.delay ")
    task = createQR.apply_async((locale, path, projectCod, packages), queue="ClimMob")
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    print("*****create_qr_packages. registerProductInstance ")
    registerProductInstance(
        projectId,
        "qrpackage",
        "packages_" + projectCod + ".pdf",
        "application/pdf",
        "create_packages",
        task.id,
        request,
    )
