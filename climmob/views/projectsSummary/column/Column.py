from dataclasses import dataclass, field
from typing import List, Optional
from climmob.views.projectsSummary.column.ColumnValidation import ColumnValidation


MAX_KEY_LENGTH = 50
MAX_NAME_LENGTH = 50
VALID_TYPES = ['static', 'input', 'dropdown']

@dataclass
class Column:
    id: int
    key: str
    name: str
    type: str = "static"
    show: bool = True
    options: Optional[dict] = field(default_factory=dict)

    existing_keys: Optional[set] = None

    def __post_init__(self):
        self._stages = [
            {"validation": ColumnValidation.REQUIRE_INT, "function": self.check_int},
            {"validation": ColumnValidation.BLANK_KEY, "function": self.check_required_key},
            {"validation": ColumnValidation.LONG_KEY, "function": self.check_key_length},
            {"validation": ColumnValidation.BLANK_NAME, "function": self.check_required_name},
            {"validation": ColumnValidation.LONG_NAME, "function": self.check_name_length},
            {"validation": ColumnValidation.REQUIRE_BOOL, "function": self.check_show},
            {"validation": ColumnValidation.INVALID_TYPE, "function": self.check_type},
            {"validation": ColumnValidation.UNIQUE_KEY, "function": self.check_unique_key},
        ]

        # check for dropdown
        if self.type == "dropdown":
            self._stages.extend([
                {"validation": ColumnValidation.OPTION_NOT_DICT, "function": self.check_options_type},
                {"validation": ColumnValidation.EMPTY_OPTION_DICT, "function": self.check_options_non_empty},
                {"validation": ColumnValidation.INVALID_OPTION_ITEM, "function": self.check_options_items},
            ])

        self.validate()

    def validate(self):
        for stage in self._stages:
            result = stage["function"]()
            if result != ColumnValidation.SUCCESS:
                raise ValueError(result.value)

    # ====== basic check ======
    def check_int(self):
        try:
            int(self.id)
            return ColumnValidation.SUCCESS
        except (TypeError, ValueError):
            return ColumnValidation.REQUIRE_INT

    def check_required_key(self):
        if not self.key or not self.key.strip():
            return ColumnValidation.BLANK_KEY
        return ColumnValidation.SUCCESS

    def check_key_length(self):
        if len(self.key) > MAX_KEY_LENGTH:
            return ColumnValidation.LONG_KEY
        return ColumnValidation.SUCCESS

    def check_required_name(self):
        if not self.name or not self.name.strip():
            return ColumnValidation.BLANK_NAME
        return ColumnValidation.SUCCESS

    def check_name_length(self):
        if len(self.name) > MAX_NAME_LENGTH:
            return ColumnValidation.LONG_NAME
        return ColumnValidation.SUCCESS

    def check_show(self):
        if not isinstance(self.show, bool):
            return ColumnValidation.REQUIRE_BOOL
        return ColumnValidation.SUCCESS

    def check_type(self):
        if not self.type or self.type.strip().lower() not in VALID_TYPES:
            return ColumnValidation.INVALID_TYPE
        return ColumnValidation.SUCCESS

    def check_unique_key(self):
        if self.existing_keys is not None:
            if self.key in self.existing_keys and self.id is None:
                return ColumnValidation.UNIQUE_KEY
        return ColumnValidation.SUCCESS

    # ====== dropdown check ======
    def check_options_type(self):
        if not isinstance(self.options, dict):
            return ColumnValidation.OPTION_NOT_DICT
        return ColumnValidation.SUCCESS

    def check_options_non_empty(self):
        if not self.options:
            return ColumnValidation.EMPTY_OPTION_DICT
        return ColumnValidation.SUCCESS

    def check_options_items(self):
        for key, value in self.options.items():
            if not isinstance(key, str) or not key.strip():
                return ColumnValidation.INVALID_OPTION_KEY
            if not isinstance(value, int):
                return ColumnValidation.INVALID_OPTION_VALUE
        return ColumnValidation.SUCCESS