from ...models import Regsection, Assessment, Asssection, Question, Registry, AssDetail
import xlsxwriter
import os
from pyxform import xls2xform
from pyxform.xls2json import parse_file_to_json
from subprocess import check_call, CalledProcessError, Popen, PIPE, check_output
import logging
from datetime import datetime
import json
from hashlib import md5
from lxml import etree
from ..db.project import getProjectData, getRegisteredFarmers
from jinja2 import Environment
import glob

log = logging.getLogger(__name__)

__all__ = [
    "generateRegistry",
    "generateAssessmentFiles",
]


def buildDatabase(cnfFile, createFile, insertFile, schema, dropSchema):
    error = False

    if dropSchema:
        print("****buildDatabase**Dropping schema******")
        args = []
        args.append("mysql")
        args.append("--defaults-file=" + cnfFile)
        args.append("--execute=DROP SCHEMA IF EXISTS " + schema)
        try:
            check_call(args)
        except CalledProcessError as e:
            msg = "Error dropping schema \n"
            msg = msg + "Error: \n"
            msg = msg + str(e) + "\n"
            log.error(msg)
            print(msg)
            error = True

        if not error:
            print("****buildDatabase**Creating new schema******")
            args = []
            args.append("mysql")
            args.append("--defaults-file=" + cnfFile)
            args.append(
                "--execute=CREATE SCHEMA "
                + schema
                + " DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci"
            )
            try:
                check_call(args)
            except CalledProcessError as e:
                msg = "Error dropping schema \n"
                msg = msg + "Error: \n"
                msg = msg + str(e) + "\n"
                log.error(msg)
                error = True

    if not error:
        print("****buildDatabase**Creating tables******")
        args = []
        args.append("mysql")
        args.append("--defaults-file=" + cnfFile)
        args.append(schema)

        with open(createFile) as input_file:
            proc = Popen(args, stdin=input_file, stderr=PIPE, stdout=PIPE)
            output, error = proc.communicate()
            # if output != "" or error != "":
            if proc.returncode != 0:
                # print("3")
                msg = "Error creating database \n"
                msg = msg + "File: " + createFile + "\n"
                msg = msg + "Error: \n"
                msg = msg + str(error) + "\n"
                msg = msg + "Output: \n"
                msg = msg + str(output) + "\n"
                log.error(msg)
                error = True

    if not error:
        print("****buildDatabase**Inserting into lookup tables******")
        with open(insertFile) as input_file:
            proc = Popen(args, stdin=input_file, stderr=PIPE, stdout=PIPE)
            output, error = proc.communicate()
            # if output != "" or error != "":
            if proc.returncode != 0:
                msg = "Error loading lookup tables \n"
                msg = msg + "File: " + createFile + "\n"
                msg = msg + "Error: \n"
                msg = msg + str(error) + "\n"
                msg = msg + "Output: \n"
                msg = msg + str(output) + "\n"
                log.error(msg)
                error = True

    return error


