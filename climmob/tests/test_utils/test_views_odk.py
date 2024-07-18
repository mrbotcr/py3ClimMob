import unittest
from unittest.mock import MagicMock, patch

from pyramid.response import Response

from climmob.views.odk import (
    FormlistView,
    FormListByProjectView,
    SubmissionView,
    SubmissionByProjectView,
    XMLFormView,
    PushView,
    AssessmentXMLFormView,
    ManifestView,
    AssessmentManifestView,
    MediaFileView,
    AssessmentMediaFileView,
)


class TestFormListView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"userid": "test_user"}
        self.view = FormlistView(self.mock_request)
        self.view.user = "test_enumerator"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_isEnumeratorActive,
        mock_getEnumeratorPassword,
        mock_authorize,
        expected_authorize_call=True,
    ):
        mock_isEnumeratorActive.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        mock_getEnumeratorPassword.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        if expected_authorize_call:
            mock_authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(FormlistView, "authorize", return_value=True)
    @patch("climmob.views.odk.getFormList", return_value="<formlist></formlist>")
    @patch.object(FormlistView, "createXMLResponse")
    def test_process_view_authorized_enumerator(
        self,
        mock_createXMLResponse,
        mock_getFormList,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        mock_createXMLResponse.return_value = Response("<formlist></formlist>")

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_getFormList.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        mock_createXMLResponse.assert_called_once_with("<formlist></formlist>")

        self.assertEqual(response, mock_createXMLResponse.return_value)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(FormlistView, "authorize", return_value=False)
    @patch.object(FormlistView, "askForCredentials")
    def test_process_view_unauthorized_enumerator(
        self,
        mock_askForCredentials,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        mock_askForCredentials.return_value = Response(status=401)

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response, mock_askForCredentials.return_value)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    @patch.object(FormlistView, "askForCredentials")
    def test_process_view_inactive_enumerator(
        self, mock_askForCredentials, mock_isEnumeratorActive
    ):
        mock_askForCredentials.return_value = Response(status=401)

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response, mock_askForCredentials.return_value)


class TestFormListByProjectView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "userOwner",
            "project": "projectCod",
            "collaborator": "userCollaborator",
        }
        self.view = FormListByProjectView(self.mock_request)
        self.view.user = "test_enumerator"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_isEnumeratorActive,
        mock_getEnumeratorPassword,
        mock_authorize,
        expected_authorize_call=True,
    ):
        mock_isEnumeratorActive.assert_called_once_with(
            "userCollaborator", "test_enumerator", self.mock_request
        )
        mock_getEnumeratorPassword.assert_called_once_with(
            "userCollaborator", "test_enumerator", self.mock_request
        )
        if expected_authorize_call:
            mock_authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(FormListByProjectView, "authorize", return_value=True)
    @patch("climmob.views.odk.getFormList", return_value="<formlist></formlist>")
    @patch.object(FormListByProjectView, "createXMLResponse")
    def test_process_view_authorized_enumerator(
        self,
        mock_createXMLResponse,
        mock_getFormList,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        mock_createXMLResponse.return_value = Response("<formlist></formlist>")

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_getFormList.assert_called_once_with(
            "userCollaborator",
            "test_enumerator",
            self.mock_request,
            userOwner="userOwner",
            projectCod="projectCod",
        )
        mock_createXMLResponse.assert_called_once_with("<formlist></formlist>")

        self.assertEqual(response, mock_createXMLResponse.return_value)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(FormListByProjectView, "authorize", return_value=False)
    @patch.object(FormListByProjectView, "askForCredentials")
    def test_process_view_unauthorized_enumerator(
        self,
        mock_askForCredentials,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        mock_askForCredentials.return_value = Response(status=401)

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response, mock_askForCredentials.return_value)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    @patch.object(FormListByProjectView, "askForCredentials")
    def test_process_view_inactive_enumerator(
        self, mock_askForCredentials, mock_isEnumeratorActive
    ):
        mock_askForCredentials.return_value = Response(status=401)

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "userCollaborator", "test_enumerator", self.mock_request
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response, mock_askForCredentials.return_value)


