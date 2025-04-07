from http import HTTPStatus

from pyramid.response import Response

from climmob.models import ProjectObjectives
from climmob.processes.db.project_objectives import get_objective_by_id
from climmob.views.classes import privateView

from climmob.processes import (
    get_all_project_location,
    add_objective,
    update_objective,
    delete_objective_by_id,
    get_all_location_unit_of_analysis_grouped_by_project_location,
    get_location_unit_of_analysis_objectives_by_proj_objective_id,
    add_location_unit_of_analysis_objective,
    delete_location_unit_of_analysis_objective,
)


class ObjectiveByIdView(privateView):
    def processView(self):
        print(
            f"{self.request.method} objective by id {self.request.matchdict['objective_id']}"
        )
        pobj_id = self.request.matchdict["objective_id"]
        if self.request.method == "GET":
            self.returnRawViewResult = True
            return get_objective_by_id(self.request, pobj_id)

        elif self.request.method == "PATCH":
            return self.process_patch(pobj_id)

        elif self.request.method == "DELETE":
            delete_objective_by_id(self.request, pobj_id)
            self.returnRawViewResult = True
            return Response(status=str(HTTPStatus.NO_CONTENT.__int__()))

    def process_patch(self, pobj_id):
        self.returnRawViewResult = True
        new_name = self.request.json_body["pobjective_name"]
        loc_unit_of_analyses = self.request.json_body["luoas"]
        if len(loc_unit_of_analyses) == 0:
            return Response(self._("Must select at least one category"), status="400")

        self.update_objective_luoaobjs(loc_unit_of_analyses, pobj_id)

        success, msg = update_objective(
            self.request,
            ProjectObjectives(pobjective_id=pobj_id, pobjective_name=new_name),
        )
        if not success:
            return Response(self._(msg), status="400")
        response = Response(
            json_body=get_objective_by_id(self.request, pobj_id), status="200"
        )
        return response

    def update_objective_luoaobjs(self, loc_unit_of_analyses, pobj_id):
        loc_unit_of_an_objectives = (
            get_location_unit_of_analysis_objectives_by_proj_objective_id(
                self.request, pobj_id
            )
        )
        self.delete_removed_luoaobjs(loc_unit_of_an_objectives, loc_unit_of_analyses)

        self.add_new_luoaobjs(loc_unit_of_an_objectives, loc_unit_of_analyses, pobj_id)

    def add_new_luoaobjs(
        self, loc_unit_of_an_objectives, loc_unit_of_analyses, pobj_id
    ):
        loc_unit_of_an_objectives_ids = [
            x["pluoa_id"] for x in loc_unit_of_an_objectives
        ]
        for loc_unit_of_analysis in loc_unit_of_analyses:
            if loc_unit_of_analysis not in loc_unit_of_an_objectives_ids:
                add_location_unit_of_analysis_objective(
                    self.request, pobj_id, loc_unit_of_analysis
                )

    def delete_removed_luoaobjs(self, loc_unit_of_an_objectives, loc_unit_of_analyses):
        for loc_unit_of_an_objective in loc_unit_of_an_objectives:
            if loc_unit_of_an_objective["pluoa_id"] not in loc_unit_of_analyses:
                delete_location_unit_of_analysis_objective(
                    self.request, loc_unit_of_an_objective["pluoaobj_id"]
                )


class ProjectObjectivesView(privateView):
    def processView(self):
        dataworking = {"project_location": "-1", "project_unit_of_analysis": "-1"}
        error_summary = {}
        modify = False
        reportUpload = []

        nextPage = self.request.params.get("next")

        print(f"{self.request.method} project objectives")

        if self.request.method == "POST":
            # dataworking = {...dataworking, self.getPostDict()}
            body = self.getPostDict()
            name = body.get("pobjective_name")
            loc_unit_of_analyses = body.get("luaos")
            success, msg = add_objective(self.request, name, loc_unit_of_analyses)
            if not success:
                error_summary = {"error": self._(msg)}

        return {
            "activeUser": self.user,
            "dataworking": dataworking,
            "error_summary": error_summary,
            "reportUpload": reportUpload,
            "modify": modify,
            "nextPage": nextPage,
            "sectionActive": "project_objectives",
            "listOfLocations": get_all_project_location(self.request),
            "luoas": get_all_location_unit_of_analysis_grouped_by_project_location(
                self.request
            ),
        }