def createDatabase(xlsxFile, outputDir, schema, keyVar, preFix, dropSchema, request):
    paths = ["JXFormToMysql", "jxformtomysql"]
    jxform_to_mysql = os.path.join(request.registry.settings["odktools.path"], *paths)

    filename, file_extension = os.path.splitext(xlsxFile)
    json_file = filename + ".srv"
    warnings = []
    json_dict = parse_file_to_json(xlsxFile, warnings=warnings)
    # Save the JSON output to a File
    with open(json_file, "w") as outfile:
        json_string = json.dumps(json_dict, indent=4, ensure_ascii=False)
        outfile.write(json_string)

    args = [
        jxform_to_mysql,
        "-j " + json_file,
        "-t geninfo",
        "-v " + keyVar,
        "-p " + preFix,
        "-o m",
    ]

    paths = ["tmp"]
    tempPath = os.path.join(outputDir, *paths)
    args.append("-e " + tempPath)

    paths = ["manifest.xml"]
    args.append("-f " + os.path.join(outputDir, *paths))

    paths = ["iso639.sql"]
    args.append("-T " + os.path.join(outputDir, *paths))

    paths = ["metadata.sql"]
    args.append("-m " + os.path.join(outputDir, *paths))

    paths = ["insert.xml"]
    args.append("-I " + os.path.join(outputDir, *paths))

    paths = ["insert.sql"]
    insertFile = os.path.join(outputDir, *paths)
    args.append("-i " + insertFile)

    paths = ["create.xml"]
    args.append("-C " + os.path.join(outputDir, *paths))

    paths = ["create.sql"]
    createFile = os.path.join(outputDir, *paths)
    args.append("-c " + createFile)

    paths = ["drop.sql"]
    dropFile = os.path.join(outputDir, *paths)
    args.append("-D " + dropFile)

    paths = ["custom.js"]
    jsFile = os.path.join(outputDir, *paths)
    file = open(jsFile, "w")

    # We create here a custom function to handle the QR codes generated by Climmob
    file.write("function beforeInsert(table,data)\n")
    file.write("{\n")
    file.write('\tif (table == "REG_geninfo")\n')
    file.write("\t{\n")
    file.write('\t\tvar index = data.getIndexByColumnName("qst162");\n')
    file.write("\t\tif (index >= 0)\n")
    file.write("\t\t{\n")
    file.write("\t\t\tvar qrvalue = data.itemValue(index);\n")
    file.write('\t\t\tvar temp1 = qrvalue.split("~");\n')
    file.write("\t\t\tif (temp1.length == 2)\n")
    file.write("\t\t\t{\n")
    file.write('\t\t\t\tvar temp2 = temp1[0].split("-");\n')
    file.write("\t\t\t\tvar pkgcode = temp2[1];\n")
    file.write("\t\t\t\tdata.setItemValue(index,pkgcode);\n")
    file.write("\t\t\t}\n")
    file.write("\t\t}\n")
    file.write("\t}\n")
    file.write("}\n")

    file.close()

    print("****createDatabase**Dropping previous registry******")
    # Drop the previous schema if the file exists
    if os.path.exists(dropFile):
        dropargs = []
        dropargs.append("mysql")
        dropargs.append("--defaults-file=" + request.registry.settings["mysql.cnf"])
        dropargs.append(schema)
        # print (" ".join(dropargs))
        with open(dropFile) as input_file:
            proc = Popen(dropargs, stdin=input_file, stderr=PIPE, stdout=PIPE)
            output, error = proc.communicate()
            # if output != "" or error != "":
            if proc.returncode != 0:
                # print("Error dropping database 2***")
                msg = "Error dropping database \n"
                msg = msg + "File: " + dropFile + "\n"
                msg = msg + "Error: \n"
                msg = msg + str(error) + "\n"
                msg = msg + "Output: \n"
                msg = msg + str(output) + "\n"
                log.error(msg)

    print("****createDatabase**Calling ODKToMySQL******")
    try:
        info = check_output(args)
    except CalledProcessError as e:
        msg = "Error creating database files \n"
        msg = msg + "Error: \n"
        msg = msg + str(e)
        log.debug(msg)
        try:
            error = e.output
        except:
            error = ""

        return True, error

    return (
        buildDatabase(
            request.registry.settings["mysql.cnf"],
            createFile,
            insertFile,
            schema,
            dropSchema,
        ),
        b"",
    )


