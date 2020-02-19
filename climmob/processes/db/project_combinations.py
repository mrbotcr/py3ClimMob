import itertools
from ...models import Prjcombination, Prjcombdet, Project
from .registry import setRegistryStatus

__all__ = [
    "createCombinations",
    "getCombinations",
    "setCombinationStatus",
    "projectHasCombinations",
    "getCombinationStatus",
    "projectCreateCombinations",
    "projectCreatePackages",
    "getTech",
]


def projectHasCombinations(user, project, request):
    data = (
        request.dbsession.query(Prjcombination)
        .filter(Prjcombination.user_name == user)
        .filter(Prjcombination.project_cod == project)
        .first()
    )
    if data is not None:
        return True
    else:
        return False


def getCombinationStatus(user, project, comb_code, request):
    result = (
        request.dbsession.query(Prjcombination)
        .filter(Prjcombination.user_name == user)
        .filter(Prjcombination.project_cod == project)
        .filter(Prjcombination.comb_code == comb_code)
        .first()
    )

    if result:
        return True, result.comb_usable
    else:
        return False, ""


def setCombinationStatus(user, project, id, status, request):
    request.dbsession.query(Prjcombination).filter(
        Prjcombination.user_name == user
    ).filter(Prjcombination.project_cod == project).filter(
        Prjcombination.comb_code == id
    ).update(
        {"comb_usable": status}
    )
    request.dbsession.query(Project).filter(Project.user_name == user).filter(
        Project.project_cod == project
    ).update({"project_createpkgs": 1})


def getTech(user, project, request):
    sql = (
        "SELECT prjcombdet.tech_id,technology.tech_name FROM "
        "prjcombdet,technology WHERE "
        "prjcombdet.tech_id = technology.tech_id AND "
        "prjcombdet.prjcomb_user = '" + user + "' AND "
        "prjcombdet.prjcomb_project = '" + project + "' AND "
        "comb_code = 1 ORDER BY alias_order"
    )
    ttechs = request.dbsession.execute(sql).fetchall()
    techs = []
    for tech in ttechs:
        techs.append({"tech_id": tech.tech_id, "tech_name": tech.tech_name})

    return techs


def getCombinations(user, project, request):
    # Get the tehcnologies used
    sql = (
        "SELECT prjcombdet.tech_id,technology.tech_name FROM "
        "prjcombdet,technology WHERE "
        "prjcombdet.tech_id = technology.tech_id AND "
        "prjcombdet.prjcomb_user = '" + user + "' AND "
        "prjcombdet.prjcomb_project = '" + project + "' AND "
        "comb_code = 1 ORDER BY alias_order"
    )
    ttechs = request.dbsession.execute(sql).fetchall()
    techs = []
    for tech in ttechs:
        techs.append({"tech_id": tech.tech_id, "tech_name": tech.tech_name})

    # Get the list of combinations
    sql = (
        "SELECT * FROM (("
        "SELECT prjcombdet.comb_code,prjcombination.comb_usable,prjcombdet.tech_id,techalias.alias_id,"
        "techalias.alias_name,prjcombdet.alias_order FROM "
        "prjcombdet,prjalias,techalias,prjcombination WHERE "
        "prjcombdet.user_name = prjalias.user_name AND "
        "prjcombdet.project_cod = prjalias.project_cod AND "
        "prjcombdet.tech_id = prjalias.tech_id AND "
        "prjcombdet.alias_id = prjalias.alias_id AND "
        "prjalias.tech_used = techalias.tech_id AND "
        "prjalias.alias_used = techalias.alias_id AND "
        "prjcombdet.prjcomb_user = prjcombination.user_name AND "
        "prjcombdet.prjcomb_project = prjcombination.project_cod AND "
        "prjcombdet.comb_code = prjcombination.comb_code AND "
        "prjcombdet.prjcomb_user = '" + user + "' AND "
        "prjcombdet.prjcomb_project = '" + project + "' AND "
        "prjalias.tech_used IS NOT NULL "
        "ORDER BY prjcombdet.comb_code,prjcombdet.alias_order) "
        "UNION ("
        "SELECT prjcombdet.comb_code,prjcombination.comb_usable,prjcombdet.tech_id,"
        "concat('C',prjalias.alias_id) as alias_id,prjalias.alias_name,alias_order FROM "
        "prjcombdet,prjalias,prjcombination WHERE "
        "prjcombdet.user_name = prjalias.user_name AND "
        "prjcombdet.project_cod = prjalias.project_cod AND "
        "prjcombdet.tech_id = prjalias.tech_id AND "
        "prjcombdet.alias_id = prjalias.alias_id AND "
        "prjcombdet.prjcomb_user = prjcombination.user_name AND "
        "prjcombdet.prjcomb_project = prjcombination.project_cod AND "
        "prjcombdet.comb_code = prjcombination.comb_code AND "
        "prjcombdet.prjcomb_user = '" + user + "' AND "
        "prjcombdet.prjcomb_project = '" + project + "' AND "
        "prjalias.tech_used IS NULL "
        "ORDER BY prjcombdet.comb_code,prjcombdet.alias_order)) "
        "as T "
        "ORDER BY T.comb_code,T.alias_order"
    )

    tcombs = request.dbsession.execute(sql).fetchall()

    combs = []
    for item in tcombs:
        dct = dict(item)
        # for key, value in dct.iteritems():
        #    if isinstance(value, str):
        #        dct[key] = value
        combs.append(dct)

    sql = (
        "select max(comb_code) as maxcomb FROM "
        "prjcombination WHERE "
        "user_name = '" + user + "' AND "
        "project_cod = '" + project + "'"
    )

    ncombs = request.dbsession.execute(sql).fetchone()

    return techs, ncombs.maxcomb, combs


