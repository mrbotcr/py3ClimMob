import glob
import json
import logging
import os
from datetime import datetime
from hashlib import md5
from subprocess import check_call, CalledProcessError, Popen, PIPE, check_output

import xlsxwriter
from jinja2 import Environment
from lxml import etree
from pyxform import xls2xform
from pyxform.xls2json import parse_file_to_json
from climmob.models.schema import mapFromSchema
from sqlalchemy import func, and_

from climmob.models import (
    Regsection,
    Assessment,
    Asssection,
    Question,
    Registry,
    AssDetail,
    generalPhrases,
    I18nGeneralPhrases,
)
from climmob.processes.db.project import getProjectData, getRegisteredFarmers
from climmob.processes.db.prjlang import getPrjLangDefaultInProject, getPrjLangInProject
from climmob.processes.db.i18n_question import getFieldTranslationByLanguage
from climmob.processes.db.i18n_qstoption import (
    getFieldTranslationQuestionOptionByLanguage,
)
from climmob.processes.db.i18n_general_phrases import getPhraseTranslationInLanguage

log = logging.getLogger(__name__)

__all__ = [
    "generateRegistry",
    "generateAssessmentFiles",
]


def buildDatabase(
    cnfFile, createFile, insertFile, schema, dropSchema, settings, outputDir
):
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

    if not error:
        print("****buildDatabase**Creating triggers******")
        functionForCreateTheTriggers(schema, settings, outputDir, cnfFile)

    return error


def functionForCreateTheTriggers(schema, settings, form_repository_path, my_cnf_file):

    create_xml_file = os.path.join(form_repository_path, "create.xml")
    create_file = os.path.join(form_repository_path, "mysql_create_audit.sql")

    if os.path.exists(create_xml_file):

        parser = etree.XMLParser(remove_blank_text=True)
        tree_create = etree.parse(create_xml_file, parser)
        root_create = tree_create.getroot()
        tables = root_create.findall(".//table")
        table_array = []
        if tables:
            for a_table in tables:
                table_array.append(a_table.get("name"))

        create_audit_triggers = os.path.join(
            settings["odktools.path"],
            *["utilities", "createAuditTriggers", "createaudittriggers"]
        )

        args = [
            create_audit_triggers,
            "-H " + settings.get("odktools.mysql.host"),
            "-P " + settings.get("odktools.mysql.port", "3306"),
            "-u " + settings.get("odktools.mysql.user"),
            "-p " + settings.get("odktools.mysql.password"),
            "-s " + schema,
            "-o " + form_repository_path,
            "-t " + ",".join(table_array),
        ]
        p = Popen(args, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()

        if p.returncode == 0:
            args = ["mysql", "--defaults-file=" + my_cnf_file, schema]

            with open(create_file) as input_create_file:
                proc = Popen(args, stdin=input_create_file, stderr=PIPE, stdout=PIPE)
                output, error = proc.communicate()
                if proc.returncode != 0:
                    print(
                        "Cannot create new triggers for schema {} with file {}. Error:{}-{}".format(
                            schema,
                            create_file,
                            output.decode(),
                            error.decode(),
                        )
                    )
        else:
            print(
                "Cannot create new triggers. Error: {}-{}".format(
                    stdout.decode(), stderr.decode()
                )
            )


def createDatabase(
    xlsxFile,
    outputDir,
    schema,
    keyVar,
    preFix,
    dropSchema,
    request,
    external_files=None,
    default_language=None,
    other_languages=None,
):

    if external_files is None:
        external_files = []

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

    for a_file in external_files:
        args.append(a_file)

    if other_languages is not None:
        args.append("-l '" + other_languages + "'")
    if default_language is not None:
        args.append("-d '" + default_language + "'")

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
            request.registry.settings,
            outputDir,
        ),
        b"",
    )


