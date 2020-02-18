from .classes import privateView
from ..processes import getJSONResult
from climmob.processes import getActiveProject

class test_view(privateView):
    def processView(self):
        #generateRegistry(self.user.login,'prj001',self.request)
        activeProjectData = getActiveProject(self.user.login, self.request)
        return getJSONResult(self.user.login,activeProjectData["project_cod"],self.request)