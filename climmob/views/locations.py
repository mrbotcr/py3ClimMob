import re

from cherrypy.lib.sessions import Session
from pattern.graph import redirect
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
import validators
from pyramid.view import view_config

from climmob.processes import (
    getActiveProject,
)

from climmob.processes.db.project_location import (
    get_all_project_location,
    deleteLocationdb,
    add_Location_DB,
    editLocation,
    get_location_by_name
)

from climmob.views.classes import privateView
import climmob.plugins as p


class crud_view(privateView):
    def processView(self):
        dataworking = {}
        error_summary = {}
        success_message = None
        error_message = None
        exist = None
        modify = False
        reportUpload = []
        nextPage = self.request.params.get("next")

        if self.request.method == "POST":
            dataworking = self.getPostDict()
            if "btn_add_location" in self.request.POST:
                modify = False
                exist = get_location_by_name(self.request, dataworking["plocation_name"])
                if not exist:
                    dataworking, error_summary = functionForAddLocations(
                        self, dataworking, error_summary
                    )
                    success_message = "Location created successfully"
                else:

                    error_message = "All ready exist this name"

            if "btn_edit_location" in self.request.POST:
                modify = False

                exist = get_location_by_name(self.request, dataworking["edit_plocation_name"])
                if not exist:
                    locationid = dataworking["edit_plocation_id"]
                    dataworking, error_summary = editLocation(
                        dataworking, locationid, error_summary, self.request
                    )
                    success_message = "Location edited successfully"
                else:
                    error_message = "All ready exist this name"

        return {
            "activeUser": self.user,
            "activeProject": getActiveProject(self.user.login, self.request),
            "searchAllProyectLocation": get_all_project_location(self.request),
            "nextPage": nextPage,
            "modify": modify,
            "reportUpload": reportUpload,
            "error_summary": error_summary,
            "error_message": error_message,
            "dataworking": dataworking,
            'success_message': success_message
        }


def functionForAddLocations(self, dataworking, error_summary, showMessage=True):
    added, message = add_Location_DB(dataworking, self.request)
    if not added:
        error_summary = {"error": message}
    else:
        dataworking = {}
        if showMessage:
            self.request.session.flash(self._("The location was created successfully."))
    return dataworking, error_summary


class deleteLocation_view(privateView):
    def processView(self):
        locationid = self.request.matchdict["locationid"]

        if self.request.method == "POST":
            continue_delete = True
            message = ""

            if continue_delete:
                deleted, message = deleteLocationdb(locationid, self.request)
                if not deleted:
                    self.returnRawViewResult = True
                    return {"status": 400, "error": message}
                else:
                    self.request.session.flash(
                        self._("The location was successfully removed")
                    )
                    self.returnRawViewResult = True
                    return {"status": 200}
            else:
                self.returnRawViewResult = True
                return {"status": 400, "error": message}


# class addLocation(privateView):
#
#     def addLocation(self):
#         dataworking = {}
#         modify = False
#         reportUpload = []
#         nextPage = self.request.params.get("next")
#
#         return {
#             "dataworking": dataworking,
#             "reportUpload": reportUpload,
#             "modify": modify,
#             "nextPage": nextPage
#         }
#
#     @view_config(route_name='add_crud_locations_json', request_method='POST', renderer='json')
#     def add_location_json(self):
#         try:
#             # Obtener los datos del cuerpo de la solicitud en formato JSON
#             data = json.loads(self.request.body.decode())
#             location_name = data.get('plocation_name')
#             csrf_token = self.request.headers.get('check_csrf_token')
#
#
#             # Llamar a la función para guardar los datos en la base de datos
#             success, error = add_Location_DB(data, self.request)
#
#             if not success:
#                 # Si hubo un error al agregar la ubicación, se devuelve un mensaje de error
#                 return Response(
#                     json.dumps({
#                         'status': 'error',
#                         'message': error
#                     }),
#                     content_type='application/json',
#                     status=400
#                 )
#

#             return Response(
#                 json.dumps({
#                     'status': 'success',
#                     'message': f'Location "{location_name}" added successfully!'
#                 }),
#                 content_type='application/json',
#                 status=200
#             )
#         except json.JSONDecodeError:
#             # Si hay un error en el formato JSON
#             return Response(
#                 json.dumps({'status': 'error', 'message': 'Invalid JSON format'}),
#                 content_type='application/json',
#                 status=400
#             )
#         except Exception as e:
#             # Si ocurre cualquier otro error inesperado
#             return Response(
#                 json.dumps({'status': 'error', 'message': str(e)}),
#                 content_type='application/json',
#                 status=500
#             )
# class editLocation(privateView):
#     def editLocation(self):
#         print(self.request.id)
#         # location = get_location_by_id(self.request,self.request.id)
#         location = "hola"
#
#         if location is None:
#            return HTTPFound(self.request.route_url('404.jinja2'))
#         return  dict(location=location)
#
# class deleteLocation(privateView):
#     def deleteLocation(self):
#         self.request.session.flash('Deleted: %s' % self.request.id)
#         self.request.dbsession.delete(self.request)
#         url = "climmob3/crud_locations"
#         return redirect(url)
