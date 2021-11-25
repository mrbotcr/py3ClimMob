from climmob.views.classes import privateView
from climmob.processes import (
    getProjectData,
    searchTechnologiesInProject,
    getCombinations,
    createExtraPackages,
    getPackages,
    AliasSearchTechnologyInProject,
    getTheProjectIdForOwner,
    getTech,
)
from climmob.config.auth import getCountryName
from climmob.products.qrpackages.qrpackages import create_qr_packages
from climmob.products.packages.packages import create_packages_excell


class projectHelp_view(privateView):
    def processView(self):
        dataworking = {}
        dataworking["project_username"] = ""
        dataworking["project_cod"] = ""

        if self.request.method == "POST":

            dataworking = self.getPostDict()

            activeProjectId = getTheProjectIdForOwner(
                dataworking["project_username"],
                dataworking["project_cod"],
                self.request,
            )

            dataworking["project_details"] = getProjectData(
                activeProjectId, self.request,
            )

            if dataworking["project_details"]:
                if "btn_search_project" in self.request.POST:

                    dataworking = getImportantInformation(dataworking, self.request)

                if "btn_apply_changes" in self.request.POST:

                    status, message = createExtraPackages(
                        dataworking["project_username"],
                        activeProjectId,
                        dataworking["project_cod"],
                        self.request,
                        dataworking["project_details"]["project_numcom"],
                        dataworking["project_packages"],
                        dataworking["project_details"]["project_numobs"],
                    )
                    if status:
                        dataworking["project_details"] = getProjectData(
                            activeProjectId, self.request,
                        )
                        dataworking["result_positive"] = self._(
                            "The number of participants was successfully increased"
                        )
                        dataworking = getImportantInformation(dataworking, self.request)

                        ncombs, packages = getPackages(
                            dataworking["project_username"],
                            activeProjectId,
                            self.request,
                        )
                        create_qr_packages(
                            self.request,
                            self.request.locale_name,
                            dataworking["project_username"],
                            activeProjectId,
                            dataworking["project_cod"],
                            ncombs,
                            packages,
                        )
                        listOfLabels = [
                            dataworking["project_details"]["project_label_a"],
                            dataworking["project_details"]["project_label_b"],
                            dataworking["project_details"]["project_label_c"],
                        ]
                        create_packages_excell(
                            self.request,
                            self.request.locale_name,
                            dataworking["project_username"],
                            activeProjectId,
                            dataworking["project_cod"],
                            packages,
                            getTech(activeProjectId, self.request),
                            listOfLabels,
                        )

                    else:
                        dataworking["result_negative"] = message
            else:
                dataworking["result_negative"] = self._(
                    "We haven't found a project that matches what was specified"
                )
        return {"dataworking": dataworking}


def getImportantInformation(dataworking, request):

    dataworking["project_details"]["country"] = getCountryName(
        dataworking["project_details"]["project_cnty"], request
    )
    techs, ncombs, combs, = getCombinations(
        dataworking["project_details"]["project_id"], request
    )
    techInfo = searchTechnologiesInProject(
        dataworking["project_details"]["project_id"], request
    )
    for tech in techInfo:
        tech["alias"] = AliasSearchTechnologyInProject(
            tech["tech_id"], dataworking["project_details"]["project_id"], request,
        )
    dataworking["project_details"]["techs"] = techInfo
    dataworking["project_details"]["ncombs"] = ncombs
    if dataworking["project_details"]["project_regstatus"] > 0:
        pos = 1
        elements = []
        combArray = []
        pos2 = 0
        for comb in combs:
            if pos <= len(techs):
                elements.append(
                    {"alias_id": comb["alias_id"], "alias_name": comb["alias_name"],}
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
                    {"alias_id": comb["alias_id"], "alias_name": comb["alias_name"],}
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
        dataworking["project_details"]["combs"] = combArray

    return dataworking
