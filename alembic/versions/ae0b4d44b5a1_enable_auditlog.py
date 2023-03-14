"""Enable Auditlog

Revision ID: ae0b4d44b5a1
Revises: faee167e183a
Create Date: 2023-01-26 14:21:39.045300

"""
import os
from alembic import op
from subprocess import Popen, PIPE
from lxml import etree
from alembic import context
from pyramid.paster import get_appsettings, setup_logging
from sqlalchemy.orm.session import Session
from climmob.models.climmobv4 import Project, userProject, Assessment
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

# revision identifiers, used by Alembic.
revision = "ae0b4d44b5a1"
down_revision = "faee167e183a"
branch_labels = None
depends_on = None


def functionForCreateTheTriggers(
    schema, create_xml_file, settings, create_file, form_repository_path, my_cnf_file
):

    if os.path.exists(create_xml_file):

        parser = etree.XMLParser(remove_blank_text=True)
        tree_create = etree.parse(create_xml_file, parser)
        root_create = tree_create.getroot()
        tables = root_create.findall(".//table")
        table_array = []
        if tables:
            for a_table in tables:
                table_array.append(a_table.get("name"))

        create_audit_triggers = os.path.join(
            settings["odktools.path"],
            *["utilities", "createAuditTriggers", "createaudittriggers"]
        )

        args = [
            create_audit_triggers,
            "-H " + settings.get("odktools.mysql.host"),
            "-P " + settings.get("odktools.mysql.port", "3306"),
            "-u " + settings.get("odktools.mysql.user"),
            "-p " + settings.get("odktools.mysql.password"),
            "-s " + schema,
            "-o " + form_repository_path,
            "-t " + ",".join(table_array),
        ]
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if p.returncode == 0:
            args = ["mysql", "--defaults-file=" + my_cnf_file, schema]

            with open(create_file) as input_create_file:
                proc = Popen(args, stdin=input_create_file, stderr=PIPE, stdout=PIPE)
                output, error = proc.communicate()
                if proc.returncode != 0:
                    print(
                        "Cannot create new triggers for schema {} with file {}. Error:{}-{}".format(
                            schema,
                            create_file,
                            output.decode(),
                            error.decode(),
                        )
                    )
                    exit(1)
        else:
            print(
                "Cannot create new triggers. Error: {}-{}".format(
                    stdout.decode(), stderr.decode()
                )
            )
            exit(1)