class TestPushView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.method = "POST"
        self.mock_request.matchdict = {"userid": "test_user"}
        self.view = PushView(self.mock_request)
        self.view.user = "test_enumerator"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_isEnumeratorActive,
        mock_getEnumeratorPassword,
        mock_authorize,
        expected_authorize_call=True,
    ):
        mock_isEnumeratorActive.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        mock_getEnumeratorPassword.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        if expected_authorize_call:
            mock_authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(PushView, "authorize", return_value=True)
    @patch("climmob.views.odk.storeSubmission", return_value=(True, ""))
    def test_process_view_post_successful_submission(
        self,
        mock_storeSubmission,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_storeSubmission.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 201)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(PushView, "authorize", return_value=True)
    @patch("climmob.views.odk.storeSubmission", return_value=(False, 500))
    def test_process_view_post_failed_submission(
        self,
        mock_storeSubmission,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_storeSubmission.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 500)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(PushView, "authorize", return_value=False)
    @patch.object(PushView, "askForCredentials")
    def test_process_view_post_unauthorized(
        self,
        mock_askForCredentials,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        mock_askForCredentials.return_value = Response(status=401)

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    def test_process_view_post_inactive_enumerator(self, mock_isEnumeratorActive):
        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 401)

    def test_process_view_get_request(self):
        self.mock_request.method = "GET"
        response = self.view.processView()

        self.assertEqual(response.status_code, 404)


