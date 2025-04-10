import unittest
from unittest.mock import MagicMock

from climmob.views.validators.BaseValidator import BaseValidator


class TestBaseValidator(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()

        self.validator = BaseValidator(self.request)

    def test_run(self):
        with self.assertRaises(NotImplementedError):
            self.validator.run()
