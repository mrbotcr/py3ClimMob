import unittest
from unittest.mock import patch

from climmob.tests.test_utils.common import ViewBaseTest
from climmob.views.project_metadata import (
ProjectMetadataFormView,
)

class TestProjectMetadataFormView(ViewBaseTest):
    view = ProjectMetadataFormView
    request_method = "POST"


    @patch("climmob.views.project_metadata.getMetadataForm", return_value=None)
    def test_project_metadata_form_view_no_metadata(self):

        self.view.project = "Test Project"
        self.view.metadataForm = None


