from ..processes import (
    addProductInstance,
    getRunningTasksByProcess,
    cancelTask,
    deleteProducts,
)
from celery.contrib.abortable import AbortableAsyncResult

__all__ = [
    "addProduct",
    "registerProductInstance",
    "product_found",
    "getProducts",
    "stopTasksByProcess",
]

_PRODUCTS = []


def product_found(name):
    for product in _PRODUCTS:
        if product["name"] == name:
            return True
    return False


def output_found(product, output):
    for p in _PRODUCTS:
        if p["name"] == product:
            for o in p["outputs"]:
                if o["filename"] == output:
                    return True
    return False


def addProduct(product):
    if not product_found(product["name"]):
        # if product["outputs"]:
        _PRODUCTS.append(product)
        # else:
        #    raise Exception("The products {} does not have outputs".format(product["name"]))
    else:
        raise Exception("Product name {} is already in use".format(product["name"]))


def registerProductInstance(
    projectId,
    product,
    output,
    mimeType,
    processName,
    instanceID,
    request,
    newTask=True,
):
    if product_found(product):
        addProductInstance(
            projectId,
            product,
            output,
            mimeType,
            processName,
            instanceID,
            request,
            newTask,
        )


def getProducts():
    return list(_PRODUCTS)


def stopTasksByProcess(request, projectId, processName="ALL"):
    tasks = getRunningTasksByProcess(request, projectId, processName)
    for task in tasks:
        print("*****stopTasksByProcess. Revoking task " + task)
        result = AbortableAsyncResult(task)
        result.abort()
        # celeryApp.control.revoke(task, terminate=False, signal=signal.SIGKILL)
        print("*****stopTasksByProcess. Cancelling task from database " + task)
        # cancelTask(request, task)

    deleteProducts(request, projectId, processName)
