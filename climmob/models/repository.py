from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from climmob.config.celery_app import get_ini_value


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


def execute_two_sqls(sql1, sql2):
    engine = create_engine(get_ini_value("sqlalchemy.url"), poolclass=NullPool)
    connection = engine.connect()
    res1 = connection.execute(sql1)
    res2 = connection.execute(sql2)
    connection.invalidate()
    engine.dispose()
    return res2
