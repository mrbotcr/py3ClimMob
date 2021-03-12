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
)
from ..processes import (
    generateRegistry,
    numberOfCombinationsForTheProject,
    searchTechnologiesInProject,
    getTheGroupOfThePackageCode,
)
import climmob.plugins as p
from ..products.qrpackages.qrpackages import create_qr_packages
from ..products.forms.form import create_document_form
from ..products.packages.packages import create_packages_excell
from ..products.colors.colors import create_colors_cards
from ..products.fieldagents.fieldagents import create_fieldagents_report
from ..products.stickers.stickers import create_stickers_document
from .registry import getDataFormPreview
import time

import pprint


class projectCombinations_view(privateView):
    def processView(self):
        projectid = self.request.matchdict["projectid"]
        if not projectExists(self.user.login, projectid, self.request):
            raise HTTPNotFound()
        else:
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
                            setCombinationStatus(
                                self.user.login, projectid, id, 0, self.request
                            )
                        if key.find("add") >= 0:
                            id = int(key.replace("add", ""))
                            setCombinationStatus(
                                self.user.login, projectid, id, 1, self.request
                            )
                    formdata = self.getPostDict()
                    scrollPos = int(formdata["scroll"])

                createCombinations(self.user.login, projectid, self.request)
                techs, ncombs, combs, = getCombinations(
                    self.user.login, projectid, self.request
                )

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
                    "projectid": projectid,
                    "techs": techs,
                    "combArray": combArray,
                    "stage": stage,
                    "csrf": self.request.session.get_csrf_token(),
                    "scrollPos": scrollPos,
                    "registryCreated": False,
                }
            if stage == 2:
                # EDITED BY BRANDON
                # if not projectHasCombinations(self.user.login, projectid, self.request):
                # self.returnRawViewResult = True
                # return HTTPFound(
                #    location=self.request.route_url(
                #        "combinations", _query={"stage": 1}, projectid=projectid
                #    )
                # )
                createCombinations(self.user.login, projectid, self.request)

                create_packages_with_r(self.user.login, projectid, self.request)
                ncombs, packages = getPackages(self.user.login, projectid, self.request)

                # print "*******************************10"
                # pprint.pprint(packages)
                # print "*******************************10"

                lcombs = list(range(ncombs))
                combArray = []
                for c in lcombs:
                    combArray.append(chr(65 + c))
                # self.needCSS('datatables')
                # self.needJS('prjcombinations')

                return {
                    "activeUser": self.user,
                    "projectid": projectid,
                    "ncombs": combArray,
                    "packages": packages,
                    "stage": stage,
                    "registryCreated": False,
                    "tech": getTech(self.user.login, projectid, self.request),
                }
            if stage == 3:
                if not projectHasCombinations(self.user.login, projectid, self.request):
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "combinations", _query={"stage": 1}, projectid=projectid
                        )
                    )
                if not projectHasPackages(self.user.login, projectid, self.request):
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "combinations", _query={"stage": 2}, projectid=projectid
                        )
                    )

                startIsOk, error = startTheRegistry(self, projectid)

                if startIsOk:
                    self.returnRawViewResult = True
                    return HTTPFound(location=self.request.route_url("dashboard"))
                else:
                    return {
                        "projectid": projectid,
                        "stage": stage,
                        "error_summary": {
                            "error": self._(
                                "There has been a problem in the creation of the basic structure of the project, this may be due to something wrong with the form."
                            ),
                            "contact": self._(
                                "Contact the ClimMob team with the next message to get the solution to the problem:"
                            ),
                            "copie": error
                        },
                    }


def startTheRegistry(self, projectid):
    locale = self.request.locale_name

    sectionOfThePackageCode = getTheGroupOfThePackageCode(
        self.user.login, projectid, self.request
    )
    correct,error = generateRegistry(
        self.user.login, projectid, self.request, sectionOfThePackageCode
    )

    if correct:

        setRegistryStatus(self.user.login, projectid, 1, self.request)

        ncombs, packages = getPackages(self.user.login, projectid, self.request)

        create_qr_packages(self.request, self.user.login, projectid, ncombs, packages)
        time.sleep(1)

        data, finalCloseQst = getDataFormPreview(self, projectid)
        create_document_form(
            self.request,
            locale,
            self.user.login,
            projectid,
            "Registration",
            "",
            data,
            packages,
        )
        time.sleep(1)
        # create_cards(self.request, self.user.login, projectid, packages)
        # create_stickers_document(
        #    self.request.locale_name, self.request, self.user.login, projectid, packages
        # )

        time.sleep(1)
        create_packages_excell(
            self.request,
            self.user.login,
            projectid,
            packages,
            getTech(self.user.login, projectid, self.request),
        )
        time.sleep(1)

        create_fieldagents_report(
            locale,
            self.request,
            self.user.login,
            projectid,
            getProjectEnumerators(self.user.login, projectid, self.request),
        )

        numberOfCombinations = numberOfCombinationsForTheProject(
            self.user.login, projectid, self.request
        )

        if numberOfCombinations == 3:
            tech = searchTechnologiesInProject(self.user.login, projectid, self.request)
            if len(tech) == 1:
                if (
                    tech[0]["tech_name"] == "Colores"
                    or tech[0]["tech_name"] == "Colors"
                ):
                    time.sleep(1)
                    create_colors_cards(
                        self.request, self.user.login, projectid, packages
                    )
        # Call extenal plugins here

        for plugin in p.PluginImplementations(p.IPackage):
            plugin.after_create_packages(
                self.request,
                self.user.login,
                projectid,
                "create_packages",
                ncombs,
                packages,
            )

    return correct, str(error,'utf-8')
