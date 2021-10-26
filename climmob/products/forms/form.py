from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


from .celerytasks import createDocumentForm

# This function has been declated in climmob.plugins.interfaces.IPackage#after_create_packages
def create_document_form(
    request,
    locale,
    userOwner,
    projectId,
    projectCod,
    form,
    code,
    formGroupAndQuestions,
    packages,
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, userOwner, projectCod, "documentform")
    # We call the Celery task that will generate the output packages.pdf
    task = createDocumentForm.apply_async(
        (
            locale,
            userOwner,
            path,
            projectCod,
            formGroupAndQuestions,
            form,
            code,
            packages,
        ),
        queue="ClimMob",
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    nameOutput = form + "_form"
    if code != "":
        nameOutput += "_" + code

    registerProductInstance(
        projectId,
        "documentform",
        nameOutput + "_" + projectCod + ".docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "create_from_" + form + "_" + code,
        task.id,
        request,
    )
