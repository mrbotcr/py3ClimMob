from climmob.processes import getJSONResult, getProjectData
from climmob.views.classes import apiView


class ResultsView(apiView):
    def get(self):
        active_project_data = getProjectData(
            self.context.active_project_id, self.request
        )
        anonymize = str(self.request.params.get("anonymize")).lower() == "true"
        return getJSONResult(
            self.user.login,
            self.context.active_project_id,
            active_project_data["project_cod"],
            self.request,
            anonymize=anonymize,
        )
