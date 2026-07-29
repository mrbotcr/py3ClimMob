from unittest.mock import patch, MagicMock

from climmob.models.climmobv4 import ProjectPublicationStatus
from climmob.processes import (
    get_global_project_publication_status_id,
)
from climmob.tests.test_utils.test_processes import DBProcessBaseTest
from climmob.utility import (
    PublicationStatus as PublicationStatusEnum,
    PublicationApproved,
)


class TestProjectPublicationStatusDBProcess(DBProcessBaseTest):
    @classmethod
    def setUpClass(cls):
        cls.patchers["mapFromSchema"] = {
            "patch": patch(
                "climmob.processes.db.project_publication_status.mapFromSchema"
            ),
            "return_value": MagicMock(),
        }
        cls.patchers["get_project_publication_approved"] = {
            "patch": patch(
                "climmob.processes.db.project_publication_status.get_project_publication_approved"
            ),
            "return_value": PublicationApproved.DEFAULT.value,
        }

        super().setUpClass()


# The tester functions name follows a pattern:
#       test__<publication_approved>__<status>__returns__<expected_return_value>
class TestGetGlobalProjectPublicationStatusId(TestProjectPublicationStatusDBProcess):
    def setUp(self):
        super().setUp()
        self.process = get_global_project_publication_status_id

    def test__default__empty__returns__not_requested(self):
        self.session.set_final_return_value([])

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.NOT_REQUESTED.value)

    def test__rejected____returns__rejected(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.REJECTED.value

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.REJECTED.value)

    def test__rejected__climmob_failed__returns__failed(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.REJECTED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.FAILED.value,
                    destination="climmob",
                )
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.FAILED.value)

    def test__approved__not_empty__returns__approved(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.APPROVED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=MagicMock(int), destination=MagicMock(str)
                ),
                ProjectPublicationStatus(
                    publication_status_id=MagicMock(int), destination=MagicMock(str)
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.APPROVED.value)

    def test__approved__published__returns__published(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.APPROVED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=MagicMock(int), destination="climmob"
                ),
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.PUBLISHED.value,
                    destination=MagicMock(str),
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.PUBLISHED.value)

    def test__approved__just_climmob_published__returns__published(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.APPROVED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.PUBLISHED.value,
                    destination="climmob",
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.PUBLISHED.value)

    def test__approved__climmob_failed__returns__failed(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.APPROVED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.FAILED.value,
                    destination="climmob",
                ),
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.PUBLISHED.value,
                    destination=MagicMock(str),
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.FAILED.value)

    def test__approved__failed__returns__failed(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.APPROVED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.PUBLISHED.value,
                    destination="climmob",
                ),
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.FAILED.value,
                    destination=MagicMock(str),
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.FAILED.value)

    def test__approved__failed_and_published__returns__partial(self):
        self.get_mock(
            "get_project_publication_approved"
        ).return_value = PublicationApproved.APPROVED.value
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.PUBLISHED.value,
                    destination="climmob",
                ),
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.FAILED.value,
                    destination=MagicMock(str),
                ),
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.PUBLISHED.value,
                    destination=MagicMock(str),
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.PARTIAL.value)

    def test__not_approved__not_empty__returns__requested(self):
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=MagicMock(int), destination=MagicMock(str)
                ),
                ProjectPublicationStatus(
                    publication_status_id=MagicMock(int), destination=MagicMock(str)
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.REQUESTED.value)

    def test__not_approved__climmob_failed__returns__failed(self):
        self.session.set_final_return_value(
            [
                ProjectPublicationStatus(
                    publication_status_id=PublicationStatusEnum.FAILED.value,
                    destination="climmob",
                ),
                ProjectPublicationStatus(
                    publication_status_id=MagicMock(int), destination=MagicMock(str)
                ),
            ]
        )

        result = self.process(self.request, MagicMock(str, name="project_id"))

        self.assertEqual(result, PublicationStatusEnum.FAILED.value)