class ODKExcelFile(object):
    def __init__(self, xlsxFile, formID, formLabel, formInstance, _):
        self.xlsxFile = xlsxFile
        self.root = etree.Element("root")
        self.log = logging.getLogger(__name__)
        self.formID = formID
        self.formLabel = formLabel
        self.formInstance = formInstance
        self.surveyRow = 0
        self.choicesRow = 1
        self._ = _
        try:
            os.remove(self.xlsxFile)
        except:
            pass
        self.option_list = []
        self.book = xlsxwriter.Workbook(self.xlsxFile)
        self.sheet1 = self.book.add_worksheet("survey")
        self.sheet2 = self.book.add_worksheet("choices")

    def get_options(self, option_name, new_options):
        options_to_add = []
        for element in new_options.iterchildren():
            options_to_add.append(
                {"code": element.get("code"), "label": element.get("label")}
            )
        duplicated_list = None
        for a_list in self.option_list:
            list_same = [False] * len(options_to_add)
            if a_list["size"] == len(options_to_add) and len(options_to_add) > 0:
                idx = 0
                for an_option in a_list["options"]:
                    for a_new_option in options_to_add:
                        if (
                            an_option["code"].strip().upper()
                            == a_new_option["code"].strip().upper()
                            and an_option["label"].strip().upper()
                            == a_new_option["label"].strip().upper()
                        ):
                            list_same[idx] = True
                    idx = idx + 1
                if all(list_same):
                    duplicated_list = a_list["name"]
                    break
        if duplicated_list is not None:
            return True, duplicated_list
        else:
            self.option_list.append(
                {
                    "name": option_name,
                    "size": len(options_to_add),
                    "options": options_to_add,
                }
            )
            return False, option_name

    def addGroup(
        self, name, label, appearance="field-list", inGroup=None, inRepeat=None
    ):
        exist = self.root.findall(".//group[@name='" + name + "']")
        if not exist:
            group = etree.Element("group")
            group.set("name", name)
            group.set("label", label)
            group.set("appearance", appearance)
            if inGroup is None and inRepeat is None:
                self.root.append(group)
            else:
                if inGroup is not None:
                    toGroup = self.root.findall(".//group[@name='" + inGroup + "']")
                    if toGroup:
                        toGroup[0].append(group)
                    else:
                        self.log.error("The group does not exists")
                else:
                    repeat = self.root.findall(".//repeat[@name='" + inRepeat + "']")
                    if repeat:
                        repeat[0].append(group)
                    else:
                        self.log.error("The repeat does not exists")
        else:
            self.log.error("The group already exists")

    def addOptionToFile(self, rootElement, listName):
        for element in rootElement.iterchildren():
            self.sheet2.write(self.choicesRow, 0, listName)
            self.sheet2.write(self.choicesRow, 1, element.get("code"))
            self.sheet2.write(self.choicesRow, 2, element.get("label"))
            self.choicesRow = self.choicesRow + 1

    def addNodeToFile(self, rootElement):

        for element in rootElement.iterchildren():
            self.surveyRow = self.surveyRow + 1
            if element.tag == "group" or element.tag == "repeat":
                if element.tag == "group":
                    self.sheet1.write(self.surveyRow, 0, "begin group")
                    self.sheet1.write(self.surveyRow, 1, element.get("name"))
                    self.sheet1.write(self.surveyRow, 2, element.get("label"))
                    self.sheet1.write(self.surveyRow, 8, element.get("appearance"))
                if element.tag == "repeat":
                    self.sheet1.write(self.surveyRow, 0, "begin repeat")
                    self.sheet1.write(self.surveyRow, 1, element.get("name"))
                    self.sheet1.write(self.surveyRow, 2, element.get("label"))
                    self.sheet1.write(self.surveyRow, 8, element.get("appearance"))
                self.addNodeToFile(element)
                if element.tag == "group":
                    self.surveyRow = self.surveyRow + 1
                    self.sheet1.write(self.surveyRow, 0, "end group")
                    self.sheet1.write(self.surveyRow, 1, element.get("name"))
                if element.tag == "repeat":
                    self.surveyRow = self.surveyRow + 1
                    self.sheet1.write(self.surveyRow, 0, "end repeat")
                    self.sheet1.write(self.surveyRow, 1, element.get("name"))
            else:
                if element.tag != "root":
                    if (
                        element.get("type") != "select_one"
                        and element.get("type") != "select_multiple"
                    ):
                        self.sheet1.write(self.surveyRow, 0, element.get("type"))
                    else:
                        duplicated_list, duplicated_name = self.get_options(
                            element.get("name"), element[0]
                        )
                        if not duplicated_list:
                            self.sheet1.write(
                                self.surveyRow,
                                0,
                                element.get("type")
                                + " "
                                + element.get("name")
                                + "_opts",
                            )
                            self.addOptionToFile(
                                element[0], element.get("name") + "_opts"
                            )
                        else:
                            self.sheet1.write(
                                self.surveyRow,
                                0,
                                element.get("type") + " " + duplicated_name + "_opts",
                            )
                    self.sheet1.write(self.surveyRow, 1, element.get("name"))
                    self.sheet1.write(self.surveyRow, 2, element.get("label"))
                    self.sheet1.write(self.surveyRow, 3, element.get("hint"))
                    self.sheet1.write(self.surveyRow, 4, element.get("constraint"))
                    self.sheet1.write(self.surveyRow, 14, element.get("calculation"))
                    self.sheet1.write(self.surveyRow, 6, element.get("required"))
                    if element.get("appearance") is not None:
                        self.sheet1.write(self.surveyRow, 8, element.get("appearance"))

                    if element.get("type") == "barcode":
                        self.sheet1.write(
                            self.surveyRow,
                            5,
                            self._(
                                "The scanned Qr is incorrect, it is not for this project."
                            ),
                        )
                    if element.get("required") == "True":
                        self.sheet1.write(
                            self.surveyRow,
                            7,
                            element.get("label") + self._(" requires a value"),
                        )

    def addQuestion(
        self,
        name,
        label,
        type,
        hint="",
        required=0,
        inGroup=None,
        inRepeat=None,
        constraint="",
        calculation="",
    ):
        options = {
            1: "text",
            2: "decimal",
            3: "integer",
            4: "geopoint",
            5: "select_one",
            6: "select_multiple",
            7: "barcode",
            8: "select_one",
            9: "select_one",
            10: "select_one",
            11: "geotrace",
            12: "geoshape",
            13: "date",
            14: "time",
            15: "dateTime",
            16: "image",
            17: "audio",
            18: "video",
            19: "barcode",
            20: "start",
            21: "end",
            22: "today",
            23: "deviceid",
            24: "subscriberid",
            25: "simserial",
            26: "phonenumber",
            27: "text",
            28: "calculate",
            29: "note",
        }
        ODKType = options[type]

        exist = self.root.findall(".//question[@name='" + name + "']")
        if not exist:
            question = etree.Element("question")
            question.set("name", name)
            question.set("label", label)
            question.set("hint", hint)
            question.set("type", ODKType)
            question.set("constraint", constraint)
            question.set("calculation", calculation)

            if type == 8:
                question.set("appearance", "autocomplete")

            if required == 0:
                question.set("required", "False")
            else:
                question.set("required", "True")
            if inGroup is None and inRepeat is None:
                self.root.append(question)
            else:
                if inGroup is not None:
                    group = self.root.findall(".//group[@name='" + inGroup + "']")
                    if group:
                        group[0].append(question)
                    else:
                        self.log.error("The group does not exists")
                else:
                    repeat = self.root.findall(".//repeat[@name='" + inRepeat + "']")
                    if repeat:
                        repeat[0].append(question)
                    else:
                        self.log.error("The repeat does not exists")
        else:
            self.log.error("The question {} already exists".format(name))

    def addOption(self, question, code, label):
        exist = self.root.findall(".//question[@name='" + question + "']")
        if exist:
            equestion = exist[0]
            if (
                equestion.get("type") == "select_one"
                or equestion.get("type") == "select_multiple"
            ):
                values = equestion.find(".//values")
                if values is not None:
                    evalues = values
                    codes = evalues.find(".//value[@code='" + code + "']")
                    if not codes:
                        value = etree.Element("value")
                        value.set("code", code)
                        value.set("label", label)
                        evalues.append(value)
                else:
                    evalues = etree.Element("values")
                    equestion.append(evalues)
                    value = etree.Element("value")
                    value.set("code", code)
                    value.set("label", label)
                    evalues.append(value)
            else:
                self.log.error("This question is not a select or multiselect")
        else:
            self.log.error("The question does not exists")

    def addRepeat(self, name, label, inGroup, inRepeat):
        exist = self.root.findall(".//group[@name='" + name + "']")
        if not exist:
            repeat = etree.Element("group")
            repeat.set("name", name)
            repeat.set("label", label)
            if inGroup is None and inRepeat is None:
                self.root.append(repeat)
            else:
                if inGroup is not None:
                    toGroup = self.root.findall(".//group[@name='" + inGroup + "']")
                    if toGroup:
                        toGroup[0].append(repeat)
                    else:
                        self.log.error("The group does not exists")
                else:
                    inrepeat = self.root.findall(".//repeat[@name='" + inRepeat + "']")
                    if inrepeat:
                        inrepeat[0].append(repeat)
                    else:
                        self.log.error("The repeat does not exists")
        else:
            self.log.error("The repeat group already exists")

    def renderFile(self):

        self.sheet1.write(0, 0, "type")
        self.sheet1.write(0, 1, "name")
        self.sheet1.write(0, 2, "label")
        self.sheet1.write(0, 3, "hint")
        self.sheet1.write(0, 4, "constraint")
        self.sheet1.write(0, 5, "constraint_message")
        self.sheet1.write(0, 6, "required")
        self.sheet1.write(0, 7, "required_message")
        self.sheet1.write(0, 8, "appearance")
        self.sheet1.write(0, 9, "default")
        self.sheet1.write(0, 10, "relevant")
        self.sheet1.write(0, 11, "repeat_count")
        self.sheet1.write(0, 12, "read_only")
        self.sheet1.write(0, 13, "choice_filter")
        self.sheet1.write(0, 14, "calculation")

        self.sheet2.write(0, 0, "list_name")
        self.sheet2.write(0, 1, "name")
        self.sheet2.write(0, 2, "label")

        sheet3 = self.book.add_worksheet("settings")
        sheet3.write(0, 0, "form_id")
        sheet3.write(0, 1, "form_title")
        sheet3.write(0, 2, "instance_name")

        sheet3.write(1, 0, self.formID)
        sheet3.write(1, 1, self.formLabel)
        sheet3.write(1, 2, self.formInstance)

        self.addNodeToFile(self.root)
        self.book.close()


