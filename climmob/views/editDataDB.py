import json
import xml.etree.ElementTree as ET

from climmob.models.repository import sql_execute
from climmob.processes import getProjectData, getQuestionOptionsByQuestionCode


def get_FieldsByType(types, file):
    return [item[0] for item in getNamesEditByColums(file) if item[2] in types]


def make_selOneOpt(
    self, userOwner, projectId, projectCod, form, rtable, lkp_field
):  # make value for select one and multiple in jqgrid
    vals = {}
    if rtable != "None":
        result = sql_execute(
            "select %s as qc, %s as qd from %s.%s;"
            % (
                lkp_field,
                lkp_field.replace("_cod", "_des"),
                userOwner + "_" + projectCod,
                rtable,
            )
        )

        for res in result:
            vals[str(res["qc"])] = res["qd"]
    else:
        options = getQuestionOptionsByQuestionCode(
            lkp_field, projectId, form, self.request
        )
        for option in options:
            vals[str(option["value_code"])] = option["value_desc"]

    return vals


def getRTable(field, name, table):
    loTiene = False
    tieneElSegundo = False
    for i, x in enumerate(table.findall("tables/table/table")):
        # print x.attrib
        for c, v in enumerate(x):

            if "name" in v.attrib:
                # print v.attrib
                if v.attrib["name"] == field:
                    return v.attrib["rtable"], v.attrib["rfield"]


def getNamesEditByColums(file):  # create available list of columns for editing online

    tree = ET.parse(file)
    columns = []  # var name, desc, type (rfield in selects)

    for i, x in enumerate(tree.find("tables/table")):
        row = []
        if "odktype" in x.attrib:
            if x.attrib["odktype"] not in [
                "barcode",
                "deviceid",
                "start",
                "end",
                "calculate",
            ]:
                if x.attrib["name"] not in [
                    "rowuuid",
                    "surveyid",
                    "originid",
                    "",
                    "_xform_id_string",
                    "_geopoint",
                    "_longitude",
                    "_latitude",
                    "_elevation",
                    "_precision",
                    "instancename",
                ]:  # campos del formulario que no tienen que aparecer
                    # print x.attrib["name"]
                    row.append(x.attrib["name"])
                    row.append(x.attrib["desc"])
                    if "isMultiSelect" in x.attrib:
                        row.append("select")
                        rtable, rfield = getRTable(
                            x.attrib["name"], x.attrib["multiSelectTable"], tree
                        )
                        row.append(rtable)
                        row.append(rfield)
                    elif "select one" in x.attrib["odktype"]:  # .split(" ")[0]:
                        row.append("select1")
                        if "rtable" in x.attrib.keys():
                            row.append(x.attrib["rtable"])
                            row.append(x.attrib["rfield"])
                        else:
                            row.append("None")
                            row.append(x.attrib["name"])
                    elif "select_one" in x.attrib["odktype"].split(" ")[0]:
                        row.append("select1")
                        if "rtable" in x.attrib.keys():
                            row.append(x.attrib["rtable"])
                            row.append(x.attrib["rfield"])
                        else:
                            row.append("None")
                            row.append(x.attrib["name"])
                    elif x.attrib["odktype"] in ["integer", "decimal"]:
                        row.append("decimal")
                        row.append("")
                        row.append("")
                    elif x.attrib["type"] in ["datetime"]:
                        row.append("date")
                        row.append("")
                        row.append("")
                    else:
                        row.append("string")
                        row.append("")
                        row.append("")
                    columns.append(row[:])
    return columns
    # except:
    #    return []


