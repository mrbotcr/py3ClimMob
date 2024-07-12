import zope.sqlalchemy
from sqlalchemy import engine_from_config
from sqlalchemy.orm import configure_mappers
from sqlalchemy.orm import sessionmaker

# import or define all models here to ensure they are attached to the
# Base.metadata prior to any initialization routines
from climmob.models.climmobv4 import (
    Base,
    Activitylog,
    Apilog,
    Country,
    Enumerator,
    I18n,
    I18nPrjalia,
    I18nProject,
    I18nQuestion,
    I18nRegsection,
    I18nTechalia,
    I18nTechnology,
    I18nQstoption,
    I18nUser,
    I18nGeneralPhrases,
    Package,
    Pkgcomb,
    Prjalia,
    Prjcnty,
    Prjcombdet,
    Prjcombination,
    Prjlang,
    Prjtech,
    Project,
    Question,
    Registry,
    Regsection,
    Sector,
    Techalia,
    Technology,
    User,
    PrjEnumerator,
    Products,
    I18nAsssection,
    Assessment,
    Asssection,
    AssDetail,
    Qstoption,
    I18nQstoption,
    Tasks,
    finishedTasks,
    RegistryJsonLog,
    AssessmentJsonLog,
    storageErrors,
    Chat,
    userProject,
    CropTaxonomy,
    I18nCropTaxonomy,
    generalPhrases,
    ProjectMetadata,
    ExtraForm,
    ExtraFormAnswer,
    ProjectType,
    ProjectStatus,
    I18nProjectType,
    I18nProjectStatus,
)
from climmob.models.schema import *

#

# Qstprjopt

# run configure_mappers after defining all of the models to ensure
# all relationships can be setup
configure_mappers()


def get_engine(settings, prefix="sqlalchemy."):
    pool_size = int(settings.get("pool.size", "30"))
    max_overflow = int(settings.get("pool.max.overflow", "10"))
    pool_recycle = int(settings.get("pool.recycle", "2000"))
    return engine_from_config(
        settings,
        prefix,
        pool_recycle=pool_recycle,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )


def get_session_factory(engine):
    factory = sessionmaker()
    factory.configure(bind=engine)
    Base.metadata.bind = engine
    return factory


def get_tm_session(session_factory, transaction_manager):
    """
    Get a ``sqlalchemy.orm.Session`` instance backed by a transaction.

    This function will hook the session to the transaction manager which
    will take care of committing any changes.

    - When using pyramid_tm it will automatically be committed or aborted
      depending on whether an exception is raised.

    - When using scripts you should wrap the session in a manager yourself.
      For example::

          import transaction

          engine = get_engine(settings)
          session_factory = get_session_factory(engine)
          with transaction.manager:
              dbsession = get_tm_session(session_factory, transaction.manager)

    """
    dbsession = session_factory()
    zope.sqlalchemy.register(dbsession, transaction_manager=transaction_manager)
    return dbsession


def initializeClimmobDB(config):
    """
    Initialize the model for a Pyramid app.

    Activate this setup using ``config.include('climmob.models')``.

    """
    settings = config.get_settings()

    # use pyramid_tm to hook the transaction lifecycle to the request
    config.include("pyramid_tm")

    session_factory = get_session_factory(get_engine(settings))
    config.registry["dbsession_factory"] = session_factory
    config.registry["dbsession_metadata"] = Base.metadata

    # make request.dbsession available for use in Pyramid
    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(session_factory, r.tm),
        "dbsession",
        reify=True,
    )
    # Initializes the schema
    initialize_schema()


def initializeRepositoryDB(config):
    settings = config.get_settings()
    repository_session_factory = get_session_factory(
        get_engine(settings, "repository.")
    )
    config.registry["repository_dbsession_factory"] = repository_session_factory

    config.add_request_method(
        # r.tm is the transaction manager used by pyramid_tm
        lambda r: get_tm_session(repository_session_factory, r.tm),
        "repsession",
        reify=True,
    )


def includeme(config):
    initializeClimmobDB(config)
    initializeRepositoryDB(config)