def validateSchema(settings, schema):
    engine = create_engine(settings.get("sqlalchemy.url", ""), poolclass=NullPool)
    connection = engine.connect()
    try:
        res1 = connection.execute("use {};".format(schema))
        continueProcess = True
    except Exception as e:
        continueProcess = False

    connection.invalidate()
    engine.dispose()

    return continueProcess


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    config_uri = context.config.get_main_option("climmob.ini.file", None)

    if config_uri is None:
        print(
            "This migration needs parameter 'climmob.ini.file' in the alembic ini file."
        )
        print(
            "The parameter 'climmob.ini.file' must point to the full path of the ClimMob ini file"
        )
        exit(1)

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, "climmob")
    # ### end Alembic commands ###
    session = Session(bind=op.get_bind())

    my_cnf_file = settings.get("mysql.cnf")

    repository_directory = settings.get("user.repository", "")
    if repository_directory == "":
        print("Cannot find the repository path.")
        exit(1)

    registryForms = (
        session.query(Project.project_cod, userProject.user_name)
        .filter(Project.project_id == userProject.project_id)
        .filter(userProject.access_type == 1)
        .filter(Project.project_regstatus > 0)
        .all()
    )

    for form in registryForms:

        print(form.project_cod)

        schema = form.user_name + "_" + form.project_cod
        print(schema)
        continueProcess = validateSchema(settings, schema)

        if continueProcess:

            parts = [form.user_name, form.project_cod, "db", "reg", "create.xml"]
            create_xml_file = os.path.join(repository_directory, *parts)

            parts = [
                form.user_name,
                form.project_cod,
                "db",
                "reg",
                "mysql_create_audit.sql",
            ]
            create_file = os.path.join(repository_directory, *parts)

            parts = [
                form.user_name,
                form.project_cod,
                "db",
                "reg",
            ]
            form_repository_path = os.path.join(repository_directory, *parts)

            functionForCreateTheTriggers(
                schema,
                create_xml_file,
                settings,
                create_file,
                form_repository_path,
                my_cnf_file,
            )
        else:
            print("The database does not exist...")

    assessmentsForms = (
        session.query(Project.project_cod, userProject.user_name, Assessment.ass_cod)
        .filter(Project.project_id == userProject.project_id)
        .filter(userProject.access_type == 1)
        .filter(Assessment.project_id == Project.project_id)
        .filter(Assessment.ass_status > 0)
        .all()
    )

    for form in assessmentsForms:

        print(form.project_cod)

        schema = form.user_name + "_" + form.project_cod

        continueProcess = validateSchema(settings, schema)

        if continueProcess:

            parts = [
                form.user_name,
                form.project_cod,
                "db",
                "ass",
                form.ass_cod,
                "create.xml",
            ]
            create_xml_file = os.path.join(repository_directory, *parts)

            parts = [
                form.user_name,
                form.project_cod,
                "db",
                "ass",
                form.ass_cod,
                "mysql_create_audit.sql",
            ]
            create_file = os.path.join(repository_directory, *parts)

            parts = [form.user_name, form.project_cod, "db", "ass", form.ass_cod]
            form_repository_path = os.path.join(repository_directory, *parts)

            functionForCreateTheTriggers(
                schema,
                create_xml_file,
                settings,
                create_file,
                form_repository_path,
                my_cnf_file,
            )

        else:
            print("The database does not exist...")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    print("_____Downgrade of Enable Auditlog_____")
    config_uri = context.config.get_main_option("climmob.ini.file", None)

    if config_uri is None:
        print(
            "This migration needs parameter 'climmob.ini.file' in the alembic ini file."
        )
        print(
            "The parameter 'climmob.ini.file' must point to the full path of the ClimMob ini file"
        )
        exit(1)

    setup_logging(config_uri)
    settings = get_appsettings(config_uri, "climmob")
    # ### end Alembic commands ###
    session = Session(bind=op.get_bind())

    my_cnf_file = settings.get("mysql.cnf")

    repository_directory = settings.get("user.repository", "")
    if repository_directory == "":
        print("Cannot find the repository path.")
        exit(1)

    registryForms = (
        session.query(Project.project_cod, userProject.user_name)
        .filter(Project.project_id == userProject.project_id)
        .filter(userProject.access_type == 1)
        .filter(Project.project_regstatus > 0)
        .all()
    )

    for form in registryForms:
        print(form.project_cod)
        schema = form.user_name + "_" + form.project_cod

        continueProcess = validateSchema(settings, schema)

        if continueProcess:

            parts = [
                form.user_name,
                form.project_cod,
                "db",
                "reg",
                "mysql_drop_audit.sql",
            ]
            drop_file = os.path.join(repository_directory, *parts)

            functionForDropTheTriggers(my_cnf_file, schema, drop_file)
        else:
            print("The database does not exist...")

    assessmentsForms = (
        session.query(Project.project_cod, userProject.user_name, Assessment.ass_cod)
        .filter(Project.project_id == userProject.project_id)
        .filter(userProject.access_type == 1)
        .filter(Assessment.project_id == Project.project_id)
        .filter(Assessment.ass_status > 0)
        .all()
    )

    for form in assessmentsForms:
        print(form.project_cod)

        schema = form.user_name + "_" + form.project_cod

        continueProcess = validateSchema(settings, schema)

        if continueProcess:

            parts = [
                form.user_name,
                form.project_cod,
                "db",
                "ass",
                form.ass_cod,
                "mysql_drop_audit.sql",
            ]
            drop_file = os.path.join(repository_directory, *parts)

            schema = form.user_name + "_" + form.project_cod

            functionForDropTheTriggers(my_cnf_file, schema, drop_file)
        else:
            print("The database does not exist...")

    # ### end Alembic commands ###


def functionForDropTheTriggers(my_cnf_file, schema, drop_file):

    if os.path.exists(drop_file):
        args = ["mysql", "--defaults-file=" + my_cnf_file, schema]
        with open(drop_file) as input_drop_file:
            proc = Popen(args, stdin=input_drop_file, stderr=PIPE, stdout=PIPE)
            output, error = proc.communicate()
            if proc.returncode != 0:
                print(
                    "Cannot drop old triggers for schema {} with file {}. Error:{}-{}".format(
                        schema,
                        drop_file,
                        output.decode(),
                        error.decode(),
                    )
                )
                exit(1)
    # else:
    #    exit(1)
