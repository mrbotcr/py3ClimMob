import json
import pprint
import transaction
import xml.etree.ElementTree as ET
from zope.sqlalchemy import mark_changed


def get_FieldsByType(types, db, self, file, code):
    return [
        item[0] for item in getNamesEditByColums(db, file, code) if item[2] in types
    ]


def make_selOneOpt(
    self, bd, form, rtable, lkp_field
):  # make value for select one and multiple in jqgrid
    mySession = self.request.dbsession
    vals = {}
    result = mySession.execute(
        "select %s as qc, %s as qd from %s.%s;"
        % (
            lkp_field,
            lkp_field.replace("_cod", "_des"),
            self.user.login + "_" + bd,
            rtable,
        )
    )

    for res in result:
        vals[str(res["qc"])] = res["qd"]
    return vals


def getRTable(field, name, table):
    # print field
    loTiene = False
    tieneElSegundo = False
    for i, x in enumerate(table.findall("tables/table/table")):
        # print x.attrib
        for c, v in enumerate(x):

            if "name" in v.attrib:
                # print v.attrib
                if v.attrib["name"] == field:
                    return v.attrib["rtable"], v.attrib["rfield"]


def getNamesEditByColums(
    db, file, code
):  # create available list of columns for editing online
    # request.registry.settings['odktools.path']
    # try:

    tree = ET.parse(file)
    columns = []  # var name, desc, type (rfield in selects)

    for i, x in enumerate(tree.find("tables/table")):
        row = []
        if "odktype" in x.attrib:
            # print x.attrib["odktype"]
            if x.attrib["odktype"] not in ["barcode", "deviceid", "start", "end"]:
                if x.attrib["name"] not in [
                    "rowuuid",
                    "surveyid",
                    "originid",
                    "",
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
                    elif "select_one" in x.attrib["odktype"].split(" ")[0]:
                        row.append("select1")
                        row.append(x.attrib["rtable"])
                        row.append(x.attrib["rfield"])
                    elif x.attrib["odktype"] in ["integer"]:
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


def fillDataTable(self, db, form, columns, file, code):
    ret = {
        "colNames": [],
        "data": [],
        "colModel": [],
        "projectMeta": [
            {"project_code": db, "form": form, "code": code, "user": self.user.login}
        ],
    }
    sql = "select "

    columns.insert(0, "surveyid$%*ID$%*string")
    if form == "reg":
        columns.insert(1, "qst162$%*Package code$%*string")

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
        if col[0] == "surveyid" or col[0] == "qst162":
            ret["colModel"].append(
                {
                    "align": "center",
                    "frozen": True,
                    "label": col[1],
                    "name": col[0],
                    "index": col[0],
                    "editable": False,
                    "width": 75,
                    "sortable": True,
                    "align": "center",
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
                            "value": make_selOneOpt(self, db, form, col[3], col[4]),
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
                                "value": make_selOneOpt(self, db, form, col[3], col[4]),
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

    sql = sql[:-1] + " from %s.%s_geninfo order by surveyid;" % (
        self.user.login + "_" + db,
        form.upper() + code,
    )

    # print sql
    # print "***************************************************************************"
    mySession = self.request.dbsession
    result = mySession.execute(sql)
    for res in result:
        rowx = {}
        rowx["flag_update"] = False
        for r in zip(result._metadata.keys, res):
            if str(r[0]) in get_FieldsByType(
                ["select12", "select"], db, self, file, code
            ):
                rowx[str(r[0])] = list(map(str, str(r[1]).split(" ")))
            else:
                rowx[str(r[0])] = str(r[1])
        ret["data"].append(rowx)

    return json.dumps(ret)


def update_edited_data(self, db, form, data, file, code):
    mySession = self.request.dbsession
    data = json.loads(data[0])

    for row in data:
        if row["flag_update"]:
            query_update = "update %s.%s_geninfo set " % (
                self.user.login + "_" + db,
                form.upper() + code,
            )
            del row["flag_update"]
            for key in row:
                val = ""
                if key in get_FieldsByType(["int", "decimal"], db, self, file, code):
                    val = str(row[key])
                else:
                    if key in get_FieldsByType(["select1"], db, self, file, code):
                        val = str(row[key]).replace("[", "").replace("]", "")
                    else:
                        if key in get_FieldsByType(["select"], db, self, file, code):
                            val = "'" + " ".join(row[key]) + "'"
                        else:
                            val = "'" + str(row[key]) + "'"
                query_update += key + "=" + val + ", "
            query_update = (
                query_update[:-2] + " where surveyid ='" + str(row["surveyid"]) + "';"
            )

            # print query_update
            try:
                transaction.begin()
                mySession.execute(query_update)
                mark_changed(mySession)
                transaction.commit()
            except:
                return 0
    return 1
