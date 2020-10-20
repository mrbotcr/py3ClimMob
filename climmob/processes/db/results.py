import os
from lxml import etree
from ...models import Assessment, Question, Project, mapFromSchema
import datetime, decimal
import json

__all__ = ["getJSONResult"]


def getMiltiSelectLookUpTable(XMLFile, multiSelectTable):
    tree = etree.parse(XMLFile)
    root = tree.getroot()
    etable = root.findall(".//table[@name='" + multiSelectTable + "']")
    if etable:
        for child in etable[0].iterchildren():
            if child.tag == "field":
                if child.get("rlookup") == "true":
                    return child.get("rtable"), child.get("rfield")
    return None, None


def getFields(XMLFile, table):
    fields = []
    tree = etree.parse(XMLFile)
    root = tree.getroot()
    etables = root.find(".//tables")
    if etables is not None:
        etable = etables.find(".//table[@name='" + table + "']")
        if etable is not None:
            for child in etable.iterchildren():
                if child.tag == "field":
                    field = {}
                    field["name"] = child.get("name")
                    field["odktype"] = child.get("odktype")
                    field["desc"] = child.get("desc")
                    field["key"] = child.get("key")
                    field["isMultiSelect"] = child.get("isMultiSelect")
                    field["multiSelectTable"] = child.get("multiSelectTable")
                    field["rlookup"] = child.get("rlookup")
                    if (
                        field["isMultiSelect"] == "false"
                        or field["isMultiSelect"] is None
                    ):
                        field["rtable"] = child.get("rtable")
                        field["rfield"] = child.get("rfield")
                    else:
                        field["rtable"], field["rfield"] = getMiltiSelectLookUpTable(
                            XMLFile, field["multiSelectTable"]
                        )
                    fields.append(field)
    return fields


def getLookups(XMLFile, user, project, request):
    lktables = []
    tree = etree.parse(XMLFile)
    root = tree.getroot()
    elkptables = root.find(".//lkptables")
    if elkptables is not None:
        etables = elkptables.findall(".//table")
        for table in etables:
            atable = {}
            atable["name"] = table.get("name")
            atable["desc"] = table.get("desc")
            atable["fields"] = []
            for child in table.iterchildren():
                if child.tag == "field" and child.get("name") != "rowuuid":
                    afield = {}
                    afield["name"] = child.get("name")
                    afield["desc"] = child.get("desc")
                    afield["key"] = child.get("key")
                    atable["fields"].append(afield)
            if atable["fields"]:
                atable["values"] = []
                fieldArray = []
                for field in atable["fields"]:
                    fieldArray.append(field["name"])
                sql = (
                    "SELECT "
                    + ",".join(fieldArray)
                    + " FROM "
                    + user
                    + "_"
                    + project
                    + "."
                    + atable["name"]
                )
                lkpvalues = request.repsession.execute(sql).fetchall()
                for value in lkpvalues:
                    avalue = {}
                    for field in atable["fields"]:
                        avalue[field["name"]] = value[field["name"]]
                    atable["values"].append(avalue)
            lktables.append(atable)
    return lktables


