from climmob.processes import getActiveProject, getJSONResult
from climmob.views.classes import privateView, publicView


class test_view(privateView):
    def processView(self):
        activeProjectData = getActiveProject(self.user.login, self.request)
        return getJSONResult(
            self.user.login, activeProjectData["project_cod"], self.request
        )


class sentry_debug_view(publicView):
    def processView(self):
        division_by_zero = 1 / 0

        return {}
