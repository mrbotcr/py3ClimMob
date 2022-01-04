from climmob.views.classes import privateView
from pyramid.httpexceptions import HTTPNotFound, HTTPFound

from climmob.processes import (
    getPackages,
    projectHasCombinations,
    projectHasPackages,
    setRegistryStatus,
    generateRegistry,
    numberOfCombinationsForTheProject,
    searchTechnologiesInProject,
    getTheGroupOfThePackageCode,
    getTheProjectIdForOwner,
    getActiveProject,
    setCombinationQuantityAvailable,
    getProjectData,
    deleteProjectPackages,
    updateCreatePackages,
    getProjectProgress,
    createCombinations,
    getCombinations,
    setCombinationStatus,
    projectExists,
    getTech,
    getProjectEnumerators,
)
import climmob.plugins as p
from climmob.products.randomization.randomization import create_randomization
from climmob.products.qrpackages.qrpackages import create_qr_packages
from climmob.products.forms.form import create_document_form
from climmob.products.packages.packages import create_packages_excell
from climmob.products.colors.colors import create_colors_cards
from climmob.products.fieldagents.fieldagents import create_fieldagents_report
from climmob.views.registry import getDataFormPreview
import time


class projectCombinations_view(privateView):
    def processView(self):

        activeProjectUser = self.request.matchdict["user"]
        activeProjectCod = self.request.matchdict["project"]

        if not projectExists(
            self.user.login, activeProjectUser, activeProjectCod, self.request
        ):
            raise HTTPNotFound()
        else:

            activeProjectId = getTheProjectIdForOwner(
                activeProjectUser, activeProjectCod, self.request
            )

            prjData = getProjectData(activeProjectId, self.request)

            if prjData["project_regstatus"] != 0:
                raise HTTPNotFound()

            progress, pcompleted = getProjectProgress(
                activeProjectUser, activeProjectCod, activeProjectId, self.request
            )

            if (
                progress["enumerators"] != True
                or progress["technology"] != True
                or progress["techalias"] != True
                or progress["registry"] != True
            ):
                raise HTTPNotFound()

            if not "stage" in self.request.params.keys():
                stage = 1
            else:
                try:
                    stage = int(self.request.params["stage"])
                except:
                    stage = 1

            if stage < 1 or stage > 3:
                raise HTTPNotFound()

            if stage == 1:

                prjData = getProjectData(activeProjectId, self.request)
                # Only create the packages if its needed
                if prjData["project_createpkgs"] == 2:
                    self.returnRawViewResult = True

                    return HTTPFound(
                        location=self.request.route_url(
                            "combinations",
                            _query={"stage": 2},
                            project=activeProjectCod,
                            user=activeProjectUser,
                        )
                    )

                scrollPos = 0
                if self.request.method == "POST":

                    for key in self.request.params.keys():
                        if key.find("remove") >= 0:
                            id = int(key.replace("remove", ""))
                            setCombinationStatus(activeProjectId, id, 0, self.request)
                        if key.find("add") >= 0:
                            id = int(key.replace("add", ""))
                            setCombinationStatus(activeProjectId, id, 1, self.request)
                    formdata = self.getPostDict()
                    scrollPos = int(formdata["scroll"])

                    if "btn_save_quantity" in self.request.POST:
                        for key in self.request.params.keys():
                            if key.find("quantitycombination_") > -1:
                                comb_id = key.split("_")[1]
                                setCombinationQuantityAvailable(
                                    activeProjectId,
                                    comb_id,
                                    int(formdata[key]),
                                    self.request,
                                )

                        self.returnRawViewResult = True

                        return HTTPFound(
                            location=self.request.route_url(
                                "combinations",
                                _query={"stage": 2},
                                project=activeProjectCod,
                                user=activeProjectUser,
                            )
                        )

                createCombinations(
                    activeProjectUser, activeProjectId, activeProjectCod, self.request
                )
                techs, ncombs, combs, = getCombinations(activeProjectId, self.request)

                pos = 1
                elements = []
                combArray = []
                pos2 = 0
                for comb in combs:
                    if pos <= len(techs):
                        elements.append(
                            {
                                "alias_id": comb["alias_id"],
                                "alias_name": comb["alias_name"],
                            }
                        )
                        pos += 1
                    else:
                        combArray.append(
                            {
                                "ncomb": comb["comb_code"] - 1,
                                "comb_usable": combs[pos2 - 1]["comb_usable"],
                                "quantity_available": combs[pos2 - 1][
                                    "quantity_available"
                                ],
                                "elements": list(elements),
                            }
                        )
                        elements = []
                        elements.append(
                            {
                                "alias_id": comb["alias_id"],
                                "alias_name": comb["alias_name"],
                            }
                        )
                        pos = 2
                    pos2 += 1
                combArray.append(
                    {
                        "ncomb": ncombs,
                        "comb_usable": combs[pos2 - 1]["comb_usable"],
                        "quantity_available": combs[pos2 - 1]["quantity_available"],
                        "elements": list(elements),
                    }
                )

                return {
                    "activeUser": self.user,
                    "activeProject": getActiveProject(self.user.login, self.request),
                    "techs": techs,
                    "combArray": combArray,
                    "stage": stage,
                    "csrf": self.request.session.get_csrf_token(),
                    "scrollPos": scrollPos,
                    "registryCreated": False,
                }
            if stage == 2:
                error_summary = {}

                createCombinations(
                    activeProjectUser, activeProjectId, activeProjectCod, self.request
                )

                prjData = getProjectData(activeProjectId, self.request)
                # Only create the packages if its needed
                if prjData["project_createpkgs"] == 1:

                    up = updateCreatePackages(activeProjectId, 2, self.request)

                    dl = deleteProjectPackages(activeProjectId, self.request)

                    settings = createSettings(self.request)
                    create_randomization(
                        self.request,
                        self.request.locale_name,
                        activeProjectUser,
                        activeProjectId,
                        activeProjectCod,
                        settings,
                    )

                packagesCreated = True

                if prjData["project_createpkgs"] == 3:
                    packagesCreated = False

                if not packagesCreated:
                    error_summary["error"] = self._(
                        "There was a problem with the creation of the packages please check the available quantity of each combination (Click on the 'Modify' button) and try to generate the packages again."
                    )

                ncombs, packages = getPackages(
                    activeProjectUser, activeProjectId, self.request
                )

                projectDetails = getActiveProject(self.user.login, self.request)
                listOfLabels = [
                    projectDetails["project_label_a"],
                    projectDetails["project_label_b"],
                    projectDetails["project_label_c"],
                ]
                return {
                    "activeUser": self.user,
                    "activeProject": projectDetails,
                    "packages": packages,
                    "stage": stage,
                    "registryCreated": False,
                    "tech": getTech(activeProjectId, self.request),
                    "listOfLabels": listOfLabels,
                    "error_summary": error_summary,
                }
            if stage == 3:
                if not projectHasCombinations(activeProjectId, self.request):
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "combinations",
                            _query={"stage": 1},
                            project=activeProjectCod,
                            user=activeProjectUser,
                        )
                    )
                if not projectHasPackages(activeProjectId, self.request):
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "combinations",
                            _query={"stage": 2},
                            project=activeProjectCod,
                            user=activeProjectUser,
                        )
                    )

                projectDetails = getActiveProject(self.user.login, self.request)

                startIsOk, error = startTheRegistry(
                    self,
                    activeProjectUser,
                    activeProjectId,
                    activeProjectCod,
                    [
                        projectDetails["project_label_a"],
                        projectDetails["project_label_b"],
                        projectDetails["project_label_c"],
                    ],
                )

                if startIsOk:
                    self.returnRawViewResult = True
                    return HTTPFound(location=self.request.route_url("dashboard"))
                else:
                    return {
                        "activeProject": getActiveProject(
                            self.user.login, self.request
                        ),
                        "stage": stage,
                        "error_summary": {
                            "error": self._(
                                "There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form."
                            ),
                            "contact": self._(
                                "Contact the ClimMob team with the next message to get the solution to the problem:"
                            ),
                            "copie": error,
                        },
                    }