def getPackageData(user, project, request):
    data = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    qstPackage = data.question_code
    data = (
        request.dbsession.query(Question).filter(Question.question_fname == 1).first()
    )
    qstFarmer = data.question_code

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
        "SELECT * FROM (("
        "SELECT user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,"
        "project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate,"
        "project.project_numcom, pkgcomb.package_id,package.package_code, technology.tech_name,techalias.alias_name,"
        "pkgcomb.comb_order,"
        + user
        + "_"
        + project
        + ".REG_geninfo."
        + qstFarmer
        + " "
        + "FROM pkgcomb,package,prjcombination,prjcombdet,prjalias,techalias, technology,user,project,"
        + user
        + "_"
        + project
        + ".REG_geninfo "
        "WHERE pkgcomb.user_name = user.user_name "
        "AND pkgcomb.project_cod = project.project_cod "
        "AND pkgcomb.user_name = package.user_name "
        "AND pkgcomb.project_cod = package.project_cod "
        "AND pkgcomb.package_id = package.package_id "
        "AND pkgcomb.comb_user = prjcombination.user_name "
        "AND pkgcomb.comb_project = prjcombination.project_cod "
        "AND pkgcomb.comb_code = prjcombination.comb_code "
        "AND prjcombination.user_name = prjcombdet.prjcomb_user "
        "AND prjcombination.project_cod = prjcombdet.prjcomb_project "
        "AND prjcombination.comb_code = prjcombdet.comb_code "
        "AND prjcombdet.user_name = prjalias.user_name "
        "AND prjcombdet.project_cod = prjalias.project_cod "
        "AND prjcombdet.tech_id = prjalias.tech_id "
        "AND prjcombdet.alias_id = prjalias.alias_id "
        "AND prjalias.tech_used = techalias.tech_id "
        "AND prjalias.alias_used = techalias.alias_id "
        "AND techalias.tech_id = technology.tech_id "
        "AND prjalias.tech_used IS NOT NULL "
        "AND pkgcomb.user_name = '" + user + "' "
        "AND pkgcomb.project_cod = '" + project + "' "
        "AND pkgcomb.package_id = "
        + user
        + "_"
        + project
        + ".REG_geninfo."
        + qstPackage
        + " "
        "ORDER BY pkgcomb.package_id,pkgcomb.comb_order) "
        "UNION ( "
        "SELECT user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,"
        "project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate, "
        "project.project_numcom, pkgcomb.package_id,package.package_code, technology.tech_name,prjalias.alias_name,"
        "pkgcomb.comb_order," + user + "_" + project + ".REG_geninfo." + qstFarmer + " "
        "FROM pkgcomb,package,prjcombination,prjcombdet,prjalias, technology,user,project,"
        + user
        + "_"
        + project
        + ".REG_geninfo "
        "WHERE pkgcomb.user_name = user.user_name "
        "AND pkgcomb.project_cod = project.project_cod "
        "AND pkgcomb.user_name = package.user_name "
        "AND pkgcomb.project_cod = package.project_cod "
        "AND pkgcomb.package_id = package.package_id "
        "AND pkgcomb.comb_user = prjcombination.user_name "
        "AND pkgcomb.comb_project = prjcombination.project_cod "
        "AND pkgcomb.comb_code = prjcombination.comb_code "
        "AND prjcombination.user_name = prjcombdet.prjcomb_user "
        "AND prjcombination.project_cod = prjcombdet.prjcomb_project "
        "AND prjcombination.comb_code = prjcombdet.comb_code "
        "AND prjcombdet.user_name = prjalias.user_name "
        "AND prjcombdet.project_cod = prjalias.project_cod "
        "AND prjcombdet.tech_id = prjalias.tech_id "
        "AND prjcombdet.alias_id = prjalias.alias_id "
        "AND prjcombdet.tech_id = technology.tech_id "
        "AND prjalias.tech_used IS NULL "
        "AND pkgcomb.user_name = '" + user + "' "
        "AND pkgcomb.project_cod = '" + project + "' "
        "AND pkgcomb.package_id = "
        + user
        + "_"
        + project
        + ".REG_geninfo."
        + qstPackage
        + " "
        "ORDER BY pkgcomb.package_id,pkgcomb.comb_order)) AS T ORDER BY T.package_id,T.comb_order,T.tech_name"
    )

    pkgdetails = request.dbsession.execute(sql).fetchall()
    packages = []
    pkgcode = -999
    for pkg in pkgdetails:
        if pkgcode != pkg.package_id:
            aPackage = {}
            pkgcode = pkg.package_id
            aPackage["package_id"] = pkg.package_id
            aPackage["farmername"] = pkg["farmername"]
            aPackage["comps"] = []
            for x in range(0, ncombs):
                aPackage["comps"].append({})
            aPackage["comps"][pkg.comb_order - 1]["comb_order"] = pkg.comb_order
            aPackage["comps"][pkg.comb_order - 1]["technologies"] = []
            aPackage["comps"][pkg.comb_order - 1]["technologies"].append(
                {"tech_name": pkg.tech_name, "alias_name": pkg.alias_name}
            )
            packages.append(aPackage)
        else:
            try:
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "comb_order"
                ] = pkg.comb_order
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "technologies"
                ].append({"tech_name": pkg.tech_name, "alias_name": pkg.alias_name})
            except:
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "technologies"
                ] = []
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "technologies"
                ].append({"tech_name": pkg.tech_name, "alias_name": pkg.alias_name})

    return packages