class TestSubmissionView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {"userid": "test_user"}
        self.view = SubmissionView(self.mock_request)
        self.view.user = "test_enumerator"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_isEnumeratorActive,
        mock_getEnumeratorPassword=None,
        mock_authorize=None,
        expected_authorize_call=True,
    ):
        mock_isEnumeratorActive.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )
        if mock_getEnumeratorPassword:
            mock_getEnumeratorPassword.assert_called_once_with(
                "test_user", "test_enumerator", self.mock_request
            )
        if mock_authorize and expected_authorize_call:
            mock_authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    def test_process_view_head_request_active_enumerator(self, mock_isEnumeratorActive):
        self.mock_request.method = "HEAD"
        self.mock_request.route_url.return_value = "/odkpush/test_user"

        response = self.view.processView()

        self.common_assertions(mock_isEnumeratorActive)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["Location"], "/odkpush/test_user")

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    @patch.object(
        SubmissionView, "askForCredentials", return_value=Response(status=401)
    )
    def test_process_view_head_request_inactive_enumerator(
        self, mock_askForCredentials, mock_isEnumeratorActive
    ):
        self.mock_request.method = "HEAD"

        response = self.view.processView()

        self.common_assertions(mock_isEnumeratorActive, expected_authorize_call=False)
        mock_askForCredentials.assert_called_once()
        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(SubmissionView, "authorize", return_value=True)
    @patch("climmob.views.odk.storeSubmission", return_value=(True, ""))
    def test_process_view_post_successful_submission(
        self,
        mock_storeSubmission,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_storeSubmission.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 201)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(SubmissionView, "authorize", return_value=True)
    @patch("climmob.views.odk.storeSubmission", return_value=(False, 500))
    def test_process_view_post_failed_submission(
        self,
        mock_storeSubmission,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_storeSubmission.assert_called_once_with(
            "test_user", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 500)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(SubmissionView, "authorize", return_value=False)
    @patch.object(
        SubmissionView, "askForCredentials", return_value=Response(status=401)
    )
    def test_process_view_post_unauthorized(
        self,
        mock_askForCredentials,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        self.common_assertions(
            mock_isEnumeratorActive, mock_getEnumeratorPassword, mock_authorize
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    def test_process_view_post_inactive_enumerator(self, mock_isEnumeratorActive):
        self.mock_request.method = "POST"

        response = self.view.processView()

        self.common_assertions(mock_isEnumeratorActive, expected_authorize_call=False)
        self.assertEqual(response.status_code, 401)

    def test_process_view_invalid_method(self):
        self.mock_request.method = "GET"

        response = self.view.processView()

        self.assertEqual(response.status_code, 404)


class TestSubmissionByProjectView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "project": "test_project",
            "collaborator": "test_collaborator",
        }
        self.view = SubmissionByProjectView(self.mock_request)
        self.view.user = "test_enumerator"

    def tearDown(self):
        patch.stopall()

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorAssigned", return_value=False)
    def test_process_view_head_request_active_enumerator(
        self,
        mock_isEnumeratorAssigned,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "HEAD"
        self.mock_request.route_url.return_value = "/odkpush/test_collaborator"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.mock_request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "test_collaborator", "project_id", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.headers["Location"], "/odkpush/test_collaborator")

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    @patch.object(
        SubmissionByProjectView, "askForCredentials", return_value=Response(status=401)
    )
    def test_process_view_head_request_inactive_enumerator(
        self, mock_askForCredentials, mock_isEnumeratorActive
    ):
        self.mock_request.method = "HEAD"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_askForCredentials.assert_called_once()
        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorAssigned", return_value=False)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(SubmissionByProjectView, "authorize", return_value=True)
    @patch("climmob.views.odk.storeSubmission", return_value=(True, ""))
    def test_process_view_post_successful_submission(
        self,
        mock_storeSubmission,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorAssigned,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.mock_request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "test_collaborator", "project_id", "test_enumerator", self.mock_request
        )
        mock_getEnumeratorPassword.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_authorize.assert_called_once_with("password")
        mock_storeSubmission.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 201)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorAssigned", return_value=False)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(SubmissionByProjectView, "authorize", return_value=True)
    @patch("climmob.views.odk.storeSubmission", return_value=(False, 500))
    def test_process_view_post_failed_submission(
        self,
        mock_storeSubmission,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorAssigned,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.mock_request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "test_collaborator", "project_id", "test_enumerator", self.mock_request
        )
        mock_getEnumeratorPassword.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_authorize.assert_called_once_with("password")
        mock_storeSubmission.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 500)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorAssigned", return_value=True)
    @patch.object(
        SubmissionByProjectView, "askForCredentials", return_value=Response(status=401)
    )
    def test_process_view_head_enumerator_assigned(
        self,
        mock_askForCredentials,
        mock_isEnumeratorAssigned,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "HEAD"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.mock_request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "test_collaborator", "project_id", "test_enumerator", self.mock_request
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorAssigned", return_value=True)
    @patch.object(
        SubmissionByProjectView, "askForCredentials", return_value=Response(status=401)
    )
    def test_process_view_post_enumerator_assigned(
        self,
        mock_askForCredentials,
        mock_isEnumeratorAssigned,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.mock_request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "test_collaborator", "project_id", "test_enumerator", self.mock_request
        )
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorAssigned", return_value=False)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch.object(SubmissionByProjectView, "authorize", return_value=False)
    @patch.object(
        SubmissionByProjectView, "askForCredentials", return_value=Response(status=401)
    )
    def test_process_view_post_unauthorized(
        self,
        mock_askForCredentials,
        mock_authorize,
        mock_getEnumeratorPassword,
        mock_isEnumeratorAssigned,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorActive,
    ):
        self.mock_request.method = "POST"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_user", "test_project", self.mock_request
        )
        mock_isEnumeratorAssigned.assert_called_once_with(
            "test_collaborator", "project_id", "test_enumerator", self.mock_request
        )
        mock_getEnumeratorPassword.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )
        mock_authorize.assert_called_once_with("password")
        mock_askForCredentials.assert_called_once()

        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorActive", return_value=False)
    def test_process_view_post_inactive_enumerator(self, mock_isEnumeratorActive):
        self.mock_request.method = "POST"

        response = self.view.processView()

        mock_isEnumeratorActive.assert_called_once_with(
            "test_collaborator", "test_enumerator", self.mock_request
        )

        self.assertEqual(response.status_code, 401)

    def test_process_view_invalid_method(self):
        self.mock_request.method = "PUT"

        response = self.view.processView()

        self.assertEqual(response.status_code, 404)