def generateODKFile(
    userOwner,
    projectId,
    projectCod,
    xlsxFile,
    formID,
    formLabel,
    formInstance,
    groups,
    questions,
    numComb,
    request,
    selectedPackageQuestionGroup,
    listOfLabelsForPackages,
):
    _ = request.translate

    excelFile = ODKExcelFile(xlsxFile, formID, formLabel, formInstance, _)

    excelFile.addQuestion("clm_deviceimei", _("Device IMEI"), 23, "")
    excelFile.addQuestion("clm_start", _("Start of survey"), 20, "")

    # Edited by Brandon
    for group in groups:
        excelFile.addGroup("grp_" + str(group.section_id), group.section_name)
        if group.section_id == selectedPackageQuestionGroup:
            excelFile.addGroup(
                "grp_validation", _("Validation of the selected participant")
            )

    if formID[:3] == "REG":
        excelFile.addQuestion(
            "clc_before",
            "",
            28,
            calculation="substring-before(${QST162},'-" + projectCod + "~')",
            inGroup="grp_validation",
        )
        excelFile.addQuestion(
            "clc_after",
            "",
            28,
            calculation="substring-after(${clc_before},'" + userOwner + "-')",
            inGroup="grp_validation",
        )
        excelFile.addQuestion(
            "note_validation",
            _(
                'You scanned package number <span style="color:#009551; font-weight:bold">${clc_after}</span>.<br>This package belongs to <span style="color:#009551; font-weight:bold">${farmername}</span>.'
            ),
            29,
            inGroup="grp_validation",
        )
    else:
        excelFile.addQuestion(
            "clc_after",
            "",
            28,
            calculation="substring-after(${cal_QST163},'-')",
            inGroup="grp_validation",
        )
        excelFile.addQuestion(
            "note_validation",
            _(
                'You selected package number <span style="color:#009551; font-weight:bold">${QST163}</span>.<br>This package belongs to <span style="color:#009551; font-weight:bold">${clc_after}</span>.'
            ),
            29,
            inGroup="grp_validation",
        )
    # End of edition

    for question in questions:
        repeatQuestion = 1
        if question.question_quantitative == 1:
            repeatQuestion = numComb

        for questionNumber in range(0, repeatQuestion):
            nameExtra = ""
            descExtra = ""
            if question.question_quantitative == 1:
                nameExtra = "_" + chr(65 + questionNumber).lower()
                descExtra = " - " + listOfLabelsForPackages[questionNumber]

            if (
                question.question_dtype != 8
                and question.question_dtype != 9
                and question.question_dtype != 10
            ):
                if question.question_dtype != 7:
                    excelFile.addQuestion(
                        question.question_code + nameExtra,
                        question.question_desc + descExtra,
                        question.question_dtype,
                        question.question_unit,
                        question.question_requiredvalue,
                        "grp_" + str(question.section_id),
                    )
                else:
                    # print "EL PACKAGE CODE"
                    lenuser = len(userOwner) + 1
                    excelFile.addQuestion(
                        question.question_code,
                        question.question_desc,
                        question.question_dtype,
                        question.question_unit,
                        question.question_requiredvalue,
                        "grp_" + str(question.section_id),
                        None,
                        "substr(${QST162}, 0, "
                        + str(lenuser)
                        + ") = '"
                        + userOwner
                        + "-' and contains(.,'-"
                        + projectCod
                        + "~')",
                    )
            else:
                if question.question_dtype == 8:
                    excelFile.addQuestion(
                        "note_dtype8",
                        _(
                            "In the following field try to write the name of the participant to filter the information and find him/her more easily."
                        ),
                        29,
                        inGroup="grp_" + str(question.section_id),
                    )

                    excelFile.addQuestion(
                        question.question_code,
                        question.question_desc,
                        question.question_dtype,
                        question.question_unit,
                        question.question_requiredvalue,
                        "grp_" + str(question.section_id),
                    )
                    farmers = getRegisteredFarmers(
                        userOwner, projectId, projectCod, request
                    )
                    for farmer in farmers:
                        excelFile.addOption(
                            question.question_code,
                            farmer["farmer_id"],
                            farmer["farmer_name"],
                        )
                    if question.question_code == "QST163":
                        excelFile.addQuestion(
                            "cal_" + question.question_code,
                            "",
                            28,
                            inGroup="grp_" + str(question.section_id),
                            calculation="jr:choice-name(${"
                            + question.question_code
                            + "}, '${"
                            + question.question_code
                            + "}')",
                        )

                if question.question_dtype == 9:
                    if numComb == 2:
                        excelFile.addQuestion(
                            "char_" + question.question_code,
                            question.question_twoitems,
                            5,
                            "",
                            question.question_requiredvalue,
                            "grp_" + str(question.section_id),
                        )
                        for opt in range(0, numComb):
                            excelFile.addOption(
                                "char_" + question.question_code,
                                str(opt + 1),
                                listOfLabelsForPackages[opt],
                            )

                        if question.question_tied == 1:
                            excelFile.addOption(
                                "char_" + question.question_code, str(98), "Tied",
                            )

                        if question.question_notobserved == 1:
                            excelFile.addOption(
                                "char_" + question.question_code,
                                str(99),
                                _("Not observed"),
                            )

                    if numComb == 3:
                        excelFile.addQuestion(
                            "char_" + question.question_code + "_pos",
                            question.question_posstm,
                            5,
                            "",
                            question.question_requiredvalue,
                            "grp_" + str(question.section_id),
                        )
                        # EDITED BY BRANDON
                        constraintGen = ""
                        if question.question_tied == 1:
                            constraintGen = ". = " + str(98)

                        if question.question_notobserved == 1:
                            if constraintGen == "":
                                constraintGen = ". = " + str(99)
                            else:
                                constraintGen += " or . = " + str(99)

                        if constraintGen == "":
                            constraintGen = (
                                ". != ${"
                                + "char_"
                                + question.question_code
                                + "_pos"
                                + "}"
                            )
                        else:
                            constraintGen += (
                                " or . != ${"
                                + "char_"
                                + question.question_code
                                + "_pos"
                                + "}"
                            )
                        # END EDITED
                        excelFile.addQuestion(
                            "char_" + question.question_code + "_neg",
                            question.question_negstm,
                            5,
                            "",
                            question.question_requiredvalue,
                            "grp_" + str(question.section_id),
                            constraint=constraintGen,
                        )
                        for opt in range(0, numComb):
                            excelFile.addOption(
                                "char_" + question.question_code + "_pos",
                                str(opt + 1),
                                listOfLabelsForPackages[opt],
                            )
                            excelFile.addOption(
                                "char_" + question.question_code + "_neg",
                                str(opt + 1),
                                listOfLabelsForPackages[opt],
                            )

                        # EDITED BY BRANDON
                        if question.question_tied == 1:
                            excelFile.addOption(
                                "char_" + question.question_code + "_pos",
                                str(98),
                                _("Tied"),
                            )
                            excelFile.addOption(
                                "char_" + question.question_code + "_neg",
                                str(98),
                                _("Tied"),
                            )
                        if question.question_notobserved == 1:
                            excelFile.addOption(
                                "char_" + question.question_code + "_pos",
                                str(99),
                                _("Not observed"),
                            )

                            excelFile.addOption(
                                "char_" + question.question_code + "_neg",
                                str(99),
                                _("Not observed"),
                            )
                        # END EDITED

                    if numComb >= 4:
                        constraintGen = ""
                        for opt in range(0, numComb):
                            renderedString = (
                                Environment()
                                .from_string(question.question_moreitems)
                                .render(pos=opt + 1)
                            )
                            excelFile.addQuestion(
                                "char_"
                                + question.question_code
                                + "_stmt_"
                                + str(opt + 1),
                                renderedString,
                                5,
                                "",
                                question.question_requiredvalue,
                                "grp_" + str(question.section_id),
                                constraint=constraintGen,
                            )
                            if constraintGen == "":
                                constraintGen += (
                                    ". = "
                                    + str(numComb + 1)
                                    + " or . != ${"
                                    + "char_"
                                    + question.question_code
                                    + "_stmt_"
                                    + str(opt + 1)
                                    + "}"
                                )
                            else:
                                constraintGen += (
                                    " and . != ${"
                                    + "char_"
                                    + question.question_code
                                    + "_stmt_"
                                    + str(opt + 1)
                                    + "}"
                                )
                            for opt2 in range(0, numComb):
                                excelFile.addOption(
                                    "char_"
                                    + question.question_code
                                    + "_stmt_"
                                    + str(opt + 1),
                                    str(opt2 + 1),
                                    listOfLabelsForPackages[opt2],
                                )

                            if question.question_tied == 1:
                                excelFile.addOption(
                                    "char_"
                                    + question.question_code
                                    + "_stmt_"
                                    + str(98),
                                    str(98),
                                    _("Tied"),
                                )

                            if question.question_notobserved == 1:
                                excelFile.addOption(
                                    "char_"
                                    + question.question_code
                                    + "_stmt_"
                                    + str(99),
                                    str(99),
                                    _("Not observed"),
                                )

                if question.question_dtype == 10:
                    for opt in range(0, numComb):
                        renderedString = (
                            Environment()
                            .from_string(question.question_perfstmt)
                            .render(option=listOfLabelsForPackages[opt])
                        )
                        excelFile.addQuestion(
                            "perf_" + question.question_code + "_" + str(opt + 1),
                            renderedString,
                            5,
                            "",
                            question.question_requiredvalue,
                            "grp_" + str(question.section_id),
                        )
                        excelFile.addOption(
                            "perf_" + question.question_code + "_" + str(opt + 1),
                            "1",
                            _("Better"),
                        )
                        excelFile.addOption(
                            "perf_" + question.question_code + "_" + str(opt + 1),
                            "2",
                            _("Worse"),
                        )

            if question.question_dtype == 5 or question.question_dtype == 6:
                print("****generateODKFile**Query options******")
                sql = (
                    " SELECT qstoption.value_code, coalesce(i18n_qstoption.value_desc, qstoption.value_desc) as value_desc,qstoption.value_isother,qstoption.value_order "
                    " FROM question,qstoption "
                    "LEFT JOIN i18n_qstoption "
                    " ON i18n_qstoption.question_id = qstoption.question_id "
                    " AND i18n_qstoption.value_code = qstoption.value_code "
                    " AND i18n_qstoption.lang_code = '" + request.locale_name + "' "
                    " WHERE qstoption.question_id = question.question_id "
                    " AND (question.question_dtype = 5 or question.question_dtype = 6) "
                    " AND question.question_code = '" + question.question_code + "' "
                    " AND question.question_id= " + str(question.question_id) + " "
                    "ORDER BY qstoption.value_order"
                )

                values = request.dbsession.execute(sql).fetchall()
                other = False
                for value in values:
                    if value.value_isother == 1:
                        other = True
                    excelFile.addOption(
                        question.question_code + nameExtra,
                        value.value_code,
                        value.value_desc,
                    )
                if other:
                    excelFile.addQuestion(
                        question.question_code + nameExtra + "_oth",
                        question.question_desc + descExtra + " " + _("Other"),
                        1,
                        _("Add the other value here"),
                        0,
                        "grp_" + str(question.section_id),
                    )

    excelFile.addQuestion("clm_end", _("End of survey"), 21, "")

    excelFile.renderFile()


