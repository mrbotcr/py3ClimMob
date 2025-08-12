from dataclasses import dataclass

from .Field import Field
from .FieldValidation import FieldValidation


@dataclass
class IntegerField(Field):
    def __post_init__(self):
        super().__post_init__()
        self._stages.extend(
            [
                {
                    "validation": FieldValidation.NOT_INTEGER,
                    "function": self.check_integer,
                }
            ]
        )

    def check_integer(self, body: dict):
        value = body.get(self.key)
        try:
            int(value)
            return FieldValidation.SUCCESS
        except ValueError:
            return FieldValidation.NOT_INTEGER
