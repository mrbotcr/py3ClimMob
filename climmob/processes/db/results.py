import datetime
import decimal
import os

from lxml import etree

from climmob.models import Assessment, Question, Project, mapFromSchema
from climmob.models.repository import sql_fetch_all, sql_fetch_one
from climmob.processes.db.project_combinations import getCombinations
from climmob.processes.db.anonymization_params import get_anonymization_params_as_dict
from climmob.processes.db.question import (
    get_sensitive_questions_anonymity_by_project_id,
    get_registry_key_question,
    get_assessment_key_question,
)
from climmob.processes import getCombinations
from climmob.processes.db.project_location import get_location_by_id_with_details
from climmob.processes.db.project_unit_of_analysis import (
    get_unit_of_analysis_by_unit_of_analysis_id_details,
)
from climmob.processes.db.project_objectives import (
    get_all_objectives_by_location_and_unit_of_analysis,
)
from climmob.processes.db.metadata_form import getMetadataForProject

__all__ = [
    "getJSONResult",
    "getCombinationsData",
    "get_registry_non_null_fields_count",
    "get_assessment_non_null_fields_count",
]

from climmob.utility import get_question_by_field_name, QuestionAnonymity


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


def getLookups(XMLFile, userOwner, projectCod, anonymize, request):
    lktables = []
    tree = etree.parse(XMLFile)
    root = tree.getroot()
    elkptables = root.find(".//lkptables")
    qst_163_pseudonym = get_anonymization_params_as_dict(163, request)["pseudonym"]
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
                    + userOwner
                    + "_"
                    + projectCod
                    + "."
                    + atable["name"]
                )
                lkpvalues = sql_fetch_all(sql)
                for value in lkpvalues:
                    avalue = {}
                    for field in atable["fields"]:
                        avalue[field["name"]] = value[field["name"]]
                    if anonymize and atable["name"].endswith("lkpqst163_opts"):
                        avalue["qst163_opts_des"] = qst_163_pseudonym.replace(
                            "{}", str(avalue["qst163_opts_cod"])
                        )
                    atable["values"].append(avalue)
            lktables.append(atable)
    return lktables


