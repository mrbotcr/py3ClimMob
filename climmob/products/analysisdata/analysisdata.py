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
from climmob.utility import get_settings


def create_raw_data(
    user_owner,
    project_id,
    project_cod,
    result_params,
    request,
    form,
    code,
    file_type="csv",
    anonymized=False,
    start_anonymization=False,
):
    # We create the plugin directory if it does not exists and return it
    extra = "-anonymized" if anonymized else ""

    file_name = form + f"_data{extra}"
    if code != "":
        file_name += "_" + code

    file_name += "_" + project_cod

    product_path = createProductDirectory(
        request, user_owner, project_cod, f"data{file_type}{extra}"
    )
    # We call the Celery task that will generate the output packages.pdf
    settings = get_settings(request)
    request_attrs = {
        "settings": settings,
        "locale_name": request.locale_name,
        "user_in_session": request.user_in_session,
    }
    file = {
        "product_path": product_path,
        "name": file_name,
        "type": file_type,
    }
    task = create_raw_data_file.apply_async(
        (request_attrs, project_id, file, result_params, start_anonymization),
        queue="ClimMob",
    )
    # We register the instance of the output with the task ID of celery
    # This will go to the products table that then you can monitor and use
    # in the nice product interface
    # u.registerProductInstance(user, project, 'cards', 'cards.pdf', task.id, request)

    mimetypes = {
        "csv": "text/csv",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    mimetype = mimetypes.get(file_type)

    process_name = (
        f"create_data{extra}_"
        f"{'xlsx_' if file_type == 'xlsx' else ''}" + form + "_" + code
    )

    registerProductInstance(
        project_id,
        f"data{file_type}{extra}",
        file_name + f".{file_type}",
        mimetype,
        process_name,
        task.id,
        request,
    )

    for plugin in p.PluginImplementations(p.IMultimedia):
        there_are_multimedia = False
        if form == "Registration":
            there_are_multimedia = registryHaveQuestionOfMultimediaType(
                request, project_id
            )

        if form == "Assessment":
            there_are_multimedia = assessmentHaveQuestionOfMultimediaType(
                request, project_id, code
            )

        if there_are_multimedia:
            plugin.start_multimedia_download(
                request, user_owner, project_id, project_cod, form, code
            )