def getData(user, project, registry, assessments, request):
    data = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    registryKey = data.question_code
    data = (
        request.dbsession.query(Question).filter(Question.question_asskey == 1).first()
    )
    assessmentKey = data.question_code

    fields = []
    for field in registry["fields"]:
        fields.append(
            user
            + "_"
            + project
            + ".REG_geninfo."
            + field["name"]
            + " AS "
            + "REG_"
            + field["name"]
        )
    for assessment in assessments:
        for field in assessment["fields"]:
            fields.append(
                user
                + "_"
                + project
                + ".ASS"
                + assessment["code"]
                + "_geninfo."
                + field["name"]
                + " AS "
                + "ASS"
                + assessment["code"]
                + "_"
                + field["name"]
            )

    sql = (
        "SELECT " + ",".join(fields) + " FROM " + user + "_" + project + ".REG_geninfo "
    )
    for assessment in assessments:
        sql = (
            sql
            + " LEFT JOIN "
            + user
            + "_"
            + project
            + ".ASS"
            + assessment["code"]
            + "_geninfo ON "
        )
        sql = (
            sql
            + user
            + "_"
            + project
            + ".REG_geninfo."
            + registryKey
            + " = "
            + user
            + "_"
            + project
            + ".ASS"
            + assessment["code"]
            + "_geninfo."
            + assessmentKey
        )
    sql = sql + " ORDER BY " + user + "_" + project + ".REG_geninfo." + registryKey

    data = request.dbsession.execute(sql).fetchall()

    result = []
    for item in data:
        dct = dict(item)
        for key, value in dct.items():
            if type(value) is datetime.datetime:
                dct[key] = str(value)
            if type(value) is datetime.date:
                dct[key] = str(value)
            if type(value) is datetime.time:
                dct[key] = str(value)
            if type(value) is datetime.timedelta:
                dct[key] = str(value)
            if isinstance(value, decimal.Decimal):
                dct[key] = str(value)
        result.append(dct)
    return result


def getImportantFields(user, project, request):
    result = []

    prjData = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )

    data = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    registryKey = data.question_code
    result.append(
        {"type": "PackageID", "field": "REG_" + registryKey, "desc": "Package ID"}
    )
    data = (
        request.dbsession.query(Question).filter(Question.question_fname == 1).first()
    )
    registryKey = data.question_code
    result.append(
        {
            "type": "FarmerName",
            "field": "REG_" + registryKey,
            "desc": "Name of registered farmer",
        }
    )

    sql = (
        "SELECT '' as ass_cod,question_code,question_overall,question_overallperf "
        "FROM question,registry "
        "WHERE question.question_id = registry.question_id "
        "AND registry.user_name = '" + user + "' "
        "AND registry.project_cod = '" + project + "' "
        "AND (question_overall = 1 or question_overallperf = 1)"
    )
    data = request.dbsession.execute(sql).fetchall()
    result = getImportantFieldSameFunction(data, prjData, result, "REG")

    sql = (
        "SELECT assdetail.ass_cod,question_code,question_overall,question_overallperf "
        "FROM question,assdetail "
        "WHERE question.question_id = assdetail.question_id "
        "AND assdetail.user_name = '" + user + "' "
        "AND assdetail.project_cod = '" + project + "' "
        "AND (question_overall = 1 or question_overallperf = 1)"
    )

    data = request.dbsession.execute(sql).fetchall()

    result = getImportantFieldSameFunction(data, prjData, result, "ASS")

    return result


def getImportantFieldSameFunction(data, prjData, result, form):

    for question in data:

        if question.question_overall == 1:
            if prjData.project_numcom == 2:

                result.append(
                    {
                        "type": "OverallChar",
                        "field": form
                        + question.ass_cod
                        + "_char_"
                        + question.question_code,
                        "desc": "Over all characteristic positive",
                    }
                )
            if prjData.project_numcom == 3:
                result.append(
                    {
                        "type": "OverallCharPos",
                        "field": form
                        + question.ass_cod
                        + "_char_"
                        + question.question_code
                        + "_pos",
                        "desc": "Over all characteristic positive",
                    }
                )
                result.append(
                    {
                        "type": "OverallCharNeg",
                        "field": form
                        + question.ass_cod
                        + "_char_"
                        + question.question_code
                        + "_neg",
                        "desc": "Over all characteristic negative",
                    }
                )
            if prjData.project_numcom >= 4:
                for comp in range(0, prjData.project_numcom):
                    result.append(
                        {
                            "type": "OverallCharPosition" + str(comp + 1),
                            "field": form
                            + question.ass_cod
                            + "_char)"
                            + question.question_code
                            + "_stmt_"
                            + str(comp + 1),
                            "desc": "Over all characteristic for position "
                            + str(comp + 1),
                        }
                    )
        if question.question_overallperf == 1:
            for comp in range(0, prjData.project_numcom):
                result.append(
                    {
                        "type": "OverallPerf" + str(comp + 1),
                        "field": form
                        + question.ass_cod
                        + "_perf_"
                        + question.question_code
                        + "_"
                        + str(comp + 1),
                        "desc": "Over all performance of "
                        + chr(65 + comp)
                        + " against current",
                    }
                )
    return result


