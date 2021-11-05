import argparse
from pyramid.paster import get_appsettings, setup_logging
from climmob.models import get_engine, get_session_factory, get_tm_session
from climmob.models.meta import Base
import transaction
import MySQLdb
import os
import sys


def get_dump(host, user, password, db, outputPath):

    os.popen(
        "mysqldump --column-statistics=0 -h %s -u %s --password=%s %s > %s.sql"
        % (host, user, password, db, outputPath + "/db_climmob_" + db)
    )

    print("\n|| Database dumped to db_climmob_" + db + ".sql || ")


def main(raw_args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("ini_path", help="Path to ini file")
    parser.add_argument("output_path", help="Directory to write the dbs")
    args = parser.parse_args(raw_args)

    config_uri = args.ini_path
    outputPath = args.output_path

    if not os.path.isdir(outputPath):
        print("The output_path parameter must be an existing directory")
        sys.exit(1)

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, "climmob")

    connection = MySQLdb.connect(
        host=settings["odktools.mysql.host"],
        user=settings["odktools.mysql.user"],
        passwd=settings["odktools.mysql.password"],
        db=settings["odktools.mysql.db"],
    )
    cursor = connection.cursor()

    print(
        "********** Getting projects from database: "
        + settings["odktools.mysql.db"]
        + " **********"
    )

    get_dump(
        settings["odktools.mysql.host"],
        settings["odktools.mysql.user"],
        settings["odktools.mysql.password"],
        settings["odktools.mysql.db"],
        outputPath,
    )

    cursor.execute(
        "select table_name FROM information_schema.tables WHERE table_schema = '"
        + settings["odktools.mysql.db"]
        + "' AND table_name = 'user_project' LIMIT 1;"
    )
    existsTableUserProject = cursor.fetchone()

    if existsTableUserProject:
        queryProjects = "SELECT user_name, project_cod FROM user_project u, project p WHERE u.project_id = p.project_id AND u.access_type=1 order by user_name"
    else:
        queryProjects = "SELECT user_name, project_cod FROM project order by user_name"

    cursor.execute(queryProjects)
    for project in cursor.fetchall():
        queryForDatabase = (
            "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = '"
            + project[0]
            + "_"
            + project[1]
            + "'"
        )
        cursor.execute(queryForDatabase)
        if cursor.fetchone():
            get_dump(
                settings["odktools.mysql.host"],
                settings["odktools.mysql.user"],
                settings["odktools.mysql.password"],
                project[0] + "_" + project[1],
                outputPath,
            )

    connection.close()