def getPackageData(userOwner, projectId, projectCod, request, anonymize=False):
    data = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    qstPackage = data.question_code
    data = (
        request.dbsession.query(Question).filter(Question.question_fname == 1).first()
    )
    farmer_name_qst_id = data.question_id
    qstFarmer = data.question_code

    sql = (
        "SELECT project.project_cod,project.project_numcom,count(prjtech.tech_id) as ttech FROM "
        "project,prjtech WHERE "
        "project.project_id = prjtech.project_id AND "
        "project.project_id = '" + projectId + "' "
        "GROUP BY project.project_id"
    )

    pkgdetails = sql_fetch_one(sql)
    ncombs = pkgdetails.project_numcom

    sql = (
        "SELECT * FROM (("
        "SELECT user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,"
        "project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate,"
        "project.project_numcom, pkgcomb.package_id,package.package_code, COALESCE(t.tech_name,technology.tech_name) as tech_name,COALESCE(i.alias_name,techalias.alias_name) as alias_name,"
        "pkgcomb.comb_order,"
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo."
        + qstFarmer
        + " , technology.tech_id, techalias.alias_id "
        + "FROM pkgcomb,package,prjcombination,prjcombdet,prjalias,user,project,"
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo,technology, techalias"
        "          LEFT JOIN i18n_techalias i "
        "          ON        techalias.tech_id = i.tech_id "
        "          AND       techalias.alias_id = i.alias_id "
        "          AND       i.lang_code = '" + request.locale_name + "' "
        "          LEFT JOIN i18n_technology t "
        "          ON        techalias.tech_id = t.tech_id "
        "          AND       t.lang_code = '" + request.locale_name + "' "
        " WHERE  user.user_name= '" + userOwner + "' "
        " AND pkgcomb.project_id = project.project_id "
        " AND pkgcomb.project_id = package.project_id "
        " AND pkgcomb.package_id = package.package_id "
        " AND pkgcomb.comb_project_id = prjcombination.project_id "
        " AND pkgcomb.comb_code = prjcombination.comb_code "
        " AND prjcombination.project_id = prjcombdet.project_id "
        " AND prjcombination.comb_code = prjcombdet.comb_code "
        " AND prjcombdet.project_id_tech = prjalias.project_id "
        " AND prjcombdet.tech_id = prjalias.tech_id "
        " AND prjcombdet.alias_id = prjalias.alias_id "
        " AND prjalias.tech_used = techalias.tech_id "
        " AND prjalias.alias_used = techalias.alias_id "
        " AND techalias.tech_id = technology.tech_id "
        " AND prjalias.tech_used IS NOT NULL "
        " AND pkgcomb.project_id = '" + projectId + "' "
        " AND pkgcomb.package_id = "
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo."
        + qstPackage
        + " "
        " ORDER BY pkgcomb.package_id,pkgcomb.comb_order) "
        " UNION ( "
        " SELECT user.user_name,user.user_fullname, project.project_name,project.project_pi,project.project_piemail,"
        " project.project_numobs,project.project_lat,project.project_lon,project.project_creationdate, "
        " project.project_numcom, pkgcomb.package_id,package.package_code, technology.tech_name,prjalias.alias_name,"
        " pkgcomb.comb_order,"
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo."
        + qstFarmer
        + " , technology.tech_id, prjalias.alias_used as alias_id "
        " FROM pkgcomb,package,prjcombination,prjcombdet,prjalias, technology,user,project,"
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo "
        " WHERE user.user_name= '" + userOwner + "' "
        " AND pkgcomb.project_id = project.project_id "
        " AND pkgcomb.project_id = package.project_id "
        " AND pkgcomb.package_id = package.package_id "
        " AND pkgcomb.comb_project_id = prjcombination.project_id "
        " AND pkgcomb.comb_code = prjcombination.comb_code "
        " AND prjcombination.project_id = prjcombdet.project_id "
        " AND prjcombination.comb_code = prjcombdet.comb_code "
        " AND prjcombdet.project_id_tech = prjalias.project_id "
        " AND prjcombdet.tech_id = prjalias.tech_id "
        " AND prjcombdet.alias_id = prjalias.alias_id "
        " AND prjcombdet.tech_id = technology.tech_id "
        " AND prjalias.tech_used IS NULL "
        " AND pkgcomb.project_id = '" + projectId + "' "
        " AND pkgcomb.package_id = "
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo."
        + qstPackage
        + " "
        "ORDER BY pkgcomb.package_id,pkgcomb.comb_order)) AS T ORDER BY T.package_id,T.comb_order,T.tech_name"
    )

    pkgdetails = sql_fetch_all(sql)

    farmer_name_pseudonym = ""
    if anonymize:
        params = get_anonymization_params_as_dict(farmer_name_qst_id, request)
        farmer_name_pseudonym = params["pseudonym"]

    packages = []
    pkgcode = -999
    for pkg in pkgdetails:
        if pkgcode != pkg.package_id:
            aPackage = {}
            pkgcode = pkg.package_id
            aPackage["package_id"] = pkg.package_id
            if anonymize:
                aPackage["farmername"] = farmer_name_pseudonym.replace(
                    "{}", str(pkg.package_id)
                )
            else:
                aPackage["farmername"] = pkg["farmername"]
            aPackage["comps"] = []
            for x in range(0, ncombs):
                aPackage["comps"].append({})
            aPackage["comps"][pkg.comb_order - 1]["comb_order"] = pkg.comb_order
            aPackage["comps"][pkg.comb_order - 1]["technologies"] = []
            aPackage["comps"][pkg.comb_order - 1]["technologies"].append(
                {
                    "tech_name": pkg.tech_name,
                    "tech_id": pkg.tech_id,
                    "alias_name": pkg.alias_name,
                    "alias_id": pkg.alias_id,
                }
            )
            packages.append(aPackage)
        else:
            try:
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "comb_order"
                ] = pkg.comb_order
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "technologies"
                ].append(
                    {
                        "tech_name": pkg.tech_name,
                        "tech_id": pkg.tech_id,
                        "alias_name": pkg.alias_name,
                        "alias_id": pkg.alias_id,
                    }
                )
            except:
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "technologies"
                ] = []
                packages[len(packages) - 1]["comps"][pkg.comb_order - 1][
                    "technologies"
                ].append(
                    {
                        "tech_name": pkg.tech_name,
                        "tech_id": pkg.tech_id,
                        "alias_name": pkg.alias_name,
                        "alias_id": pkg.alias_id,
                    }
                )

    return packages


