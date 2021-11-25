from sqlalchemy import create_engine
from climmob.config.celery_app import get_ini_value
from sqlalchemy.pool import NullPool
from celery.contrib.abortable import AbortableTask


class celeryTask(AbortableTask):
    def on_success(self, retval, task_id, args, kwargs):
        engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
        connection = engine.connect()
        connection.execute(
            "INSERT INTO finishedtasks(taskid,taskerror) VALUES ('"
            + str(task_id)
            + "',0)"
        )
        connection.invalidate()
        engine.dispose()

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
        engine.execute(
            "INSERT INTO finishedtasks(taskid,taskerror) VALUES ('"
            + str(task_id)
            + "',1)"
        )
        engine.dispose()