def projectCreateCombinations(user, project, request):
    prjData = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    if prjData.project_createcomb == 1:
        return True
    else:
        return False


def projectCreatePackages(user, project, request):
    prjData = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    if prjData.project_createpkgs == 1:
        return True
    else:
        return False


def createCombinations(user, project, request):
    try:
        prjData = (
            request.dbsession.query(Project)
            .filter(Project.user_name == user)
            .filter(Project.project_cod == project)
            .first()
        )
        # Only create the combinations if its needed
        if prjData.project_createcomb == 1:
            sql = (
                "SELECT DISTINCT prjalias.tech_id,technology.tech_name FROM prjalias,technology "
                "WHERE prjalias.tech_id = technology.tech_id AND "
                "prjalias.user_name = '" + user + "' AND "
                "prjalias.project_cod = '" + project + "' "
                "ORDER BY prjalias.tech_id"
            )

            techs = request.dbsession.execute(sql).fetchall()
            tech_array = []
            tech_used = []
            for tech in techs:
                tech_id = tech.tech_id
                alias_array = []
                sql = (
                    "SELECT prjalias.alias_id,prjalias.alias_used,techalias.alias_name FROM prjalias,techalias "
                    "WHERE prjalias.tech_used = techalias.tech_id AND "
                    "prjalias.alias_used = techalias.alias_id AND "
                    "prjalias.user_name = '" + user + "' AND "
                    "prjalias.project_cod = '" + project + "' AND "
                    "prjalias.tech_id = " + str(tech_id) + " AND "
                    "prjalias.tech_used IS NOT NULL "
                    "UNION SELECT alias_id,CONCAT('C',alias_id) AS alias_used,alias_name FROM prjalias "
                    "WHERE user_name = '" + user + "' AND "
                    "project_cod = '" + project + "' AND "
                    "tech_id = " + str(tech_id) + " AND "
                    "tech_used IS NULL"
                )

                alises = request.dbsession.execute(sql).fetchall()
                for alias in alises:
                    alias_array.append(
                        {
                            "tech_id": str(tech_id),
                            "tech_name": tech.tech_name,
                            "alias_id": str(alias.alias_id),
                            "alias_used": str(alias.alias_used),
                            "alias_name": alias.alias_name,
                        }
                    )
                if len(alias_array) > 0:
                    tech_array.append(list(alias_array))
                    tech_used.append(
                        {"tech_id": str(tech_id), "tech_name": tech.tech_name}
                    )

            combinations = []
            if len(tech_array) > 1:
                for element in itertools.product(*tech_array):
                    combinations.append(element)

                # Delete all combinations
                request.dbsession.query(Prjcombination).filter(
                    Prjcombination.user_name == user
                ).filter(Prjcombination.project_cod == project).delete()
                combNumber = 1
                for combination in combinations:
                    newCombination = Prjcombination(
                        user_name=user,
                        project_cod=project,
                        comb_code=combNumber,
                        comb_usable=1,
                    )
                    request.dbsession.add(newCombination)
                    aliasNumber = 1
                    for aAlias in combination:
                        newAliasUsed = Prjcombdet(
                            prjcomb_user=user,
                            prjcomb_project=project,
                            comb_code=combNumber,
                            user_name=user,
                            project_cod=project,
                            tech_id=aAlias["tech_id"],
                            alias_id=aAlias["alias_id"],
                            alias_order=aliasNumber,
                        )
                        request.dbsession.add(newAliasUsed)
                        aliasNumber += 1
                    combNumber += 1

                request.dbsession.query(Project).filter(
                    Project.user_name == user
                ).filter(Project.project_cod == project).update(
                    {"project_createcomb": 0}
                )

                request.dbsession.query(Project).filter(
                    Project.user_name == user
                ).filter(Project.project_cod == project).update(
                    {"project_createpkgs": 1}
                )

                setRegistryStatus(user, project, 0, request)

                return True, ""
            else:
                # print "*******************11"
                tech_array = tech_array[0]
                # print tech_array
                # print "*******************11"
                request.dbsession.query(Prjcombination).filter(
                    Prjcombination.user_name == user
                ).filter(Prjcombination.project_cod == project).delete()
                aliasNumber = 1
                for aAlias in tech_array:
                    newCombination = Prjcombination(
                        user_name=user,
                        project_cod=project,
                        comb_code=aliasNumber,
                        comb_usable=1,
                    )
                    request.dbsession.add(newCombination)
                    newAliasUsed = Prjcombdet(
                        prjcomb_user=user,
                        prjcomb_project=project,
                        comb_code=aliasNumber,
                        user_name=user,
                        project_cod=project,
                        tech_id=aAlias["tech_id"],
                        alias_id=aAlias["alias_id"],
                        alias_order=aliasNumber,
                    )
                    request.dbsession.add(newAliasUsed)
                    aliasNumber += 1
                request.dbsession.query(Project).filter(
                    Project.user_name == user
                ).filter(Project.project_cod == project).update(
                    {"project_createcomb": 0}
                )

                request.dbsession.query(Project).filter(
                    Project.user_name == user
                ).filter(Project.project_cod == project).update(
                    {"project_createpkgs": 1}
                )

                setRegistryStatus(user, project, 0, request)

                return True, ""
        else:
            return True, ""
    except Exception as e:
        return False, str(e)