class QuestionSelectFieldBuilder:
    def __init__(self, anonymize):
        self.column = None
        self.table = None
        self.form_id = None
        self.prefix = None
        self.sensitive = False
        self.anonymize = anonymize

    def set_column(self, column):
        self.column = column

    def set_table(self, table):
        self.table = table

    def set_form_id(self, form_id):
        self.form_id = form_id

    def set_prefix(self, prefix):
        self.prefix = prefix

    def set_sensitive(self, sensitive):
        self.sensitive = sensitive

    def build(self):
        if not self.anonymize or not self.sensitive:
            return f"{self.table}.{self.column} AS {self.prefix}_{self.column}"

        query = (
            f"COALESCE(MAX("
            f"CASE WHEN da.col_name = '{self.column}' "
            f"AND da.form_id='{self.form_id}'"
            f"THEN da.value END),"
            f"{self.table}.{self.column}) "
            f"AS {self.prefix}_{self.column}"
        )
        return query


def getData(
    userOwner, project_id, projectCod, registry, assessments, request, anonymize=False
):
    registryKey = get_registry_key_question(request).question_code

    assessmentKey = get_assessment_key_question(request).question_code

    questions = get_sensitive_questions_anonymity_by_project_id(project_id, request)

    fields = []

    reg_alias = "reg"

    select_field_builder = QuestionSelectFieldBuilder(anonymize)
    select_field_builder.set_table(reg_alias)
    select_field_builder.set_prefix("REG")
    select_field_builder.set_form_id("-")

    for field in registry["fields"]:
        select_field_builder.set_column(field["name"])
        if anonymize:
            question = get_question_by_field_name(field["name"], questions)
            if (
                question
                and question.question_anonymity == QuestionAnonymity.REMOVE.value
            ):
                continue
            select_field_builder.set_sensitive(question is not None)
        fields.append(select_field_builder.build())

    for assessment in assessments:
        assessment_alias = "assess_" + assessment["code"]
        select_field_builder.set_table(assessment_alias)
        select_field_builder.set_prefix(f'ASS{assessment["code"]}')
        select_field_builder.set_form_id(f"{assessment['code']}")
        for field in assessment["fields"]:
            select_field_builder.set_column(field["name"])
            if anonymize:
                question = get_question_by_field_name(field["name"], questions)
                if (
                    question
                    and question.question_anonymity == QuestionAnonymity.REMOVE.value
                ):
                    continue
                select_field_builder.set_sensitive(question is not None)
            fields.append(select_field_builder.build())

    if anonymize:
        to_remove_keys = [
            "instancename",
            "deviceimei",
            "cal_qst163",
            "clc_after",
            "_submitted_by",
            "_xform_id_string",
            "_clc_before",
        ]
        tmp_fields = fields.copy()
        fields = []
        for field in tmp_fields:
            append = True
            for key in to_remove_keys:
                if key in field:
                    append = False
                    break
            if append:
                fields.append(field)

    sql = (
        "SELECT "
        + ",".join(fields)
        + " FROM "
        + userOwner
        + "_"
        + projectCod
        + ".REG_geninfo "
        + reg_alias
    )

    for assessment in assessments:
        assessment_alias = "assess_" + assessment["code"]
        sql = (
            sql
            + " LEFT JOIN "
            + userOwner
            + "_"
            + projectCod
            + ".ASS"
            + assessment["code"]
            + "_geninfo "
            + assessment_alias
            + " ON "
        )
        sql = (
            sql
            + reg_alias
            + "."
            + registryKey
            + " = "
            + assessment_alias
            + "."
            + assessmentKey
        )
    if anonymize:
        sql = (
            sql
            + " LEFT JOIN "
            + f"{userOwner}_{projectCod}.anonymized da "
            + f"ON da.reg_id = {reg_alias}.qst162 "
            + f"GROUP BY {reg_alias}.qst162"
        )
    sql = sql + f" ORDER BY cast({reg_alias}.{registryKey} AS unsigned)"

    data = sql_fetch_all(sql)

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


