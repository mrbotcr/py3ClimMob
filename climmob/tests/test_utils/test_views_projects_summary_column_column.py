from climmob.tests.test_utils.common import BaseTest
from climmob.views.projectsSummary.column.Column import *


class TestProjectSummaryColumnColumn(BaseTest):
    view_class = Column

    def setUp(self):
        super().setUp()

        self.valid_data = {
            "id": 1,
            "key": "valid_key",
            "name": "Valid Name",
            "type": "dropdown",
            "show": True,
            "options": {"Yes": 1, "No": 0},
            "existing_keys": ["valid_key"],
        }
        self.valid_column = Column(
            id=1,
            key="valid_key",
            name="Valid Name",
            type="static",
            show=True,
            options={},
            existing_keys=[],
        )
        self.list_error = [
            ColumnValidation.REQUIRE_INT,
            ColumnValidation.BLANK_KEY,
            ColumnValidation.LONG_KEY,
            ColumnValidation.BLANK_NAME,
            ColumnValidation.LONG_NAME,
            ColumnValidation.REQUIRE_BOOL,
            ColumnValidation.INVALID_TYPE,
            ColumnValidation.UNIQUE_KEY,
            ColumnValidation.OPTION_NOT_DICT,
            ColumnValidation.EMPTY_OPTION_DICT,
            ColumnValidation.INVALID_OPTION_ITEM,
        ]

    def test_column__post_init__success(self):
        instance = Column(**self.valid_data)
        result = instance.validate()
        self.assertEqual(result, None)
        self.assertEqual(len(instance._stages), 11)
        for i, validate in enumerate(self.list_error):
            self.assertEqual(instance._stages[i]["validation"], validate)

    def test_check_int_with_valid_id(self):
        self.valid_column.id = 123
        result = self.valid_column.check_int()
        self.assertEqual(result, ColumnValidation.SUCCESS)

    def test_check_int_with_string_id(self):
        self.valid_column.id = "This_is_not_integer"
        result = self.valid_column.check_int()
        self.assertEqual(result, ColumnValidation.REQUIRE_INT)

    def test_check_int_with_none_id(self):
        self.valid_column.id = None
        result = self.valid_column.check_int()
        self.assertEqual(result, ColumnValidation.REQUIRE_INT)

    def test_check_required_key_with_valid_key(self):
        self.valid_column.key = "valid_key"
        result = self.valid_column.check_required_key()
        self.assertEqual(result, ColumnValidation.SUCCESS)

    def test_check_required_key_with_empty_key(self):
        test_cases = ["", "   ", None]
        for case in test_cases:
            with self.subTest(case=case):
                self.valid_column.key = case
                result = self.valid_column.check_required_key()
                self.assertEqual(result, ColumnValidation.BLANK_KEY)

    # --- Validador: check_key_length() ---
    def test_key_length_valid(self):
        self.valid_column.key = "a" * MAX_KEY_LENGTH
        self.assertEqual(self.valid_column.check_key_length(), ColumnValidation.SUCCESS)

    def test_key_length_invalid(self):
        self.valid_column.key = "a" * (MAX_KEY_LENGTH + 1)
        self.assertEqual(
            self.valid_column.check_key_length(), ColumnValidation.LONG_KEY
        )

    # --- Validador: check_required_name() ---
    def test_required_name_valid(self):
        self.valid_column.name = "Nombre válido"
        self.assertEqual(
            self.valid_column.check_required_name(), ColumnValidation.SUCCESS
        )

    def test_required_name_invalid(self):
        for empty_name in ["", "   ", None]:
            with self.subTest(empty_name=empty_name):
                self.valid_column.name = empty_name
                self.assertEqual(
                    self.valid_column.check_required_name(), ColumnValidation.BLANK_NAME
                )

    # --- Validador: check_name_length() ---
    def test_name_length_valid(self):
        self.valid_column.name = "a" * MAX_NAME_LENGTH
        self.assertEqual(
            self.valid_column.check_name_length(), ColumnValidation.SUCCESS
        )

    def test_name_length_invalid(self):
        self.valid_column.name = "a" * (MAX_NAME_LENGTH + 1)
        self.assertEqual(
            self.valid_column.check_name_length(), ColumnValidation.LONG_NAME
        )

    # --- Validador: check_show() ---
    def test_show_valid(self):
        for valid_bool in [True, False]:
            with self.subTest(valid_bool=valid_bool):
                self.valid_column.show = valid_bool
                self.assertEqual(
                    self.valid_column.check_show(), ColumnValidation.SUCCESS
                )

    def test_show_invalid(self):
        for invalid_bool in ["true", 1, None]:
            with self.subTest(invalid_bool=invalid_bool):
                self.valid_column.show = invalid_bool
                self.assertEqual(
                    self.valid_column.check_show(), ColumnValidation.REQUIRE_BOOL
                )

    # --- Validador: check_type() ---
    def test_type_valid(self):
        for valid_type in VALID_TYPES:
            with self.subTest(valid_type=valid_type):
                self.valid_column.type = valid_type
                self.assertEqual(
                    self.valid_column.check_type(), ColumnValidation.SUCCESS
                )

    def test_type_invalid(self):
        for invalid_type in ["", "   ", "invalid", None, 123, True]:
            with self.subTest(invalid_type=invalid_type):
                self.valid_column.type = invalid_type
                result = self.valid_column.check_type()
                self.assertEqual(result, ColumnValidation.INVALID_TYPE)

    # --- Validador: check_unique_key() ---
    def test_unique_key_valid(self):
        self.valid_column.existing_keys = ["other_key"]
        self.assertEqual(self.valid_column.check_unique_key(), ColumnValidation.SUCCESS)

    def test_unique_key_invalid(self):
        self.valid_column.existing_keys = [self.valid_column.key]
        self.valid_column.id = None
        self.assertEqual(
            self.valid_column.check_unique_key(), ColumnValidation.UNIQUE_KEY
        )

    # ====== check for Dropdown ======
    # --- Validador: check_options_type() ---
    def test_options_type_valid(self):
        self.valid_column.options = {"opt1": 1}
        self.assertEqual(
            self.valid_column.check_options_type(), ColumnValidation.SUCCESS
        )

    def test_options_type_invalid(self):
        for invalid in ["options", [], None, 123]:
            with self.subTest(invalid=invalid):
                self.valid_column.options = invalid
                self.assertEqual(
                    self.valid_column.check_options_type(),
                    ColumnValidation.OPTION_NOT_DICT,
                )

    # --- Validador: check_options_non_empty() ---
    def test_options_non_empty_valid(self):
        self.valid_column.options = {"opt1": 1}
        self.assertEqual(
            self.valid_column.check_options_non_empty(), ColumnValidation.SUCCESS
        )

    def test_options_non_empty_invalid(self):
        self.valid_column.options = {}
        self.assertEqual(
            self.valid_column.check_options_non_empty(),
            ColumnValidation.EMPTY_OPTION_DICT,
        )

    # --- Validador: check_options_items() ---
    def test_options_items_valid(self):
        self.valid_column.options = {"valid_opt": 1, "another_opt": 2}
        self.assertEqual(
            self.valid_column.check_options_items(), ColumnValidation.SUCCESS
        )

    def test_options_items_invalid_key(self):
        for invalid_key in ["", "   ", 123, None]:
            with self.subTest(invalid_key=invalid_key):
                self.valid_column.options = {invalid_key: 1}
                self.assertEqual(
                    self.valid_column.check_options_items(),
                    ColumnValidation.INVALID_OPTION_KEY,
                )

    def test_options_items_invalid_value(self):
        for invalid_value in ["1", None, "True"]:
            with self.subTest(invalid_value=invalid_value):
                self.valid_column.options = {"valid_key": invalid_value}
                self.assertEqual(
                    self.valid_column.check_options_items(),
                    ColumnValidation.INVALID_OPTION_VALUE,
                )

    def test_options_not_dict(self):
        for invalid_options in ["Hello", 123, None, []]:
            with self.subTest(invalid_options=invalid_options):
                self.valid_column.options = invalid_options
                self.assertEqual(
                    self.valid_column.check_options_items(),
                    ColumnValidation.OPTION_NOT_DICT,
                )
