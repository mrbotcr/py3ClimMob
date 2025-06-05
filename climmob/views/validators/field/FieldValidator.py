import json

from pyramid.exceptions import HTTPBadRequest

from .FieldValidation import FieldValidation
from .Field import Field
from climmob.views.validators.BaseValidator import BaseValidator


class FieldValidator(BaseValidator):
    def __init__(self, request):
        super().__init__(request)
        self.invalid_fields: dict = {}
        for validation in FieldValidation:
            if validation != FieldValidation.SUCCESS:
                self.invalid_fields[validation] = []

    def run(self):
        if self.view.valid_fields is None:
            return

        body = json.loads(self.view.body)

        for key in body:
            if key not in [v.key for v in self.view.valid_fields]:
                self.add_invalid_field(FieldValidation.UNALLOWED, key)

        if len(self.invalid_fields[FieldValidation.UNALLOWED]) == 0:
            first_error_found = None
            for valid_field in self.view.valid_fields:  # type: Field

                result = valid_field.validate(body, first_error_found)

                if result == FieldValidation.SUCCESS:
                    continue

                if first_error_found is None:
                    first_error_found = result

                self.add_invalid_field(result, valid_field.key)

        for validation in FieldValidation:
            if validation == FieldValidation.SUCCESS:
                continue

            if len(self.invalid_fields[validation]) > 0:
                msg = self._(validation.value)
                msg += ", ".join(self.invalid_fields[validation])
                raise HTTPBadRequest(msg)

    def add_invalid_field(self, status, key):
        self.invalid_fields[status].append(key)