class TestXMLFormView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "userowner": "test_owner",
            "project": "test_project",
        }
        self.view = XMLFormView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user_login"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword=None,
        authorize_called=True,
    ):
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "test_owner", "test_project", self.mock_request
        )
        mock_isEnumeratorinProject.assert_called_once_with(
            "project_id", self.view.user, self.mock_request
        )
        if mock_getEnumeratorPassword:
            mock_getEnumeratorPassword.assert_called_once_with(
                "test_user", self.view.user, self.mock_request
            )
        if authorize_called:
            self.view.authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.getXMLForm", return_value="xml_form")
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_authorized_enumerator(
        self,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword,
        mock_getXMLForm,
    ):
        self.view.authorize = MagicMock(return_value=True)

        response = self.view.processView()

        self.assertEqual(response, "xml_form")
        self.common_assertions(
            mock_getTheProjectIdForOwner,
            mock_isEnumeratorinProject,
            mock_getEnumeratorPassword,
        )
        mock_getXMLForm.assert_called_once_with(
            "test_owner", "project_id", "test_project", self.mock_request
        )

    @patch("climmob.views.odk.isEnumeratorinProject", return_value=False)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_unauthorized_enumerator(
        self, mock_getTheProjectIdForOwner, mock_isEnumeratorinProject
    ):
        self.view.authorize = MagicMock(return_value=True)

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.common_assertions(
            mock_getTheProjectIdForOwner,
            mock_isEnumeratorinProject,
            authorize_called=False,
        )

    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_invalid_credentials(
        self,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword,
    ):
        self.view.authorize = MagicMock(return_value=False)

        response = self.view.processView()

        self.assertEqual(response.status_code, 401)
        self.common_assertions(
            mock_getTheProjectIdForOwner,
            mock_isEnumeratorinProject,
            mock_getEnumeratorPassword,
        )


class TestAssessmentXMLFormView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "userowner": "owner_user",
            "project": "test_project",
            "assessmentid": "test_assessment",
        }
        self.view = AssessmentXMLFormView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def common_assertions(
        self,
        mock_getTheProjectIdForOwner,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword=None,
        authorize_called=True,
    ):
        mock_getTheProjectIdForOwner.assert_called_once_with(
            "owner_user", "test_project", self.mock_request
        )
        mock_isEnumeratorinProject.assert_called_once_with(
            "project_id", self.view.user, self.mock_request
        )
        if mock_getEnumeratorPassword:
            mock_getEnumeratorPassword.assert_called_once_with(
                "test_user", self.view.user, self.mock_request
            )
        if authorize_called:
            self.view.authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch(
        "climmob.views.odk.getAssessmentXMLForm",
        return_value=Response(body="<xml></xml>"),
    )
    def test_process_view_authorized(
        self,
        mock_getAssessmentXMLForm,
        mock_getEnumeratorPassword,
        mock_isEnumeratorinProject,
        mock_getTheProjectIdForOwner,
    ):
        self.view.authorize = MagicMock(return_value=True)
        response = self.view.processView()

        self.common_assertions(
            mock_getTheProjectIdForOwner,
            mock_isEnumeratorinProject,
            mock_getEnumeratorPassword,
        )
        mock_getAssessmentXMLForm.assert_called_once_with(
            "owner_user",
            "project_id",
            "test_project",
            "test_assessment",
            self.mock_request,
        )
        self.assertEqual(response.body, b"<xml></xml>")

    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=False)
    def test_process_view_not_in_project(
        self, mock_isEnumeratorinProject, mock_getTheProjectIdForOwner
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_getTheProjectIdForOwner,
            mock_isEnumeratorinProject,
            authorize_called=False,
        )
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    def test_process_view_unauthorized(
        self,
        mock_getEnumeratorPassword,
        mock_isEnumeratorinProject,
        mock_getTheProjectIdForOwner,
    ):
        self.view.authorize = MagicMock(return_value=False)
        response = self.view.processView()

        self.common_assertions(
            mock_getTheProjectIdForOwner,
            mock_isEnumeratorinProject,
            mock_getEnumeratorPassword,
        )
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, 401)


