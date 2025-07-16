import unittest
from unittest.mock import MagicMock

from climmob.utility import is_type_numerical, QuestionType


class TestIsTypeNumerical(unittest.TestCase):
    def test_with_str_decimal(self):
        q_type = str(QuestionType.DECIMAL.value)

        result = is_type_numerical(q_type)

        self.assertTrue(result)

    def test_with_str_integer(self):
        q_type = str(QuestionType.INTEGER.value)

        result = is_type_numerical(q_type)

        self.assertTrue(result)

    def test_with_int_decimal(self):
        q_type = QuestionType.DECIMAL.value

        result = is_type_numerical(q_type)

        self.assertTrue(result)

    def test_with_int_integer(self):
        q_type = QuestionType.INTEGER.value

        result = is_type_numerical(q_type)

        self.assertTrue(result)

    def test_false(self):
        q_type = MagicMock(int)

        result = is_type_numerical(q_type)

        self.assertFalse(result)