def startTheRegistry(self, userOwner, projectId, projectCod, listOfLabelsForPackages):
    locale = self.request.locale_name

    sectionOfThePackageCode = getTheGroupOfThePackageCode(projectId, self.request)
    correct, error = generateRegistry(
        userOwner,
        projectId,
        projectCod,
        self.request,
        sectionOfThePackageCode,
        listOfLabelsForPackages,
    )

    if correct:

        setRegistryStatus(userOwner, projectCod, projectId, 1, self.request)

        ncombs, packages = getPackages(userOwner, projectId, self.request)

        create_qr_packages(
            self.request,
            self.request.locale_name,
            userOwner,
            projectId,
            projectCod,
            ncombs,
            packages,
        )
        time.sleep(1)

        data, finalCloseQst = getDataFormPreview(self, userOwner, projectId)
        create_document_form(
            self.request,
            locale,
            userOwner,
            projectId,
            projectCod,
            "Registration",
            "",
            data,
            packages,
            listOfLabelsForPackages,
        )

        time.sleep(1)
        create_packages_excell(
            self.request,
            self.request.locale_name,
            userOwner,
            projectId,
            projectCod,
            packages,
            getTech(projectId, self.request),
            listOfLabelsForPackages,
        )
        time.sleep(1)

        create_fieldagents_report(
            locale,
            self.request,
            userOwner,
            projectCod,
            projectId,
            getProjectEnumerators(projectId, self.request),
            getActiveProject(self.user.login, self.request),
        )

        numberOfCombinations = numberOfCombinationsForTheProject(
            projectId, self.request
        )

        if numberOfCombinations == 3:
            tech = searchTechnologiesInProject(projectId, self.request)
            if len(tech) == 1:
                if (
                    tech[0]["tech_name"] == "Colores"
                    or tech[0]["tech_name"] == "Colors"
                ):
                    time.sleep(1)
                    create_colors_cards(
                        self.request,
                        userOwner,
                        projectId,
                        projectCod,
                        packages,
                        listOfLabelsForPackages,
                    )
        # Call extenal plugins here

        for plugin in p.PluginImplementations(p.IForm):
            plugin.after_adding_form(
                self.request, userOwner, projectId, projectCod, "registry", ""
            )

        for plugin in p.PluginImplementations(p.IPackage):
            plugin.after_create_packages(
                self.request,
                userOwner,
                projectId,
                projectCod,
                "create_packages",
                ncombs,
                packages,
            )

        for plugin in p.PluginImplementations(p.IUpload):
            plugin.create_Excel_template_for_upload_data(
                self.request,
                userOwner,
                projectId,
                projectCod,
                "registry"
            )

    return correct, str(error, "utf-8")


def createSettings(request):

    settings = {}
    for key, value in request.registry.settings.items():
        if isinstance(value, str):
            settings[key] = value

    return settings
