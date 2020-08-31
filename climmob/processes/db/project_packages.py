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


def projectHasPackages(user, project, request):
    data = (
        request.dbsession.query(Package)
        .filter(Package.user_name == user)
        .filter(Package.project_cod == project)
        .first()
    )
    if data is not None:
        return True
    else:
        return False


def getPackages(user, project, request):

    sql = (
        "SELECT project.project_cod,project.project_numcom,count(prjtech.tech_id) as ttech FROM "
        "project,prjtech WHERE "
        "project.user_name = prjtech.user_name AND "
        "project.project_cod = prjtech.project_cod AND "
        "project.user_name = '" + user + "' AND "
        "project.project_cod = '" + project + "' "
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
        "          technology.tech_name,techalias.alias_name,pkgcomb.comb_order, technology.tech_id FROM"
        "          pkgcomb,package,prjcombination,prjcombdet,prjalias,techalias,"
        "          technology,user,project WHERE"
        "          pkgcomb.user_name = user.user_name AND"
        "          pkgcomb.user_name = project.user_name AND"
        "          pkgcomb.project_cod = project.project_cod AND"
        "          pkgcomb.user_name = package.user_name AND"
        "          pkgcomb.project_cod = package.project_cod AND"
        "          pkgcomb.package_id = package.package_id AND"
        "          pkgcomb.comb_user = prjcombination.user_name AND"
        "          pkgcomb.comb_project = prjcombination.project_cod AND"
        "          pkgcomb.comb_code = prjcombination.comb_code AND"
        "          prjcombination.user_name = prjcombdet.prjcomb_user AND"
        "          prjcombination.project_cod = prjcombdet.prjcomb_project AND"
        "          prjcombination.comb_code = prjcombdet.comb_code AND"
        "          prjcombdet.user_name = prjalias.user_name AND"
        "          prjcombdet.project_cod = prjalias.project_cod AND"
        "          prjcombdet.tech_id = prjalias.tech_id AND"
        "          prjcombdet.alias_id = prjalias.alias_id AND"
        "          prjalias.tech_used = techalias.tech_id AND"
        "          prjalias.alias_used = techalias.alias_id AND"
        "          techalias.tech_id = technology.tech_id AND"
        "          prjalias.tech_used IS NOT NULL AND"
        "          pkgcomb.user_name = '" + user + "' AND"
        "          pkgcomb.project_cod = '" + project + "'"
        "          ORDER BY pkgcomb.package_id,pkgcomb.comb_order"
        "      )"
        "      UNION"
        "      ("
        "          SELECT"
        "          user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate, project.project_numcom,"
        "          pkgcomb.package_id,package.package_code,"
        "          technology.tech_name,prjalias.alias_name,pkgcomb.comb_order, technology.tech_id FROM"
        "          pkgcomb,package,prjcombination,prjcombdet,prjalias,"
        "          technology,user,project WHERE"
        "          pkgcomb.user_name = user.user_name AND"
        "          pkgcomb.user_name = project.user_name AND"
        "          pkgcomb.project_cod = project.project_cod AND"
        "          pkgcomb.user_name = package.user_name AND"
        "          pkgcomb.project_cod = package.project_cod AND"
        "          pkgcomb.package_id = package.package_id AND"
        "          pkgcomb.comb_user = prjcombination.user_name AND"
        "          pkgcomb.comb_project = prjcombination.project_cod AND"
        "          pkgcomb.comb_code = prjcombination.comb_code AND"
        "          prjcombination.user_name = prjcombdet.prjcomb_user AND"
        "          prjcombination.project_cod = prjcombdet.prjcomb_project AND"
        "          prjcombination.comb_code = prjcombdet.comb_code AND"
        "          prjcombdet.user_name = prjalias.user_name AND"
        "          prjcombdet.project_cod = prjalias.project_cod AND"
        "          prjcombdet.tech_id = prjalias.tech_id AND"
        "          prjcombdet.alias_id = prjalias.alias_id AND"
        "          prjcombdet.tech_id = technology.tech_id AND"
        "          prjalias.tech_used IS NULL AND"
        "          pkgcomb.user_name = '" + user + "' AND"
        "          pkgcomb.project_cod = '" + project + "'"
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


def create_packages_with_r(user, project, request):
    path = os.path.join(
        request.registry.settings["user.repository"], *[user, project, "r"]
    )
    if not os.path.exists(path):
        os.makedirs(path)
    rfile = os.path.join(
        request.registry.settings["user.repository"], *[user, project, "r", "comb.txt"]
    )
    rout = os.path.join(
        request.registry.settings["user.repository"],
        *[user, project, "r", "comb_2.txt"]
    )

    prjData = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    # Only create the packages if its needed
    if prjData.project_createpkgs == 1:
        combData = (
            request.dbsession.query(Prjcombination)
            .filter(Prjcombination.user_name == user)
            .filter(Prjcombination.project_cod == project)
            .filter(Prjcombination.comb_usable == 1)
            .all()
        )

        combinations = []
        for comb in combData:
            combinations.append(comb.comb_code)
        if combinations:

            args = []
            args.append("Rscript")
            args.append(request.registry.settings["r.random.script"])
            args.append(str(prjData.project_numcom))
            args.append(str(prjData.project_numobs))
            args.append(str(len(combinations)))
            args.append("inames=c(" + ", ".join(map(str, combinations)) + ")")
            args.append(rout)

            # print(' '.join(map(str, args)))
            try:
                check_call(args)
                request.dbsession.query(Package).filter(
                    Package.user_name == user
                ).filter(Package.project_cod == project).delete()

                with open(rout) as fp:
                    lines = fp.readlines()
                    pkgid = 1
                    for line in lines:
                        newPackage = Package(
                            user_name=user,
                            project_cod=project,
                            package_id=pkgid,
                            package_code="Package #" + str(pkgid),
                        )
                        request.dbsession.add(newPackage)

                        a_package = line.replace('"', "")
                        combs = a_package.split("\t")
                        combid = 1
                        for comb in combs:
                            newPkgcomb = Pkgcomb(
                                user_name=user,
                                project_cod=project,
                                package_id=pkgid,
                                comb_user=user,
                                comb_project=project,
                                comb_code=int(comb),
                                comb_order=combid,
                            )
                            request.dbsession.add(newPkgcomb)
                            combid = combid + 1
                        pkgid = pkgid + 1

                    request.dbsession.query(Project).filter(
                        Project.user_name == user
                    ).filter(Project.project_cod == project).update(
                        {"project_createpkgs": 0}
                    )

                    setRegistryStatus(user, project, 0, request)

            except CalledProcessError as e:
                msg = "Error running R randomization file \n"
                msg = msg + "Commang: " + " ".join(args) + "\n"
                msg = msg + "Error: \n"
                msg = msg + str(e)
                print(msg)
                return False


def createExtraPackages(user, project, request, numCom, numObsExtra, numObsNow):
    #print(numCom)
    #print(numObsExtra)
    #print(numObsNow)
    path = os.path.join(
        request.registry.settings["user.repository"], *[user, project, "r"]
    )
    if not os.path.exists(path):
        os.makedirs(path)

    rout = os.path.join(
        request.registry.settings["user.repository"],
        *[user, project, "r", "comb_2.txt"]
    )

    combData = getCombinationsUsableInProject(user, project, request)

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
                        user_name=user,
                        project_cod=project,
                        package_id=pkgid,
                        package_code="Package #" + str(pkgid),
                    )
                    request.dbsession.add(newPackage)

                    a_package = line.replace('"', "")
                    combs = a_package.split("\t")
                    combid = 1
                    for comb in combs:
                        newPkgcomb = Pkgcomb(
                            user_name=user,
                            project_cod=project,
                            package_id=pkgid,
                            comb_user=user,
                            comb_project=project,
                            comb_code=int(comb),
                            comb_order=combid,
                        )
                        request.dbsession.add(newPkgcomb)
                        combid = combid + 1
                    pkgid = pkgid + 1

                request.dbsession.query(Project).filter(
                    Project.user_name == user
                ).filter(Project.project_cod == project).update(
                    {"project_numobs": int(numObsExtra) + int(numObsNow)}
                )

            return True, ""

        except CalledProcessError as e:
            msg = "Error running R randomization file \n"
            msg = msg + "Commang: " + " ".join(args) + "\n"
            msg = msg + "Error: \n"
            msg = msg + str(e)
            return False, msg