def fillDataTable(
    self, userOwner, projectId, projectCod, form, columns, file, code, where=""
):
    ret = {
        "colNames": [],
        "data": [],
        "colModel": [],
        "projectMeta": [
            {"project_code": projectCod, "form": form, "code": code, "user": userOwner}
        ],
    }
    sql = "select "

    columns.insert(0, "rowuuid$%*ID$%*string")
    if form == "reg":
        columns.insert(1, "qst162$%*" + self._("Package code") + "$%*string")

    # hidden field
    ret["colNames"].append("flag_update")

    ret["colModel"].append(
        {
            "name": "flag_update",
            "hidden": True,
            "editable": True,
            "editrules": {"edithidden": False},
        }
    )

    for col in columns:
        # print col
        col = col.split("$%*")
        ret["colNames"].append(col[1])
        if col[0] == "qst162":
            proData = getProjectData(projectId, self.request)
            packages = {}
            for y in range(1, proData["project_numobs"] + 1):
                packages[y] = self._("Package") + " #" + str(y)

            ret["colModel"].append(
                {
                    "align": "center",
                    "frozen": True,
                    "label": col[1],
                    "name": col[0],
                    "index": col[0],
                    "editable": True,
                    "width": 75,
                    "sortable": True,
                    "align": "center",
                    "formatter": "select",
                    "edittype": "select",
                    "editoptions": {
                        "multiple": False,
                        "value": packages,
                    },
                }
            )
        else:
            if "select1" in col[2]:  # list select type
                ret["colModel"].append(
                    {
                        "align": "center",
                        "label": col[1],
                        "name": col[0],
                        "index": col[0],
                        "editable": True,
                        "formatter": "select",
                        "edittype": "select",
                        "validation": col[5],
                        "editoptions": {
                            "multiple": False,
                            "value": make_selOneOpt(
                                self,
                                userOwner,
                                projectId,
                                projectCod,
                                form,
                                col[3],
                                col[4],
                            ),
                        },
                    }
                )

            else:
                if "select" in col[2]:  # list select multiple
                    ret["colModel"].append(
                        {
                            "align": "center",
                            "label": col[1],
                            "name": col[0],
                            "index": col[0],
                            "editable": True,
                            "formatter": "select",
                            "edittype": "select",
                            "editoptions": {
                                "multiple": True,
                                "value": make_selOneOpt(
                                    self,
                                    userOwner,
                                    projectId,
                                    projectCod,
                                    form,
                                    col[3],
                                    col[4],
                                ),
                            },
                        }
                    )
                else:
                    if "decimal" in col[2] or "int" == col[2]:  # integer values
                        ret["colModel"].append(
                            {
                                "align": "center",
                                "label": col[1],
                                "name": col[0],
                                "index": col[0],
                                "editable": True,
                                "edittype": "text",
                                "formatter": "integer",
                                "editrules": {"number": True, "required": False},
                            }
                        )
                    else:
                        if "date" in col[2]:
                            ret["colModel"].append(
                                {
                                    "align": "center",
                                    "label": col[1],
                                    "name": col[0],
                                    "index": col[0],
                                    "editable": True,
                                    "edittype": "text",
                                    "formatter": "date",
                                    "editrules": {"date": True, "required": True},
                                }
                            )
                        else:
                            if "rowuuid" in col[0]:
                                ret["colModel"].append(
                                    {
                                        "align": "center",
                                        "label": col[1],
                                        "name": col[0],
                                        "index": col[0],
                                        "editable": "False",
                                        "edittype": "text",
                                    }
                                )
                            else:
                                ret["colModel"].append(
                                    {
                                        "align": "center",
                                        "label": col[1],
                                        "name": col[0],
                                        "index": col[0],
                                        "editable": True,
                                        "edittype": "text",
                                    }
                                )

        # formatter formatter:'date'
        # print "**********************77"
        # print sql
        # print "**********************77"
        sql = sql + col[0] + ","

    orderBy = "qst163"
    if form == "reg":
        orderBy = "qst162"

    sql = (
        sql[:-1]
        + " from "
        + userOwner
        + "_"
        + projectCod
        + "."
        + form.upper()
        + code
        + "_geninfo "
        + where
        + " order by "
        + orderBy
        + "+0;"
    )

    # print sql
    # print "***************************************************************************"
    result = sql_execute(sql)
    cont = 1
    for res in result:
        rowx = {}
        rowx["flag_update"] = False
        for r in zip(result._metadata.keys, res):
            if str(r[0]) in get_FieldsByType(["select12", "select"], file):
                rowx[str(r[0])] = list(map(str, str(r[1]).split(" ")))
            else:
                rowx[str(r[0])] = str(r[1])

        rowx["id"] = cont
        ret["data"].append(rowx)
        cont = cont + 1

    return json.dumps(ret)


def update_edited_data(userOwner, projectCod, form, data, file, code):

    data = json.loads(data[0])

    for row in data:
        del row["id"]
        if row["flag_update"]:
            query_update = "update %s.%s_geninfo set " % (
                userOwner + "_" + projectCod,
                form.upper() + code,
            )
            del row["flag_update"]
            for key in row:
                val = ""
                addField = True
                if key in get_FieldsByType(["int", "decimal"], file):
                    if row[key] and row[key] != "None":
                        val = str(row[key])
                    else:
                        val = "0"
                else:
                    if key in get_FieldsByType(["select1"], file):
                        if row[key] and row[key] != "None":
                            val = (
                                "'"
                                + str(row[key]).replace("[", "").replace("]", "")
                                + "'"
                            )
                        else:
                            addField = False
                    else:
                        if key in get_FieldsByType(["select"], file):
                            val = "'" + " ".join(row[key]) + "'"
                        else:
                            val = "'" + str(row[key]) + "'"

                if addField:
                    query_update += key + "=" + val + ", "

            query_update = (
                query_update[:-2] + " where rowuuid ='" + str(row["rowuuid"]) + "';"
            )

            # print query_update
            try:
                sql_execute(query_update)
            except Exception as e:
                return 0, str(e)
    return 1, ""
