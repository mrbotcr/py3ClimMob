from datetime import datetime

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
    getCombinations,
    get_all_affiliations,
    languageByLanguageCode,
)
from climmob.views.validators.ProjectExistsValidator import ProjectExistsValidator
from climmob.views.classes import privateView
from jinja2 import Environment, FileSystemLoader
import json
import os

from climmob.views.validators.project import ProjectOpenValidator


class ProjectMetadataFormView(privateView):
    validators = (ProjectExistsValidator,
                  ProjectOpenValidator)

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
                    postData["pmf_last_update"] = datetime.now()

                    projectMetadataForm = getProjectMetadataForm(
                        self.request, activeProjectId, postData["metadata_id"]
                    )

                    if not projectMetadataForm:
                        postData["pmf_lang"] = self.request.locale_name
                        added, message = addProjectMetadataForm(postData, self.request)
                        # if not added:
                        #     error_summary = {"error": message}
                    else:
                        edited, message = modifyProjectMetadataForm(
                            self.request,
                            activeProjectId,
                            postData["metadata_id"],
                            postData,
                        )

                    if not message:

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
                    else:
                        self.request.session.flash(message)
        return {
            "activeProject": activeProject,
            "dataworking": dataworking,
            "metadataForm": metadataForm,
            "listOfProjectMetadata": listOfProjectMetadata,
        }


class ShowMetadataFormView(privateView):
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
                    lang_answer = self.request.locale_name
                    lang_answer_name = None

                    projectMetadataForm = getProjectMetadataForm(
                        self.request, activeProjectId, metadataId
                    )

                    if projectMetadataForm:
                        informationFilled = projectMetadataForm["pmf_json"]

                        if projectMetadataForm["pmf_lang"]:
                            lang_answer = projectMetadataForm["pmf_lang"]
                            lang_answer_name = languageByLanguageCode(
                                lang_answer, self.request
                            )["lang_name"]

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
                    template_form = env.get_template("template_form.jinja2")
                    template_table = env.get_template("template_table.jinja2")
                    inputs = env.get_template("metadata_inputs.jinja2")

                    dict_of_technologies_with_synonyms = {}
                    if metadataForm["metadata_for_technology_options"] == 1:

                        techs, ncombs, combs = getCombinations(
                            activeProjectId, self.request
                        )

                        for comb in combs:
                            dict_of_technologies_with_synonyms[
                                "{}_{}".format(comb["tech_id"], comb["alias_id"])
                            ] = []
                            dict_of_technologies_with_synonyms[
                                "{}_{}".format(comb["tech_id"], comb["alias_id"])
                            ].append({"option": comb["alias_name"]})

                        if not informationFilled:

                            informationFilled["data"] = {}
                            informationFilled["data"]["br_trial_varieties"] = []

                            for comb in combs:
                                informationFilled["data"]["br_trial_varieties"].append(
                                    {
                                        "climmob_technology_id": comb["tech_id"],
                                        "climmob_technology_option_id": comb[
                                            "alias_id"
                                        ],
                                        "climmob_genotype_name": comb["alias_name"],
                                    }
                                )

                    activeProjectData = getActiveProject(self.user.login, self.request)

                    dict = {
                        "activeProject": activeProjectData,
                        "Form": json.loads(metadataForm["metadata_json"]),
                        "postData": json.dumps(informationFilled),
                        "_": self._,
                        "request": self.request,
                        "technologies_with_synonyms": json.dumps(
                            dict_of_technologies_with_synonyms
                        ),
                        "template_form": template_form,
                        "template_table": template_table,
                        "inputs": inputs,
                        "form_to_use": metadataForm["metadata_for_technology_options"],
                        "list_of_affiliations": get_all_affiliations(self.request),
                        "lang_answer": lang_answer,
                        "lang_answer_name": lang_answer_name,
                    }
                    render_temp = template.render(dict)

                    return metadataForm["metadata_name"] + "@@@@@@@@@@" + render_temp

        return ""