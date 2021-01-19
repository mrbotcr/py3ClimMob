from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


from .celerytasks import createDataCollectionProgress

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_data_collection_progress(request, locale, user, project, projectDetails, geoInformation):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, user, project, "datacollectionprogress")
    # We call the Celery task that will generate the output packages.pdf
    task = createDataCollectionProgress.apply_async(
        (locale, user, path, project, projectDetails, geoInformation), queue="ClimMob"
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface

    registerProductInstance(
        user,
        project,
        "datacollectionprogress",
        "datacollectionprogress_" + project + ".docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "create_data_collection_progress",
        task.id,
        request,
    )
