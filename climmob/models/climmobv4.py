# coding: utf-8
import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    Unicode,
    text,
    BLOB,
    JSON,
)
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import relationship

from climmob.models.meta import Base


class Activitylog(Base):
    __tablename__ = "activitylog"

    log_id = Column(Integer, primary_key=True)
    log_user = Column(ForeignKey("user.user_name"), nullable=False, index=True)
    log_datetime = Column(DateTime, default=datetime.datetime.now())
    log_type = Column(Unicode(3))
    log_message = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    user = relationship("User")


class Apilog(Base):
    __tablename__ = "apilog"

    log_id = Column(Integer, primary_key=True)
    log_datetime = Column(DateTime)
    log_ip = Column(Unicode(45))
    log_user = Column(ForeignKey("user.user_name"), nullable=False, index=True)
    log_uuid = Column(Unicode(80))

    user = relationship("User")


class Assessment(Base):
    __tablename__ = "assessment"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )
    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    ass_cod = Column(Unicode(80), primary_key=True, nullable=False)
    ass_desc = Column(Unicode(120))
    ass_days = Column(Integer)
    ass_status = Column(Integer, server_default=text("'0'"))
    ass_final = Column(Integer, server_default=text("'0'"))
    extra = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    project = relationship("Project")


class AssDetail(Base):
    __tablename__ = "assdetail"
    __table_args__ = (
        ForeignKeyConstraint(
            ["section_project_id", "section_assessment", "section_id"],
            [
                "asssection.project_id",
                "asssection.ass_cod",
                "asssection.section_id",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id", "ass_cod"],
            ["assessment.project_id", "assessment.ass_cod"],
            ondelete="CASCADE",
        ),
        Index(
            "fk_assessment_asssection1_idx",
            "section_project_id",
            "section_id",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    ass_cod = Column(Unicode(80), primary_key=True, nullable=False)
    question_id = Column(
        ForeignKey("question.question_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    section_project_id = Column(Unicode(80), nullable=False)
    section_assessment = Column(Unicode(80), nullable=False)
    section_id = Column(Integer, nullable=False)
    question_order = Column(Integer)

    question = relationship("Question")
    asssection = relationship("Asssection")
    assessment = relationship("Assessment")


class Asssection(Base):
    __tablename__ = "asssection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "ass_cod"],
            ["assessment.project_id", "assessment.ass_cod"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    ass_cod = Column(Unicode(80), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(Unicode(120))
    section_content = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    section_order = Column(Integer)
    section_private = Column(Integer, nullable=True)

    assessment = relationship("Assessment")


class Country(Base):
    __tablename__ = "country"

    cnty_cod = Column(Unicode(3), primary_key=True)
    cnty_iso = Column(Unicode(3), nullable=True)
    cnty_name = Column(Unicode(120))
    cnty_lang = Column(ForeignKey("i18n.lang_code"), server_default=text("'en'"))

    i18n = relationship("I18n")


class I18nCountry(Base):
    __tablename__ = "i18n_country"

    cnty_cod = Column(ForeignKey("country.cnty_cod"), primary_key=True, nullable=False)
    lang_code = Column(ForeignKey("i18n.lang_code"), primary_key=True, nullable=False)
    cnty_name = Column(Unicode(120))

    i18n = relationship("I18n")
    country = relationship("Country")


class Enumerator(Base):
    __tablename__ = "enumerator"
    __table_args__ = (
        ForeignKeyConstraint(["user_name"], ["user.user_name"], ondelete="CASCADE"),
    )
    user_name = Column(Unicode(80), primary_key=True, nullable=False)
    enum_id = Column(Unicode(80), primary_key=True, nullable=False)
    enum_name = Column(Unicode(120))
    enum_password = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    enum_telephone = Column(Unicode(120), server_default=text("''"))
    enum_email = Column(Unicode(120), server_default=text("''"))
    enum_active = Column(Integer)
    extra = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    user = relationship("User")


class PrjEnumerator(Base):
    __tablename__ = "prjenumerator"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["enum_user", "enum_id"],
            ["enumerator.user_name", "enumerator.enum_id"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    enum_user = Column(Unicode(80), primary_key=True, nullable=False)
    enum_id = Column(Unicode(80), primary_key=True, nullable=False)
    extra = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    project = relationship("Project")
    enumerator = relationship("Enumerator")


class Products(Base):
    __tablename__ = "products"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), nullable=True)
    celery_taskid = Column(Unicode(80), primary_key=True, nullable=False)
    process_name = Column(Unicode(80), nullable=False)
    product_id = Column(Unicode(80), primary_key=True, nullable=False)
    output_id = Column(Unicode(80), nullable=False)
    output_mimetype = Column(Unicode(80), nullable=False)
    datetime_added = Column(DateTime)

    project = relationship("Project")


class Tasks(Base):
    __tablename__ = "tasks"
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8"},)
    taskid = Column(Unicode(80), primary_key=True, nullable=False)


class finishedTasks(Base):
    __tablename__ = "finishedtasks"
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8"},)
    taskid = Column(Unicode(80), primary_key=True, nullable=False)
    taskerror = Column(Integer)


class storageErrors(Base):
    __tablename__ = "storageerrors"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), nullable=False)
    fileuid = Column(Unicode(80), primary_key=True, nullable=False)
    error_datetime = Column(DateTime)
    submission_type = Column(Unicode(80))
    assessment_id = Column(Unicode(80))
    command_executed = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    error_cod = Column(Unicode(80))
    error_des = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    error_table = Column(Unicode(120))

    project = relationship("Project")


class I18n(Base):
    __tablename__ = "i18n"

    lang_code = Column(Unicode(5), primary_key=True)
    lang_name = Column(Unicode(120))
    lang_in_climmob = Column(Integer, server_default=text("'0'"))


class I18nUser(Base):
    __tablename__ = "i18n_user"

    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    user_name = Column(
        ForeignKey("user.user_name"), primary_key=True, nullable=False, index=True
    )
    lang_default = Column(Integer, server_default=text("'0'"))

    i18n = relationship("I18n")
    user = relationship("User")


class I18nAsssection(Base):
    __tablename__ = "i18n_asssection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "ass_cod", "section_id"],
            [
                "asssection.project_id",
                "asssection.ass_cod",
                "asssection.section_id",
            ],
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    ass_cod = Column(Unicode(80), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    section_name = Column(Unicode(120))
    section_content = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    i18n = relationship("I18n")
    asssection = relationship("Asssection")


class I18nPrjalia(Base):
    __tablename__ = "i18n_prjalias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "tech_id", "alias_id"],
            [
                "prjalias.project_id",
                "prjalias.tech_id",
                "prjalias.alias_id",
            ],
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    alias_name = Column(Unicode(120))

    i18n = relationship("I18n")
    prjalia = relationship("Prjalia")


class I18nProject(Base):
    __tablename__ = "i18n_project"
    __table_args__ = (ForeignKeyConstraint(["project_id"], ["project.project_id"]),)

    project_id = Column(Unicode(64), primary_key=True, nullable=True)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    project_name = Column(Unicode(120))
    project_abstract = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    i18n = relationship("I18n")
    project = relationship("Project")


class I18nQstoption(Base):
    __tablename__ = "i18n_qstoption"
    __table_args__ = (
        ForeignKeyConstraint(
            ["question_id", "value_code"],
            ["qstoption.question_id", "qstoption.value_code"],
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    question_id = Column(Integer, primary_key=True, nullable=False)
    value_code = Column(Unicode(80), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    value_desc = Column(Unicode(120))

    i18n = relationship("I18n")
    qstoption = relationship("Qstoption")


class I18nQuestion_group(Base):
    __tablename__ = "i18n_qstgroups"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "qstgroups_id"],
            [
                "qstgroups.user_name",
                "qstgroups.qstgroups_id",
            ],
        ),
    )

    user_name = Column(Unicode(80), primary_key=True, nullable=False)
    qstgroups_id = Column(Unicode(80), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    qstgroups_name = Column(Unicode(120))

    i18n = relationship("I18n")
    question = relationship("Question_group")


class I18nQuestion(Base):
    __tablename__ = "i18n_question"

    question_id = Column(
        ForeignKey("question.question_id"), primary_key=True, nullable=False
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    question_desc = Column(Unicode(120))
    question_notes = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    question_unit = Column(Unicode(120))
    question_posstm = Column(Unicode(120))
    question_negstm = Column(Unicode(120))
    question_perfstmt = Column(Unicode(120))
    question_name = Column(Unicode(120))

    i18n = relationship("I18n")
    question = relationship("Question")


class I18nRegsection(Base):
    __tablename__ = "i18n_regsection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "section_id"],
            [
                "regsection.project_id",
                "regsection.section_id",
            ],
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    section_name = Column(Unicode(120))
    section_content = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    i18n = relationship("I18n")
    regsection = relationship("Regsection")


class I18nTechalia(Base):
    __tablename__ = "i18n_techalias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tech_id", "alias_id"], ["techalias.tech_id", "techalias.alias_id"]
        ),
    )

    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    alias_name = Column(Unicode(120))

    i18n = relationship("I18n")
    tech = relationship("Techalia")


class I18nTechnology(Base):
    __tablename__ = "i18n_technology"

    tech_id = Column(ForeignKey("technology.tech_id"), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    tech_name = Column(Unicode(45))

    i18n = relationship("I18n")
    tech = relationship("Technology")


class Package(Base):
    __tablename__ = "package"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    package_id = Column(Integer, primary_key=True, nullable=False)
    package_code = Column(Unicode(45))
    package_image = Column(LargeBinary)

    project = relationship("Project")


class Pkgcomb(Base):
    __tablename__ = "pkgcomb"
    __table_args__ = (
        ForeignKeyConstraint(
            ["comb_project_id", "comb_code"],
            [
                "prjcombination.project_id",
                "prjcombination.comb_code",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id", "package_id"],
            ["package.project_id", "package.package_id"],
            ondelete="CASCADE",
        ),
        Index("fk_pkgcomb_prjcombination1_idx", "comb_project_id", "comb_code"),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    package_id = Column(Integer, primary_key=True, nullable=False)
    comb_project_id = Column(Unicode(64), primary_key=True, nullable=False)
    comb_code = Column(Integer, primary_key=True, nullable=False)
    comb_order = Column(Integer)

    prjcombination = relationship("Prjcombination")
    package = relationship("Package")


class Prjalia(Base):
    __tablename__ = "prjalias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tech_used", "alias_used"],
            ["techalias.tech_id", "techalias.alias_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id", "tech_id"],
            ["prjtech.project_id", "prjtech.tech_id"],
            ondelete="CASCADE",
        ),
        Index("fk_prjalias_techalias1_idx", "tech_used", "alias_used"),
        Index("fk_prjalias_prjtech1_idx", "project_id", "tech_id"),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    alias_name = Column(Unicode(120))
    tech_used = Column(Integer)
    alias_used = Column(Integer)

    techalia = relationship("Techalia")
    prjtech = relationship("Prjtech")


class Prjcnty(Base):
    __tablename__ = "prjcnty"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    cnty_cod = Column(
        ForeignKey("country.cnty_cod", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    cnty_contact = Column(Unicode(120))

    country = relationship("Country")
    project = relationship("Project")


class Prjcombdet(Base):
    __tablename__ = "prjcombdet"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "comb_code"],
            [
                "prjcombination.project_id",
                "prjcombination.comb_code",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id_tech", "tech_id", "alias_id"],
            [
                "prjalias.project_id",
                "prjalias.tech_id",
                "prjalias.alias_id",
            ],
            ondelete="CASCADE",
        ),
        Index(
            "fk_prjcombdet_prjalias1_idx",
            "project_id",
            "tech_id",
            "alias_id",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    comb_code = Column(Integer, primary_key=True, nullable=False)
    project_id_tech = Column(Unicode(64), primary_key=True, nullable=False)
    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    alias_order = Column(Integer)

    prjcombination = relationship("Prjcombination")
    prjalia = relationship("Prjalia")


class Prjcombination(Base):
    __tablename__ = "prjcombination"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    comb_code = Column(Integer, primary_key=True, nullable=False)
    comb_usable = Column(Integer)
    quantity_available = Column(Integer, nullable=True)

    project = relationship("Project")


class Prjlang(Base):
    __tablename__ = "prjlang"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    lang_default = Column(Integer)

    i18n = relationship("I18n")
    project = relationship("Project")


class Prjtech(Base):
    __tablename__ = "prjtech"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    tech_id = Column(
        ForeignKey("technology.tech_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    tech = relationship("Technology")
    project = relationship("Project")


class Project(Base):
    __tablename__ = "project"

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    project_cod = Column(Unicode(80), nullable=False)
    project_name = Column(Unicode(120))
    project_abstract = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    project_tags = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    project_pi = Column(Unicode(120))
    project_piemail = Column(Unicode(120))
    project_active = Column(Integer, server_default=text("'1'"))
    project_public = Column(Integer, server_default=text("'0'"))
    project_regstatus = Column(Integer, server_default=text("'0'"))
    project_assstatus = Column(Integer, server_default=text("'0'"))
    project_createcomb = Column(Integer, server_default=text("'0'"))
    project_createpkgs = Column(Integer, server_default=text("'0'"))
    project_numobs = Column(Integer, nullable=False, server_default=text("'0'"))
    project_numcom = Column(Integer, nullable=False)
    project_lat = Column(Unicode(120), nullable=False)
    project_lon = Column(Unicode(120), nullable=False)
    project_creationdate = Column(DateTime, nullable=False)
    project_localvariety = Column(Integer, server_default=text("'0'"))
    project_cnty = Column(ForeignKey("country.cnty_cod"), nullable=True, index=True)
    project_registration_and_analysis = Column(Integer, server_default=text("'0'"))
    project_label_a = Column(
        Unicode(120), nullable=False, server_default=text("'Option A'")
    )
    project_label_b = Column(
        Unicode(120), nullable=False, server_default=text("'Option B'")
    )
    project_label_c = Column(
        Unicode(120), nullable=False, server_default=text("'Option C'")
    )
    project_template = Column(Integer, server_default=text("'0'"))
    extra = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    project_status = Column(
        ForeignKey("project_status.prjstatus_id"),
        nullable=False,
        server_default=text("'0'"),
    )
    project_type = Column(
        ForeignKey("project_type.prjtype_id"),
        nullable=False,
        server_default=text("'0'"),
    )

    country = relationship("Country")


class Qstoption(Base):
    __tablename__ = "qstoption"
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8"},)

    question_id = Column(
        ForeignKey("question.question_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    value_code = Column(Unicode(80), primary_key=True, nullable=False)
    value_desc = Column(Unicode(120))
    value_isother = Column(Integer, server_default=text("'0'"))
    value_isna = Column(Integer, server_default=text("'0'"))
    value_order = Column(Integer, server_default=text("'0'"))

    question = relationship("Question")


class Question_group(Base):
    __tablename__ = "qstgroups"
    __table_args__ = (
        ForeignKeyConstraint(["user_name"], ["user.user_name"], ondelete="CASCADE"),
    )

    user_name = Column(Unicode(80), primary_key=True, nullable=False)
    qstgroups_id = Column(Unicode(80), primary_key=True, nullable=False)
    qstgroups_name = Column(Unicode(120))

    user = relationship("User")


class Question_subgroup(Base):
    __tablename__ = "qstsubgroups"
    __table_args__ = (
        ForeignKeyConstraint(
            [
                "group_username",
                "group_id",
            ],
            ["qstgroups.user_name", "qstgroups.qstgroups_id"],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            [
                "parent_username",
                "parent_id",
            ],
            ["qstgroups.user_name", "qstgroups.qstgroups_id"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    group_username = Column(Unicode(80), primary_key=True, nullable=False)
    group_id = Column(Unicode(80), primary_key=True, nullable=False)

    parent_username = Column(Unicode(80), primary_key=True, nullable=True)
    parent_id = Column(Unicode(80), primary_key=True, nullable=True)


class Question(Base):
    __tablename__ = "question"
    __table_args__ = (
        ForeignKeyConstraint(
            ["qstgroups_user", "qstgroups_id"],
            ["qstgroups.user_name", "qstgroups.qstgroups_id"],
            ondelete="CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )
    question_id = Column(Integer, primary_key=True)
    question_code = Column(Unicode(120))
    question_name = Column(Unicode(120))
    question_desc = Column(Unicode(120))
    question_notes = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    question_unit = Column(Unicode(120))
    question_dtype = Column(Integer)
    question_cmp = Column(Unicode(120))
    question_reqinreg = Column(Integer, server_default=text("'0'"))
    question_reqinasses = Column(Integer, server_default=text("'0'"))
    question_alwaysinreg = Column(Integer, server_default=text("'0'"))
    question_alwaysinasse = Column(Integer, server_default=text("'0'"))
    question_optperprj = Column(Integer, server_default=text("'0'"))
    user_name = Column(ForeignKey("user.user_name"), index=True)
    question_posstm = Column(Unicode(120))
    question_negstm = Column(Unicode(120))
    question_twoitems = Column(Unicode(120))
    question_moreitems = Column(Unicode(120))
    question_perfstmt = Column(Unicode(120))
    question_requiredvalue = Column(Integer)
    question_regkey = Column(Integer, server_default=text("'0'"))
    question_asskey = Column(Integer, server_default=text("'0'"))
    question_overall = Column(Integer, server_default=text("'0'"))
    question_overallperf = Column(Integer, server_default=text("'0'"))
    question_fname = Column(Integer, server_default=text("'0'"))
    question_district = Column(Integer, server_default=text("'0'"))
    question_village = Column(Integer, server_default=text("'0'"))
    question_father = Column(Integer, server_default=text("'0'"))
    question_visible = Column(Integer, server_default=text("'1'"))
    question_tied = Column(Integer, server_default=text("'0'"))
    question_notobserved = Column(Integer, server_default=text("'0'"))
    question_quantitative = Column(Integer, server_default=text("'0'"))
    question_forms = Column(Integer, server_default=text("'3'"))
    qstgroups_user = Column(Unicode(80), nullable=True)
    qstgroups_id = Column(Unicode(80), nullable=True)
    question_sensitive = Column(Integer, server_default=text("'0'"))
    question_lang = Column(ForeignKey("i18n.lang_code"), nullable=True)
    extra = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    i18n = relationship("I18n")
    user = relationship("User")


class Registry(Base):
    __tablename__ = "registry"
    __table_args__ = (
        ForeignKeyConstraint(
            ["section_project_id", "section_id"],
            [
                "regsection.project_id",
                "regsection.section_id",
            ],
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
        Index(
            "fk_registry_regsection1_idx",
            "section_project_id",
            "section_id",
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    question_id = Column(
        ForeignKey("question.question_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    section_project_id = Column(Unicode(64))
    section_id = Column(Integer)
    question_order = Column(Integer)

    question = relationship("Question")
    regsection = relationship("Regsection")
    project = relationship("Project")


class Regsection(Base):
    __tablename__ = "regsection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )
    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(Unicode(45))
    section_content = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    section_order = Column(Integer)
    section_private = Column(Integer, nullable=True)

    project = relationship("Project")


class Sector(Base):
    __tablename__ = "sector"

    sector_cod = Column(Integer, primary_key=True)
    sector_name = Column(Unicode(120))
    section_order = Column(Integer, nullable=True)
    section_available = Column(Integer, nullable=True)


class Techalia(Base):
    __tablename__ = "techalias"

    tech_id = Column(
        ForeignKey("technology.tech_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    alias_id = Column(Integer, primary_key=True, nullable=False)
    alias_name = Column(Unicode(120))

    tech = relationship("Technology")


class generalPhrases(Base):
    __tablename__ = "general_phrases"

    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},)

    phrase_id = Column(Integer, primary_key=True, autoincrement=True)
    phrase_desc = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))


class I18nGeneralPhrases(Base):
    __tablename__ = "i18n_general_phrases"

    phrase_id = Column(
        ForeignKey("general_phrases.phrase_id", ondelete="CASCADE"), primary_key=True
    )
    user_name = Column(
        ForeignKey("user.user_name", ondelete="CASCADE"), primary_key=True
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    phrase_desc = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    i18n = relationship("I18n")
    user = relationship("User")
    generalPhrases = relationship("generalPhrases")


class CropTaxonomy(Base):
    __tablename__ = "croptaxonomy"

    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},)

    taxonomy_code = Column(Integer, primary_key=True, autoincrement=False)
    taxonomy_name = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))


class I18nCropTaxonomy(Base):
    __tablename__ = "i18n_croptaxonomy"
    __table_args__ = (
        ForeignKeyConstraint(["taxonomy_code"], ["croptaxonomy.taxonomy_code"]),
    )

    taxonomy_code = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey("i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    crop_name = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    i18n = relationship("I18n")
    croptaxonomy = relationship("CropTaxonomy")


class Technology(Base):
    __tablename__ = "technology"

    tech_id = Column(Integer, primary_key=True)
    tech_name = Column(Unicode(45))
    user_name = Column(ForeignKey("user.user_name", ondelete="CASCADE"), index=True)
    croptaxonomy_code = Column(
        ForeignKey("croptaxonomy.taxonomy_code", ondelete="RESTRICT"),
        index=True,
        nullable=False,
        server_default=text("'0'"),
    )
    tech_accession_id = Column(Unicode(255))

    user = relationship("User")
    crop = relationship("CropTaxonomy")


class User(Base):
    __tablename__ = "user"

    user_name = Column(Unicode(80), primary_key=True)
    user_fullname = Column(Unicode(120))
    user_password = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    user_organization = Column(Unicode(120))
    user_email = Column(Unicode(120))
    user_apikey = Column(Unicode(45))
    user_about = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    user_cnty = Column(ForeignKey("country.cnty_cod"), nullable=False, index=True)
    user_sector = Column(ForeignKey("sector.sector_cod"), nullable=False, index=True)
    user_active = Column(Integer, server_default=text("'1'"))
    user_joindate = Column(DateTime, default=datetime.datetime.now())
    user_last_login = Column(DateTime)

    user_password_reset_key = Column(Unicode(64))
    user_password_reset_token = Column(Unicode(64))
    user_password_reset_expires_on = Column(DateTime)

    user_admin = Column(Integer, server_default=text("'0'"))

    extra = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    country = relationship("Country")
    sector = relationship("Sector")


class RegistryJsonLog(Base):
    __tablename__ = "registry_jsonlog"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
        ),
        ForeignKeyConstraint(
            ["enum_user", "enum_id"],
            ["enumerator.user_name", "enumerator.enum_id"],
        ),
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    log_id = Column(Unicode(64), primary_key=True, nullable=False)
    enum_user = Column(Unicode(80), primary_key=True, nullable=False)
    enum_id = Column(Unicode(80), primary_key=True, nullable=False)

    log_dtime = Column(DateTime)
    json_file = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    log_file = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    status = Column(Integer)

    project = relationship("Project")
    enumerator = relationship("Enumerator")


class AssessmentJsonLog(Base):
    __tablename__ = "assesment_jsonlog"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id", "ass_cod"],
            ["assessment.project_id", "assessment.ass_cod"],
        ),
        ForeignKeyConstraint(
            ["enum_user", "enum_id"],
            ["enumerator.user_name", "enumerator.enum_id"],
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    ass_cod = Column(Unicode(80), primary_key=True, nullable=False)
    log_id = Column(Unicode(64), primary_key=True, nullable=False)
    enum_user = Column(Unicode(80), primary_key=True, nullable=False)
    enum_id = Column(Unicode(80), primary_key=True, nullable=False)
    log_dtime = Column(DateTime)
    json_file = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    log_file = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    status = Column(Integer)

    assessment = relationship("Assessment")
    enumerator = relationship("Enumerator")


class Chat(Base):
    __tablename__ = "chat"
    __table_args__ = (
        ForeignKeyConstraint(["user_name"], ["user.user_name"], ondelete="CASCADE"),
    )
    user_name = Column(Unicode(80), primary_key=True, nullable=False)
    chat_id = Column(Integer, primary_key=True, nullable=False)
    chat_message = Column(Unicode(500))
    chat_send = Column(Integer)
    chat_read = Column(Integer)
    chat_tofrom = Column(Integer)
    chat_date = Column(DateTime)

    project = relationship("User")


class userProject(Base):
    __tablename__ = "user_project"

    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
        ),
        ForeignKeyConstraint(
            ["user_name"],
            ["user.user_name"],
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    user_name = Column(Unicode(80), primary_key=True, nullable=False)
    access_type = Column(Integer, nullable=False)  # 1=Owner,2=Admin,3=Editor,4=Member.
    project_dashboard = Column(Integer, server_default=text("'1'"))
    collaboration_accepted = Column(Integer, server_default=text("'1'"))

    project = relationship("Project")
    user = relationship("User")


"""class ProjectMetadata(Base):
    __tablename__ = "project_metadata"
    __table_args__ = (
        ForeignKeyConstraint(
            ["project_id"],
            ["project.project_id"],
            ondelete="CASCADE",
        ),
    )
    project_id = Column(Unicode(64), primary_key=True, nullable=False)
    md_coordinator = Column(Unicode(100), primary_key=True, nullable=False)
    md_crops = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_year = Column(Integer)
    md_tricot_project = Column(Unicode(120))
    md_objective = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_collaborators = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_experimental_design = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_steps_followed = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_special_features = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_how_varieties_were_selected = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_how_participants_were_selected = Column(
        MEDIUMTEXT(collation="utf8mb4_unicode_ci")
    )
    md_geographic_areas = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_selection_criteria_used = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_how_participants_approached_recruitment = Column(
        MEDIUMTEXT(collation="utf8mb4_unicode_ci")
    )
    md_where_recruidment_place = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_how_recruitment_formalised = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_participants_compensated = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_participants_approached_participate = Column(Integer)
    md_how_tricot_explained = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_training_sessions = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_follow_up_procedures = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_how_was_data_collected = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_how_were_results_devolved = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_instructions_given = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_additional_inputs_provided = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))
    md_varieties = Column(MEDIUMTEXT(collation="utf8mb4_unicode_ci"))

    project = relationship("Project")"""


class ExtraForm(Base):
    __tablename__ = "extra_form"

    form_id = Column(Integer, primary_key=True, autoincrement=True)
    form_name = Column(Unicode(120), nullable=False)
    form_started = Column(DateTime, nullable=False)
    form_finished = Column(DateTime)
    form_status = Column(Integer, default=0, nullable=False)


class ExtraFormAnswer(Base):
    __tablename__ = "extra_form_answers"

    form_id = Column(ForeignKey("extra_form.form_id"), nullable=False, primary_key=True)
    user_name = Column(
        ForeignKey("user.user_name", ondelete="CASCADE"), primary_key=True
    )
    answer_field = Column(Unicode(120), nullable=False, primary_key=True)
    answer_date = Column(DateTime)
    answer_data = Column(Unicode(120), nullable=False)

    extraform = relationship("ExtraForm")
    user = relationship("User")


class ProjectType(Base):
    __tablename__ = "project_type"

    prjtype_id = Column(Integer, primary_key=True, autoincrement=False)
    prjtype_name = Column(Unicode(120), nullable=False)
    prjtype_description = Column(
        MEDIUMTEXT(collation="utf8mb4_unicode_ci"), nullable=True
    )
    prjtype_lang = Column(ForeignKey("i18n.lang_code"), nullable=False)

    i18n = relationship("I18n")


class I18nProjectType(Base):
    __tablename__ = "i18n_project_type"

    prjtype_id = Column(
        ForeignKey("project_type.prjtype_id", ondelete="CASCADE"), primary_key=True
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    prjtype_name = Column(Unicode(120), nullable=False)
    prjtype_description = Column(
        MEDIUMTEXT(collation="utf8mb4_unicode_ci"), nullable=True
    )

    i18n = relationship("I18n")
    ProjectType = relationship("ProjectType")


class ProjectStatus(Base):
    __tablename__ = "project_status"

    prjstatus_id = Column(Integer, primary_key=True, autoincrement=False)
    prjstatus_name = Column(Unicode(120), nullable=False)
    prjstatus_description = Column(
        MEDIUMTEXT(collation="utf8mb4_unicode_ci"), nullable=True
    )
    prjstatus_lang = Column(ForeignKey("i18n.lang_code"), nullable=False)

    i18n = relationship("I18n")


class I18nProjectStatus(Base):
    __tablename__ = "i18n_project_status"

    prjstatus_id = Column(
        ForeignKey("project_status.prjstatus_id", ondelete="CASCADE"), primary_key=True
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    prjstatus_name = Column(Unicode(120), nullable=False)
    prjstatus_description = Column(
        MEDIUMTEXT(collation="utf8mb4_unicode_ci"), nullable=True
    )

    i18n = relationship("I18n")
    ProjectStatus = relationship("ProjectStatus")


class ProjectLocation(Base):
    __tablename__ = "project_location"

    plocation_id = Column(Integer, primary_key=True, autoincrement=True)
    plocation_name = Column(Unicode(120), nullable=False)
    plocation_lang = Column(ForeignKey("i18n.lang_code"), nullable=False)

    i18n = relationship("I18n")


class I18nProjectLocation(Base):
    __tablename__ = "i18n_project_location"

    plocation_id = Column(
        ForeignKey("project_location.plocation_id", ondelete="CASCADE"),
        primary_key=True,
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    plocation_name = Column(Unicode(120), nullable=False)

    i18n = relationship("I18n")
    ProjectLocation = relationship("ProjectLocation", backref="i18n_project_location")


class ProjectUnitOfAnalysis(Base):
    __tablename__ = "project_unit_of_analysis"

    puoa_id = Column(Integer, primary_key=True, autoincrement=True)
    puoa_name = Column(Unicode(120), nullable=False)
    puoa_lang = Column(ForeignKey("i18n.lang_code"), nullable=False)

    i18n = relationship("I18n")


class I18nProjectUnitOfAnalysis(Base):
    __tablename__ = "i18n_project_unit_of_analysis"

    puoa_id = Column(
        ForeignKey("project_unit_of_analysis.puoa_id", ondelete="CASCADE"),
        primary_key=True,
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    puoa_name = Column(Unicode(120), nullable=False)

    i18n = relationship("I18n")
    ProjectUnitOfAnalysis = relationship(
        "ProjectUnitOfAnalysis", backref="i18n_project_unit_of_analysis"
    )


class ProjectObjectives(Base):
    __tablename__ = "project_objective"

    pobjective_id = Column(Integer, primary_key=True, autoincrement=True)
    pobjective_name = Column(Unicode(120), nullable=False)
    pobjective_lang = Column(ForeignKey("i18n.lang_code"), nullable=False)

    i18n = relationship("I18n")


class I18nProjectObjectives(Base):
    __tablename__ = "i18n_project_objective"

    pobjective_id = Column(
        ForeignKey("project_objective.pobjective_id", ondelete="CASCADE"),
        primary_key=True,
    )
    lang_code = Column(
        ForeignKey("i18n.lang_code", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    pobjective_name = Column(Unicode(120), nullable=False)

    i18n = relationship("I18n")
    ProjectObjectives = relationship("ProjectObjectives")


class LocationUnitOfAnalysis(Base):
    __tablename__ = "location_unit_of_analysis"

    pluoa_id = Column(Integer, autoincrement=True, nullable=False, unique=True)

    plocation_id = Column(
        ForeignKey("project_location.plocation_id", ondelete="CASCADE"),
        primary_key=True,
    )

    puoa_id = Column(
        ForeignKey("project_unit_of_analysis.puoa_id", ondelete="CASCADE"),
        primary_key=True,
    )

    ProjectLocation = relationship("ProjectLocation")
    ProjectUnitOfAnalysis = relationship("ProjectUnitOfAnalysis")


class MetadataForm(Base):
    __tablename__ = "metadata_form"

    metadata_id = Column(Unicode(64), primary_key=True)
    metadata_name = Column(Unicode(200), nullable=False)
    metadata_odk = Column(BLOB, nullable=False)
    metadata_json = Column(JSON, nullable=False)
    metadata_active = Column(Integer, nullable=False, server_default=text("'1'"))

    @property
    def test(self):

        return self.metadata_id + "_test"


class MetadaFormLocationUnitOfAnalysis(Base):
    __tablename__ = "metadata_form_location_unit_of_analysis"

    metadata_id = Column(
        ForeignKey("metadata_form.metadata_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    pluoa_id = Column(
        ForeignKey("location_unit_of_analysis.pluoa_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )

    MetadataForm = relationship(
        "MetadataForm", backref="metadata_form_location_unit_of_analysis"
    )
    LocationUnitOfAnalysis = relationship("LocationUnitOfAnalysis")


class ProjectMetadataForm(Base):
    __tablename__ = "project_metadata_form"

    project_id = Column(
        ForeignKey("project.project_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    metadata_id = Column(
        ForeignKey("metadata_form.metadata_id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    pmf_json = Column(JSON, nullable=False)

    Project = relationship("Project")
    MetadataForm = relationship("MetadataForm", backref="project_metadata_form")
