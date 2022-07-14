import time

from climmob.config.celery_app import celeryApp


@celeryApp.task
def aClimmobTask():
    time.sleep(30)
    print("aClimmobTask has finished")
