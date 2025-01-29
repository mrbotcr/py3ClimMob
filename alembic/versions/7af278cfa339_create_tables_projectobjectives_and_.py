"""Create tables ProjectObjectives and I18nProjectObjectives

Revision ID: 7af278cfa339
Revises: 18a87d7851ee
Create Date: 2024-11-18 10:59:34.310977

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import String, Integer
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = "7af278cfa339"
down_revision = "18a87d7851ee"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project_objective",
        sa.Column("pobjective_id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pobjective_name", sa.Unicode(length=120), nullable=False),
        sa.Column("pobjective_lang", sa.Unicode(length=5), nullable=False),
        sa.ForeignKeyConstraint(
            ["pobjective_lang"],
            ["i18n.lang_code"],
            name=op.f("fk_project_objective_pobjective_lang_i18n"),
        ),
        sa.PrimaryKeyConstraint("pobjective_id", name=op.f("pk_project_objective")),
    )
    op.create_table(
        "i18n_project_objective",
        sa.Column("pobjective_id", sa.Integer(), nullable=False),
        sa.Column("lang_code", sa.Unicode(length=5), nullable=False),
        sa.Column("pobjective_name", sa.Unicode(length=120), nullable=False),
        sa.ForeignKeyConstraint(
            ["lang_code"],
            ["i18n.lang_code"],
            name=op.f("fk_i18n_project_objective_lang_code_i18n"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["pobjective_id"],
            ["project_objective.pobjective_id"],
            name=op.f("fk_i18n_project_objective_pobjective_id_project_objective"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "pobjective_id", "lang_code", name=op.f("pk_i18n_project_objective")
        ),
    )

    project_objectives_values = [
        {
            "pobjective_id": 1,
            "pobjective_name": "Adaptation trial",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 2,
            "pobjective_name": "Concept evaluation",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 3,
            "pobjective_name": "Demonstration trial",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 4,
            "pobjective_name": "Mixture introduction",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 5,
            "pobjective_name": "Mixture recommendation",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 6,
            "pobjective_name": "On-farm verification",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 7,
            "pobjective_name": "Piloting/training",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 8,
            "pobjective_name": "Practice validation trial",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 9,
            "pobjective_name": "Validation trial",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 10,
            "pobjective_name": "Variety introduction",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 11,
            "pobjective_name": "Variety recommendation",
            "pobjective_lang": "en",
        },
        {
            "pobjective_id": 12,
            "pobjective_name": "Variety release",
            "pobjective_lang": "en",
        },
    ]

    project_objectives = table(
        "project_objective",
        column("pobjective_id", Integer),
        column("pobjective_name", String),
        column("pobjective_lang", String),
    )
    op.bulk_insert(project_objectives, project_objectives_values)

    i18n_project_objectives_values = [
        {
            "pobjective_id": 1,
            "lang_code": "es",
            "pobjective_name": "Ensayo de adaptación",
        },
        {
            "pobjective_id": 1,
            "lang_code": "fr",
            "pobjective_name": "Essai d'adaptation",
        },
        {
            "pobjective_id": 2,
            "lang_code": "es",
            "pobjective_name": "Evaluación de concepto",
        },
        {
            "pobjective_id": 2,
            "lang_code": "fr",
            "pobjective_name": "Évaluation de concept",
        },
        {
            "pobjective_id": 3,
            "lang_code": "es",
            "pobjective_name": "Ensayo de demostración",
        },
        {
            "pobjective_id": 3,
            "lang_code": "fr",
            "pobjective_name": "Essai de démonstration",
        },
        {
            "pobjective_id": 4,
            "lang_code": "es",
            "pobjective_name": "Introducción de la mezcla",
        },
        {
            "pobjective_id": 4,
            "lang_code": "fr",
            "pobjective_name": "Introduction de mélange",
        },
        {
            "pobjective_id": 5,
            "lang_code": "es",
            "pobjective_name": "Recomendación de la mezcla",
        },
        {
            "pobjective_id": 5,
            "lang_code": "fr",
            "pobjective_name": "Recommandation de mélange",
        },
        {
            "pobjective_id": 6,
            "lang_code": "es",
            "pobjective_name": "Verificación en campo",
        },
        {
            "pobjective_id": 6,
            "lang_code": "fr",
            "pobjective_name": "Vérification en exploitation",
        },
        {
            "pobjective_id": 7,
            "lang_code": "es",
            "pobjective_name": "Piloto/capacitación",
        },
        {
            "pobjective_id": 7,
            "lang_code": "fr",
            "pobjective_name": "Pilotage/formation",
        },
        {
            "pobjective_id": 8,
            "lang_code": "es",
            "pobjective_name": "Ensayo de validación de la práctica",
        },
        {
            "pobjective_id": 8,
            "lang_code": "fr",
            "pobjective_name": "Validation des pratiques",
        },
        {
            "pobjective_id": 9,
            "lang_code": "es",
            "pobjective_name": "Ensayo de validación",
        },
        {
            "pobjective_id": 9,
            "lang_code": "fr",
            "pobjective_name": "Essai de validation",
        },
        {
            "pobjective_id": 10,
            "lang_code": "es",
            "pobjective_name": "Introducción de la variedad",
        },
        {
            "pobjective_id": 10,
            "lang_code": "fr",
            "pobjective_name": "Introduction de variété",
        },
        {
            "pobjective_id": 11,
            "lang_code": "es",
            "pobjective_name": "Recomendación de la variedad",
        },
        {
            "pobjective_id": 11,
            "lang_code": "fr",
            "pobjective_name": "Recommandation de variété",
        },
        {
            "pobjective_id": 12,
            "lang_code": "es",
            "pobjective_name": "Liberación de la variedad",
        },
        {
            "pobjective_id": 12,
            "lang_code": "fr",
            "pobjective_name": "Homologation de variété",
        },
    ]

    i18n_project_objectives = table(
        "i18n_project_objective",
        column("pobjective_id", Integer),
        column("lang_code", String),
        column("pobjective_name", String),
    )
    op.bulk_insert(i18n_project_objectives, i18n_project_objectives_values)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("i18n_project_objective")
    op.drop_table("project_objective")
    # ### end Alembic commands ###