def get_registry_non_null_fields_count(user_owner, project_cod, columns):
    fields = [f"({col} IS NOT NULL)" for col in columns]
    sql = f"""
        SELECT 
            SUM( {" + ".join(fields)} ) AS non_null_count
        FROM {user_owner}_{project_cod}.REG_geninfo;
    """
    data = sql_fetch_all(sql)
    return data[0][0]


def get_assessment_non_null_fields_count(
    user_owner, project_cod, assessment_code, columns
):
    fields = [f"({col} IS NOT NULL)" for col in columns]
    sql = f"""
        SELECT 
            SUM( {" + ".join(fields)} ) AS non_null_count
        FROM {user_owner}_{project_cod}.ASS{assessment_code}_geninfo;
    """
    data = sql_fetch_all(sql)
    return data[0][0]


def getImportantFields(projectId, request):
    result = []

    prjData = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
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
        " SELECT '' as ass_cod,question_code,question_overall,question_overallperf "
        " FROM question,registry "
        " WHERE question.question_id = registry.question_id "
        " AND registry.project_id = '" + projectId + "' "
        " AND (question_overall = 1 or question_overallperf = 1)"
    )

    data = sql_fetch_all(sql)
    result = getImportantFieldSameFunction(data, prjData, result, "REG")

    sql = (
        "SELECT assdetail.ass_cod,question_code,question_overall,question_overallperf "
        "FROM question,assdetail "
        "WHERE question.question_id = assdetail.question_id "
        "AND assdetail.project_id = '" + projectId + "' "
        "AND (question_overall = 1 or question_overallperf = 1)"
    )

    data = sql_fetch_all(sql)

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