class TestManifestView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "userowner": "owner_user",
            "project": "project_code",
        }
        self.view = ManifestView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "enumerator_user"

    def common_assertions(
        self,
        mock_getProjectId,
        mock_isEnumerator,
        mock_getPassword=None,
        authorize_called=True,
    ):
        mock_getProjectId.assert_called_once_with(
            "owner_user", "project_code", self.mock_request
        )
        mock_isEnumerator.assert_called_once_with(
            "project_id", self.view.user, self.mock_request
        )
        if mock_getPassword:
            mock_getPassword.assert_called_once_with(
                "test_user", self.view.user, self.mock_request
            )
        if authorize_called:
            self.view.authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.getManifest", return_value="<manifest>data</manifest>")
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_authorized_enumerator(
        self, mock_getProjectId, mock_isEnumerator, mock_getPassword, mock_getManifest
    ):
        self.view.authorize = MagicMock(return_value=True)
        self.view.createXMLResponse = MagicMock(
            return_value=Response("<manifest>data</manifest>", content_type="text/xml")
        )

        response = self.view.processView()

        self.common_assertions(mock_getProjectId, mock_isEnumerator, mock_getPassword)
        mock_getManifest.assert_called_once_with(
            "test_user", "owner_user", "project_id", "project_code", self.mock_request
        )
        self.view.createXMLResponse.assert_called_once_with("<manifest>data</manifest>")
        self.assertEqual(response.status_code, 200)

    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_unauthorized_enumerator(
        self, mock_getProjectId, mock_isEnumerator, mock_getPassword
    ):
        self.view.authorize = MagicMock(return_value=False)

        response = self.view.processView()

        self.common_assertions(mock_getProjectId, mock_isEnumerator, mock_getPassword)
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)

    @patch("climmob.views.odk.isEnumeratorinProject", return_value=False)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_enumerator_not_in_project(
        self, mock_getProjectId, mock_isEnumerator
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumerator, authorize_called=False
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)


class TestAssessmentManifestView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "userowner": "owner_user",
            "project": "project_code",
            "assessmentid": "assessment_id",
        }
        self.view = AssessmentManifestView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "enumerator_user"

    def common_assertions(
        self,
        mock_getProjectId,
        mock_isEnumerator,
        mock_getPassword=None,
        authorize_called=True,
    ):
        mock_getProjectId.assert_called_once_with(
            "owner_user", "project_code", self.mock_request
        )
        mock_isEnumerator.assert_called_once_with(
            "project_id", self.view.user, self.mock_request
        )
        if mock_getPassword:
            mock_getPassword.assert_called_once_with(
                "test_user", self.view.user, self.mock_request
            )
        if authorize_called:
            self.view.authorize.assert_called_once_with("password")

    @patch(
        "climmob.views.odk.getAssessmentManifest",
        return_value="<manifest>data</manifest>",
    )
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_authorized_enumerator(
        self, mock_getProjectId, mock_isEnumerator, mock_getPassword, mock_getManifest
    ):
        self.view.authorize = MagicMock(return_value=True)
        self.view.createXMLResponse = MagicMock(
            return_value=Response("<manifest>data</manifest>", content_type="text/xml")
        )

        response = self.view.processView()

        self.common_assertions(mock_getProjectId, mock_isEnumerator, mock_getPassword)
        mock_getManifest.assert_called_once_with(
            "test_user",
            "owner_user",
            "project_id",
            "project_code",
            "assessment_id",
            self.mock_request,
        )
        self.view.createXMLResponse.assert_called_once_with("<manifest>data</manifest>")
        self.assertEqual(response.status_code, 200)

    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_unauthorized_enumerator(
        self, mock_getProjectId, mock_isEnumerator, mock_getPassword
    ):
        self.view.authorize = MagicMock(return_value=False)

        response = self.view.processView()

        self.common_assertions(mock_getProjectId, mock_isEnumerator, mock_getPassword)
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)

    @patch("climmob.views.odk.isEnumeratorinProject", return_value=False)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_enumerator_not_in_project(
        self, mock_getProjectId, mock_isEnumerator
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumerator, authorize_called=False
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("WWW-Authenticate", response.headers)


class TestMediaFileView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "userowner": "owner_user",
            "project": "test_project",
            "fileid": "file123",
        }
        self.view = MediaFileView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_getProjectId,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword=None,
        authorize_called=True,
    ):
        mock_getProjectId.assert_called_once_with(
            "owner_user", "test_project", self.mock_request
        )
        mock_isEnumeratorinProject.assert_called_once_with(
            "project_id", self.view.user, self.mock_request
        )
        if mock_getEnumeratorPassword:
            mock_getEnumeratorPassword.assert_called_once_with(
                "test_user", self.view.user, self.mock_request
            )
        if authorize_called:
            self.view.authorize.assert_called_once_with("password")

    @patch("climmob.views.odk.getMediaFile", return_value=Response(status=200))
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_authorized(
        self,
        mock_getProjectId,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword,
        mock_getMediaFile,
    ):
        self.view.authorize = MagicMock(return_value=True)

        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumeratorinProject, mock_getEnumeratorPassword
        )
        mock_getMediaFile.assert_called_once_with(
            "owner_user", "project_id", "test_project", "file123", self.mock_request
        )

        self.assertEqual(response.status_code, 200)

    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_unauthorized(
        self, mock_getProjectId, mock_isEnumeratorinProject, mock_getEnumeratorPassword
    ):
        self.view.authorize = MagicMock(return_value=False)

        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumeratorinProject, mock_getEnumeratorPassword
        )
        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorinProject", return_value=False)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_not_in_project(
        self, mock_getProjectId, mock_isEnumeratorinProject
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumeratorinProject, authorize_called=False
        )
        self.assertEqual(response.status_code, 401)


