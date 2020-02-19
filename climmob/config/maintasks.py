from climmob.config.celery_app import celeryApp
import time


@celeryApp.task
def aClimmobTask():
    time.sleep(30)
    print("aClimmobTask has finished")
