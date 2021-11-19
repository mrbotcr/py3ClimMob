from climmob.config.celery_app import celeryApp
from climmob.config.celery_class import celeryTask
import transaction
from sqlalchemy.orm import configure_mappers
from climmob.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    initialize_schema,
    Project,
    Prjcombination,
    Package,
    Pkgcomb,
    Assessment
)
import gettext
import os
import shutil as sh
from subprocess import check_call, CalledProcessError

@celeryApp.task(bind=True, base=celeryTask, soft_time_limit=7200, time_limit=7200)
def createRandomization(self, locale, path, settings, projectId, userOwner, projectCod):
    if os.path.exists(path):
        sh.rmtree(path)

    PATH_lo = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )
    this_file_path = PATH_lo + "/locale"
    try:
        es = gettext.translation(
            "climmob", localedir=this_file_path, languages=[locale]
        )
        es.install()
        _ = es.gettext
    except:
        locale = "en"
        es = gettext.translation(
            "climmob", localedir=this_file_path, languages=[locale]
        )
        es.install()
        _ = es.gettext

    os.makedirs(path)

    rfile = os.path.join(
        settings["user.repository"],
        *[userOwner, projectCod, "r", "comb.txt"]
    )
    rout = os.path.join(
        path,
        "comb_2.txt"
    )

    #cnf_file = settings["mysql.cnf"]

    engine = get_engine(settings)
    session_factory = get_session_factory(engine)

    with transaction.manager:
        db_session = get_tm_session(session_factory, transaction.manager)
        configure_mappers()
        initialize_schema()

        prjData = (
            db_session.query(Project).filter(Project.project_id == projectId).first()
        )
        # Only create the packages if its needed
        #if prjData.project_createpkgs == 2:
        combData = (
            db_session.query(Prjcombination)
            .filter(Prjcombination.project_id == projectId)
            .filter(Prjcombination.comb_usable == 1)
            .all()
        )

        combinations = []
        availability = []
        for comb in combData:
            combinations.append(comb.comb_code)
            availability.append(comb.quantity_available)

        if combinations:
            args = []
            args.append("Rscript")
            args.append(settings["r.random.script"])
            args.append(str(prjData.project_numobs))
            args.append("inames=c(" + ", ".join(map(str, combinations)) + ")")
            args.append("iavailability=c(" + ", ".join(map(str, availability)) + ")")
            args.append(rout)

            try:
                if self.is_aborted():
                    return ""

                db_session.query(Package).filter(
                    Package.project_id == projectId
                ).delete()

                if self.is_aborted():
                    return ""

                check_call(args)

                if self.is_aborted():
                    return ""
                if os.path.exists(rout):
                    with open(rout) as fp:
                        lines = fp.readlines()
                        pkgid = 1
                        for line in lines:

                            if self.is_aborted():
                                return ""

                            newPackage = Package(
                                project_id=projectId,
                                package_id=pkgid,
                                package_code=_("Package") + " #" + str(pkgid),
                            )
                            db_session.add(newPackage)

                            a_package = line.replace('"', "")
                            combs = a_package.split("\t")
                            combid = 1
                            for comb in combs:

                                if self.is_aborted():
                                    return ""

                                newPkgcomb = Pkgcomb(
                                    project_id=projectId,
                                    package_id=pkgid,
                                    comb_project_id=projectId,
                                    comb_code=int(comb),
                                    comb_order=combid,
                                )
                                db_session.add(newPkgcomb)
                                combid = combid + 1
                            pkgid = pkgid + 1

                        if self.is_aborted():
                            return ""

                        db_session.query(Project).filter(
                            Project.project_id == projectId
                        ).update({"project_createpkgs": 0})

                        #setRegistryStatus(userOwner, projectCod, projectId, 0, request)
                        db_session.query(Project).filter(Project.project_id == projectId).update({"project_regstatus": 0})
                        db_session.query(Project).filter(Project.project_id == projectId).update({"project_assstatus": 0})
                        db_session.query(Assessment).filter(Assessment.project_id == projectId).update({"ass_status": 0})

                        assessments = (
                            db_session.query(Assessment)
                            .filter(Assessment.project_id == projectId)
                            .all()
                        )
                        for assessment in assessments:
                            try:
                                path = os.path.join(settings["user.repository"],*[userOwner, projectCod, "data", "ass", assessment.ass_cod])
                                sh.rmtree(path)
                            except:
                                pass
                else:
                    db_session.query(Project).filter(
                        Project.project_id == projectId
                    ).update({"project_createpkgs": 3})

            except CalledProcessError as e:
                db_session.query(Project).filter(
                    Project.project_id == projectId
                ).update({"project_createpkgs": 3})

                msg = "Error running R randomization file \n"
                msg = msg + "Commang: " + " ".join(args) + "\n"
                # msg = msg + "Error: \n"
                # msg = msg + str(e)
                print(msg)
                return False
        #else:
        #    print("No se deben de crear paquetes")

    engine.dispose()