class ODKExcelFile(object):
    def __init__(
        self,
        xlsxFile,
        formID,
        formLabel,
        formInstance,
        _,
        languages,
        userOwner,
        request,
    ):
        self.xlsxFile = xlsxFile
        self.root = etree.Element("root")
        self.log = logging.getLogger(__name__)
        self.formID = formID
        self.formLabel = formLabel
        self.formInstance = formInstance
        self.surveyRow = 0
        self.choicesRow = 1
        self._ = _
        self.languages = languages
        self.userOwner = userOwner
        self.request = request
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
            if not self.languages:
                options_to_add.append(
                    {"code": element.get("code"), "label": element.get("label")}
                )
            else:
                for language in self.languages:
                    options_to_add.append(
                        {
                            "code": element.get("code"),
                            "label_{}".format(language["lang_code"]): element.get(
                                "label_{}".format(language["lang_code"])
                            ),
                        }
                    )
        duplicated_list = None
        for a_list in self.option_list:
            list_same = [False] * len(options_to_add)
            if a_list["size"] == len(options_to_add) and len(options_to_add) > 0:
                idx = 0
                for an_option in a_list["options"]:
                    keysao = list(an_option.keys())
                    keysao.remove("code")
                    keyao = keysao[0]
                    for a_new_option in options_to_add:
                        keysano = list(a_new_option.keys())
                        keysano.remove("code")
                        keyano = keysano[0]
                        if (
                            an_option["code"].strip().upper()
                            == a_new_option["code"].strip().upper()
                            and an_option[keyao].strip().upper()
                            == a_new_option[keyano].strip().upper()
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
            if not self.languages:
                group.set("label", label)
            else:
                if isinstance(label, str):
                    for language in self.languages:
                        group.set("label_{}".format(language["lang_code"]), label)
                else:
                    for language in label:
                        group.set(language["label"], language["value"])

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

    def addOptionToFile(self, rootElement, listName, dictOfColumnsChoices):
        for element in rootElement.iterchildren():
            self.sheet2.write(self.choicesRow, 0, listName)
            self.sheet2.write(self.choicesRow, 1, element.get("code"))
            if self.languages:
                for language in self.languages:
                    # print(
                    #     dictOfColumnsChoices["label_{}".format(language["lang_code"])]
                    # )
                    # print(element.get("label_{}".format(language["lang_code"])))
                    self.sheet2.write(
                        self.choicesRow,
                        dictOfColumnsChoices["label_{}".format(language["lang_code"])],
                        element.get("label_{}".format(language["lang_code"])),
                    )
            else:
                self.sheet2.write(
                    self.choicesRow, dictOfColumnsChoices["label"], element.get("label")
                )
            self.choicesRow = self.choicesRow + 1

    def addNodeToFile(self, rootElement, dictOfColumns, dictOfColumnsChoices):

        for element in rootElement.iterchildren():
            self.surveyRow = self.surveyRow + 1
            if element.tag == "group" or element.tag == "repeat":
                if element.tag == "group":
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["type"], "begin group"
                    )
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["name"], element.get("name")
                    )

                    if self.languages:
                        for language in self.languages:
                            self.sheet1.write(
                                self.surveyRow,
                                dictOfColumns["label_{}".format(language["lang_code"])],
                                element.get("label_{}".format(language["lang_code"])),
                            )
                    else:
                        self.sheet1.write(
                            self.surveyRow, dictOfColumns["label"], element.get("label")
                        )

                    self.sheet1.write(
                        self.surveyRow,
                        dictOfColumns["appearance"],
                        element.get("appearance"),
                    )
                if element.tag == "repeat":
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["type"], "begin repeat"
                    )
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["name"], element.get("name")
                    )

                    if self.languages:
                        for language in self.languages:
                            self.sheet1.write(
                                self.surveyRow,
                                dictOfColumns["label_{}".format(language["lang_code"])],
                                element.get("label_{}".format(language["lang_code"])),
                            )
                    else:
                        self.sheet1.write(
                            self.surveyRow, dictOfColumns["label"], element.get("label")
                        )

                    self.sheet1.write(
                        self.surveyRow,
                        dictOfColumns["appearance"],
                        element.get("appearance"),
                    )
                self.addNodeToFile(element, dictOfColumns, dictOfColumnsChoices)
                if element.tag == "group":
                    self.surveyRow = self.surveyRow + 1
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["type"], "end group"
                    )
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["name"], element.get("name")
                    )
                if element.tag == "repeat":
                    self.surveyRow = self.surveyRow + 1
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["type"], "end repeat"
                    )
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["name"], element.get("name")
                    )
            else:
                if element.tag != "root":
                    if (
                        element.get("type") != "select_one"
                        and element.get("type") != "select_multiple"
                    ):
                        self.sheet1.write(
                            self.surveyRow, dictOfColumns["type"], element.get("type")
                        )
                    else:
                        duplicated_list, duplicated_name = self.get_options(
                            element.get("name"), element[0]
                        )
                        if not duplicated_list:
                            self.sheet1.write(
                                self.surveyRow,
                                dictOfColumns["type"],
                                element.get("type")
                                + " "
                                + element.get("name")
                                + "_opts",
                            )
                            self.addOptionToFile(
                                element[0],
                                element.get("name") + "_opts",
                                dictOfColumnsChoices,
                            )
                        else:
                            self.sheet1.write(
                                self.surveyRow,
                                0,
                                element.get("type") + " " + duplicated_name + "_opts",
                            )
                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["name"], element.get("name")
                    )
                    if self.languages:
                        for language in self.languages:
                            self.sheet1.write(
                                self.surveyRow,
                                dictOfColumns["label_{}".format(language["lang_code"])],
                                element.get("label_{}".format(language["lang_code"])),
                            )
                    else:
                        self.sheet1.write(
                            self.surveyRow, dictOfColumns["label"], element.get("label")
                        )

                    self.sheet1.write(
                        self.surveyRow, dictOfColumns["hint"], element.get("hint")
                    )
                    self.sheet1.write(
                        self.surveyRow,
                        dictOfColumns["constraint"],
                        element.get("constraint"),
                    )
                    self.sheet1.write(
                        self.surveyRow,
                        dictOfColumns["calculation"],
                        element.get("calculation"),
                    )
                    self.sheet1.write(
                        self.surveyRow,
                        dictOfColumns["required"],
                        element.get("required"),
                    )

                    if element.get("appearance") is not None:
                        self.sheet1.write(
                            self.surveyRow,
                            dictOfColumns["appearance"],
                            element.get("appearance"),
                        )

                    if element.get("type") == "barcode":
                        if self.languages:
                            for language in self.languages:
                                self.sheet1.write(
                                    self.surveyRow,
                                    dictOfColumns[
                                        "constraint_message_{}".format(
                                            language["lang_code"]
                                        )
                                    ],
                                    getTranslationOrText(
                                        [],
                                        "14",
                                        "The scanned Qr is incorrect, it is not for this project",
                                        self.userOwner,
                                        self.request,
                                        specificLanguage=language["lang_code"],
                                    ),
                                )
                        else:
                            self.sheet1.write(
                                self.surveyRow,
                                dictOfColumns["constraint_message"],
                                getTranslationOrText(
                                    [],
                                    "14",
                                    "The scanned QR is incorrect, it is not for this project",
                                    self.userOwner,
                                    self.request,
                                    specificLanguage="en",
                                ),
                            )

                    if element.get("required") == "True":
                        if self.languages:
                            for language in self.languages:
                                self.sheet1.write(
                                    self.surveyRow,
                                    dictOfColumns[
                                        "required_message_{}".format(
                                            language["lang_code"]
                                        )
                                    ],
                                    element.get(
                                        "label_{}".format(language["lang_code"])
                                    )
                                    + " "
                                    + getTranslationOrText(
                                        [],
                                        "10",
                                        "requires a value",
                                        self.userOwner,
                                        self.request,
                                        specificLanguage=language["lang_code"],
                                    ),
                                )
                        else:
                            self.sheet1.write(
                                self.surveyRow,
                                dictOfColumns["required_message"],
                                element.get("label")
                                + getTranslationOrText(
                                    [],
                                    "10",
                                    "requires a value",
                                    self.userOwner,
                                    self.request,
                                    specificLanguage="en",
                                ),
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
            if not self.languages:
                question.set("label", label)
            else:
                if isinstance(label, str):
                    for language in self.languages:
                        question.set("label_{}".format(language["lang_code"]), label)
                else:
                    for language in label:
                        question.set(language["label"], language["value"])

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
                        if not self.languages:
                            value.set("label", label)
                        else:
                            if isinstance(label, str):
                                for language in self.languages:
                                    value.set(
                                        "label_{}".format(language["lang_code"]), label
                                    )
                            else:
                                for language in label:
                                    value.set(language["label"], language["value"])

                        evalues.append(value)
                else:
                    evalues = etree.Element("values")
                    equestion.append(evalues)
                    value = etree.Element("value")
                    value.set("code", code)
                    if not self.languages:
                        value.set("label", label)
                    else:
                        if isinstance(label, str):
                            for language in self.languages:
                                value.set(
                                    "label_{}".format(language["lang_code"]), label
                                )
                        else:
                            for language in label:
                                value.set(language["label"], language["value"])
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
        dictOfColumns = {}
        columnsCount = 0
        self.sheet1.write(0, columnsCount, "type")
        dictOfColumns["type"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "name")
        dictOfColumns["name"] = columnsCount
        columnsCount += 1

        if self.languages:
            for language in self.languages:
                self.sheet1.write(
                    0,
                    columnsCount,
                    "label::{} ({})".format(
                        language["lang_name"], language["lang_code"]
                    ),
                )
                dictOfColumns["label_{}".format(language["lang_code"])] = columnsCount
                columnsCount += 1
            columnsCount -= 1
        else:
            self.sheet1.write(0, columnsCount, "label")
            dictOfColumns["label"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "hint")
        dictOfColumns["hint"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "constraint")
        dictOfColumns["constraint"] = columnsCount
        columnsCount += 1

        if self.languages:
            for language in self.languages:
                self.sheet1.write(
                    0,
                    columnsCount,
                    "constraint_message::{} ({})".format(
                        language["lang_name"], language["lang_code"]
                    ),
                )
                dictOfColumns[
                    "constraint_message_{}".format(language["lang_code"])
                ] = columnsCount
                columnsCount += 1
            columnsCount -= 1
        else:
            self.sheet1.write(0, columnsCount, "constraint_message")
            dictOfColumns["constraint_message"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "required")
        dictOfColumns["required"] = columnsCount
        columnsCount += 1

        if self.languages:
            for language in self.languages:
                self.sheet1.write(
                    0,
                    columnsCount,
                    "required_message::{} ({})".format(
                        language["lang_name"], language["lang_code"]
                    ),
                )
                dictOfColumns[
                    "required_message_{}".format(language["lang_code"])
                ] = columnsCount
                columnsCount += 1
            columnsCount -= 1
        else:
            self.sheet1.write(0, columnsCount, "required_message")
            dictOfColumns["required_message"] = columnsCount

        columnsCount += 1
        self.sheet1.write(0, columnsCount, "appearance")
        dictOfColumns["appearance"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "default")
        dictOfColumns["default"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "relevant")
        dictOfColumns["relevant"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "repeat_count")
        dictOfColumns["repeat_count"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "read_only")
        dictOfColumns["read_only"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "choice_filter")
        dictOfColumns["choice_filter"] = columnsCount
        columnsCount += 1
        self.sheet1.write(0, columnsCount, "calculation")
        dictOfColumns["calculation"] = columnsCount

        # CHOICES
        dictOfColumnsChoices = {}
        columnsCountChoices = 0
        self.sheet2.write(0, columnsCountChoices, "list_name")
        dictOfColumnsChoices["list_name"] = columnsCountChoices
        columnsCountChoices += 1
        self.sheet2.write(0, columnsCountChoices, "name")
        dictOfColumnsChoices["name"] = columnsCountChoices
        columnsCountChoices += 1
        if self.languages:
            for language in self.languages:
                self.sheet2.write(
                    0,
                    columnsCountChoices,
                    "label::{} ({})".format(
                        language["lang_name"], language["lang_code"]
                    ),
                )
                dictOfColumnsChoices[
                    "label_{}".format(language["lang_code"])
                ] = columnsCountChoices
                columnsCountChoices += 1
            columnsCountChoices -= 1
        else:
            self.sheet2.write(0, columnsCountChoices, "label")
            dictOfColumnsChoices["label"] = columnsCountChoices

        sheet3 = self.book.add_worksheet("settings")
        sheet3.write(0, 0, "form_id")
        sheet3.write(0, 1, "form_title")
        sheet3.write(0, 2, "instance_name")
        if self.languages:
            sheet3.write(0, 3, "default_language")

        sheet3.write(1, 0, self.formID)
        sheet3.write(1, 1, self.formLabel)
        sheet3.write(1, 2, self.formInstance)

        if self.languages:
            for language in self.languages:
                if language["lang_default"] == 1:
                    sheet3.write(
                        1,
                        3,
                        "{} ({})".format(language["lang_name"], language["lang_code"]),
                    )

        self.addNodeToFile(self.root, dictOfColumns, dictOfColumnsChoices)
        self.book.close()


def renderQuestion(question, fielName, option, value=None):
    if value:
        renderedString = Environment().from_string(value).render(option=option)
    else:
        renderedString = (
            Environment().from_string(question[fielName]).render(option=option)
        )

    return renderedString


def getI18nGeneralPhrase(language, textId, userName, request):

    translation = getPhraseTranslationInLanguage(request, textId, userName, language)
    if translation:
        return translation["phrase_desc"]
    else:
        if userName != "bioversity":
            return getI18nGeneralPhrase(language, textId, "bioversity", request)
        else:
            translation = mapFromSchema(
                request.dbsession.query(generalPhrases)
                .filter(generalPhrases.phrase_id == textId)
                .first()
            )

            return translation["phrase_desc"]


def getTranslationOrText(
    prjLanguages,
    textId,
    text,
    userOwner,
    request,
    specificLanguage=None,
    additionalOne=None,
    additionalTwo=None,
):

    if not specificLanguage:
        if prjLanguages:
            qstDesc = []

            for language in prjLanguages:
                dictTraduction = {}
                dictTraduction["label"] = "label_{}".format(language["lang_code"])
                try:
                    val = getI18nGeneralPhrase(
                        language["lang_code"], textId, userOwner, request
                    )
                    if additionalOne:
                        val = val + additionalOne

                    dictTraduction["value"] = val

                    if textId in ["16", "17"]:
                        val2 = dictTraduction["value"] + getI18nGeneralPhrase(
                            language["lang_code"], 18, userOwner, request
                        )
                        if additionalTwo:
                            val2 = val2 + additionalTwo

                        dictTraduction["value"] = val2
                except:
                    print("ERROR:******************************52****************")
                    dictTraduction["value"] = text

                qstDesc.append(dictTraduction)

            return qstDesc
        else:
            return text
    else:
        return getI18nGeneralPhrase(specificLanguage, textId, userOwner, request)


def translateQuestion(
    prjLanguages,
    question,
    request,
    fieldName,
    descExtra="",
    requireRender=False,
    optionRender="",
):
    if prjLanguages:
        qstDesc = []

        for language in prjLanguages:
            dictTraduction = {}
            dictTraduction["label"] = "label_{}".format(language["lang_code"])
            # Esto es porque la preguntas ya vienen en el lenguaje por default, ya no hay que traducirlas
            if language["lang_default"] == 1:
                if not requireRender:
                    dictTraduction["value"] = question[fieldName]
                else:
                    dictTraduction["value"] = renderQuestion(
                        question, fieldName, optionRender
                    )
            else:
                traduction, value = getFieldTranslationByLanguage(
                    request, question.question_id, language["lang_code"], fieldName
                )
                if not requireRender:
                    if traduction:
                        dictTraduction["value"] = value
                    else:
                        dictTraduction["value"] = question[fieldName]
                else:
                    dictTraduction["value"] = renderQuestion(
                        question, fieldName, optionRender, value
                    )

            qstDesc.append(dictTraduction)
    else:
        if not requireRender:
            qstDesc = question[fieldName] + descExtra
        else:
            qstDesc = renderQuestion(question, fieldName, optionRender)

    return qstDesc


def translateQuestionOption(prjLanguages, questionId, option, request):

    if prjLanguages:
        optionDesc = []

        for language in prjLanguages:
            dictTraduction = {}
            dictTraduction["label"] = "label_{}".format(language["lang_code"])
            if language["lang_default"] == 1:
                dictTraduction["value"] = option["value_desc"]
            else:
                traduction, value = getFieldTranslationQuestionOptionByLanguage(
                    request, questionId, language["lang_code"], option["value_code"]
                )
                if traduction:
                    dictTraduction["value"] = value
                else:
                    dictTraduction["value"] = option["value_desc"]

            optionDesc.append(dictTraduction)

    else:
        optionDesc = option["value_desc"]

    return optionDesc


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
    language="default",
):
    _ = request.translate

    prjLanguages = getPrjLangInProject(projectId, request)

    excelFile = ODKExcelFile(
        xlsxFile, formID, formLabel, formInstance, _, prjLanguages, userOwner, request
    )
    excelFile.addQuestion(
        "clm_deviceimei",
        getTranslationOrText(prjLanguages, "5", "Device IMEI", userOwner, request),
        23,
        "",
    )
    excelFile.addQuestion(
        "clm_start",
        getTranslationOrText(prjLanguages, "9", "Start of survey", userOwner, request),
        20,
        "",
    )

    # Edited by Brandon
    for group in groups:
        excelFile.addGroup("grp_" + str(group.section_id), group.section_name)
        if group.section_id == selectedPackageQuestionGroup:
            excelFile.addGroup(
                "grp_validation",
                getTranslationOrText(
                    prjLanguages,
                    "13",
                    "Validation of the selected participant",
                    userOwner,
                    request,
                ),
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
            getTranslationOrText(
                prjLanguages,
                "17",
                "You scanned package number:",
                userOwner,
                request,
                additionalOne=' <span style="color:#009551; font-weight:bold">${clc_after}</span>.<br>',
                additionalTwo=' <span style="color:#009551; font-weight:bold">${farmername}</span>.',
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
            getTranslationOrText(
                prjLanguages,
                "16",
                "You selected package number:",
                userOwner,
                request,
                additionalOne=' <span style="color:#009551; font-weight:bold">${QST163}</span>.<br>',
                additionalTwo=' <span style="color:#009551; font-weight:bold">${clc_after}</span>',
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

                    qstDesc = translateQuestion(
                        prjLanguages,
                        question,
                        request,
                        "question_desc",
                        descExtra=descExtra,
                    )

                    excelFile.addQuestion(
                        question.question_code + nameExtra,
                        qstDesc,
                        question.question_dtype,
                        question.question_unit,
                        question.question_requiredvalue,
                        "grp_" + str(question.section_id),
                    )
                else:
                    # print "EL PACKAGE CODE"
                    lenuser = len(userOwner) + 1
                    qstDesc = translateQuestion(
                        prjLanguages, question, request, "question_desc"
                    )

                    excelFile.addQuestion(
                        question.question_code,
                        qstDesc,
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
                        getTranslationOrText(
                            prjLanguages,
                            "15",
                            "In the following field try to write the name of the participant to filter the information and find him/her more easily.",
                            userOwner,
                            request,
                        ),
                        29,
                        inGroup="grp_" + str(question.section_id),
                    )

                    qstDesc = translateQuestion(
                        prjLanguages, question, request, "question_desc"
                    )

                    excelFile.addQuestion(
                        question.question_code,
                        qstDesc,
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
                                "char_" + question.question_code,
                                str(98),
                                getTranslationOrText(
                                    prjLanguages, "1", "Tied", userOwner, request
                                ),
                            )

                        if question.question_notobserved == 1:
                            excelFile.addOption(
                                "char_" + question.question_code,
                                str(99),
                                getTranslationOrText(
                                    prjLanguages,
                                    "6",
                                    "Not observed",
                                    userOwner,
                                    request,
                                ),
                            )

                    if numComb == 3:
                        qstDesc = translateQuestion(
                            prjLanguages, question, request, "question_posstm"
                        )

                        excelFile.addQuestion(
                            "char_" + question.question_code + "_pos",
                            qstDesc,
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
                        qstDesc = translateQuestion(
                            prjLanguages, question, request, "question_negstm"
                        )

                        excelFile.addQuestion(
                            "char_" + question.question_code + "_neg",
                            qstDesc,
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
                                getTranslationOrText(
                                    prjLanguages, "1", "Tied", userOwner, request
                                ),
                            )
                            excelFile.addOption(
                                "char_" + question.question_code + "_neg",
                                str(98),
                                getTranslationOrText(
                                    prjLanguages, "1", "Tied", userOwner, request
                                ),
                            )
                        if question.question_notobserved == 1:
                            excelFile.addOption(
                                "char_" + question.question_code + "_pos",
                                str(99),
                                getTranslationOrText(
                                    prjLanguages,
                                    "6",
                                    "Not observed",
                                    userOwner,
                                    request,
                                ),
                            )

                            excelFile.addOption(
                                "char_" + question.question_code + "_neg",
                                str(99),
                                getTranslationOrText(
                                    prjLanguages,
                                    "6",
                                    "Not observed",
                                    userOwner,
                                    request,
                                ),
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
                                    getTranslationOrText(
                                        prjLanguages, "1", "Tied", userOwner, request
                                    ),
                                )

                            if question.question_notobserved == 1:
                                excelFile.addOption(
                                    "char_"
                                    + question.question_code
                                    + "_stmt_"
                                    + str(99),
                                    str(99),
                                    getTranslationOrText(
                                        prjLanguages,
                                        "6",
                                        "Not observed",
                                        userOwner,
                                        request,
                                    ),
                                )

                if question.question_dtype == 10:
                    for opt in range(0, numComb):
                        renderedString = translateQuestion(
                            prjLanguages,
                            question,
                            request,
                            "question_perfstmt",
                            requireRender=True,
                            optionRender=listOfLabelsForPackages[opt],
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
                            getTranslationOrText(
                                prjLanguages, "4", "Better", userOwner, request
                            ),
                        )
                        excelFile.addOption(
                            "perf_" + question.question_code + "_" + str(opt + 1),
                            "2",
                            getTranslationOrText(
                                prjLanguages, "2", "Worse", userOwner, request
                            ),
                        )

            if question.question_dtype == 5 or question.question_dtype == 6:
                print("****generateODKFile**Query options******")
                sql = (
                    " SELECT qstoption.value_code, coalesce(i18n_qstoption.value_desc, qstoption.value_desc) as value_desc,qstoption.value_isother,qstoption.value_order "
                    " FROM question,qstoption "
                    "LEFT JOIN i18n_qstoption "
                    " ON i18n_qstoption.question_id = qstoption.question_id "
                    " AND i18n_qstoption.value_code = qstoption.value_code "
                    " AND i18n_qstoption.lang_code = '" + language + "' "
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

                    optionDesc = translateQuestionOption(
                        prjLanguages, question.question_id, value, request
                    )

                    excelFile.addOption(
                        question.question_code + nameExtra,
                        value.value_code,
                        optionDesc,
                    )
                if other:
                    qstDesc = translateQuestion(
                        prjLanguages,
                        question,
                        request,
                        "question_desc",
                        descExtra=descExtra
                        + " "
                        + getTranslationOrText(
                            prjLanguages, "3", "Other", userOwner, request
                        ),
                    )

                    excelFile.addQuestion(
                        question.question_code + nameExtra + "_oth",
                        qstDesc,
                        1,
                        getTranslationOrText(
                            prjLanguages,
                            "12",
                            "Add the other value here",
                            userOwner,
                            request,
                        ),
                        0,
                        "grp_" + str(question.section_id),
                    )

    excelFile.addQuestion(
        "clm_end",
        getTranslationOrText(prjLanguages, "7", "End of survey", userOwner, request),
        21,
        "",
    )

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

    langDefault = getPrjLangDefaultInProject(projectId, request)
    if langDefault:
        default_language = "({}){}".format(
            langDefault["lang_code"], langDefault["lang_name"]
        )
        langDefault = langDefault["lang_code"]
    else:
        langDefault = "default"
        default_language = None

    sql = (
        "SELECT q.question_code,COALESCE(i.question_desc,q.question_desc) as question_desc,COALESCE(i.question_unit,q.question_unit) as question_unit, q.question_dtype, q.question_twoitems, "
        "r.section_id, COALESCE(i.question_posstm, q.question_posstm) as question_posstm, COALESCE(i.question_negstm ,q.question_negstm) as question_negstm, q.question_moreitems, COALESCE(i.question_perfstmt, q.question_perfstmt) as question_perfstmt, "
        "q.question_requiredvalue, r.question_order, q.question_id, q.question_tied, q.question_notobserved, q.question_quantitative "
        "FROM registry r,question q "
        " LEFT JOIN i18n_question i "
        " ON        q.question_id = i.question_id "
        " AND       i.lang_code = '" + langDefault + "' "
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
        language=langDefault,
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
    listLang = []
    for lang in prjdata["languages"]:
        if lang["lang_default"] != 1:
            listLang.append("({}){}".format(lang["lang_code"], lang["lang_name"]))

    if listLang:
        other_languages = ",".join(listLang)
    else:
        other_languages = None

    paths = ["db", "reg"]
    state, error = createDatabase(
        xlsxFile,
        os.path.join(path, *paths),
        userOwner + "_" + projectCod,
        keyQuestion.question_code,
        "REG",
        True,
        request,
        default_language=default_language,
        other_languages=other_languages,
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

        langDefault = getPrjLangDefaultInProject(projectId, request)
        if langDefault:
            default_language = "({}){}".format(
                langDefault["lang_code"], langDefault["lang_name"]
            )
            langDefault = langDefault["lang_code"]
        else:
            langDefault = "default"

        sql = (
            " SELECT q.question_code, COALESCE(i.question_desc,q.question_desc) as question_desc,COALESCE(i.question_unit,q.question_unit) as question_unit, q.question_dtype, q.question_twoitems, "
            " a.section_id, COALESCE(i.question_posstm, q.question_posstm) as question_posstm, COALESCE(i.question_negstm ,q.question_negstm) as question_negstm, q.question_moreitems, COALESCE(i.question_perfstmt, q.question_perfstmt) as question_perfstmt, "
            " q.question_requiredvalue, q.question_id, q.question_tied, q.question_notobserved, q.question_quantitative "
            " FROM assdetail a, question q "
            " LEFT JOIN i18n_question i "
            " ON        q.question_id = i.question_id "
            " AND       i.lang_code = '" + langDefault + "' "
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
            language=langDefault,
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

            listLang = []
            for lang in prjdata["languages"]:
                if lang["lang_default"] != 1:
                    listLang.append(
                        "({}){}".format(lang["lang_code"], lang["lang_name"])
                    )

            if listLang:
                other_languages = ",".join(listLang)
            else:
                other_languages = None

            # Edited by Brandon -> The validation was incorrect if createDatabase
            state, error = createDatabase(
                xlsxFile,
                os.path.join(path, *paths),
                userOwner + "_" + projectCod,
                keyQuestion.question_code,
                "ASS" + assessment.ass_cod,
                False,
                request,
                default_language=default_language,
                other_languages=other_languages,
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
