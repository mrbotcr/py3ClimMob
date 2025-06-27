import unittest
from unittest.mock import MagicMock, patch


class BaseTest(unittest.TestCase):
    patchers = {}
    mocks = {}

    def setUp(self):
        for key in self.mocks:
            self.mocks[key].reset_mock()
            self.mocks[key].return_value = self.patchers[key]["return_value"]

    @classmethod
    def setUpClass(cls):
        """
        super().setUpClass() must be called at the end of subclasses' setUpClass().
        """
        for key in cls.patchers:
            cls.mocks[key] = cls.patchers[key]["patch"].start()

    @classmethod
    def tearDownClass(cls):
        for key in cls.patchers:
            cls.patchers[key]["patch"].stop()

    def get_mock(self, name):
        return self.mocks[name]


class ViewBaseTest(BaseTest):
    view_class = None
    request_method = "GET"
    request_body = None

    def setUp(self):
        super().setUp()
        self.request = MagicMock()
        self.request.translate = self.mock_translation
        with patch("climmob.views.classes.ApiContext"), patch(
            "climmob.views.classes.PrivateContext"
        ):
            self.view = self.view_class(self.request)
        self.view.request.method = self.request_method
        self.view.user = MagicMock(login="test_user")
        if self.request_body:
            self.view.body = self.request_body
        self.view._ = self.mock_translation

    def mock_translation(self, message):
        return message
