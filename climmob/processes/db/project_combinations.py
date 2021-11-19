import itertools
from ...models import Prjcombination, Prjcombdet, Project
from .registry import setRegistryStatus
import math

__all__ = [
    "createCombinations",
    "getCombinations",
    "setCombinationStatus",
    "projectHasCombinations",
    "getCombinationStatus",
    "projectCreateCombinations",
    "projectCreatePackages",
    "getTech",
    "getCombinationsUsableInProject",
    "setCombinationQuantityAvailable",
]


def getCombinationsUsableInProject(projectId, request):
    data = (
        request.dbsession.query(Prjcombination)
        .filter(Prjcombination.project_id == projectId)
        .filter(Prjcombination.comb_usable == 1)
        .all()
    )
    return data


def projectHasCombinations(projectId, request):
    data = (
        request.dbsession.query(Prjcombination)
        .filter(Prjcombination.project_id == projectId)
        .first()
    )
    if data is not None:
        return True
    else:
        return False


def getCombinationStatus(projectId, comb_code, request):
    result = (
        request.dbsession.query(Prjcombination)
        .filter(Prjcombination.project_id == projectId)
        .filter(Prjcombination.comb_code == comb_code)
        .first()
    )

    if result:
        return True, result.comb_usable
    else:
        return False, ""


def setCombinationStatus(projectId, id, status, request):
    request.dbsession.query(Prjcombination).filter(
        Prjcombination.project_id == projectId
    ).filter(Prjcombination.comb_code == id).update({"comb_usable": status})
    request.dbsession.query(Project).filter(Project.project_id == projectId).update(
        {"project_createpkgs": 1}
    )


def setCombinationQuantityAvailable(projectId, id, quantity, request):
    res = (
        request.dbsession.query(Prjcombination)
        .filter(Prjcombination.project_id == projectId)
        .filter(Prjcombination.comb_code == id)
    )
    if res.first().quantity_available != quantity:

        res.update({"quantity_available": quantity})
        request.dbsession.query(Project).filter(Project.project_id == projectId).update(
            {"project_createpkgs": 1}
        )


def getTech(projectId, request):
    sql = (
        "SELECT prjcombdet.tech_id,COALESCE(i.tech_name,technology.tech_name) as tech_name FROM "
        "prjcombdet,technology "
        " LEFT JOIN i18n_technology i "
        " ON        technology.tech_id = i.tech_id "
        " AND       i.lang_code = '" + request.locale_name + "' "
        " WHERE "
        "prjcombdet.tech_id = technology.tech_id AND "
        "prjcombdet.project_id_tech = '" + projectId + "' AND "
        "comb_code = 1 ORDER BY alias_order"
    )
    ttechs = request.dbsession.execute(sql).fetchall()
    techs = []
    for tech in ttechs:
        techs.append({"tech_id": tech.tech_id, "tech_name": tech.tech_name})

    return techs


def getCombinations(projectId, request):
    # Get the tehcnologies used
    sql = (
        "SELECT prjcombdet.tech_id,COALESCE(i.tech_name,technology.tech_name) as tech_name FROM "
        " prjcombdet,technology "
        " LEFT JOIN i18n_technology i "
        " ON        technology.tech_id = i.tech_id "
        " AND       i.lang_code = '" + request.locale_name + "' "
        " WHERE "
        " prjcombdet.tech_id = technology.tech_id AND "
        " prjcombdet.project_id_tech = '" + projectId + "' AND "
        " comb_code = 1 ORDER BY alias_order"
    )
    ttechs = request.dbsession.execute(sql).fetchall()
    techs = []
    for tech in ttechs:
        techs.append({"tech_id": tech.tech_id, "tech_name": tech.tech_name})

    # Get the list of combinations
    sql = (
        " SELECT * FROM (("
        " SELECT prjcombdet.comb_code,prjcombination.comb_usable,prjcombination.quantity_available,prjcombdet.tech_id,techalias.alias_id,"
        " COALESCE(i.alias_name,techalias.alias_name) as alias_name,prjcombdet.alias_order FROM "
        " prjcombdet,prjalias,prjcombination,techalias "
        " LEFT JOIN i18n_techalias i "
        " ON        techalias.tech_id = i.tech_id "
        " AND       techalias.alias_id = i.alias_id "
        " AND       i.lang_code = '" + request.locale_name + "'"
        " WHERE "
        " prjcombdet.project_id = prjalias.project_id AND "
        " prjcombdet.tech_id = prjalias.tech_id AND "
        " prjcombdet.alias_id = prjalias.alias_id AND "
        " prjalias.tech_used = techalias.tech_id AND "
        " prjalias.alias_used = techalias.alias_id AND "
        " prjcombdet.project_id_tech = prjcombination.project_id AND "
        " prjcombdet.comb_code = prjcombination.comb_code AND "
        " prjcombdet.project_id_tech = '" + projectId + "' AND "
        " prjalias.tech_used IS NOT NULL "
        " ORDER BY prjcombdet.comb_code,prjcombdet.alias_order) "
        " UNION ("
        " SELECT prjcombdet.comb_code,prjcombination.comb_usable,prjcombination.quantity_available,prjcombdet.tech_id,"
        " concat('C',prjalias.alias_id) as alias_id,prjalias.alias_name,alias_order FROM "
        " prjcombdet,prjalias,prjcombination WHERE "
        " prjcombdet.project_id = prjalias.project_id AND "
        " prjcombdet.tech_id = prjalias.tech_id AND "
        " prjcombdet.alias_id = prjalias.alias_id AND "
        " prjcombdet.project_id_tech = prjcombination.project_id AND "
        " prjcombdet.comb_code = prjcombination.comb_code AND "
        " prjcombdet.project_id_tech = '" + projectId + "' AND "
        " prjalias.tech_used IS NULL "
        " ORDER BY prjcombdet.comb_code,prjcombdet.alias_order)) "
        " as T "
        " ORDER BY T.comb_code,T.alias_order"
    )

    tcombs = request.dbsession.execute(sql).fetchall()

    combs = []
    for item in tcombs:
        dct = dict(item)
        combs.append(dct)

    sql = (
        "select max(comb_code) as maxcomb FROM "
        "prjcombination WHERE "
        "project_id = '" + projectId + "'"
    )

    ncombs = request.dbsession.execute(sql).fetchone()

    return techs, ncombs.maxcomb, combs


