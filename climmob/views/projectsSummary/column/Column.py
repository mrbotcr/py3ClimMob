from dataclasses import dataclass, field
from typing import List, Optional
from climmob.views.projectsSummary.column.ColumnValidation import ColumnValidation

MAX_KEY_LENGTH = 50
MAX_NAME_LENGTH = 50
VALID_TYPES = ("static", "input", "dropdown")

@dataclass
class Column:
    id: int
    key: str
    column_name: str
    type: str = "static"
    field_editable: bool = False
    show: bool = True
    options: Optional[List[str]] = field(default_factory=list)

    def __post_init__(self):
        self._stages = [
            {"validation": ColumnValidation.REQUIRE_INT, "function": self.check_int},
            {"validation": ColumnValidation.BLANK_KEY, "function": self.check_required_key},
            {"validation": ColumnValidation.LONG_KEY, "function": self.check_key_length},
            {"validation": ColumnValidation.BLANK_NAME, "function": self.check_required_name},
            {"validation": ColumnValidation.LONG_NAME, "function": self.check_name_length},
            {"validation": ColumnValidation.REQUIRE_BOOL, "function": self.check_show},
            {"validation": ColumnValidation.INVALID_TYPE, "function": self.check_type},
            {"validation": ColumnValidation.INCONSISTENT_EDITABLE, "function": self.check_editable_consistency},
            {"validation": ColumnValidation.UNIQUE_KEY, "function": self.check_unique_key},
        ]

        # check for dropdown
        if self.type == "dropdown":
            self._stages.extend([
                {"validation": ColumnValidation.OPTION_NOT_LIST, "function": self.check_options_type},
                {"validation": ColumnValidation.EMPTY_OPTION_LIST, "function": self.check_options_non_empty},
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
        if not self.id or not isinstance(id, int):
            return ColumnValidation.REQUIRE_INT
        return ColumnValidation.SUCCESS

    def check_required_key(self):
        if not self.key or not self.key.strip():
            return ColumnValidation.BLANK_KEY
        return ColumnValidation.SUCCESS

    def check_key_length(self):
        if len(self.key) > MAX_KEY_LENGTH:
            return ColumnValidation.LONG_KEY
        return ColumnValidation.SUCCESS

    def check_required_name(self):
        if not self.column_name or not self.column_name.strip():
            return ColumnValidation.BLANK_NAME
        return ColumnValidation.SUCCESS

    def check_name_length(self):
        if len(self.column_name) > MAX_NAME_LENGTH:
            return ColumnValidation.LONG_NAME
        return ColumnValidation.SUCCESS

    def check_show(self):
        if self.field_editable:
            return ColumnValidation.INVALID_TYPE
        return ColumnValidation.SUCCESS

    def check_type(self):
        if self.type not in VALID_TYPES:
            return ColumnValidation.INVALID_TYPE
        return ColumnValidation.SUCCESS

    def check_editable_consistency(self):
        if self.type == "static" and self.field_editable:
            return ColumnValidation.INCONSISTENT_EDITABLE
        return ColumnValidation.SUCCESS

    # espacio para exepcion por coliciones (elementos iguales) necesito la BD para consultar
    def check_unique_key(self):
        # TODO: Implementar con lista o DB externa
        return ColumnValidation.SUCCESS

    # ====== dropdown check ======
    def check_options_type(self):
        if not isinstance(self.options, list):
            return ColumnValidation.OPTION_NOT_LIST
        return ColumnValidation.SUCCESS

    def check_options_non_empty(self):
        if not self.options:
            return ColumnValidation.EMPTY_OPTION_LIST
        return ColumnValidation.SUCCESS

    def check_options_items(self):
        for opt in self.options:
            if not isinstance(opt, str) or not opt.strip():
                return ColumnValidation.INVALID_OPTION_ITEM
        return ColumnValidation.SUCCESS
