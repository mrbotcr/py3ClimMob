"""Create tables Project status and type with i18n

Revision ID: 7e160694b2f9
Revises: a05c2747571e
Create Date: 2024-05-10 11:27:05.284010

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = "7e160694b2f9"
down_revision = "a05c2747571e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project_status",
        sa.Column("prjstatus_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("prjstatus_name", sa.Unicode(length=120), nullable=False),
        sa.Column(
            "prjstatus_description",
            mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"),
            nullable=True,
        ),
        sa.Column("prjstatus_lang", sa.Unicode(length=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["prjstatus_lang"],
            ["i18n.lang_code"],
            name=op.f("fk_project_status_prjstatus_lang_i18n"),
        ),
        sa.PrimaryKeyConstraint("prjstatus_id", name=op.f("pk_project_status")),
    )
    op.create_table(
        "project_type",
        sa.Column("prjtype_id", sa.Integer(), autoincrement=False, nullable=False),
        sa.Column("prjtype_name", sa.Unicode(length=120), nullable=False),
        sa.Column(
            "prjtype_description",
            mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"),
            nullable=True,
        ),
        sa.Column("prjtype_lang", sa.Unicode(length=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["prjtype_lang"],
            ["i18n.lang_code"],
            name=op.f("fk_project_type_prjtype_lang_i18n"),
        ),
        sa.PrimaryKeyConstraint("prjtype_id", name=op.f("pk_project_type")),
    )
    op.create_table(
        "i18n_project_status",
        sa.Column("prjstatus_id", sa.Integer(), nullable=False),
        sa.Column("lang_code", sa.Unicode(length=5), nullable=False),
        sa.Column("prjstatus_name", sa.Unicode(length=120), nullable=False),
        sa.Column(
            "prjstatus_description",
            mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["lang_code"],
            ["i18n.lang_code"],
            name=op.f("fk_i18n_project_status_lang_code_i18n"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prjstatus_id"],
            ["project_status.prjstatus_id"],
            name=op.f("fk_i18n_project_status_prjstatus_id_project_status"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "prjstatus_id", "lang_code", name=op.f("pk_i18n_project_status")
        ),
    )
    op.create_table(
        "i18n_project_type",
        sa.Column("prjtype_id", sa.Integer(), nullable=False),
        sa.Column("lang_code", sa.Unicode(length=5), nullable=False),
        sa.Column("prjtype_name", sa.Unicode(length=120), nullable=False),
        sa.Column(
            "prjtype_description",
            mysql.MEDIUMTEXT(collation="utf8mb4_unicode_ci"),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["lang_code"],
            ["i18n.lang_code"],
            name=op.f("fk_i18n_project_type_lang_code_i18n"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["prjtype_id"],
            ["project_type.prjtype_id"],
            name=op.f("fk_i18n_project_type_prjtype_id_project_type"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "prjtype_id", "lang_code", name=op.f("pk_i18n_project_type")
        ),
    )

    project_status_inserts = [
        {
            "prjstatus_id": 0,
            "prjstatus_name": "Undefined",
            "prjstatus_description": "",
            "prjstatus_lang": "en",
        },
        {
            "prjstatus_id": 1,
            "prjstatus_name": "Definition",
            "prjstatus_description": "",
            "prjstatus_lang": "en",
        },
        {
            "prjstatus_id": 2,
            "prjstatus_name": "In progress",
            "prjstatus_description": "",
            "prjstatus_lang": "en",
        },
        {
            "prjstatus_id": 3,
            "prjstatus_name": "Finalized",
            "prjstatus_description": "",
            "prjstatus_lang": "en",
        },
    ]

    project_status = table(
        "project_status",
        column("prjstatus_id", Integer),
        column("prjstatus_name", String),
        column("prjstatus_description", String),
        column("prjstatus_lang", String),
    )
    try:
        op.bulk_insert(project_status, project_status_inserts)
    except Exception as e:
        print(e)
        pass

    project_type_inserts = [
        {
            "prjtype_id": 0,
            "prjtype_name": "Undefined",
            "prjtype_description": "The project does not have any type configured",
            "prjtype_lang": "en",
        },
        {
            "prjtype_id": 1,
            "prjtype_name": "Real",
            "prjtype_description": "The project contains real information from participants who have been trained on the Tricot approach and who have conducted their field trial and are using real technology options",
            "prjtype_lang": "en",
        },
        {
            "prjtype_id": 2,
            "prjtype_name": "Training",
            "prjtype_description": "This project was only used to explain the use of the ClimMob platform and was created as an example",
            "prjtype_lang": "en",
        },
    ]

    project_type = table(
        "project_type",
        column("prjtype_id", Integer),
        column("prjtype_name", String),
        column("prjtype_description", String),
        column("prjtype_lang", String),
    )
    try:
        op.bulk_insert(project_type, project_type_inserts)
    except Exception as e:
        print(e)
        pass

    i18n_project_status_inserts = [
        {
            "prjstatus_id": 0,
            "prjstatus_name": "Sin definir",
            "prjstatus_description": "",
            "lang_code": "es",
        },
        {
            "prjstatus_id": 1,
            "prjstatus_name": "Definición",
            "prjstatus_description": "",
            "lang_code": "es",
        },
        {
            "prjstatus_id": 2,
            "prjstatus_name": "En progreso",
            "prjstatus_description": "",
            "lang_code": "es",
        },
        {
            "prjstatus_id": 3,
            "prjstatus_name": "Finalizado",
            "prjstatus_description": "",
            "lang_code": "es",
        },
        {
            "prjstatus_id": 0,
            "prjstatus_name": "Non défini",
            "prjstatus_description": "",
            "lang_code": "fr",
        },
        {
            "prjstatus_id": 1,
            "prjstatus_name": "Définition",
            "prjstatus_description": "",
            "lang_code": "fr",
        },
        {
            "prjstatus_id": 2,
            "prjstatus_name": "En cours",
            "prjstatus_description": "",
            "lang_code": "fr",
        },
        {
            "prjstatus_id": 3,
            "prjstatus_name": "Finalisé",
            "prjstatus_description": "",
            "lang_code": "fr",
        },
    ]

    i18n_project_status = table(
        "i18n_project_status",
        column("prjstatus_id", Integer),
        column("prjstatus_name", String),
        column("prjstatus_description", String),
        column("lang_code", String),
    )
    try:
        op.bulk_insert(i18n_project_status, i18n_project_status_inserts)
    except Exception as e:
        print(e)
        pass

    i18n_project_type_inserts = [
        {
            "prjtype_id": 0,
            "prjtype_name": "Sin definir",
            "prjtype_description": "El proyecto no tiene ningún tipo configurado",
            "lang_code": "es",
        },
        {
            "prjtype_id": 1,
            "prjtype_name": "Real",
            "prjtype_description": "El proyecto contiene información real de participantes que han recibido formación sobre el enfoque Tricot y que han realizado su ensayo de campo y están utilizando opciones tecnológicas reales.",
            "lang_code": "es",
        },
        {
            "prjtype_id": 2,
            "prjtype_name": "Entrenamiento",
            "prjtype_description": "Este proyecto sólo se utilizó para explicar el uso de la plataforma ClimMob y se creó como ejemplo",
            "lang_code": "es",
        },
        {
            "prjtype_id": 0,
            "prjtype_name": "Non défini",
            "prjtype_description": "Le projet n'a aucun type configuré",
            "lang_code": "fr",
        },
        {
            "prjtype_id": 1,
            "prjtype_name": "Réel",
            "prjtype_description": "Le projet contient des informations réelles provenant de participants formés à l'approche Tricot, qui ont mené leur essai sur le terrain et utilisent des options technologiques réelles.",
            "lang_code": "fr",
        },
        {
            "prjtype_id": 2,
            "prjtype_name": "Formation",
            "prjtype_description": "Ce projet a été utilisé uniquement pour expliquer l'utilisation de la plateforme ClimMob et a été créé à titre d'exemple.",
            "lang_code": "fr",
        },
    ]

    i18n_project_type = table(
        "i18n_project_type",
        column("prjtype_id", Integer),
        column("prjtype_name", String),
        column("prjtype_description", String),
        column("lang_code", String),
    )
    try:
        op.bulk_insert(i18n_project_type, i18n_project_type_inserts)
    except Exception as e:
        print(e)
        pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("i18n_project_type")
    op.drop_table("i18n_project_status")
    op.drop_table("project_type")
    op.drop_table("project_status")
    # ### end Alembic commands ###
