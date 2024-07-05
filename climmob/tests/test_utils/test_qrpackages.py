import unittest
from unittest.mock import MagicMock, patch

from climmob.products.qrpackages.qrpackages import create_qr_packages


class PackagesTestCase(unittest.TestCase):
    @patch("climmob.products.qrpackages.qrpackages.registerProductInstance")
    @patch("climmob.products.qrpackages.qrpackages.createQR.apply_async")
    @patch("climmob.products.qrpackages.qrpackages.createProductDirectory")
    def test_create_qr_packages(
        self,
        mock_createProductDirectory,
        mock_createQR_apply_async,
        mock_registerProductInstance,
    ):
        mock_request = MagicMock()
        _locale = "us"
        mock_user_owner = MagicMock()
        _project_id = "123asd"
        _project_code = "123abc"
        _options = None
        _packages = ["1", "2", "3"]
        mock_path = MagicMock()
        mock_createProductDirectory.return_value = mock_path
        mock_task = MagicMock()
        mock_createQR_apply_async.return_value = mock_task

        create_qr_packages(
            mock_request,
            _locale,
            mock_user_owner,
            _project_id,
            _project_code,
            _options,
            _packages,
        )

        mock_createProductDirectory.assert_called_with(
            mock_request, mock_user_owner, _project_code, "qrpackage"
        )

        mock_createQR_apply_async.assert_called_with(
            (_locale, mock_path, _project_code, _packages), queue="ClimMob"
        )

        mock_registerProductInstance.assert_called_with(
            _project_id,
            "qrpackage",
            "packages_" + _project_code + ".pdf",
            "application/pdf",
            "create_packages",
            mock_task.id,
            mock_request,
        )

        # self.assertTrue(mock_createQR_apply_async.called)
        # self.assertTrue(mock_createProductDirectory.called)
        # self.assertTrue(mock_registerProductInstance.called)
