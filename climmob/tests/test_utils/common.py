import unittest
from unittest.mock import MagicMock, patch


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
