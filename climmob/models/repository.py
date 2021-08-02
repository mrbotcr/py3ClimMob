from sqlalchemy import create_engine
from climmob.config.celery_app import get_ini_value
from sqlalchemy.pool import NullPool

def sql_fetch_one(sql):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res = connection.execute(sql).fetchone()
    connection.invalidate()
    engine.dispose()
    return res


def sql_fetch_all(sql):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res = connection.execute(sql).fetchall()
    connection.invalidate()
    engine.dispose()
    return res


def sql_execute(sql):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res = connection.execute(sql)
    connection.invalidate()
    engine.dispose()
    return res
