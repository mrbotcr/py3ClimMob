from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.processes import (
    getActiveProject,
    projectExists,
    getTheProjectIdForOwner,
    getMetadataForProject,
    getMetadataForm,
    addProjectMetadataForm,
    getProjectMetadataForm,
    modifyProjectMetadataForm,
)
from climmob.views.classes import privateView
from jinja2 import Environment, FileSystemLoader
import json
import os


class ProjectMetadataForm_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        metadataForm = None

        if "metadataForm" in self.request.params.keys():
            metadataForm = self.request.params["metadataForm"]
            if not getMetadataForm(self.request, metadataForm):
                metadataForm = None

        error_summary = {}
        dataworking = {}

        activeProject = getActiveProject(self.user.login, self.request)

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:
            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            listOfProjectMetadata = getMetadataForProject(self.request, activeProjectId)

            if self.request.method == "POST":
                if "btn_save_metadata" in self.request.POST:

                    postData = self.getPostDict()
                    postData["project_id"] = activeProjectId
                    postData["pmf_json"] = json.loads(postData["_jsonResult"])

                    projectMetadataForm = getProjectMetadataForm(
                        self.request, activeProjectId, postData["metadata_id"]
                    )

                    if not projectMetadataForm:
                        added, message = addProjectMetadataForm(postData, self.request)
                        if not added:
                            error_summary = {"error": message}
                    else:
                        edited, message = modifyProjectMetadataForm(
                            self.request,
                            activeProjectId,
                            postData["metadata_id"],
                            postData,
                        )

                        if not edited:
                            error_summary = {"error": message}

                    if not error_summary:

                        self.request.session.flash(
                            self._("The project metadata was save successfully.")
                        )

                        self.returnRawViewResult = True
                        return HTTPFound(
                            location=self.request.route_url(
                                "Metadata",
                                user=activeProjectUser,
                                project=activeProjectCod,
                                _query={"metadataForm": postData["metadata_id"]},
                            )
                        )
        return {
            "activeProject": activeProject,
            "dataworking": dataworking,
            "metadataForm": metadataForm,
            "listOfProjectMetadata": listOfProjectMetadata,
        }


class ShowMetadataForm_view(privateView):
    def processView(self):
        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]
        metadataId = self.request.matchdict["metadataform"]

        self.returnRawViewResult = True

        if self.request.method == "GET":

            if not projectExists(
                self.user.login, activeProjectUser, activeProjectCod, self.request
            ):
                return ""
            else:
                activeProjectId = getTheProjectIdForOwner(
                    activeProjectUser, activeProjectCod, self.request
                )

                metadataForm = getMetadataForm(self.request, metadataId)
                if not metadataForm:
                    return ""
                else:
                    informationFilled = {}
                    projectMetadataForm = getProjectMetadataForm(
                        self.request, activeProjectId, metadataId
                    )

                    if projectMetadataForm:
                        informationFilled = projectMetadataForm["pmf_json"]

                    PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    env = Environment(
                        autoescape=False,
                        loader=FileSystemLoader(
                            os.path.join(
                                PATH, "templates", "snippets", "project", "metadata"
                            )
                        ),
                        trim_blocks=False,
                    )
                    template = env.get_template("metadataForm.jinja2")

                    dictionary = self.extract_names_and_types(
                        json.loads(metadataForm["metadata_json"])
                    )

                    dict = {
                        "Form": json.loads(metadataForm["metadata_json"]),
                        "postData": json.dumps(informationFilled),
                        "dictionary": json.dumps(dictionary),
                        "_": self._,
                        "request": self.request,
                    }
                    render_temp = template.render(dict)

                    return render_temp

        return ""

    def extract_names_and_types(self, data, result=None):
        if result is None:
            result = []

        if isinstance(data, dict):

            if "name" in data and "type" in data:
                if "climmob_users" in data:
                    if data["climmob_users"] == "yes":
                        result.append(
                            {
                                "name": data["name"],
                                "type": data["type"] + " climmob_users",
                            }
                        )
                else:
                    result.append({"name": data["name"], "type": data["type"]})

            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    self.extract_names_and_types(value, result)

        elif isinstance(data, list):
            for item in data:
                self.extract_names_and_types(item, result)

        return result
