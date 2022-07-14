from climmob.products.analysis.celerytasks import createReports
from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


def create_analysis(
    locale,
    userOwner,
    projectId,
    projectCod,
    data,
    info,
    infosheet,
    request,
    pathScript,
    variablesSplit,
    combinationRerence,
):
    # We create the plugin directory if it does not exists and return it
    # The path user.repository in development.ini/user/project/products/product and
    # user.repository in development.ini/user/project/products/product/outputs
    path = createProductDirectory(request, userOwner, projectCod, "reports")
    if infosheet == "TRUE":
        pathInfosheets = createProductDirectory(
            request, userOwner, projectCod, "infosheets"
        )
    else:
        pathInfosheets = ""
    # We call the Celery task that will generate the output packages.pdf
    task = createReports.apply_async(
        (
            locale,
            path,
            pathInfosheets,
            userOwner,
            projectCod,
            data,
            info,
            infosheet,
            pathScript,
            variablesSplit,
            combinationRerence,
        ),
        queue="ClimMob",
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)
    registerProductInstance(
        projectId,
        "reports",
        "Report_" + projectCod + ".docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "reports",
        task.id,
        request,
    )

    if infosheet == "TRUE":
        registerProductInstance(
            projectId,
            "infosheets",
            "Infosheets_" + projectCod + ".docx",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "infosheets",
            task.id,
            request,
            newTask=False,
        )
