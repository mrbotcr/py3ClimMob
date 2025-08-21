from unittest.mock import MagicMock, patch, ANY, call

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.enumerator import *


class TestGetEnumeratorDetailsView(ViewBaseTest):
    view_class = GetEnumeratorDetailsView

    @patch("climmob.views.enumerator.p.PluginImplementations")
    @patch("climmob.views.enumerator.getEnumeratorData")
    def test_get_enumerator_details_view(
        self, mock_get_enumerator_data, mock_plugin_implementations
    ):
        self.view.request.matchdict = {"user": "test_owner", "enumid": 1}
        mock_enum = MagicMock(name="mock enumerator")
        mock_get_enumerator_data.return_value = mock_enum
        mock_plugin = MagicMock()
        mock_plugin.before_returning_context.return_value = MagicMock(
            name="mock plugin"
        )
        mock_plugin_implementations.return_value = [mock_plugin]

        result = self.view.get()
        self.assertEqual(result, mock_plugin.before_returning_context.return_value)
        mock_get_enumerator_data.assert_called_once_with(
            self.view.request.matchdict["user"],
            self.view.request.matchdict["enumid"],
            self.view.request,
        )
        mock_plugin.before_returning_context.assert_called_once_with(
            self.view.request, mock_enum
        )
