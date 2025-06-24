from unittest.mock import MagicMock, call

from climmob.tests.test_utils.common import BaseTest


class SessionMock:
    def __init__(self, return_value=MagicMock()):
        self.mock = MagicMock(name="SessionMock")
        self.mock.query.return_value = self.mock
        self.mock.filter.return_value = self.mock
        self.mock.join.return_value = self.mock
        self.mock.group_by.return_value = self.mock
        self.mock.order_by.return_value = self.mock
        self.mock.add.return_value = self.mock
        self.mock.first.return_value = return_value
        self.mock.one.return_value = return_value
        self.mock.all.return_value = return_value
        self.return_value = return_value

    def attach_to(self, request_mock):
        request_mock.dbsession = self.mock

    def get_mock(self):
        return self.mock

    def set_final_return_value(self, return_value):
        self.mock.first.return_value = return_value
        self.mock.one.return_value = return_value
        self.return_value = return_value

    def assert_call_sequence(self, *steps):
        expected_calls = [getattr(call, step[0])(*step[1:]) for step in steps]
        assert expected_calls == self.mock.mock_calls


class DBProcessBaseTest(BaseTest):
    def setUp(self):
        super().setUp()

        self.request = MagicMock()
        self.session = SessionMock()
        self.session.attach_to(self.request)
