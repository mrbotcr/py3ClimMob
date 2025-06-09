from dataclasses import dataclass

from .FieldValidation import FieldValidation


@dataclass
class Field:
    key: str = None
    required: bool = False
    not_blank: bool = False
    _stages = []

    def __post_init__(self):
        self._stages = [
            {"validation": FieldValidation.MISSING, "function": self.check_required},
            {"validation": FieldValidation.BLANK, "function": self.check_not_blank},
        ]

    def validate(self, body, first_error_found) -> FieldValidation:
        for stage in self._stages:
            result = stage["function"](body)
            if result != FieldValidation.SUCCESS:
                return result

            if stage["validation"] == first_error_found:
                break

        return FieldValidation.SUCCESS

    def check_required(self, body: dict) -> FieldValidation:
        if self.required:
            try:
                _ = body[self.key]
            except KeyError:
                return FieldValidation.MISSING

        return FieldValidation.SUCCESS

    def check_not_blank(self, body: dict) -> FieldValidation:
        if self.not_blank:
            value = body.get(self.key)
            if value == "":
                return FieldValidation.BLANK

        return FieldValidation.SUCCESS