def generateRegistry(
    userOwner,
    projectId,
    projectCod,
    request,
    sectionOfThePackageCode,
    listOfLabelsForPackages,
):
    _ = request.translate

    formID = (
        "REG_" + userOwner + "_" + projectCod + "_" + datetime.now().strftime("%Y%m%d")
    )

    path = os.path.join(
        request.registry.settings["user.repository"], *[userOwner, projectCod]
    )
    if not os.path.exists(path):
        os.makedirs(path)

    paths = ["db", "reg"]
    if not os.path.exists(os.path.join(path, *paths)):
        os.makedirs(os.path.join(path, *paths))

    paths = ["odk", "reg"]
    if os.path.exists(os.path.join(path, *paths)):
        paths = ["odk", "reg", "*.*"]
        files = glob.glob(os.path.join(path, *paths))
        for f in files:
            try:
                os.remove(f)
            except:
                pass

    paths = ["odk", "reg", "media"]
    if not os.path.exists(os.path.join(path, *paths)):
        os.makedirs(os.path.join(path, *paths))

    dataPath = os.path.join(request.registry.settings["user.repository"], userOwner)
    paths = ["data", "xml"]
    if not os.path.exists(os.path.join(dataPath, *paths)):
        os.makedirs(os.path.join(dataPath, *paths))

    paths = ["data", "json"]
    if not os.path.exists(os.path.join(dataPath, *paths)):
        os.makedirs(os.path.join(dataPath, *paths))

    paths = ["odk", "reg", formID + ".xlsx"]
    xlsxFile = os.path.join(path, *paths)
    paths = ["odk", "reg", formID + ".xml"]
    xmlFile = os.path.join(path, *paths)
    paths = ["odk", "reg", formID + ".json"]
    jsonFile = os.path.join(path, *paths)

    print("****generateRegistry**Query questions******")
    # Edit by Brandon
    sections_id = (
        request.dbsession.query(Registry.section_id)
        .distinct()
        .filter(Registry.project_id == projectId)
    )
    groups = (
        request.dbsession.query(Regsection)
        .filter(Regsection.project_id == projectId)
        .filter(Regsection.section_id.in_(sections_id))
        .order_by(Regsection.section_order)
        .all()
    )
    # Terminan los cambios

    sql = (
        "SELECT q.question_code,COALESCE(i.question_desc,q.question_desc) as question_desc,COALESCE(i.question_unit,q.question_unit) as question_unit, q.question_dtype, q.question_twoitems, "
        "r.section_id, COALESCE(i.question_posstm, q.question_posstm) as question_posstm, COALESCE(i.question_negstm ,q.question_negstm) as question_negstm, q.question_moreitems, COALESCE(i.question_perfstmt, q.question_perfstmt) as question_perfstmt, "
        "q.question_requiredvalue, r.question_order, q.question_id, q.question_tied, q.question_notobserved, q.question_quantitative "
        "FROM registry r,question q "
        " LEFT JOIN i18n_question i "
        " ON        q.question_id = i.question_id "
        " AND       i.lang_code = '" + request.locale_name + "' "
        " WHERE q.question_id = r.question_id "
        " AND r.project_id = '" + projectId + "'"
        "ORDER BY r.question_order"
    )

    questions = request.dbsession.execute(sql).fetchall()

    prjdata = getProjectData(projectId, request)
    label = _("Registration-") + prjdata["project_name"]
    formInstance = "concat('" + projectCod + "_Regis_',${farmername})"

    generateODKFile(
        userOwner,
        projectId,
        projectCod,
        xlsxFile,
        formID,
        label,
        formInstance,
        groups,
        questions,
        prjdata["project_numcom"],
        request,
        sectionOfThePackageCode,
        listOfLabelsForPackages,
    )

    print("****generateRegistry**Convert XLSX to XML******")
    try:
        xls2xform.xls2xform_convert(xlsxFile, xmlFile)
    except Exception as e:
        msg = _("Error converting XLSX to XML") + "\n"
        msg = msg + "XLSX File: " + xlsxFile + "\n"
        msg = msg + "XML File: " + xmlFile + "\n"
        msg = msg + "Error: \n"
        msg = msg + str(e)
        log.error(msg)
        return False

    print("****generateRegistry**Writing JSON file******")
    metadata = {}
    metadata["formID"] = formID
    metadata["name"] = label
    metadata["majorMinorVersion"] = ""
    metadata["version"] = datetime.now().strftime("%Y%m%d")
    metadata["hash"] = "md5:" + md5(open(xmlFile, "rb").read()).hexdigest()
    metadata["descriptionText"] = label
    with open(jsonFile, "w") as outfile:
        jsonString = json.dumps(metadata, indent=4, ensure_ascii=False)
        outfile.write(jsonString)

    print("****generateRegistry**Getting key question******")
    keyQuestion = (
        request.dbsession.query(Question).filter(Question.question_regkey == 1).first()
    )
    paths = ["db", "reg"]
    state, error = createDatabase(
        xlsxFile,
        os.path.join(path, *paths),
        userOwner + "_" + projectCod,
        keyQuestion.question_code,
        "REG",
        True,
        request,
    )

    return not state, error


