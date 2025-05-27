import unittest
from unittest.mock import MagicMock, patch

from climmob.views.validators import Field, FieldValidation, BinaryField, IntegerField


class TestField(unittest.TestCase):
    def setUp(self):
        self.field = Field("test_key")
        self.body = {}

    def test_post_init(self):
        self.assertEqual(
            self.field._stages,
            [
                {
                    "validation": FieldValidation.MISSING,
                    "function": self.field.check_required,
                },
                {
                    "validation": FieldValidation.BLANK,
                    "function": self.field.check_not_blank,
                },
            ],
        )

    def test_validate_success(self):

        with patch.object(
            self.field, "check_required", return_value=FieldValidation.SUCCESS
        ) as mock_check_required, patch.object(
            self.field, "check_not_blank", return_value=FieldValidation.SUCCESS
        ) as mock_check_not_blank:

            self.field._stages = [
                {
                    "validation": FieldValidation.MISSING,
                    "function": self.field.check_required,
                },
                {
                    "validation": FieldValidation.BLANK,
                    "function": self.field.check_not_blank,
                },
            ]

            self.field.validate(self.body, MagicMock(FieldValidation))

            mock_check_required.assert_called_once_with(self.body)
            mock_check_not_blank.assert_called_once_with(self.body)

    def test_validate_validation_stopped(self):
        first_error = MagicMock(FieldValidation)

        mock_checker_1 = MagicMock()
        mock_checker_1.return_value = FieldValidation.SUCCESS
        mock_validation_1 = first_error

        mock_checker_2 = MagicMock()
        mock_checker_2.return_value = FieldValidation.SUCCESS
        mock_validation_2 = MagicMock(FieldValidation)

        self.field._stages = [
            {
                "validation": mock_validation_1,
                "function": mock_checker_1,
            },
            {
                "validation": mock_validation_2,
                "function": mock_checker_2,
            },
        ]

        self.field.validate(self.body, first_error)

        mock_checker_1.assert_called_once_with(self.body)
        mock_checker_2.assert_not_called()

    def test_check_required_true_invalid_returns_missing(self):
        self.field.required = True

        result = self.field.check_required(self.body)

        self.assertEqual(result, FieldValidation.MISSING)

    def test_check_required_true_valid_returns_success(self):
        self.field.required = True
        self.body[self.field.key] = "test_value"

        result = self.field.check_required(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_required_false_returns_success(self):
        self.field.required = False

        result = self.field.check_required(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_not_blank_true_invalid_returns_blank(self):
        self.field.not_blank = True
        self.body[self.field.key] = ""

        result = self.field.check_not_blank(self.body)

        self.assertEqual(result, FieldValidation.BLANK)

    def test_check_not_blank_true_valid_returns_success(self):
        self.field.not_blank = True
        self.body[self.field.key] = "test_value"

        result = self.field.check_not_blank(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_not_blank_false_returns_success(self):
        self.field.not_blank = False

        result = self.field.check_not_blank(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)


class TestBinaryField(unittest.TestCase):
    def setUp(self):
        self.field = BinaryField("test_key")
        self.body = {}

    def test_post_init(self):
        with patch.object(BinaryField, "_stages") as mock_stages, patch.object(
            Field, "__post_init__"
        ) as mock_field_post_init:
            binary_field = BinaryField()

            mock_field_post_init.assert_called_once()

            mock_stages.extend.assert_called_once_with(
                [
                    {
                        "validation": FieldValidation.NOT_BINARY,
                        "function": binary_field.check_binary,
                    }
                ]
            )

    def test_check_binary_invalid_returns_not_binary(self):
        self.body[self.field.key] = "test_value"

        result = self.field.check_binary(self.body)

        self.assertEqual(result, FieldValidation.NOT_BINARY)

    def test_check_binary_invalid_number_returns_not_binary(self):
        self.body[self.field.key] = "2"

        result = self.field.check_binary(self.body)

        self.assertEqual(result, FieldValidation.NOT_BINARY)

    def test_check_binary_valid_zero_str_returns_success(self):
        self.body[self.field.key] = "0"

        result = self.field.check_binary(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_binary_valid_zero_int_returns_success(self):
        self.body[self.field.key] = 0

        result = self.field.check_binary(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_binary_valid_one_str_returns_success(self):
        self.body[self.field.key] = "1"

        result = self.field.check_binary(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_binary_valid_one_int_returns_success(self):
        self.body[self.field.key] = 1

        result = self.field.check_binary(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)


class TestIntegerField(unittest.TestCase):
    def setUp(self):
        self.field = IntegerField("test_key")
        self.body = {}

    def test_post_init(self):
        with patch.object(IntegerField, "_stages") as mock_stages, patch.object(
            Field, "__post_init__"
        ) as mock_field_post_init:
            integer_field = IntegerField()

            mock_field_post_init.assert_called_once()

            mock_stages.extend.assert_called_once_with(
                [
                    {
                        "validation": FieldValidation.NOT_INTEGER,
                        "function": integer_field.check_integer,
                    }
                ]
            )

    def test_check_integer_invalid_str_returns_not_integer(self):
        self.body[self.field.key] = "test_value"

        result = self.field.check_integer(self.body)

        self.assertEqual(result, FieldValidation.NOT_INTEGER)

    def test_check_integer_valid_str_returns_success(self):
        self.body[self.field.key] = "256"

        result = self.field.check_integer(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)

    def test_check_integer_valid_int_returns_success(self):
        self.body[self.field.key] = 256

        result = self.field.check_integer(self.body)

        self.assertEqual(result, FieldValidation.SUCCESS)
