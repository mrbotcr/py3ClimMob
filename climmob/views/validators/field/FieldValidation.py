from enum import Enum

# This function is just for detecting the messages for the translation
def _(x):
    return x


class FieldValidation(Enum):
    SUCCESS = None
    UNALLOWED = _("The following fields are not allowed: ")
    MISSING = _("The following fields are required: ")
    BLANK = _("The following fields require a value: ")
    NOT_BINARY = _("The following fields may only have values of 0 or 1: ")
    NOT_INTEGER = _("The following fields must be integers: ")
