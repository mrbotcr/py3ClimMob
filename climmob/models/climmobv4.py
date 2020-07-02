# coding: utf-8
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    Index,
    Integer,
    LargeBinary,
    Numeric,
    UnicodeText,
    String,
    Unicode,
    Text,
    text,
)
from sqlalchemy.orm import relationship
import datetime


from .meta import Base


class Activitylog(Base):
    __tablename__ = "activitylog"

    log_id = Column(Integer, primary_key=True)
    log_user = Column(ForeignKey(u"user.user_name"), nullable=False, index=True)
    log_datetime = Column(DateTime, default=datetime.datetime.now())
    log_type = Column(String(3))
    log_message = Column(Text)

    user = relationship(u"User")


class Apilog(Base):
    __tablename__ = "apilog"

    log_id = Column(Integer, primary_key=True)
    log_datetime = Column(DateTime)
    log_ip = Column(String(45))
    log_user = Column(ForeignKey(u"user.user_name"), nullable=False, index=True)
    log_uuid = Column(String(80))

    user = relationship(u"User")


class Assessment(Base):
    __tablename__ = "assessment"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    ass_cod = Column(String(80), primary_key=True, nullable=False)
    ass_desc = Column(String(120))
    ass_days = Column(Integer)
    ass_status = Column(Integer, server_default=text("'0'"))
    ass_final = Column(Integer, server_default=text("'0'"))

    project = relationship(u"Project")


