from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


from .celerytasks import createErrorLogDocument

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_error_log_document(
    request, locale,user, project, form, code, structure, listOfErrors, info
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs

    path = createProductDirectory(request, user, project, "errorlogdocument")
    # We call the Celery task that will generate the output packages.pdf
    task = createErrorLogDocument.apply_async(
        (locale, user, path, project, form, code, structure, listOfErrors, info),
        queue="ClimMob",
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    nameOutput = form + "_form"
    if code != "":
        nameOutput += "_" + code

    registerProductInstance(
        user,
        project,
        "errorlogdocument",
        nameOutput + "_" + project + ".xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "create_errorlog_" + form + "_" + code,
        task.id,
        request,
    )
