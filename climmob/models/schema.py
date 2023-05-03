import json

from future.utils import iteritems
from sqlalchemy import inspect

from climmob.models.meta import metadata

__all__ = [
    "initialize_schema",
    "addColumnToSchema",
    "mapToSchema",
    "mapFromSchema",
    "add_modules_to_schema",
]

_SCHEMA = []
_MODULES = []


def initialize_schema():
    for table in metadata.sorted_tables:
        fields = []
        for column in table.c:
            fields.append(
                {"name": column.name, "storage": "db", "comment": column.comment}
            )
        table_found = False
        for a_table in _SCHEMA:
            if a_table["name"] == table.name:
                table_found = True
                break
        if not table_found:
            _SCHEMA.append({"name": table.name, "fields": fields})


def add_modules_to_schema(module_list):
    for a_module in module_list:
        _MODULES.append(a_module)


# This function add new columns to the schema in the extra field
def addColumnToSchema(tableName, fieldName, fieldComment):
    for pos in range(len(_SCHEMA)):
        if _SCHEMA[pos]["name"] == tableName:
            found = False
            for field in _SCHEMA[pos]["fields"]:
                if field["name"] == fieldName:
                    found = True
            if not found:
                _SCHEMA[pos]["fields"].append(
                    {"name": fieldName, "storage": "extra", "comment": fieldComment}
                )
            else:
                raise Exception("Field {} is already defined".format(fieldName))


def getStorageType(tableName, fieldName):
    storageType = None
    for table in _SCHEMA:
        if table["name"] == tableName:
            for field in table["fields"]:
                if field["name"] == fieldName:
                    storageType = field["storage"]
    return storageType


def getDictionaryOfModel(modelClass):

    tableName = modelClass.__table__.name
    dict = {}

    for table in _SCHEMA:
        if table["name"] == tableName:
            for field in table["fields"]:
                dict[field["name"]] = ""
    return dict


# This function maps a data dict to the schema
# Data fields that are mapped to the extra storage are converted to JSON and stored in _extra
# Data fields that are not present in the schema are discarded
# The function returns a mapped dict that can be used to add or update data
def mapToSchema(modelClass, data):
    mappedData = {}
    extraData = {}
    for key, value in iteritems(data):
        storageType = getStorageType(modelClass.__table__.name, key)
        if storageType is not None:
            if storageType == "db":
                mappedData[key] = value
            else:
                extraData[key] = value
    if bool(extraData):
        mappedData["extra"] = json.dumps(extraData)
    if not bool(mappedData):
        raise Exception("The mapping for table {} is empty!".format(modelClass.name))
    return mappedData


# This function maps a row/list of raw data from de database to the schema
# Data fields that resided i the extra storage are separated into independent fields
# The function returns the data in a dict form or an array of dict
"""
def mapFromSchema(data):
    if type(data) is not list:
        mappedData = {}
        if data is not None:
            for c in inspect(data).mapper.column_attrs:
                if c.key != "extra":
                    if isinstance(getattr(data, c.key), str):
                        #mappedData[c.key] = getattr(data, c.key).decode("utf8")
                        #else:
                        mappedData[c.key] = getattr(data, c.key)
                else:
                    if getattr(data, c.key) is not None:
                        jsondata = json.loads(getattr(data, c.key))
                        if bool(jsondata):
                            for key,value in jsondata.items():
                                mappedData[key] = value
        return mappedData
    else:
        mappedData = []
        for row in data:
            temp = {}
            for c in inspect(row).mapper.column_attrs:
                if c.key != "extra":
                    if isinstance(getattr(row, c.key), str):
                        temp[c.key] = getattr(row, c.key).decode("utf8")
                    else:
                        temp[c.key] = getattr(row, c.key)
                else:
                    if getattr(row, c.key) is not None:
                        jsondata = json.loads(getattr(row, c.key))
                        if bool(jsondata):
                            for key, value in jsondata.iteritems():
                                temp[key] = value
            mappedData.append(temp)
        return mappedData
"""


def mapFromSchema(data):
    """
    This function maps a row/list of raw data from de database to the schema
    Data fields that resided in the extra storage are separated into independent fields
    :param data: Data as stored in the database
    :return: The data in a dict form or an array of dict
    """
    if type(data) is not list:
        mapped_data = {}
        if data is not None:
            if data.__class__.__name__ != "Row":
                for c in inspect(data).mapper.column_attrs:
                    if c.key != "extra":
                        mapped_data[c.key] = getattr(data, c.key)
                    else:
                        if getattr(data, c.key) is not None:
                            jsondata = json.loads(getattr(data, c.key))
                            if bool(jsondata):
                                for key, value in iteritems(jsondata):
                                    mapped_data[key] = value
            else:
                # noinspection PyProtectedMember
                dict_result = data._asdict()  # This is not private
                for key, value in dict_result.items():
                    if value.__class__.__module__ in _MODULES:
                        for c in inspect(value).mapper.column_attrs:
                            if c.key != "extra":
                                mapped_data[c.key] = getattr(value, c.key)
                            else:
                                if getattr(value, c.key) is not None:
                                    jsondata = json.loads(getattr(value, c.key))
                                    if bool(jsondata):
                                        for key2, value2 in iteritems(jsondata):
                                            mapped_data[key2] = value2
                    else:
                        mapped_data[key] = value

        return mapped_data
    else:
        mapped_data = []
        for row in data:
            temp = {}
            if row.__class__.__name__ != "Row":
                for c in inspect(row).mapper.column_attrs:
                    if c.key != "extra":
                        temp[c.key] = getattr(row, c.key)
                    else:
                        if getattr(row, c.key) is not None:
                            jsondata = json.loads(getattr(row, c.key))
                            if bool(jsondata):
                                for key, value in iteritems(jsondata):
                                    temp[key] = value
            else:
                # noinspection PyProtectedMember
                dict_result = row._asdict()  # This is not private
                for key, value in dict_result.items():
                    if value.__class__.__module__ in _MODULES:
                        for c in inspect(value).mapper.column_attrs:
                            if c.key != "extra":
                                temp[c.key] = getattr(value, c.key)
                            else:
                                if getattr(value, c.key) is not None:
                                    jsondata = json.loads(getattr(value, c.key))
                                    if bool(jsondata):
                                        for key2, value2 in iteritems(jsondata):
                                            temp[key2] = value2
                    else:
                        temp[key] = value

            mapped_data.append(temp)
        return mapped_data