def projectCreateCombinations(projectId, request):
    prjData = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if prjData.project_createcomb == 1:
        return True
    else:
        return False


def projectCreatePackages(projectId, request):
    prjData = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if prjData.project_createpkgs != 0:
        return True
    else:
        return False


def createCombinations(userOwner, projectId, projectCod, request):
    try:
        prjData = (
            request.dbsession.query(Project)
            .filter(Project.project_id == projectId)
            .first()
        )
        # Only create the combinations if its needed
        if prjData.project_createcomb == 1:
            sql = (
                "SELECT DISTINCT prjalias.tech_id, COALESCE( i18n_technology.tech_name ,technology.tech_name) as tech_name "
                "FROM prjalias,technology "
                "LEFT JOIN i18n_technology "
                "ON        i18n_technology.tech_id = technology.tech_id "
                "AND       i18n_technology.lang_code = '" + request.locale_name + "' "
                "WHERE prjalias.tech_id = technology.tech_id AND prjalias.project_id = '"
                + projectId
                + "' ORDER BY prjalias.tech_id "
            )

            techs = request.dbsession.execute(sql).fetchall()
            tech_array = []
            tech_used = []
            for tech in techs:
                tech_id = tech.tech_id
                alias_array = []
                sql = (
                    "SELECT prjalias.alias_id,prjalias.alias_used, COALESCE(i18n_techalias.alias_name ,techalias.alias_name) as alias_name FROM prjalias,techalias "
                    "LEFT JOIN i18n_techalias "
                    "ON        i18n_techalias.tech_id = techalias.tech_id "
                    "AND       i18n_techalias.alias_id = techalias.alias_id "
                    "AND       i18n_techalias.lang_code = '" + request.locale_name + "'"
                    "WHERE prjalias.tech_used = techalias.tech_id AND "
                    "prjalias.alias_used = techalias.alias_id AND "
                    "prjalias.project_id = '" + projectId + "' AND "
                    "prjalias.tech_id = " + str(tech_id) + " AND "
                    "prjalias.tech_used IS NOT NULL "
                    "UNION SELECT alias_id,CONCAT('C',alias_id) AS alias_used,alias_name FROM prjalias "
                    "WHERE  "
                    "project_id = '" + projectId + "' AND "
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
                    Prjcombination.project_id == projectId
                ).delete()
                combNumber = 1
                for combination in combinations:
                    newCombination = Prjcombination(
                        project_id=projectId,
                        comb_code=combNumber,
                        comb_usable=1,
                        quantity_available=math.ceil(
                            (prjData.project_numobs * prjData.project_numcom)
                            / len(combinations)
                        ),
                    )
                    request.dbsession.add(newCombination)
                    aliasNumber = 1
                    for aAlias in combination:
                        newAliasUsed = Prjcombdet(
                            project_id=projectId,
                            comb_code=combNumber,
                            project_id_tech=projectId,
                            tech_id=aAlias["tech_id"],
                            alias_id=aAlias["alias_id"],
                            alias_order=aliasNumber,
                        )
                        request.dbsession.add(newAliasUsed)
                        aliasNumber += 1
                    combNumber += 1

                request.dbsession.query(Project).filter(
                    Project.project_id == projectId
                ).update({"project_createcomb": 0})

                request.dbsession.query(Project).filter(
                    Project.project_id == projectId
                ).update({"project_createpkgs": 1})

                setRegistryStatus(userOwner, projectCod, projectId, 0, request)

                return True, ""
            else:
                # print ("*******************11")
                tech_array = tech_array[0]
                # print tech_array
                # print "*******************11"
                request.dbsession.query(Prjcombination).filter(
                    Prjcombination.project_id == projectId
                ).delete()
                aliasNumber = 1
                for aAlias in tech_array:
                    newCombination = Prjcombination(
                        project_id=projectId,
                        comb_code=aliasNumber,
                        comb_usable=1,
                        quantity_available=math.ceil(
                            (prjData.project_numobs * prjData.project_numcom)
                            / len(tech_array)
                        ),
                    )
                    request.dbsession.add(newCombination)
                    newAliasUsed = Prjcombdet(
                        project_id_tech=projectId,
                        comb_code=aliasNumber,
                        project_id=projectId,
                        tech_id=aAlias["tech_id"],
                        alias_id=aAlias["alias_id"],
                        alias_order=aliasNumber,
                    )
                    request.dbsession.add(newAliasUsed)
                    aliasNumber += 1
                request.dbsession.query(Project).filter(
                    Project.project_id == projectId
                ).update({"project_createcomb": 0})

                request.dbsession.query(Project).filter(
                    Project.project_id == projectId
                ).update({"project_createpkgs": 1})

                setRegistryStatus(userOwner, projectCod, projectId, 0, request)

                return True, ""
        else:
            return True, ""
    except Exception as e:
        return False, str(e)
