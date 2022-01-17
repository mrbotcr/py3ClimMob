from climmob.views.classes import publicView
import os
import json


class showMapForProjectVisualization_view(publicView):
    def processView(self):
        projects = {}
        mapLocation = os.path.join(
            self.request.registry.settings["user.repository"], "_map"
        )
        if os.path.exists(mapLocation + "/dataForProjectVisualization.json"):
            with open(mapLocation + "/dataForProjectVisualization.json") as json_data:
                projects = json.load(json_data)

        return {"projects": projects}
