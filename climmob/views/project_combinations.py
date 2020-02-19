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
)
import climmob.plugins as p
from ..products.qrpackages.qrpackages import create_qr_packages
from ..products.cards.cards import create_cards
from ..products.packages.packages import create_packages_excell
from ..products.colors.colors import create_colors_cards
from ..products.fieldagents.fieldagents import create_fieldagents_report

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

            # self.needCSS('jquerysteps')
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
                # self.needCSS('datatables')
                # self.needJS('prjcombinations')
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
                if not projectHasCombinations(self.user.login, projectid, self.request):
                    self.returnRawViewResult = True
                    return HTTPFound(
                        location=self.request.route_url(
                            "combinations", _query={"stage": 1}, projectid=projectid
                        )
                    )

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

                startTheRegistry(self, projectid)

                return {
                    "activeUser": self.user,
                    "projectid": projectid,
                    "registryCreated": True,
                }


def startTheRegistry(self, projectid):

    setRegistryStatus(self.user.login, projectid, 1, self.request)

    generateRegistry(self.user.login, projectid, self.request)

    ncombs, packages = getPackages(self.user.login, projectid, self.request)

    create_qr_packages(self.request, self.user.login, projectid, ncombs, packages)

    create_cards(self.request, self.user.login, projectid, packages)

    create_packages_excell(
        self.request,
        self.user.login,
        projectid,
        packages,
        getTech(self.user.login, projectid, self.request),
    )

    locale = self.request.locale_name
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
            if tech[0]["tech_name"] == "Colores" or tech[0]["tech_name"] == "Colors":
                create_colors_cards(self.request, self.user.login, projectid, packages)
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
