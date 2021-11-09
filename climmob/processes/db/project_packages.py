from ...models import Project, Prjcombination, Package, Pkgcomb
import numpy as np
from subprocess import check_call, CalledProcessError
from itertools import zip_longest as izip, chain, repeat
import pprint
from .registry import setRegistryStatus
import os
from .project_combinations import getCombinationsUsableInProject

__all__ = [
    "create_packages_with_r",
    "getPackages",
    "projectHasPackages",
    "createExtraPackages",
]


def grouper(n, iterable, padvalue=None):
    return izip(*[chain(iterable, repeat(padvalue, n - 1))] * n)


def projectHasPackages(projectId, request):
    data = (
        request.dbsession.query(Package).filter(Package.project_id == projectId).first()
    )
    if data is not None:
        return True
    else:
        return False


def getPackages(userOwner, projectId, request):

    sql = (
        "SELECT project.project_cod,project.project_numcom,count(prjtech.tech_id) as ttech FROM "
        "project,prjtech WHERE "
        "project.project_id = prjtech.project_id AND "
        "project.project_id = '" + projectId + "' "
        "GROUP BY project.project_cod"
    )

    pkgdetails = request.dbsession.execute(sql).fetchone()
    ncombs = pkgdetails.project_numcom

    sql = (
        "SELECT * FROM"
        "  ("
        "      ("
        "          SELECT"
        "          user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate,project.project_numcom,"
        "          pkgcomb.package_id,package.package_code,"
        "          COALESCE(t.tech_name,technology.tech_name) as tech_name,COALESCE(i.alias_name,techalias.alias_name) as alias_name,pkgcomb.comb_order, technology.tech_id FROM "
        "          pkgcomb,package,prjcombination,prjcombdet,prjalias,"
        "          user,project, technology,techalias"
        "          LEFT JOIN i18n_techalias i "
        "          ON        techalias.tech_id = i.tech_id "
        "          AND       techalias.alias_id = i.alias_id "
        "          AND       i.lang_code = '" + request.locale_name + "' "
        "          LEFT JOIN i18n_technology t "
        "          ON        techalias.tech_id = t.tech_id "
        "          AND       t.lang_code = '" + request.locale_name + "' "
        "          WHERE "
        "          user.user_name = '" + userOwner + "' AND "
        "          pkgcomb.project_id = project.project_id AND "
        "          pkgcomb.project_id = package.project_id AND "
        "          pkgcomb.package_id = package.package_id AND "
        "          pkgcomb.comb_project_id = prjcombination.project_id AND "
        "          pkgcomb.comb_code = prjcombination.comb_code AND "
        "          prjcombination.project_id = prjcombdet.project_id_tech AND "
        "          prjcombination.comb_code = prjcombdet.comb_code AND "
        "          prjcombdet.project_id = prjalias.project_id AND "
        "          prjcombdet.tech_id = prjalias.tech_id AND "
        "          prjcombdet.alias_id = prjalias.alias_id AND "
        "          prjalias.tech_used = techalias.tech_id AND "
        "          prjalias.alias_used = techalias.alias_id AND "
        "          techalias.tech_id = technology.tech_id AND "
        "          prjalias.tech_used IS NOT NULL AND "
        "          pkgcomb.project_id = '" + projectId + "'"
        "          ORDER BY pkgcomb.package_id,pkgcomb.comb_order"
        "      )"
        "      UNION"
        "      ("
        "          SELECT"
        "          user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate, project.project_numcom,"
        "          pkgcomb.package_id,package.package_code,"
        "          COALESCE(t.tech_name,technology.tech_name) as tech_name,prjalias.alias_name,pkgcomb.comb_order, technology.tech_id FROM"
        "          pkgcomb,package,prjcombination,prjcombdet,prjalias,"
        "          user,project,technology "
        "          LEFT JOIN i18n_technology t "
        "          ON        technology.tech_id = t.tech_id "
        "          AND       t.lang_code = '" + request.locale_name + "' "
        "          WHERE "
        "          user.user_name = '" + userOwner + "' AND "
        "          pkgcomb.project_id = project.project_id AND "
        "          pkgcomb.project_id = package.project_id AND "
        "          pkgcomb.package_id = package.package_id AND "
        "          pkgcomb.comb_project_id = prjcombination.project_id AND "
        "          pkgcomb.comb_code = prjcombination.comb_code AND "
        "          prjcombination.project_id = prjcombdet.project_id_tech AND "
        "          prjcombination.comb_code = prjcombdet.comb_code AND "
        "          prjcombdet.project_id = prjalias.project_id AND "
        "          prjcombdet.tech_id = prjalias.tech_id AND "
        "          prjcombdet.alias_id = prjalias.alias_id AND "
        "          prjcombdet.tech_id = technology.tech_id AND "
        "          prjalias.tech_used IS NULL AND "
        "          pkgcomb.project_id = '" + projectId + "'"
        "          ORDER BY pkgcomb.package_id,pkgcomb.comb_order"
        "      )"
        "  ) AS T ORDER BY T.package_id,T.comb_order,T.tech_name"
    )
    pkgdetails = request.dbsession.execute(sql).fetchall()

    packages = []
    pkgcode = -999
    for pkg in pkgdetails:
        if pkgcode != pkg.package_id:
            aPackage = {}
            pkgcode = pkg.package_id
            aPackage["user_name"] = pkg.user_name
            aPackage["user_fullname"] = pkg["user_fullname"]
            aPackage["project_name"] = pkg["project_name"]
            aPackage["project_pi"] = pkg["project_pi"]
            aPackage["project_piemail"] = pkg["project_piemail"]
            aPackage["project_numobs"] = pkg["project_numobs"]
            aPackage["project_numcom"] = pkg["project_numcom"]
            aPackage["project_lat"] = pkg["project_lat"]
            aPackage["project_lon"] = pkg["project_lon"]
            aPackage["project_creationdate"] = pkg["project_creationdate"]
            aPackage["package_id"] = pkg["package_id"]
            aPackage["package_code"] = pkg["package_code"]
            aPackage["combs"] = []
            for x in range(0, ncombs):
                aPackage["combs"].append({})
            aPackage["combs"][pkg.comb_order - 1]["comb_order"] = pkg.comb_order
            aPackage["combs"][pkg.comb_order - 1]["technologies"] = []
            aPackage["combs"][pkg.comb_order - 1]["technologies"].append(
                {
                    "tech_id": pkg.tech_id,
                    "tech_name": pkg.tech_name,
                    "alias_name": pkg.alias_name,
                }
            )
            packages.append(aPackage)
        else:
            try:
                packages[len(packages) - 1]["combs"][pkg.comb_order - 1][
                    "comb_order"
                ] = pkg.comb_order
                packages[len(packages) - 1]["combs"][pkg.comb_order - 1][
                    "technologies"
                ].append(
                    {
                        "tech_id": pkg.tech_id,
                        "tech_name": pkg.tech_name,
                        "alias_name": pkg.alias_name,
                    }
                )
            except:
                packages[len(packages) - 1]["combs"][pkg.comb_order - 1][
                    "technologies"
                ] = []
                packages[len(packages) - 1]["combs"][pkg.comb_order - 1][
                    "technologies"
                ].append(
                    {
                        "tech_id": pkg.tech_id,
                        "tech_name": pkg.tech_name,
                        "alias_name": pkg.alias_name,
                    }
                )

    return ncombs, packages


