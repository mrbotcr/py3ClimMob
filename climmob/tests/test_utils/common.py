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


class ViewBaseTest(unittest.TestCase):
    view_class = None
    request_method = "GET"
    request_body = None

    def setUp(self):
        with patch("climmob.views.classes.ApiContext") as mock_context:
            self.view = self.view_class(MagicMock())
        self.context = mock_context.return_value
        self.view.request.method = self.request_method
        self.view.user = MagicMock(login="test_user")
        if self.request_body:
            self.view.body = self.request_body
        self.view._ = self.mock_translation

    def mock_translation(self, message):
        return message


class PrivateViewBaseTest(BaseTest):
    view_class = None

    def setUp(self):
        super().setUp()
        self.request = MagicMock()
        self.request.translate = lambda x: x
        with patch("climmob.views.classes.PrivateContext"):
            self.view = self.view_class(self.request)