class TestAssessmentMediaFileView(unittest.TestCase):
    def setUp(self):
        self.mock_request = MagicMock()
        self.mock_request.matchdict = {
            "user": "test_user",
            "userowner": "owner_user",
            "project": "test_project",
            "fileid": "file123",
            "assessmentid": "assessment456",
        }
        self.view = AssessmentMediaFileView(self.mock_request)
        self.view.user = MagicMock()
        self.view.user.login = "test_user"

    def tearDown(self):
        patch.stopall()

    def common_assertions(
        self,
        mock_getProjectId,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword=None,
        authorize_called=True,
    ):
        mock_getProjectId.assert_called_once_with(
            "owner_user", "test_project", self.mock_request
        )
        mock_isEnumeratorinProject.assert_called_once_with(
            "project_id", self.view.user, self.mock_request
        )
        if mock_getEnumeratorPassword:
            mock_getEnumeratorPassword.assert_called_once_with(
                "test_user", self.view.user, self.mock_request
            )
        if authorize_called:
            self.view.authorize.assert_called_once_with("password")

    @patch(
        "climmob.views.odk.getAssessmentMediaFile", return_value=Response(status=200)
    )
    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_authorized(
        self,
        mock_getProjectId,
        mock_isEnumeratorinProject,
        mock_getEnumeratorPassword,
        mock_getAssessmentMediaFile,
    ):
        self.view.authorize = MagicMock(return_value=True)

        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumeratorinProject, mock_getEnumeratorPassword
        )
        mock_getAssessmentMediaFile.assert_called_once_with(
            "owner_user",
            "project_id",
            "test_project",
            "assessment456",
            "file123",
            self.mock_request,
        )

        self.assertEqual(response.status_code, 200)

    @patch("climmob.views.odk.getEnumeratorPassword", return_value="password")
    @patch("climmob.views.odk.isEnumeratorinProject", return_value=True)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_unauthorized(
        self, mock_getProjectId, mock_isEnumeratorinProject, mock_getEnumeratorPassword
    ):
        self.view.authorize = MagicMock(return_value=False)

        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumeratorinProject, mock_getEnumeratorPassword
        )
        self.assertEqual(response.status_code, 401)

    @patch("climmob.views.odk.isEnumeratorinProject", return_value=False)
    @patch("climmob.views.odk.getTheProjectIdForOwner", return_value="project_id")
    def test_process_view_not_in_project(
        self, mock_getProjectId, mock_isEnumeratorinProject
    ):
        response = self.view.processView()

        self.common_assertions(
            mock_getProjectId, mock_isEnumeratorinProject, authorize_called=False
        )
        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
