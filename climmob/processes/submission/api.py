import datetime
import json
import os
import re
from decimal import Decimal

import paginate
from lxml import etree
from sqlalchemy import create_engine
from sqlalchemy import exc
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import NullPool
from webhelpers2.html import literal
from zope.sqlalchemy import mark_changed

__all__ = ["getTablesFromForm", "getFieldsFromTable", "updateData"]


def getTablesFromForm(request, userOwner, projectCod, assessmentId):
    _ = request.translate
    result = []
    pathOfTheUser = os.path.join(
        request.registry.settings["user.repository"],
        *[userOwner, projectCod, "db", "ass", assessmentId]
    )
    create_file = pathOfTheUser + "/create.xml"
    if not os.path.isfile(create_file):
        return []
    tree = etree.parse(create_file)
    root = tree.getroot()
    element_lkp_tables = root.find(".//lkptables")
    element_tables = root.find(".//tables")
    # Append all tables
    tables = element_tables.findall(".//table")
    if tables:
        for table in tables:
            fields = []
            sfields = []
            num_sensitive = 0
            for field in table.getchildren():
                if field.tag == "field":
                    desc = field.get("desc", "")
                    if desc == "":
                        desc = _("Without description")
                    fields.append({"name": field.get("name"), "desc": desc})
                    sfields.append(field.get("name") + "-" + desc)
                    sensitive = field.get("sensitive", "false")
                    if sensitive == "true":
                        num_sensitive = num_sensitive + 1
            if table.get("name").find("_msel_") >= 0:
                multi = True
            else:
                multi = False
            result.append(
                {
                    "name": table.get("name"),
                    "desc": table.get("desc"),
                    "fields": fields,
                    "lookup": False,
                    "multi": multi,
                    "sfields": ",".join(sfields),
                    "numsensitive": num_sensitive,
                }
            )
    # Append all lookup tables
    tables = element_lkp_tables.findall(".//table")
    if tables:
        for table in tables:
            fields = []
            sfields = []
            num_sensitive = 0
            for field in table.getchildren():
                if field.tag == "field":
                    desc = field.get("desc", "")
                    if desc == "":
                        desc = _("Without description")
                    fields.append({"name": field.get("name"), "desc": desc})
                    sfields.append(field.get("name") + "-" + desc)
                    sensitive = field.get("sensitive", "false")
                    if sensitive == "true":
                        num_sensitive = num_sensitive + 1
            result.append(
                {
                    "name": table.get("name"),
                    "desc": table.get("desc"),
                    "fields": fields,
                    "lookup": True,
                    "multi": False,
                    "sfields": ",".join(sfields),
                    "numsensitive": num_sensitive,
                }
            )

    return result


def getFieldsFromTable(
    request,
    userOwner,
    projectCod,
    assessmentId,
    tableName,
    currentFields,
    getValues=True,
):

    result = []
    checked = 0
    pathOfTheUser = os.path.join(
        request.registry.settings["user.repository"],
        *[userOwner, projectCod, "db", "ass", assessmentId]
    )
    create_file = pathOfTheUser + "/create.xml"
    tree = etree.parse(create_file)
    root = tree.getroot()
    table = root.find(".//table[@name='" + tableName + "']")
    if table is not None:
        for field in table.getchildren():
            if field.tag == "field":
                found = False
                if len(currentFields) != 0:
                    if "rowuuid" not in currentFields:
                        currentFields.append("rowuuid")
                for cfield in currentFields:
                    if field.get("name") == cfield:
                        found = True
                        checked = checked + 1
                desc = field.get("desc")
                if desc == "" or desc == "Without label":
                    desc = field.get("name") + " - Without description"
                if field.get("key", "false") == "true":
                    editable = "false"
                else:
                    editable = fieldIsEditable(field.get("name"))
                data = {
                    "name": field.get("name"),
                    "desc": desc,
                    "type": field.get("type"),
                    "xmlcode": field.get("xmlcode"),
                    "size": field.get("size"),
                    "decsize": field.get("decsize"),
                    "checked": found,
                    "sensitive": field.get("sensitive"),
                    "protection": field.get("protection", "None"),
                    "protection_desc": getProtectionDesc(
                        request, field.get("protection", "None")
                    ),
                    "key": field.get("key", "false"),
                    "rlookup": field.get("rlookup", "false"),
                    "rtable": field.get("rtable", "None"),
                    "rfield": field.get("rfield", "None"),
                    "editable": editable,
                }

                if data["rlookup"] == "true" and getValues:
                    data["lookupvalues"] = getLookupValues(
                        request, userOwner, projectCod, data["rtable"], data["rfield"]
                    )
                result.append(data)
            else:
                break
    return result, checked


def fieldIsEditable(field_name):
    read_only_fields = [
        "surveyid",
        "originid",
        "_submitted_by",
        "_xform_id_string",
        "_submitted_date",
        "_geopoint",
        "_longitude",
        "_latitude",
        "instanceid",
        "rowuuid",
    ]
    if field_name in read_only_fields:
        return "false"
    return "true"


def getProtectionDesc(request, protection_code):
    _ = request.translate
    if protection_code == "exclude":
        return _("Exclude it")
    if protection_code == "recode":
        return _("Recode it")
    if protection_code == "unlink":
        return _("Unlink it")
    return ""


