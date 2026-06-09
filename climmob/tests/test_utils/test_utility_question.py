import unittest
from unittest.mock import MagicMock

from climmob.utility import is_type_numerical, QuestionType, get_question_by_field_name


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


class TestGetQuestionByFieldName(unittest.TestCase):
    def setUp(self):
        self.question_codes = ["qst_a_test", "qst_b_test"]
        self.questions = [
            MagicMock(question_code=self.question_codes[0]),
            MagicMock(question_code=self.question_codes[1]),
        ]

    def test_simple(self):
        field_name = self.question_codes[1]
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_a(self):
        field_name = self.question_codes[1] + "_a"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_b(self):
        field_name = self.question_codes[1] + "_b"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_c(self):
        field_name = self.question_codes[1] + "_c"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_a_oth(self):
        field_name = self.question_codes[1] + "_a_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_b_oth(self):
        field_name = self.question_codes[1] + "_b_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_c_oth(self):
        field_name = self.question_codes[1] + "_c_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_oth(self):
        field_name = self.question_codes[1] + "_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_perf_1(self):
        field_name = "perf_" + self.question_codes[1] + "_1"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_perf_2(self):
        field_name = "perf_" + self.question_codes[1] + "_2"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_perf_3(self):
        field_name = "perf_" + self.question_codes[1] + "_3"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_char_pos(self):
        field_name = "char_" + self.question_codes[1] + "_pos"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_with_char_neg(self):
        field_name = "char_" + self.question_codes[1] + "_neg"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, self.questions[1])

    def test_unknown_suffix(self):
        field_name = self.question_codes[1] + "_unknown_suffix"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_prefix(self):
        field_name = "unknown_prefix_" + self.question_codes[1]
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_prefix_and_suffix(self):
        field_name = "unknown_prefix_" + self.question_codes[1] + "_unknown_suffix"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_simple(self):
        field_name = "unknown_question_code"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_a(self):
        field_name = "unknown_question_code" + "_a"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_b(self):
        field_name = "unknown_question_code" + "_b"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_c(self):
        field_name = "unknown_question_code" + "_c"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_a_oth(self):
        field_name = "unknown_question_code" + "_a_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_b_oth(self):
        field_name = "unknown_question_code" + "_b_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_c_oth(self):
        field_name = "unknown_question_code" + "_c_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_oth(self):
        field_name = "unknown_question_code" + "_oth"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_perf_1(self):
        field_name = "perf_" + "unknown_question_code" + "_1"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_perf_2(self):
        field_name = "perf_" + "unknown_question_code" + "_2"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_perf_3(self):
        field_name = "perf_" + "unknown_question_code" + "_3"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_char_pos(self):
        field_name = "char_" + "unknown_question_code" + "_pos"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)

    def test_unknown_question_with_char_neg(self):
        field_name = "char_" + "unknown_question_code" + "_neg"
        result = get_question_by_field_name(field_name, self.questions)

        self.assertEqual(result, None)