def getJSONResult(
    userOwner,
    projectId,
    projectCod,
    request,
    includeRegistry=True,
    includeAssessment=True,
    assessmentCode="",
    anonymize=False,
):
    data = {}
    res = (
        request.dbsession.query(Project).filter(Project.project_id == projectId).first()
    )
    if res is not None:

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

            mappedData["project_location_name"] = get_location_by_id_with_details(
                request, mappedData["project_location"]
            ).get("plocation_name", None)
            mappedData[
                "project_unit_of_analysis_name"
            ] = get_unit_of_analysis_by_unit_of_analysis_id_details(
                request, mappedData["project_unit_of_analysis"]
            ).get(
                "puoa_name", None
            )
            mappedData["project_objectives"] = []

            for obj in get_all_objectives_by_location_and_unit_of_analysis(
                request,
                mappedData["project_location"],
                mappedData["project_unit_of_analysis"],
            ):
                mappedData["project_objectives"].append(obj["pobjective_name"])

            forms = getMetadataForProject(request, mappedData["project_id"])
            project_documentation = []
            for form in forms:
                project_documentation.append(
                    {
                        "form": form["metadata_name"],
                        "metadata": form["result"].get("pmf_json"),
                    }
                )

            mappedData["project_documentation"] = project_documentation

            data["project"] = mappedData

            if includeRegistry:
                registryXML = os.path.join(
                    request.registry.settings["user.repository"],
                    *[userOwner, projectCod, "db", "reg", "create.xml"],
                )
                if os.path.exists(registryXML):
                    data["registry"] = {
                        "lkptables": getLookups(
                            registryXML, userOwner, projectCod, anonymize, request
                        ),
                        "fields": getFields(registryXML, "REG_geninfo"),
                    }
            else:
                data["registry"] = {"lkptables": [], "fields": []}

            data["assessments"] = []
            haveAssessments = False

            if includeAssessment:
                assessments = (
                    request.dbsession.query(Assessment)
                    .filter(Assessment.project_id == projectId)
                    .order_by(Assessment.ass_days)
                    .all()
                )

                for assessment in assessments:
                    if assessmentCode == "" or assessmentCode == assessment.ass_cod:
                        if assessment.ass_status == 1 or assessment.ass_status == 2:
                            haveAssessments = True
                            assessmentXML = os.path.join(
                                request.registry.settings["user.repository"],
                                *[
                                    userOwner,
                                    projectCod,
                                    "db",
                                    "ass",
                                    assessment.ass_cod,
                                    "create.xml",
                                ],
                            )
                            if os.path.exists(assessmentXML):
                                data["assessments"].append(
                                    {
                                        "code": assessment.ass_cod,
                                        "desc": assessment.ass_desc,
                                        "intervalindays": assessment.ass_days,
                                        "lkptables": getLookups(
                                            assessmentXML,
                                            userOwner,
                                            projectCod,
                                            anonymize,
                                            request,
                                        ),
                                        "fields": getFields(
                                            assessmentXML,
                                            "ASS" + assessment.ass_cod + "_geninfo",
                                        ),
                                    }
                                )

            if res.project_registration_and_analysis == 1:
                haveAssessments = True
            # Get the package information but only for registered farmers
            data["packages"] = getPackageData(
                userOwner, projectId, projectCod, request, anonymize
            )
            data["combination"] = getCombinationsData(projectId, request)

            if haveAssessments:
                data["specialfields"] = getSpecialFields(
                    data["registry"], data["assessments"]
                )
                data["data"] = getData(
                    userOwner,
                    projectId,
                    projectCod,
                    data["registry"],
                    data["assessments"],
                    request,
                    anonymize=anonymize,
                )
                data["importantfields"] = getImportantFields(projectId, request)

            else:
                data["specialfields"] = []
                data["data"] = getData(
                    userOwner,
                    projectId,
                    projectCod,
                    data["registry"],
                    data["assessments"],
                    request,
                    anonymize=anonymize,
                )
                data["importantfields"] = []

        else:
            data["specialfields"] = []
            data["assessments"] = []
            data["packages"] = []
            data["data"] = []
            data["importantfields"] = []
            data["combinations"] = []

    else:
        data["specialfields"] = []
        data["assessments"] = []
        data["packages"] = []
        data["data"] = []
        data["importantfields"] = []
        data["combinations"] = []

    return data


def getCombinationsData(ProjectId, request):

    techs, ncombs, combs = getCombinations(ProjectId, request)

    pos = 1
    elements = []
    combArray = []
    pos2 = 0
    for comb in combs:
        if pos <= len(techs):
            elements.append(
                {
                    "technology_name": techs[pos - 1]["tech_name"],
                    "alias_name": comb["alias_name"],
                }
            )
            pos += 1
        else:
            combArray.append(
                {
                    "combination_code": comb["comb_code"] - 1,
                    "comb_usable": combs[pos2 - 1]["comb_usable"],
                    "quantity_available": combs[pos2 - 1]["quantity_available"],
                    "number_of_times_used": combs[pos2 - 1]["number_of_times_used"],
                    "elements": list(elements),
                }
            )
            elements = []
            elements.append(
                {
                    "technology_name": techs[0]["tech_name"],
                    "alias_name": comb["alias_name"],
                }
            )
            pos = 2
        pos2 += 1
    combArray.append(
        {
            "combination_code": ncombs,
            "comb_usable": combs[pos2 - 1]["comb_usable"],
            "quantity_available": combs[pos2 - 1]["quantity_available"],
            "number_of_times_used": combs[pos2 - 1]["number_of_times_used"],
            "elements": list(elements),
        }
    )

    return combArray
