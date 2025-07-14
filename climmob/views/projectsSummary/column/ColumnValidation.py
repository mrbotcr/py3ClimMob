from enum import Enum

# This function is just for detecting the messages for the translation
def _(x):
    return x


class ColumnValidation(Enum):
    SUCCESS = None
    BLANK_KEY = _("The Key requires a value.")
    BLANK_NAME = _("The Name requires a value.")
    LONG_KEY = _("The 'key' is too long (max 50 characters).")
    LONG_NAME = _("The 'column_name' is too long (max 50 characters).")
    REPEAT_KEY = _("This key column already exists.")
    INVALID_TYPE = _("The 'type' must be one of: 'input', 'dropdown', 'static'.")
    INCONSISTENT_EDITABLE = _("A 'static' type cannot be editable.")
    OPTION_NOT_DICT = _("The option field must be a list.")
    EMPTY_OPTION_DICT = _("The option list cannot be empty.")
    INVALID_OPTION_ITEM = _("The option field must be a dictionary.")
    INVALID_OPTION_KEY = _("All options must be non-empty strings.")
    INVALID_OPTION_VALUE = _("All options must be non-empty integer")
    UNIQUE_KEY = _("The key should be unique, the used already exists.")
    REQUIRE_BOOL = _("The data should be boolean.")
    REQUIRE_INT = _("The data should be integer.")