def generateAssessmentFiles(
    userOwner,
    projectId,
    projectCod,
    assessment,
    request,
    sectionOfThePackageCode,
    listOfLabelsForPackages,
):
    _ = request.translate

    result = []
    keyQuestion = (
        request.dbsession.query(Question).filter(Question.question_asskey == 1).first()
    )
    assessments = (
        request.dbsession.query(Assessment)
        .filter(Assessment.project_id == projectId)
        .filter(Assessment.ass_cod == assessment)
        .all()
    )
    for assessment in assessments:
        formID = (
            "ASS_"
            + userOwner
            + "_"
            + projectCod
            + "_"
            + assessment.ass_cod
            + "_"
            + datetime.now().strftime("%Y%m%d")
        )
        path = os.path.join(
            request.registry.settings["user.repository"], *[userOwner, projectCod]
        )
        if not os.path.exists(path):
            os.makedirs(path)

        paths = ["odk", "ass", assessment.ass_cod]
        if os.path.exists(os.path.join(path, *paths)):
            paths = ["odk", "ass", assessment.ass_cod, "*.*"]
            files = glob.glob(os.path.join(path, *paths))
            for f in files:
                try:
                    os.remove(f)
                except:
                    pass

        paths = ["odk", "ass", assessment.ass_cod, "media"]
        if not os.path.exists(os.path.join(path, *paths)):
            os.makedirs(os.path.join(path, *paths))

        dataPath = os.path.join(request.registry.settings["user.repository"], userOwner)

        paths = ["data", "xml"]
        if not os.path.exists(os.path.join(dataPath, *paths)):
            os.makedirs(os.path.join(dataPath, *paths))

        paths = ["data", "json"]
        if not os.path.exists(os.path.join(dataPath, *paths)):
            os.makedirs(os.path.join(dataPath, *paths))

        paths = ["odk", "ass", assessment.ass_cod, formID + ".xlsx"]
        xlsxFile = os.path.join(path, *paths)
        paths = ["odk", "ass", assessment.ass_cod, formID + ".xml"]
        xmlFile = os.path.join(path, *paths)
        paths = ["odk", "ass", assessment.ass_cod, formID + ".json"]
        jsonFile = os.path.join(path, *paths)

        # Edited by Brandon
        sections_id = (
            request.dbsession.query(AssDetail.section_id)
            .distinct()
            .filter(AssDetail.project_id == projectId)
            .filter(AssDetail.ass_cod == assessment.ass_cod)
        )
        groups = (
            request.dbsession.query(Asssection)
            .filter(Asssection.project_id == projectId)
            .filter(Asssection.ass_cod == assessment.ass_cod)
            .filter(Asssection.section_id.in_(sections_id))
            .order_by(Asssection.section_order)
            .all()
        )
        # End

        sql = (
            " SELECT q.question_code, COALESCE(i.question_desc,q.question_desc) as question_desc,COALESCE(i.question_unit,q.question_unit) as question_unit, q.question_dtype, q.question_twoitems, "
            " a.section_id, COALESCE(i.question_posstm, q.question_posstm) as question_posstm, COALESCE(i.question_negstm ,q.question_negstm) as question_negstm, q.question_moreitems, COALESCE(i.question_perfstmt, q.question_perfstmt) as question_perfstmt, "
            " q.question_requiredvalue, q.question_id, q.question_tied, q.question_notobserved, q.question_quantitative "
            " FROM assdetail a, question q "
            " LEFT JOIN i18n_question i "
            " ON        q.question_id = i.question_id "
            " AND       i.lang_code = '" + request.locale_name + "' "
            " WHERE q.question_id = a.question_id "
            " AND a.project_id = '" + projectId + "' "
            " AND a.ass_cod = '" + assessment.ass_cod + "' "
            " order by a.question_order "
        )

        questions = request.dbsession.execute(sql).fetchall()

        prjdata = getProjectData(projectId, request)
        label = (
            _("Data collection - ")
            + assessment.ass_desc
            + " - "
            + prjdata["project_name"]
        )
        formInstance = "concat('" + projectCod + "_Assess_',${cal_QST163})"
        generateODKFile(
            userOwner,
            projectId,
            projectCod,
            xlsxFile,
            formID,
            label,
            formInstance,
            groups,
            questions,
            prjdata["project_numcom"],
            request,
            sectionOfThePackageCode,
            listOfLabelsForPackages,
        )

        try:
            xls2xform.xls2xform_convert(xlsxFile, xmlFile)
            metadata = {}
            metadata["formID"] = formID
            metadata["name"] = label
            metadata["majorMinorVersion"] = ""
            metadata["version"] = datetime.now().strftime("%Y%m%d")
            metadata["hash"] = "md5:" + md5(open(xmlFile, "rb").read()).hexdigest()
            metadata["descriptionText"] = label
            with open(jsonFile, "w") as outfile:
                jsonString = json.dumps(metadata, indent=4, ensure_ascii=False)
                outfile.write(jsonString)

            paths = ["db", "ass", assessment.ass_cod]
            if not os.path.exists(os.path.join(path, *paths)):
                os.makedirs(os.path.join(path, *paths))

            # Edited by Brandon -> The validation was incorrect if createDatabase
            state, error = createDatabase(
                xlsxFile,
                os.path.join(path, *paths),
                userOwner + "_" + projectCod,
                keyQuestion.question_code,
                "ASS" + assessment.ass_cod,
                False,
                request,
            )
            if not state:
                result.append(
                    {"code": assessment.ass_cod, "result": True, "error": error}
                )
            else:
                result.append(
                    {"code": assessment.ass_cod, "result": False, "error": error}
                )

        except Exception as e:
            msg = _("Error converting XLSX to XML") + "\n"
            msg = msg + "XLSX File: " + xlsxFile + "\n"
            msg = msg + "XML File: " + xmlFile + "\n"
            msg = msg + "Error: \n"
            msg = msg + str(e)
            log.error(msg)
            result.append({"code": assessment.ass_cod, "result": False})

    return result
