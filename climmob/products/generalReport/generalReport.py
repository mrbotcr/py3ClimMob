from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


from .celerytasks import createGeneralReport

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_general_report(request, locale, user, project, projectDetails):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, user, project, "generalreport")
    # We call the Celery task that will generate the output packages.pdf
    task = createGeneralReport.delay(locale, user, path, project, projectDetails)
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface

    registerProductInstance(
        user,
        project,
        "generalreport",
        user+"_"+project+"_general_report.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "create_general_report",
        task.id,
        request,
    )