def create_packages_with_r(userOwner, projectId, projectCod, request):
    _ = request.translate

    path = os.path.join(
        request.registry.settings["user.repository"], *[userOwner, projectCod, "r"]
    )
    if not os.path.exists(path):
        os.makedirs(path)
    rfile = os.path.join(
        request.registry.settings["user.repository"],
        *[userOwner, projectCod, "r", "comb.txt"]
    )
    rout = os.path.join(
        request.registry.settings["user.repository"],
        *[userOwner, projectCod, "r", "comb_2.txt"]
    )

    prjData = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    # Only create the packages if its needed
    if prjData.project_createpkgs == 1:
        combData = (
            request.dbsession.query(Prjcombination)
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
            args.append(request.registry.settings["r.random.script"])
            args.append(str(prjData.project_numcom))
            args.append(str(prjData.project_numobs))
            args.append(str(len(combinations)))
            args.append("inames=c(" + ", ".join(map(str, combinations)) + ")")
            #args.append("iavailability=c(" + ", ".join(map(str, availability)) + ")")
            args.append(rout)

            # print(' '.join(map(str, args)))
            try:
                request.dbsession.query(Package).filter(
                    Package.project_id == projectId
                ).delete()

                with open(rout) as fp:
                    lines = fp.readlines()
                    pkgid = 1
                    for line in lines:
                        newPackage = Package(
                            project_id=projectId,
                            package_id=pkgid,
                            package_code=_("Package") + " #" + str(pkgid),
                        )
                        request.dbsession.add(newPackage)

                        a_package = line.replace('"', "")
                        combs = a_package.split("\t")
                        combid = 1
                        for comb in combs:
                            newPkgcomb = Pkgcomb(
                                project_id=projectId,
                                package_id=pkgid,
                                comb_project_id=projectId,
                                comb_code=int(comb),
                                comb_order=combid,
                            )
                            request.dbsession.add(newPkgcomb)
                            combid = combid + 1
                        pkgid = pkgid + 1

                    request.dbsession.query(Project).filter(
                        Project.project_id == projectId
                    ).update({"project_createpkgs": 0})

                    setRegistryStatus(userOwner, projectCod, projectId, 0, request)

            except CalledProcessError as e:
                msg = "Error running R randomization file \n"
                msg = msg + "Commang: " + " ".join(args) + "\n"
                msg = msg + "Error: \n"
                msg = msg + str(e)
                print(msg)
                return False


def createExtraPackages(
    userOwner, projectId, projectCode, request, numCom, numObsExtra, numObsNow
):

    path = os.path.join(
        request.registry.settings["user.repository"], *[userOwner, projectCode, "r"]
    )
    if not os.path.exists(path):
        os.makedirs(path)

    rout = os.path.join(
        request.registry.settings["user.repository"],
        *[userOwner, projectCode, "r", "comb_2.txt"]
    )

    combData = getCombinationsUsableInProject(projectId, request)

    combinations = []
    for comb in combData:
        combinations.append(comb.comb_code)
    if combinations:
        args = []
        args.append("Rscript")
        args.append(request.registry.settings["r.random.script"])
        args.append(str(numCom))
        args.append(str(numObsExtra))
        args.append(str(len(combinations)))
        args.append("inames=c(" + ", ".join(map(str, combinations)) + ")")
        args.append(rout)

        try:
            check_call(args)
            with open(rout) as fp:
                lines = fp.readlines()
                pkgid = numObsNow + 1
                for line in lines:
                    newPackage = Package(
                        project_id=projectId,
                        package_id=pkgid,
                        package_code="Package #" + str(pkgid),
                    )
                    request.dbsession.add(newPackage)

                    a_package = line.replace('"', "")
                    combs = a_package.split("\t")
                    combid = 1
                    for comb in combs:
                        newPkgcomb = Pkgcomb(
                            project_id=projectId,
                            package_id=pkgid,
                            comb_project_id=projectId,
                            comb_code=int(comb),
                            comb_order=combid,
                        )
                        request.dbsession.add(newPkgcomb)
                        combid = combid + 1
                    pkgid = pkgid + 1

                request.dbsession.query(Project).filter(
                    Project.project_id == projectId
                ).update({"project_numobs": int(numObsExtra) + int(numObsNow)})

            return True, ""

        except CalledProcessError as e:
            msg = "Error running R randomization file \n"
            msg = msg + "Commang: " + " ".join(args) + "\n"
            msg = msg + "Error: \n"
            msg = msg + str(e)
            return False, msg


def createPackages(userOwner, projectCod, projectId, request):
    prjData = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    # Only create the packages if its needed
    if prjData.project_createpkgs == 1:
        combData = (
            request.dbsession.query(Prjcombination)
            .filter(Prjcombination.project_id == projectId)
            .filter(Prjcombination.comb_usable == 1)
            .all()
        )
        combinations = []
        for comb in combData:
            combinations.append(comb.comb_code)
        if combinations:
            observations = []
            for pos in range(1, prjData.project_numobs * prjData.project_numcom + 1):
                observations.append(pos)
            pcomb = np.random.permutation(combinations)
            pobs = np.random.permutation(observations)

            final = []
            for i in range(1, prjData.project_numobs * prjData.project_numcom + 1):
                final.append({"obs": pobs[i - 1], "cmb": pcomb[i % len(combinations)]})

            allComb = []
            for f in final:
                allComb.append(f["cmb"])

            groups = grouper(prjData.project_numcom, allComb, -1)
            groups = list(groups)

            p = 0
            for grp in groups:
                groups[p] = np.asarray(grp, dtype=np.int16).tolist()
                p += 1

            # The combination in line 88 does not take into consideration the position inside a group
            # Now we shuffle the group
            numcomArray = []
            for p in range(0, prjData.project_numcom):
                numcomArray.append(p)
            p = 0
            for grp in groups:
                pposition = np.random.permutation(numcomArray)
                temp = []
                for t in grp:
                    temp.append(t)
                for t in range(0, prjData.project_numcom):
                    groups[p][t] = temp[pposition[t]]
                p += 1

            # Delete all packages
            request.dbsession.query(Package).filter(
                Package.project_id == projectId
            ).delete()
            pkgid = 1

            print("*******************************20")
            pprint.pprint(groups)
            print("*******************************20")

            for grp in groups:
                newPackage = Package(
                    project_id=projectId,
                    package_id=pkgid,
                    package_code="Package #" + str(pkgid),
                )
                request.dbsession.add(newPackage)
                combid = 1
                for comb in grp:
                    newPkgcomb = Pkgcomb(
                        project_id=projectId,
                        package_id=pkgid,
                        comb_project_id=projectId,
                        comb_code=int(comb),
                        comb_order=combid,
                    )
                    request.dbsession.add(newPkgcomb)
                    combid += 1
                pkgid += 1

            request.dbsession.query(Project).filter(
                Project.project_id == projectId
            ).update({"project_createpkgs": 0})

            setRegistryStatus(userOwner, projectCod, projectId, 0, request)