class AssDetail(Base):
    __tablename__ = "assdetail"
    __table_args__ = (
        ForeignKeyConstraint(
            ["section_user", "section_project", "section_assessment", "section_id"],
            [
                u"asssection.user_name",
                u"asssection.project_cod",
                u"asssection.ass_cod",
                u"asssection.section_id",
            ],
            ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_name", "project_cod", "ass_cod"],
            [u"assessment.user_name", u"assessment.project_cod", u"assessment.ass_cod"],
            ondelete=u"CASCADE",
        ),
        Index(
            "fk_assessment_asssection1_idx",
            "section_user",
            "section_project",
            "section_id",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    ass_cod = Column(String(80), primary_key=True, nullable=False)
    question_id = Column(
        ForeignKey(u"question.question_id", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    section_user = Column(String(80), nullable=False)
    section_project = Column(String(80), nullable=False)
    section_assessment = Column(String(80), nullable=False)
    section_id = Column(Integer, nullable=False)
    question_order = Column(Integer)

    question = relationship(u"Question")
    asssection = relationship(u"Asssection")
    assessment = relationship(u"Assessment")


class Asssection(Base):
    __tablename__ = "asssection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod", "ass_cod"],
            [u"assessment.user_name", u"assessment.project_cod", u"assessment.ass_cod"],
            ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    ass_cod = Column(String(80), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(String(120))
    section_content = Column(Text)
    section_order = Column(Integer)
    section_color = Column(String(20))

    assessment = relationship(u"Assessment")


class Country(Base):
    __tablename__ = "country"

    cnty_cod = Column(String(3), primary_key=True)
    cnty_name = Column(String(120))


class Enumerator(Base):
    __tablename__ = "enumerator"
    __table_args__ = (
        ForeignKeyConstraint(["user_name"], [u"user.user_name"], ondelete=u"CASCADE"),
    )
    user_name = Column(String(80), primary_key=True, nullable=False)
    enum_id = Column(String(80), primary_key=True, nullable=False)
    enum_name = Column(String(120))
    enum_password = Column(String(80))
    enum_active = Column(Integer)

    project = relationship(u"User")


class PrjEnumerator(Base):
    __tablename__ = "prjenumerator"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["enum_user", "enum_id"],
            [u"enumerator.user_name", u"enumerator.enum_id"],
            ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    enum_user = Column(String(80), primary_key=True, nullable=False)
    enum_id = Column(String(80), primary_key=True, nullable=False)

    project = relationship(u"Project")
    enumerator = relationship(u"Enumerator")


class Products(Base):
    __tablename__ = "products"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )
    celery_taskid = Column(String(80), primary_key=True, nullable=False)
    process_name = Column(String(80), nullable=False)
    user_name = Column(String(80), nullable=False)
    project_cod = Column(String(80), nullable=False)
    product_id = Column(String(80), nullable=False)
    output_id = Column(String(80), nullable=False)
    output_mimetype = Column(String(80), nullable=False)
    datetime_added = Column(DateTime)
    project = relationship(u"Project")


class Tasks(Base):
    __tablename__ = "tasks"
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8"},)
    taskid = Column(String(80), primary_key=True, nullable=False)


class finishedTasks(Base):
    __tablename__ = "finishedtasks"
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8"},)
    taskid = Column(String(80), primary_key=True, nullable=False)
    taskerror = Column(Integer)


class storageErrors(Base):
    __tablename__ = "storageerrors"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )
    fileuid = Column(String(80), primary_key=True, nullable=False)
    error_datetime = Column(DateTime)
    user_name = Column(String(80), nullable=False)
    project_cod = Column(String(80), nullable=False)
    submission_type = Column(String(80))
    assessment_id = Column(String(80))
    command_executed = Column(Text)
    error_cod = Column(String(80))
    error_des = Column(Text)
    error_table = Column(String(120))
    project = relationship(u"Project")


class I18n(Base):
    __tablename__ = "i18n"

    lang_code = Column(String(5), primary_key=True)
    lang_name = Column(String(120))


class I18nAsssection(Base):
    __tablename__ = "i18n_asssection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod", "ass_cod", "section_id"],
            [
                u"asssection.user_name",
                u"asssection.project_cod",
                u"asssection.ass_cod",
                u"asssection.section_id",
            ],
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    ass_cod = Column(String(80), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    section_name = Column(String(120))
    section_content = Column(Text)

    i18n = relationship(u"I18n")
    asssection = relationship(u"Asssection")


class I18nPrjalia(Base):
    __tablename__ = "i18n_prjalias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod", "tech_id", "alias_id"],
            [
                u"prjalias.user_name",
                u"prjalias.project_cod",
                u"prjalias.tech_id",
                u"prjalias.alias_id",
            ],
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    alias_name = Column(String(120))

    i18n = relationship(u"I18n")
    prjalia = relationship(u"Prjalia")


class I18nProject(Base):
    __tablename__ = "i18n_project"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"], [u"project.user_name", u"project.project_cod"]
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    project_name = Column(String(120))
    project_abstract = Column(Text)

    i18n = relationship(u"I18n")
    project = relationship(u"Project")


class I18nQstoption(Base):
    __tablename__ = "i18n_qstoption"
    __table_args__ = (
        ForeignKeyConstraint(
            ["question_id", "value_code"],
            [u"qstoption.question_id", u"qstoption.value_code"],
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    question_id = Column(Integer, primary_key=True, nullable=False)
    value_code = Column(String(80), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    value_desc = Column(String(120))

    i18n = relationship(u"I18n")
    question = relationship(u"Qstoption")


class I18nQuestion(Base):
    __tablename__ = "i18n_question"

    question_id = Column(
        ForeignKey(u"question.question_id"), primary_key=True, nullable=False
    )
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    question_desc = Column(String(120))
    question_notes = Column(Text)
    question_unit = Column(String(120))
    question_posstm = Column(String(120))
    question_negstm = Column(String(120))

    i18n = relationship(u"I18n")
    question = relationship(u"Question")


class I18nRegsection(Base):
    __tablename__ = "i18n_regsection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod", "section_id"],
            [
                u"regsection.user_name",
                u"regsection.project_cod",
                u"regsection.section_id",
            ],
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    section_name = Column(String(120))
    section_content = Column(Text)

    i18n = relationship(u"I18n")
    regsection = relationship(u"Regsection")


class I18nTechalia(Base):
    __tablename__ = "i18n_techalias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tech_id", "alias_id"], [u"techalias.tech_id", u"techalias.alias_id"]
        ),
    )

    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    alias_name = Column(String(120))

    i18n = relationship(u"I18n")
    tech = relationship(u"Techalia")


class I18nTechnology(Base):
    __tablename__ = "i18n_technology"

    tech_id = Column(
        ForeignKey(u"technology.tech_id"), primary_key=True, nullable=False
    )
    lang_code = Column(
        ForeignKey(u"i18n.lang_code"), primary_key=True, nullable=False, index=True
    )
    tech_name = Column(String(45))

    i18n = relationship(u"I18n")
    tech = relationship(u"Technology")


class Package(Base):
    __tablename__ = "package"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    package_id = Column(Integer, primary_key=True, nullable=False)
    package_code = Column(String(45))
    package_image = Column(LargeBinary)

    project = relationship(u"Project")


