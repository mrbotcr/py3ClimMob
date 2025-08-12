from dataclasses import dataclass

from . import Field
from .FieldValidation import FieldValidation


@dataclass
class BinaryField(Field):
    def __post_init__(self):
        super().__post_init__()
        self._stages.extend(
            [{"validation": FieldValidation.NOT_BINARY, "function": self.check_binary}]
        )

    def check_binary(self, body: dict):
        value = body.get(self.key)
        if str(value) in ["0", "1"]:
            return FieldValidation.SUCCESS
        else:
            return FieldValidation.NOT_BINARY
