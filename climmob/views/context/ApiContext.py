import json
from functools import cached_property

from climmob.processes import getTheProjectIdForOwner
from climmob.utility.request import get_body_from_api_request
from climmob.views.context.BaseContext import BaseContext


class ApiContext(BaseContext):
    def __init__(self, request):
        super().__init__(request)

    @cached_property
    def __body(self):
        body = get_body_from_api_request(self.request)
        return json.loads(body)

    @cached_property
    def active_project_id(self):
        active_project_id = getTheProjectIdForOwner(
            self.__body["user_owner"],
            self.__body["project_cod"],
            self.request,
        )
        return active_project_id