def getSpecialFields(registry, assessments):
    result = []
    for field in registry["fields"]:
        if field["name"][:5] == "char_":
            result.append(
                {
                    "type": "Characteristic",
                    "name": "REG_" + field["name"],
                    "desc": field["desc"],
                }
            )
        if field["name"][:5] == "perf_":
            result.append(
                {
                    "type": "Performance",
                    "name": "REG_" + field["name"],
                    "desc": field["desc"],
                }
            )
    for assessment in assessments:
        for field in assessment["fields"]:
            if field["name"][:5] == "char_":
                result.append(
                    {
                        "type": "Characteristic",
                        "name": "ASS" + assessment["code"] + "_" + field["name"],
                        "desc": field["desc"],
                    }
                )
            if field["name"][:5] == "perf_":
                result.append(
                    {
                        "type": "Performance",
                        "name": "ASS" + assessment["code"] + "_" + field["name"],
                        "desc": field["desc"],
                    }
                )
    return result


def getJSONResult(user, project, request, includeRegistry=True, includeAssessment=True,assessmentCode=""):
    data = {}
    res = (
        request.dbsession.query(Project)
        .filter(Project.user_name == user)
        .filter(Project.project_cod == project)
        .first()
    )
    if res is not None:
        # print(res.project_registration_and_analysis)
        if res.project_regstatus == 1 or res.project_regstatus == 2:
            mappedData = mapFromSchema(res)
            for key, value in mappedData.items():
                if type(value) is datetime.datetime:
                    mappedData[key] = str(value)
                if type(value) is datetime.date:
                    mappedData[key] = str(value)
                if type(value) is datetime.time:
                    mappedData[key] = str(value)
                if type(value) is datetime.timedelta:
                    mappedData[key] = str(value)
                if isinstance(value, decimal.Decimal):
                    mappedData[key] = str(value)
            data["project"] = mappedData

            if includeRegistry:
                registryXML = os.path.join(
                    request.registry.settings["user.repository"],
                    *[user, project, "db", "reg", "create.xml"]
                )
                if os.path.exists(registryXML):
                    data["registry"] = {
                        "lkptables": getLookups(registryXML, user, project, request),
                        "fields": getFields(registryXML, "REG_geninfo"),
                    }

            data["assessments"] = []
            haveAssessments = False

            if includeAssessment:
                assessments = (
                    request.dbsession.query(Assessment)
                    .filter(Assessment.user_name == user)
                    .filter(Assessment.project_cod == project)
                    .all()
                )

                for assessment in assessments:
                    if assessmentCode == "" or assessmentCode == assessment.ass_cod:
                        if assessment.ass_status == 1 or assessment.ass_status == 2:
                            haveAssessments = True
                            assessmentXML = os.path.join(
                                request.registry.settings["user.repository"],
                                *[user, project, "db", "ass", assessment.ass_cod, "create.xml"]
                            )
                            if os.path.exists(registryXML):
                                data["assessments"].append(
                                    {
                                        "code": assessment.ass_cod,
                                        "desc": assessment.ass_desc,
                                        "lkptables": getLookups(
                                            assessmentXML, user, project, request
                                        ),
                                        "fields": getFields(
                                            assessmentXML,
                                            "ASS" + assessment.ass_cod + "_geninfo",
                                        ),
                                    }
                                )
            # EDITED BY BRANDON#
            if res.project_registration_and_analysis == 1:
                haveAssessments = True
            # Get the package information but only for registered farmers
            data["packages"] = getPackageData(user, project, request)
            if haveAssessments:
                data["specialfields"] = getSpecialFields(
                    data["registry"], data["assessments"]
                )
                data["data"] = getData(
                    user, project, data["registry"], data["assessments"], request
                )
                data["importantfields"] = getImportantFields(user, project, request)

            else:
                data["specialfields"] = []
                data["data"] = getData(
                    user, project, data["registry"], data["assessments"], request
                )
                data["importantfields"] = []

        else:
            data["specialfields"] = []
            data["assessments"] = []
            data["packages"] = []
            data["data"] = []
            data["importantfields"] = []

    else:
        data["specialfields"] = []
        data["assessments"] = []
        data["packages"] = []
        data["data"] = []
        data["importantfields"] = []

    # with open("/home/bmadriz/temp/climmobv4_metadata.json", "w") as outfile:
    #     jsonString = json.dumps(data, indent=4, ensure_ascii=False).encode("utf8")
    #     outfile.write(jsonString)

    # metadata = []
    # metadata.append({'code':"OUT001",'desc':"Report by farmer",'mime':"application/pdf","path":"/home/cquiros/outs/report.pdf"})
    # metadata.append({'code': "OUT002", 'desc': "A bar chart", 'mime': "image/png",
    #                  "path": "/home/cquiros/outs/chart1.png"})
    #
    # with open("/home/bmadriz/temp/climmobv4_metadata.json", "w") as outfile:
    #     jsonString = json.dumps(metadata, indent=4, ensure_ascii=False).encode("utf8")
    #     outfile.write(jsonString)

    return data