def createPackages(user, project, request):
    prjData = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    # Only create the packages if its needed
    if prjData.project_createpkgs == 1:
        combData = (
            request.dbsession.query(Prjcombination)
            .filter(Prjcombination.user_name == user)
            .filter(Prjcombination.project_cod == project)
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
            # print "*******************************9"
            # print pcomb
            # print "--------------------------------"
            # print pobs
            # print "*******************************9"

            final = []
            for i in range(1, prjData.project_numobs * prjData.project_numcom + 1):
                final.append({"obs": pobs[i - 1], "cmb": pcomb[i % len(combinations)]})

            # print "*******************************10"
            # print final
            # print "*******************************10"

            # cbs = []
            # for f in final:
            #     found = False
            #     for n in cbs:
            #         if n == f["cmb"]:
            #             found = True
            #     if not found:
            #         cbs.append(f["cmb"])

            allComb = []
            for f in final:
                allComb.append(f["cmb"])

            # print "*******************************11"
            # print len(cbs)
            # print "*******************************11"

            groups = grouper(prjData.project_numcom, allComb, -1)
            groups = list(groups)

            # Convert nparray into list
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
            request.dbsession.query(Package).filter(Package.user_name == user).filter(
                Package.project_cod == project
            ).delete()
            pkgid = 1

            print("*******************************20")
            pprint.pprint(groups)
            print("*******************************20")

            for grp in groups:
                newPackage = Package(
                    user_name=user,
                    project_cod=project,
                    package_id=pkgid,
                    package_code="Package #" + str(pkgid),
                )
                request.dbsession.add(newPackage)
                combid = 1
                for comb in grp:
                    newPkgcomb = Pkgcomb(
                        user_name=user,
                        project_cod=project,
                        package_id=pkgid,
                        comb_user=user,
                        comb_project=project,
                        comb_code=int(comb),
                        comb_order=combid,
                    )
                    request.dbsession.add(newPkgcomb)
                    combid += 1
                pkgid += 1

            request.dbsession.query(Project).filter(Project.user_name == user).filter(
                Project.project_cod == project
            ).update({"project_createpkgs": 0})

            setRegistryStatus(user, project, 0, request)

            # print "*******************************12"
            # print bda.heip_e(allComb)
            # print "*******************************12"

            # print "*******************************13"
            # print groups
            # print "*******************************13"
            #
            # f = open('/home/cquiros/comb.txt', "w+")
            # print "pedo"
            # for grp in groups:
            #     line = ""
            #     for item in grp:
            #         line = line + str(item) + "\t"
            #     line = line[:-1]
            #     f.write(line + "\r\n")
            # f.close()

            # combFile = runRcreatePackages(user,project,prjData.project_numobs,prjData.project_numcom,combinations,request)
            # if combFile != "":
            #     print "******************9"
            #     print combFile
            #     print "******************9"
            #     request.dbsession.query(Project).filter(Project.user_name == user).filter(
            #         Project.project_cod == project).update({'project_createpkgs': 0})
