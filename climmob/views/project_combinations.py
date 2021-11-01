from .classes import privateView
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from ..processes import projectExists, getTech, getProjectEnumerators
from ..processes import createCombinations, getCombinations, setCombinationStatus
from ..processes import (
    create_packages_with_r,
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
)
import climmob.plugins as p
from ..products.qrpackages.qrpackages import create_qr_packages
from ..products.forms.form import create_document_form
from ..products.packages.packages import create_packages_excell
from ..products.colors.colors import create_colors_cards
from ..products.fieldagents.fieldagents import create_fieldagents_report
from .registry import getDataFormPreview
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

                createCombinations(
                    activeProjectUser, activeProjectId, activeProjectCod, self.request
                )

                create_packages_with_r(
                    activeProjectUser, activeProjectId, activeProjectCod, self.request
                )
                ncombs, packages = getPackages(
                    activeProjectUser, activeProjectId, self.request
                )

                # print "*******************************10"
                # pprint.pprint(packages)
                # print "*******************************10"

                lcombs = list(range(ncombs))
                combArray = []
                for c in lcombs:
                    combArray.append(chr(65 + c))

                return {
                    "activeUser": self.user,
                    "activeProject": getActiveProject(self.user.login, self.request),
                    "ncombs": combArray,
                    "packages": packages,
                    "stage": stage,
                    "registryCreated": False,
                    "tech": getTech(activeProjectId, self.request),
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

                startIsOk, error = startTheRegistry(
                    self, activeProjectUser, activeProjectId, activeProjectCod
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


def startTheRegistry(self, userOwner, projectId, projectCod):
    locale = self.request.locale_name

    sectionOfThePackageCode = getTheGroupOfThePackageCode(projectId, self.request)
    correct, error = generateRegistry(
        userOwner, projectId, projectCod, self.request, sectionOfThePackageCode
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
        )
        time.sleep(1)

        create_fieldagents_report(
            locale,
            self.request,
            userOwner,
            projectCod,
            projectId,
            getProjectEnumerators(projectId, self.request),
            getActiveProject(self.user.login, self.request)
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
                        self.request, userOwner, projectId, projectCod, packages
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

    return correct, str(error, "utf-8")
