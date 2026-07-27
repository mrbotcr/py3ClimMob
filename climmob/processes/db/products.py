import datetime
import os
from pathlib import Path

from climmob.models import Products, Tasks, finishedTasks

__all__ = ["addProductInstance", "deleteProducts", "product_file_exists"]

from climmob.products.climmob_products import getProductDirectory


def addProductInstance(
    projectId,
    product,
    output,
    mimeType,
    processName,
    instanceID,
    request,
    newTask=True,
):
    newInstance = Products(
        project_id=projectId,
        product_id=product,
        output_id=output,
        output_mimetype=mimeType,
        process_name=processName,
        celery_taskid=instanceID,
        datetime_added=datetime.datetime.now(),
    )
    try:
        request.dbsession.add(newInstance)
        if newTask:
            newTask = Tasks(taskid=instanceID)
            request.dbsession.add(newTask)
        return True, ""
    except Exception as e:
        return False, str(e)


def deleteProducts(request, projectId, processName="ALL"):

    if processName == "ALL":
        result = (
            request.dbsession.query(Products)
            .filter(Products.project_id == projectId)
            .all()
        )
    else:
        result = (
            request.dbsession.query(Products)
            .filter(Products.project_id == projectId)
            .filter(Products.process_name == processName)
            .all()
        )

    for product in result:
        request.dbsession.query(finishedTasks).filter(
            finishedTasks.taskid == product.celery_taskid
        ).delete()

    if processName == "ALL":
        request.dbsession.query(Products).filter(
            Products.project_id == projectId
        ).delete()
    else:
        request.dbsession.query(Products).filter(
            Products.project_id == projectId
        ).filter(Products.process_name == processName).delete()


def product_file_exists(request, owner_username, project_cod, product):
    product_directory = getProductDirectory(
        request, owner_username, project_cod, product
    )

    if product == "reports":
        product_filename = "Report_" + project_cod + ".docx"
    else:
        raise NotImplementedError

    product_directory = Path(product_directory) / "outputs" / product_filename

    return os.path.exists(product_directory)
