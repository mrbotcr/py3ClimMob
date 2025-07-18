import climmob.plugins as p
from climmob.processes import (
    registryHaveQuestionOfMultimediaType,
    assessmentHaveQuestionOfMultimediaType,
)
from climmob.products.analysisdata.celerytasks import create_raw_data_file
from climmob.products.climmob_products import (
    createProductDirectory,
    registerProductInstance,
)


def create_raw_data(userOwner, projectId, projectCod, info, request, form, code, file_type="csv", anonymized=False):
    # We create the plugin directory if it does not exists and return it
    extra = "-anonymized" if anonymized else ""

    name_output = form + f"_data{extra}"
    if code != "":
        name_output += "_" + code

    name_output += "_" + projectCod

    path = createProductDirectory(request, userOwner, projectCod, f"data{file_type}{extra}")
    # We call the Celery task that will generate the output packages.pdf
    task = create_raw_data_file.apply_async((path, info, name_output, file_type), queue="ClimMob")
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)

    mimetypes = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }
    mimetype = mimetypes.get(file_type)

    process_name = f"create_data{extra}_{'xlsx_' if file_type == 'xlsx' else ''}" + form + "_" + code

    registerProductInstance(
        projectId,
        f"data{file_type}{extra}",
        name_output + f".{file_type}",
        mimetype,
        process_name,
        task.id,
        request,
    )

    for plugin in p.PluginImplementations(p.IMultimedia):
        thereAreMultimedia = False
        if form == "Registration":
            thereAreMultimedia = registryHaveQuestionOfMultimediaType(
                request, projectId
            )

        if form == "Assessment":
            thereAreMultimedia = assessmentHaveQuestionOfMultimediaType(
                request, projectId, code
            )

        if thereAreMultimedia:
            plugin.start_multimedia_download(
                request, userOwner, projectId, projectCod, form, code
            )
