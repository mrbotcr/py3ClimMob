import os

from climmob.config.celery_app import celeryApp
from climmob.plugins.utilities import climmobCeleryTask


@celeryApp.task(base=climmobCeleryTask)
def createDataDesk(path, name, data):

    if not os.path.exists(path):
        os.makedirs(path)

    pathfinal = os.path.join(path, *["outputs", name + ".json"])

    f = open(pathfinal, "w")
    f.write(data)
    f.close()

    return ""