class Pkgcomb(Base):
    __tablename__ = "pkgcomb"
    __table_args__ = (
        ForeignKeyConstraint(
            ["comb_user", "comb_project", "comb_code"],
            [
                u"prjcombination.user_name",
                u"prjcombination.project_cod",
                u"prjcombination.comb_code",
            ],
            ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_name", "project_cod", "package_id"],
            [u"package.user_name", u"package.project_cod", u"package.package_id"],
            ondelete=u"CASCADE",
        ),
        Index(
            "fk_pkgcomb_prjcombination1_idx", "comb_user", "comb_project", "comb_code"
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    package_id = Column(Integer, primary_key=True, nullable=False)
    comb_user = Column(String(80), primary_key=True, nullable=False)
    comb_project = Column(String(80), primary_key=True, nullable=False)
    comb_code = Column(Integer, primary_key=True, nullable=False)
    comb_order = Column(Integer)

    prjcombination = relationship(u"Prjcombination")
    package = relationship(u"Package")


class Prjalia(Base):
    __tablename__ = "prjalias"
    __table_args__ = (
        ForeignKeyConstraint(
            ["tech_used", "alias_used"],
            [u"techalias.tech_id", u"techalias.alias_id"],
            ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_name", "project_cod", "tech_id"],
            [u"prjtech.user_name", u"prjtech.project_cod", u"prjtech.tech_id"],
            ondelete=u"CASCADE",
        ),
        Index("fk_prjalias_techalias1_idx", "tech_used", "alias_used"),
        Index("fk_prjalias_prjtech1_idx", "user_name", "project_cod", "tech_id"),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    alias_name = Column(String(120))
    tech_used = Column(Integer)
    alias_used = Column(Integer)

    techalia = relationship(u"Techalia")
    prjtech = relationship(u"Prjtech")


class Prjcnty(Base):
    __tablename__ = "prjcnty"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    cnty_cod = Column(
        ForeignKey(u"country.cnty_cod", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    cnty_contact = Column(String(120))

    country = relationship(u"Country")
    project = relationship(u"Project")


class Prjcombdet(Base):
    __tablename__ = "prjcombdet"
    __table_args__ = (
        ForeignKeyConstraint(
            ["prjcomb_user", "prjcomb_project", "comb_code"],
            [
                u"prjcombination.user_name",
                u"prjcombination.project_cod",
                u"prjcombination.comb_code",
            ],
            ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_name", "project_cod", "tech_id", "alias_id"],
            [
                u"prjalias.user_name",
                u"prjalias.project_cod",
                u"prjalias.tech_id",
                u"prjalias.alias_id",
            ],
            ondelete=u"CASCADE",
        ),
        Index(
            "fk_prjcombdet_prjalias1_idx",
            "user_name",
            "project_cod",
            "tech_id",
            "alias_id",
        ),
    )

    prjcomb_user = Column(String(80), primary_key=True, nullable=False)
    prjcomb_project = Column(String(80), primary_key=True, nullable=False)
    comb_code = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    tech_id = Column(Integer, primary_key=True, nullable=False)
    alias_id = Column(Integer, primary_key=True, nullable=False)
    alias_order = Column(Integer)

    prjcombination = relationship(u"Prjcombination")
    prjalia = relationship(u"Prjalia")


class Prjcombination(Base):
    __tablename__ = "prjcombination"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    comb_code = Column(Integer, primary_key=True, nullable=False)
    comb_usable = Column(Integer)

    project = relationship(u"Project")
    prjalias = relationship(u"Prjalia", secondary="prjcombdet")


class Prjlang(Base):
    __tablename__ = "prjlang"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    lang_code = Column(
        ForeignKey(u"i18n.lang_code", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    lang_default = Column(Integer)

    i18n = relationship(u"I18n")
    project = relationship(u"Project")


class Prjtech(Base):
    __tablename__ = "prjtech"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    tech_id = Column(
        ForeignKey(u"technology.tech_id", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )

    tech = relationship(u"Technology")
    project = relationship(u"Project")


class Project(Base):
    __tablename__ = "project"

    user_name = Column(
        ForeignKey(u"user.user_name"), primary_key=True, nullable=False, index=True
    )
    project_cod = Column(String(80), primary_key=True, nullable=False)
    project_name = Column(String(120))
    project_abstract = Column(Text)
    project_tags = Column(Text)
    project_pi = Column(String(120))
    project_piemail = Column(String(120))
    project_active = Column(Integer, server_default=text("'1'"))
    project_public = Column(Integer, server_default=text("'0'"))
    project_dashboard = Column(Integer, server_default=text("'1'"))
    project_regstatus = Column(Integer, server_default=text("'0'"))
    project_assstatus = Column(Integer, server_default=text("'0'"))
    project_createcomb = Column(Integer, server_default=text("'0'"))
    project_createpkgs = Column(Integer, server_default=text("'0'"))
    project_numobs = Column(Integer, nullable=False, server_default=text("'0'"))
    project_numcom = Column(Integer, nullable=False)
    project_lat = Column(String(120), nullable=False)
    project_lon = Column(String(120), nullable=False)
    project_creationdate = Column(DateTime, nullable=False)
    project_localvariety = Column(Integer, server_default=text("'0'"))
    extra = Column(Text)

    user = relationship(u"User")


class Qstoption(Base):
    __tablename__ = "qstoption"
    __table_args__ = ({"mysql_engine": "InnoDB", "mysql_charset": "utf8"},)

    question_id = Column(
        ForeignKey(u"question.question_id", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
    )
    value_code = Column(String(80), primary_key=True, nullable=False)
    value_desc = Column(String(120))
    value_isother = Column(Integer, server_default=text("'0'"))
    value_isna = Column(Integer, server_default=text("'0'"))
    value_order = Column(Integer, server_default=text("'0'"))

    question = relationship(u"Question")


# class Qstprjopt(Base):
#     __tablename__ = 'qstprjopt'
#     __table_args__ = (
#         ForeignKeyConstraint(['parent_user', 'parent_project', 'parent_question', 'parent_value'], [u'qstprjopt.project_user', u'qstprjopt.project_cod', u'qstprjopt.question_id', u'qstprjopt.value_code'], ondelete=u'CASCADE'),
#         ForeignKeyConstraint(['project_user', 'project_cod'], [u'project.user_name', u'project.project_cod'], ondelete=u'CASCADE'),
#         Index('fk_qstprjopt_qstprjopt1_idx', 'parent_user', 'parent_project', 'parent_question', 'parent_value')
#     )
#
#     project_user = Column(String(80), primary_key=True, nullable=False)
#     project_cod = Column(String(80), primary_key=True, nullable=False)
#     question_id = Column(ForeignKey(u'question.question_id', ondelete=u'CASCADE'), primary_key=True, nullable=False, index=True)
#     value_code = Column(Integer, primary_key=True, nullable=False)
#     value_desc = Column(String(120))
#     parent_user = Column(String(80))
#     parent_project = Column(String(80))
#     parent_question = Column(Integer)
#     parent_value = Column(Integer)
#
#     parent = relationship(u'Qstprjopt', remote_side=[project_user, project_cod, question_id, value_code])
#     project = relationship(u'Project')
#     question = relationship(u'Question')


class Question_group(Base):
    __tablename__ = "qstgroups"
    __table_args__ = (
        ForeignKeyConstraint(["user_name"], [u"user.user_name"], ondelete=u"CASCADE"),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    qstgroups_id = Column(String(80), primary_key=True, nullable=False)
    qstgroups_name = Column(String(120))

    user = relationship(u"User")


class Question(Base):
    __tablename__ = "question"
    __table_args__ = (
        ForeignKeyConstraint(
            ["qstgroups_user", "qstgroups_id"],
            [u"qstgroups.user_name", u"qstgroups.qstgroups_id"],
            ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )
    question_id = Column(Integer, primary_key=True)
    question_code = Column(String(120))
    question_desc = Column(String(120))
    question_notes = Column(Text)
    question_unit = Column(String(120))
    question_dtype = Column(Integer)
    question_cmp = Column(String(120))
    question_reqinreg = Column(Integer, server_default=text("'0'"))
    question_reqinasses = Column(Integer, server_default=text("'0'"))
    question_alwaysinreg = Column(Integer, server_default=text("'0'"))
    question_alwaysinasse = Column(Integer, server_default=text("'0'"))
    question_optperprj = Column(Integer, server_default=text("'0'"))
    user_name = Column(ForeignKey(u"user.user_name"), index=True)
    question_posstm = Column(String(120))
    question_negstm = Column(String(120))
    question_twoitems = Column(String(120))
    question_moreitems = Column(String(120))
    question_perfstmt = Column(String(120))
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

    qstgroups_user = Column(String(80), nullable=True)
    qstgroups_id = Column(String(80), nullable=True)

    extra = Column(Text)
    user = relationship(u"User")
    # qstgroups = relationship(u'Question_group')


class Registry(Base):
    __tablename__ = "registry"
    __table_args__ = (
        ForeignKeyConstraint(
            ["section_user", "section_project", "section_id"],
            [
                u"regsection.user_name",
                u"regsection.project_cod",
                u"regsection.section_id",
            ],
            ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
        Index(
            "fk_registry_regsection1_idx",
            "section_user",
            "section_project",
            "section_id",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    question_id = Column(
        ForeignKey(u"question.question_id", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    section_user = Column(String(80))
    section_project = Column(String(80))
    section_id = Column(Integer)
    question_order = Column(Integer)

    question = relationship(u"Question")
    regsection = relationship(u"Regsection")
    project = relationship(u"Project")


class Regsection(Base):
    __tablename__ = "regsection"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            ondelete=u"CASCADE",
        ),
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    section_id = Column(Integer, primary_key=True, nullable=False)
    section_name = Column(String(45))
    section_content = Column(Text)
    section_order = Column(Integer)
    section_color = Column(String(20))

    project = relationship(u"Project")


class Sector(Base):
    __tablename__ = "sector"

    sector_cod = Column(Integer, primary_key=True)
    sector_name = Column(String(120))


class Techalia(Base):
    __tablename__ = "techalias"

    tech_id = Column(
        ForeignKey(u"technology.tech_id", ondelete=u"CASCADE"),
        primary_key=True,
        nullable=False,
        index=True,
    )
    alias_id = Column(Integer, primary_key=True, nullable=False)
    alias_name = Column(String(120))

    tech = relationship(u"Technology")


class Technology(Base):
    __tablename__ = "technology"

    tech_id = Column(Integer, primary_key=True)
    tech_name = Column(String(45))
    user_name = Column(ForeignKey(u"user.user_name", ondelete=u"CASCADE"), index=True)

    user = relationship(u"User")
    project = relationship(u"Project", secondary="prjtech")


class User(Base):
    __tablename__ = "user"

    user_name = Column(String(80), primary_key=True)
    user_fullname = Column(String(120))
    user_password = Column(String(80))
    user_organization = Column(String(120))
    user_email = Column(String(120))
    user_apikey = Column(String(45))
    user_about = Column(Text)
    user_cnty = Column(ForeignKey(u"country.cnty_cod"), nullable=False, index=True)
    user_sector = Column(ForeignKey(u"sector.sector_cod"), nullable=False, index=True)
    user_active = Column(Integer, server_default=text("'1'"))
    user_joindate = Column(DateTime, default=datetime.datetime.now())
    extra = Column(Text)

    country = relationship(u"Country")
    sector = relationship(u"Sector")


class RegistryJsonLog(Base):
    __tablename__ = "registry_jsonlog"
    __table_args__ = (

        ForeignKeyConstraint(
            ["user_name", "project_cod"],
            [u"project.user_name", u"project.project_cod"],
            #ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
        ["enum_user", "enum_id"],
        [u"enumerator.user_name", u"enumerator.enum_id"],
        #ondelete=u"CASCADE",
    )
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    log_id = Column(Unicode(64), primary_key=True, nullable=False)
    enum_user = Column(String(80), primary_key=True, nullable=False)
    enum_id = Column(String(80), primary_key=True, nullable=False)

    log_dtime = Column(DateTime)
    json_file = Column(UnicodeText)
    log_file = Column(UnicodeText)
    status = Column(Integer)

    project = relationship(u"Project")
    enumerator = relationship(u"Enumerator")


class AssessmentJsonLog(Base):
    __tablename__ = "assesment_jsonlog"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_name", "project_cod", "ass_cod"],
            [u"assessment.user_name", u"assessment.project_cod", u"assessment.ass_cod"],
            #ondelete=u"CASCADE",
        ),
        ForeignKeyConstraint(
            ["enum_user", "enum_id"],
            [u"enumerator.user_name", u"enumerator.enum_id"],
            #ondelete=u"CASCADE",
        ),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8"},
    )

    user_name = Column(String(80), primary_key=True, nullable=False)
    project_cod = Column(String(80), primary_key=True, nullable=False)
    ass_cod = Column(String(80), primary_key=True, nullable=False)
    log_id = Column(Unicode(64), primary_key=True, nullable=False)
    enum_user = Column(String(80), primary_key=True, nullable=False)
    enum_id = Column(String(80), primary_key=True, nullable=False)
    log_dtime = Column(DateTime)
    json_file = Column(UnicodeText)
    log_file = Column(UnicodeText)
    status = Column(Integer)

    assessment = relationship(u"Assessment")
    enumerator = relationship(u"Enumerator")