def getLookupValues(request, userOwner, projectCod, rtable, rfield):
    schema = userOwner + "_" + projectCod
    sql = (
        "SELECT "
        + rfield
        + ","
        + rfield.replace("_cod", "_des")
        + " FROM "
        + schema
        + "."
        + rtable
    )
    records = request.dbsession.execute(sql).fetchall()
    res_dict = {"": ""}
    for record in records:
        res_dict[record[0]] = record[1]
    return literal(json.dumps(res_dict))


def getRequestDataJqgrid(
    request,
    userOwner,
    projectCod,
    tableName,
    fields,
    currentPage,
    length,
    tableOrder,
    orderDirection,
    searchField,
    searchString,
    searchOperator,
):
    _ = request.translate
    schema = userOwner + "_" + projectCod
    sql_fields = ",".join(fields)

    if searchField is None or searchString == "":
        sql = "SELECT " + sql_fields + " FROM " + schema + "." + tableName
        where_clause = ""
    else:
        sql = "SELECT " + sql_fields + " FROM " + schema + "." + tableName
        if searchOperator == "like":
            sql = (
                sql
                + " WHERE LOWER("
                + searchField
                + ") like '%"
                + searchString.lower()
                + "%'"
            )
            where_clause = (
                " WHERE LOWER("
                + searchField
                + ") like '%"
                + searchString.lower()
                + "%'"
            )
        else:
            sql = (
                sql
                + " WHERE LOWER("
                + searchField
                + ") not like '%"
                + searchString.lower()
                + "%'"
            )
            where_clause = (
                " WHERE LOWER("
                + searchField
                + ") not like '%"
                + searchString.lower()
                + "%'"
            )

    count_sql = (
        "SELECT count(*) as total FROM " + schema + "." + tableName + where_clause
    )
    records = request.dbsession.execute(count_sql).fetchone()
    total = records.total

    collection = list(range(total))
    page = paginate.Page(collection, currentPage, length)
    if page.first_item is not None:
        start = page.first_item - 1
    else:
        start = 0

    if tableOrder is not None:
        sql = sql + " ORDER BY " + tableOrder + " " + orderDirection
    sql = sql + " LIMIT " + str(start) + "," + str(length)

    mark_changed(request.dbsession)
    records = request.dbsession.execute(sql).fetchall()
    data = []

    for i in range(len(fields)):
        if fields[i].find(" as ") >= 0:
            parts = fields[i].split(" as ")
            fields[i] = parts[1]

    if records is not None:
        for record in records:
            a_record = {}
            for field in fields:
                try:
                    if (
                        isinstance(record[field], datetime.datetime)
                        or isinstance(record[field], datetime.date)
                        or isinstance(record[field], datetime.time)
                    ):
                        a_record[field] = record[field].isoformat().replace("T", " ")
                    else:
                        if isinstance(record[field], float):
                            a_record[field] = str(record[field])
                        else:
                            if isinstance(record[field], Decimal):
                                a_record[field] = str(record[field])
                            else:
                                if isinstance(record[field], datetime.timedelta):
                                    a_record[field] = str(record[field])
                                else:
                                    a_record[field] = record[field]
                except Exception as e:
                    a_record[field] = (
                        _("AJAX Data error. Report this error as an issue on ")
                        + "https://github.com/qlands/FormShare"
                    )
            data.append(a_record)

    result = {
        "records": total,
        "page": currentPage,
        "total": page.page_count,
        "rows": data,
    }
    return result


def getTableDesc(request, userOwner, projectCod, assessmentId, table_name):
    """
    Return the description of a table from  XML file
    :param request: Pyramid request object
    :param project: Project ID
    :param form: Form ID
    :param table_name: Table Name
    :return: Description of a table or ""
    """
    pathOfTheUser = os.path.join(
        request.registry.settings["user.repository"],
        *[userOwner, projectCod, "db", "ass", assessmentId]
    )
    create_file = pathOfTheUser + "/create.xml"
    tree = etree.parse(create_file)
    root = tree.getroot()
    table = root.find(".//table[@name='" + table_name + "']")
    if table is not None:
        return table.get("desc")
    return ""


def updateData(
    request, userOwner, projectCod, assessmentId, tableName, row_uuid, field, value
):
    _ = request.translate
    sql_url = request.registry.settings.get("sqlalchemy.url")
    schema = userOwner + "_" + projectCod
    sql = "UPDATE " + schema + "." + tableName + " SET " + field + " = '" + value + "'"
    sql = sql + " WHERE rowuuid = '" + row_uuid + "'"
    sql = sql.replace("''", "null")

    engine = create_engine(sql_url, poolclass=NullPool)
    try:
        session = Session(bind=engine)
        # session.execute("SET @odktools_current_user = '" + user + "'")
        session.execute(sql)
        session.commit()
        engine.dispose()
        res = {"data": {field: value}}
        return res
    except exc.IntegrityError as e:
        engine.dispose()
        p1 = re.compile(r"`(\w+)`")
        m1 = p1.findall(str(e))
        if m1:
            if len(m1) == 6:
                lookup = getTableDesc(
                    request, userOwner, projectCod, assessmentId, m1[4]
                )
                return {
                    "fieldErrors": [
                        {
                            "name": field,
                            "status": _(
                                "Cannot update value. Check the valid values in lookup table "
                            )
                            + '"'
                            + lookup
                            + '"',
                        }
                    ]
                }
        return {
            "fieldErrors": [
                {
                    "name": field,
                    "status": _(
                        "Cannot update value. Check the valid " "values in lookup table"
                    ),
                }
            ]
        }
    except Exception as ex:
        return {"fieldErrors": [{"name": field, "status": "Unknown error"}]}
