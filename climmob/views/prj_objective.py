from pyramid.response import Response

from climmob.models import ProjectObjectives
from climmob.processes.db.project_objectives import get_objective_by_id
from climmob.views.classes import privateView

from climmob.processes import (
    get_all_project_location,
    add_objective,
    update_objective,
    delete_objective_by_id,
    getAllLocationUnitOfAnalysisAgg,
)


class objective_by_id_view(privateView):
    def processView(self):
        print(
            f"{self.request.method} objective by id {self.request.matchdict['objective_id']}"
        )
        pobj_id = self.request.matchdict["objective_id"]
        if self.request.method == "GET":
            self.returnRawViewResult = True
            return get_objective_by_id(self.request, pobj_id)

        elif self.request.method == "PATCH":
            self.returnRawViewResult = True
            new_name = self.request.json_body["pobjective_name"]
            success, msg = update_objective(
                self.request,
                ProjectObjectives(pobjective_id=pobj_id, pobjective_name=new_name),
            )
            if not success:
                return Response(self._(msg), status="400")
            return get_objective_by_id(self.request, pobj_id)

        elif self.request.method == "DELETE":
            delete_objective_by_id(self.request, pobj_id)
            self.returnRawViewResult = True
            return {"status": 200}


class prj_objectives_view(privateView):
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
            luaos = body.get("luaos")
            success, msg = add_objective(self.request, name, luaos)
            if not success:
                error_summary = {"error": self._(msg)}

        return {
            "activeUser": self.user,
            "dataworking": dataworking,
            "error_summary": error_summary,
            "reportUpload": reportUpload,
            "modify": modify,
            "nextPage": nextPage,
            "sectionActive": "prj_objectives",
            "listOfLocations": get_all_project_location(self.request),
            "luoas": getAllLocationUnitOfAnalysisAgg(self.request),
        }
