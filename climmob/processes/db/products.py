import datetime

from climmob.models import Products, Tasks, finishedTasks

__all__ = ["addProductInstance", "deleteProducts"]


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
