from enum import Enum

# This function is just for detecting the messages for the translation
def _(x):
    return x


class FieldValidation(Enum):
    SUCCESS = None
    UNALLOWED = _("ENUM. The following fields are not allowed: ")
    MISSING = _("ENUM. The following fields are required: ")
    BLANK = _("ENUM. The following fields require a value: ")
    NOT_BINARY = _("ENUM. The following fields may only have values of 0 or 1: ")
    NOT_INTEGER = _("ENUM. The following fields must be integers: ")
